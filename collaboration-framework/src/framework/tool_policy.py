"""Tool policy — the registry and the pure ceiling contract
(agent layer, Piece A2; SPEC SHEET Rev 6, R44/R47).

One policy, two appliers (scope point 5): the doorway invokes
these functions at the grant check, and the independent checker
applies the same contract to validate recorded requests. The
functions are pure and deterministic — of (tool, ceiling,
parameters) only — they fail closed, and they never execute a
tool: nothing in this module touches the filesystem, the
network, or a clock.

Why the checker holds its own copy (`checker.tool_policy`)
instead of importing this one: the checker's independence is
witnessed by Piece 7's C1 audits — importing the checker loads
no `framework.*` module, and its sources import only
`fabric.canonical`, itself, and the standard library. A shared
import would break that witnessed boundary, so — exactly as
with the projection schema (Piece 7, C3) — the contract is held
in two copies and the A2 suite witnesses their agreement over a
battery of cases, including the registry version. The registry
is framework policy, not a source of authority: a registered
tool is granted only per worker, per case, in the sealed
assembly record.

The registry is deliberately small and real (scope point 6):
`sandbox.write` and `sandbox.read` against a per-run sandbox
directory, and `sandbox.flaky`, a test tool whose behaviour is
set by its parameters so uncertain outcomes are exercised for
real. A ceiling is structured data; each tool's checker
understands only its own constraint keys, and an unknown key —
in the ceiling or in the parameters — fails closed.

Piece A3-CAT adds the registry's worker-facing layer — a
plain description and a parameter schema per tool — and with
it a second registry version. The registry is therefore held
as one view per version: `tool-registry-v1` is the contract
exactly as it stood for Piece A2 (ceiling and parameter keys
only, no worker-facing layer), preserved immutable so a
dispatch recorded under it is verified under it, never
reinterpreted under the new contract; `tool-registry-v2` is
v1's ceiling contract unchanged plus the worker-facing layer.
Every contract function takes the version it applies; the
default is the current version, and an unknown version fails
closed — a version the registry does not hold is a contract
nobody can verify under.

The retrieval piece (RETRIEVAL-SCOPE-2026-11-23, Rev 5) adds
a third view, `tool-registry-v3`: v2's contract for the
standing tools unchanged, plus the three structured
retrieval tools (`sandbox.list`, `sandbox.read_range`,
`sandbox.search`) — and `sandbox.read` joins the retrieval
set, its results bounded like the others'. v3 does NOT
become the default version: `REGISTRY_VERSION` stays v2, so
an assembly is governed by the retrieval contract only
where its sealed record declares it (`RETRIEVAL_CATALOGUE_
CONTRACT`), and the doorway and the loop apply v3 per
assembly, recording the version on each dispatch and
iteration exactly as the A3-CAT settlement established.
Pre-v3 assemblies keep their behaviour whole — the
historical-exemption pattern, applied to a registry version
this time. The retrieval constants below (the per-result
ceiling, the aggregate per-package ceiling, the search page
cap, the two scope prefixes) are the scope's named design
bounds, held here as contract data so the doorway, the
executor and the checker all read the same numbers.

The versioned views are frozen deeply at module load (A3-CAT
correction round): every mapping is a MappingProxyType, every
list a tuple, every set a frozenset, so no caller can alter a
version's contract — v1's historical ceiling contract
included — for the lifetime of the process. Accessors return
plain, mutable copies; the registry's own data never leaves
this module by reference.
"""
from collections.abc import Mapping
from types import MappingProxyType

from fabric.canonical import canonical, sha256_hex


def _freeze(value):
    """The deeply immutable form of a registry structure:
    mappings become MappingProxyType, lists and tuples become
    tuples of frozen items, sets become frozensets; scalars
    pass through. Applied to each version's view at module
    load, so the contract a version names cannot be altered
    in-process, at any depth."""
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(value)
    return value

# The registry's current version identifier: inspectable, and
# pinned for a run by being recorded in every TOOL_DISPATCHED
# the doorway issues — the version is part of the dispatch
# contract, so which policy governed a historical dispatch is
# established from the record, not from whatever source
# happens to be present at replay (Piece A2, correction
# round 1). Both copies carry it; the suite witnesses that
# they agree, and the checker verifies each dispatch under
# the version its record names (Piece A3-CAT settlement (c)).
REGISTRY_VERSION = "tool-registry-v2"

