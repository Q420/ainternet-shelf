"""Duenna Stage 6 — report resolution on the Examiner
Surface (G6, over K9's event/step identity).

K9: "reports refer to event identities; step locations are
RESOLVED from the event and the frozen tree set; any
human-readable location in a report is RENDERED from that
resolution, never independently typed; a report containing
both a reference and a contradictory literal location is
rejected or flagged by a named check on the Examiner
Surface."

G6: "Inputs: the report's event references and any literal
locations. Evidence: resolution of each reference against
the record and frozen tree set. Pass: every literal location
equals its rendered resolution. Fail: the report is flagged
with the conflicting reference identities; the conflict is a
discrepancy, never silently corrected."

DR-07 is the defect this gate answers: one adjudication
restated a step location two ways in two passages, and the
copies diverged because the location had two homes. Under
G6 a location has exactly one home — the event — and a
report's literal is checked against the rendered resolution,
by name, every time.

The events here are read from a preserved run record (the
attempt-3 record is the fixture of record): each event
carries its own tree/step identity, and the frozen tree set
confirms the resolved step exists in the tree as frozen.
Resolution renders "<tree>:<step>" from the EVENT — never
from the report, never from a payload field the event
happens to carry about another step.
"""

from __future__ import annotations


class ResolutionError(Exception):
    """A reference cannot be resolved at all: the event is
    not in the record, or its step is not in the frozen tree
    set. Distinct from a contradiction — an unresolvable
    reference is a broken report, not a disagreeing one."""

    def __init__(self, details: dict):
        self.details = details
        super().__init__(f"resolution error: {details!r}")


def render_location(event: dict, tree_set: dict) -> str:
    """Render an event's location from the event itself:
    its tree identity and its step identity, confirmed
    against the frozen tree set. This rendering is the only
    legitimate source of a human-readable location for the
    event."""
    tree_id = event.get("tree_id")
    step_id = event.get("step_id")
    steps = tree_set.get(tree_id)
    if steps is None or step_id not in steps:
        raise ResolutionError(
            {"reason": "the event's step is not in the "
                       "frozen tree set",
             "tree_id": tree_id, "step_id": step_id})
    return f"{tree_id}:{step_id}"


def resolve_report(events, tree_set: dict, references) -> dict:
    """The G6 check. ``references`` is the report as
    presented: a list of {event_seq, literal_location}. Each
    reference is resolved against the record; the literal is
    compared with the rendered resolution.

    Returns {passed, resolved, conflicts}: every reference
    appears in ``resolved`` with its RENDERED location (the
    report's literals are never echoed back as fact), and
    every contradiction appears in ``conflicts`` BY NAME —
    the reference's event identity, the literal the report
    stated, and the resolution it contradicts. A conflicting
    report is FLAGGED, not corrected: this function does not
    rewrite the report, and nothing in its result selects
    the literal's side."""
    by_seq = {ev["seq"]: ev for ev in events}
    resolved = []
    conflicts = []
    for ref in references:
        seq = ref["event_seq"]
        ev = by_seq.get(seq)
        if ev is None:
            raise ResolutionError(
                {"reason": "no event with that sequence in "
                           "the record",
                 "event_seq": seq})
        rendered = render_location(ev, tree_set)
        entry = {"event_seq": seq,
                 "event_digest": ev.get("event_sha256"),
                 "rendered_location": rendered,
                 "literal_location": ref["literal_location"]}
        resolved.append(entry)
        if ref["literal_location"] != rendered:
            conflicts.append({
                "event_seq": seq,
                "event_digest": ev.get("event_sha256"),
                "literal_location": ref["literal_location"],
                "rendered_location": rendered,
                "flag": "REPORT_LOCATION_CONTRADICTION",
            })
    return {"passed": not conflicts,
            "resolved": resolved,
            "conflicts": conflicts}
