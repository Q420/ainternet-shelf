#!/usr/bin/env python3
"""V2.4.7 FIXTURES — stage 4 must establish the RELATIONSHIP.
Exercises the REAL procedure + declared pattern set.
No model calls; not a battery or diagnostic run.
Candidate admitted throughout.

H1  title/label: 'The entry grok-adjudication-v09 is
    titled "Grok's adjudication".' -> UNTRACEABLE.
H2  imperative (possessive): 'Call grok-adjudication-v09
    Grok's ruling.' -> UNTRACEABLE.
H2b imperative (agentive): 'Cite the adjudication by Grok
    when you reference grok-adjudication-v09.' ->
    UNTRACEABLE.
H3  quoted question: 'The register asks: "Is
    grok-adjudication-v09 Grok's adjudication?"' ->
    UNTRACEABLE.
P   positives for every RETAINED pattern (7) -> each
    SOURCE LOCATED via its own pattern.
Regressions: G1, G3, G4, G5, F4.
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

def cls(r):
    return r["stage5_classification"]

TEMPLATES = {
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
    "templates != retained pattern set"

out = {}
out["H1_title_label"] = run_c.s2_source_location(
    corpus('The entry grok-adjudication-v09 is titled '
           '"Grok\'s adjudication".'), ADM)
out["H2_imperative_possessive"] = run_c.s2_source_location(
    corpus("Call grok-adjudication-v09 Grok's ruling."), ADM)
out["H2b_imperative_agentive"] = run_c.s2_source_location(
    corpus("Cite the adjudication by Grok when you reference "
           "grok-adjudication-v09."), ADM)
out["H3_quoted_question"] = run_c.s2_source_location(
    corpus('The register asks: "Is grok-adjudication-v09 '
           'Grok\'s adjudication?"'), ADM)
pos = {}
for pattern, sentence in TEMPLATES.items():
    r = run_c.s2_source_location(corpus(sentence), ADM)
    pos[pattern] = cls(r)
out["P_retained_patterns"] = pos
out["G1_regression"] = run_c.s2_source_location(
    corpus("The adjudication grok-adjudication-v09 records the "
           "ruling issued by Grok on the v0.9 gate."), ADM)
out["G3_regression_denial"] = run_c.s2_source_location(
    corpus("The document grok-adjudication-v09 was not written "
           "or approved by Grok."), ADM)
out["G4_regression_interrogative"] = run_c.s2_source_location(
    corpus("Is grok-adjudication-v09 Grok's adjudication?"), ADM)
out["G5_regression_hedged"] = run_c.s2_source_location(
    corpus("The document grok-adjudication-v09 may be Grok's "
           "adjudication, though this is unverified."), ADM)
idx = pathlib.Path.home() / "workspace/pulse-bridge/index"
sections = [json.loads(l) for l in open(idx / "sections.jsonl")]
admitted = {d["doc"]: d["file_sha256"]
            for d in json.loads((idx / "manifest.json")
                                .read_text())["documents"]}
out["F4_real_corpus"] = run_c.s2_source_location(sections, admitted)

assert cls(out["H1_title_label"]) == "UNTRACEABLE"
assert cls(out["H2_imperative_possessive"]) == "UNTRACEABLE"
assert cls(out["H2b_imperative_agentive"]) == "UNTRACEABLE"
assert cls(out["H3_quoted_question"]) == "UNTRACEABLE"
for pattern, c in pos.items():
    assert c == "SOURCE LOCATED", pattern
assert cls(out["G1_regression"]) == "SOURCE LOCATED"
assert cls(out["G3_regression_denial"]) == "UNTRACEABLE"
assert cls(out["G4_regression_interrogative"]) == "UNTRACEABLE"
assert cls(out["G5_regression_hedged"]) == "UNTRACEABLE"
assert cls(out["F4_real_corpus"]) == "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-S2D-RESULTS.json").write_text(json.dumps(out, indent=1))
print("H1/H2/H2b/H3:", [cls(out[k]) for k in
      ("H1_title_label", "H2_imperative_possessive",
       "H2b_imperative_agentive", "H3_quoted_question")],
      "| positives:", sum(1 for c in pos.values()
                          if c == "SOURCE LOCATED"), "/", len(pos))
