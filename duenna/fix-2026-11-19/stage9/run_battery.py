#!/usr/bin/env python3
"""Stage 9 — the one bounded battery execution.

Runs the assembled battery once, end to end, against the live
subject (openai/gpt-oss-20b on the NVIDIA endpoint, per Alex's
pin ruling 2026-11-17), and prints the run summary as JSON.

The K2 verification is part of the freeze (the binder's lane):
if the endpoint does not answer, or the answering model cannot
be verified as the pinned subject, the freeze refuses and this
exits with the FREEZE_REFUSED summary — no scored run, no
substitution.
"""
import json
import os
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import assembly          # noqa: E402
import transport as live  # noqa: E402


def main():
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    package_name = f"STAGE9BATT-{date}-001"
    runs_root = os.path.join(_HERE, "runs")
    os.makedirs(runs_root, exist_ok=True)
    existing = [d for d in os.listdir(runs_root)
                if d.startswith(f"STAGE9BATT-{date}-")]
    if existing:
        package_name = f"STAGE9BATT-{date}-{len(existing) + 1:03d}"

    transport = live.LiveTransport(assembly.SUBJECT)

    def models_check():
        listing = live.list_models()
        if "data" in listing:
            ids = [m.get("id") for m in listing["data"]]
            return {"listed": assembly.SUBJECT in ids,
                    "model_count": len(ids)}
        return {"error": listing.get("error")}

    summary = assembly.run_battery(
        runs_root=runs_root, package_name=package_name,
        transport=transport, models_check=models_check)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
