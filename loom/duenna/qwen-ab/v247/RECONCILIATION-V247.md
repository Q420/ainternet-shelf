# RECONCILIATION — V2.4.7 DELTA

Answers Alex's V2.4.6 review (a phrase in a sentence is
not a relationship; three new false-positive paths; a
punctuation edge). Five-stage model preserved.

## The pattern set — reviewed, two patterns REMOVED

Per Alex's direction (don't retain a pattern because its
fixture can pass), every pattern was re-judged on whether
it expresses authorship, issuance or approval:
**REMOVED: "grok's adjudication", "grok's ruling."** A
possessive names or labels a document as readily as it
attributes one — titles, headings and naming commands all
use it. The retained set is AGENTIVE only, verbatim from
run_c.ATTRIBUTION_PATTERNS (single source; fixture
templates assert key-set identity): "adjudication by
grok" · "authored by grok" · "written by grok" ·
"issued by grok" · "approved by grok" · "grok authored" ·
"grok approved". Each states the relationship in the
sentence's grammar.

## Three new screens

- **Titles/labels:** labelling verbs (titled / called /
  labelled / labeled / named / headed) disqualify the
  sentence; quoted spans are stripped before matching (a
  quoted phrase is mentioned, not used). Fixture H1.
- **Imperatives:** a sentence-initial imperative cue
  (call / cite / refer / file / list / treat / describe /
  mark / note / see / name / title / label) disqualifies
  the sentence — a command is not an assertion. Fixtures
  H2 (possessive imperative) and H2b (agentive imperative).
- **Interrogatives:** ANY "?" in the sentence
  disqualifies it — this closes the closing-quote edge
  ('…Grok's adjudication?"') without depending on the
  sentence's final character. Fixture H3.

Positives for all seven retained patterns pass
(fixture_s2d.py P-cases); G1/G3/G4/G5 and the real-corpus
regression hold. All screens are conservative: any doubt
about a sentence's form excludes it as evidence.
