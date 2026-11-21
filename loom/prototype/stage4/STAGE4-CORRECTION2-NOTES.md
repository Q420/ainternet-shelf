# Stage 4 — Correction Round 2 Notes

Correction round 2 built 2026-11-21 against Vane's
correction-round examination
(`VANE-STAGE4-CORRECTION-EXAMINATION-2026-11-21.md`):
**B1 PASS, B4 PASS** (closed; their substance is not disturbed
by this round), **B2 NOT CLOSED** (the authoritative/snapshot
separation was implemented only at the admission call sites),
**B3 NOT CLOSED** (`open_run_legacy_unbound` was still
dispatched by the running service; its test-only status rested
on a comment and a name). The S1 genesis-repair half was ruled
**formally non-constructible under the current protocol** —
recorded as such in section 4, never as passed.

Dispatch brief of record:
`STAGE4-CORRECTION2-DISPATCH-2026-11-21.md`. One addition
arrived from Vane after dispatch and is folded into this round:
the boundary evidence must be **same-run** (section 5).

**Preserved artifacts.** The Stage 4 build round (shelf
a99a7676) and correction round 1 (shelf e46d47d0) are NOT
amended. `STAGE4-BUILD-NOTES.md` and
`STAGE4-CORRECTION-NOTES.md` are untouched. Everything here is
a new round in the working tree, shelved separately.

**This file's boundary statement (section 1) and correction
design (sections 2–5) were recorded BEFORE the new execution.**
Results are appended in section 7 after execution; nothing in
sections 1–6 is rewritten afterwards.

---

## 1. The boundary statement (recorded before execution)

The invariant: the TV-1 fault — a corruption of the engine's
operational live view (`engine.state`, e.g. a region record
dropped by the fault hook) — is visible through exactly ONE
consumer: the snapshot L handed to seal attempts. Every other
consumer reads the **authoritative state**: the verified fold
of the committed history (`Harness._authoritative_state()`,
head-memoised), which the fault cannot reach because the fault
mutates an in-memory cache, never the history.

**Paths that read the AUTHORITATIVE state after this round:**

