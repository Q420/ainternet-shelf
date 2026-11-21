#!/usr/bin/env python3
"""V2.1 FIXTURE DEMO for Alex's review. D1–D3 repeat the v2
demonstrations with every value obtained through the tools
(no manufactured values). N1–N3 are the new negative fixtures
Alex required: missing provenance, altered extraction results
(stale digest AND recomputed-digest forgery), and unsupported
operations. No Qwen calls; no battery runs."""
import json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import tools21 as T  # noqa: E402
import run_ab  # noqa: E402

SEC = "r60-revision-change-record#009"
ADJ = "alex-combined-adjudication-r60rev#001"

def main():
    out = {}
    # ---- D1: T05 construction, tool-pure
    record, ledger = {}, []
    def put(field, step, extraction, select=None):
        v, e = T.reference_insert(field, step, extraction, select=select)
        record[field] = v
        ledger.append(e)
    lk = T.shelf_lookup("shelf-manifest:duenna/harness-r60rev.py")
    put("artifact", "T05-STEP-02", lk, select="file_name")
    put("version", "T05-STEP-02", T.source_extract(SEC, "version"))
    put("fixtures_total", "T05-STEP-03", T.source_extract(SEC, "fixtures_executed"))
    put("fixtures_passed", "T05-STEP-03", T.source_extract(SEC, "fixtures_passed"))
    put("harness_sha256", "T05-STEP-03", T.source_extract(SEC, "harness_sha256"))
    put("results_sha256", "T05-STEP-03", T.source_extract(SEC, "results_sha256"))
    put("correction_b", "T05-STEP-03", T.source_extract(ADJ, "correction_b_status"))
    put("evidence", "T05-STEP-03", T.cite(SEC))
    cross = T.verify_field("harness_sha256 cross-record agreement",
                           record["harness_sha256"],
                           lk["value"]["stated_sha256"])
    checks = [T.verify_field(f, record[f], w)
              for f, w in run_ab.EXPECTED_RECORD.items()]
    checks.append(T.verify_field("evidence", record["evidence"], [SEC]))
    out["D1_t05_tool_pure"] = {
        "record": record, "ledger": ledger,
        "cross_record_agreement": cross["verification"],
        "all_fields_verified": all(c["verification"] == "PASS" for c in checks),
        "record_matches_expected":
            all(record[f] == w for f, w in run_ab.EXPECTED_RECORD.items())}
    # ---- D2: the v1 error value
    v1_error = ("R60 REVISION — CHANGE RECORD (v0.10 package, harness "
                "v2.2) > Addendum 3 — Verdict provenance implemented "
                "(2026-11-10)")
    d2 = T.verify_field("artifact", v1_error, "harness-r60rev.py")
    out["D2_v1_error"] = {"verification": d2["verification"],
                          "failure_reason": d2["failure_reason"]}
    # ---- D3: receipt worksheets
    spec = T.load_obligation_spec()["value"]
    out["D3_receipts"] = {}
    for variant, receipt in run_ab.RECEIPTS.items():
        ws = T.receipt_worksheet(spec, receipt)
        out["D3_receipts"][variant] = ws["value"]
    # ---- N1: missing provenance
    ex = T.source_extract(SEC, "fixtures_executed")
    stripped = {k: v for k, v in ex.items()
                if k not in ("source_hash", "value_offsets",
                             "evidence_line_no", "result_digest")}
    v, e = T.reference_insert("fixtures_total", "N1", stripped)
    out["N1_missing_provenance"] = {"insert_verification": e["verification"],
                                    "failure_reason": e["failure_reason"],
                                    "value_inserted": v}
    # ---- N2a: altered value, stale digest
    ex2 = T.source_extract(SEC, "fixtures_passed")
    altered = dict(ex2, value=39)
    v, e = T.reference_insert("fixtures_passed", "N2a", altered)
    out["N2a_altered_stale_digest"] = {"insert_verification": e["verification"],
                                       "failure_reason": e["failure_reason"],
                                       "value_inserted": v}
    # ---- N2b: altered value, digest recomputed (forgery)
    forged = dict(ex2, value=39)
    forged["result_digest"] = T._digest({k: forged.get(k) for k in
        ("tool", "source_ref", "source_hash", "value", "verification",
         "extract_field", "evidence_line_no", "value_offsets")})
    v, e = T.reference_insert("fixtures_passed", "N2b", forged)
    out["N2b_altered_recomputed_digest"] = {
        "insert_verification": e["verification"],
        "failure_reason": e["failure_reason"], "value_inserted": v}
    # ---- N3: unsupported operations
    u1 = T.call("publish_record", record=record)
    u2 = T.source_extract(SEC, "no_such_field")
    out["N3_unsupported"] = {
        "unknown_operation": {"verification": u1["verification"],
                              "failure_reason": u1["failure_reason"]},
        "unknown_extractor": {"verification": u2["verification"],
                              "failure_reason": u2["failure_reason"]}}
    out["tool_call_log"] = T.CALL_LOG
    (HERE / "DEMO21-RESULTS.json").write_text(json.dumps(out, indent=1))
    print("D1 record matches expected:", out["D1_t05_tool_pure"]["record_matches_expected"])
    print("D1 all fields verified:", out["D1_t05_tool_pure"]["all_fields_verified"])
    print("D1 cross-record agreement:", out["D1_t05_tool_pure"]["cross_record_agreement"])
    print("D2 v1 error:", out["D2_v1_error"]["verification"])
    for k, ws in out["D3_receipts"].items():
        print(f"D3 {k}: {ws['decision']} (obligation {ws['obligation_state']})")
    print("N1 missing provenance:", out["N1_missing_provenance"]["insert_verification"],
          "—", out["N1_missing_provenance"]["failure_reason"])
    print("N2a stale digest:", out["N2a_altered_stale_digest"]["insert_verification"],
          "—", out["N2a_altered_stale_digest"]["failure_reason"])
    print("N2b recomputed digest:", out["N2b_altered_recomputed_digest"]["insert_verification"],
          "—", out["N2b_altered_recomputed_digest"]["failure_reason"])
    print("N3 unknown op:", out["N3_unsupported"]["unknown_operation"]["verification"],
          "| unknown extractor:", out["N3_unsupported"]["unknown_extractor"]["verification"])
    print("tool calls logged:", len(T.CALL_LOG))

if __name__ == "__main__":
    main()
