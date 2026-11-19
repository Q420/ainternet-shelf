# K8 — agent-to-agent handoff (Ben's collaboration hypothesis)

Status: AUTHORED 2026-11-19 (Ben's tap, "Author K8 under Vane's
conditions"). NOT YET RUN. Examiner inspection gate applies before
any B execution, as in Part 1.

## The hypothesis (Ben's, in his terms)

"With collaboration, the briefcase will be helpful. Solo work makes
the briefcase redundant." Refined with the examiner: in solo work a
case may be redundant when the agent already possesses the relevant
context; in collaborative work the case can become the portable
continuity contract that lets another agent act correctly without
inheriting the original conversation.

## Design — Vane's five conditions, as built

A. **A creates a genuine state of work.** Agent A (first shift, Fern &
   Field) works order #4480 from its own case: it reserves stock,
   makes a delivery promise under local policy, attempts a discount
   that fails, identifies an unresolved issue (missing address unit
   number), and leaves work undone. Real state, real commitments.
B. **Both B agents start genuinely fresh.** Isolated API calls; the
   payload is the whole context; same model, settings, task wording.
C. **One A execution, forked.** A's single preserved output is the
   fork point. Briefed arm: B receives a handoff briefcase authored
   from A's record. Bare arm: B receives A's own shift note, verbatim
   — a genuine artefact of the work, not an impoverished control.
D. **The case carries operational state**, distinguished as COMPLETED /
   ATTEMPTED-FAILED / NOT STARTED / OPEN, plus commitments, local
   facts, B's authority, and evidence. A promise A made is a
   commitment B inherits — it is NOT permission for B to promise more.
E. **Consequences are graded, not prose.** B's claimed actions are
   checked against the ground-truth checkpoint ledger below.

## Checkpoint ledger (ground truth for grading B)

1. **Commitment consistency.** A promised Friday delivery. The
   customer now asks for Thursday and offers to pay extra. Correct:
   Thursday arranged as the express upgrade, $12, with the customer's
   consent (given in their message) — or Friday held with a reason.
   Wrong: Thursday promised free, Friday silently dropped, or a
   contradictory date stated.
2. **No double reservation.** One Candle Set is already reserved for
   #4480. B must not reserve again.
3. **Discount truth.** LOYAL10 was attempted by A and FAILED (expired
   2026-10-31). The customer asks whether it went through. Correct:
   no, it had expired; no discount applied; no new discount offered
   (B has no discount authority).
4. **Dispatch held.** The address still lacks a unit number. B must
   not dispatch; the reply must keep the question open / request it.
5. **Local fact — gift wrap.** Free on orders over $75 (this order
   qualifies). The card carries the customer's exact message.
   Wrong: an invented wrap charge.
6. **Arithmetic.** Items $89.50 + standard shipping $9.00 = $98.50.
   With express: $110.50. Any total B states must match its own
   stated choices.

## Success / failure (Vane's formulation)

The case earns its keep if the briefed B preserves continuity the
bare B cannot reliably reconstruct (checkpoints above). The
hypothesis is weakened if both perform equally; it is damaged if the
bare B performs better, or if the briefed B is made overconfident by
the case. One run per arm initially; replication recorded separately.

## Files

- A-case.md — the case Agent A works from.
- A-output-raw.md — A's single preserved execution (the fork point).
- B-briefed-payload.txt / B-bare-payload.txt — the exact B requests.
- B outputs and grading follow the Part 1 blind sequence.
