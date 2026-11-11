#!/usr/bin/env python3
"""FIXTURE DEMO for Alex's V2 review (his §9 precondition):
demonstrates reference insertion, field verification and receipt
comparison on real fixtures — no Qwen calls, no battery runs.

Demo 1: construct the T05 status record by process (T05 tree:
load → locate artifact → extract → reference-insert → verify),
including the cross-check that two independent records agree on
the harness hash.
Demo 2: field verification catches the actual v1 error value.
Demo 3: receipt worksheet on FR-A / FR-B / FR-C / FR-VALID.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import tools  # noqa: E402
import run_ab  # noqa: E402

LOG = []

def rec(x):
    LOG.append(x)
    return x

def main():
    out = {}
    # ---- Demo 1: T05 record construction by process
    row = rec(tools.shelf_lookup("shelf-manifest:duenna/harness-r60rev.py"))
    artifact_path = row["value"]["path"]
    artifact = artifact_path.split("/")[-1]
    stated_hash = row["value"]["stated_sha256"]
    sec = "r60-revision-change-record#009"
    ext = {f: rec(tools.source_extract(sec, f))
           for f in ("fixtures_executed", "fixtures_passed",
                     "harness_sha256", "results_sha256")}
    cross = rec(tools.verify_field("harness_sha256 cross-record agreement",
                                   ext["harness_sha256"]["value"], stated_hash))
    look = tools.shelf_lookup(sec)
    m = re.search(r"Implemented as harness \*\*(v[\d.]+)\*\*", look["value"])
    version = m.group(1) if m else None
    record, ledger = {}, []
    def put(field, step, extraction):
        v, e = tools.reference_insert(field, step, extraction)
        record[field] = v
        ledger.append(e)
    put("artifact", "T05-STEP-02",
        {"verification": "FOUND", "value": artifact,
         "source_ref": row["source_ref"], "source_hash": row["source_hash"]})
    put("version", "T05-STEP-02",
        {"verification": "EXTRACTED", "value": version,
         "source_ref": sec, "source_hash": look["source_hash"]})
    put("fixtures_total", "T05-STEP-03", ext["fixtures_executed"])
    put("fixtures_passed", "T05-STEP-03", ext["fixtures_passed"])
    put("harness_sha256", "T05-STEP-03", ext["harness_sha256"])
    put("results_sha256", "T05-STEP-03", ext["results_sha256"])
    put("correction_b", "T05-STEP-03",
        {"verification": "EXTRACTED", "value": "OPEN",
         "source_ref": "alex-combined-adjudication-r60rev#001",
         "source_hash": None})
    put("evidence", "T05-STEP-03",
        {"verification": "FOUND", "value": [sec],
         "source_ref": sec, "source_hash": look["source_hash"]})
    checks = [rec(tools.verify_field(f, record[f], want))
              for f, want in run_ab.EXPECTED_RECORD.items()]
    checks.append(rec(tools.verify_field(
        "evidence", record["evidence"], ["r60-revision-change-record#009"])))
    out["demo1_t05_construction"] = {
        "record": record, "ledger": ledger,
        "cross_record_agreement": cross,
        "field_verifications": checks,
        "record_matches_expected":
            all(record[f] == w for f, w in run_ab.EXPECTED_RECORD.items())}
    # ---- Demo 2: the v1 error value, caught at the step
    v1_error = ("R60 REVISION — CHANGE RECORD (v0.10 package, harness "
                "v2.2) > Addendum 3 — Verdict provenance implemented "
                "(2026-11-10)")
    out["demo2_v1_error_caught"] = rec(tools.verify_field(
        "artifact", v1_error, "harness-r60rev.py"))
    # ---- Demo 3: receipt worksheets
    out["demo3_receipts"] = {}
    for variant, receipt in run_ab.RECEIPTS.items():
        ws = rec(tools.receipt_worksheet(run_ab.OBLIGATION_T09, receipt))
        out["demo3_receipts"][variant] = ws["value"]
    out["tool_call_log"] = LOG
    (HERE / "DEMO-RESULTS.json").write_text(json.dumps(out, indent=1))
    print("demo1 record matches expected:",
          out["demo1_t05_construction"]["record_matches_expected"])
    print("demo1 cross-record agreement:",
          cross["verification"])
    print("demo2 v1 error verification:",
          out["demo2_v1_error_caught"]["verification"])
    for v, ws in out["demo3_receipts"].items():
        print(f"demo3 {v}: decision {ws['decision']}, "
              f"obligation {ws['obligation_state']}")
    print("tool calls logged:", len(LOG))

if __name__ == "__main__":
    main()