| Path | What it reads there |
|---|---|
| `Harness.view_pattern()` | regions, dependencies, tensions, claims, watches, facet statuses (agent-facing pattern surface) |
| `Harness.consult_index()` | open tensions, claims (agent-facing index surface) |
| `Harness.open_region()` | region existence, content, version (agent-facing content reads; the breadth cap's region set is the frozen set) |
| `Harness.read_breadth()` | the region total RB is measured against |
| `Harness.run_failed` | the folded run status |
| `Harness.submit()` step 1c `_schema_errors()` | frozen region set, dependency records (admission — moved in round 1, kept) |
| `Harness.submit()` step 2 staleness | current versions, changed-by record (admission — moved in round 1, kept) |
| `Harness.submit()` step 3 `_structural_violation()` | the whole hypothetical state (admission — restored in round 1, kept) |
| `Harness._note_accepted()` fallback | dependency endpoints for the changed-by record |
| `Harness._commit()` | region titles for the acceptance summary; `last_seq` for the planning entry |
| `Harness._commit_group()` **planning** | the hypothetical state the derived tension/facet evaluation runs against (`_evaluate_derived`, `_next_tension_transition`, `_facet_status`) |
| Stage 3 ladder `_ladder_referential()` | assessment targets, examination regions / related tension, claim facet |
| Stage 3 ladder `_ladder_state()` | facet versions (`version_never_existed`), superseded assessments |
| `Harness.examine()` post-ladder | the multi-match duplicate scan over tensions; region titles |
| `FabricService.failed` | derived from the history itself (a RUN_FAILED event stands in it), not from the live cache |
| `Harness.close_run()` | `last_seq` for the close attempt's position; the recorded `final_state_hash` is the authoritative state's hash |

**The single path that reads the LIVE view:**

- The **seal-attempt snapshot L**. In `_commit_group`, a
  parallel live hypothetical is maintained beside the planning
  hypothetical: it starts from the operational live state and
  each staged spec is applied to it under a guard (a spec the
  corrupted view cannot fold — e.g. an operation touching the
  dropped region — leaves the live hypothetical at its
  pre-spec value for that spec; on an unfaulted run the guard
  never fires and the live hypothetical is exactly the
  post-batch live state, as before). The snapshot handed to
  `_seal_step` (and captured by the round-1 `attempt_observer`)
  is that live hypothetical. In `close_run`, the close-time
  attempt's snapshot is the live state itself, as before.
- The fault hook itself (`inject_live_state_fault` on the
  service's admin path, and the in-process `del
  engine.state[...]` in tests) writes the live view — that is
  its purpose; it is the fault, not a consumer.
- `Engine.commit_events` folds committed events into the live
  cache. That is the cache's maintenance, not a read: the
  events it folds are the committed history, and the corruption
  persists across commits precisely because the cache is only
  ever updated by folding new events onto it (TV-6 depends on
  this: later attempts must still see the fault). No decision
  is taken from the cache there. One guard rides with it
  (C2-B2): an event the corrupted cache cannot fold (one
  touching the dropped region — a `FACET_STATUS` for it, say)
  still appends, because the harness validated and planned it
  against the authoritative fold; the cache keeps its pre-event
  value for that event rather than vetoing the commit. On an
  unfaulted history the guard never fires.

Two things that are NOT state reads of either kind: the harness
registries (`read_record`, `_last_changed_by`, the Stage 3
idempotency/identity/registry records) are rebuilt from and
maintained against the event history event by event; and the
checker's own fold is its independent business (B1/B4, closed,
untouched).

## 2. C2-B2 — the boundary made real throughout the service

Changes in `fabric/harness.py`:

- `view_pattern()`, `consult_index()`, `open_region()`,
  `read_breadth()`: the state they serve from is
  `_authoritative_state()` instead of `self._engine.state`.
  On an unfaulted run the two are identical, so Stage 1–3
  behaviour is unchanged; on a faulted run the faulted region
  no longer vanishes from what agents see, and a content read
  of it is served (and recorded) at its authoritative version.
- `run_failed`: folded status from the authoritative state.
- `_note_accepted()`: the fallback dependency-endpoint map is
  built from the authoritative state's dependencies.
- `_commit()`: titles and `last_seq` from the authoritative
  state.
- `_commit_group()`: the planning hypothetical is a deep copy
  of the authoritative state; the snapshot is the guarded
  parallel live hypothetical described in section 1. The
  derived evaluation (tension transitions, facet accounting)
  therefore plans against the state the history establishes,
  while the attempt still judges the live view.
- Stage 3 ladder: `_ladder_referential()` and
  `_ladder_state()` read the authoritative state;
  `examine()`'s duplicate scan and titles likewise. (The
  ladder's authority step reads the harness read record —
  history-derived already.)
- `close_run()`: attempt position and `final_state_hash` from
  the authoritative state; the close attempt's snapshot
  remains the live view.

Changes in `fabric/engine.py`:

- `commit_events`: the guarded cache fold described in
  section 1 — a committed event the corrupted live cache
  cannot fold appends anyway (it was validated against the
  authoritative fold); the cache keeps its pre-event value for
  that event. Store-append failures still roll the whole
  transaction back, exactly as before.

Changes in `fabric/service.py`:

- `FabricService.failed` derives from the event history (a
  RUN_FAILED event stands in it) rather than the live cache's
  `run_status` key.
- The fault hook is unchanged: it corrupts the live view only.

**Direct tests** (new suite, section 6): with a region dropped
from the live view — the region still appears in
`view_pattern()`; `open_region()` serves it at its
authoritative version and `read_breadth()` accounts the read;
`examine()` over a region set including the faulted region is
recorded (its referential check reads the frozen set from the
fold); an assessment of the faulted facet at its authoritative
version is recorded (its state check reads the fold); a
completion claim on the faulted facet is recorded; a
contribution passes planning + admission unaffected; the seal
attempt still FAILs S1 in both evaluators; the TV-1 lifecycle
still resolves after the I-5 repair. The same-run form of all
of these is section 5.

## 3. C2-B3 — the legacy unbound opening, mechanically isolated

Chosen route: **legacy opening moves entirely into
test-support code the service never imports or dispatches**
(the brief's first option), over a construction-time posture,
because the posture would still leave the operation inside the
running service's dispatch table, reachable by any service
started in that posture; the test-support route removes it
from the service altogether.

- `fabric/service.py`: the `open_run_legacy_unbound` admin
  branch is **deleted**. The ordinary Stage 4 service has no
  such operation: dispatched as a normal admin request it
  falls through to the unknown-operation refusal, and no run
  opens. `open_run` is unchanged (always binds; caller flags
  ignored; wrong digest refused — round 1's negative tests
  stand).
- `fabric/runtime_setup.py` (driver-side tooling; the service
  does not import it): `admin_request()` — the helper the
  correction suites already import — routes an
  `open_run_legacy_unbound` request to a test-support
  constructor (`_legacy_unbound_open`) that opens the unbound
  run directly against the runtime's store with
  `Engine.open_run(..., binding=None)`, fills the rig
  identity's run id as the old service branch did, and returns
  the same result shape (`legacy_unbound: true`). This is the
  reroute the dispatch brief sanctions: correction round 1's
  suite reaches legacy opening only through this already-
  imported helper, and **no existing suite file is edited**.
  The running service process never sees the request; its own
  history reads (the round-1 suite's next call) read the store
  the constructor wrote, which is all that suite asserts on.
- Required test (new suite): a **raw** admin-socket request
  (straight to the socket, bypassing the helper's reroute)
  naming `open_run_legacy_unbound` is refused by the ordinary
  running service and opens nothing; the same runtime's
  ordinary `open_run` still binds; and the helper-routed
  legacy construction still produces an unbound run, proving
  the path survives only in test support.

## 4. C2-B2b — the orphan-removal negative test; the non-constructible record

Per Vane's ruling: under Rev 9's operation and read-set rules,
a dangling dependency whose endpoint is not a region has **no
lawful contribution-level repair**, and the S1 genesis-fixing
half is **formally non-constructible under the current
protocol — not passed, not failed: non-constructible**. No new
operation is invented; Rev 9 semantics are unaltered. What
stands, preserved from round 1: the successful S1 rejection
test (a genesis-carried dangling dependency blocks every
non-fixing contribution at whole-state admission), the
complete S3 rejection/fix path, and the genuine TV-1
live-fault repair path (I-5 rebuild + correcting contribution
+ passing same-check attempt).

Added here (new suite): the negative test of the attempted
orphan-removal boundary — on a genesis carrying the dangling
dependency (Components uses Q, Q not a region): Q cannot be
opened (no discovery exists for it; `open_region(Q)` is
refused at the interface), and a contribution attempting to
remove that dependency is **rejected** (schema step: the
removal's endpoints cannot both enter the read/write sets, as
cross-field rule (iii) requires), with no acceptance recorded
and the dependency still standing active in the authoritative
state. If Ben later wants repair of poisoned genesis, that is
a separate design decision (Vane's ruling).

## 5. The same-run boundary evidence (Vane's addition, post-dispatch)

Separate demonstrations that happen to pass are not enough:
the boundary evidence is one continuous lifecycle in ONE run,
asserted over that run's single history. The new suite carries
it as a dedicated test (`stage4_correction2_tests.py`, the
SAME-RUN section), with these beats in order, all in one bound
run's history:

1. Agents open their regions (the correcting agent reads
   Components + the soon-to-be-faulted State; the working
   agent reads Interactions + Presentation; a third agent
   reads State).
2. The fault is injected: State is dropped from the live view
   only (the history is untouched — verified by fold).
3. Agent-facing reads still show State from the authoritative
   state: it stands in `view_pattern()` at version 1; the
   third agent's earlier read stands in the breadth accounting
   (RB = 1/6), and a fresh `open_region(State)` serves its
   authoritative content and version.
4. A contribution by the working agent (append to
   Interactions) passes planning + admission unaffected and is
   accepted.
5. The seal attempt on that same run FAILs S1 with affected
   {D-CS, State}: the recorded SEAL_ATTEMPTED says so, and the
   attempt's captured (H, B, L) — replayed through BOTH
   evaluators (`fabric.seal.evaluate_attempt` and the checker
   process) — FAILs S1 in both, with State in the affected set.
   Exactly one structural tension stands, from that attempt.
6. The I-5 repair: the live view is rebuilt by explicit
   verified replay; the history is byte-identical across the
   repair; the tension still stands open in the rebuilt state.
7. The correcting contribution (the correcting agent removes
   D-CS) is accepted; its attempt passes the SAME check (S1
   re-run on the original affected set); the tension resolves
   with that attempt's sequence as its evidence.
8. Continuity assertions over the single history: one
   RUN_OPENED; the event sequence interleaves exactly as the
   beats ran (reads → accepted contribution → failed attempt →
   tension raised → accepted correction → passing attempt →
   resolution); the hash chain verifies end to end.

## 6. New suite and changed files (planned; results in section 7)

| File | Change |
|---|---|
| `fabric/harness.py` | C2-B2: authoritative reads throughout (section 2); planning/snapshot split in `_commit_group`. |
| `fabric/engine.py` | C2-B2: guarded cache fold in `commit_events` (sections 1–2). |
| `fabric/service.py` | C2-B2: `failed` derived from the history. C2-B3: `open_run_legacy_unbound` dispatch deleted. |
| `fabric/runtime_setup.py` | C2-B3: legacy unbound opening as a test-support constructor, routed by the already-imported `admin_request` helper. |
| `stage4_correction2_tests.py` | NEW: C2-B2 direct tests, the same-run boundary evidence, C2-B2b orphan-removal negative, C2-B3 refusal + legacy-in-test-support tests. |
| `STAGE4-CORRECTION2-NOTES.md` | NEW: this file. |

No existing test suite file is edited. `STAGE4-BUILD-NOTES.md`
and `STAGE4-CORRECTION-NOTES.md` are untouched. The pinned pack
V2, Brief Rev 2, Rev 9 + A1 are untouched. No closing exercise.
No live agents.

## 7. Results

*(Appended after execution; sections 1–6 stand as recorded
before it. Every count is the suite's own printed count, from
a full clean run of the finished round.)*

**New correction-round-2 suite
(stage4_correction2_tests.py) — 21/21 checks PASS.**
C2-B2 direct (7 checks): the fault confined to the live view;
view_pattern still shows State at its authoritative version;
a fresh agent opens State from the fold with breadth accounted
at 1/6 over six regions; examine over a region set including
State creates its tension; assessing that tension plans its
open → examined transition against the fold; a facet
assessment of State at its authoritative version records; a
completion claim on State records and its derived transition
commits (the facet stands COMPLETE on the claim plus the
independent examined review — the corrupted cache did not
veto the commit). SAME-RUN (7 checks, section 5's beats 2–8):
every beat passed in the one history, including the captured
(H, B, L) replayed through BOTH evaluators — both FAIL S1 on
{D-CS, State} — and the closing continuity assertions over the
single chain. C2-B2b (3 checks): Q cannot be opened; the
orphan-removal contribution is rejected at schema with the
dependency still standing; the preserved S1 rejection half
still blocks non-fixing work. C2-B3 (4 checks): the raw admin
request for the legacy op is refused `unknown_op` by the
ordinary running service and opens nothing; the same service's
open_run binds the pinned pack; the helper-routed test-support
construction opens the unbound run; the genesis hash is the
pinned constant under both openings.

**Pack validation (pack_validation.py, unedited) — 64/64
case records PASS.** VP-29 unchanged in substance: **54
dual-applicable cases compared, zero disagreements, zero
unmarked entries.** The captured (H, B, L) semantics are
unchanged: the snapshot the observer captures is still the
live hypothetical, fault and all.

**Stage 4 suite (stage4_tests.py, unedited) — all checks pass
(22 PASS lines).** **Correction-round-1 suite
(stage4_corrections_tests.py, unedited) — 24/24 PASS**,
including its C-B3 legacy-boundary check, which now reaches
legacy opening through the test-support reroute in
`fabric/runtime_setup.py` (the helper it already imported);
no suite file was edited.

**Regressions — all prior suites unedited, exact baseline
counts, zero failures:** stage1_smoke 18, stage2_tests 40,
stage2_corrections 53, stage2_corrections_round2 27,
stage2_corrections_round3 34, stage2_corrections_round4 32,
stage2_corrections_round5 37, stage2_corrections_round6 31,
stage3_tests 71, stage3_corrections 37, observer safety 11 —
**391 checks**, matching the pre-Stage-4 baseline exactly,
with the legacy op absent from the service dispatch
throughout.

**Genesis state hash:**
`9a7250bde82bfd8bd220b6013f38b4ce289a702fe86119f2723616055c070b1f`
— unchanged (asserted in the new suite under both the bound
opening and the test-support legacy unbound opening).

**Totals for correction round 2: 391 + 22 + 24 + 64 + 21 =
522 checks, all passing.** The closing exercise and the
Annex E evidence package were NOT run (they remain downstream
of Stage 4 acceptance). No live agents were used at any point.

**Named items, not smoothed:**

- The S1 genesis-fixing half remains **formally
  non-constructible under the current protocol** (Vane's
  ruling; section 4). It is not counted as passed anywhere in
  this round; the new negative test makes the boundary
  executable, and the preserved rejection half, the complete
  S3 path, and the TV-1 repair path all still stand.
- The live-hypothetical snapshot guard and the engine cache
  guard (section 1) fire only when the corrupted live view
  cannot fold a spec/event. They preserve the divergence for
  the checker instead of letting the cache veto or paper over
  a commit the authoritative planning validated. On every
  unfaulted history both guards are inert, which the 391
  unedited regressions at exact baseline counts demonstrate.
- One assertion in the new suite was corrected during the
  round's own execution: the claim test first expected the
  faulted facet to derive `claimed`; with the independent
  examined review also on record, section 5's precedence
  derives `complete`. The suite now asserts `complete` — the
  implementation was right, the expectation was wrong, and
  the correction is recorded here rather than silently
  adjusted.
