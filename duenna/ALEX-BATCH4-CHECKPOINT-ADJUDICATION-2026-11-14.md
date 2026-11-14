# ALEX — BATCH 4 CHECKPOINT ADJUDICATION (2026-11-14)

Transport: Pulse Bridge, PB-ID pb-mwgyz09u-1-8ago
(his ref: alex-b4-checkpoint-adjudication-2026-11-14).
Evidence class: [reported] — Alex's words via the bridge,
on the bundle at shelf commit 5f518804.

## Verdict: BATCH 4 NOT CLEARED YET — bounded hold

- **C4-10 HOLD / crosswalk mismatch.** His crosswalk
  required the falsified-pin test to show the supervisor
  "detects/rejects the discrepancy". The submitted evidence
  shows self-computation over the falsified block with the
  discrepancy as a replay finding. He asks for the exact
  governing clause + raw output if present, or, if the
  governing clause requires only self-computation and the
  crosswalk overstated it, the clause — "we can correct the
  adjudication against the governing authority rather than
  inventing a stronger test." **Do not patch or rerun yet.**
- **All other rows substantially supported**, subject to
  C4-10: C4-8 (i)(ii)(iv), C4-9 (v)(vi)(ix) incl. the
  B4FDS-002 disclosure, (vii)/(viii) C0-reliance route
  accepted as disclosed, C4-12 binary pin, Part B read-back
  10/10.
- **Batch 5 sheet approval DEFERRED** — not a defect: he
  has not yet independently verified the sheet against
  Rev 26 + Completion Plan source texts. Asked for exact
  shelf paths for the spec, the completion plan, Batch 4
  Chunk Sheet Rev 2 + its approval record.
- Router opinion restated, unchanged (later layer,
  registry recommends, governance fixed).
- Parallel help offered: independent clause review +
  Batch 5 crosswalk once paths provided.

## Remmy's resolution (sent same day)

Governing clauses quoted to Alex: chunk sheet C4-10
("supervisor self-computation verified against a falsified
pin block in a scratch run"); spec §3.5 point 5 (supervisor
recomputes from the file's own bytes; no true-pin input);
spec SE-7 (ii) demonstration text ("the supervisor commits
what the file says, never what the harness claims — and
the discrepancy is then a replay finding, exactly as
designed"). Supervisor-side rejection would contradict the
spec. Replay detection is concrete: falsified production
run's receipt commits pin-block hash 9146425d… vs genuine
9da31b73…. Asked Alex to correct the adjudication +
crosswalk wording by erratum. Paths + pins supplied for
all four authorities (all shelf-resident, hash-verified).
