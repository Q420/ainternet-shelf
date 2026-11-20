# Duenna Stage 8 — Fixture Discipline Report (K14)

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 8; ID-SYSTEM-DESIGN-DRAFT-V3.md (K14)
Build location: ~/workspace/duenna-fix/stage8/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 8 built from the plan, after Stage 7 cleared Gate 1)

## Status of this report

This report is EVIDENCE for the examiner, not a verdict: whether
Stage 8 passes is the examiner's determination (Gate 1
discipline), not this report's. Nothing here declares Stage 8
complete.

## Verdict first

The fixture discipline now exists and has run over the whole
programme. All 287 tests in Stages 1–7 are inventoried with a
fixture identity (inventory completeness is exact — set equality
with discovery, asserted by a Stage 8 test), and the sabotage
matrix ran 88 mechanism neutralisations plus the joint-guard
combined runs (96 run records on disk), every outcome observed
by the witness runner, none taken from a fixture's own account
of itself.

Of 217 claimed (fixture, mechanism) pairs: **189 EXERCISED,
7 JOINT-ONLY** (the fixture discriminates its targets only in
combination), **4 SELF-WITNESSED** (Stage 4's examination
fixtures, whose own baseline sabotage is their reach evidence),
and **17 NOT-EXERCISED** — each named individually below with
the reason the matrix establishes. Two mechanisms are
discriminated by **no fixture at all** in their suites, and one
further mechanism has **no fixture claiming it and none
discriminating it**. Every earlier stage's evidence showing is
re-confirmed or downgraded below, per stage, on this evidence.

Per-stage pair counts (EXERCISED / JOINT-ONLY / SELF-WITNESSED /
NOT-EXERCISED): Stage 1: 40 / 1 / – / 1 (of 42). Stage 2: 18 / 2 /
– / 1 (of 21). Stage 3: 27 / 1 / – / 6 (of 34). Stage 4: 24 / – /
4 / 1 (of 29). Stage 5: 20 / – / – / 0 (of 20). Stage 6: 29 / 3 /
– / 6 (of 38). Stage 7: 31 / – / – / 2 (of 33).

The headline is not the 17. It is that the matrix caught its own
instrument first (below), and that the NOT-EXERCISED findings
are nearly all of one shape: a refusal or attribution that is
**overdetermined** — produced by two mechanisms in series or in
parallel, so the fixture passes when either one is removed.
Overdetermination is not a defect in the mechanism; it is a
defect in the *coverage claim* the fixture was cited for. That
is exactly DR-12's qualification, now measured instead of
asserted.

## What was built

- `witness_run.py` — the per-test witness runner: runs one
  stage suite in whatever tree it is pointed at and emits one
  JSON outcome per test. Baseline (real trees): 68 / 27 / 38 /
  36 / 30 / 54 / 34 = **287/287 ok**, re-run after the witness
  correction below with identical totals.
- `witness.py` + `mechanism8.py` + `coverage.py` — the K14
  witness for Test 8: reach records written only by the
  instrumented target mechanism at the moment its branch
  executes, naming mechanism + execution instance; the
  coverage accountant consumes witness records only.
- `mechanisms.py` — 88 sabotage mechanisms with exact source
  anchors; `verify_anchors()` is clean against the real trees
  (every anchor at its expected count).
- `inventory.py` — all 287 fixtures classified (183 guard,
  13 joint-guard, 55 functional, 24 control, 7 reproduction,
  3 exam, 1 exam-evidence, 1 boundary), with a completeness
  check against witness discovery.
- `matrix.py` / `run_matrix.py` — per mechanism: scratch-copy
  the trees, apply the patch (anchors re-verified in the
  scratch), run the witness over the mechanism's suites, diff
  against baseline, classify pairs / joint fixtures /
  collateral / instrument interaction. A baseline test absent
  from a sabotage run's outcomes is recorded as changed
  (MISSING), never as a silent pass.
- `tests/test_stage8.py` — Stage 8's own suite, **11/11**:
  Test 8's three cases, witness instance separation,
  reach-is-not-pass, coverage exclusion, inventory
  completeness, the subTest blind-spot regression, and two
  smoke matrix runs asserted exactly.

## The instrument defects this stage caught in itself

1. **The witness was blind to subTest failures.** A test whose
   failures live entirely inside `subTest` blocks produces
   neither `addSuccess` nor `addFailure` in unittest, so the
   first-pass witness recorded *nothing* for it under sabotage
   and the diff read it as unchanged. Stage 1's s5 (altered
   account) and s6 (structural validity) sabotages — both
   subTest-structured — first read as NOT-EXERCISED; both are
   in fact EXERCISED (FAIL under their sabotages once the
   witness records `addSubTest`). Fixed in `witness_run.py`,
   pinned by a regression test, baselines and the full matrix
   re-run. This is DR-08's pattern one level up: the measuring
   instrument silently not reaching the thing it claimed to
   measure.
