"""Starvation report — a named derived read over the event history.

Stage 4 (2026-11-21), Loom spec v0.1 Rev 9 section 7 and the
settled Stage 4 design (Brief Rev 2, B8): starvation is exposed,
not solved — measured and published per agent, as a deterministic
derived report, never as authoritative state. This module reads
an event history and computes the report; it mutates nothing and
appends nothing. The measure definitions are pinned in the Stage
4 build notes, section 3, and repeated in this module's contract:

- Agent set: every actor of a CONTRIBUTION_ACCEPTED,
  CONTRIBUTION_REJECTED, ASSESSMENT_RECORDED, EXAMINATION_RECORDED,
  COMPLETION_CLAIMED, or IDLE event. Every agent in the set is
  reported, including agents with no successful commit (VP-50).
- Wake: one event authored by the agent, of the types above.
- Rejections by outcome: CONTRIBUTION_REJECTED events counted by
  their payload outcome, plus Stage 3 outcome events whose
  payload outcome is "rejected", counted under "stage3:<reason>".
- Consecutive rejections: over the agent's own rejection events
  in sequence order; the run resets ONLY on that agent's accepted
  commit. IDLE and every other event neither increments nor
  resets it (VP-51). Current and maximum runs are both reported.
- Wakes between successful commits: per pair of consecutive
  accepted commits, the agent's wakes strictly between them, as a
  list in commit order; JSON null when fewer than two accepted
  commits exist (no gap observed). The field is always present
  (VP-52).
- Time to first success: first_success_seq - first_wake_seq in
  run events, and wakes_to_first_success (the agent's wakes up to
  and including the first accepted commit). Both JSON null when
  the agent has no accepted commit; fields always present.
- Changed-read diff sizes: for each stale CONTRIBUTION_REJECTED,
  in sequence order, the length of the recorded diff — REGIONS,
  read from the rejection evidence itself, never recomputed
  (VP-53).
- Progression: accepted_commits (count) and
  progressed_after_first_rejection (bool).

The report is serialised with the fabric's canonical JSON, agent
keys sorted: byte-identical for identical input (VP-54). The
module runs standalone (`python3 -m fabric.starvation <history
file>`) printing the canonical report — the second execution
path the pack validation uses (build notes I-12).
"""
import json
import sys

from .canonical import canonical

_COUNTED_TYPES = ("CONTRIBUTION_ACCEPTED", "CONTRIBUTION_REJECTED",
                  "ASSESSMENT_RECORDED", "EXAMINATION_RECORDED",
                  "COMPLETION_CLAIMED", "IDLE")


def _is_rejection(ev):
    if ev["type"] == "CONTRIBUTION_REJECTED":
        return True
    return ev["type"] in ("ASSESSMENT_RECORDED",
                          "EXAMINATION_RECORDED",
                          "COMPLETION_CLAIMED") \
        and ev["payload"].get("outcome") == "rejected"


def _rejection_key(ev):
    if ev["type"] == "CONTRIBUTION_REJECTED":
        return ev["payload"].get("outcome")
    return "stage3:" + str(ev["payload"].get("reason"))


def build_report(events) -> dict:
    """Compute the starvation report over an event history (a list
    of event dicts as the store returns them). Pure: the input is
    not mutated and no state is kept between calls."""
    per_agent = {}

    def slot(agent):
        return per_agent.setdefault(agent, {
            "wakes": 0,
            "rejections_by_outcome": {},
            "rejection_seqs": [],
            "accepted_commit_seqs": [],
            "wake_seqs": [],
            "changed_read_diff_sizes": [],
        })

    for ev in events:
        if ev["type"] not in _COUNTED_TYPES:
            continue
        record = slot(ev["actor"])
        record["wakes"] += 1
        record["wake_seqs"].append(ev["event_seq"])
        if ev["type"] == "CONTRIBUTION_ACCEPTED":
            record["accepted_commit_seqs"].append(ev["event_seq"])
        elif _is_rejection(ev):
            record["rejection_seqs"].append(ev["event_seq"])
            key = _rejection_key(ev)
            record["rejections_by_outcome"][key] = \
                record["rejections_by_outcome"].get(key, 0) + 1
            if ev["type"] == "CONTRIBUTION_REJECTED" \
                    and ev["payload"].get("outcome") == "stale":
                diff = ev["payload"].get("diff") or []
                record["changed_read_diff_sizes"].append(len(diff))

    agents = {}
    for agent in sorted(per_agent):
        record = per_agent[agent]
        accepted = record["accepted_commit_seqs"]
        # Consecutive rejections over the agent's own timeline:
        # rejection and accepted-commit events in sequence order;
        # only an accepted commit resets the run (VP-51).
        timeline = sorted(
            [(seq, "rejection") for seq in record["rejection_seqs"]]
            + [(seq, "accepted") for seq in accepted])
        current = 0
        maximum = 0
        for _seq, kind in timeline:
            if kind == "rejection":
                current += 1
                maximum = max(maximum, current)
            else:
                current = 0
        if len(accepted) >= 2:
            gaps = []
            for first, second in zip(accepted, accepted[1:]):
                gaps.append(sum(1 for seq in record["wake_seqs"]
                                if first < seq < second))
            wakes_between = gaps
        else:
            wakes_between = None
        if accepted:
            first_success = accepted[0]
            time_to_first = first_success - record["wake_seqs"][0]
            wakes_to_first = sum(
                1 for seq in record["wake_seqs"]
                if seq <= first_success)
        else:
            time_to_first = None
            wakes_to_first = None
        agents[agent] = {
            "wakes": record["wakes"],
            "rejections_by_outcome":
                record["rejections_by_outcome"],
            "total_rejections": len(record["rejection_seqs"]),
            "consecutive_rejections": current,
            "max_consecutive_rejections": maximum,
            "accepted_commits": len(accepted),
            "wakes_between_successful_commits": wakes_between,
            "time_to_first_success": time_to_first,
            "wakes_to_first_success": wakes_to_first,
            "changed_read_diff_sizes":
                record["changed_read_diff_sizes"],
            "changed_read_diff_unit": "regions",
            "progressed_after_first_rejection": bool(
                record["rejection_seqs"] and accepted
                and accepted[-1] > record["rejection_seqs"][0]),
        }
    return {"agents": agents, "events_considered": len(events)}


def report_bytes(events) -> bytes:
    """The report as canonical bytes — the byte-identical form
    VP-54 requires for identical input."""
    return canonical(build_report(events))


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        events = json.load(fh)
    sys.stdout.write(report_bytes(events).decode("utf-8") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
