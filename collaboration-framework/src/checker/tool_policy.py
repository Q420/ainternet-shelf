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
"""
import copy

from fabric.canonical import canonical, sha256_hex

REGISTRY_VERSION = "tool-registry-v2"

FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

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

_REGISTRIES = {
    "tool-registry-v1": _TOOLS_V1,
    "tool-registry-v2": _TOOLS_V2,
}

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
    return True, ""