2. **A sabotage patch that broke its target file's syntax.**
   The first form of the s4.contract_identity patch appended
   the neutralisation comment after a line-continuation
   backslash — a SyntaxError — so the whole Stage 4 suite
   failed to import and every test "changed". The run records
   showed `unittest.loader._FailedTest` ids; classification
   now records any out-of-inventory test id as a named witness
   anomaly instead of crashing or dropping it, and the patch
   was rewritten. (Final classification: zero anomalies.)

## Test 8 — the plan's acceptance cases

All three pass, against Stage 8's own instrumented mechanism
(`mechanism8.DigestGate`, whose comparison branch writes the
reach record when — and only when — it executes):

- **(a) Setup forced to exit before the target comparison:**
  the fixture raises SystemExit in setup; the witness holds
  no record for its instance; coverage records NOT-EXERCISED.
- **(b) A fixture falsely reporting its target reached:** the
  fixture's self-report claims reach; the witness contradicts
  it; coverage follows the witness — NOT-EXERCISED.
- **(c) The target comparison removed:** against
  `DigestGateWithoutComparison` the fixture's own outcome is
  PASS (the wrong digest is "accepted"), the witness records
  nothing, and the coverage accountant excludes the fixture
  from the covered count mechanically (covered_count 0).
- Instance separation: reach in one execution instance never
  attaches to another. Reach is not pass: a wrong-digest
  fixture that does reach the comparison is EXERCISED (and
  its assertion fails) — reach and outcome are different facts.

## The NOT-EXERCISED fixtures — every one, named

Pairs (fixture :: mechanism), with the reason the matrix and a
first-hand reading jointly establish:

**Stage 1 (1)**
- `test_c6_account_schema…test_c6_complete_unknowns_wrong_type
  :: s1.account_schema` — unknowns is the string `"none"`. Both
  assertions survive the schema branch's removal: the FAIL
  status is also produced by the COMPLETE-with-unknowns branch
  (a non-empty string is truthy), and `account_schema_invalid`
  in the details is *computed* independently of the return
  branch. Its sibling (missing unknowns) does discriminate the
  schema facet. The C6 showing for the wrong-type case is
  overdetermined.

**Stage 2 (1)**
- `test_schema…test_schema_is_frozen_after_construction ::
  s2.schema_freeze` — FrozenSchema's public attributes are
  read-only properties over `__slots__`; assignment raises
  AttributeError through the property data descriptor even
  with the `__setattr__` guard neutralised. The seal is two
  mechanisms; the fixture discriminates neither alone.
  (Mechanism-level companion: the s2.schema_freeze run changed
  nothing at all.)

**Stage 3 (6)**
- `test_access_admission…test_output_with_fabricated_receipt_refused
  :: s3.receipt_record_presence` and `:: s3.receipt_facts`;
  `test_stage3_sabotage…test_fabricated_receipt_quoting_canonical_hash
  :: s3.receipt_record_presence` and `:: s3.receipt_facts`;
  `test_access_admission…test_output_without_any_receipt_refused
  :: s3.receipt_record_presence` — all five pairs, and the two
  fabricated fixtures also fail their *combined* run
  (NOT-EXERCISED jointly). The fabricated/absent receipts are
  refused one gate earlier than either claimed facet: the
  output gate's receipt-registry lookup
  (`self.access.receipt(receipt_id)` → `receipt_not_issued`).
  The recorded-event presence facet the fixtures were cited
  for is reached only when a registry receipt exists whose
  event is missing — a case no fixture presents. The
  s3.receipt_record_presence run changed **nothing in the
  whole suite**: the facet is discriminated by no fixture.
  And the registry lookup that actually does the work has no
  sabotage mechanism in the matrix — a mechanism-coverage
  gap, named as such.
- `test_stage3_sabotage…test_frozen_run_cannot_be_rebound ::
  s3.frozenrun_seal` — the FrozenSchema shape again: FrozenRun's
  public attributes are read-only properties over `__slots__`,
  so rebinding raises with or without the `__setattr__` guard.
  (The s3.frozenrun_seal run changed nothing.)

**Stage 4 (1)**
- `test_dispatch…test_corrupt_artefact_takes_failure_path ::
  s4.digest_comparison` — **DR-08's exact shape, recurring in
  the current suite.** `preservation_check` checks the corrupt
  flag before the digest comparison, so the corrupt-flag
  fixture never reaches the comparison it was presented as
  exercising. The comparison's showing rests — soundly — on
  `test_wrong_digest_no_corrupt_flag_takes_failure_path`,
  which discriminates it exactly (the FX-R60f shape). The
  Stage 4 report's pairing of the two fixtures as
  comparison coverage is corrected by this record: one of
  them is, one of them is not.

