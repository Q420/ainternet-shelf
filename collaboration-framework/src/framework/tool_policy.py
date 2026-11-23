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
"""
import copy

from fabric.canonical import canonical, sha256_hex

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

# sandbox.flaky's modes (scope point 6): the first three are
# the outcome shapes; the fourth performs the operation and
# loses the report — execution happened, the outcome is what
# never arrives.
FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

# The v1 view: the registry exactly as Piece A2 settled it.
_TOOLS_V1 = {
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
}

# The v2 view: v1's ceiling contract, unchanged, plus the
# worker-facing layer (Piece A3-CAT): a plain description of
# what the tool does and returns, and a parameter schema —
# each parameter's name, whether it is required, and its
# meaning. The parameter lists name exactly the tool's
# param_keys; the A2 suite's agreement battery witnesses the
# two copies agree on all of it, under both versions.
_TOOLS_V2 = {
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
}

# One registry view per version, v1 preserved immutable for
# historical verification (Piece A3-CAT settlement (a)/(c)).
_REGISTRIES = {
    "tool-registry-v1": _TOOLS_V1,
    "tool-registry-v2": _TOOLS_V2,
}

# The current view: what an unversioned call applies.
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
            not isinstance(parameters, list):
        return None
    names = set()
    for param in parameters:
        if not isinstance(param, dict) or \
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
    return {"description": description,
            "parameters": copy.deepcopy(parameters)}


def request_fingerprint(tool, parameters) -> str:
    """The canonical fingerprint a request identity binds to
    (R47, scope point 3): SHA-256 over the fabric canonical
    form of the tool and the parameters together. Same tool,
    same parameters — same fingerprint, wherever computed."""
    return sha256_hex(canonical(
        {"tool": tool, "parameters": parameters}))


def _path_problem(path, prefix):
    """Why a sandbox path may not be used, or None: the path
    is a relative, normalised file path inside the sandbox —
    no absolute paths, no empty, dot or dot-dot segments — and,
    where the ceiling names a prefix, it lies strictly under
    that prefix."""
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
    return True, ""
