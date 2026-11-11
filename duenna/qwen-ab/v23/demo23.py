#!/usr/bin/env python3
"""V2.3 FIXTURE DEMO for Alex's review (pb-mwbk6099). D1–D3 and
N1–N3 re-run under the v2.2 tools; N4–N7 are the new fixtures:
evidence-line alteration (stale digest AND recomputed digest),
evidence-line-number alteration, altered source hash with a
recomputed digest, and offset correctness with duplicate
identical lines in a real corpus section. No Qwen calls."""
import json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import tools23 as T  # noqa: E402
import run_ab  # noqa: E402

SEC = "r60-revision-change-record#009"
ADJ = "alex-combined-adjudication-r60rev#001"

def forge(extraction, **changes):
    """Alter fields and recompute the digest correctly — the
    strongest attacker this layer claims to stop."""
    f = dict(extraction, **changes)
    f["result_digest"] = T._digest({k: f.get(k) for k in T.DIGEST_KEYS})
    return f

def strip_forge(extraction, *keys):
    """Remove fields entirely and recompute the digest — the
    v2.3 bypass attempt: absent evidence must not become
    optional evidence."""
    f = dict(extraction)
    for k in keys:
        f.pop(k, None)
    f["result_digest"] = T._digest({k: f.get(k) for k in T.DIGEST_KEYS})
    return f

def attempt(field, extraction):
    v, e = T.reference_insert(field, "fixture", extraction)
    return {"insert_verification": e["verification"],
            "failure_reason": e["failure_reason"], "value_inserted": v}

def main():
    out = {}
    # ---- D1: T05 construction, tool-pure (as v2.1)
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
    checks = [T.verify_field(f, record[f], w)
              for f, w in run_ab.EXPECTED_RECORD.items()]
    checks.append(T.verify_field("evidence", record["evidence"], [SEC]))
    out["D1_t05_tool_pure"] = {
        "record": record,
        "record_matches_expected":
            all(record[f] == w for f, w in run_ab.EXPECTED_RECORD.items()),
        "all_fields_verified": all(c["verification"] == "PASS" for c in checks)}
    # ---- D2 / D3 (as v2.1)
    d2 = T.verify_field("artifact",
                        "R60 REVISION — CHANGE RECORD (v0.10 package, harness v2.2) > Addendum 3 — Verdict provenance implemented (2026-11-10)",
                        "harness-r60rev.py")
    out["D2_v1_error"] = {"verification": d2["verification"]}
    spec = T.load_obligation_spec()["value"]
    out["D3_receipts"] = {k: T.receipt_worksheet(spec, r)["value"]
                          for k, r in run_ab.RECEIPTS.items()}
    # ---- N1–N3 carried from v2.1
    ex = T.source_extract(SEC, "fixtures_executed")
    stripped = {k: v for k, v in ex.items()
                if k not in ("source_hash", "value_offsets",
                             "evidence_line_no", "result_digest")}
    out["N1_missing_provenance"] = attempt("fixtures_total", stripped)
    ex2 = T.source_extract(SEC, "fixtures_passed")
    out["N2a_altered_stale_digest"] = attempt("fixtures_passed", dict(ex2, value=39))
    out["N2b_altered_recomputed_digest"] = attempt(
        "fixtures_passed", forge(ex2, value=39))
    u1 = T.call("publish_record", record=record)
    out["N3_unsupported"] = {"verification": u1["verification"],
                            "failure_reason": u1["failure_reason"]}
    # ---- N4a: evidence line altered, stale digest
    ex3 = T.source_extract(SEC, "harness_sha256")
    out["N4a_evidence_line_stale_digest"] = attempt(
        "harness_sha256",
        dict(ex3, evidence_line="Harness sha256 **deadbeef** (fabricated line)"))
    # ---- N4b: evidence line altered, digest recomputed
    out["N4b_evidence_line_recomputed"] = attempt(
        "harness_sha256",
        forge(ex3, evidence_line="Harness sha256 **deadbeef** (fabricated line)"))
    # ---- N5: evidence line NUMBER altered, digest recomputed
    out["N5_line_number_recomputed"] = attempt(
        "harness_sha256",
        forge(ex3, evidence_line_no=ex3["evidence_line_no"] + 5))
    # ---- N6: source hash altered, digest recomputed
    out["N6_source_hash_recomputed"] = attempt(
        "harness_sha256",
        forge(ex3, source_hash="0" * 64))
    # ---- N7: duplicate identical lines — offsets must identify
    # the occurrence the loop reported (real corpus section)
    dup_sec = "process-tree-v04#018"
    ex4 = T.extract_line(dup_sec, "assembled by Remmy, 2026-11-08, under Alex's authorisation")
    text = run_ab.BY_ID[dup_sec]["text"]
    a, b = ex4["value_offsets"]
    occurrences = text.count(ex4["evidence_line"])
    out["N7_duplicate_lines"] = {
        "section": dup_sec,
        "occurrences_of_line_in_text": occurrences,
        "reported_line_no": ex4["evidence_line_no"],
        "slice_equals_reported_line": text[a:b].strip() == ex4["evidence_line"],
        "offset_is_a_line_start": a == 0 or text[a - 1] == "\n",
        "line_index_from_offset": text.count("\n", 0, a),
        "consistent": (text[a:b].strip() == ex4["evidence_line"]
                       and (a == 0 or text[a - 1] == "\n")
                       and text.count("\n", 0, a) == ex4["evidence_line_no"])}
    # ---- N8a/b/c (v2.3): evidence fields REMOVED, digest
    # recomputed — must fail at provenance completeness
    ex5 = T.source_extract(SEC, "harness_sha256")
    out["N8a_evidence_line_removed"] = attempt(
        "harness_sha256", strip_forge(ex5, "evidence_line"))
    out["N8b_evidence_line_no_removed"] = attempt(
        "harness_sha256", strip_forge(ex5, "evidence_line_no"))
    out["N8c_both_removed"] = attempt(
        "harness_sha256", strip_forge(ex5, "evidence_line", "evidence_line_no"))
    out["tool_call_log"] = T.CALL_LOG
    (HERE / "DEMO23-RESULTS.json").write_text(json.dumps(out, indent=1))
    print("D1 matches/verifies:", out["D1_t05_tool_pure"]["record_matches_expected"],
          out["D1_t05_tool_pure"]["all_fields_verified"])
    print("D2:", out["D2_v1_error"]["verification"])
    for k, ws in out["D3_receipts"].items():
        print(f"D3 {k}: {ws['decision']}")
    for k in ("N1_missing_provenance", "N2a_altered_stale_digest",
              "N2b_altered_recomputed_digest", "N4a_evidence_line_stale_digest",
              "N4b_evidence_line_recomputed", "N5_line_number_recomputed",
              "N6_source_hash_recomputed"):
        print(k, "->", out[k]["insert_verification"], "—", out[k]["failure_reason"])
    print("N3:", out["N3_unsupported"]["verification"])
    print("N7 duplicate lines:", out["N7_duplicate_lines"])
    for k in ("N8a_evidence_line_removed", "N8b_evidence_line_no_removed",
              "N8c_both_removed"):
        print(k, "->", out[k]["insert_verification"], "—", out[k]["failure_reason"])
    print("tool calls logged:", len(T.CALL_LOG))

if __name__ == "__main__":
    main()
