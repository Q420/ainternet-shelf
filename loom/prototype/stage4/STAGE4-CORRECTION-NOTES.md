# Stage 4 — Correction Round Notes

Correction round built 2026-11-21 against Vane's Stage 4
examination (`VANE-STAGE4-EXAMINATION-2026-11-21.md`: NOT
ACCEPTED, blockers B1–B4) and her settled rulings on S2 and
binding (`VANE-STAGE4-S2-BINDING-RULINGS-2026-11-21.md`).
Dispatch brief of record:
`STAGE4-CORRECTION-DISPATCH-2026-11-21.md`.

**The examined round is preserved.** The Stage 4 build at shelf
head a99a7676 is not amended; everything here is a new round in
the working tree, shelved separately. `STAGE4-BUILD-NOTES.md`
(the round-1 notes) is NOT rewritten — it stands as the examined
record, including the interpretations this round supersedes or
corrects. Corrections live only in this file.

**This file's revised pack mapping table (section 6) was
recorded BEFORE the reworked pack harness was executed**, as
the dispatch brief requires. Results are appended in section 7
after execution; nothing in sections 1–6 was rewritten
afterwards.

---

## 1. The four corrections

### C-B1 — S2 evaluated against L, per the settled definition (B1)

Vane's ruling settles S2's operational definition: for each
region r, R_r is the version established by verified replay of
the accepted history (H + B) at the seal position, and L_r is
the version in the live snapshot. **S2 fails iff L_r < R_r**,
affected = {r}. Lower-bound only: L_r > R_r is divergence
(MISMATCH unless another check fails on L); any check failing
on L makes FAIL govern, with divergence kept as diagnostics.

Implemented independently in both evaluators:

- `fabric/seal.py`: `s2_findings(committed_state, replay_state)`
  (the I-3 staged-transition property) replaced by
  `s2_findings(replay_state, live_state)` implementing the
  ruling; the call site now passes the replay of H + B and the
  live snapshot. A region present in replay but absent from the
  snapshot yields no S2 finding (its absence is S1's to name
  when a dependency dangles, and divergence otherwise — VP-43's
  pinned expectation depends on exactly this).
- `fabric/checker.py`: `_s2_findings(before, replay)` replaced
  by `_s2_findings(replay, live)`, the same definition in the
  checker's own words and code; it imports nothing new.
- The S2 branch of the resolution re-run
  (`inconsistency_absent` / `_inconsistency_absent`) is no
  longer defensive: an S2 tension resolves iff the live version
  of its region is no longer below the version replay
  establishes at the resolving attempt. Both implementations
  take the replay state for this re-run. An S2 tension is now
  reachable (a live regression raises one), and the new suite
  exercises its attach/resolve lifecycle in both evaluators.

Interpretation I-3 (round-1 notes) is **superseded by the
ruling**; its history stands in the round-1 notes, unrewritten.

### C-B2 — Whole-state admission restored, on the authoritative fold (B2)

The admission-attribution deviation is **rejected** (Vane's
ruling); this correction restores the accepted Stage 2
semantics by the route her examination proposed.

- `fabric/harness.py::_structural_violation` is restored to
  the whole-state form of the accepted Stage 2 artifact
  (dbdf1769): the S1 premise scan, the hypothetical application,
  the S1 scan over ALL active dependencies in the hypothetical
  state, the S2 monotonicity guard, and the S3 scan over the
  whole pattern graph — no introduced-only narrowing anywhere.
- The state it (and the rest of admission) validates against
  is the **authoritative, history-derived fold**, via the new
  `Harness._authoritative_state()` (a verified fold of the
  committed history, memoised on the head hash). Three
  admission reads moved to the authoritative fold:
  `_structural_violation` (step 3), the staleness comparison
  (step 2), and `_schema_errors`' cross-field rules (step 1c —
  the frozen region set and the dependency records; this is
  the read whose round-1 form made the correcting contribution
  unmentionable while a fault stood, as round-1 note I-5
  recorded). The read record and the changed-by record were
  already history-derived and are unchanged.
