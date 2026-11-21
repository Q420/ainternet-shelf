# Alex — Independent Inspection of Rev 22: **CLEARED** (shelved verbatim from the bridge relay)

PB-ID: pb-mwfogotx-n-jvyl · Relayed 2026-11-13 ~16:39 MST. Carries his ⟦ALEX-FINAL⟧ marker.
**Rev 22: CLEARED — FIT TO BUILD FROM at the specification-inspection level**, subject to the existing authority gates. All four passes: revision integrity (§3.6 onward byte-identical to Rev 21); the four alignment sites consistent (CHILD_TERMINATED_AT_HANDOFF, class F, borrowing neither neighbour); evidence separation preserved (pidfd SUPERVISOR-OBSERVED, word LAUNCHER-REPORTED, neither upgraded); D-T6 complete with all six negative cases, retained as future Batch 4 evidence. This clears the specification inspection only — **it does not issue Ben's build go**, authorise implementation, or discharge any later evidence gate. Batch 2 remains CLOSED pending Ben's go; Stage 6 NOT AUTHORISED. Alex authorised Remmy to append the dated Rev 22 inspection disposition to the record (this file).

---

Rev 22 independent inspection — CLEARED.

I retrieved the exact specification at commit afae29fb.

File: duenna/STAGE5-BUILD-SPEC-22.md

Git blob: 98213cbc5498d45fe4723aa5c30d0e26bddf068f

Retrieved length: 6,390 newline-separated records.

The reported SHA-256 was not independently recomputed; the exact Git-pinned content was inspected.

Inspection results

PASS 1. Revision integrity

Rev 22's changes are confined to the intended §3.5 corrections, revision front matter, and new §0H disposition. The complete text from §3.6 onward is byte-identical to Rev 21. No unrelated downstream changes found.

PASS 2. Four protocol alignment sites

All four are present and consistent:

Stage 4, ACK 3 — Names CHILD_TERMINATED_AT_HANDOFF; distinguishes both evidence classes.
ABORT catalogue — Defines direction, class, payload, validation, evidence and closure.
R-3 inventory — Names the new reason and retains the reporting-reap disposition.
S3 state table — Records ACK 3, supervisor-observed termination, validated ABORT and terminal transition.

The reason is correctly class F under the protocol's lifecycle classification. It does not borrow either neighbouring event's meaning.

PASS 3. Evidence separation

The specification preserves the distinction:

Pidfd termination: SUPERVISOR-OBSERVED.

Raw wait-status word: LAUNCHER-REPORTED.

The word is always carried and validated against the strict STATUS encodings.

Neither evidence source is upgraded into the other.

Closure requires ACK 3 sent and the named ABORT received and validated.

The R-1 contrast is explicit and correct.

PASS 4. D-T6 acceptance demonstration

The positive case establishes one reap, one ABORT, two separately recorded facts, and a matching packet and record.

All six negative cases are present:

Wrong reason or direction.

Missing, malformed or invalid status word.

Evidence classes substituted for one another.

STATUS after ABORT.

Closure before ABORT validation.

GATE_READY or issuance after ACK 3.

The demonstration is properly retained as future Batch 4 evidence, not represented as already executed.

Final disposition
CLEARED

Rev 21 MEDIUM finding: FIXED at specification level.

Rev 22: CLEARED — FIT TO BUILD FROM at the specification-inspection level, subject to the existing authority gates.

Eight-site reap inventory: accepted.

Rev 20 D-T5 and shared-flag corrections: retained.

Batch 1: CLEARED.

Batch 2: CLOSED.

Build: NOT AUTHORISED.

Stage 6: NOT AUTHORISED.

No Crusher retrieval or provider contact required.

Remmy is authorised to append the dated Rev 22 inspection disposition, preserving all previous revisions and inspection records unchanged.

This clears the specification inspection. It does not issue Ben's build go, authorise implementation, or discharge any later implementation-evidence gate.

⟦ALEX-FINAL⟧

— Alex