**Stage 6 (6)**
- `test_attribution…test_ledger_requires_the_issued_capability
  :: s6.point_of_use` and
  `test_discrepancy…test_resolution_without_authority_refused
  :: s6.point_of_use` — both present non-authority objects
  (a governance record; `object()`) and are refused at the
  `isinstance` gate, one check before `capability_is_issued`.
  The point-of-use facet is genuinely discriminated — by the
  correction-round fixtures, which present correctly-typed
  forgeries (EXERCISED / JOINT-ONLY there). These two older
  fixtures do not reach it.
- `test_attribution…test_label_preserved_as_local_not_attribution
  :: s6.label_conversion` — the fixture asserts the label is
  preserved as local; the conversion guard (which its sibling
  `test_every_conversion_attempt_raises` discriminates
  exactly) is not what produces that outcome.
- `test_reproductions…test_t02_finding_recorded_and_attributed
  :: s6.format_prescribed` — T02's SYSTEM attribution is
  overdetermined across examine()'s stated-value branches:
  with the value stated, *both* prescribed values attribute
  SYSTEM (FORMAT_NOT_RECOGNISED / CHECKER_FAILED_ON_
  COMPLIANT_RESPONSE); format_prescribed discriminates the
  finding's *kind*, not this attribution. The kind
  discrimination is witnessed — by
  `test_finding_event_on_the_record`, which asserts the kind
  and did fail under the sabotage (recorded as collateral,
  since it claimed no pair). T07's attribution, by contrast,
  discriminates s6.response_matching (a lines contract).
- `test_schema_contract…test_checker_binding_comes_from_the_frozen_object
  :: s6.schema_binding` — the fixture tests construction
  binding (Checker takes its digest from the frozen object);
  examine()'s binding-divergence facet is discriminated by
  the three ChangedUnderUnchanged fixtures (all EXERCISED).
  No sabotage in the matrix targets Checker construction.
- `test_examiner_g6…test_unresolvable_reference_is_an_error_not_a_flag
  :: s6.g6_resolution` — the sabotage substitutes a synthetic
  event for the missing one, but every downstream use of the
  synthetic event fails, so the error outcome is unchanged:
  the refusal is overdetermined. (The s6.g6_resolution run
  changed nothing.)

**Stage 7 (2)**
- `test_lifecycle…test_collect_unissued_refused ::
  s7.collect_issuance` — with the issuance check neutralised,
  collection proceeds one step and is refused by the
  package-entry check in series ("missing from the package").
  The fixture asserts the refusal, not its reason, so the
  issuance facet is not discriminated; no fixture in the
  suite asserts the issuance-specific refusal. (The
  s7.collect_issuance run changed nothing.)
- `test_lifecycle…test_issuance_never_satisfies_collection_or_verification
  :: s7.package_lookup` — the fixture asserts an inequality
  (state ≠ VERIFIED; no content held). Under the sabotage the
  state becomes COLLECTED_DIGEST_MISMATCH — still not
  VERIFIED — so the assertion holds. The exact-state sibling
  (`test_issued_without_content`) carries the discrimination
  and is EXERCISED.

**Mechanism-level (no fixture discriminates the mechanism)**
- `s2.registry_completeness` — the run changed nothing. Stage
  2's registry-completeness facet is discriminated by no
  fixture alone: the fixtures cited for the verify pipeline
  discriminate the sole-issuer facet (asserting the unissued
  detail exactly), the chain facet, or the whole pipeline
  (under s2.verify_all, exactly the six sole-issuer/chain
  fixtures change). This confirms the pre-build classification
  finding mechanically.
- `s3.receipt_record_presence` — as above: zero changes.
- `s3.output_not_frozen` — no fixture claims it and none
  discriminates it: no Stage 3 test presents a governed value
  absent from the frozen configuration (the private-value
  sabotage uses a frozen field with a wrong value — the
  differing facet). The `values_not_in_frozen_config` refusal
  path is unexercised by the suite.

**Joint-guard fixtures (8 of 10 EXERCISED-JOINT):**
Stage 1's corrupted-reopen (chain ∧ structural), Stage 2's
duplicate-entry (build ∧ close duplicate guards — either alone
still refuses with the identical detail; the conjunction is
the discriminator), Stage 3's post-issuance mutation (facts ∧
coverage), Stage 6's three forged-capability fixtures
(construction token ∧ point-of-use) and unknown-branch causal
control, Stage 7's five-states and exact-gap fixtures
(authentication ∧ digest ∧ package). The two fabricated-receipt
fixtures are the joint NOT-EXERCISED cases above.

