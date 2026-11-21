# Remmy — Challenge to Vane's Stage 4 Examiner Validation Pack v1 (2026-11-21)

Examined artifact: `duenna/fix-2026-11-19/VANE-STAGE4-EXAMINER-VALIDATION-PACK-V1-2026-11-21.md`, shelf commit 6978e91fe2ebaec1115e4e62a7f5f6b8445acbaa, blob 93a573b0118025e76ae69b59f0fae22cac61b4e4 — **verified by read-back; the blob matches**. Authorities checked against: Rev 9 (blob 6a7e3d54…), Amendment A1 (blob 8af1afb6…), Stage 4 Brief Rev 2 (shelf head 6aee9455) — the pack's citations of all three are accurate.

**Disposition: a strong pack — NOT YET PINNABLE.** One blocker (C1), seven must-pin items (C2–C8), and five confirm-or-note items (N1–N5). Everything not listed is accepted as written — in particular VP-25 (omitted-batch refusal), VP-28 (transitive import audit), the VP-39–VP-44 identity suite, VP-45's nine-step TV-1 sequence, and §10's no-informal-waiver rule. Per Ben's standing mode ruling, each finding carries a proposed resolution as joint text where I have one.

## C1 — BLOCKER: the precedence between MISMATCH and FAIL(check) is undefined

VP-26 says a live snapshot that differs from replay state yields `MISMATCH` and no seal. VP-16 and VP-45 say a live snapshot carrying a dangling dependency yields `FAIL(S1, …)` and raises a structural tension. But TV-1's fault (VP-45) *is* a divergence between L and R — the same input shape VP-26 describes ("differs in one region record, version, or dependency record"). As written, the two outcomes are both defensible on the VP-45 input, the two implementations may legitimately choose differently, and VP-29 then blocks the run with no contract to settle it. Worse: if MISMATCH swallowed check failures, no structural tension could ever be raised from a live-state fault, and the genuine TV-13 lifecycle would be unreachable.

