# T03 Remediation — Amendment Draft 0.1 (Alex)

Source: Alex (ChatGPT desk), reply to RB-2026-11-15-38, conversation 6af966fb-2150-83e8-9985-4e82978b592c, captured 2026-11-15T01:21:42-0700 via the Remmy Browser watcher (watcher-sweep). Filed verbatim by Remmy. Authority: Ben's ruling 2026-11-15 01:15 MST. Alex fixes the rule content and amendment obligations; mapping onto the live artefact formats (EXTRACTOR-RULES-02 / PILOT-DATA-PACKS-01 / pin authority) is Remmy's implementation work. His quoted document SHA-256 for the R60REV source is his claim from the Shelf manifest — provenance is verified from the pinned corpus snapshot itself during implementation, per the draft's own section 3.

---

The capability-trials programme is now established and its three-document paper basis is frozen. That closes the design lane; the 216-attempt pilot remains unauthorised until you separately approve execution.

The T03 assignment is authorised. I’ll keep this to the amendment draft: three disposition rules, the Correction B source-pack addition, and the corresponding pin/manifest changes. Remmy retains implementation, re-freeze and recalibration.

The source review confirms the three dispositions belong to alex-combined-adjudication-v010#002, while Correction B's status belongs to the separate alex-combined-adjudication-r60rev#001. Remmy's precision is important: three new extraction rules, not four. Correction B is fixed by adding its source to the pack.

One implementation detail remains unverified: the current EXTRACTOR-RULES-02, PILOT-DATA-PACKS-01 and PILOT-PIN-AUTHORITY-01 files are not present on the Shelf. I won't invent their JSON field names or hashes. The draft below fixes the exact rule content and amendment obligations for Remmy to map onto the live artefact format.

Writing
T03 Remediation — Amendment Draft 0.1

Prepared by: Alex
Authority: Ben's ruling, 2026-11-15 01:15 MST
Basis: T03 Remediation Proposal 0.1, as qualified by Remmy RB-35
Status: Draft for Remmy's implementation
Scope: Three EXTRACTOR-RULES entries; one T03 pack addition; re-freeze pin and manifest updates. No tree re-scope.

1. EXTRACTOR-RULES-02 additions

All three rules read from:

Source reference: alex-combined-adjudication-v010#002

Source document: duenna/ALEX-COMBINED-ADJUDICATION-V010.md

Source section: Final dispositions

Expected source type: Markdown text

Expected extracted type: string

Match cardinality: exactly one match per rule

Missing or multiple matches: extraction failure; do not infer, default, or choose a match.

Rule: R47 disposition

Pattern:

(?m)^- \*\*R47 — PASS, narrow\.\*\*$

Interpretation:

PASS (narrow)

The qualifier is mandatory. Do not reduce this to an unqualified PASS.

Type expectation: string, exact value PASS (narrow).

Rule: R60 disposition

Pattern:

(?m)^- \*\*R60 — FAIL\.\*\*$

Interpretation:

FAIL

Type expectation: string, exact value FAIL.

Do not infer a different status from the later revision record. This rule extracts the disposition in the specified v0.10 combined adjudication.

Rule: R65 disposition

Pattern:

(?m)^- \*\*R65 — PASS, qualified\.\*\*$

Interpretation:

PASS (qualified)

The qualification is mandatory. Do not reduce this to an unqualified PASS.

Type expectation: string, exact value PASS (qualified).

Shared rule requirements

Match only within the specified source section.

Preserve the distinction between the source's literal wording and the normalized extracted value.

Require exactly one match.

Preserve the source reference and matched evidence text in the extraction result.

A missing, duplicate, malformed or type-invalid match is a failed extraction, not an invitation to infer the intended disposition.

Do not add a fourth extraction rule for Correction B.

2. T03 pack amendment

Target: The T03 entry in PILOT-DATA-PACKS-01.

Existing source set: Preserve every existing T03 item unchanged.

Add this item:

source_ref: alex-combined-adjudication-r60rev#001
document: ALEX-COMBINED-ADJUDICATION-R60REV.md
source_section: Summary of dispositions
item_kind: record document
purpose: authoritative Correction B disposition

Source identity: The Shelf manifest records the source document SHA-256 as:

393cba4c8adae5b153580a1a42dede4543701712f8e99592b2694e0aa2aa366b

The section-level hash must be taken from the pinned corpus snapshot's own manifest. Do not substitute the document hash for the section hash.

Expected content: The source records Correction B as OPEN, with a failing case standing. That status is obtained from this source record, not inferred from the v0.10 adjudication or reconstructed from another report.

Pack integrity: Recompute the T03 pack digest and the containing PILOT-DATA-PACKS-01 file digest after the addition.

3. Re-freeze pin and manifest updates

The re-freeze amendment should carry the following changes:

Artefact	Required action
EXTRACTOR-RULES-02	Add the three rules above; compute and record the new file SHA-256 and byte length
PILOT-DATA-PACKS-01	Add the R60REV section to T03; compute and record the new file SHA-256 and byte length
PILOT-PIN-AUTHORITY-01	Regenerate from the amended manifest and re-freeze amendment; record its new SHA-256
PILOT-CALIBRATION-01	Issue a new certificate after complete offline recalibration; preserve the prior certificate unchanged
Corpus snapshot condition

First verify that alex-combined-adjudication-r60rev#001 already exists in the frozen corpus snapshot and that its section hash matches the authoritative source.

If it exists and verifies, the corpus snapshot itself does not need to change. Only the T03 pack membership changes.

If it does not exist or fails verification, stop the re-freeze draft at that dependency. The snapshot and its manifest must then be amended and pinned through the same recorded process. Do not silently source the section from outside the pinned snapshot.

Pin authority

The regenerated authority must include the amended pack and rules files, with each pin traceable to the re-freeze amendment. Its own hash must be recorded in the amendment that establishes it.

Do not overwrite the original freeze record or silently replace historical pin values. The amendment must preserve the previous values and identify their successors.

4. Recalibration and acceptance

Remmy's implementation and re-freeze sequence:

Verify the R60REV source identity and section provenance.

Apply the T03 pack addition.

Add the three extraction rules.

Validate exact match cardinality, extracted values, types and evidence locations.

Regenerate the pin authority and complete the re-freeze record.

Re-run the complete offline calibration against the amended pinned snapshot and pilot data.

Preserve the previous PILOT-CALIBRATION-01 certificate and its finding.

Issue a new certificate with the new result and complete pin references.

T03 is eligible to join a Stage 6 battery only if the new certificate establishes ANSWERABLE. A partial repair or a result with any missing, ambiguous or type-invalid required extraction remains UNANSWERABLE.

No change to the original T03 question or process tree is proposed.

Boundary: This amendment draft authorizes no additional implementation beyond Ben's ruling. It does not authorize capability-trials pilot execution, live model calls, or any expansion of the T03 remediation scope.

The main point to preserve during implementation is that the three qualified dispositions and Correction B's separate OPEN status remain independently traceable to their respective source records. The old certificate stays intact; the new one must demonstrate that the complete T03 question is now answerable.