**Classification corrections the matrix forced** (inventory
amended, each noted in place): Stage 1's case5 discriminates
the account function only as a whole (its closure has no
account section at all); Stage 4's different-digests replay
discriminates **s4.contract_identity** — the K7 lookup's
*contract* conjunct, a facet no earlier stage had separated —
not the identity conjunct or pinned hash it was presented
under (its input *identity* matches B; only the payload
digest differs, and no field check compares that); Stage 5's
two partial-insertion fixtures exercise the never-landed /
fresh-apply path, not effect recognition; Stage 5's
recognition-per-identity discriminates the identity function;
Stage 6's causal-table agreement / input / model /
checker-defect branches needed three mechanisms this stage
added (regex extraction, the input-defect branch, and the
opposite-direction format_prescribed sabotage) — with them,
each of the four discriminates exactly its one fixture and
nothing else.

## Collateral — every run's unexplained-looking changes, explained

No collateral change is left unexplained. The classes:

- **Whole-function / shared-primitive breadth (by design):**
  s1.account_whole (29 changes — every account fixture is a
  dependent of the whole function), s2.verify_all (6 — exactly
  the sole-issuer and chain fixtures), s7.issuance_lookup
  (30 of 34 — `_issuance_event` is a shared primitive; the
  synthetic-issuance sabotage poisons issuance itself, so the
  run is recorded as necessarily broad, a sabotage-shape
  limitation, not a Step-7-clean run), s5.event_recognition
  (9 — every changed test reads state through the same
  `_operation_events` primitive), s5.identity_determinism
  (11 — a non-deterministic mint breaks the stage's premise
  globally), s5.identity_function (3) and s5.identity_payload
  (2 — multi-slot fixtures and the payload fixtures' own
  identity-equality assertions).
- **Process-global pollution:** s4.registry_immutable (15) —
  with a plain dict, the remapping attack *succeeds* in its
  fixture and corrupts the shared registry for every later
  test in the process. The blast radius is itself the
  demonstration of why the proxy matters.
- **Callable-identity coupling:** s4.construction_binding
  (15) — the sabotage lambda's `implementation_hash` differs
  from the pinned function's, so verdict-issuance assertions
  across the suite move. One sabotage, two coupled quantities
  (dispatch target and callable hash); recorded as such.
- **Single explained cross-effects (each named in the run
  records):** whitespace fixtures whose `_has_content` failure
  lands in the schema list (under s1.account_schema, 2);
  INCOMPLETE-status dependents (under s1.account_status_
  incomplete, 2); the freshness fixture, whose discriminating
  signal *is* the terminal check on the re-read record, and
  the s6 structural fixture's terminal assertion (under
  s1.terminal_check, 2); Stage 3's rebinding scenario, whose
  second half routes through the output gate's digest check
  (under s3.output_digest, 1); the recorded-event fixture
  under coverage (1); Stage 4's registry-attack fixtures,
  whose assertions route through run()'s preservation path
  (under s4.digest_comparison, 4) and the rebinding fixture
  under s4.pinned_hash (1); the crash-window payload fixture's
  honest-retry half (under s5.effect_recognition, 1); the
  finding-event fixture (under s6.format_prescribed, 1 —
  the kind discrimination noted above); T07's attribution
  (under s6.response_matching, 1); the discrepancy-conflict
  fixture (under s6.g6_contradiction, 1); the indeterminate
  fixture's second-terminal-action half (under
  s6.one_resolution, 1); Stage 7's gap-survival fixture,
  whose gap *is* the unauthenticated state (under
  s7.authentication, 1); Stage 7's full-lifecycle and two
  record-discipline fixtures, which assert through
  `package.read_content` itself (under s7.package_lookup, 3).

## Instrument interaction (Stage 4 examinations)

Under 11 of the Stage 4 mechanism runs, one or more of the
three examination fixtures (FX-R60i / FX-R60k / FX-R60l)
changed outcome. These are recorded as **instrument
interaction**, distinct from FAIL and from collateral: an
examination measures the mechanism suites against its own
sabotaged variant of contract.py, so a matrix run that alters
contract.py — or the suites' baseline behaviour — alters the
examination's instrument. Their pair verdicts rest on their
own baseline examinations (SELF-WITNESSED): in the unsabotaged
tree each applies its sabotage and asserts the exact failing
set, and each passes.

## Earlier stages' EVIDENCE SHOWING — re-confirmed or downgraded

- **Stage 1 — RE-CONFIRMED, one narrowing.** Every facet is
  discriminated as claimed except the C6 wrong-type case
  (overdetermined, above). Case5's showing is whole-function
  only. The whitespace term, the anchor facets, the terminal
  check and the reconciliation facets (each of the five
  branches discriminated by at least one fixture) all stand.