# The retrieval piece's contract data (RETRIEVAL-SCOPE Rev 5).
# The registry version an assembly declaring the retrieval
# contract is dispatched and catalogued under; the catalogue
# contract value its sealed generated record declares; the
# per-result ceiling every retrieval result is bounded by
# (bytes of returned content, enforced at execution — a
# result over it is refused with the bound named, never
# truncated); the aggregate ceiling on retrieved content
# presented in one package (enforced at admission, before
# execution, §3a); the search page's line cap; the tools the
# retrieval contract governs (`sandbox.read` included — under
# the contract, whole-document injection is impossible
# through it too); and the two authority scopes' path
# prefixes — source material under sources/, the worker's
# own scratch under scratch/.
RETRIEVAL_REGISTRY_VERSION = "tool-registry-v3"
RETRIEVAL_CATALOGUE_CONTRACT = "retrieval-v3"
RETRIEVAL_RESULT_CEILING = 12000
RETRIEVAL_AGGREGATE_CEILING = 36000
# Working-set carriage (the run-3 correction, examiner's
# ruling 2026-11-24): the aggregate content budget of a wake
# package's working set — the successful retrieval material
# an assembly under the working-set contract carries forward
# from wake to wake. The figure: the demonstration's three
# stocked sources measure 57,562 content bytes in total
# (11,946 + 4,663 + 40,953), so 64,000 holds the whole
# stocked set whole, with headroom — and it is a hard stop
# against unbounded prompt growth: past it, an entry stands
# in the working set by its provenance alone, marked
# not-carried, never silently truncated. It is roughly five
# times the per-result ceiling (12,000) and deliberately a
# different bound from the per-package aggregate ceiling
# above: that ceiling governs what one package may SERVE;
# this one governs what a package may CARRY FORWARD.
WORKING_SET_CONTENT_BUDGET = 64000
# The working-set contract's name, as the generated record
# declares it and the checker reads it (the checker's own
# copy stands in checker.py, as its other contracts do).
WORKING_SET_CONTRACT = "working-set-v1"
# The freshness guard's suspension declaration (Ben's
# ruling, 2026-11-24: "Disable R31 until we need to worry
# about that"): a sealed generated record declaring this
# value under "freshness_guard" stands under the ruling
# that the doorway's R31 freshness rejection does not
# apply to its instance's answers. The ruling's ground:
# the one-worker demonstration excludes the staleness
# hazard by construction — nothing outside the worker's
# own run changes the case while he answers it — and the
# guard as it stood refused his deliveries for record
# movement the framework's own bookkeeping caused. The
# declaration is a switch, not a deletion: the rule's
# code stands untouched, the doorway honours the
# declaration only for the declaring instance's acts (the
# act records, flagged stale_basis where its view is
# behind, never freshness-refused), and the checker
# reads the same value from its own copy in checker.py.
# A record declaring any other value under the field
# declares a state this framework does not understand.
FRESHNESS_GUARD_SUSPENDED = "r31-suspended-v1"
# The delivery declaration's one known route (door scope,
# 2026-11-24): a sealed generated record declaring this
# route under "delivery" stands under Ben's ruling that
# the worker's contribution is the deliverable's arrival
# and the office files it. The checker reads the same
# value from its own copy in checker.py.
DELIVERY_ROUTE_CONTRIBUTION = "contribution-v1"
# The staged-onboarding presentation contract (INDEX 544,
# Ben's direction, 2026-11-25): a sealed generated record
# declaring this value under "presentation_contract"
# stands under the direction that its worker is onboarded
# in stages instead of being handed the whole briefcase
# at once — the finding behind it (INDEX 543) is that the
# wake package carried the sealed case verbatim AND the
# labelled components built on top of it, so the worker
# read the office's furniture twice (~49 KB on the wire)
# before he could look out the window. Under the contract
# the loop's packages walk the onboarding across the
# first wakes — his memory, introduced as his own; his
# case's essentials; his files, as pointers he pulls
# from; his task, with the phase-grouped tool menu — and
# after onboarding a dashboard wake carries the cover, the
# newest results, the working set, any gate correction
# and pointers back into the briefcase. The verbatim case
# dump, the view and the delta leave his packages
# entirely; no content item stands twice in any package.
# The declaration seals only alongside the working-set
# contract (the combined configuration is its whole
# population, as the working set's is), rides outside the
# record's canonical hash fields like the other contracts,
# and is committed per iteration by a presentation hash
# on the iteration record, which the checker re-derives
# from the record exactly. A generation made without the
# declaration presents exactly as before. The checker
# reads the same value from its own copy in checker.py.
PRESENTATION_CONTRACT = "staged-onboarding-v1"

