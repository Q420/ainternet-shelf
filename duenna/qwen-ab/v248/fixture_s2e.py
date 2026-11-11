#!/usr/bin/env python3
"""V2.4.8 FIXTURES — stage 4 must BIND the pattern to the
candidate. Exercises the REAL procedure + declared set.
No model calls; not a battery or diagnostic run.

I1  single-quoted search term -> UNTRACEABLE.
I2  backtick-quoted search term -> UNTRACEABLE.
I3  unrelated statements joined in one sentence
    (candidate in one clause, pattern in another) ->
    UNTRACEABLE.
I4  pattern describes a DIFFERENT document ->
    UNTRACEABLE.
P   positives for every retained pattern (7) ->
    SOURCE LOCATED each.
Regressions: H1, H2b, H3, G3, G4, G5, F4.
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
assert set(TEMPLATES) == set(run_c.ATTRIBUTION_PATTERNS)

out = {}
out["I1_single_quoted_term"] = run_c.s2_source_location(
    corpus("The entry grok-adjudication-v09 contains the "
           "search term 'authored by Grok'."), ADM)
out["I2_backtick_term"] = run_c.s2_source_location(
    corpus("The entry grok-adjudication-v09 contains the "
           "search term `authored by Grok`."), ADM)
out["I3_unrelated_joined"] = run_c.s2_source_location(
    corpus("Ben shelved grok-adjudication-v09, and the style "
           "guide notes that rulings are authored by Grok."), ADM)
out["I4_different_document"] = run_c.s2_source_location(
    corpus("The register cites alex-adjudication-v08, "
           "authored by Grok, alongside grok-adjudication-v09."),
    ADM)
pos = {}
for pattern, sentence in TEMPLATES.items():
    pos[pattern] = cls(run_c.s2_source_location(
        corpus(sentence), ADM))
out["P_retained_patterns"] = pos
out["H1_regression"] = run_c.s2_source_location(
    corpus('The entry grok-adjudication-v09 is titled '
           '"Grok\'s adjudication".'), ADM)
out["H2b_regression"] = run_c.s2_source_location(
    corpus("Cite the adjudication by Grok when you reference "
           "grok-adjudication-v09."), ADM)
out["H3_regression"] = run_c.s2_source_location(
    corpus('The register asks: "Is grok-adjudication-v09 '
           'Grok\'s adjudication?"'), ADM)
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

for k in ("I1_single_quoted_term", "I2_backtick_term",
          "I3_unrelated_joined", "I4_different_document"):
    assert cls(out[k]) == "UNTRACEABLE", k
for pattern, c in pos.items():
    assert c == "SOURCE LOCATED", pattern
assert cls(out["H1_regression"]) == "UNTRACEABLE"
assert cls(out["H2b_regression"]) == "UNTRACEABLE"
assert cls(out["H3_regression"]) == "UNTRACEABLE"
assert cls(out["G3_regression_denial"]) == "UNTRACEABLE"
assert cls(out["G4_regression_interrogative"]) == "UNTRACEABLE"
assert cls(out["G5_regression_hedged"]) == "UNTRACEABLE"
assert cls(out["F4_real_corpus"]) == "UNTRACEABLE"
out["assertions"] = "all passed"
(HERE / "FIXTURE-S2E-RESULTS.json").write_text(json.dumps(out, indent=1))
print("I1–I4:", [cls(out[k]) for k in
      ("I1_single_quoted_term", "I2_backtick_term",
       "I3_unrelated_joined", "I4_different_document")],
      "| positives:", sum(1 for c in pos.values()
                          if c == "SOURCE LOCATED"), "/", len(pos))