- **Stage 2 — DOWNGRADED in one named respect.** The
  registry-completeness facet has no discriminating fixture;
  Stage 2's showing for it rested on whole-pipeline evidence.
  The claim is re-scoped: sole-issuer, chain-in-verify and
  the close facets are re-confirmed exactly; registry
  completeness is **not independently shown by the suite**.
  The duplicate-entry showing is joint-only, as the
  redundancy intends. The FrozenSchema seal showing is
  re-scoped to the conjunction (guard ∧ read-only
  properties), not the guard alone.
- **Stage 3 — DOWNGRADED in two named respects.** (i) The
  recorded-event presence facet is discriminated by no
  fixture; the fabricated-receipt showing belongs to the
  registry lookup, which has no matrix mechanism. (ii) The
  FrozenRun seal showing is re-scoped to the conjunction
  (guard ∧ read-only properties). (iii) A coverage gap with
  no fixture at all: the not-frozen-values facet. Against
  that, the shared chain and terminal facets are the most
  heavily discriminated mechanisms in the programme —
  claimed by fixtures in Stages 3, 5, 6 and 7, EXERCISED in
  every case — and the remaining Stage 3 facets are
  re-confirmed.
- **Stage 4 — RE-CONFIRMED, two corrections.** The FX-R60k
  showing stands, refined: the lookup has two identity
  conjuncts and each is load-bearing for one fixture
  (verdict conjunct — byte-identical copy; contract conjunct
  — identical contents and, solely, different digests). The
  FX-R60l and FX-R60i showings stand. Corrections: the
  different-digests replay was misattributed to
  identity/pinned-hash (above), and the corrupt-flag fixture
  does not exercise the digest comparison (DR-08 shape,
  above) — the comparison's showing rests on the
  wrong-digest fixture alone, which is sufficient and exact.
- **Stage 5 — RE-CONFIRMED, one correction.** The
  completed-state correction (Gate 1 round 1) is
  discriminated exactly (all three divergence fixtures and
  the restart variant EXERCISED). The correction: the two
  partial-insertion fixtures do not exercise effect
  recognition — the recovery showing for a mid-insertion
  crash rests on the orphan-temp / fresh-apply path. Every
  Stage 5 pair is EXERCISED (20/20) after the inventory
  corrections.
- **Stage 6 — RE-CONFIRMED, three qualifications.** (i) The
  point-of-use showing rests on the forged-capability
  fixtures, not the two type-gate fixtures. (ii) The T02
  attribution showing is re-scoped: format_prescribed
  discriminates the finding kind for stated-value cases, and
  the SYSTEM attribution there is overdetermined; T07's
  attribution discriminates response matching. (iii) The
  checker-binding fixture does not discriminate examine()'s
  divergence facet (the ChangedUnderUnchanged fixtures do).
  With Stage 8's three added mechanisms, every causal-table
  branch now has exactly one discriminating fixture.
- **Stage 7 — RE-CONFIRMED, two qualifications.** (i) The
  collect-issuance facet's showing is re-scoped: the refusal
  is overdetermined in series with the package-entry check,
  and no fixture asserts its specific refusal. (ii) The
  issuance-never-satisfies fixture discriminates nothing in
  the matrix (an inequality assertion); the exact-state
  fixtures carry that showing and are EXERCISED. The Gate 1
  correction (anchor provenance) is discriminated exactly:
  pin_constructor 2/2, pin_point_of_use 4/4. The five-state
  lifecycle showing stands (jointly, as built).

## Register disposition

- **DR-08 — ADVANCED.** The historical defect (a fixture
  whose setup bypassed the branch it claimed to test) now has
  a programme-wide mechanical check, and the check found the
  same shape still present in the current suites: Stage 4's
  corrupt-flag fixture does not reach the digest comparison.
  The corrected-shape fixture (wrong digest, no flag)
  discriminates the comparison exactly. The historical R60
  defect remains historical; the *class* is now patrolled.
- **DR-12 — ADVANCED.** The narrow-coverage qualification is
  now measured: 17 NOT-EXERCISED pairs, 2 mechanisms with no
  discriminating fixture, 1 mechanism with no fixture at all,
  each named above, and every stage's showing re-scoped to
  what its fixtures actually discriminate. Coverage claims in
  Stages 1–7 stand exactly where this record leaves them —
  no wider.

## Boundaries