**Proposed pinning (the full 2×2):** the structural checks run against L. (i) L = R and all checks pass → PASS. (ii) L = R and a check fails → FAIL(check, affected), tension lifecycle engaged (VP-27's second branch). (iii) L ≠ R and a check fails on L → FAIL governs; the tension lifecycle engages; the divergence is recorded in the attempt's diagnostics. (iv) L ≠ R and no check fails on L → MISMATCH, no seal (VP-26's case, narrowed to divergence not explained by a check failure). Under this table VP-45 step (3) is FAIL(S1) as the pack expects, and VP-26 keeps a real, distinct case.

## C2 — MUST-PIN: VP-27's expectation is disjunctive

VP-27 permits either a replay halt or an S1 failure on the same input ("if the fault violates event protocol/schema… If the history is valid but…"). VP-29 requires both implementations to agree on branch, not only on no-seal. **Proposed rewrite:** state the input as a protocol-valid, hash-valid history whose recorded events assert a dangling dependency (commit-time validation bypassed in the canned history — replay does not re-run commit validation), L = R, expected `FAIL(S1, …)`. The halt branch is already covered by VP-06/VP-11-class cases.

## C3 — MUST-PIN: one reason taxonomy for replay halts

The halt reasons across VP-04–VP-15 are named inconsistently: VP-07/08/09 use the disjunction `schema_invalid_or_protocol_invalid` (the pack's own note — each implementation names its stable reason in its mapping table — would let the two implementations disagree while both "pass", against VP-29's "halt position/reason class must agree"); VP-10 assigns an unknown tension *type* to `protocol_transition_invalid` while VP-07's malformed type is left disjunctive; VP-13 and VP-14 name no reason at all; VP-15B says "rejects or halts". **Proposed table, for Vane to settle:** a field value that violates its Annex B type/enum (wrong type, unhashable value, unknown enum member, IDLE under a pre-A1 authority set) → `schema_invalid` (VP-06, 07, 08, 09, 10, 14-status, 15B-as-HALT); individually valid values in a forbidden combination or transition (origin/type mismatch, illegal transitions, terminal escapes) → `protocol_transition_invalid` (VP-11, 12, 13); chain and sequence keep `hash_chain_invalid` / `sequence_invalid` (VP-04, 05). VP-14's two halves split: status outside the enumeration → `schema_invalid`; facet target outside the six regions → `protocol_transition_invalid`.

## C4 — MUST-PIN: "may" is not an expected outcome

VP-01 ("a close-time attempt may pass"), VP-24 ("the attempt may pass"), VP-34, VP-46 and VP-49 ("seal may issue") use permissive wording where the inputs fully determine the outcome. Rev 9 §7 is deterministic: every check succeeds → a seal **is** issued. Under VP-29, "may" makes agreement untestable for those cases. **Proposed:** replace with the definite outcome wherever the case's conditions are complete (PASS / seal issues), reserving permissive language for genuinely conditional steps.

## C5 — MUST-PIN: VP-36 does not name the failure outcome

VP-36 requires no partial commit and explicit, durable failure handling "under the existing run-failure contract", but does not say whether a checker-process failure (a) refuses the submission (the group rolls back; the run continues) or (b) fails the run under the Stage 2 RUN_FAILED latch. The two implementations must choose the same. **Proposed:** (b) — machinery failure is the established fail-closed case (Stage 2 corrections, accepted); a refusal outcome is reserved for contract-level rejections of the submission itself. If you intend (a) for some failure classes and (b) for others, the split must be named.

## C6 — MUST-PIN: VP-51 leaves the consecutive-rejection rule to build notes

Whether IDLE (or other non-rejection outcomes) breaks a consecutive-rejection run is behavioural, not presentational; left to build notes, the two implementations of the *report* — and VP-54's byte-identical requirement — can diverge. **Proposed rule, for the pack to pin:** the counter counts successive rejection outcomes for the agent; it resets on that agent's next accepted commit, and on nothing else (IDLE neither increments nor resets — it is not a rejection and not progress).

## C7 — MUST-PIN: VP-52's censored convention must be identical, not merely explicit

VP-52 requires "an explicit not-yet-observed/null-or-censored convention" but does not choose one; VP-54 requires byte-identical reports. **Proposed:** JSON `null` for wakes-to-first-success / time-to-first-success when no successful commit exists, with the field always present. (VP-53 likewise: pin the counting unit as **regions**, matching the settled changed-read diff definition, rather than "unless the contract chooses otherwise".)

## C8 — MUST-PIN: VP-20's affected set — edges or regions?

S3's affected set is "{all records participating in the detected cycle}". A cycle is formed by dependency edges through regions; the set's membership (the dependency records, the region records, or both) decides identity under B6 deduplication and must be one pinned choice. **Proposed:** the dependency records forming the cycle (the edges are the records the check examines; regions enter via the edges' endpoints). Same question, smaller, for VP-18: "reports a mismatch or S2 failure" is disjunctive — under the C1 table, a version regression in L against history is L ≠ R with no live-state check able to fail on versions alone, i.e. MISMATCH, while a candidate batch that would lower a version is a commit-protocol rejection before any attempt; propose the pack say exactly that.

## Confirm-or-note

- **N1 — VP-16/VP-39's affected set {dependency, missing endpoint}** refines Rev 9 TV-1's wording ("naming the S1 check and the affected dependency"). I accept the pair as the pack's pinned definition — it is applied consistently (VP-16, 39, 41, 42) and §7's "affected records" admits it — but flag it as a deliberate refinement of the Annex E wording, to be recorded as such, not read as TV-1 verbatim.
- **N2 — VP-03 (IDLE actor mismatch)** should state explicitly that the refusal is transport-level with **no event of any kind appended**: no rejection event type exists for IDLE, and inventing one in one implementation would break VP-29.
- **N3 — VP-37's close attempt** has no staged batch; the input model should state that at close the checker receives H and L with B empty (the attempt is generated by the close itself), so the interface contract covers it.
- **N4 — VP-35's initial boundary** ("since genesis/previous seal") must be pinned in the mapping table **before** validation begins, not only in build notes after; §10.3's per-case manifest can carry it.
- **N5 — No case asserts the run record names the exact pack and hash** (Rev 2 §5 / B4). VP-29 implies it; a one-line case (or a §10 manifest requirement with teeth) would close it.

## What this challenge does not do

It does not validate either implementation, authorise a build, or amend Rev 9, A1, or Brief Rev 2. If Vane accepts the proposed pinnings (or settles them differently), the pack is revised and re-hashed by its author, and the revised pack returns for a confirmation pass before pinning.