# The pointer-rule successor contract (INDEX 568, Ben's
# tap 2026-11-25, applying his pointer rule of INDEX 504
# to the working set's own presentation). Under v1 a
# gathered entry's content stands in every dashboard
# package whole — the wake three free provider routes
# refused at 79,660–85,862 bytes. Under v2 an entry's
# content is presented exactly once, in the first wake
# after it was gathered, as part of that wake's newest
# results; in every later package the entry stands as a
# pointer: its address, the tool and step that gathered
# it, its size and content hash, its content_carried
# standing, and one plain sentence naming the room, the
# address and the access call. The record side is
# untouched: derivation, carriage budget, dedupe, the
# gates and filing are exactly v1's. v1's meaning under
# its name does not change; an assembly seals one
# contract or the other, and the loop and the checker
# derive the sealed one's presentation whole.
PRESENTATION_CONTRACT_V2 = "staged-onboarding-v2"
# The onboarding's stages, in the order the wakes walk
# them: the iteration number (1-based) selects the stage —
# iterations 1..4 walk memory, case, files, task; every
# later wake is a dashboard.
PRESENTATION_STAGES = ("memory", "case", "files", "task",
                       "dashboard")
SEARCH_PAGE_LINE_CAP = 40
RETRIEVAL_TOOLS = frozenset({
    "sandbox.list", "sandbox.read_range", "sandbox.search",
    "sandbox.read"})
SOURCE_SCOPE_PREFIX = "sources"
SCRATCH_SCOPE_PREFIX = "scratch"

# The room-exec configuration's contract data (demonstration
# preparation paper §2/§3.2; gate 4): the registry version an
# assembly declaring the exec catalogue contract is dispatched
# and catalogued under; the contract value its sealed generated
# record declares; and the tool the contract governs — the
# worker's own execution tool, offered under the name and the
# shape its preserved generations used (Track A, INDEX 433):
# `container.exec`, arguments an object whose `cmd` is an array
# of strings, no other fields required. The doorway's check for
# this tool is the grant and the shape alone (the paper §2.2):
# its ceiling keys are therefore empty — a grant's scope ceiling
# for it is the empty object, and any ceiling key fails closed —
# and its parameter contract is the cmd array's form, which
# check_ceiling enforces below. What a command may do is
# governed by the room's walls, never by this policy.
EXEC_REGISTRY_VERSION = "tool-registry-v4"
EXEC_CATALOGUE_CONTRACT = "exec-v4"
EXEC_TOOLS = frozenset({"container.exec"})


def retrieval_authority(path):
    """The authority path a sandbox path falls under, or
    None: "source" for a path under sources/, "scratch" for
    a path under scratch/, and None anywhere else — a path
    under neither scope is admitted by no authority path
    (retrieval scope, boundary enforcement). Pure, of the
    path only."""
    if not isinstance(path, str):
        return None
    if path.startswith(SOURCE_SCOPE_PREFIX + "/"):
        return "source"
    if path.startswith(SCRATCH_SCOPE_PREFIX + "/"):
        return "scratch"
    return None


def boundary_member(boundary, path) -> bool:
    """Whether a path is a member of a case's sealed evidence
    boundary. The boundary names material ids (a list of
    strings, as the office seals them); an id names its path
    either exactly or as its leading field — the sealing
    convention names the path, then the material's hash, in
    the one id. Pure, of the two values."""
    if not isinstance(boundary, list) or \
            not isinstance(path, str):
        return False
    for item in boundary:
        if item == path:
            return True
        if isinstance(item, str) and \
                item.startswith(path + " "):
            return True
    return False


def list_authority(path):
    """sandbox.list's authority path (round ten, INDEX
    552): the standing retrieval authority, extended at
    exactly one point — the bare granted prefixes
    themselves ("sources", "scratch"), which
    retrieval_authority does not admit because its paths
    lie strictly under a scope. Listing a directory is
    the one operation whose path may BE the scope. The
    path is canonicalised first — exactly one trailing
    slash stripped — as the ceiling canonicalises it,
    so the directory's two spellings share the one
    authority. Every other retrieval operation keeps
    the strict shape."""
    if isinstance(path, str) and len(path) > 1 \
            and path.endswith("/"):
        path = path[:-1]
    if path == SOURCE_SCOPE_PREFIX:
        return "source"
    if path == SCRATCH_SCOPE_PREFIX:
        return "scratch"
    return retrieval_authority(path)


