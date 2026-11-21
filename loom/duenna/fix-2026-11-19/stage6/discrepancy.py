"""Duenna Stage 6 — the discrepancy lifecycle (K10).

K10: "a disagreement mints a discrepancy record linked to
the attribution, preserving both positions, with an explicit
resolution state — UNRESOLVED / RESOLVED BY AUTHORISED
DECISION (the decision and its authority recorded) /
INDETERMINATE. Until a resolution exists, no consumer may
silently select a side; the canonical attribution remains
one fact, and the disagreement is additional evidence, not a
second attribution. INDETERMINATE is a terminal state of the
DISAGREEMENT, not a resolution of the attribution: consumers
continue to see that no authoritative resolution selected a
side."

Mechanised here as three event types on the same record:

- DISCREPANCY_RECORDED — the disagreement itself: the
  attribution it is linked to (by event digest), the subject
  it concerns, and BOTH POSITIONS VERBATIM. Minting changes
  nothing about the attribution: the attribution event is
  already on the record, append-only, and stays byte-for-byte
  what it was.
- DISCREPANCY_RESOLUTION — appended by the pinned authority
  only: the decision, the basis, the authority it acted
  under. State becomes RESOLVED_BY_AUTHORISED_DECISION.
- DISCREPANCY_INDETERMINATE — appended by the pinned
  authority only: the disagreement is closed as not
  resolvable on the evidence. The attribution is untouched.

A resolution attempted without the issued authority
capability is refused and appends nothing. The state of a
discrepancy is established by folding its events from the
verified read-back — never from a live object's memory.

CORRECTION ROUND 1 (Gate 1 verdict, shelf @ b9916f4f), two
changes. First, the resolution-side authority check now
verifies the capability itself (``capability_is_issued``),
not merely its type — the same self-issuance bypass the
verdict found at minting reached resolution through the
shared type check. Second, the attribution link is now
RESOLVED, not merely cited: ``mint_discrepancy`` resolves
the supplied digest against the verified snapshot and
requires an actual ATTRIBUTION_RECORDED event; a fictitious
digest, or a digest belonging to an event of another type,
is refused with nothing appended. ``discrepancy_state``
applies the same resolution on read-back, so a stored
reference that does not resolve is never presented as a
valid attribution link. K10 requires the discrepancy to be
linked to the canonical attribution record by its event
digest — a string-shaped reference is not that link.
"""

from __future__ import annotations

from binder import CHAIN_VERIFICATION_FAILED, verify_record_current

from attribution import ATTRIBUTION_RECORDED, RecordIntegrityRefused
from authority import AttributionAuthority, capability_is_issued

DISCREPANCY_RECORDED = "DISCREPANCY_RECORDED"
DISCREPANCY_RESOLUTION = "DISCREPANCY_RESOLUTION"
DISCREPANCY_INDETERMINATE = "DISCREPANCY_INDETERMINATE"

UNRESOLVED = "UNRESOLVED"
RESOLVED_BY_AUTHORISED_DECISION = "RESOLVED_BY_AUTHORISED_DECISION"
INDETERMINATE = "INDETERMINATE"


