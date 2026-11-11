#!/usr/bin/env python3
"""V2.4.6 FIXTURES — stage 4 must accept assertions only.
Exercises the REAL procedure + the REAL declared pattern
set (run_c.ATTRIBUTION_PATTERNS). No model calls; not a
battery or diagnostic run. Candidate admitted throughout.

G4  interrogative ("Is grok-adjudication-v09 Grok's
    adjudication?") -> not an assertion -> UNTRACEABLE.
G5  hedged ("may be Grok's adjudication, though this is
    unverified") -> not an assertion -> UNTRACEABLE.
G6  one positive corpus per declared pattern (the fixture
    builds its sentences from templates keyed to
    run_c.ATTRIBUTION_PATTERNS and asserts the key sets are
    identical, so a code/doc drift fails loudly) -> each
    must yield SOURCE LOCATED via its own pattern.
G1–G3 regressions + F4 real corpus.
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

TEMPLATES = {
    "grok's adjudication":
        "The programme records list grok-adjudication-v09 as "
        "Grok's adjudication on the v0.9 gate.",
    "grok's ruling":
        "The document grok-adjudication-v09 is catalogued in "
        "the register as Grok's ruling on the gate.",
    "adjudication by grok":
        "The file grok-adjudication-v09 is the adjudication "
        "by Grok concerning the v0.9 gate.",
    "authored by grok":
        "The document grok-adjudication-v09 was authored by "
        "Grok for the program record.",
    "written by grok":
        "The text of grok-adjudication-v09 was written by "
        "Grok and filed on the shelf.",
    "issued by grok":
        "The adjudication grok-adjudication-v09 records the "
        "ruling issued by Grok on the v0.9 gate.",
    "approved by grok":
        "The gate decision recorded in grok-adjudication-v09 "
        "was approved by Grok.",
    "grok authored":
        "Grok authored grok-adjudication-v09 as his "
        "adjudication of the v0.9 gate.",
    "grok approved":
        "Grok approved the v0.9 gate in "
        "grok-adjudication-v09 for the record.",
}
assert set(TEMPLATES) == set(run_c.ATTRIBUTION_PATTERNS), \
    "template keys != declared pattern set"

out = {}
out["G4_interrogative"] = run_c.s2_source_location(
    corpus("Is grok-adjudication-v09 Grok's adjudication?"), ADM)
out["G5_hedged"] = run_c.s2_source_location(
    corpus("The document grok-adjudication-v09 may be Grok's "
           "adjudication, though this is unverified."), ADM)
g6 = {}
for pattern, sentence in TEMPLATES.items():
    r = run_c.s2_source_location(corpus(sentence), ADM)
    g6[pattern] = {"classification": r["stage5_classification"],
                   "stage4": r["stage4_author_attribution"]}
out["G6_every_declared_pattern"] = g6
out["G1_regression"] = run_c.s2_source_location(
    corpus("The adjudication grok-adjudication-v09 records the "
           "ruling issued by Grok on the v0.9 gate."), ADM)
out["G3_regression_denial"] = run_c.s2_source_location(
    corpus("The document grok-adjudication-v09 was not written "
           "or approved by Grok."), ADM)
idx = pathlib.Path.home() / "workspace/pulse-bridge/index"
sections = [json.loads(l) for l in open(idx / "sections.jsonl")]
admitted = {d["doc"]: d["file_sha256"]
            for d in json.loads((idx / "manifest.json")
                                .read_text())["documents"]}
out["F4_real_corpus"] = run_c.s2_source_location(sections, admitted)

assert out["G4_interrogative"]["stage5_classification"] == "UNTRACEABLE"
assert out["G5_hedged"]["stage5_classification"] == "UNTRACEABLE"
for pattern, r in g6.items():
    assert r["classification"] == "SOURCE LOCATED", pattern
assert out["G1_regression"]["stage5_classification"] == "SOURCE LOCATED"
assert out["G3_regression_denial"]["stage5_classification"] == \
    "UNTRACEABLE"
assert out["F4_real_corpus"]["stage5_classification"] == "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-S2C-RESULTS.json").write_text(json.dumps(out, indent=1))
print("G4:", out["G4_interrogative"]["stage5_classification"],
      "| G5:", out["G5_hedged"]["stage5_classification"],
      "| G6 patterns located:",
      sum(1 for r in g6.values()
          if r["classification"] == "SOURCE LOCATED"), "/", len(g6))
