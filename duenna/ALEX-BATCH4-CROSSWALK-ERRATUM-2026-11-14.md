# ERRATUM — ALEX BATCH 4 CHECKPOINT CROSSWALK, ROW C4-10 (2026-11-14)

Filed by Remmy at Alex's direction (PB-ID
pb-mwgz9mjj-2-dp2t, alex-remmy-b4-b5-and-programme-
decision-2026-11-14). The original crosswalk
(ALEX-BATCH4-CROSSWALK-2026-11-14.md, shelved at
1ebbc01d) is preserved unchanged as history; this
erratum corrects one row of it. Alex's words on the
correction: "My earlier crosswalk wording was wrong…
The crosswalk's extra requirement would contradict
the specified issuance behaviour. I withdraw it."

## Original row text (superseded)

"C4-10 — Supervisor self-computation: Scratch-run
record containing the falsified pin block, inputs,
supervisor-computed result and observed outcome. —
The supervisor independently computes against the
falsified pin block and detects/rejects the
discrepancy. Do not substitute a launcher-side check
or a report of expected behaviour. — Chunk Sheet
Rev 2 C4-10; Whole Plan Rev 8 Part D; Completion
Plan Block 1."

## Corrected row text (Alex, exact replacement)

C4-10 — Supervisor self-computation: Scratch-run record containing the falsified pin block, inputs, supervisor-computed result and observed outcome. — The supervisor independently parses the RUN_STARTED event and recomputes the genesis hash and pin-block hash from the file's own bytes, then commits a START receipt over those actual bytes. The receipt must reflect the supervisor's own computation, not harness-supplied values. The falsified-versus-genuine pin discrepancy is a replay finding. The supervisor is not expected to compare against a true pin or reject the falsified block at issuance. — Chunk Sheet Rev 2 C4-10; Whole Plan Rev 8 Part D; Completion Plan Block 1; governing spec §3.5 point 5 and SE-7(ii).

## Effect

With this correction, the sole material hold in
Alex's Batch 4 checkpoint adjudication of
2026-11-14 is resolved: **BATCH 4 CHECKPOINT:
CLEARED.** No patch, no rerun, no reopening of C0
or completed chunks. The previously disclosed
evidence limitations remain accurately disclosed;
the clearance does not turn C0-referenced evidence
into production reruns or make the superseded
B4FDS-002 record valid.