def boundary_member_for_list(boundary, path) -> bool:
    """Whether a sandbox.list path stands within a
    case's sealed evidence boundary (round ten): a file
    path by the standing membership; a directory — a
    scope prefix itself, in canonical form — where the
    boundary names material under it: the listing shows
    only what stands in the directory, and the
    boundary's members under it are exactly what may be
    seen."""
    if boundary_member(boundary, path):
        return True
    if path not in (SOURCE_SCOPE_PREFIX,
                    SCRATCH_SCOPE_PREFIX) or \
            not isinstance(boundary, list):
        return False
    prefix = path + "/"
    for item in boundary:
        if isinstance(item, str) and \
                item.split(" ")[0].startswith(prefix):
            return True
    return False

# sandbox.flaky's modes (scope point 6): the first three are
# the outcome shapes; the fourth performs the operation and
# loses the report — execution happened, the outcome is what
# never arrives.
FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

# The v1 view: the registry exactly as Piece A2 settled it.
_TOOLS_V1 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content", "hang_seconds"},
    },
})

# The v2 view: v1's ceiling contract, unchanged, plus the
# worker-facing layer (Piece A3-CAT): a plain description of
# what the tool does and returns, and a parameter schema —
# each parameter's name, whether it is required, and its
# meaning. The parameter lists name exactly the tool's
# param_keys; the A2 suite's agreement battery witnesses the
# two copies agree on all of it, under both versions.
_TOOLS_V2 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
        "description":
            "Write a text file inside the sandbox: creates "
            "the file at the given path (with any folders it "
            "needs) or replaces it, storing exactly the given "
            "content. Returns the path written and the number "
            "of bytes stored.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "content", "required": True,
             "meaning": "the text to store in the file"},
        ],
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "Read a text file inside the sandbox. Returns "
            "the file's path and its full text content.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
        ],
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content",
                       "hang_seconds"},
        "description":
            "A test tool whose behaviour its mode parameter "
            "sets, so uncertain outcomes are exercised for "
            "real: 'succeed' performs (writing the file when "
            "a path is given) and reports its result; 'fail' "
            "fails; 'hang-past-deadline' runs past the "
            "deadline, so its outcome is recorded uncertain; "
            "'execute-but-lose-the-report' performs the "
            "operation but its report never arrives, so its "
            "outcome is recorded uncertain. Returns the mode, "
            "and the write's result when it wrote.",
        "parameters": [
            {"name": "mode", "required": True,
             "meaning": "one of 'succeed', 'fail', "
                        "'hang-past-deadline', "
                        "'execute-but-lose-the-report'"},
            {"name": "path", "required": False,
             "meaning": "a file path inside the sandbox to "
                        "write, for the modes that write"},
            {"name": "content", "required": False,
             "meaning": "the text to store when writing"},
            {"name": "hang_seconds", "required": False,
             "meaning": "how long the 'hang-past-deadline' "
                        "mode runs, in seconds (a positive "
                        "number)"},
        ],
    },
})

