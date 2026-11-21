# Vane — Stage 4 Design Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:31 MST (PB-ID pb-mwqe0jgs-16-5nbb). Examined artifact: Stage 4 design brief (shelf head b13c2fed) against Rev 9. Verdict: **Stage 4 design NOT YET SETTLED** — B1–B3 and B6 are required design clarifications; the Amendment A1 authority must be made available; Q4/Q5/Q6 accepted with precisions; on Q3 she chooses the stronger authorship boundary (she authors the checker-validation pack). Transcribed from the bridge delivery as received.

---

Received. I'll treat this as a design-settlement round, not a build review. The scope is appropriately bounded: Stage 4 must close the real structural lifecycle and independently verify the mechanical slice, not merely produce a successful-looking seal.

My initial position is that your proposed direction is sound, but several boundaries need to be made exact before I settle the brief. In particular, the seal event ordering, what "same atomic group" means when the seal itself is appended, the checker's independence, and the evidentiary status of the external close anchor all need unambiguous contracts.

The exact Rev9 text reveals one substantive omission and two important interfaces that need tightening. I would not settle the brief unchanged.

## Stage 4 design examination

**B1. The structural check set is incomplete.**

The brief names S1 dependency integrity and S2 version consistency, but Rev9 §4 defines four structural invariants:

- S1 dependency integrity
- S2 version monotonicity
- S3 pattern acyclicity
- S4 declared scope

S4 is enforced at schema and targeting validation, but S3 is a distinct structural invariant and must be included in the seal checks. The Stage 4 brief must explicitly include S3. Otherwise, the seal can pass while a pattern cycle exists.

Also specify which checks apply to the live derived state and which apply to the event history. Schema conformance and hash-chain continuity are not substitutes for S1–S3.

**B2. The checker needs a defined view of live state.**

Q1's proposed independence boundary is acceptable, with one important addition.

The checker may share canonical JSON and hash primitives because these define the record format. It must independently implement:

- event folding and state derivation;
- S1, S2 and S3 checks;
- seal eligibility and outcome;
- structural-tension identity, deduplication and resolution.

It must not import engine or harness logic.

However, the brief says the checker reads the event history directly, while TV-1 deliberately corrupts the live derived state only. Replaying the valid event history alone cannot reveal that injected corruption. The checker therefore needs two distinct inputs:

- The event history, read-only, from which it independently derives the expected state.
- A read-only snapshot of the actual live derived state at the attempt boundary.

It must perform the structural checks against the live snapshot and independently compare that snapshot with its replay-derived state. The snapshot is input evidence, not authority. This is essential to making TV-1 genuine rather than simulated.

**B3. Q2: accept atomic grouping, but define the transaction boundary.**

I accept one atomic group per accepted contribution, with this deterministic order:

- Accepted contribution events.
- Contribution-triggered tension and facet transitions.
- SEAL_ATTEMPTED.
- Any structural TENSION_RAISED or TENSION_STATUS events caused by that attempt.

The entire group must commit or roll back together. No observer may see a partially committed group.

The checker must evaluate the staged post-contribution state and event batch before the group is committed. It cannot simply read the old committed history from another process and somehow see uncommitted events. Give it the candidate event batch and live-state snapshot as explicit inputs, alongside its read-only access to the committed history.

A passing seal is anchored to the SEAL_ATTEMPTED event position. The structural status event that resolves an existing tension may follow it in the same atomic group. State explicitly that the seal covers the structural state at its recorded position, not later events.

**B4. Q3: I choose the stronger authorship boundary, with a distinction.**

I should author the independent checker-validation pack from the specification text, not from either implementation. Remmy should examine and challenge it. The existing Annex E remains the contract's stated vector set; the new pack must be visibly identified as examiner-authored, versioned, and hash-pinned. Do not describe Remmy-authored material as independently examiner-authored merely because I examine it.

Both implementations must be tested against the same pinned material before RUN_OPENED. A disagreement means no run opens. The record must identify the exact pack and hash, not just say "Annex E".

**B5. Q4: accept.**

TV-1's injection belongs in the live derived state only. The event history must remain valid and unchanged. The test driver must identify the injection as fixture activity, and the evidence must show:

- valid replay before and after injection;
- the exact live-state mutation;
- the checker detecting the resulting S1 inconsistency;
- the failed attempt and raised structural tension;
- a genuine correcting contribution;
- an unconditional subsequent attempt;
- the passing result and resolution evidence.

One further detail: the ordinary contribution that triggers the first attempt must be independent of the missing region, so the test does not accidentally make the contribution itself invalid.

**B6. Structural identity and resolution need one more precision.**

I accept identity as (check name, affected record set), with the set canonically ordered for comparison.

But resolution must re-run the same check against the original tension's affected record set. It must not merely observe that the latest attempt produced a different failure set, or that some other check passed. The passing attempt must establish that the particular inconsistency represented by that tension no longer exists.

Repeated failures with the same identity must attach their findings to the existing open tension. A different affected set is a different identity. The tests should exercise both cases.

**B7. Q5: accept the shelf anchor, but name it honestly.**

The shelved record and its Git commit SHA provide a content-addressed archival anchor outside the event database. That is useful and appropriate for this prototype.

Do not describe it as an independently trusted external anchor unless the commit SHA is itself preserved outside the repository's control. Record the closed chain head, the RUN_CLOSED state hash, the shelf commit SHA, and the relationship between them. The evidence should say precisely what the shelf establishes and what it does not.

**B8. Q6: accept the derived-report approach, with tests.**

Starvation reporting should remain a deterministic read over the event history, not new authoritative state. I want it implemented as a named derived report with tests, rather than as ad hoc calculations in the closing exercise.

The report must define its measures unambiguously, including consecutive rejections, wakes between successful commits, changed-read diff sizes, and progression. It must report every agent, including agents with no successful commits. No progress must not disappear through an undefined or omitted metric.

## Carried hardening item

The Stage 3 malformed-payload issue remains a named Stage 4 obligation. Hash-valid events containing unhashable type, from, or to values must produce a controlled ReplayHalt at the offending sequence, never a native TypeError. Include negative replay cases and verify that the chain itself is valid, so the test proves protocol validation rather than hash rejection.

## Two things to reconcile before settlement

The brief cites Amendment A1, but I could not locate that amendment alongside the exact Rev9 artifact. Please give me its precise path and hash, or include its text in the revised brief. I will not assume what it changes.

The closing exercise must distinguish the full mechanical evidence package from a successful run. A run may legitimately end with unresolved semantic work or a failed structural condition. The exercise must preserve and report those outcomes honestly; it must not manufacture a pass by selecting a favourable lifecycle.

## Verdict — Stage 4 design not yet settled

The six proposed questions are substantially answerable as above. B1 through B3 and B6 are required design clarifications, not optional implementation details. The Amendment A1 authority also needs to be made available.

Once those are incorporated, I can settle the design and authorize the Stage 4 build under Ben's existing commission. Until then: no Stage 4 build, no live agents, and no implied acceptance of the full commissioned slice.

The target remains the same: the machinery must demonstrate that it can preserve the constitution under a real fault, not merely produce a seal-shaped record.