- The separation this creates: the engine's operational live
  state remains the source of the snapshot L handed to seal
  attempts, and the TV-1 fault hook (and the in-process fault)
  corrupts only that view. Admission never reads it. Unfaulted,
  the two states are identical, so Stage 1–3 behaviour is
  unchanged bit-for-bit.
- **Boundary of this correction, stated plainly:** commit
  planning (the hypothetical group state in `_commit_group`,
  from which the attempt's snapshot is taken) and the Stage 3
  ladder's referential/state reads still read the operational
  live state. The snapshot MUST come from the live view — that
  is what makes it L rather than a second copy of R — and no
  case in this round exercises a ladder action against a
  faulted region. The brief's separation is implemented for
  admission, staleness, and the read-record checks, which are
  the reads C-B2 names; the planning/ladder reads are named
  here so the boundary is examined, not hidden.

### C-B3 — Binding mandatory on the service path (B3)

Interpretation I-1 is **not accepted as implemented** (the
historical-compatibility principle is accepted; the selectable
route is not). Correction in `fabric/service.py`:

- The normal `open_run` admin op now ALWAYS binds Rev 9 + A1 +
  the pinned pack (`stage4_binding()`), with the VP-55 digest
  guard unconditional: a request naming a different
  `pack_sha256` is refused before anything is appended. The
  former `bind_stage4` flag is ignored — omitting it or setting
  it false produces the same bound opening. Requests still
  carrying `bind_stage4: true` (the round-1 service tests) work
  unchanged.
- Legacy unbound opening survives only as a separate,
  explicitly named admin op, `open_run_legacy_unbound`, which
  opens with no binding and names itself in its result
  (`legacy_unbound: true`). It is not an option of `open_run`
  and nothing in the Stage 4 protocol uses it.
- **No suite setup needed rerouting.** With mandatory binding
  in force, every pre-Stage-4 suite was rerun UNEDITED and
  passed at its exact baseline count (section 7): their service
  flows never reach a seal-relevant difference (idle commits
  bypass the seal step by design; breach submissions are
  rejected before any commit; the twin probe is read-only;
  Stage 3's one socket contribution passes its seal attempt
  cleanly and its assertions do not count attempts). The
  legacy op therefore stands as the isolated compatibility
  path, exercised by the new suite's boundary test, but no
  existing suite depends on it.

### C-B4 — Dual-evaluator pack execution, actual verdicts (B4)

`pack_validation.py` reworked:

- The harness gained a behaviour-neutral capture hook
  (`Harness.attempt_observer`, installed only by the pack
  harness): at each seal attempt, before the checker is
  invoked, it records the attempt's exact inputs — the
  committed history H as it stands before the group, the staged
  batch B, the snapshot L, and the authenticated actor.
- Every live attempt case (VP-30..VP-38, VP-45, VP-46, VP-48,
  VP-49, and the newly realised VP-35) now replays its captured
  (H, B, L) through BOTH `fabric.seal.evaluate_attempt` and the
  checker process and records BOTH actual verdicts (the
  contract projection: outcome, failed checks + affected sets,
  raises, attachments, resolutions, divergence, seal contents,
  halt position where applicable), the expected outcome, and
  the fixture hash over the captured inputs. The live-path
  assertions (attempt counts, recorded outcomes, tension
  lifecycle in the history) are kept and must ALSO hold — the
  dual verdicts are additional evidence, not a replacement.
- VP-36's dual content: the captured inputs of the doomed
  attempt, evaluated by both evaluators in working form (the
  live path's checker is a failing process by construction);
  the case's pass condition remains the failure contract
  (CheckerFailure, no partial group, history unchanged).
- VP-38's dual content: the final commit's captured attempt
  (both verdicts); the case additionally asserts the observer
  captured NO second attempt at close — the absence is now
  evidenced at the evaluator boundary, not only in the history.
- Genuinely single-subject cases are marked
  `dual_applicable: false` in the manifest itself, with the
  justification recorded (section 6 register): VP-22, VP-23
  (no attempt is staged for a rejected contribution — there is
  no (H, B, L) to evaluate; their subject is the trigger
  contract), VP-28 (the checker alone is the subject; I-13
  accepted), VP-50..VP-54 (one derived-report implementation
  by design; I-12 accepted), VP-55 (the binding contract; its
  cross-side property — both sides honour the one pinned
  digest — is asserted inside the case), VP-29 (the agreement
  computation itself).
- **VP-29 recomputed** over the full dual-applicable set: every
  manifest entry is either in the compared set or explicitly
  marked not dual-applicable; an unmarked, uncompared entry
  fails VP-29. Disagreements are computed from the recorded
  verdict columns, as before, but the compared set is now the
  whole dual set (section 6).
- **Gap found and closed:** round 1's manifest contained no
  VP-35 record at all (61 records realised 54 of the 55
  vectors; the two-seal contributions boundary was asserted
  nowhere). VP-35 is realised in this round as a live dual
  case: two accepted contributions with passing attempts; both
  attempts' dual verdicts recorded; seal 1 lists exactly the
  first contribution, seal 2 exactly the second.

### Interpretations — disposition summary

- **I-5 — ACCEPTED with boundary** (examination ruling). Kept:
  the repair in every TV-1 demonstration is an explicit replay
  rebuild / service restart, shown as a recovery step in the
  evidence; the history is unchanged by it; the rebuilt state
  is shown to come from verified replay; the restart is not
  the correcting contribution. The new suite's C-B2 (v) test
  asserts each element. (One I-5 sentence described
  pre-correction behaviour — the schema's frozen set read from
  the corrupted state; under C-B2 that read is authoritative,
  and the repair is nonetheless retained as TV-1's explicit
  recovery step, per the accepted boundary.)
- **I-1 — NOT ACCEPTED as implemented** → corrected per C-B3.
  The binding is still read from RUN_OPENED and a run cannot
  change its authority set mid-run; what changed is that the
  service's normal opening no longer offers an unbound route.
- **I-3 — SUPERSEDED by Vane's S2 ruling** → corrected per
  C-B1. VP-18's expectation changes accordingly (section 6):
  the pack text left VP-18 conditional ("if S2 does fail on L,
  FAIL(S2) governs"); the ruling defines the regression branch
  as exactly an S2 failure on L, so VP-18 now expects
  FAIL(S2, {Components}). The MISMATCH branch survives for
  divergence no check explains, realised as VP-18-hi
  (higher-version divergence) alongside the combined
  precedence case VP-18-prec.
- **Admission-attribution deviation — REJECTED** → corrected
  per C-B2. The round-1 deviation text stands in the round-1
  notes as the examined record.

## 2. Changed files

| File | Correction | Change |
|---|---|---|
| `fabric/seal.py` | C-B1 | `s2_findings` redefined on (replay, live) per the ruling; call site updated; S2 resolution re-run takes the replay baseline. |
| `fabric/checker.py` | C-B1 | `_s2_findings` redefined on (replay, live), independently worded and coded; `_inconsistency_absent` S2 branch likewise; no new imports (VP-28 boundary intact). |
| `fabric/harness.py` | C-B2, C-B4 | `_authoritative_state()` added (verified fold, head-memoised); `_structural_violation` restored to whole-state Stage 2 semantics on the authoritative fold; staleness and `_schema_errors` cross-field reads moved to the authoritative fold; `attempt_observer` capture hook in `_seal_step` (behaviour-neutral when unset); `verified_fold`/`empty_state` imports added. |
| `fabric/service.py` | C-B3 | `open_run` always binds + unconditional digest guard; `bind_stage4` flag ignored; new isolated `open_run_legacy_unbound` op. |
| `pack_validation.py` | C-B4, C-B1 | VP-18 reworked (regression / -hi / -prec); live attempt cases record dual verdicts from captured (H, B, L); VP-35 realised; `dual_applicable` marking in every manifest entry; VP-29 recomputed over the dual set with an unmarked-entry failure condition. |
| `stage4_corrections_tests.py` | new | The correction round's suite: C-B1 (6 checks, both evaluators), C-B2 (13 checks), C-B3 (4 checks) + genesis (1) — 24 checks. |
| `STAGE4-CORRECTION-NOTES.md` | new | This file. |

No existing test suite file was edited. `stage4_tests.py` is
untouched (no additions were needed). `STAGE4-BUILD-NOTES.md`
is untouched.

## 3. Named partial — C-B2 test (i), the S1 fixing half

The dispatch brief's test (i) asks, for a violation standing
in the authoritative state, that a non-fixing contribution be
rejected and a fixing contribution admitted — for S1 and S3
alike. The S3 half is realised in full (genesis-asserted cycle:
non-fixing rejected; the removing contribution admitted; the
state then admits ordinary work again). **The S1 fixing half
cannot be constructed through the protocol, and this is
named, not smoothed:**

- A genesis-asserted dangling dependency (C uses Q, Q not a
  region) makes every non-fixing contribution inadmissible —
  that half is tested and passes.
- A fixing contribution would have to remove the dangling
  dependency. Its endpoints must both enter the contribution's
  read and write sets (Annex B cross-field rule (iii)); Q is
  not a region, the harness serves no discovery for it, and a
  read set must equal the recorded reads exactly — so the
  removal cannot lawfully be submitted. Independently, the
  shared operation application advances BOTH endpoints'
  versions on a removal, and Q has no version record to
  advance: the application itself is undefined for a
  missing-endpoint dependency. Both properties are inherited
  from the accepted Stage 2 artifact (the same cross-field
  rules and the same `_apply_operations`), not introduced by
  this round.
- Consequence, stated plainly: a genesis-asserted
  missing-endpoint dependency is a poisoned genesis — the
  fabric can refuse all further work on such a run (which the
  whole-state check now guarantees it does, rather than
  silently carrying the violation), but no agent contribution
  can repair it. Repair at the history level is an
  examiner-side act, outside the contribution protocol. If
  Vane wants this corner closed, it needs a design decision
  (e.g. a removal that tolerates a missing endpoint), not a
  test.

## 4. What was NOT changed

- The pinned pack V2, Brief Rev 2, Rev 9 + A1: untouched.
- The examined round at a99a7676: untouched (this round's
  changes are new working-tree states, shelved separately).
- All prior suite files: untouched, rerun unedited.
- The checker interface contract (round-1 notes section 2):
  unchanged — same request/verdict shapes; the S2 definition
  inside the verdict changed per the ruling.
- No closing exercise was run. No live agents were used.

## 5. New-suite design notes

- C-B1's lifecycle checks use canned histories (an open S2
  tension asserted in H) because no live path in this round
  manufactures a live version regression — the fault hooks
  drop regions (S1-shaped), they do not lower versions. The
  evaluator contract is where S2 tensions live; both
  evaluators are exercised on identical inputs, which is what
  the correction requires.
- C-B2's genesis-asserted states are built through the
  store's own append path with a modified RUN_OPENED payload
  (the same construction the pack's canned VP-27 uses), so the
  authoritative fold — not a test double — carries the
  violation.

## 6. Revised pack mapping table (recorded BEFORE execution)

Unchanged cases keep their round-1 realisations (round-1
notes section 4 stands for them); their dual-applicability is
registered here. Changed or new realisations are specified in
full. "Dual" = the manifest records both implementations'
actual verdicts (fold projections for replay cases, verdict
contracts for attempt cases) over identical inputs, and VP-29
compares them.

| Case | Realisation (this round) | Dual? | Expected |
|---|---|---|---|
| VP-01-fold, VP-01 | as round 1 | yes | fold ok; attempt PASS, seal issued |
| VP-02 | as round 1 | yes | state identical except last_seq |
| VP-03 | as round 1 | yes | `refused`; nothing folded; no seal |
| VP-04..VP-15 (incl. lettered) | as round 1 | yes | as round 1 |
| VP-16 | as round 1 | yes | FAIL(S1, {D-CS, S}); no seal |
| VP-17 | as round 1 (this is also the S2 equality case: L == R, no S2 finding) | yes | PASS |
| VP-18 | **changed**: evaluate(H, B=[], L = fold(H) with C's version lowered to 0) | yes | **FAIL(S2, {C})**; raise (S2, {C}); no seal (per the ruling: the regression branch is an S2 failure on L) |
| VP-18-hi | **new sub-case**: L with C's version raised to 7 | yes | MISMATCH; no failed check; divergence names C (lower-bound-only S2) |
| VP-18-prec | **new sub-case**: L missing S (divergence + S1 failure) AND C's version lowered | yes | FAIL governs; failed = S1 {D-CS, S} and S2 {C} |
| VP-19 | as round 1 | yes | no S2 finding; PASS; versions advanced |
| VP-20 | as round 1 | yes | FAIL(S3, {D-CS, D-SC}); no seal |
| VP-21 | as round 1 | yes | PASS |
| VP-22 | live trigger case, as round 1 | **no** — no attempt is staged for a rejected contribution; no (H, B, L) exists to evaluate | outcome `schema`; no SEAL_ATTEMPTED |
| VP-23 | live trigger case, as round 1 | **no** — same justification as VP-22 | outcome `stale`; no SEAL_ATTEMPTED |
| VP-24 | as round 1 | yes | PASS; seal issued |
| VP-25 | as round 1 | yes | `refused`; no seal |
| VP-26 | as round 1 | yes | MISMATCH; divergence names P |
| VP-27 | as round 1 | yes | replay ok; FAIL(S1, {D-CQ, Q}); no seal |
| VP-28 | import audit + static scan, as round 1 | **no** — single subject (the checker alone); I-13 accepted | no forbidden module in the checker's transitive graph |
| VP-29 | **recomputed**: agreement over every dual-applicable entry; exclusions are exactly the entries marked `dual_applicable: false`; any unmarked/uncompared entry fails the case | — (the computation itself) | disagreements == [] over the dual set |
| VP-30 | live flow as round 1 + captured attempt replayed through both evaluators | yes | live: one attempt, PASS; dual verdicts: PASS, agreeing |
| VP-31 | live flow as round 1 + BOTH captured attempts replayed | yes | live: 2 attempts, first FAIL, tension raised, second still attempted; dual verdicts: FAIL(S1) then FAIL(S1, attached), agreeing |
| VP-32 | continuation + the correcting attempt replayed | yes | live: group ends [SEAL_ATTEMPTED(pass), TENSION_STATUS(resolved)] with the attempt's seq in evidence; dual verdict: PASS with the resolution |
| VP-33 | VP-31's first captured attempt | yes | dual verdicts: outcome fail; failed = S1 {D-CS, S}; no seal |
| VP-34 | live flow as round 1 + the content contribution's captured attempt replayed | yes | live: seal issued, both questions listed with marks, statuses unchanged; dual verdict: PASS, seal lists both questions with the same marks |
| VP-35 | **new**: bound run, two accepted contributions (I then P), each with a passing attempt; both attempts captured and replayed | yes | live + dual: seal 1 lists exactly [cid1]; seal 2 lists exactly [cid2]; no omission, no double count |
| VP-36 | live flow as round 1 (checker command = failing process) + the doomed attempt's captured inputs evaluated by both evaluators in working form | yes (see C-B4 note) | live: CheckerFailure, no partial group, history unchanged; dual verdicts on the inputs: agreeing (the attempt the machinery could not evaluate) |
| VP-37 | live flow as round 1 + the close attempt (B = []) captured and replayed | yes | live: exactly one close-time attempt, then RUN_CLOSED; dual verdicts: PASS, agreeing |
| VP-38 | live flow as round 1 + the final commit's captured attempt replayed; observer asserts no second capture at close | yes | live: no second SEAL_ATTEMPTED; RUN_CLOSED; dual verdicts: PASS, agreeing |
| VP-39..VP-44 | as round 1 | yes | as round 1 (VP-43 additionally pins: no S2 finding for the absent region) |
| VP-45 | live nine-step flow as round 1 + both captured attempts replayed | yes | live: steps 1–9 in order; dual verdicts: FAIL(S1) then PASS + resolution, agreeing |
| VP-46 | VP-34's first captured attempt replayed | yes | dual verdict: PASS; seal lists T1 open; tension status unchanged |
| VP-47 | as round 1 | yes | PASS; raises == [] |
| VP-48 | live flow as round 1 + the faulted attempt captured and replayed | yes | live: assessment rejected `structural_target`, nothing recorded, tension open; dual verdicts: FAIL(S1) with the raise, agreeing |
| VP-49 | live flow as round 1 + the captured attempt replayed | yes | live + dual: seal issued; facet status as folded, unchanged by the seal |
| VP-50..VP-54 | starvation report, as round 1 | **no** — one derived-report implementation by design; I-12 accepted; agreement property is byte-identity of API vs CLI output, asserted inside each case | as round 1 |
| VP-55 | binding cases, as round 1 | **no** — the binding contract; the cross-side property (both sides honour the one pinned digest) is asserted inside the case | opening blocked on wrong digest; RUN_OPENED names id/version/SHA-256; checker fold reports the bound digest and flags a mismatch |

## 7. Results

*(Appended after execution. Nothing above this section was
altered after the mapping table was recorded. Every count is
the suite's own printed count, from a full clean run of the
finished round.)*

**New correction suite (stage4_corrections_tests.py) — 24/24
checks PASS.** C-B1: regression FAIL(S2) in both evaluators;
equality (no S2 finding); higher-version MISMATCH; combined
precedence (FAIL governs, S1 + S2 findings); S2 lifecycle
attach and resolve in both evaluators. C-B2: genesis-carried
S1 blocks non-fixing admission; genesis-carried S3 blocks
non-fixing admission and admits the fixing contribution (and
ordinary work after it); plant introduction rejected S3;
double-remove rejected S1 (premise); add-to-non-region rejected
at schema; TV-1 fault in L only — triggering contribution
admitted, attempt fails S1, one tension; a contribution whose
read set includes the faulted region also admitted, its
attempt attaching to the standing tension; repair by replay
rebuild with the history byte-identical, resolution earned by
the correcting contribution's passing attempt with the
attempt's seq as evidence. C-B3: the three negative opens
(omitted flag, false flag, false flag + wrong digest) and the
legacy boundary; genesis hash pinned under both openings.

**Pack validation (pack_validation.py) — 64/64 case records
PASS** (the round-1 baseline of 61, plus VP-18-hi, VP-18-prec,
and the newly realised VP-35). Per implementation: every
dual-applicable case's observed verdict equals the expected
verdict on the engine side (`fabric.seal.evaluate_attempt` /
`fabric.engine.verified_fold`) and on the checker side (the
checker process), over identical inputs — for the live cases,
the captured (H, B, L) of the actual attempts. **VP-29:
54 dual-applicable cases compared, zero disagreements, zero
unmarked entries.** Exclusions (marked in the manifest with
justifications): VP-22, VP-23, VP-28, VP-50, VP-51, VP-52,
VP-53, VP-54, VP-55 — and VP-29 itself, as the computation.
VP-18 now records FAIL(S2, {Components}) on both
implementations; VP-35's two seals list exactly one
contribution each on both. The full per-case manifest is at
`pack-validation-manifest.json` (now carrying the
`dual_applicable` marking per entry).

**Stage 4 suite (stage4_tests.py, unedited) — all checks pass
(22 PASS lines)**, unchanged from the examined round's own
reporting.

**Regressions — all prior suites unedited, exact baseline
counts, zero failures:** stage1_smoke 18, stage2_tests 40,
stage2_corrections 53, stage2_corrections_round2 27,
stage2_corrections_round3 34, stage2_corrections_round4 32,
stage2_corrections_round5 37, stage2_corrections_round6 31,
stage3_tests 71, stage3_corrections 37, observer safety 11 —
**391 checks**, matching the pre-Stage-4 baseline exactly,
with mandatory service binding (C-B3) in force throughout.

**Genesis state hash:**
`9a7250bde82bfd8bd220b6013f38b4ce289a702fe86119f2723616055c070b1f`
— unchanged, under both the bound and the legacy unbound
opening (asserted in the new suite).

**Totals for the correction round: 391 + 22 + 24 + 64 = 501
checks, all passing.** The closing exercise and the Annex E
evidence package were NOT run (they remain downstream of
Stage 4 acceptance). No live agents were used at any point.

**Named partial (from section 3, restated so it cannot be
missed):** C-B2's test (i) is realised in full for S3 and in
its rejection half for S1; the S1 fixing half is not
constructible through the contribution protocol, for reasons
inherited from the accepted Stage 2 artifact. It is Vane's to
rule on whether that corner needs a design change.
