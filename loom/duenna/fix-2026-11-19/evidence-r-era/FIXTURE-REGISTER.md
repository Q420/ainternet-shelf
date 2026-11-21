# D3 v0.10 — FIXTURE REGISTER (revision build)

Every fixture case executed in the v0.10 revision build, generated mechanically from the machine
results (results.json, harness v2.1 run) so that no row is a transcription.
Harness: fixtures-v010/harness.py v2.1 (SHA-256 efe69df64a964bf5fb45cc2234c539908e3b7e600cd209de5867ccf0ad78ee6c).

| Fixture | Finding | Requirement | Result |
|---|---|---|---|
| FX-R62 | R62 | REQ-K-1 outcome (i) | PASS |
| FX-R40a | R40 | REQ-A-2/A-1 unconditional creation at binding | PASS |
| FX-R40b | R40 | REQ-A-1 conditional creation; kind preserved; separate CREATION entry | PASS |
| FX-R40c | R40 | REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected | PASS |
| FX-R40d | R40 | REQ-A-2 unresolvable role fails loudly and totally | PASS |
| FX-R40e | R40 | REQ-A-3 classification procedure over bearer-present and bearer-missing instances | PASS |
| FX-R47a | R47 | REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected | PASS |
| FX-R47b | R47 | REQ-C-1 conditional trigger: qualifying content is examined by the fold and establishes nothing; removing the content empties the examination record and changes no outcome; admitted determinations with the same predicates satisfy | PASS |
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
| FX-R65 | R65 | REQ-K-4 all five provenance relationships: intact report passes; a mismatch or a deletion of any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails; empty references, an unexpected reference, and a components_present that disagrees with the required set all fail | PASS |
| FX-R60a | R60 | REQ-I-2 defined input artefact: defined input accepted; a different artefact refused | PASS |
| FX-R60b | R60 | REQ-I-2 validation procedure and reproducibility trio: genuine verdict accepted; forged procedure, missing/altered implementation hash, missing input identity and missing version all rejected | PASS |
| FX-R60c | R60 | REQ-I-2 reproducible result: repeated runs produce identical verdicts | PASS |
| FX-R60d | R60 | REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict | PASS |
| FX-R60e | R60 | REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected | PASS |
| FX-R61 | R61 | REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution | PASS |
