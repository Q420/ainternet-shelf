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
"""
from fabric.canonical import canonical, sha256_hex

# The registry's version identifier: inspectable, and pinned
# for a run by being recorded in every TOOL_DISPATCHED the
# doorway issues — the version is part of the dispatch
# contract, so which policy governed a historical dispatch is
# established from the record, not from whatever source
# happens to be present at replay (Piece A2, correction
# round 1). Both copies carry it; the suite witnesses that
# they agree, and the checker refuses to verify a dispatch
# recorded under a version other than its own.
REGISTRY_VERSION = "tool-registry-v1"

# sandbox.flaky's modes (scope point 6): the first three are
# the outcome shapes; the fourth performs the operation and
# loses the report — execution happened, the outcome is what
# never arrives.
FLAKY_MODES = ("succeed", "fail", "hang-past-deadline",
               "execute-but-lose-the-report")

_TOOLS = {
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


def registered(tool) -> bool:
    """Whether the registry knows this tool at all. An
    unregistered tool is refused at the doorway and divergent
    in the checker: registration is the precondition of a grant
    meaning anything."""
    return tool in _TOOLS


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


def check_ceiling(tool, ceiling, parameters):
    """The pure ceiling contract: (ok, ground). Applies the
    named tool's registered checker to the grant's ceiling and
    the request's parameters. Deterministic, fail-closed, no
    execution — the same result at the doorway and in the
    checker, or the piece is wrong."""
    spec = _TOOLS.get(tool)
    if spec is None:
        return False, (f"tool {tool!r} is not in the tool "
                       f"registry ({REGISTRY_VERSION}); an "
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
