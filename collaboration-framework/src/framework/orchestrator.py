"""Orchestrator functions — SPEC SHEET §3.8, R26/R35/R36
(Piece 6, third part).

The derivations this piece adds over the fold, per the approved
scope (src/PIECE6-ORCHESTRATOR-SCOPE-REV3-2026-11-22.md). Like
the gates derivations, everything here is a pure function of
the recorded history: replay reproduces it, and no derivation
is ever recorded as an act. The doorway enforces the mechanical
rules from these derivations; substantive judgement — whether
a mapping is right, whether readiness is warranted, whether a
certification's conclusions hold — remains where the design
puts it: with the examiner, the director, and the seats.
"""


def identity_status_of(state, seat_id):
    """A seat's derived identity status (§3.6's fold): the
    onboarding record's status where one stands; a seat with no
    onboarding record is `unverified` — never a status borrowed
    from a binding or a caller's assertion."""
    rec = (state.get("onboarding") or {}).get(seat_id)
    if rec is None:
        return "unverified"
    return rec.get("identity_status", "unverified")


def certification_coverage(state, covers_parts):
    """R36's derived coverage: the seats whose contributions a
    certification over `covers_parts` covers, each with its
    derived identity status. `covers_parts` None means the whole
    run — every contribution, on any part or the job. Otherwise
    only contributions on the named parts. A seat contributing
    on several covered parts appears once."""
    covered = {}
    for contribution in (state.get("contributions") or {}).values():
        if covers_parts is not None and \
                contribution.get("tree_part") not in covers_parts:
            continue
        seat = contribution.get("author")
        if seat not in covered:
            covered[seat] = identity_status_of(state, seat)
    return covered


def derive(state):
    """Derive §3.8's state over a folded (and gate-enriched)
    record: the current route per disagreement, and the claim
    standing per part. Pure and idempotent."""
    routing = {}
    for note in state.get("routing_notes", []):
        # Latest valid route is current; every note remains in
        # the record and in routing_notes — superseded as
        # current state only, never erased (§3.8, S4).
        routing[note["disagreement_id"]] = {
            "joint": note["joint"],
            "event_seq": note["event_seq"],
            "by": note["by"],
        }
    state["routing"] = routing
    claims_by_part = {}
    for claim in state.get("completion_claims", []):
        key = claim.get("tree_part") or "(job)"
        claims_by_part.setdefault(key, []).append({
            "event_seq": claim["event_seq"], "by": claim["by"],
        })
    state["claims_by_part"] = claims_by_part
    return state