# The v3 view (retrieval piece): v2's entries for the
# standing tools, unchanged word for word, plus the three
# retrieval tools with their worker-facing layers. A v3
# assembly's catalogue therefore describes its standing
# tools exactly as v2 did, and its retrieval tools in the
# same style.
_TOOLS_V3 = _freeze({
    "sandbox.write": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "content"},
        "description":
            "Write a text file inside the sandbox: creates "
            "the file at the given path (with any folders it "
            "needs) or replaces it, storing exactly the given "
            "content. Returns the path written and the number "
            "of bytes stored.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "content", "required": True,
             "meaning": "the text to store in the file"},
        ],
    },
    "sandbox.read": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "Read a text file inside the sandbox. Returns "
            "the file's path and its full text content.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
        ],
    },
    "sandbox.flaky": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"mode", "path", "content",
                       "hang_seconds"},
        "description":
            "A test tool whose behaviour its mode parameter "
            "sets, so uncertain outcomes are exercised for "
            "real: 'succeed' performs (writing the file when "
            "a path is given) and reports its result; 'fail' "
            "fails; 'hang-past-deadline' runs past the "
            "deadline, so its outcome is recorded uncertain; "
            "'execute-but-lose-the-report' performs the "
            "operation but its report never arrives, so its "
            "outcome is recorded uncertain. Returns the mode, "
            "and the write's result when it wrote.",
        "parameters": [
            {"name": "mode", "required": True,
             "meaning": "one of 'succeed', 'fail', "
                        "'hang-past-deadline', "
                        "'execute-but-lose-the-report'"},
            {"name": "path", "required": False,
             "meaning": "a file path inside the sandbox to "
                        "write, for the modes that write"},
            {"name": "content", "required": False,
             "meaning": "the text to store when writing"},
            {"name": "hang_seconds", "required": False,
             "meaning": "how long the 'hang-past-deadline' "
                        "mode runs, in seconds (a positive "
                        "number)"},
        ],
    },
    "sandbox.list": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path"},
        "description":
            "List what stands at a path inside the sandbox "
            "without returning any file's contents. On a "
            "file: its structure — its byte size, its line "
            "count, and — for markdown or text files — its "
            "headings with their line numbers. On a "
            "directory — a granted prefix itself, such as "
            "sources, spelled with or without a trailing "
            "slash: its entries — each entry's address, "
            "whether it is a file or a directory, and each "
            "file's byte size. The map is returned as the "
            "result's content. Use it to discover what "
            "stands where before retrieving any of it.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the path inside the sandbox, "
                        "relative, under the grant's prefix — "
                        "a file's path, or a granted "
                        "directory's own path"},
        ],
    },
    "sandbox.read_range": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"path", "start_line", "end_line",
                       "heading", "byte_start", "byte_end"},
        "description":
            "Retrieve a bounded slice of a text file inside "
            "the sandbox: the lines of an inclusive 1-based "
            "line range, or one heading's section (from its "
            "heading line to just before the next heading of "
            "the same or higher level), or — for a "
            "single-line range — a byte window of that line. "
            "A result is never larger than 12,000 bytes: a "
            "range whose content exceeds the ceiling is "
            "refused with the bound named, and nothing "
            "partial is returned. A heading naming more "
            "than one heading is refused as ambiguous, "
            "naming the matches and their line numbers. A "
            "byte window may span at most 11,997 bytes; the "
            "slice served is aligned to character "
            "boundaries, and the window actually served is "
            "recorded in the result.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
            {"name": "start_line", "required": False,
             "meaning": "the range's first line, numbered "
                        "from 1; given with end_line when no "
                        "heading is named"},
            {"name": "end_line", "required": False,
             "meaning": "the range's last line, inclusive; "
                        "given with start_line when no "
                        "heading is named"},
            {"name": "heading", "required": False,
             "meaning": "the exact text of the one heading "
                        "whose section to retrieve; refused "
                        "when it matches more than one "
                        "heading"},
            {"name": "byte_start", "required": False,
             "meaning": "for a single-line range, the byte "
                        "window's start within the line, "
                        "0-based and inclusive; given with "
                        "byte_end"},
            {"name": "byte_end", "required": False,
             "meaning": "for a single-line range, the byte "
                        "window's end within the line, "
                        "0-based and exclusive; given with "
                        "byte_start"},
        ],
    },
    "sandbox.search": {
        "ceiling_keys": {"path_prefix"},
        "param_keys": {"query", "path", "offset"},
        "description":
            "Search permitted text inside the sandbox for a "
            "query string (an exact, case-sensitive "
            "substring) and return matching passages — each "
            "matching line with up to two lines of context, "
            "labelled with its file and line numbers. "
            "Matches are ordered by path, then by line, and "
            "returned in deterministic pages under the "
            "result ceiling and a 40-line page cap: every "
            "result states the total match count, how many "
            "matches it returns, and — where more remain — "
            "the continuation offset to pass back as the "
            "offset parameter for the next page. A matching "
            "line too large to return even on its own is "
            "reported as a stub — its path, line number and "
            "byte size, with no content — which "
            "sandbox.read_range can fetch in byte-window "
            "slices. With no path, the search covers the "
            "case's sealed source material; with a path, it "
            "searches that one file.",
        "parameters": [
            {"name": "query", "required": True,
             "meaning": "the exact text to search for "
                        "(case-sensitive)"},
            {"name": "path", "required": False,
             "meaning": "one file to search, under the "
                        "grant's prefix; without it, the "
                        "sealed source material is searched"},
            {"name": "offset", "required": False,
             "meaning": "the continuation offset a previous "
                        "search result returned: the match "
                        "index the next page starts at"},
        ],
    },
})

