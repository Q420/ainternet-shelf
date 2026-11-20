"""Run the full Stage 8 sabotage matrix and classify it.

Usage: python3 run_matrix.py
Writes results/matrix-<mechanism>.json per mechanism,
results/matrix-joint-*.json per joint-guard group, and
results/matrix-summary.json with pair verdicts, collateral and
instrument interactions. Progress is printed per run.
"""

import matrix

if __name__ == "__main__":
    runs = matrix.run_matrix()
    summary = matrix.classify(runs)
    not_ex = [p for p, v in summary["pairs"].items()
              if v == "NOT-EXERCISED"]
    print(f"pairs NOT-EXERCISED: {len(not_ex)}")
    for p in not_ex:
        print("  ", p)
    print(f"collateral runs: {len(summary['collateral'])}")
    for run_id, ids in summary["collateral"].items():
        print(f"  {run_id}: {len(ids)}")
    print(f"instrument-interaction runs: "
          f"{len(summary['instrument_interaction'])}")
    for run_id, ids in summary["instrument_interaction"].items():
        print(f"  {run_id}: {ids}")
    print(f"invalid runs: {len(summary['invalid_runs'])}")
    for run_id, entry in summary["invalid_runs"].items():
        print(f"  {run_id}: {entry['invalid_reasons']}")
    print(f"witness anomalies: {len(summary['witness_anomalies'])}")
    for anomaly in summary["witness_anomalies"]:
        print(f"  {anomaly}")
    print(f"exercised by outcome: {summary['exercised_by_outcome']}")