Counts are builder-run (the orchestrator re-runs them); the
matrix's witness is the unittest result stream in scratch
copies, not an independent execution by the examiner. The
matrix neutralises one mechanism at a time (plus the stated
joint runs); interactions between two simultaneously-removed
guards beyond the joint-guard groups are out of scope. Three
mechanisms added by this stage (Stage 6 extraction,
input-defect branch, opposite-direction prescribed) and one
facet separated by it (Stage 4 contract identity) are part of
Stage 8's own build, recorded as such. Sabotage shapes are
single-direction per mechanism except where a second
direction is listed as its own mechanism. The real trees were
never patched: all sabotage ran in scratch copies, and after
the matrix all seven suites re-run green in their real trees
(68 / 27 / 38 / 36 / 30 / 54 / 34).

## Correction round 1 — Gate 1 return

**The ruling answered** (VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md,
shelf commit 5107157c039fc64a53f9831d5f20094f227797af, on the
package @ a1a3c290): Gate 1 FAIL, one targeted correction. The
substantive fixture analysis is accepted as submitted — the
Stage 2 and Stage 3 downgrades, the Stage 3 coverage gap, the
Stage 4 corrections, and the named 17 NOT-EXERCISED pairs —
subject to this correction and the regenerated matrix. The
blocking finding is in the measurement machinery, not the
analysis: the patrol's own log could convert an unobserved
fixture into discrimination evidence.

**The fail-open shape.** Three composed defects in
`matrix.py` as submitted. (1) `run_suite()` invoked
`witness_run.py`, parsed whatever JSON lines it happened to
receive, and discarded the subprocess return code; it never
validated the emitted summary, the expected test count, or
the completeness of the outcome set. (2) `run_one()`
explicitly converted every baseline test absent from a
sabotage run's outcomes into a change with
`under_sabotage: "MISSING"`. (3) `classify()` treated any
changed claimed fixture as EXERCISED, without distinguishing
an assertion failure from MISSING, ERROR, skipped, or any
other non-ok result. Composed: if a runner process crashed
before emitting outcomes, or a collection failure prevented
a test from being observed, the baseline fixtures became
MISSING, and any of them claiming the neutralised mechanism
was classified EXERCISED. Absence of evidence was credited
as discrimination — precisely the false assurance this stage
exists to prevent, in the stage's own instrument. (The
submitted matrix itself contained no MISSING change and no
witness anomaly; the defect was latent, in the code path,
not realised in the submitted numbers. That is luck about
the runs that happened to execute, not a property of the
machinery, and the correction treats it accordingly.)

**The correction** (`matrix.py`; `witness_run.py` and
`coverage.py` needed no change — the runner's output already
carries everything validation requires, and the coverage
accountant consumes the separate Test 8 witness log, not
matrix runs). Every witness-runner execution is now
validated by `validate_run_output()` before anything is
classified from it: the runner must have exited cleanly
(return code preserved; a timeout is an abnormal exit);
stdout must parse line by line as JSON records (a malformed
or unrecognised line is an anomaly); test IDs must be unique
(each duplicate named); every outcome value must be one of
ok / FAIL / ERROR / skipped; there must be exactly one
summary record, whose test count equals the number of
outcome records and whose outcome tally equals the records'
own tally; and the observed test-ID set must equal the
baseline test-ID set for that suite exactly — every missing
and every unexpected ID is named. Any defect makes the run
INVALID: `run_one()` records the validation per suite, the
run's `valid` flag, and its `invalid_reasons`, and preserves
the raw diagnostic (return code, anomaly list, stderr and
stdout tails) in the run record. The MISSING synthesis is
deleted — an absent outcome is now an anomaly, never a
change. `classify()` fails closed on top of that: a run
record that is invalid — or that carries no validation at
all, as a pre-correction result file would not — yields no
pair verdicts, no collateral, and no joint verdicts; its
claimed pairs are recorded INVALID-RUN and the run is named,
with its reasons and affected pairs, in
`summary["invalid_runs"]`.

