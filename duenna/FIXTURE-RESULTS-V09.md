# D3 v0.9 — FIXTURE RESULTS (revision build)

**Harness:** fixtures-v09/harness.py v2.0, SHA-256 678f4e636c3d785d61d720a5f0faf10a8a09f0527b70b9ea7bc95d3058680c1d
**Run:** `python3 harness.py` from fixtures-v09/ (Python 3.12.3)
**Results file:** results.json, SHA-256 7fb8f6d25dc58c143b8a832bf0b2f15f90f515f4833fac79348f2d40b22d1a8f
**Outcome: 31 fixtures executed, 31 PASS, 0 FAIL**

Authorised by Alex (pb-mwad2zc6-6-k60l) to address the six findings left open by
independent verification of the v0.8 package. The complete suite was re-run —
every carried-over fixture plus the new and extended coverage — not only the
new tests. The v0.8 harness (v1.2) and its results are preserved untouched in
fixtures-v08/; the v0.8 specification is immutable (SHA-256
3e053efc97d876d50f649eb0b4c8c740ab6085314aa54f9132fdf33e243d97d4, re-verified
after this run).

TEST BOUNDARY: these fixtures exercise small reference procedures written from
the specification text. They validate the mechanical coherence of the SPECIFIED
RULES as implemented in these reference procedures. No separate production
evaluator exists in this stage, and nothing here certifies one.

## What changed for the six findings

- **R47** — FX-R47b now runs a conditional trigger whose content WOULD qualify
  (PROGRESS + SATISFACTION predicates carried on the trigger entry) and shows
  the fold establishing nothing from it, with a control run proving the same
  predicates satisfy when supplied as admitted determinations. FX-R47c's
  INDETERMINATE is now emitted by the fold's own REQ-C-2 resolution, not
  written by the test.
- **R56** — split into FX-R56a (the full three-way separation holds; each
  role's verdict independently necessary, exercised by removing each role in
  turn) and FX-R56b (every prohibited substitution: evaluator->examiner,
  examiner->gate, evaluator->gate, plus self-verification — each rejected).
- **R60** — the checker is now a standalone CheckerContract object defined by
  the harness, not a closure inside the fixture. FX-R60a–e exercise the five
  properties independently: defined input artefact, validation procedure,
  reproducible result, failure paths, pinned/recorded version.
- **R63** — FX-R63a validates the creation block against a stream the binding
  machinery actually produced, with an interleaved stream as a negative case.
  FX-R63c (new) exercises the matrix's third item: every entry's stable
  identity, record position, and instance identity or declared instance-free
  status, with tampered-position and missing-identity negatives. FX-R63b also
  covers the valid role-free entry.
- **R65** — FX-R65 now mismatches each of the five provenance relationships in
  turn (evaluation_record, content_identity, procedure, defect_link,
  verdict_trio); each fails validation while every component is present.

## Results by fixture (mechanical, from results.json)

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 conditional trigger with qualifying content establishes nothing; admitted determinations with the same predicates satisfy | PASS |
| FX-R47c | R47 | REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE | PASS |
| FX-R63a | R63 | REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected | PASS |
| FX-R63c | R63 | REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected | PASS |
| FX-R63b | R63 | REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted | PASS |
| FX-R44 | R44 | REQ-B-2 reverse mix: artefact progress + event satisfaction | PASS |
| FX-R52 | R52 | REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED | PASS |
| FX-R49a | R49 | D3-CANON-1 composition-distinct strings/keys are distinct | PASS |
| FX-R49b | R49 | D3-CANON-1 duplicate exact keys rejected at parse, recursively | PASS |
| FX-R49c | R49 | D3-CANON-1 member order + whitespace variants share one digest | PASS |
| FX-R49d | R49 | D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected | PASS |
| FX-R54a | R54 | REQ-E-3 one response, two event-specific requirements, no multi-use permission | PASS |
| FX-R54b | R54 | REQ-E-3 multi-use expressly permitted by the rule | PASS |
| FX-R56a | R56 | REQ-E-6 full three-way separation holds; each role's verdict independently necessary | PASS |
| FX-R56b | R56 | REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification | PASS |
| FX-R57 | R57 | REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently | PASS |
| FX-R64 | R64 | REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail | PASS |
| FX-R65 | R65 | REQ-K-4 all five provenance relationships: intact report passes; a mismatch in any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails validation | PASS |
| FX-R60a | R60 | REQ-I-2 defined input artefact: defined input accepted; a different artefact refused | PASS |
| FX-R60b | R60 | REQ-I-2 validation procedure: verdict stamped with the contract procedure; foreign procedure stamp detected | PASS |
| FX-R60c | R60 | REQ-I-2 reproducible result: repeated runs produce identical verdicts | PASS |
| FX-R60d | R60 | REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict | PASS |
| FX-R60e | R60 | REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |
