# Ben's rulings governing the Duenna fix — compiled by Remmy, 2026-11-19

Source: Ben's own words, ruled in session 2026-11-18 (closure rulings) and 2026-11-19 (briefcase session, where they bear on identity). These are the law any fix design must implement. Wording is Ben's substance as recorded in the session record; the five closure rulings were stress-tested with Vane in-window before adoption.

## The five closure rulings (Ben, 2026-11-18)
1. **Closure always completes.** If closure were refused it creates an unfixable loop. The system must allow closure but state what failed and why. The gate is the statement, not the block. (Vane's name for 1+2: "No silent closure. No trapped runs." Execution completion, record completion and adjudication are three distinct things; the system must distinguish what it knows from what it cannot establish, and never invent a root cause.)
2. **No silent closure.** The closure record must carry what failed and why.
3. **Attribution classes.** Every failure is SYSTEM (caused by us — harness/record layer/checkers), MODEL (caused by the subject model), or INPUT (caused by what was given to the agent). Unattributable = UNKNOWN, stated as unknown, never guessed.
4. **Attribution sync.** An attribution is one fact, identical in the closure statement, the ledger, and adjudication. Disagreement = an explicitly recorded discrepancy, both positions preserved, never a silent overwrite.
5. **Closure statements are immutable and hash-chained.** (Ben's word: "immutable".)

## Identity rulings from the briefcase session (Ben, 2026-11-19)
- The flow order for generated work: **Generate → Verify → Pack → Approve**. Verification precedes packing; the final gate is an approval, not a release.
- The orchestrator itself understands the relationships between the things it delegates over; that understanding is a precondition of delegation. Addressing/vocabulary layers supply references, not understanding.
- A pin (SHA-256) establishes identity, never truth. (Programme-standing; restated and agreed in the briefcase examination.)
- One fact, one home: a fact stated in two places as two copies will diverge; the second place must reference the first, not restate it. (Programme-standing; the attempt-3 subject-identity defect is its violation.)

## Standing constraints
- Duenna governs what an agent may do; the briefcase governs what an agent can know. The fix is Duenna-side.
- Design and plan only, until Ben authorises a build on the finished package.
- The subject-identity discrepancy inside Alex's attempt-3 adjudication (verification line vs body) stays untouched in that document; a discrepancy record is the remedy, per ruling 4.