**The outcome policy, stated explicitly** (the ruling's
fourth requirement). In a validated, complete run, a claimed
pair is credited EXERCISED when the fixture's observed
outcome is FAIL or ERROR. Both are terminal outcomes in
which the fixture was observed to execute and its baseline
behaviour did not occur. The ERROR half of that policy is a
judgement, and it is recorded here rather than left silent:
in these suites the fixtures predominantly assert controlled
refusals, and when the guard is removed, the guarded input
characteristically flows past the missing guard into code
that assumes the guard ran, raising an uncontrolled
exception instead of producing the asserted refusal.
Four of the fifteen ERROR-earned credits were sampled
first-hand against their sabotage runs before this policy
was adopted, and all four have exactly that shape:
Stage 1's whitespace fixtures (the expected rejection
diagnostic is never produced; the fixture's lookup of it
raises StopIteration); Stage 2's forged-canonical-events
fixture (a refusal is raised, but — the sole-issuer facet
being gone — without the `unissued_provenance_events`
details the fixture asserts; KeyError inside the test);
Stage 3's consume-unknown fixture (the unknown governed
value passes the missing check and raises KeyError inside
`consume()` itself); Stage 4's missing-implementation-hash
fixture (the malformed verdict reaches the comparison that
indexes the very field the removed check existed to
guarantee; KeyError in `validate_verdict`). None of the
four is fixture-plumbing breakage or a collection failure.
A "skipped" outcome never credits: the fixture abstained
from executing its assertions, so the pair is INDETERMINATE
and the abstention is recorded as a witness anomaly. A
missing outcome cannot occur in a valid run at all. And the
distinction the ruling demanded is carried in the record,
not just the policy: `summary["pair_evidence"]` names the
earning outcome of every credited pair, and
`summary["exercised_by_outcome"]` totals them — FAIL-earned
and ERROR-earned credits are never silently merged.