# The v4 view (room-exec configuration, gate 4): v3's entries
# whole and unchanged — taken from the frozen v3 view itself, so
# the two views cannot drift — plus the one new tool. An
# assembly declaring the exec catalogue contract is catalogued
# and dispatched under v4, exactly as a retrieval assembly is
# under v3; every other assembly keeps the version it has
# always had.
_TOOLS_V4 = _freeze({
    **_TOOLS_V3,
    "container.exec": {
        "ceiling_keys": set(),
        "param_keys": {"cmd"},
        "description":
            "Execute one command inside your office — the "
            "sealed room stocked for this task — and return "
            "its result: the exit status, the captured "
            "output (bounded, with the full byte counts and "
            "any truncation flagged), what ended it, the "
            "CPU charged and the duration. Commands run "
            "with the working directory at /room/work: the "
            "sources stand under sources/, your own space "
            "is /room/scratch, and the deliverable is "
            "written there. Nothing outside the room is "
            "reachable from inside it.",
        "parameters": [
            {"name": "cmd", "required": True,
             "meaning": "the command to execute, as an "
                        "array of strings: the program "
                        "followed by its arguments"},
        ],
    },
})

# One registry view per version, v1 preserved immutable for
# historical verification (Piece A3-CAT settlement (a)/(c)) —
# the version map itself is frozen with its views, so a
# version can neither be altered nor added in-process.
_REGISTRIES = MappingProxyType({
    "tool-registry-v1": _TOOLS_V1,
    "tool-registry-v2": _TOOLS_V2,
    "tool-registry-v3": _TOOLS_V3,
    "tool-registry-v4": _TOOLS_V4,
})

# The current view: what an unversioned call applies. This
# is the frozen v2 view itself, not a mutable alias to it.
_TOOLS = _TOOLS_V2


def known_version(version) -> bool:
    """Whether the registry holds a view under this version
    at all. A version nobody holds is unverifiable: callers
    fail closed or report the inability explicitly, never
    silently apply another version."""
    return version in _REGISTRIES


def _view(version):
    """The registry view a call applies: the current version
    where none is named; None for a version nobody holds."""
    if version is None:
        version = REGISTRY_VERSION
    return _REGISTRIES.get(version)


def registered(tool, version=None) -> bool:
    """Whether the registry knows this tool at all, under the
    named version (the current version where none is named).
    An unregistered tool is refused at the doorway and
    divergent in the checker: registration is the precondition
    of a grant meaning anything."""
    view = _view(version)
    return view is not None and tool in view


def worker_facing(tool, version=None):
    """The tool's worker-facing layer under the named
    version — {"description": ..., "parameters": [...]} —
    or None where the tool is unknown under that version or
    its entry carries no complete layer. v1 entries carry
    none: under v1 no catalogue can be derived, which is a
    fact about v1, not a defect in it. The result is a copy;
    the registry's own data never leaves this module by
    reference."""
    view = _view(version)
    if view is None:
        return None
    spec = view.get(tool)
    if spec is None:
        return None
    description = spec.get("description")
    parameters = spec.get("parameters")
    if not isinstance(description, str) or \
            not description.strip() or \
            not isinstance(parameters, (list, tuple)):
        return None
    names = set()
    for param in parameters:
        if not isinstance(param, Mapping) or \
                set(param) != {"name", "required", "meaning"} \
                or not isinstance(param.get("name"), str) \
                or not param["name"] \
                or not isinstance(param.get("required"), bool) \
                or not isinstance(param.get("meaning"), str) \
                or not param["meaning"].strip():
            return None
        names.add(param["name"])
    if names != set(spec["param_keys"]):
        return None
    # A plain, mutable copy, rebuilt field by field: the
    # frozen registry's own structures never leave by
    # reference (and cannot be deep-copied in any case).
    return {"description": description,
            "parameters": [
                {"name": param["name"],
                 "required": param["required"],
                 "meaning": param["meaning"]}
                for param in parameters]}


def request_fingerprint(tool, parameters) -> str:
    """The canonical fingerprint a request identity binds to
    (R47, scope point 3): SHA-256 over the fabric canonical
    form of the tool and the parameters together. Same tool,
    same parameters — same fingerprint, wherever computed."""
    return sha256_hex(canonical(
        {"tool": tool, "parameters": parameters}))


