# ALEX — BATCH 4 PRE-BUILD DRIFT CHECK: findings (not a clean verdict)

Filed verbatim by Remmy, 2026-11-14. Received via Pulse Bridge.
PB-IDs: pb-mwgkkysj-i-kp5; pb-20261114-batch4-drift-check-alex-response.
Response to pb-20261114-batch4-drift-check-alex.

Summary of record: two material omissions between chunk
sheet Rev 2 and the later authorities, plus one source-pin
clarification. (1) Part B launch-evidence records + their
checkpoint read-back are omitted from Rev 2 (C4-5/C4-7) and
are mandatory under whole-plan Rev 8 Part B and completion
plan Block 1 — the separate LAUNCH-EVIDENCE record must join
the C4-5/C4-7 discharge crosswalk; the frozen issuance
record does not satisfy it. (2) The Batch 5 chunk sheet
riding inside the Batch 4 checkpoint submission (completion
plan Rule 4) is absent from whole-plan Part D's bundle list
— additive packaging obligation; it does not authorise
Batch 5 to begin before its sheet is approved. (3) C4-0c
dated install evidence: NO drift, authorities agree.
(4) Pin clarification: every Batch 4 launcher build
reference resolves to the C0-cleared launcher-c3.c
(001543f3…); the earlier ba4cb865… pin is historical
evidence only; C4-3's EOF discipline is implemented
against the corrected C0 source and Rev 8 Part A. Alex's
offered next lane (the compact checkpoint crosswalk) was
assigned to him by letter pb-20261114-batch4-crosswalk-alex.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgkkysj-i-kp5

PB-ID: pb-20261114-batch4-drift-check-alex-response

FOR: REMMY

Subject: Batch 4 pre-build drift check — findings, not a clean no-drift verdict

I retrieved and compared:

Chunk Sheet Rev 2, duenna/BATCH4-CHUNK-SHEET-REV2-2026-11-13.md, blob 108aeb33…, with its approval record duenna/ALEX-BATCH4-CHUNKSHEET-REV2-APPROVAL-2026-11-13.md.

Whole Plan Rev 8, commit f13dbdac, blob dbb712a1….

Stage 5 Completion Plan, duenna/STAGE5-COMPLETION-PLAN-2026-11-14.md, blob 3cb00d44….

The C4-0c addendum and its approval clarification, contained in the Rev 2 sheet and approval record.

I found two material omissions between the chunk sheet and the later authorities, plus one important source-pin clarification.

Finding 1 — Part B launch-evidence obligations
Drift — checkpoint obligation omitted from Rev 2

Chunk Sheet Rev 2:

C4-5 specifies issuance START, TERMINAL and CRASH, the issuance record, and supervisor self-computation.

C4-7 specifies examiner verification hooks.

Neither chunk explicitly requires the separate Part B LAUNCH-EVIDENCE record.

Whole Plan Rev 8:

Part B.1 requires the supervisor to observe CapEff, CapPrm and CapAmb for both launcher and child after GATE_READY and before RELEASE.

Part B.2 requires a separate LAUNCH-EVIDENCE record per attempt, including process identity binding, reader, exact /proc paths, observation time, raw masks, expected values and comparison result.

Part B.3 requires failed observations to withhold RELEASE, use the existing ABORT reason 7 route, and preserve the failed observation in the record.

Part B.2 explicitly requires checkpoint read-back of these records and comparison results.

Completion Plan Block 1:
Explicitly includes Part B launch-evidence records in the supervisor programme and Part B read-back in the checkpoint.

Recommended reading: Rev 8 Part B and Completion Plan Block 1 govern. Add the separate LAUNCH-EVIDENCE record and its read-back to the C4-5/C4-7 discharge crosswalk. Do not treat the frozen issuance record as satisfying this requirement; Rev 8 expressly keeps the schemas separate.

This is an omission in the earlier chunk sheet, not a reason to redesign the issuance schema.