**Regression tests** (`tests/test_runner_validation.py`, 20
new tests; the stage's suite is now 31). Validation:
a healthy run is valid; an ERROR outcome is a valid
observation; a crashed runner (nonzero exit, no output);
a runner exiting before emitting any outcomes; a partial
outcome set with an internally consistent summary (still
invalid — completeness is against the expected set, not the
summary's own claim); a duplicate test ID; a malformed
output line; a missing summary; a duplicate summary;
a summary test-count mismatch; a summary tally mismatch;
an invalid outcome value; an unexpected test ID — each
asserted invalid, with the anomaly named. Classification:
an invalid run containing a FAIL change for its claimed
fixture credits nothing (the pair is INVALID-RUN, the run
named, zero exercised-by-outcome); an unvalidated run record
credits nothing; a valid run's FAIL credits EXERCISED with
FAIL evidence; a valid run's ERROR credits EXERCISED with
ERROR evidence; a valid run's skipped change credits
nothing (INDETERMINATE, anomaly recorded); an invalid joint
run gives no joint verdict. Plus one end-to-end check that a
healthy `run_one` is valid and carries its suite validation.
The pre-existing subTest regression and the unknown-ID
anomaly handling in `classify()` remain intact (the latter
is now defence in depth behind run validation).

**Regeneration and the diff, stated exactly.** The full
matrix was regenerated with the corrected machinery (88
mechanism runs + 6 joint runs), and FIXTURE-INVENTORY.md was
regenerated from the corrected summary. Every one of the 96
regenerated runs validated clean: zero invalid runs, zero
witness anomalies. The pair classifications are IDENTICAL
to the submitted ones — the diff over all 217 pairs is
empty: EXERCISED 189, JOINT-ONLY 7, SELF-WITNESSED 4,
NOT-EXERCISED 17, every pair with the same verdict in both
generations; the joint-fixture verdicts, the collateral
record, and the instrument-interaction record are likewise
identical, run for run. The credited pairs' earning outcomes
are now recorded: of the 196 credited pairs (189 EXERCISED +
7 JOINT-ONLY), 181 are FAIL-earned and 15 are ERROR-earned.
One record-level difference, named rather than smoothed:
the regenerated summary carries 94 run records against the
submitted 96. The two absent records are joint runs —
`joint-s4_identity_check+s4_pinned_hash` and
`joint-s6_format_prescribed+s6_response_matching` — for
target groups whose fixtures the FINAL inventory classifies
as guard fixtures with single targets, not joint-guard
fixtures: during the original build those fixtures were
reclassified after their joint runs had executed (the Stage
4 replay fixture's inventory note records "two classification
attempts"; its discriminating facet is the single mechanism
s4.contract_identity, and the Stage 6 causal-table controls
resolve to s6.extraction, s6.input_defect_branch and
s6.format_prescribed respectively). In the submitted summary
those runs already contributed no verdict — `classify()`
filtered joint verdicts to current joint-guard fixtures —
and every affected fixture's pair verdict is EXERCISED via
its single-mechanism run in both generations. Their stale
run files were removed from `results/`; reclassifying from
the on-disk records now reproduces the regenerated summary
exactly. So the correction changes no finding: it removes
the machinery path by which a future incomplete run could
have manufactured one.

**Counts after correction.** Stage 8 suite: 31/31 (the 11
prior tests with unchanged outcomes, plus 20 new).
Regressions in the real trees: Stage 1, 68/68; Stage 2,
27/27; Stage 3, 38/38; Stage 4, 36/36; Stage 5, 30/30;
Stage 6, 54/54; Stage 7, 34/34. `stage1/`–`stage7/`
unmodified. The register disposition is unchanged by this
round: DR-08 and DR-12 await the examiner's re-examination
of the corrected package, which has not yet occurred. The
collateral-heavy sabotage shapes named in the Boundaries
section remain limitations of those sabotage designs, as
the ruling notes they must.

## Correction round 2 — Gate 1 return

**The ruling answered** (VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md,
shelf commit c352207af85d9d58002d16969fabb57b265ef6c7, on the
package @ 61587a35): Gate 1 FAIL, one narrow validator
correction. Round 1's correction is accepted — validation
before classification, invalid runs contributing nothing,
the outcome policy explicit, the regenerated pair matrix
unchanged with the two stale joint-run records accounted
for. Everything substantive stands. The remaining defect is
in the validator itself, at the record-shape boundary.

**The defect.** `validate_run_output()` parsed JSON syntax
but assumed every `test_id` was hashable and sortable. A
syntactically valid but schema-invalid record such as
`{"test_id": [], "outcome": "FAIL"}` raised `TypeError` at
dictionary membership/insertion, because the ID is
unhashable; a hashable non-string ID (an integer) mixed
with string IDs raised `TypeError` when the unexpected-ID
difference was sorted. Both escaped the validator's stated
contract — malformed records become named anomalies and the
run is recorded invalid — and, since `run_suite()` caught
nothing, aborted the matrix run instead. Reproduced before
the fix, all as `TypeError`: a list-valued test_id
(unhashable), an object-valued test_id (unhashable), an
integer test_id alongside an unexpected string ID (mixed
sort), and — the neighbouring field, below — a list-valued
outcome.

**The correction** (`matrix.py`, `validate_run_output()`
only; `witness_run.py` and `coverage.py` unchanged). Field
types are now validated before any use that assumes them. A
`test_id` that is not a non-empty string is a malformed
record: it is named in the anomaly list (`malformed test id
<value> on line <n> — not a string test id`) and nothing
from the record is stored, so the ID never reaches
membership, insertion, or sorting; exact membership in the
expected set continues to be enforced by the set comparison
for string IDs. The neighbouring fields were checked with
the same suspicion, and one further crash was found and
fixed: an `outcome` that is not a string (a list or object)
was stored by round 1's validator and raised `TypeError`
when the summary tally used it as a dictionary key — it is
now named as an invalid outcome and the record is not
stored. (String outcomes keep round 1's behaviour exactly:
an out-of-vocabulary string is named and stored, so the
tally semantics are unchanged.) The remaining fields were
audited and need no change: the summary's `tests`/`counts`
are only ever compared with `!=`, which no JSON value can
make raise, and a non-dict summary is already refused by
the isinstance check. No exception escapes
`validate_run_output()` for any JSON value shape a record
can carry.

**Regression tests** (`tests/test_runner_validation.py`,
five new). Both of the ruling's named shapes: a list-valued
test_id and an object-valued test_id each produce the named
malformed-ID anomaly and `None` outcomes; an integer
test_id mixed among string IDs (with an unexpected string
ID, the sorting-crash shape) produces the malformed-ID
anomaly naming the integer and the unexpected-ID anomaly,
no exception. The neighbouring field: a list-valued outcome
produces the invalid-outcome anomaly, no exception. And the
end-to-end proof: a crafted witness stream carrying every
Stage 1 baseline ID plus one list-valued test_id record
travels the real path — `run_one()` (scratch copy, patching,
the runner subprocess replaced by a fake returning the
crafted stream) records the run invalid with the malformed
ID named in its reasons and no changes, and `classify()`
then records the guard pair INVALID-RUN, names the run in
`invalid_runs` with the pair among its affected pairs, and
awards no pair evidence and no coverage credit.

**The matrix check.** The fix changes validator behaviour
only for malformed records; no real witness run emits one.
Classification was re-run from the on-disk run records with
the corrected code and diffed against the submitted
summary: all 217 pair classifications identical — EXERCISED
189, JOINT-ONLY 7, SELF-WITNESSED 4, NOT-EXERCISED 17 — and
the joint verdicts, collateral, instrument-interaction
records, pair evidence and exercised-by-outcome tallies are
identical, with zero invalid runs and zero witness
anomalies in both. The matrix was therefore not regenerated;
per the ruling, the existing 217-pair findings stand on the
corrected records.

**Counts after correction.** Stage 8: 36/36 (the 31 prior
tests with unchanged outcomes, plus five new). Regressions:
Stage 1, 68/68; Stage 2, 27/27; Stage 3, 38/38; Stage 4,
36/36; Stage 5, 30/30; Stage 6, 54/54; Stage 7, 34/34.
`stage1/`–`stage7/` unmodified. The register disposition is
unchanged by this round: DR-08 and DR-12 await the
examiner's re-examination of the corrected package, which
has not yet occurred.