def _path_problem(path, prefix, allow_prefix_itself=False):
    """Why a sandbox path may not be used, or None: the path
    is a relative, normalised file path inside the sandbox —
    no absolute paths, no empty, dot or dot-dot segments — and,
    where the ceiling names a prefix, it lies strictly under
    that prefix. Where allow_prefix_itself stands (sandbox.list's
    directory form, round ten): the path may also BE the prefix
    itself — the granted directory's own address."""
    if not isinstance(path, str) or not path:
        return "the path is not a non-empty string"
    if path.startswith("/"):
        return f"path {path!r} is absolute; sandbox paths are " \
            "relative to the sandbox directory"
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return f"path {path!r} is not a normalised relative " \
            "path inside the sandbox"
    if prefix is not None:
        if not isinstance(prefix, str) or not prefix:
            return "the ceiling's path_prefix is not a " \
                "non-empty string"
        prefix_parts = [p for p in prefix.split("/") if p]
        if parts[:len(prefix_parts)] != prefix_parts or \
                len(parts) < len(prefix_parts) or \
                (len(parts) == len(prefix_parts)
                 and not allow_prefix_itself):
            return f"path {path!r} lies outside the grant's " \
                f"ceiling prefix {prefix!r}"
    return None


def _read_range_problem(parameters):
    """Why sandbox.read_range's parameters may not be used,
    or None (retrieval scope §2): exactly one selection — a
    heading, or an inclusive 1-based line range — and a byte
    window only on a single-line range, spanning at most the
    per-result ceiling minus 3 bytes, so the served slice
    (its end extended at most 3 bytes to a character
    boundary) never exceeds the ceiling. Pure, of the
    parameters only; the same result at the doorway and in
    the checker."""
    heading = parameters.get("heading")
    if heading is not None:
        if not isinstance(heading, str) or not heading:
            return ("sandbox.read_range's heading is not a "
                    "non-empty string")
        for key in ("start_line", "end_line", "byte_start",
                    "byte_end"):
            if key in parameters:
                return (f"sandbox.read_range names a heading "
                        f"and {key}; a request selects by "
                        f"heading or by line range, never both")
        return None
    start = parameters.get("start_line")
    end = parameters.get("end_line")
    if start is None or end is None:
        return ("sandbox.read_range requires a heading, or "
                "both start_line and end_line")
    for name, value in (("start_line", start),
                        ("end_line", end)):
        if isinstance(value, bool) or \
                not isinstance(value, int) or value < 1:
            return (f"sandbox.read_range's {name} is not a "
                    f"positive integer (lines are numbered "
                    f"from 1)")
    if end < start:
        return ("sandbox.read_range's end_line precedes its "
                "start_line")
    has_start = "byte_start" in parameters
    has_end = "byte_end" in parameters
    if has_start != has_end:
        return ("sandbox.read_range's byte window names both "
                "byte_start and byte_end, or neither")
    if has_start:
        if start != end:
            return ("sandbox.read_range's byte window "
                    "applies to a single-line range only")
        byte_start = parameters["byte_start"]
        byte_end = parameters["byte_end"]
        for name, value in (("byte_start", byte_start),
                            ("byte_end", byte_end)):
            if isinstance(value, bool) or \
                    not isinstance(value, int) or value < 0:
                return (f"sandbox.read_range's {name} is not "
                        f"a non-negative integer")
        if byte_end <= byte_start:
            return ("sandbox.read_range's byte_end does not "
                    "exceed its byte_start")
        if byte_end - byte_start > \
                RETRIEVAL_RESULT_CEILING - 3:
            return (f"sandbox.read_range's byte window spans "
                    f"{byte_end - byte_start} bytes; the "
                    f"maximum requestable window is "
                    f"{RETRIEVAL_RESULT_CEILING - 3} bytes "
                    f"(the per-result ceiling minus 3, so "
                    f"the served slice — its end extended at "
                    f"most 3 bytes to a character boundary — "
                    f"never exceeds the ceiling)")
    return None


