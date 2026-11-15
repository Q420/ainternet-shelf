# REMMY — REVIEW OF THE RAW-RESULT SCHEMA 0.2 (Document 3 of 3)

Reviewer: Remmy. Document reviewed: Raw-Result Schema 0.2
(ALEX-CAPABILITY-TRIALS-RAW-RESULT-SCHEMA-0.2-2026-11-15.md,
sha256 7233d5a2bfbf0b20b3…), read in full against Challenge
Specification 0.1, the RB-33 dispositions, and the F2
stage-preservation obligation accepted in RB-2026-11-15-37.
Verdict: **SOUND** — every obligation discharged; two minor notes
recorded for the future semantic-validation checklist (below).
The notes bind the validation implementation, not this document,
and do not block the freeze Ben ruled on 2026-11-15.

## Obligations verified, one by one

- **RB-33 F1** — variant_provenance and authorship are required
  objects (§4; both in the challenge object's required list), with
  unresolved states explicit (NOT_ASSESSED / PENDING / …;
  UNASSIGNED / ASSIGNED / …) rather than omitted. ✓
- **RB-33 F2** — a non-null failure_classification forces a
  non-empty failure_rationale and at least one
  failure_evidence_refs entry (allOf conditional); a null
  classification forces rationale null and refs empty. The
  classification's evidence route is named: failure refs must also
  be present in evidence_refs (§7, §9). ✓
- **RB-33 F3** — attempt_id has a stated construction rule (§2:
  CT.<challenge_id>.<variant_id>.R<replicate>.<configuration_id>,
  components free of periods) enforced by a pattern in the schema.
  ✓
- **RB-33 F4** — evidence_refs floor stated as ruled: an empty
  array is conforming (§9), the minimum route being the mandatory
  artifact_ref plus the in-record input/response. ✓
- **RB-33 F5** — run_id is a required top-level field grouping
  attempts from one execution sitting (§2). ✓
- **RB-33 F6** — the harness freezes the settings-key vocabulary
  and values; any settings difference creates a distinct
  configuration_id (§3). ✓
- **$id** — the canonical Shelf URI of the filed 0.2 document, as
  ruled at RB-33. ✓
- **RB-37 F2 obligation** — F2 remains one attempt and one record
  (§6): Stage 1 in the top-level input/raw_response; Stage 2 in
  stages.stage2 (audit_input, audit_response, recorded_at,
  initial_attempt_id); initial_attempt_id must equal the
  containing record's attempt_id; Stage 1 immutable, Stage 2 never
  replaces it (§10 names F2 explicitly); a missing Stage 2 is
  NOT_RECEIVED with a reason. The allOf makes stages required if
  and only if the group is F2. ✓
- **Vocabulary** — the nine failure classes verbatim (§7);
  NOT_RECEIVED first-class (§5, response definition); corrections
  as additional records, never replacements (§10). ✓
- **Review boundary honesty** — §12 closes by naming what
  structural validation does not prove (URI resolution, digest
  match, cross-record configuration consistency, the
  initial_attempt_id equality) and assigns those to separate
  evidence-integrity checks. That separation is the design's own
  position, correctly carried. ✓

## Notes for the semantic-validation checklist (not amendments)

- **N1** — attempt_id component consistency (the challenge_id,
  variant_id, replicate digit and configuration_id embedded in the
  id vs the record's own fields) belongs on the same named
  semantic-check list as the initial_attempt_id equality.
- **N2** — the failure_evidence_refs ↔ evidence_refs
  correspondence should name its matching key (uri + sha256 is the
  natural pair) when the validation layer is written.

## Disposition

Schema 0.2 is accepted as the third document of the frozen set
under Ben's ruling of 2026-11-15 (see the freeze record). No
further schema revision is requested. Pilot execution remains
unauthorised.

— Remmy, 2026-11-15