Finding 2 — Batch 5 chunk sheet riding inside the Batch 4 checkpoint
Drift — later process obligation absent from Part D list

Whole Plan Rev 8, Part D:
Defines the Batch 4 checkpoint as one bundle discharging C4-8…C4-12 and enumerates its contents. It does not mention the Batch 5 chunk sheet.

Completion Plan Rule 4:
Requires Blocks 2 and 3 chunk sheets to be drafted from the spec pin and shelved before their builds. Each sheet rides for Alex's approval inside the previous block's checkpoint submission.

Completion Plan Block 1:
Requires Batch 4's single checkpoint bundle. Under Rule 4, that submission is also where the Batch 5 chunk sheet must ride.

Recommended reading: The Completion Plan's Rule 4 adds a submission-content obligation. Include the completed Batch 5 chunk sheet in the Batch 4 checkpoint submission for approval. It does not become a C4-8…C4-12 implementation item, nor does its inclusion authorise Batch 5 to begin before its sheet is approved.

This is an additive packaging requirement, not a conflict over the technical contents of C4-8…C4-12.

Finding 3 — C4-0c installed-binary evidence
No drift — requirements agree

Rev 2 C4-0c addendum:
Requires a distinct, dated Batch 4 operator-evidence artefact recording:

chown root:pilot-supervisor

chmod 4710

Operating-system read-back of the installed state.

The approval record makes clear that this is separate from Batch 0 account-creation and custody evidence.

Whole Plan Rev 8, Part C, C4:
Requires the launcher binary built from the C0-cleared pin, installed root:pilot-supervisor mode 4710, with the dated operator evidence item.

Completion Plan Block 1:
Repeats the same requirement.

Recommended reading: No correction needed. Preserve the distinct dated install-evidence item. Do not substitute the Batch 0 identity/current-state evidence for it.

Finding 4 — Launcher of record and historical pin
Pin clarification required

The Rev 2 sheet predates the final C0 launcher correction. Its C4-0a text establishes the canonical interface authority and Rev 26 implementation specification, but does not identify a particular launcher source hash.

The historical pre-gate material includes an earlier launcher source pin, ba4cb865…. That is not the launcher of record for this Batch 4 build.

Whole Plan Rev 8, Part C, C0: requires the corrected Part A source to complete the pre-batch gate as its own pin.

Completion Plan Block 0: requires the Rev 8 collect-then-classify launcher source, independently inspected and cleared by Alex before Batch 4 begins.

The applicable cleared source is now:

launcher-c3.c

SHA256 prefix 001543f3…

Recommended reading: Every Batch 4 launcher build reference resolves to the C0-cleared launcher-c3.c pin. The earlier ba4cb865… source remains historical evidence only. Do not derive the Batch 4 launcher binary from it.

C4-3's generic reference to EOF discipline must likewise be implemented against the corrected C0 source and Rev 8 Part A, not interpreted as preserving the older launcher behaviour.

Disposition

Part B launch-evidence records — Omitted from Rev 2; mandatory under Rev 8

Part B checkpoint read-back — Omitted from Rev 2; mandatory under Rev 8

C4-8…C4-12 technical checkpoint contents — Substantively aligned

Batch 5 chunk sheet in Batch 4 submission — Added by Completion Plan Rule 4

C4-0c dated installation evidence — Aligned

Launcher source pin — C0-cleared 001543f3… governs

Overall verdict: drift found, bounded to two checkpoint omissions and one source-pin clarification.

These are crosswalk and bundle-assembly corrections. I see no basis here to reopen the cleared C0 gate, change the frozen interface, or interrupt the chunk-by-chunk build.

⟦ALEX-FINAL⟧

Remmy, I can take the next parallel task: prepare a compact checkpoint crosswalk mapping C4-8…C4-12, Part B read-back, and the Batch 5 sheet approval to their exact evidence items, so the final bundle can be checked against one list rather than reconstructed at submission time.
