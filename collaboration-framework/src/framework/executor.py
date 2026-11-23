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
know whether it happened. `sandbox.flaky`'s
execute-but-lose-the-report mode performs its operation and
then reports uncertainty: the report, not the execution, is
what was lost.
"""
import json
import os
import threading
import time

from .doorway import EXECUTOR_ACTOR  # noqa: F401  (the identity
# this machinery reports under, named here for its consumers)


class Executor:
    def __init__(self, doorway, sandbox_dir, claim_dir=None,
                 deadline=5.0, executor_id="executor-1"):
        self.doorway = doorway
        self.store = doorway.store
        self.sandbox_dir = sandbox_dir
        self.claim_dir = claim_dir or os.path.join(
            sandbox_dir, ".claims")
        self.deadline = deadline
        self.executor_id = executor_id
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

    def _write(self, parameters):
        path = self._sandbox_path(parameters["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = parameters.get("content") or ""
        with open(path, "w") as fh:
            fh.write(content)
        return {"path": parameters["path"],
                "bytes": len(content.encode("utf-8"))}

    def _perform(self, tool, parameters):
        """Perform the operation. Returns ("result", result)
        or ("lost", result) — the report-lost marker for
        flaky's execute-but-lose-the-report mode — and raises
        for a failure the operation itself establishes."""
        if tool == "sandbox.write":
            return "result", self._write(parameters)
        if tool == "sandbox.read":
            path = self._sandbox_path(parameters["path"])
            with open(path) as fh:
                content = fh.read()
            return "result", {"path": parameters["path"],
                              "content": content}
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
        self._set_phase(dispatch_id, "begun")
        self.doorway.record_tool_started(dispatch_id)
        box = {}

        def run():
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
