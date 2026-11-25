"""The checker's copy of the tool policy contract — Piece A2
(SPEC SHEET Rev 6, R44/R47/R48).

The pure ceiling contract the doorway enforces at the grant
check, held here independently so the checker can validate
recorded requests against the grants that actually stood —
without importing the framework's copy (Piece 7's C1 audits
witness that importing the checker loads no `framework.*`
module) and without executing any tool (R48: replay knows
recorded outcomes only). Exactly as with the projection schema
(Piece 7, C3), the contract lives in two copies; the Piece A2
suite witnesses their agreement — registry version included —
over a battery of (tool, ceiling, parameters) cases.

The contract: deterministic functions of (tool, ceiling,
parameters); fail closed; unknown tools, unknown ceiling keys
and unknown parameters refused. The registry is policy, never
authority: a registered tool is granted only per worker, per
case, in the sealed assembly record.

Piece A3-CAT: the registry is held as one view per version —
`tool-registry-v1` exactly as Piece A2 settled it (no
worker-facing layer), preserved immutable so a dispatch
recorded under it is verified under it; `tool-registry-v2`,
v1's ceiling contract unchanged plus the worker-facing layer
(a plain description and a parameter schema per tool). Every
function takes the version it applies; an unknown version
fails closed, and a version this copy does not hold for
catalogue reconstruction is an explicit inability to verify,
never a silent ok.

The versioned views are frozen deeply at module load (A3-CAT
correction round), exactly as in the framework copy: every
mapping a MappingProxyType, every list a tuple, every set a
frozenset — no caller can alter a version's contract for the
lifetime of the process. Accessors return plain copies.
"""
from collections.abc import Mapping
from types import MappingProxyType

from fabric.canonical import canonical, sha256_hex


def _freeze(value):
    """The deeply immutable form of a registry structure
    (the framework copy's helper, duplicated as the contract
    is): mappings become MappingProxyType, lists and tuples
    become tuples of frozen items, sets become frozensets;
    scalars pass through."""
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(value)
    return value


REGISTRY_VERSION = "tool-registry-v2"

# The retrieval piece's contract data (RETRIEVAL-SCOPE
# Rev 5), duplicated from the framework copy as the contract
# is: the registry version a retrieval-governed assembly is
# verified under, its catalogue contract value, the
# per-result and aggregate ceilings, the search page cap,
# the governed tool set, and the two scope prefixes.
# REGISTRY_VERSION stays v2: v3 governs only where an
# assembly's sealed record declares the retrieval contract.
RETRIEVAL_REGISTRY_VERSION = "tool-registry-v3"
RETRIEVAL_CATALOGUE_CONTRACT = "retrieval-v3"
RETRIEVAL_RESULT_CEILING = 12000
RETRIEVAL_AGGREGATE_CEILING = 36000
# Working-set carriage (the run-3 correction, examiner's
# ruling 2026-11-24): the checker's own copy of the working
# set's aggregate content budget — the bound its independent
# reconstruction of a presented working set applies. The
# framework copy states the figure's grounds.
WORKING_SET_CONTENT_BUDGET = 64000
SEARCH_PAGE_LINE_CAP = 40
RETRIEVAL_TOOLS = frozenset({
    "sandbox.list", "sandbox.read_range", "sandbox.search",
    "sandbox.read"})
SOURCE_SCOPE_PREFIX = "sources"
SCRATCH_SCOPE_PREFIX = "scratch"

# The room-exec configuration's contract data (demonstration
# preparation paper §2/§3.2; gate 4), duplicated from the
# framework copy as the contract is: the registry version an
# assembly declaring the exec catalogue contract is verified
# under, its catalogue contract value, and the governed tool
# — the worker's own execution tool, `container.exec`, whose
# doorway check is the grant and the cmd array's shape alone.
EXEC_REGISTRY_VERSION = "tool-registry-v4"
EXEC_CATALOGUE_CONTRACT = "exec-v4"
EXEC_TOOLS = frozenset({"container.exec"})


def retrieval_authority(path):
    """The authority path a sandbox path falls under, or
    None: "source" under sources/, "scratch" under
    scratch/, None anywhere else (the framework copy's
    helper, duplicated as the contract is)."""
    if not isinstance(path, str):
        return None
    if path.startswith(SOURCE_SCOPE_PREFIX + "/"):
        return "source"
    if path.startswith(SCRATCH_SCOPE_PREFIX + "/"):
        return "scratch"
    return None


def boundary_member(boundary, path) -> bool:
    """Whether a path is a member of a case's sealed evidence
    boundary: an id names its path exactly, or as its leading
    field (the path, then the material's hash, in the one
    id)."""
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

FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

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
            "List a text file's structure inside the sandbox "
            "without returning its contents: its byte size, "
            "its line count, and — for markdown or text "
            "files — its headings with their line numbers. "
            "The structure map is returned as the result's "
            "content. Use it to discover what a file holds "
            "before retrieving any of it.",
        "parameters": [
            {"name": "path", "required": True,
             "meaning": "the file's path inside the sandbox, "
                        "relative, under the grant's prefix"},
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
# whole and unchanged — taken from the frozen v3 view itself,
# as the framework copy takes them — plus the one new tool.
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

_REGISTRIES = MappingProxyType({
    "tool-registry-v1": _TOOLS_V1,
    "tool-registry-v2": _TOOLS_V2,
    "tool-registry-v3": _TOOLS_V3,
    "tool-registry-v4": _TOOLS_V4,
})

# The frozen v2 view itself, not a mutable alias to it.
_TOOLS = _TOOLS_V2


def known_version(version) -> bool:
    return version in _REGISTRIES


def _view(version):
    if version is None:
        version = REGISTRY_VERSION
    return _REGISTRIES.get(version)


def registered(tool, version=None) -> bool:
    view = _view(version)
    return view is not None and tool in view


def worker_facing(tool, version=None):
    """The tool's worker-facing layer under the named
    version, or None where the tool is unknown there or its
    entry carries no complete layer (under v1, always None).
    The completeness rule is the framework copy's, exactly:
    a non-empty description and a parameter schema naming
    exactly the tool's parameters, each with a name, a
    required flag and a meaning."""
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
    # A plain, mutable copy, rebuilt field by field (the
    # framework copy's rule, exactly).
    return {"description": description,
            "parameters": [
                {"name": param["name"],
                 "required": param["required"],
                 "meaning": param["meaning"]}
                for param in parameters]}


def request_fingerprint(tool, parameters) -> str:
    """The canonical fingerprint a request identity binds to:
    SHA-256 over the fabric canonical form of tool + parameters,
    recomputed here from the recorded request itself."""
    return sha256_hex(canonical(
        {"tool": tool, "parameters": parameters}))


def _path_problem(path, prefix):
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
                len(parts) <= len(prefix_parts):
            return f"path {path!r} lies outside the grant's " \
                f"ceiling prefix {prefix!r}"
    return None


def _read_range_problem(parameters):
    """Why sandbox.read_range's parameters may not be used,
    or None (the framework copy's helper, duplicated as the
    contract is): exactly one selection — a heading, or an
    inclusive 1-based line range — and a byte window only on
    a single-line range, spanning at most the per-result
    ceiling minus 3 bytes."""
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
    """(ok, ground): the recorded request against the grant,
    under the named version's view — the contract the doorway
    applied when the dispatch was recorded (v1 records are
    verified under v1, never reinterpreted)."""
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
        problem = _path_problem(parameters.get("path"), prefix)
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
