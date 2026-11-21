#!/usr/bin/env python3
"""V2.4.4 FIXTURES — S2 location / admission / attribution.
Exercises the REAL procedure (run_c.s2_source_location).
No model calls; not a battery or diagnostic run.

F4  real frozen corpus: mentions found, no candidate,
    admission/attribution not performed, UNTRACEABLE.
F5  filename-only candidate (not admitted): located as a
    candidate, not admitted, attribution not performed,
    UNTRACEABLE.
F6  ADMITTED but UNATTRIBUTED candidate (Alex's ordered
    fixture): the synthetic Grok-named document IS in the
    admission manifest, and no independent record
    attributes it to Grok — admission does not authenticate
    authorship; classification remains UNTRACEABLE.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "v24"))
sys.path.insert(0, str(pathlib.Path.home()
                       / "workspace/pulse-bridge/index"))
import run_c  # noqa: E402

idx = pathlib.Path.home() / "workspace/pulse-bridge/index"
sections = [json.loads(l) for l in open(idx / "sections.jsonl")]
admitted = {d["doc"]: d["file_sha256"]
            for d in json.loads((idx / "manifest.json")
                                .read_text())["documents"]}
out = {}
out["F4_real_corpus"] = run_c.s2_source_location(sections, admitted)

synthetic = [{"section_id": "grok-adjudication-v09#001",
              "doc": "grok-adjudication-v09",
              "text": "Grok adjudication: the v0.9 gate is APPROVED. "
                      "Signed, Grok."}]
out["F5_filename_only_not_admitted"] = run_c.s2_source_location(
    synthetic, admitted)

admitted_plus = dict(admitted)
admitted_plus["grok-adjudication-v09"] = "0" * 64
out["F6_admitted_but_unattributed"] = run_c.s2_source_location(
    synthetic, admitted_plus)

f4, f5, f6 = (out["F4_real_corpus"], out["F5_filename_only_not_admitted"],
              out["F6_admitted_but_unattributed"])
assert f4["stage5_classification"] == "UNTRACEABLE"
assert f5["stage2_candidates"] == ["grok-adjudication-v09#001"]
assert "none" in f5["stage3_admission"]
assert f5["stage5_classification"] == "UNTRACEABLE"
assert "grok-adjudication-v09" in f6["stage3_admission"]
assert "none found" in f6["stage4_author_attribution"]
assert f6["stage5_classification"] == "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-S2-RESULTS.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1)[:1500])