def check_ceiling(tool, ceiling, parameters, version=None):
    """The pure ceiling contract: (ok, ground). Applies the
    named tool's registered checker to the grant's ceiling and
    the request's parameters, under the named version's view
    (the current version where none is named). Deterministic,
    fail-closed, no execution — the same result at the doorway
    and in the checker, or the piece is wrong. The ceiling
    behaviour is identical under v1 and v2 (A3-CAT changed
    only the worker-facing layer); a version nobody holds
    fails closed, naming itself."""
    if version is None:
        version = REGISTRY_VERSION
    view = _REGISTRIES.get(version)
    if view is None:
        return False, (f"registry version {version!r} is not "
                       f"a version this registry holds; the "
                       f"ceiling check fails closed")
    spec = view.get(tool)
    if spec is None:
        return False, (f"tool {tool!r} is not in the tool "
                       f"registry ({version}); an "
                       f"unregistered tool is refused")
    if not isinstance(ceiling, dict):
        return False, (f"the grant's scope ceiling for {tool} "
                       f"is not structured data; the ceiling "
                       f"check fails closed")
    for key in ceiling:
        if key not in spec["ceiling_keys"]:
            return False, (f"ceiling key {key!r} is not "
                           f"understood by {tool}'s checker; "
                           f"unknown constraint keys fail closed")
    if not isinstance(parameters, dict):
        return False, "the request's parameters are not an object"
    for key in parameters:
        if key not in spec["param_keys"]:
            return False, (f"parameter {key!r} is not a "
                           f"parameter of {tool}; unknown "
                           f"parameters fail closed")
    prefix = ceiling.get("path_prefix")
    if tool in ("sandbox.write", "sandbox.read"):
        if "path" not in parameters:
            return False, f"{tool} requires a path parameter"
        problem = _path_problem(parameters.get("path"), prefix)
        if problem is not None:
            return False, problem
        if tool == "sandbox.write" and \
                not isinstance(parameters.get("content"), str):
            return False, ("sandbox.write requires its content "
                           "parameter to be a string")
    elif tool == "sandbox.flaky":
        mode = parameters.get("mode")
        if mode not in FLAKY_MODES:
            return False, (f"sandbox.flaky's mode {mode!r} is "
                           f"not one of {list(FLAKY_MODES)}")
        if "path" in parameters:
            problem = _path_problem(parameters.get("path"),
                                    prefix)
            if problem is not None:
                return False, problem
            if "content" in parameters and \
                    not isinstance(parameters["content"], str):
                return False, ("sandbox.flaky's content "
                               "parameter is not a string")
        if "hang_seconds" in parameters:
            hang = parameters["hang_seconds"]
            if isinstance(hang, bool) or \
                    not isinstance(hang, (int, float)) or \
                    not hang > 0:
                return False, ("sandbox.flaky's hang_seconds "
                               "is not a positive number")
    elif tool == "sandbox.list":
        if "path" not in parameters:
            return False, "sandbox.list requires a path parameter"
        # The directory form (round ten): a list path is
        # canonicalised before the ceiling is applied —
        # exactly one trailing slash is stripped, so the
        # granted directory's two spellings ("sources" and
        # "sources/") meet the one governed route — and the
        # path may be the grant's prefix itself, the
        # directory's own address. Every other tool keeps
        # the strict shape: strictly under the prefix, no
        # spelling forgiven.
        list_path = parameters.get("path")
        if isinstance(list_path, str) and len(list_path) > 1 \
                and list_path.endswith("/"):
            list_path = list_path[:-1]
        problem = _path_problem(list_path, prefix,
                                allow_prefix_itself=True)
        if problem is not None:
            return False, problem
    elif tool == "sandbox.read_range":
        if "path" not in parameters:
            return False, ("sandbox.read_range requires a "
                           "path parameter")
        problem = _path_problem(parameters.get("path"), prefix)
        if problem is not None:
            return False, problem
        problem = _read_range_problem(parameters)
        if problem is not None:
            return False, problem
    elif tool == "sandbox.search":
        query = parameters.get("query")
        if not isinstance(query, str) or not query:
            return False, ("sandbox.search requires its query "
                           "parameter to be a non-empty string")
        if "path" in parameters:
            problem = _path_problem(parameters.get("path"),
                                    prefix)
            if problem is not None:
                return False, problem
        if "offset" in parameters:
            offset = parameters["offset"]
            if isinstance(offset, bool) or \
                    not isinstance(offset, int) or offset < 0:
                return False, ("sandbox.search's offset is "
                               "not a non-negative integer")
    elif tool == "container.exec":
        # The shape check, and the only one (demonstration
        # preparation paper §2.2): cmd present, an array of
        # strings. The command's contents are not policed
        # here or anywhere at the doorway — what it may do
        # is the room's governance, not the doorway's.
        cmd = parameters.get("cmd")
        if not isinstance(cmd, list) or not cmd:
            return False, ("container.exec requires its cmd "
                           "parameter to be a non-empty array "
                           "of strings")
        if any(not isinstance(part, str) for part in cmd):
            return False, ("container.exec's cmd array holds "
                           "a non-string element; every "
                           "element of cmd must be a string")
    return True, ""
