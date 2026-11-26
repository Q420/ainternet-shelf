# BUILD SCOPE — The Dictation A/B: Prescription Repaired vs Phases and Outcomes (2026-11-26)

Filed by Remmy, 2026-11-26, on the director's order ("Let's try both
angles and see which one gives better results." — "Make it so",
2026-11-26 13:38–13:39 MST). Examination: Vane, before the build.
The trade flag stands as named to the director: this displaces the
filing batch and AIvory S4/S5 again.

## The symptom this answers

Two Stage 2 runs of the prescriptive contract (office-cycle-v11)
died at the same root:

- **demo-nemotron14** (2026-11-26): stalled at the 20-step ceiling.
  At the third file the worker's journal write rewrote instead of
  adding; the journal gate refused it; the standing gate correction
  directed a read the prescription forbids. Repaired the same day
  (the gate-recovery fix, INDEX 615) — but the run's deeper shape
  already showed the second flaw below.
- **demo-nemotron15** (2026-11-26): stalled at iteration 18,
  evidence_capture_failure. At the third file (sources/index-tail.md,
  40,953 bytes, four blocks) the worker's first read_range returned
  block 1 (11,528 chars). The prescription — as built — counted any
  standing read as the gather complete and moved the step to the
  journal write. Nine times the worker requested exactly the right
  next act (read_range lines 7–13, the file's second block, or the
  whole file); nine times the doorway refused. He would not journal
  a file he had not read. His final response was ~67,000 characters
  of reasoning, which crossed the response-evidence capture ceiling
  and stalled the run.

The worker asked for all the right things in both runs. The
dictation layer is what failed. The examiner's own clarification
(INDEX 612, clarification 5) said range reads fulfil a gather only
if the required content is retrieved; the build implemented the
loose reading (any part standing = the act spent). That
implementation error is Remmy's, and it is corrected in Angle A
below — it is not what the A/B is testing. The A/B tests the two
dictation philosophies, each in a form that does not carry a known
fatal flaw.

## Held constant

The standing job (the three sealed sources; the ~600-word
plain-words brief; the delivery floor of 550 words), the worker
(Gary — Nemotron on the NVIDIA route, native mode), the road seal
(140,000), the grant model (unchanged, shared read pool included),
the working-set carriage, the response-evidence discipline, and the
checker. One live run per angle, back to back, on the same day
where the provider allows.

## Angle A — prescription, repaired (office-cycle-v11, amended)

The v11 machinery exactly as built and witnessed (INDEX 615),
with ONE correction to the gather rule:

- A file's gather act is spent only when the file stands WHOLE in
  the record — every block of the sealed block map read. A
  whole-file read spends it in one act. While any block stands
  unread, the prescribed act is the read of the next unread block
  (the prescription names the block and its line range from the
  block map), and a read of the current file (whole or any of its
  ranges) is on-prescription; every other act is refused as before.
- Nothing else in v11 changes: one prescribed act per step, the
  doorway's pre-execution refusal, the bounded retry, the desk,
  the gate-recovery fix.

## Angle B — phases and outcomes (a new contract, office-cycle-v12)

The director's design, from the drawing-board session of
2026-11-26:

1. **The schedule is computed once, up front, and sealed with the
   generation.** The block map already portions every file; the
   schedule lays the job out as the counted sequence of steps —
   per file: its block-reads, then its journal step; then
   summarize; then deliver — with each step's expected carriage.
   The worker's packages present the schedule and his position in
   it (step N of M), from the same sealed computation the office
   checks against. (The standing job's schedule: 6 block-reads +
   3 journal steps + summarize + deliver.)
2. **Inside a gather phase, reads are free.** Any range, any
   order, re-reads, whole reads — no prescription refusals for
   reads of the current file. The phase's outcome is verified, not
   choreographed: a file's journal bit is accepted when the file
   stands whole in the record (every block read), exactly the
   fact Angle A enforces act by act.
3. **Append means append.** A journal write under this contract
   carries only the new bit; the office appends it to the journal
   of record. No cumulative re-emission, no rewrite trap, no
   journal gate for the common case. (The write's mechanism —
   executor-level append at the journal path, or record-level
   concatenation of the accepted chain — is a build-plan decision
   for after examination; the contract's requirement is the
   worker-facing one: he hands over the bit, the office adds it.)
4. **The worker's step budget counts his acts.** Refusals and
   gate corrections are office overhead and do not consume the
   run's step ceiling. (Mechanism — a ceiling counted on
   dispatch-bearing iterations, or a ceiling sized from the
   sealed schedule plus a named slack — likewise a build-plan
   decision; the requirement is the accounting, not the device.)
5. **Refusals remain only for what would corrupt the record:**
   filing before the gather stands complete (the delivery gates,
   unchanged), overwriting a source, acts outside the grants.
   Corrections answer with information, as the gate corrections
   already do.

What B does not change: the grants, the road, the delivery floor
and gates, the evidence discipline, the task, the sources. B is a
dictation contract, not a new harness.

## The measures — named before any run

For each angle's live run, from its record:

1. **Completes or not** (a brief filed at the delivery floor).
2. **Steps used against the computed schedule** (iterations, and
   dispatches, against the schedule's count for the standing job).
3. **Token consumption** against the road seal (counted tokens).
4. **Refusals and corrections issued** (count, by kind).
5. **The brief itself** — checker verdict, plus a plain read by
   the director and Remmy.

One run per angle shows the shape; it does not settle a close
call. If the measures are muddy or split, the answer is more runs,
not a verdict by squinting. The comparison record is filed
whatever it shows.

## Protocol

Paper (this scope) → the examiner's examination → build plan →
build both angles, each with rehearsal witnesses in the standing
suites (Angle A: the multi-block gather walk, range by range, on
prescription; Angle B: the free-read gather, the append act, the
schedule presented and checked) → verify-config → the two live
runs back to back → the comparison record (INDEX) → the examiner's
examination of the comparison. The director rules the standing
dictation from the comparison record.

## What stays wrong if both angles work perfectly

Either dictation still leaves: the response-evidence capture
ceiling as a run-ending ground when a worker spirals (run 15's
formal cause of death — a harness question, not a dictation one,
named here so it is not lost); the shared read pool across scopes
(the examiner's standing finding, unchanged); and text-mode
packages omitting doorway refusals (the known carriage
limitation). None of these is in this scope.
