"""The executor — the framework's dispatch machinery (agent
layer, Piece A2; SPEC SHEET Rev 6, R45–R47).

Machinery, not an agent and not an authority: the executor
receives an already-recorded dispatch intent and performs only
that operation — it cannot amend the request, expand its
parameters, choose a different tool, or silently retry. Its
reports (TOOL_STARTED, TOOL_OUTCOME) are recorded through the
doorway under the executor's own distinct, constrained
identity; it can create no requests, grants, dispatches or
reconciliations.

The single-execution boundary is durable (scope Rev 3): before
any execution, the executor takes a per-dispatch **execution
claim** in its own durable store — one file per dispatch,
created atomically (O_EXCL), so two executor instances can
never both claim and perform the same dispatch. The claim
distinguishes an intent not yet claimed, an intent durably
claimed, and execution begun; the record distinguishes the
rest (result known, status uncertain). Recovery follows the
claim, not the intent: an unclaimed standing intent may be
claimed and executed; a claimed intent with no outcome is
never started again merely because no outcome was recorded —
where the recovering executor cannot establish whether the
operation occurred, it records the outcome **uncertain**. A
timeout is never proof of non-occurrence.

Execution runs under a deadline: an operation that outlives
it is reported uncertain, not failed — the framework does not
know whether it happened. The deadline binds the beginning
too: the worker rechecks it after recording its start, so a
start report that itself outlives the deadline (correction
round 3) never lets a new operation begin late — the dispatch
records uncertain instead. `sandbox.flaky`'s
execute-but-lose-the-report mode performs its operation and
then reports uncertainty: the report, not the execution, is
what was lost.
"""
import hashlib
import json
import os
import re
import stat
import threading
import time

from . import tool_policy as _tool_policy
from .doorway import EXECUTOR_ACTOR  # noqa: F401  (the identity
# this machinery reports under, named here for its consumers)


# ------------------------------------------------ retrieval
# The structured retrieval performers (RETRIEVAL-SCOPE
# Rev 5), used by Executor._perform for the v3 tools and —
# under a retrieval-governed assembly only — for
# sandbox.read. Every retrieval result carries the exact
# returned content with its sha256 and byte size as separate
# fields and the authority path that admitted it, so the
# record retains what the worker was given, verifiably
# (provenance, §5 of the scope). The per-result ceiling is
# enforced here, at execution: an oversized result is
# refused with the bound named — a failure the operation
# establishes — and nothing partial is returned.
#
# The one exception is an assembly declaring the working-set
# contract (the freedom-first setup pass, 2026-11-24): there
# a read returns its full content as a recorded result, at
# whatever size the file stands. The ceiling's real
# protection was never the file — it was package growth,
# the attempt-6 blowup — and under the working-set contract
# package growth is governed where the material is CARRIED:
# by the working-set budget and dedupe at package
# construction. Refusing the read itself made a required
# source (index-tail, 40,953 bytes) unobtainable whole
# inside a configuration whose whole purpose is that the
# worker holds his briefcase's contents; the restriction
# did not name what it protected once the budget stood.
# Every other population keeps the ceiling exactly as it
# was: refused, never truncated.

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

# The file kinds whose structure map names headings; any
# other text file's map is its line count alone (the scope's
# distinction: headings for markdown/text, line count for
# other text).
_HEADING_FILE_KINDS = ("md", "markdown", "txt")


def _split_lines(data):
    """The lines of a byte string, as the retrieval contract
    counts them: a line is the bytes up to and including its
    newline; the final line may lack one. Returns a list of
    (raw_bytes, text) — the line's bytes exactly as they
    stand, and its decoded text without the trailing
    newline."""
    lines = []
    start = 0
    while start < len(data):
        nl = data.find(b"\n", start)
        if nl == -1:
            raw = data[start:]
            start = len(data)
        else:
            raw = data[start:nl + 1]
            start = nl + 1
        text = raw.decode("utf-8")
        if text.endswith("\n"):
            text = text[:-1]
        lines.append((raw, text))
    return lines


def _headings(lines):
    """The ATX headings of a split file: each heading line's
    text (without its #s), its level (the # count) and its
    1-based line number, in file order."""
    out = []
    for number, (_raw, text) in enumerate(lines, start=1):
        match = _HEADING_RE.match(text)
        if match:
            out.append({"text": match.group(2),
                        "level": len(match.group(1)),
                        "line": number})
    return out


def _boundary_at_or_after(data, offset):
    """The first UTF-8 character boundary at or after offset
    in data: offset itself where it already falls on one (or
    at either end), else the end of the character offset
    falls inside. The retrieval scope's assignment rule
    (§2): a character straddling a requested start belongs
    to the previous slice, so the served start advances past
    it; a character straddling a requested end belongs to
    this slice, so the served end extends to include it —
    one rule, applied at both ends."""
    if offset <= 0:
        return 0
    if offset >= len(data):
        return len(data)
    index = offset
    while index < len(data) and (data[index] & 0xC0) == 0x80:
        index += 1
    return index


