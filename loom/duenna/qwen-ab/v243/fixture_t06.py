#!/usr/bin/env python3
"""V2.4.3 FIXTURES — T06 scoring boundary + S2 stages.
Exercises the REAL scorer (run_ab.check_t06_labels) and the
REAL source-location procedure (run_c.s2_source_location).
No model calls; not a battery or diagnostic run.

F1  a worker report with four WRONG labels scores 0/4
    (BLOCKED) — scored on the worker's text alone.
F2  the same worker text WITH the correct system
    classifications appended would score 4/4 — this is the
    V2.4.2 defect, shown to prove the boundary matters and
    that the corrected driver (which scores the worker text
    only and stores the system classification in the
    process record) no longer has it.
F3  a worker report with four CORRECT labels scores 4/4.
F4  S2 stages on the real frozen corpus: mentions found,
    no candidate, authentication NOT PERFORMED,
    classification UNTRACEABLE.
F5  filename is not authorship: a synthetic corpus whose
    document is named grok-adjudication-v09 (a stage-2
    candidate) but which is NOT in the admission manifest
    authenticates nothing — classification UNTRACEABLE,
    with the stage-3 record showing why.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "v24"))
sys.path.insert(0, str(pathlib.Path.home()
                       / "workspace/pulse-bridge/index"))
import run_ab  # noqa: E402
import run_c  # noqa: E402

WRONG = ("S1: CONTRADICTED — the numbers look off.\n"
         "S2: SUPPORTED — Grok approved it.\n"
         "S3: SUPPORTED — the section says so.\n"
         "S4: SUPPORTED — Vane confirmed it.")
RIGHT = ("S1: SUPPORTED — the record states 38 of 38.\n"
         "S2: UNTRACEABLE — no such adjudication is locatable.\n"
         "S3: UNTRACEABLE — the cited section does not exist.\n"
         "S4: CONTRADICTED — Vane's report states the opposite.")
SYSTEM_BLOCK = ("\n\n[SYSTEM CLASSIFICATION]\n"
                "S1: SUPPORTED\nS2: UNTRACEABLE\n"
                "S3: UNTRACEABLE\nS4: CONTRADICTED")

def score(text):
    checks = run_ab.check_t06_labels(text)
    passed = sum(1 for c in checks if c["pass"])
    return {"passed": passed, "of": len(checks),
            "decision": run_ab.gate_decision(checks),
            "checks": checks}

out = {}
out["F1_wrong_worker_scored_alone"] = score(WRONG)
out["F2_wrong_worker_with_system_appended"] = score(WRONG + SYSTEM_BLOCK)
out["F3_right_worker_scored_alone"] = score(RIGHT)

idx = pathlib.Path.home() / "workspace/pulse-bridge/index"
sections = [json.loads(l) for l in open(idx / "sections.jsonl")]
admitted = {d["doc"]: d["file_sha256"]
            for d in json.loads((idx / "manifest.json")
                                .read_text())["documents"]}
out["F4_s2_real_corpus"] = run_c.s2_source_location(sections, admitted)

synthetic = [{"section_id": "grok-adjudication-v09#001",
              "doc": "grok-adjudication-v09",
              "text": "Grok adjudication: the v0.9 gate is APPROVED. "
                      "Signed, Grok."}]
out["F5_s2_filename_only_candidate"] = run_c.s2_source_location(
    synthetic, admitted)

assert out["F1_wrong_worker_scored_alone"]["passed"] == 0
assert out["F2_wrong_worker_with_system_appended"]["passed"] == 4
assert out["F3_right_worker_scored_alone"]["passed"] == 4
assert out["F4_s2_real_corpus"]["stage4_classification"] == "UNTRACEABLE"
assert "NOT PERFORMED" in out["F4_s2_real_corpus"]["stage3_authentication"]
assert out["F5_s2_filename_only_candidate"]["stage2_candidates"] == \
    ["grok-adjudication-v09#001"]
assert out["F5_s2_filename_only_candidate"]["stage4_classification"] == \
    "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-T06-RESULTS.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: (v if not isinstance(v, dict) else
                      {kk: vv for kk, vv in v.items()
                       if kk != "checks"})
                  for k, v in out.items()}, indent=1)[:1800])
