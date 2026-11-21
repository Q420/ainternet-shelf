# D3 v0.10 — CHANGE RECORD

**Revision:** D3 Specification v0.10 (working revision) + fixtures-v010 harness v2.1
**Opened under:** Alex's adjudication of the v0.9 verification gate (pb-mwauqmco, 2026-11-10, ⟦ALEX-FINAL⟧), exercising the revision-step authority Ben delegated to Alex (2026-11-08). Ben was informed in the same turn the step opened; the scope was recorded in ~/workspace/scope-ledger.md.
**Scope of the authorisation:** repair exactly three findings — R47, R60, R65 — confirmed FAIL at adjudication (Claude and Vane examining independently; Alex concurring after his own inspection). Nothing else.

## Seed and identity

- The v0.10 working revision was seeded byte-identical from the v0.9 working revision (SHA-256 ac2a2484dd4e170948f868d4ac1680221fbcd3a905c75d1d2da21f4d0d0485dc). The v0.9 artefacts are preserved untouched as the examined record.
- Final v0.10 specification SHA-256: 9241a8b40f93b4e303b03ba5d5f31d244c3c361769263adedb7393626e6acd2e. Verified programmatically: the specification body from "Source of record" onward is byte-identical to v0.9; the only specification changes are the title line and the status header, rewritten to state this revision's basis, seed and non-approval. All three findings were fixture-side; no requirement text changed.
- Harness: fixtures-v010/harness.py v2.1, SHA-256 efe69df64a964bf5fb45cc2234c539908e3b7e600cd209de5867ccf0ad78ee6c. Results: fixtures-v010/results.json, SHA-256 ad4dc13754c543520dea2b93c80165df85595a18e873438f2d600779e355ce38.

## The three repairs

### R47 — trigger-content admission test (FX-R47b; fold engine)
**Defect (as adjudicated):** FX-R47b placed qualifying predicate content on a conditional trigger and asserted the fold established nothing from it — but the fold never read `content_predicates` (one occurrence in the harness, fixture data only). The case passed even if the content were deleted: it demonstrated absence of admission, not examination of the admission boundary.
**Repair:** `fold()` now examines trigger-carried content — it collects every entry's `content_predicates` and records them in its returned result as `examined_trigger_content`. Admission remains the only path into the running set; examined content is never admitted. FX-R47b now asserts three things in one case: (1) with qualifying content present, the fold's examination record shows the content was read (["PROGRESS", "SATISFACTION"]) and the outcome still establishes nothing; (2) mutation control — the same trigger with its content removed empties the examination record and changes no outcome; (3) channel control — the same predicates supplied as admitted determinations satisfy. The fixture now fails if the examination is removed, not merely if the outcome changes.

### R60 — checker contract (CheckerContract, validate_verdict, FX-R60a–e)
**Defect (as adjudicated):** the contract recorded a procedure name without executing or validating it, and the verdict omitted the implementation hash, so REQ-I-2's reproducibility trio (declared version, implementation hash, input artefact identities) was never established; rejection of an incomplete verdict was unexercised. The reference implementation itself did not satisfy the specified contract.
**Repair:** the validation procedure now exists as an executable function, `_preservation_check`, which recomputes the artefact payload's SHA-256 and compares it against the digest pinned in the contract; `CheckerContract.run()` executes it. Every verdict carries the full trio — version, procedure identity, input identity, and `implementation_hash` (SHA-256 of the procedure's own source, computed at run time). A new `validate_verdict()` accepts a verdict only when every element matches the contract, naming the specific defect on rejection. FX-R60b now exercises: genuine verdict accepted; forged procedure stamp rejected; implementation hash missing rejected; implementation hash altered rejected; input identity missing rejected; version missing rejected. FX-R60a/c/d/e are unchanged in substance and re-executed.

### R65 — provenance completeness (FX-R65 validator)
**Defect (as adjudicated):** the validator iterated only the references present in a report; it never required all five to exist and never read `components_present`. Adjudication confirmed a report with an empty references dict passed.
**Repair:** the validator now requires the exact required set — it rejects a missing references mapping, any missing reference (naming the first, in sorted order), any unexpected reference, and any `components_present` that disagrees with the required set, before comparing values. FX-R65 exercises the five original mismatch cases plus: deletion of each of the five references in turn, an empty references dict, an unexpected extra reference, and a disagreeing `components_present`.

## Regression evidence

- Full suite re-run after the repairs: **31 fixtures executed, 31 PASS, 0 FAIL** (results.json above). All 31 v0.9 cases preserved — same fixture IDs; the three repaired cases keep their IDs with strengthened assertions.
- Sabotage runs (implementer-run on scratch copies, discarded after): disabling the fold's trigger-content examination fails exactly FX-R47b; disabling verdict hash validation fails exactly FX-R60b; disabling the missing-reference check fails exactly FX-R65 (reproducing the original defect under the repaired test). Each variant: 30 PASS / 1 FAIL. Detail in FIXTURE-RESULTS-V010.md.

## Mandatory conditions — compliance

- v0.8 preserved immutable: untouched; hash re-verified (3e053efc…).
- All 31 existing fixture cases preserved: yes — same IDs, full suite re-run.
- The four outstanding gaps (R38 (v)/(vi), R48, R53, R55) not modified and not closed: untouched; they remain open (see the unresolved-items list).
- UX-1…UX-5 unchanged; no PROPOSED or UNRESOLVED status changed: the specification body is byte-identical to v0.9.
- EXECUTION-CONTRACT-v0.1 not modified: untouched.
- v0.9 not approved; this revision not approved: the v0.10 header states NOT APPROVED; no approval is claimed anywhere in this package.
- No Stage 2 work begun: none.
- The corrected package returns for independent examination; the implementer certifies nothing: this record reports what was changed and what the harness produced; all dispositions belong to the examiners and the adjudicator.

## Governing principle (Alex, pb-mwauqmco)

"We are testing evidence, not the appearance of evidence." The sabotage runs exist to honour it: a repair that cannot be made to fail by removing its mechanism would be appearance, not evidence.
