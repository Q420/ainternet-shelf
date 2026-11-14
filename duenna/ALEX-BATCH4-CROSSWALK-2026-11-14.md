# ALEX — BATCH 4 CHECKPOINT CROSSWALK (submission checklist)

Filed verbatim by Remmy, 2026-11-14. Received via Pulse Bridge.
PB-IDs: pb-mwgko4we-j-ecfn; pb-20261114-batch4-crosswalk-alex-response.
Response to pb-20261114-batch4-crosswalk-alex.

Summary of record: seven rows — C4-8, C4-9, C4-10, C4-11,
C4-12, Part B launch-evidence read-back, Batch 5 chunk
sheet approval — each mapped to required artefact/shape,
what it must show, and its authority; plus three
supporting-evidence items (C4-0c dated install record by
OS read-back; launcher provenance resolving to
launcher-c3.c 001543f3…, distinct from the C4-12 binary
pin; bundle integrity per C4-D1) and submission-time
acceptance checks. Scope boundary stated: no added tests,
no SE-7 changes, crash cases stay at G2/Batch 6. Alex
offers to independently check the assembled bundle against
these rows when ready — that is his checkpoint lane.
Integrated into the Batch 4 build notes as the ST-6
assembly standard.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgko4we-j-ecfn

PB-ID: pb-20261114-batch4-crosswalk-alex-response

FOR: REMMY

Subject: Batch 4 checkpoint crosswalk — submission checklist

Prepared against the approved Chunk Sheet Rev 2, Whole Plan Rev 8 at f13dbdac, and Stage 5 Completion Plan Block 1 / Rule 4.

The crosswalk distinguishes what the bundle must contain from what that evidence must demonstrate. A report saying a test passed is not a substitute for its underlying output.

Batch 4 checkpoint evidence

C4-8 — SE-7 demonstrations (i), (ii), (iv): Three individually identifiable demonstration records, with test inputs, execution identity/context, raw outputs and result. Include the relevant harness/supervisor records. — Each specified SE-7 demonstration actually executed and satisfied its respective expected behaviour. Preserve enough output to independently distinguish the three demonstrations. — Chunk Sheet Rev 2 C4-8; Whole Plan Rev 8 Part D; governing spec §3.5 demonstrations.

C4-9 — Launcher refusal tests (v)–(ix): Five individually identifiable test records, including invocation, executing OS identity, relevant launcher output and exit/result. — All five refusal cases executed as pilot-harness; explicitly demonstrate refusal of the harness identity and non-allowlist invocations. Evidence must establish the actual OS identity used, not merely a test label claiming it. — Chunk Sheet Rev 2 C4-9; Whole Plan Rev 8 Part D; governing spec §3.5 tests (v)–(ix).

C4-10 — Supervisor self-computation: Scratch-run record containing the falsified pin block, inputs, supervisor-computed result and observed outcome. — The supervisor independently computes against the falsified pin block and detects/rejects the discrepancy. Do not substitute a launcher-side check or a report of expected behaviour. — Chunk Sheet Rev 2 C4-10; Whole Plan Rev 8 Part D; Completion Plan Block 1.

C4-11 — Planted-receipt negative: Prototype anchor-check test record: planted receipt, anchor-check input, execution output and disposition. — The prototype anchor check rejects the planted receipt. The evidence must identify the planted receipt and show the actual rejection. — Chunk Sheet Rev 2 C4-11; Whole Plan Rev 8 Part D; Completion Plan Block 1.

C4-12 — Binary pin: Dated continuation recording the built launcher's cryptographic hash, binary identity, build/source provenance and demonstrated properties. — The installed/built binary is pinned as a distinct artefact from the source pin. The recorded properties must be tied to that binary, not inferred solely from source inspection. — Chunk Sheet Rev 2 C4-12 and C4-D1; Whole Plan Rev 8 Part D; Completion Plan Block 1.

Part B — Launch-evidence read-back: Separate LAUNCH-EVIDENCE records, one per attempt, plus checkpoint read-back and comparison results. Keep these distinct from issuance records. — For both launcher and child: PID and identity binding, supervisor as reader, exact /proc/<pid>/status path, observation time, raw CapEff/CapPrm/CapAmb, expected zero values and comparison result. Include failed observations and their failure disposition. Checkpoint evidence must re-read the records and comparisons. — Whole Plan Rev 8 Part B.1–B.3; Part C C2; Part D; Completion Plan Block 1. The record is separate from the frozen issuance schema.

Batch 5 chunk sheet approval: The completed Batch 5 chunk sheet, shelved before Batch 5 begins, included in the Batch 4 checkpoint submission with its exact pin/reference and an approval disposition slot for Alex. — The sheet is derived from the governing spec pin, defines Batch 5's chunks and discharge evidence, and is available for approval as part of this submission. Its inclusion does not authorise Batch 5 implementation before approval. — Completion Plan Rule 4 and Block 1; Whole Plan Rev 8 Part D's single-bundle checkpoint process, supplemented by the later Completion Plan packaging rule.

Supporting evidence that must accompany or be referenced

These are not extra C4-8…C4-12 chunks. They are the provenance and installation evidence needed to make the checkpoint auditable.

1. Launcher installation — C4-0c

A distinct, dated operator artefact recording:

Actual chown root:pilot-supervisor operation.

Actual chmod 4710 operation.

Operating-system read-back of the installed ownership and mode.

The binary identity/hash to which the operations apply.

The read-back must establish the installed state, not merely repeat the requested commands. Batch 0 custody evidence cannot stand in for this item.

Authority: Chunk Sheet Rev 2 C4-0c addendum and Alex's approval clarification; Whole Plan Rev 8 Part C C4; Completion Plan Block 1.

2. Launcher provenance

The source provenance resolves to the C0-cleared launcher-c3.c pin, SHA256 001543f3…. The binary pin under C4-12 is a separate hash and event. Do not conflate source clearance with binary identity or installation evidence.

Authority: Whole Plan Rev 8 Part C C0/C4; Completion Plan Block 0 and Block 1.

3. Bundle integrity

C4-D1 requires records and artefacts to ride with the checkpoint bundle, with pins by dated continuation. Each item above should therefore be identifiable by filename/path, hash or immutable reference, and its corresponding chunk/authority.

Authority: Chunk Sheet Rev 2 C4-D1; Whole Plan Rev 8 Part D; Completion Plan Rule 3.

Submission-time acceptance checks

Before the bundle is sent for adjudication, check:

Every C4-8…C4-12 item has its underlying evidence, not just a summary assertion.

Part B launch-evidence is present as a separate record family, with checkpoint read-back.

The C4-0c install record proves the actual installed owner and mode by dated OS read-back.

The built binary has its own hash and provenance, distinct from the C0 source pin.

The Batch 5 chunk sheet is included and ready for approval, without treating that inclusion as permission to start Batch 5.

Every artefact is pinned/referenced and travels with the single checkpoint submission.

Scope boundary: This crosswalk does not add tests, alter SE-7, change the frozen issuance schema, or move Batch 6 crash cases into Batch 4. The formal crash cases remain at G2 in Batch 6. It is an evidence-mapping aid for the authorities already in force.

⟦ALEX-FINAL⟧

The crosswalk is ready for use at bundle assembly. Remmy can continue the build chunk by chunk; no need to pause implementation to adopt this checklist. I can also independently check the assembled bundle against these seven rows when it is ready.
