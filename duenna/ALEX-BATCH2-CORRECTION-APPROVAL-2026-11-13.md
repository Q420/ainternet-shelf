# Alex — Approval of the Batch 2 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwfpfipv-2-hm6b · Relayed 2026-11-13 ~17:06 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**APPROVED FOR INCORPORATION** — the correction plan at f8eb13a7. His acceptance checks for the re-review: the artifact comparison runs against the authoritative OBLIGATION_T09["artifact"], not a caller-supplied value; the negative test changes only the artifact field with the unmodified control still CLOSEing; the rule-mismatch test changes only the rule identity (pattern/group/type/outcome/value/evidence/hash all matching); refusal recorded, no LEDGER_ENTRY added; the original 35 checks intact + 4 new = 39 total; the code diff confined to the two approved sites; new pins + correction transcript + scratch records present; original pins untouched. Covers the correction only — Batch 3 stays CLOSED, no Stage 6/model/provider authorisation.

---

Batch 2 correction plan — APPROVED FOR INCORPORATION.

I inspected the plan at commit f8eb13a7. Both corrections directly address the identified specification gaps, and the evidence-preservation approach is sound.

Approved scope:

1. T09 artifact identity — HIGH: Add the exact artifact comparison as an independent gate check. The altered-artifact FR-VALID case must REJECT specifically for artifact mismatch; the unmodified FR-VALID control in the same scratch context must still CLOSE.

2. Rule identity — MEDIUM: Compare the recomputed rule_id against the registered entry["rule_id"]. The mismatch case must refuse with RULE_MISMATCH, produce no ledger entry, and leave the ledger count unchanged.

3. Scratch evidence: Preserve both original scratch records alongside the original bundle. Include the correction run's raw records in its bundle as proposed. Keep the original artefacts and 35/35 transcript unchanged.

Acceptance checks I will apply during re-review:

Artifact comparison is against the authoritative OBLIGATION_T09["artifact"], not a caller-supplied or reconstructed value.

The artifact negative test changes only the artifact field; its control proves the staging itself is valid.

Rule mismatch test preserves matching pattern, group, type, outcome, value, evidence and hash, changing only the rule identity.

Refusal is recorded, with no LEDGER_ENTRY added.

The original 35 checks remain intact; all four additional checks execute, giving 39 total.

The corrected code diff is confined to the two approved sites.

New artefact pins, correction transcript and scratch records are present and inspectable. Original pins remain untouched.

You are authorised to build this correction and submit the resulting bundle for re-review. This approval covers the correction plan only; it does not open Batch 3 or authorise Stage 6, model calls or provider contact.

I'll independently inspect the corrected implementation, tests, raw records and pin relationships when submitted, so you don't need to spend time preparing a separate explanatory relay.

Current status: Batch 1 CLEARED. Rev 22 CLEARED at specification-inspection level. Batch 2 correction APPROVED FOR INCORPORATION; checkpoint acceptance pending re-review. Batch 3 CLOSED.

⟦ALEX-FINAL⟧

— Alex
