# RECONCILIATION — V2.4.5 DELTA

Answers Alex's V2.4.4 adjudication (five-stage S2 model
accepted; stage-4 evidence too permissive). Everything
else stands.

## Stage 4 — attribution must be an assertion

The old stage-4 test (candidate id + the word "Grok"
co-occurring in another admitted document) is withdrawn:
a denial contains both strings and says the opposite.
Stage 4 now requires, in a DIFFERENT admitted document, a
sentence that (a) names the candidate and (b) carries an
unnegated attribution assertion from a defined pattern
set ("Grok's adjudication", "adjudication by Grok",
"authored / written / issued / approved by Grok",
"Grok authored / approved"). A sentence carrying a
negation over the attribution is not evidence. Matching
evidence sentences are quoted in the stage record, so the
basis is inspectable.

Stated limits, not hidden: the rule is assertion-SHAPED,
not semantic understanding. It is deliberately
conservative — an attribution split across sentences, or
worded outside the pattern set, is missed rather than
risked. For the claim class at issue (a formal
adjudication), an explicit assertion in an admitted
record is the expected form.

Fixtures (v245/fixture_s2b.py, real procedure; candidate
admitted in all synthetic cases): **G1** explicit
attribution ("records the ruling issued by Grok") →
evidence found, SOURCE LOCATED. **G2** mere co-occurrence
→ none found, UNTRACEABLE. **G3** explicit denial ("was
not written or approved by Grok") → not evidence,
UNTRACEABLE. **F4** real-corpus regression → stage 4 NOT
PERFORMED, UNTRACEABLE. The candidate's own claims remain
excluded from its own evidence by construction (the
evidence search skips the candidate's documents).
