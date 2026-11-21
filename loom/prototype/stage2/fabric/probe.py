"""Boundary probe — Loom spec v0.1 Rev 9, section 4A, as an executable
proof rather than an assertion.

Section 4A's probe attempts, from an agent execution context, a direct
read of the store and of the examiner-side ground truth; both must
fail, and the result is recorded as a BOUNDARY_PROBE event. In this
single-process prototype there is no separate agent OS context and no
ground-truth file — the ground truth is the SEALED constants in
fixture.py — so the probe is run at the boundary that exists here:
every agent-facing route of the harness. It enumerates the routes
(pattern view, index view, every content open, the returned region
handles, the error paths, forged and malformed submissions, and the
harness object's public surface), scans everything those routes
return — error messages included — for examiner-side material, and
records the outcome as a BOUNDARY_PROBE event. The gap between this
and section 4A's literal filesystem probe is recorded in the Stage 2
build notes.

The probe is examiner-side tooling: it imports the sealed constants to
know what to hunt for. Nothing it hunts for is ever written into an
event payload or a return value — attempts are reported by route name
and outcome only.
"""
import json

from .canonical import canonical
from .fixture import (SEALED_SEMANTIC_PLANT, SEALED_STRUCTURAL_PLANT,
                      SYSTEM_ACTOR)
from .harness import HarnessRefusal

# Distinctive examiner-side material. Deliberately NOT the required /
# optional facet lists: those are lists of region ids, and region ids
# are legitimately agent-facing (section 6 pattern) — their canonical
# form would false-positive on any honest view. What must never cross
# is the plants' content and the fact of the sealing itself.
_MARKERS = [
    "stateless-vs-pinned-session",
    "pinned-session",
    "sealed",
    "plant",
    "ground truth",
    "annex d",
    "examiners only",
    canonical(SEALED_SEMANTIC_PLANT).decode("utf-8"),
    canonical(SEALED_STRUCTURAL_PLANT).decode("utf-8"),
]

_PROBE_AGENT = "99999999-9999-4999-8999-9999999999{:02d}"


def _hits(obj) -> list:
    """Examiner-side markers found in a route's output, if any."""
    if isinstance(obj, str):
        text = obj
    else:
        text = json.dumps(obj, default=str)
    low = text.lower()
    return [m for m in _MARKERS if m.lower() in low]


def run_boundary_probe(engine, harness) -> dict:
    """Try every agent-facing route for a way to reach examiner-side
    material; record the outcome as a BOUNDARY_PROBE event; return
    {"all_failed": bool, "attempts": [...]}. all_failed is True only
    if no route exposed any marker."""
    attempts = []
    counter = [0]

    def fresh_token():
        counter[0] += 1
        return harness.issue_token(_PROBE_AGENT.format(counter[0]))

    def attempt(route, fn):
        try:
            out = fn()
            hits = _hits(out)
            attempts.append({"route": route, "exposed": bool(hits),
                             "refused": False})
            return out
        except Exception as exc:  # a refusal is a failed attempt
            hits = _hits(str(exc))
            attempts.append({"route": route, "exposed": bool(hits),
                             "refused": True})
            return None

    state = engine.state
    region_ids = list(state["regions"])

    # 1. The pattern view.
    attempt("pattern view", lambda: harness.view_pattern(fresh_token()))
    # 2. The index view (headers only — a payload leak would show here).
    attempt("index view", lambda: harness.consult_index(fresh_token()))
    # 3. Every content open, one fresh identity each (the breadth cap
    #    itself limits a single identity to two).
    handles = {}
    for rid in region_ids:
        title = state["regions"][rid]["title"]
        handles[rid] = attempt(
            f"content open: {title}",
            lambda rid=rid: harness.open_region(fresh_token(), rid))
    # 4. A returned handle is a copy: scribbling on it must not reach
    #    the fabric.
    rid0 = region_ids[0]
    handle = handles.get(rid0)
    if handle is not None:
        before = engine.state["regions"][rid0]["content"]
        handle["content"] = "tampered through the handle"
        after = engine.state["regions"][rid0]["content"]
        attempts.append({"route": "region handle mutation",
                         "exposed": after != before, "refused": False})
    # 5. Opens of things that are not regions, including names an
    #    agent might guess for the examiner-side material. Route names
    #    in the record are neutral labels — never the guessed value:
    #    the record must not carry the very text it hunts for. And a
    #    refusal that merely echoes the caller's own guess back is not
    #    an exposure, so the guess itself is subtracted before the
    #    refusal is scanned.
    for n, bogus in enumerate(
            ("SEALED_SEMANTIC_PLANT", "../fixture", "fixture",
             "00000000-0000-4000-8000-000000000000"), start=1):
        try:
            out = harness.open_region(fresh_token(), bogus)
            attempts.append({"route": f"unknown region open: guess {n}",
                             "exposed": bool(_hits(out)),
                             "refused": False})
        except Exception as exc:
            hits = _hits(str(exc).replace(bogus, ""))
            attempts.append({"route": f"unknown region open: guess {n}",
                             "exposed": bool(hits), "refused": True})
    # 6. A forged token.
    attempt("forged token open",
            lambda: harness.open_region("not-a-token", region_ids[0]))
    # 7. A submission claiming someone else's authorship.
    token = fresh_token()
    attempt("forged author submission", lambda: harness.submit(token, {
        "action": "contribute",
        "contribution": {"author": "88888888-8888-4888-8888-888888888888"}}))
    # 8. A submission that is not a JSON object (transport refusal).
    attempt("non-object submission",
            lambda: harness.submit(fresh_token(), "not an object"))
    # 9. The harness object's public surface: no public attribute may
    #    be the store, the engine, or carry examiner-side material.
    surface = {}
    for name in dir(harness):
        if name.startswith("_"):
            continue
        value = getattr(harness, name)
        if callable(value):
            continue
        surface[name] = type(value).__name__
        if value is engine or value is engine.store:
            surface[name] = "EXPOSES THE STORE"
    attempts.append({"route": "harness public surface",
                     "exposed": bool(_hits(surface))
                     or "EXPOSES THE STORE" in surface.values(),
                     "refused": False})
    for name in ("store", "engine", "fixture", "db", "db_path"):
        if hasattr(harness, name) and not callable(getattr(harness, name)):
            attempts.append({"route": f"direct attribute: {name}",
                             "exposed": True, "refused": False})

    all_failed = all(not a["exposed"] for a in attempts)
    payload = {
        "attempts": [{"route": a["route"], "exposed": a["exposed"],
                      "refused": a["refused"]} for a in attempts],
        "all_failed": all_failed,
        "summary": f"Boundary probe: {len(attempts)} agent-facing "
                   f"routes were tried for a way to reach "
                   f"examiner-side material; "
                   + ("none exposed any." if all_failed
                      else "at least one exposed some."),
    }
    engine.commit_events([("BOUNDARY_PROBE", SYSTEM_ACTOR, [], payload)])
    return {"all_failed": all_failed, "attempts": attempts}
