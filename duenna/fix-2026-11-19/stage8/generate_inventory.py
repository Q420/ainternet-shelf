"""Generate FIXTURE-INVENTORY.md from the inventory (identities)
and the matrix summary (execution records). The two are kept
separate in the document, per K14: identity states what a
fixture intends; the execution record states what the matrix
observed.

Usage: python3 generate_inventory.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventory  # noqa: E402
import matrix  # noqa: E402


def main():
    _missing, _extra, stage_by_id = inventory.completeness(
        matrix.ROOT)
    with open(os.path.join(HERE, "results", "matrix-summary.json"),
              encoding="utf-8") as fh:
        summary = json.load(fh)
    pairs = {}
    for key, verdict in summary["pairs"].items():
        fixture, mech = key.split(" :: ")
        pairs.setdefault(fixture, []).append((mech, verdict))
    joint = summary["joint_fixtures"]

    lines = []
    lines.append("# Duenna Stage 8 — Fixture Inventory (K14)")
    lines.append("")
    lines.append("Every test in Stages 1–7: its fixture identity "
                 "(the target mechanism path it claims, from a "
                 "first-hand reading of the suites) and its "
                 "execution record (the sabotage matrix's verdict, "
                 "from the witness runner's outcomes — never from "
                 "the fixture's own account of itself).")
    lines.append("")
    n_pairs = sum(len(v) for v in pairs.values())
    lines.append(f"Fixtures: {len(inventory.ENTRIES)}. Claimed "
                 f"(fixture, mechanism) pairs: {n_pairs}.")
    lines.append("")
    for stage in range(1, 8):
        ids = sorted(t for t, s in stage_by_id.items() if s == stage)
        lines.append(f"## Stage {stage} — {len(ids)} fixtures")
        lines.append("")
        for test_id in ids:
            targets, kind, note = inventory.ENTRIES[test_id]
            lines.append(f"### `{test_id}`")
            lines.append(f"- kind: {kind}")
            if targets:
                lines.append(f"- targets: {', '.join(targets)}")
            else:
                lines.append("- targets: none claimed")
            verdicts = pairs.get(test_id, [])
            for mech, verdict in verdicts:
                lines.append(f"- execution ({mech}): {verdict}")
            if test_id in joint:
                lines.append(f"- execution (combined): "
                             f"{joint[test_id]}")
            if not verdicts and test_id not in joint:
                lines.append("- execution: no claimed pair — "
                             "collateral-monitored only")
            if note:
                lines.append(f"- note: {note}")
            lines.append("")
    out = os.path.join(HERE, "FIXTURE-INVENTORY.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {out}: {len(lines)} lines")


if __name__ == "__main__":
    main()