def _retrieval_result(path, content, authority, extra=None):
    """A retrieval outcome's result: the exact returned
    content, its sha256 and byte size as separate recorded
    fields, and the authority path that admitted it — the
    provenance the record retains (§5)."""
    raw = content.encode("utf-8")
    result = {"path": path, "content": content,
              "content_bytes": len(raw),
              "content_sha256": hashlib.sha256(raw).hexdigest(),
              "authority_path": authority}
    if extra:
        result.update(extra)
    return result


def _authority_or_raise(tool, path):
    """The authority path a retrieval operation on this path
    answers under, or a refusal: the executor is the last
    line before the filesystem, and it fails closed on a
    path under neither scope, whatever admitted the
    dispatch."""
    authority = _tool_policy.retrieval_authority(path)
    if authority is None:
        raise RuntimeError(
            f"{tool}: path {path!r} lies under neither the "
            f"sources/ scope nor the scratch/ scope; no "
            f"authority path admits it")
    return authority


class Executor:
    def __init__(self, doorway, sandbox_dir, claim_dir=None,
                 deadline=5.0, executor_id="executor-1",
                 clock=time.monotonic, room=None,
                 exec_timeout=None):
        self.doorway = doorway
        self.store = doorway.store
        self.sandbox_dir = sandbox_dir
        self.claim_dir = claim_dir or os.path.join(
            sandbox_dir, ".claims")
        self.deadline = deadline
        self.executor_id = executor_id
        # The room binding (room-exec configuration, gate 4):
        # the stocked demonstration room this executor's
        # `container.exec` dispatches execute in — held by
        # the harness process for the room's whole lifetime,
        # in the same process that stocked it — and the
        # per-execution wall-clock span handed to its run.
        # An executor without a room establishes an exec
        # dispatch as a failure outcome, the established
        # shape for a tool it cannot perform; it never
        # reaches anywhere else for one.
        self.room = room
        self.exec_timeout = exec_timeout
        # The executing thread's retrieval context (the
        # retrieval piece): set by the worker thread in
        # execute() from the dispatch's own record, read by
        # _perform on that same thread.
        self._retrieval_local = threading.local()
        # The monotonic clock the operation deadline is read
        # from — a dependency, defaulting to time.monotonic,
        # so a test can supply a controlled clock and place
        # the worker deterministically on either side of the
        # deadline (correction round 4). Only the deadline
        # reads it: the deadline's instant in execute() and
        # the worker's recheck. (The claim file's wall-clock
        # stamp and the flaky operation's own sleep are not
        # the deadline and stay on the real clock.)
        self.clock = clock
        os.makedirs(self.sandbox_dir, exist_ok=True)
        os.makedirs(self.claim_dir, exist_ok=True)

    # ----------------------------------------------------- claims
    def _claim_path(self, dispatch_id):
        return os.path.join(self.claim_dir,
                            f"{dispatch_id}.claim")

    def claimed(self, dispatch_id) -> bool:
        """Whether a durable execution claim stands for this
        dispatch — held by any executor, living or crashed."""
        return os.path.exists(self._claim_path(dispatch_id))

    def claim_phase(self, dispatch_id):
        """The claim's recorded phase — "claimed" (taken, not
        yet begun), "begun" (execution established as begun),
        "reported" (an outcome was reported) — or None where
        no claim stands."""
        try:
            with open(self._claim_path(dispatch_id)) as fh:
                return json.load(fh).get("phase")
        except (OSError, ValueError):
            return None

    def _fsync_claim_dir(self):
        """Fsync the claim directory itself, not only the
        claim file: the file's directory entry is part of the
        durable single-execution boundary — a claim whose
        contents survived a crash but whose entry did not
        would let a recovering executor claim and perform the
        dispatch a second time. Creation is the only
        directory-entry change in this store (phases rewrite a
        claim's contents in place; claims are never renamed or
        deleted), so creation is where the directory is
        fsynced."""
        fd = os.open(self.claim_dir, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def claim(self, dispatch_id) -> bool:
        """Take the durable execution claim, atomically: True
        when this executor took it, False when a claim already
        stands. O_EXCL creation is the concurrency protection —
        exactly one claimant per dispatch, across processes,
        crashes and recoveries."""
        path = self._claim_path(dispatch_id)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL
                       | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w") as fh:
            json.dump({"dispatch_id": dispatch_id,
                       "claimant": self.executor_id,
                       "phase": "claimed",
                       "ts": time.time()}, fh)
            fh.flush()
            os.fsync(fh.fileno())
        self._fsync_claim_dir()
        return True

    def _set_phase(self, dispatch_id, phase):
        path = self._claim_path(dispatch_id)
        with open(path) as fh:
            body = json.load(fh)
        body["phase"] = phase
        with open(path, "w") as fh:
            json.dump(body, fh)
            fh.flush()
            os.fsync(fh.fileno())

    # ---------------------------------------------------- sources
    def _dispatch_request(self, dispatch_id):
        """The recorded (tool, parameters) a dispatch answers,
        read from the record itself: the TOOL_DISPATCHED names
        the request identity, the TOOL_REQUESTED carries the
        tool and parameters. The executor performs what the
        record says — nothing else is a source."""
        dispatched = None
        requests = {}
        for ev in self.store.all_events():
            if ev["type"] == "TOOL_DISPATCHED" and \
                    ev["payload"].get("dispatch_id") == \
                    dispatch_id:
                dispatched = ev["payload"]
            elif ev["type"] == "TOOL_REQUESTED":
                key = (ev["payload"].get("instance_id"),
                       ev["payload"].get("request_id"))
                requests.setdefault(key, ev["payload"])
        if dispatched is None:
            return None
        req = requests.get(
            (dispatched.get("instance_id"),
             dispatched.get("request_id")))
        if req is None:
            return None
        return req.get("tool"), req.get("parameters") or {}

    # --------------------------------------------------- perform
    def _sandbox_path(self, rel):
        return os.path.join(self.sandbox_dir, rel)

    @staticmethod
    def _read_contained_bytes(root, rel):
        """The bytes of the regular file at `rel` under
        `root`, read WITHOUT following any symlink and
        without resolving outside `root` — or None where
        the file does not stand as an ordinary regular
        file under that root.

        Both resting places a designated scratch file
        can stand in are worker-writable: the room's
        scratch is the worker's own writing space, and
        a worker with a shell can plant a symlink at the
        designated path pointing anywhere the host can
        read. An ordinary host-side open() would follow
        it in the HOST filesystem and turn a
        presentation read into a host-file read
        primitive (the examiner's journal finding,
        2026-11-24). So the path is walked
        descriptor-by-descriptor from the root: every
        component is opened relative to its parent
        directory's descriptor with O_NOFOLLOW, so a
        symlink at any component — the scratch directory
        itself, an intermediate directory, or the file —
        refuses the read at that component; the
        descriptor chain pins each directory as opened,
        so a name swapped afterwards cannot redirect an
        already-open descriptor. The final component
        must verify by fstat as a regular file before a
        single byte is read (O_NONBLOCK keeps a planted
        FIFO from blocking the open; a non-regular file
        is refused before reading). A refusal is silent
        in the established way: the place contributes
        nothing, exactly as if the file did not stand
        there — the target's contents are never read,
        let alone presented."""
        if os.path.isabs(rel):
            return None
        parts = [p for p in rel.split("/")
                 if p not in ("", ".")]
        if not parts or any(p == ".." for p in parts):
            return None
        try:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        except OSError:
            return None
        try:
            for part in parts[:-1]:
                nfd = os.open(
                    part, os.O_RDONLY | os.O_NOFOLLOW
                    | os.O_DIRECTORY, dir_fd=fd)
                os.close(fd)
                fd = nfd
            nfd = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW
                | os.O_NONBLOCK, dir_fd=fd)
            os.close(fd)
            fd = nfd
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                return None
            chunks = []
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        except OSError:
            return None
        finally:
            os.close(fd)

    def read_designated_scratch(self, rel):
        """The current bytes of a designated scratch file
        (the worker's journal — the orientation pass,
        2026-11-24), read from its resting place: the
        bound room's scratch first — the resting place
        the combined configuration's collection treats
        as primary for the brief — then this executor's
        own sandbox scratch. Returns (resting_place,
        bytes, also_stands_in), also_stands_in naming
        the other resting place when the file stands in
        both, or None where it stands in neither. A read
        for presentation only: it performs nothing and
        records nothing.

        Each resting place is read through
        _read_contained_bytes: the scratch is the
        worker's writing space, so the designated path
        can be a worker-planted symlink, and this
        host-side reader must never follow one out of
        the scratch root (the examiner's journal
        finding). A place whose designated path is a
        symlink, escapes its root, or is not a regular
        file contributes nothing — the presentation is
        the established empty one, never the link
        target's contents."""
        places = []
        if self.room is not None:
            places.append(("room", str(self.room.tree)))
        places.append(("sandbox", self.sandbox_dir))
        found = []
        for name, root in places:
            raw = self._read_contained_bytes(root, rel)
            if raw is not None:
                found.append((name, raw))
        if not found:
            return None
        name, raw = found[0]
        also = found[1][0] if len(found) > 1 else None
        return name, raw, also

    def _retrieval_context(self, dispatch_id):
        """The dispatch's retrieval context (retrieval
        piece): (governed, boundary, working_set) — whether
        the assembly behind the dispatch declares the
        retrieval contract in its sealed record, the pinned
        case's sealed evidence boundary, and whether the
        assembly declares the working-set contract (the
        freedom-first setup pass: under that declaration a
        read returns its full content and package growth is
        governed by the working-set budget at carriage, not
        by the per-result ceiling at execution). Derived
        from the record, as every fact the executor acts on
        is; an assembly that declares nothing else is not
        governed, and its dispatches perform exactly as
        they always have."""
        state = self.doorway.state()
        entry = state["dispatches"].get(dispatch_id) or {}
        assembly_id, assembly = \
            self.doorway._assembly_entry_of_instance(
                state, entry.get("instance_id"))
        if assembly_id is None:
            return False, None, False
        generated = self.doorway._generated_payload(
            assembly_id)
        governed = self.doorway._retrieval_governed(generated)
        working_set = isinstance(generated, dict) and \
            generated.get("working_set_contract") == \
            _tool_policy.WORKING_SET_CONTRACT
        boundary = None
        if governed and assembly is not None:
            content = self.doorway._pinned_case_content(
                state, assembly)
            boundary = (content or {}).get(
                "evidence_boundary")
        return governed, boundary, working_set

    def _write(self, parameters):
        path = self._sandbox_path(parameters["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = parameters.get("content") or ""
        with open(path, "w") as fh:
            fh.write(content)
        return {"path": parameters["path"],
                "bytes": len(content.encode("utf-8"))}

    # --------------------------------------- retrieval performers
    def _read_bytes(self, path):
        with open(self._sandbox_path(path), "rb") as fh:
            return fh.read()

    def _perform_read_governed(self, parameters):
        """sandbox.read under the retrieval contract: the
        whole file, bounded — a file over the per-result
        ceiling is refused with the bound named, so
        whole-document injection is impossible through this
        door too (retrieval scope, the tool contract).

        Under the working-set contract the bound does not
        stand (freedom-first setup pass, 2026-11-24): the
        read returns the file's full content as a recorded
        result, and what enters the worker's packages is
        governed by the working-set budget and dedupe at
        carriage. The ceiling protected package growth;
        the budget is that protection now, at the place
        the growth happens."""
        path = parameters["path"]
        authority = _authority_or_raise("sandbox.read", path)
        data = self._read_bytes(path)
        if getattr(self._retrieval_local, "working_set",
                   False):
            return _retrieval_result(
                path, data.decode("utf-8"), authority)
        ceiling = _tool_policy.RETRIEVAL_RESULT_CEILING
        if len(data) > ceiling:
            raise RuntimeError(
                f"sandbox.read of {path} would return "
                f"{len(data)} bytes, exceeding the per-result "
                f"ceiling of {ceiling} bytes; the read is "
                f"refused and nothing is returned — retrieve "
                f"a bounded range with sandbox.read_range "
                f"instead")
        return _retrieval_result(path, data.decode("utf-8"),
                                 authority)

    def _perform_exec(self, parameters):
        """container.exec (room-exec configuration, gate 4):
        the granted call is handed to the stocked room's own
        run, and the room's outcome is returned in the room
        result contract the demonstration preparation paper
        §2.3 settles, field for field — the exit status (null
        where the execution never produced one: a refusal, a
        timeout, an envelope termination), the bounded output
        with its full byte counts and truncation flags, the
        termination naming what ended the execution (a
        precondition refusal names the precondition), the
        CPU charged, and the duration. The command's contents
        were the doorway's shape check and nothing more; what
        the command does inside the room is the room's
        governance. A room refusal is a result in this
        contract, never an exception: the worker is told its
        execution did not run, and why, in the same shape as
        every other outcome."""
        if self.room is None:
            raise RuntimeError(
                "container.exec: this executor holds no "
                "room; the dispatch cannot be performed")
        started = time.monotonic()
        raw = self.room.run(
            list(parameters["cmd"]),
            timeout=self.exec_timeout
            if self.exec_timeout is not None else 120)
        duration = round(time.monotonic() - started, 3)
        if raw.get("refused"):
            termination = "precondition-failed: %s" % (
                raw.get("failed_precondition"),)
            exit_status = None
        elif raw.get("timed_out"):
            termination = "timeout"
            exit_status = None
        elif raw.get("envelope_termination"):
            term = raw["envelope_termination"]
            termination = "envelope-termination: %s (%s)" % (
                term.get("resource"), term.get("rule"))
            exit_status = None
        else:
            termination = "completed"
            exit_status = raw.get("rc")
        accounting = raw.get("cpu_accounting")
        if isinstance(accounting, dict) and \
                accounting.get("charged_seconds") is not None:
            charged = accounting["charged_seconds"]
        elif raw.get("aggregate_cpu_seconds") is not None:
            charged = raw["aggregate_cpu_seconds"]
        else:
            charged = 0.0
        return {
            "exit_status": exit_status,
            "stdout": raw.get("stdout", ""),
            "stdout_bytes_total": raw.get("stdout_bytes", 0),
            "stdout_truncated": bool(
                raw.get("stdout_truncated", False)),
            "stderr": raw.get("stderr", ""),
            "stderr_bytes_total": raw.get("stderr_bytes", 0),
            "stderr_truncated": bool(
                raw.get("stderr_truncated", False)),
            "termination": termination,
            "cpu_seconds_charged": charged,
            "duration_seconds": duration,
        }

    def _perform_list(self, parameters):
        """sandbox.list: discovery without contents — the
        file's size, line count, and (for markdown/text) its
        headings with line numbers. No body text crosses."""
        path = parameters["path"]
        authority = _authority_or_raise("sandbox.list", path)
        if not os.path.isfile(self._sandbox_path(path)):
            raise RuntimeError(
                f"sandbox.list: {path} is not a file in the "
                f"sandbox")
        data = self._read_bytes(path)
        lines = _split_lines(data)
        kind = path.rsplit(".", 1)[-1].lower() \
            if "." in path else ""
        headings = _headings(lines) \
            if kind in _HEADING_FILE_KINDS else []
        rendered = [f"{path} — {len(data)} bytes, "
                    f"{len(lines)} lines"]
        for heading in headings:
            rendered.append(
                f"line {heading['line']}: "
                f"{'#' * heading['level']} {heading['text']}")
        content = "\n".join(rendered)
        ceiling = _tool_policy.RETRIEVAL_RESULT_CEILING
        if len(content.encode("utf-8")) > ceiling:
            raise RuntimeError(
                f"sandbox.list of {path} produces a structure "
                f"map of {len(content.encode('utf-8'))} "
                f"bytes, exceeding the per-result ceiling of "
                f"{ceiling} bytes; the listing is refused and "
                f"nothing is returned")
        # The rendered map is the result's whole substance:
        # the headings stand in it, with their line numbers,
        # and are not carried a second time as structured
        # extras — single carriage (INDEX 249) is a property
        # of the result itself, not only of the package. The
        # scalar facts (the file's size, its line count)
        # ride as provenance.
        return _retrieval_result(
            path, content, authority,
            {"size_bytes": len(data),
             "line_count": len(lines)})

    def _perform_read_range(self, parameters):
        """sandbox.read_range: a bounded slice — a heading's
        section, an inclusive line range, or a byte window
        of a single line — under the exact semantics of §2:
        a heading matching several headings is refused as
        ambiguous, naming the matches; a slice over the
        ceiling is refused with the bound named; a byte
        window is served aligned to character boundaries,
        and the window actually served is recorded. Under
        the working-set contract the slice ceiling does not
        stand, as with sandbox.read (freedom-first setup
        pass): the range the worker asked for is served
        whole, and carriage is the budget's business."""
        path = parameters["path"]
        authority = _authority_or_raise("sandbox.read_range",
                                        path)
        data = self._read_bytes(path)
        lines = _split_lines(data)
        ceiling = _tool_policy.RETRIEVAL_RESULT_CEILING
        extra = {}
        if "heading" in parameters:
            name = parameters["heading"]
            matches = [h for h in _headings(lines)
                       if h["text"] == name]
            if not matches:
                raise RuntimeError(
                    f"sandbox.read_range: no heading "
                    f"{name!r} stands in {path}")
            if len(matches) > 1:
                where = ", ".join(str(h["line"])
                                  for h in matches)
                raise RuntimeError(
                    f"sandbox.read_range: heading {name!r} "
                    f"matches {len(matches)} headings in "
                    f"{path} (lines {where}); the request is "
                    f"refused as ambiguous — disambiguate by "
                    f"line range")
            heading = matches[0]
            start_idx = heading["line"] - 1
            end_idx = len(lines)
            for other in _headings(lines):
                if other["line"] > heading["line"] and \
                        other["level"] <= heading["level"]:
                    end_idx = other["line"] - 1
                    break
            extra["heading"] = name
        else:
            if parameters["start_line"] > len(lines):
                raise RuntimeError(
                    f"sandbox.read_range: the range begins "
                    f"at line {parameters['start_line']}, past "
                    f"the end of {path} ({len(lines)} lines)")
            start_idx = parameters["start_line"] - 1
            end_idx = min(parameters["end_line"], len(lines))
        if "byte_start" in parameters:
            raw = lines[start_idx][0]
            requested_start = parameters["byte_start"]
            requested_end = parameters["byte_end"]
            served_start = _boundary_at_or_after(
                raw, min(requested_start, len(raw)))
            served_end = _boundary_at_or_after(
                raw, min(requested_end, len(raw)))
            if served_start > served_end:
                served_start = served_end
            chunk = raw[served_start:served_end]
            extra.update({
                "byte_start": served_start,
                "byte_end": served_end,
                "requested_byte_start": requested_start,
                "requested_byte_end": requested_end})
            served = (start_idx + 1, start_idx + 1)
        else:
            chunk = b"".join(raw for raw, _text
                             in lines[start_idx:end_idx])
            served = (start_idx + 1, end_idx)
        if len(chunk) > ceiling and not getattr(
                self._retrieval_local, "working_set", False):
            raise RuntimeError(
                f"sandbox.read_range of {path} lines "
                f"{served[0]}–{served[1]} spans {len(chunk)} "
                f"bytes, exceeding the per-result ceiling of "
                f"{ceiling} bytes; the request is refused "
                f"and nothing is returned — narrow the range")
        extra.update({"start_line": served[0],
                      "end_line": served[1]})
        return _retrieval_result(path, chunk.decode("utf-8"),
                                 authority, extra)

    def _boundary_source_files(self, boundary):
        """The source files a pathless search may cover: the
        paths the pinned case's sealed evidence boundary
        names under sources/ — the boundary governs the
        searched material, so no file outside it is searched
        and no existence signal leaks from outside it."""
        paths = []
        for item in boundary or []:
            if not isinstance(item, str):
                continue
            candidate = item.split(" sha256:")[0]
            if candidate.startswith(
                    _tool_policy.SOURCE_SCOPE_PREFIX + "/") \
                    and candidate not in paths:
                paths.append(candidate)
        return sorted(paths)

    def _perform_search(self, parameters, boundary):
        """sandbox.search: deterministic paged passages
        within permitted material. Matches order by path,
        then line; passages (a match with up to two context
        lines, neighbours merged, never grown past the page
        line cap) pack into pages under the result ceiling
        and the line cap; every result states the total, how
        many it returns, and the continuation where more
        remain — a result never silently looks complete. A
        passage too large for any page is reduced to its
        matching lines; a matching line too large even alone
        is a stub, fetchable by byte window."""
        query = parameters["query"]
        offset = parameters.get("offset", 0)
        path = parameters.get("path")
        ceiling = _tool_policy.RETRIEVAL_RESULT_CEILING
        cap = _tool_policy.SEARCH_PAGE_LINE_CAP
        if path is not None:
            authority = _authority_or_raise("sandbox.search",
                                            path)
            files = [path]
        else:
            authority = "source"
            files = self._boundary_source_files(boundary)
        file_lines = {}
        matches = []
        for name in files:
            if not os.path.isfile(self._sandbox_path(name)):
                if path is not None:
                    raise RuntimeError(
                        f"sandbox.search: {name} is not a "
                        f"file in the sandbox")
                continue
            lines = _split_lines(self._read_bytes(name))
            file_lines[name] = lines
            for number, (_raw, text) in enumerate(lines,
                                                  start=1):
                if query in text:
                    matches.append((name, number))
        matches.sort()
        # Passages: each match with its context, neighbours
        # merged — never grown past the page line cap, so a
        # page can always hold at least one passage whole.
        passages = []
        for name, number in matches:
            low = max(1, number - 2)
            high = min(len(file_lines[name]), number + 2)
            if passages and \
                    passages[-1]["path"] == name and \
                    low <= passages[-1]["end"] + 1 and \
                    high - passages[-1]["start"] + 1 <= cap:
                passages[-1]["end"] = max(passages[-1]["end"],
                                          high)
                passages[-1]["match_lines"].append(number)
            else:
                passages.append({"path": name, "start": low,
                                 "end": high,
                                 "match_lines": [number]})

        def render(passage):
            lines = file_lines[passage["path"]]
            return "\n".join(
                f"{passage['path']}:{n}: {lines[n - 1][1]}"
                for n in range(passage["start"],
                               passage["end"] + 1))

        # Pageable units: a passage that fits whole; else its
        # matching lines alone; else — a line too large even
        # alone — a content-free stub.
        units = []
        for passage in passages:
            if len(render(passage).encode("utf-8")) <= ceiling:
                units.append(passage)
                continue
            for number in passage["match_lines"]:
                single = {"path": passage["path"],
                          "start": number, "end": number,
                          "match_lines": [number]}
                if len(render(single).encode("utf-8")) \
                        <= ceiling:
                    units.append(single)
                else:
                    units.append({
                        "path": passage["path"],
                        "match_line": number, "stub": True,
                        "line_bytes": len(
                            file_lines[passage["path"]]
                            [number - 1][0])})
        # The page holding the match at `offset`: units
        # partition the matches in order, so the page starts
        # at the first unit covering a match at or past it.
        covered = 0
        start_unit = None
        for index, unit in enumerate(units):
            count = 1 if unit.get("stub") else \
                len(unit["match_lines"])
            if covered + count > offset:
                start_unit = index
                break
            covered += count
        page = []
        page_lines = 0
        content = ""
        returned = 0
        if start_unit is not None:
            for unit in units[start_unit:]:
                if unit.get("stub"):
                    page.append(unit)
                    returned += 1
                    continue
                rendered = render(unit)
                candidate = rendered if not content else \
                    content + "\n" + rendered
                if page and \
                        (page_lines + unit["end"]
                         - unit["start"] + 1 > cap or
                         len(candidate.encode("utf-8"))
                         > ceiling):
                    break
                page.append(unit)
                page_lines += unit["end"] - unit["start"] + 1
                content = candidate
                returned += len(unit["match_lines"])
        continuation = offset + returned \
            if offset + returned < len(matches) else None
        return _retrieval_result(
            path, content, authority,
            {"query": query, "total_matches": len(matches),
             "returned": returned,
             "continuation_offset": continuation,
             "passages": page})

    def _perform(self, tool, parameters):
        """Perform the operation. Returns ("result", result)
        or ("lost", result) — the report-lost marker for
        flaky's execute-but-lose-the-report mode — and raises
        for a failure the operation itself establishes. The
        dispatch's retrieval context (the retrieval piece) —
        whether its assembly declares the retrieval contract,
        the pinned case's sealed evidence boundary, and
        whether it declares the working-set contract —
        reaches this seam on the executing thread's local
        (set in execute() below), so the seam's shape is the
        one it has always had."""
        governed = getattr(self._retrieval_local, "governed",
                           False)
        boundary = getattr(self._retrieval_local, "boundary",
                           None)
        if tool == "sandbox.write":
            return "result", self._write(parameters)
        if tool == "sandbox.read":
            if governed:
                return "result", self._perform_read_governed(
                    parameters)
            path = self._sandbox_path(parameters["path"])
            with open(path) as fh:
                content = fh.read()
            return "result", {"path": parameters["path"],
                              "content": content}
        if tool == "sandbox.list":
            return "result", self._perform_list(parameters)
        if tool == "container.exec":
            return "result", self._perform_exec(parameters)
        if tool == "sandbox.read_range":
            return "result", self._perform_read_range(
                parameters)
        if tool == "sandbox.search":
            return "result", self._perform_search(
                parameters, boundary)
        if tool == "sandbox.flaky":
            mode = parameters.get("mode")
            if mode == "fail":
                raise RuntimeError(
                    "sandbox.flaky: induced failure")
            if mode == "hang-past-deadline":
                time.sleep(parameters.get(
                    "hang_seconds", self.deadline * 4))
                return "result", {"mode": mode}
            if mode == "succeed":
                if "path" in parameters:
                    return "result", self._write(parameters)
                return "result", {"mode": mode}
            if mode == "execute-but-lose-the-report":
                result = {"mode": mode}
                if "path" in parameters:
                    result = self._write(parameters)
                return "lost", result
            raise RuntimeError(
                f"sandbox.flaky: unknown mode {mode!r}")
        raise RuntimeError(f"no performer for tool {tool!r}")

    # ---------------------------------------------------- execute
    def execute(self, dispatch_id):
        """Execute one standing dispatch, exactly once: claim
        it durably, record the start, perform under the
        deadline, record the outcome. Returns a summary dict;
        a dispatch already claimed, settled, or unknown is
        reported in the summary, never executed."""
        state = self.doorway.state()
        entry = state["dispatches"].get(dispatch_id)
        if entry is None:
            return {"ok": False, "dispatch_id": dispatch_id,
                    "reason": "no such dispatch stands"}
        if entry.get("outcome") is not None or \
                entry.get("reconciled_seq") is not None:
            return {"ok": False, "dispatch_id": dispatch_id,
                    "reason": "the dispatch already stands "
                              "settled",
                    "outcome": entry.get("outcome")}
        if not self.claim(dispatch_id):
            return {"ok": False, "dispatch_id": dispatch_id,
                    "reason": "already claimed; this executor "
                              "does not perform it"}
        source = self._dispatch_request(dispatch_id)
        if source is None:
            self.doorway.record_tool_outcome(
                dispatch_id, "uncertain",
                detail="the dispatch's request cannot be read "
                       "from the record; occurrence not "
                       "established")
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "uncertain"}
        tool, parameters = source
        governed, boundary, working_set = \
            self._retrieval_context(dispatch_id)
        box = {}
        # The deadline the join below waits on, as a point on
        # the monotonic clock: the worker rechecks it after
        # its start report (see run()), so the same instant
        # governs both threads.
        deadline_at = self.clock() + self.deadline

        def run():
            # The start is the executing thread's own first
            # act (correction round 1): TOOL_STARTED means
            # execution has begun, so it is recorded here —
            # by the thread that is about to perform the
            # operation, immediately before it performs it,
            # with the claim's "begun" transition in the same
            # sequence — never by the calling thread in
            # advance, which would claim a beginning that has
            # not happened. If the start cannot be recorded,
            # the operation must not execute: the failure is
            # handed back for an outcome report instead.
            try:
                self._set_phase(dispatch_id, "begun")
                self.doorway.record_tool_started(dispatch_id)
            except Exception as exc:  # the start report failed
                box["start_error"] = exc
                return
            # The deadline recheck (correction round 3): the
            # start report itself may outlive the deadline —
            # above all when it holds the store's serialization
            # lock and the calling thread waits on that lock to
            # record uncertainty. A start recorded late does
            # not license a late beginning: if the deadline has
            # expired by the time the start stands, the
            # operation body must not run. The fact is handed
            # back distinctly; the outcome is the calling
            # thread's to record (or already recorded on its
            # timeout path) — uncertain, since a begun-but-
            # unperformed dispatch is not a result or a failure
            # the executor can establish.
            if self.clock() >= deadline_at:
                box["deadline_expired"] = True
                return
            # The dispatch's retrieval context rides the
            # executing thread's local into _perform (see
            # there): set here, by the thread that performs,
            # so concurrent executions never share it.
            self._retrieval_local.governed = governed
            self._retrieval_local.boundary = boundary
            self._retrieval_local.working_set = working_set
            try:
                box["value"] = self._perform(tool, parameters)
            except Exception as exc:  # the operation's failure
                box["error"] = exc

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        worker.join(self.deadline)
        if worker.is_alive():
            # Past the deadline the framework does not know
            # whether the operation occurred — that is
            # uncertainty, not failure (R46).
            self.doorway.record_tool_outcome(
                dispatch_id, "uncertain",
                detail="the operation outlived the deadline; "
                       "whether it occurred is not established")
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "uncertain"}
        if "deadline_expired" in box:
            # The worker finished first, but its start report
            # completed only after the deadline (correction
            # round 3): the start stands, nothing was
            # performed, and no outcome has been recorded yet
            # — the timeout path above never ran because the
            # worker was no longer alive when the join
            # returned. The outcome is uncertain, recorded
            # here exactly once: execution was established as
            # begun, but the operation did not run within its
            # deadline, so neither a result nor a failure is
            # established. (Where the join did time out with
            # the worker still inside its start report, the
            # branch above already recorded this same outcome
            # — the doorway's serialization means the two
            # paths can never both record one.)
            self.doorway.record_tool_outcome(
                dispatch_id, "uncertain",
                detail="the start report completed after the "
                       "operation deadline; the operation was "
                       "not performed")
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "uncertain"}
        if "start_error" in box:
            # The start could not be recorded, so the
            # operation never executed — an outcome without a
            # start is legitimate, and it is a failure the
            # executor can establish (nothing was performed),
            # not uncertainty. The claim stands accounted:
            # the outcome settles the dispatch, so recovery
            # leaves it exactly as it stands.
            self.doorway.record_tool_outcome(
                dispatch_id, "failure",
                detail="execution did not begin: the start "
                       "report failed "
                       f"({box['start_error']}); the operation "
                       "was not performed")
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "failure"}
        if "error" in box:
            self.doorway.record_tool_outcome(
                dispatch_id, "failure",
                detail=str(box["error"]))
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "failure"}
        kind, result = box["value"]
        if kind == "lost":
            # The operation happened; its report did not
            # arrive. The dispatch records uncertainty — only
            # reconciliation settles it (R46).
            self.doorway.record_tool_outcome(
                dispatch_id, "uncertain",
                detail="the operation was performed and its "
                       "report was lost; the outcome is not "
                       "established by the executor")
            self._set_phase(dispatch_id, "reported")
            return {"ok": True, "dispatch_id": dispatch_id,
                    "outcome": "uncertain"}
        self.doorway.record_tool_outcome(
            dispatch_id, "result", result=result)
        self._set_phase(dispatch_id, "reported")
        return {"ok": True, "dispatch_id": dispatch_id,
                "outcome": "result", "result": result}

    # --------------------------------------------------- recovery
    def recover(self):
        """Recover standing dispatches after a crash (the
        recovery contract, scope Rev 3): a dispatch with no
        outcome standing is either unclaimed — claim and
        execute it, its first execution — or claimed, in
        which case it is never executed again: where its
        occurrence cannot be established from the record, the
        recovering executor records it uncertain. Dispatches
        already accounted (an outcome, or a reconciliation)
        are left exactly as they stand. Returns the actions
        taken, per dispatch."""
        actions = []
        state = self.doorway.state()
        for dispatch_id, entry in state["dispatches"].items():
            if entry.get("outcome") is not None or \
                    entry.get("reconciled_seq") is not None:
                continue
            if self.claimed(dispatch_id):
                self.doorway.record_tool_outcome(
                    dispatch_id, "uncertain",
                    detail="recovered: the dispatch stands "
                           "claimed and no outcome was "
                           "recorded; whether the operation "
                           "occurred is not established")
                actions.append({"dispatch_id": dispatch_id,
                                "action": "recorded_uncertain"})
            else:
                summary = self.execute(dispatch_id)
                actions.append({"dispatch_id": dispatch_id,
                                "action": "executed",
                                "outcome": summary.get("outcome")})
        return actions
