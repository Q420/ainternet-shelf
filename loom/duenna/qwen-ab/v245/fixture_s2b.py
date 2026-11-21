#!/usr/bin/env python3
"""V2.4.5 FIXTURES — stage-4 attribution must be an assertion.
Exercises the REAL procedure (run_c.s2_source_location).
No model calls; not a battery or diagnostic run.

The candidate grok-adjudication-v09 is ADMITTED in all
three synthetic corpora (stage 3 passes). Only the
independent record varies:

G1  explicit attribution ("records the ruling issued by
    Grok") -> attribution established -> SOURCE LOCATED.
G2  mere co-occurrence (candidate id + "Grok" in one
    document, no attribution assertion) -> none found ->
    UNTRACEABLE.
G3  explicit denial ("was not written or approved by
    Grok") -> the negated sentence is not evidence ->
    UNTRACEABLE.
F4  regression on the real corpus -> UNTRACEABLE.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "v24"))
sys.path.insert(0, str(pathlib.Path.home()
                       / "workspace/pulse-bridge/index"))
import run_c  # noqa: E402

CAND = {"section_id": "grok-adjudication-v09#001",
        "doc": "grok-adjudication-v09",
        "text": "Grok adjudication: the v0.9 gate is APPROVED. "
                "Signed, Grok."}
ADM = {"grok-adjudication-v09": "0" * 64, "programme-register": "1" * 64}

def corpus(other_text):
    return [CAND, {"section_id": "programme-register#001",
                   "doc": "programme-register", "text": other_text}]

out = {}
out["G1_explicit_attribution"] = run_c.s2_source_location(
    corpus("The adjudication grok-adjudication-v09 records the "
           "ruling issued by Grok on the v0.9 gate."), ADM)
out["G2_mere_mention"] = run_c.s2_source_location(
    corpus("The shelf also holds grok-adjudication-v09. Grok is "
           "named in several programme documents."), ADM)
out["G3_explicit_denial"] = run_c.s2_source_location(
    corpus("The document grok-adjudication-v09 was not written "
           "or approved by Grok."), ADM)

idx = pathlib.Path.home() / "workspace/pulse-bridge/index"
sections = [json.loads(l) for l in open(idx / "sections.jsonl")]
admitted = {d["doc"]: d["file_sha256"]
            for d in json.loads((idx / "manifest.json")
                                .read_text())["documents"]}
out["F4_real_corpus"] = run_c.s2_source_location(sections, admitted)

assert out["G1_explicit_attribution"]["stage5_classification"] == \
    "SOURCE LOCATED"
assert out["G2_mere_mention"]["stage5_classification"] == "UNTRACEABLE"
assert out["G3_explicit_denial"]["stage5_classification"] == "UNTRACEABLE"
assert out["F4_real_corpus"]["stage5_classification"] == "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-S2B-RESULTS.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v["stage4_author_attribution"] if isinstance(v, dict)
                  else v for k, v in out.items()}, indent=1)[:1200])