class DiscrepancyRefused(Exception):
    """A discrepancy operation was refused: no authority for
    a resolution, an unknown discrepancy, or a terminal state
    already reached. Nothing was appended."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"discrepancy refused: {details!r}")


def _verified_events(record):
    events, failure = verify_record_current(record)
    if failure is not None:
        raise RecordIntegrityRefused(
            {CHAIN_VERIFICATION_FAILED: failure})
    return events


def _require_authority(authority):
    if not isinstance(authority, AttributionAuthority):
        raise DiscrepancyRefused(
            {"reason": "a discrepancy resolves only by "
                       "authorised decision — the issued "
                       "authority capability is required; a "
                       "party to the disagreement cannot "
                       "resolve it by assertion",
             "presented": type(authority).__name__})
    if not capability_is_issued(authority):
        raise DiscrepancyRefused(
            {"reason": "the presented capability was not "
                       "issued through the verified issuance "
                       "path (authority.py issue_authority); a "
                       "forged or self-constructed capability "
                       "cannot resolve a discrepancy",
             "presented_digest": getattr(
                 authority, "authority_digest", None)})


def _resolve_attribution(events, attribution_event):
    """Resolve a cited attribution digest against the
    verified snapshot (correction round 1): the digest must
    identify an event ON THIS RECORD, and that event must be
    an ATTRIBUTION_RECORDED event. Returns the event, or
    raises DiscrepancyRefused naming why the reference does
    not resolve. A string-shaped reference is not a link."""
    found = None
    for ev in events:
        if ev.get("digest") == attribution_event:
            found = ev
            break
    if found is None:
        raise DiscrepancyRefused(
            {"reason": "the cited attribution_event does "
                       "not resolve to any event on the "
                       "verified record; a discrepancy links "
                       "to the canonical attribution record "
                       "by its event digest, and a fictitious "
                       "digest is not a link",
             "attribution_event": attribution_event})
    if found.get("type") != ATTRIBUTION_RECORDED:
        raise DiscrepancyRefused(
            {"reason": "the cited attribution_event "
                       "resolves to an event of a different "
                       "type, not an ATTRIBUTION_RECORDED "
                       "event",
             "attribution_event": attribution_event,
             "resolved_type": found.get("type")})
    return found


def mint_discrepancy(record, attribution_event: str,
                     subject_ref: str, position_a: dict,
                     position_b: dict) -> dict:
    """Record a disagreement. Both positions are preserved
    verbatim — each position is a dict naming its holder and
    its statement, stored exactly as presented. The
    attribution it links to is cited by event digest; the
    attribution itself is not modified, restated or
    re-minted. The cited digest is RESOLVED against the
    verified snapshot before anything is appended
    (correction round 1): it must identify an actual
    ATTRIBUTION_RECORDED event on this record."""
    events = _verified_events(record)
    _resolve_attribution(events, attribution_event)
    return record.append(DISCREPANCY_RECORDED, {
        "attribution_event": attribution_event,
        "subject_ref": subject_ref,
        "position_a": position_a,
        "position_b": position_b,
        "state": UNRESOLVED,
    })


def _discrepancy_events(events, discrepancy_digest):
    minted = None
    follow = []
    for ev in events:
        body = ev.get("body", {})
        if ev.get("type") == DISCREPANCY_RECORDED \
                and ev.get("digest") == discrepancy_digest:
            minted = ev
        elif ev.get("type") in (DISCREPANCY_RESOLUTION,
                                DISCREPANCY_INDETERMINATE) \
                and body.get("discrepancy_event") == discrepancy_digest:
            follow.append(ev)
    return minted, follow


def discrepancy_state(record, discrepancy_digest: str) -> dict:
    """The discrepancy's current state, folded from the
    verified read-back: the minted record (both positions
    verbatim) plus any resolution. INDETERMINATE and
    RESOLVED_BY_AUTHORISED_DECISION are terminal for the
    disagreement."""
    events = _verified_events(record)
    minted, follow = _discrepancy_events(events, discrepancy_digest)
    if minted is None:
        raise DiscrepancyRefused(
            {"reason": "no discrepancy with that identity",
             "discrepancy_event": discrepancy_digest})
    # The read-back path preserves the minting invariant
    # (correction round 1): the stored attribution
    # reference is resolved against this verified snapshot
    # before it is presented as the discrepancy's link — a
    # reference that does not resolve to an
    # ATTRIBUTION_RECORDED event is refused, never passed
    # through as a valid link.
    _resolve_attribution(events, minted["body"]["attribution_event"])
    state = UNRESOLVED
    resolution = None
    for ev in follow:
        if ev["type"] == DISCREPANCY_RESOLUTION:
            state = RESOLVED_BY_AUTHORISED_DECISION
            resolution = ev["body"]
        elif ev["type"] == DISCREPANCY_INDETERMINATE:
            state = INDETERMINATE
            resolution = ev["body"]
    return {"discrepancy_event": discrepancy_digest,
            "subject_ref": minted["body"]["subject_ref"],
            "attribution_event": minted["body"]["attribution_event"],
            "position_a": minted["body"]["position_a"],
            "position_b": minted["body"]["position_b"],
            "state": state, "resolution": resolution}


def _append_resolution(record, authority, discrepancy_digest,
                       event_type, extra: dict) -> dict:
    _require_authority(authority)
    events = _verified_events(record)
    minted, follow = _discrepancy_events(events, discrepancy_digest)
    if minted is None:
        raise DiscrepancyRefused(
            {"reason": "no discrepancy with that identity",
             "discrepancy_event": discrepancy_digest})
    if follow:
        raise DiscrepancyRefused(
            {"reason": "the disagreement is already in a "
                       "terminal state; a second resolution "
                       "would be a second fact about it",
             "discrepancy_event": discrepancy_digest,
             "existing": follow[-1]["digest"]})
    body = {"discrepancy_event": discrepancy_digest,
            "authority": authority.authority_id,
            "authority_digest": authority.authority_digest}
    body.update(extra)
    return record.append(event_type, body)


def resolve_discrepancy(record, authority, discrepancy_digest,
                        decision: str, basis_refs) -> dict:
    """Resolve by authorised decision. The decision and the
    authority it was taken under are recorded; the two
    positions stay on the record exactly as minted — a
    resolution selects a side openly, it does not rewrite
    what either side said."""
    return _append_resolution(
        record, authority, discrepancy_digest,
        DISCREPANCY_RESOLUTION,
        {"decision": decision, "basis_refs": list(basis_refs)})


def mark_indeterminate(record, authority, discrepancy_digest,
                       reason: str) -> dict:
    """Close the disagreement as INDETERMINATE: on the
    evidence available, no authoritative resolution selects
    a side. Terminal for the DISAGREEMENT — the linked
    attribution is untouched and continues to stand as the
    one fact."""
    return _append_resolution(
        record, authority, discrepancy_digest,
        DISCREPANCY_INDETERMINATE, {"reason": reason})
