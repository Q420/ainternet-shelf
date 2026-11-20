# Duenna Stage 3 — Configuration and Subject Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 3; ID-SYSTEM-DESIGN-DRAFT-V3.md (K1, K2, K3, G1, G5)
Build location: ~/workspace/duenna-fix/stage3/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 3 built from the plan, after Stage 2 cleared Gate 1)

## Status of this report

The Stage 3 harness is built and its full test suite passes
(23/23, below), with the Stage 1 (68/68) and Stage 2 (27/27)
suites green as regression. This report is EVIDENCE for the
examiner, not a verdict: a builder's green run establishes that
the mechanism behaves as specified on the exercised cases;
whether Stage 3 passes is the examiner's determination (Gate 1
discipline), not this report's. Nothing here declares Stage 3
complete.

## What was built

- `config.py` — the one configuration object (K3).
  `freeze_config` validates a draft and returns a `FrozenConfig`:
  immutable after construction, mapping sections handed out as
  fresh copies, its identity one digest (SHA-256 over the
  canonical encoding of the whole validated draft). The draft
  carries the subject pin; the subject as named on each
  configuration surface (`driver` and `adapter`, the surfaces
  DR-03 names) as INPUTS to the one object; the governed values;
  derivations and policy; the frozen run policy
  (`on_subject_conflict`: `INVALIDATE_RUN` or `REFUSE_CAPTURE`);
  the tree set (bound by its own digest); and the pinned schema
  digest — Stage 2's frozen schema enters the configuration by
  digest (G5's schema anchor), not by a second copy of its
  sections. `derived_limit_problems` is G1's policy check on
  derived limits: for every limit the policy names as derived,
  the derivation's stated requirement is RECOMPUTED from its
  recorded inputs under the named formula
  (`reasoning_envelope`: ceil(max_reasoning_tokens /
  min_throughput_tps)), and the limit's value must meet the
  recomputed requirement. A derivation that does not recompute,
  a missing derivation, and a value below the requirement each
  fail, separately named. A written rationale alone does not
  pass — no field of a derivation is read except formula,
  inputs, and the stated requirement the check verifies.
- `binder.py` — the BINDER: run identity (K1), subject
  verification (K2), the freeze gate (G1). The run identity is
  minted at freeze-begin and recorded; `RUN_STARTED` is
  appended only on a successful freeze, binding the three
  digests (configuration, verified subject, tree set). A
  refused freeze is recorded under the run identity as a
  `FREEZE_REFUSED` governance record — never a scored subject
  outcome. G1's checks, in order: (0) the record's chain is
  recomputed over the events as they stand, and a chain failure
  refuses by raised exception ONLY, appending nothing (Stage
  2's correction-round-3 discipline, carried into this stage);
  (1) draft structure; (2) surface consistency — the pin and
  every surface must name the same subject; (3) subject
  verification — the lane is called with the pin, its response
  recorded as a `SUBJECT_VERIFICATION` event, and the subject
  identity is minted from that recorded response (asserted pin,
  served identity, endpoint, verification event digest), never
  from the pin alone; a pin/served mismatch refuses; (4) the
  derived-limits policy check, recorded as a `POLICY_CHECK`
  event either way. Attribution of every subject mismatch is
  the single class UNKNOWN (K2).
- `access.py` — the controlled configuration access path (K3
  consumption by positive proof). A `ConfigAccess` exists only
  for a `FrozenRun`. `consume` supplies the FROZEN object's
  values for a declared set of names to one component
  invocation — the caller names values, it never supplies
  them — and issues a consumption receipt recorded as a
  `CONSUMPTION_RECEIPT` event, registered by the event digest.
  Naming a value the frozen configuration does not hold is
  refused: the path has no component-local defaults (the
  supply-side half of K3(a)).
- `admission.py` — the F5 enforcement edges.
  - *Capture gate (K2 consistency).* The gate holds the lane
    and makes each capture's call itself, recording the served
    identity returned for THAT call (`CAPTURE_SERVED`). A
    capture therefore has no identity to present and none to
    borrow: `admit_capture` takes only the capture's own name
    (a test asserts the signature). Served identity equal to
    the run's verified identity admits the capture under its
    own identity; a mismatch appends the `SUBJECT_CONFLICT`
    record FIRST, then refuses the capture, and — per the
    frozen run policy — invalidates the run's subject-dependent
    execution (`RUN_INVALIDATED`) or refuses the capture and
    its dependents only.
  - *Output gate (K3(c) + G5).* A governed output is admitted
    only on positive consumption proof, every anchor obtained
    independently of the presenter: the receipt must exist in
    the access path's registry (a fabricated receipt id does
    not exist, however plausible), match the output's
    component and invocation, and have been issued under the
    frozen configuration; the output's quoted configuration
    digest must equal the FROZEN OBJECT's digest (the quote is
    checked, never believed); every value the output used must
    be a governed value at its frozen value — a private value
    is refused and preserved as a `CONFIG_CONFLICT` record;
    the receipt must cover every value used; every capture the
    output depends on must have been admitted under its own
    identity; a subject-dependent output of an invalidated run
    is refused.
- `tests/` — the full suite below. Stage 1's record is
  imported, not modified; Stage 2's schema is imported by the
  tests only, for its digest (the configuration binds it by
  that digest). `stage1/` and `stage2/` are untouched.

## The governing rule, as implemented

REFUSAL, NOT EITHER/OR. In every mismatch case both obligations
hold, and the code paths are built so they cannot come apart:
the conflict record is appended before enforcement acts, and
enforcement acts in the same operation —

- the mismatched capture's admission is refused;
- any governed output depending on it is refused;
- the run's subject-dependent execution is refused or
  invalidated per the frozen run policy;
- a conflict record never substitutes for enforcement (a
  recorded conflict admits nothing), and enforcement never
  erases the record (the conflict stands whatever the policy);
- no capture may borrow another capture's verified identity
  (there is no path by which it could present one).

## Test evidence

Full suite run 2026-11-20:

Command: `python3 -m unittest discover -s tests -v` (from stage3/)

Result: **Ran 23 tests — OK (23 passed, 0 failed)**

Per file:
- tests/test_freeze.py — 7 tests, all ok
- tests/test_access_admission.py — 9 tests, all ok
- tests/test_stage3_sabotage.py — 7 tests, all ok

Regression runs 2026-11-20:

- Stage 1 (from stage1/): **Ran 68 tests — OK** — no regression;
  stage1/ was not modified.
- Stage 2 (from stage2/): **Ran 27 tests — OK** — no regression;
  stage2/ was not modified.

## Positive controls

A gate that refused everything would "pass" every sabotage
while proving nothing, so the positive controls are first-class:

1. **A consistent configuration freezes and binds** —
   test_successful_freeze_binds_the_three_identities — PASS.
   RUN_STARTED carries the configuration digest, the verified
   subject digest and the tree-set digest of the frozen
   objects; CONFIG_FROZEN carries the pinned schema digest
   (Stage 2's TEST_SCHEMA digest); the verification record
   binds the SERVED identity; verification, policy check and
   freeze all precede the start on the record.
2. **A recorded, policy-checked constant passes** —
   test_recorded_constant_limit_passes_policy_check — PASS.
   DR-21's distinction exercised directly: the 600-second
   limit is a configuration value whose derivation recomputes
   (required 328) and whose value meets it; the POLICY_CHECK
   event records `passed: true`. The defect was never
   "constant" — it was a private constant the envelope never
   reached.
3. **Consumption is evidenced by receipts** —
   test_consume_issues_receipt_with_frozen_values — PASS. The
   receipt carries the frozen values (not caller-supplied
   ones), is registered by its record event digest, and the
   event is on the record under the run identity.
4. **Output admitted on positive consumption proof** —
   test_output_admitted_on_positive_consumption_proof —
   PASS.
5. **A capture is admitted under its own identity, and an
   output may depend on it** —
   test_capture_admitted_and_output_may_depend_on_it — PASS.
   The capture's own lane call served the verified identity;
   the admission names that capture and that identity.

## Per-sabotage results — the plan's Test 3, each result separate

Each sabotage was presented to the real paths (freeze, access,
capture gate, output gate — never a projection), and each test
asserts BOTH halves of the governing rule: the conflict record
exists, AND enforcement refused. They are reported separately
because they establish different properties.

1. **(a) Contradictory driver/adapter subject configurations**
   — test_contradictory_driver_adapter_configurations —
   REFUSED, both halves. The draft names `lane/model-a` on the
   driver surface and `lane/model-b` on the adapter surface
   (DR-03's exact mechanism: subject identity independently
   represented in multiple locations). *Closure half:* one
   `SUBJECT_CONFLICT` record, kind `configuration_surfaces`,
   naming the pin, both surfaces, and attribution UNKNOWN,
   under the minted run identity. *Execution half:*
   `FreezeRefused` raised; `FREEZE_REFUSED` recorded under the
   same run identity; no `CONFIG_FROZEN`, no `RUN_STARTED` —
   there is no run whose execution could proceed.
2. **(b) A component quoting the canonical hash while using a
   private value** —
   test_quoting_canonical_hash_while_using_private_value —
   REFUSED, both halves. The output quotes the frozen
   configuration's digest exactly and references a genuine
   receipt covering both values it used — but the
   `timeout_seconds` it actually used is a private 120, not
   the frozen 600 (DR-21's number arriving by the component's
   private path). The gate compares the used values against
   the FROZEN OBJECT, not the quote. *Closure half:* one
   `CONFIG_CONFLICT` record, kind `governed_value_mismatch`,
   naming the field with its frozen value (600) and used
   value (120). *Execution half:* `OutputRefused` raised
   naming `timeout_seconds` under
   `values_differ_from_frozen_config`; `OUTPUT_REFUSED`
   recorded; the output is not admitted. Companion —
   test_fabricated_receipt_quoting_canonical_hash — REFUSED:
   quote correct, values canonical, but the receipt id was
   never issued; refused under `receipt_not_issued`. A hash
   quote is not consumption proof.
3. **(c) Preflight verifies one model, a later capture routed
   to another** —
   test_capture_routed_to_another_model_invalidates_run —
   REFUSED, both halves, under the frozen `INVALIDATE_RUN`
   policy. The preflight lane call serves `lane/model-a`; the
   capture's own call is routed to `lane/model-b`. *Closure
   half:* one `SUBJECT_CONFLICT` record, kind
   `capture_served_mismatch`, naming the capture, the expected
   (verified) identity, the identity its own call actually
   served, attribution UNKNOWN. *Execution half:* the
   capture's admission refused (`CAPTURE_REFUSED` recorded;
   the capture is not in the admitted registry); the run
   invalidated per the frozen policy (`RUN_INVALIDATED`
   recorded, cause named); an output depending on the refused
   capture refused under `captures_not_admitted`; any
   subject-dependent output refused under `run_invalidated`.
   The refusal is scoped, not blanket: a governed output that
   is NOT subject-dependent, on a valid receipt, still admits
   in the same run. Companion —
   test_capture_gate_has_no_identity_to_borrow — PASS as a
   structural assertion: `admit_capture`'s signature is
   `(self, capture_id)`; there is no parameter by which a
   served identity or another capture's admission could be
   presented. Companion —
   test_refuse_capture_policy_scopes_the_refusal — REFUSED,
   both halves, under the frozen `REFUSE_CAPTURE` policy: the
   mismatched capture's conflict is recorded and its
   admission refused; the run is NOT invalidated; a capture
   whose own call serves the verified identity admits and an
   output may depend on it; an output depending on the
   REFUSED capture is still refused.
4. **(d) Served identity differing from the pin** —
   test_served_identity_differing_from_the_pin — REFUSED,
   both halves (DR-20's shape: the pin asserted from the
   catalogue, the lane serving something else). *Closure
   half:* the `SUBJECT_VERIFICATION` record stands naming the
   served identity as served (`lane/model-b`), and one
   `SUBJECT_CONFLICT` record, kind `pin_served_mismatch`,
   naming asserted pin and served identity, attribution
   UNKNOWN. *Execution half:* `FreezeRefused` raised at the
   subject-verification stage; `FREEZE_REFUSED` recorded; no
   `CONFIG_FROZEN`, no `RUN_STARTED`. A pin is an assertion,
   not a verification — an unverified pin cannot bind a run.

Admission mechanics additionally covered in
tests/test_access_admission.py, each refused with its named
reason: an output with no receipt at all; an output with a
fabricated receipt id; a receipt issued to a different
invocation; a receipt that does not cover every value used; an
output whose quoted digest differs from the frozen object's.
And in tests/test_freeze.py: a structurally unusable draft
refused and recorded under its run identity; a derived limit
below its recomputed requirement refused (the 120-second value
against the 328-second requirement — DR-21's established
shape); a derivation whose stated requirement does not
recompute refused; a derived limit with no derivation refused;
and a freeze attempted on a corrupted record refused by
exception only, the corrupted file asserted byte-identical
afterwards.

## Register effect

- **DR-03** (subject identity has conflicting representations):
  the mechanism specified for it — K1's run identity binding
  one K3 configuration and one K2 verified subject, G1's
  surface-consistency and verification checks — is built and
  demonstrated, including against DR-03's exact failure mode
  (driver and adapter surfaces naming different subjects).
  The register's open sub-question (where the wrong
  configuration entered the live path) is a production-history
  question this harness does not address and does not claim
  to.
- **DR-20** (a pin is an assertion, not a verification): K2's
  verification — the subject identity minted from the lane's
  recorded response, a pin/served mismatch refusing the run
  at G1, and per-capture served identity under the
  consistency condition — is built and demonstrated,
  including the evidence note's carried-in recommendation
  (verification of the pin before firing) as G1's step 3.
- **DR-21 (established part)** (a fixed transport limit
  applied without consulting the run's reasoning envelope):
  K3's obligation — every transport limit a configuration
  value carrying its derivation, G1 evaluating derived limits
  against the objective constraint recorded in the
  configuration — is built and demonstrated: the limit is
  frozen in the one configuration object, reaches components
  only through the access path, and the policy check
  recomputes the requirement from the envelope inputs.
  DR-21's decisive cause (lane latency vs timeout length)
  remains NOT established, exactly as the register records;
  nothing in this stage separates them or claims to.

On the plan's terms, DR-03, DR-20 and DR-21 (established part)
are advanced on demonstration — subject to the examiner's
independent examination of this evidence, which has not yet
occurred. As with the earlier stages, this discharges the
mechanisms in the harness; the production paths
(pilot_driver.py's duplicated subject configuration, the
adapter's private timeout) are not rewritten — production
integration belongs to the later stages.

## Boundaries

- The serving lane is a caller-supplied callable — the
  harness's stand-in for a live lane, in the fixture class of
  Stage 1's TEST authority. The verification mechanism (obtain
  the lane's response, record it, bind identity to it, refuse
  on mismatch) is exercised for real; no network call is made
  and no claim about any actual lane, endpoint or model is
  established. DR-20's live model-list evidence is production
  history, not re-derived here.
- In-process, local, synchronous only. Deterministic: run
  identities derive from the record's contents; no wall clock
  is read (a verification's "time" is its position in the
  record's chain).
- The run's invalidation state is held by the `FrozenRun`
  object in-process and recorded on the record as
  `RUN_INVALIDATED`; a fresh process re-deriving run state
  from the record alone is not part of this stage's claim.
- The schema enters the configuration by pinned digest only
  (G5's schema anchor). This stage does not re-examine Stage
  2's schema mechanism; the digest in the test fixture is
  Stage 2's TEST_SCHEMA digest.
- One derivation formula (`reasoning_envelope`) is
  implemented — the one DR-21's established part turns on.
  Other formulas are policy the configuration could name but
  this harness does not implement; an unknown formula fails
  the policy check (it does not recompute), it never passes
  silently.
- The record's own integrity guarantees are Stage 1's, with
  Stage 1's stated limits (chain verification does not defeat
  a wholesale re-chained rewrite; that is the external
  anchor's scope). Stage 3 adds the freeze-time chain check
  and otherwise builds on the record as opened — Stage 1's
  constructor already refuses to open a corrupted record.

## Correction round 1 — Gate 1 return

The examiner's Gate 1 examination of the package at shelf
commit `3d631161` established two boundary defects — specific
failures of the authority boundaries this stage exists to
establish, not objections to the overall design. Both are
corrected here; nothing else in the stage changed.

**Defect 1 — the receipt was mutable after issuance.** As
first built, a `Receipt`'s fields were publicly writable and
its `values` was the live dict the output gate later read: a
caller could add a value to `receipt.values` after issuance
and present an output using that value, and the gate could
accept it as covered — although the recorded
`CONSUMPTION_RECEIPT` event never recorded it. The positive-
proof guarantee was broken at the receipt boundary.
Correction, in two parts. (i) `Receipt` is now immutable in
the same sense as `FrozenConfig`: attribute assignment after
issuance raises, and the values are held as canonical JSON
and handed out as a fresh dict. (ii) The output gate no longer
trusts the live object at all for the facts it checks: it
reads the recorded `CONSUMPTION_RECEIPT` event back from the
record (by the registry's event digest) and establishes
component, invocation, configuration and covered values from
the EVENT. A registry object that disagrees with its recorded
event is refused (`receipt_disagrees_with_recorded_event`),
and a receipt whose event is not on the record is refused
(`receipt_event_not_on_record`); the refusal is recorded as
before (`OUTPUT_REFUSED`) — the record here is healthy, so
recording is sound.

**Defect 2 — the frozen run could be rebound.** As first
built, `FrozenRun` exposed writable `config`, `run_id` and
`subject_record` attributes: replacing `run.config` after
freeze changed what `run.config_digest` and the access path
treated as canonical, while the recorded `RUN_STARTED` event
still bound the original configuration. The frozen object was
immutable; the capability holding it was not. Correction:
`FrozenRun` is now immutable in the same sense — attributes
are set once at construction, assignment afterwards raises;
`config_digest` is the value CAPTURED at freeze (the digest
bound in `RUN_STARTED`), not recomputed from a replaceable
attribute; the subject record is held as canonical JSON,
handed out as a fresh dict, with its digest and served
identity likewise captured. The one legitimate post-freeze
transition, invalidation, now goes through the run's own
`_invalidate` method, called by the capture gate where it
records `RUN_INVALIDATED`; no other post-freeze assignment
exists in the stage.

**New sabotage results — listed separately.**

- (e) Post-issuance receipt mutation. Field assignment on an
  issued receipt raises (`AttributeError`); adding a value to
  the handed-out values dict changes only that copy. An
  output using the "added" value (`timeout_seconds`, never
  recorded on the receipt's event) is REFUSED —
  `values_not_covered_by_receipt: ["timeout_seconds"]` — with
  the refusal recorded. A white-box companion forces the live
  object past its frozen surface so it claims coverage its
  event never granted: REFUSED on
  `receipt_disagrees_with_recorded_event`, coverage still
  established from the recorded event.
- (f) FrozenRun rebinding. Replacing `run.config`, `run_id`
  or `subject_record` after freeze raises (`AttributeError`).
  `run.config_digest` still equals the digest bound in
  `RUN_STARTED`; the access path still serves the ORIGINAL
  frozen values (temperature 0, not the rebound object's 1);
  an output quoting the rebound configuration's digest is
  REFUSED (`config_digest_mismatch`, quoted vs the bound
  digest), with the refusal recorded.

**Counts after correction.** Stage 3: 26/26 (the 23 original
tests with unchanged outcomes, plus (e) ×2 and (f)). Stage 1
regression: 68/68. Stage 2 regression: 27/27. The register
disposition is unchanged by this round: DR-03, DR-20 and
DR-21 (established part) remain advanced on demonstration,
subject to the examiner's re-examination of the corrected
package — which has not yet occurred.

## Correction round 2 — Gate 1 return

The examiner's re-examination of the round-1 package (verdict
`VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md`, shelf commit
`525991a0`) confirmed both round-1 corrections hold in the
public paths examined — the frozen run retains its freeze-time
identity, and receipt coverage is established from the recorded
event. ONE integrity boundary remained, and it is corrected
here. Nothing else in the stage changed.

**The defect.** `OutputGate._recorded_receipt_body()` read the
record and trusted an event whose stored digest matched the
receipt id. It did not verify the record's CURRENT chain.
Stage 1's `read_all()` is a raw read: the chain had been
verified at the freeze, but the record could have changed
since. Output admission could therefore trust receipt evidence
without proving the current record intact — and could append
an admission or refusal using the record object's stale
in-memory chain head. The module's own docstring carried the
flawed assumption ("verified at open... every append extends
that chain"); it has been replaced with the discipline below.

**The correction — the chain-integrity discipline Stage 2 and
the freeze path already enforce, now at both F5 edges.** In
`admit_output`, before any receipt evidence is read and before
anything is appended, the gate recomputes the record's current
chain (`verify_chain` over `read_all()`). On integrity failure
it raises `OutputRefused` carrying
`record_chain_verification_failed` with the first bad seq and
appends NOTHING — not the admission, and not the refusal
either: a refusal must never mutate the record whose integrity
just failed. On a verified chain, the receipt event is read
from the very snapshot that was verified (the verified events
are passed to `_recorded_receipt_body`), and every existing
check, refusal reason and recorded refusal behaves exactly as
before.

**The capture gate — finding.** It shares the flaw's write
half. `CaptureGate` reads no record evidence for its decision
(its anchors are the lane's live response and the frozen run's
captured values), but it appends the served record, conflicts,
invalidations, admissions and refusals onto the same record,
trusting the record object's in-memory head — an append onto a
record changed since the freeze would extend corruption with
a stale head. The same rule now applies at its head: the
current chain is verified before the lane call and any append;
on failure it raises `CaptureRefused` carrying
`record_chain_verification_failed` and appends nothing.

**New tamper results — listed separately.** Each tampers with
the record on disk through its real persistence path (the
JSONL file) after a healthy freeze and a genuinely issued
receipt, and asserts the record file BYTE-IDENTICAL after the
refused attempt.

- (g) Body edited, stored digest retained. The
  `SUBJECT_VERIFICATION` event's body is edited on disk (its
  endpoint replaced) with its digest retained — an event the
  output gate never itself inspects, so no cross-check stands
  between the gate and the broken chain. Admission of an
  otherwise valid output is REFUSED, carrying
  `record_chain_verification_failed: 2` (the tampered event's
  seq); no `OUTPUT_ADMITTED` and no `OUTPUT_REFUSED` is
  appended; the file is byte-identical to its tampered state.
- (g-companion) A middle event deleted. The `POLICY_CHECK`
  event is removed from the file. (Deleting the LAST event
  would only truncate the chain to a still-valid prefix — the
  wholesale-rewrite class Stage 1 assigns to the external
  anchor; a middle deletion is what recomputation detects.)
  Admission is REFUSED, carrying
  `record_chain_verification_failed: 4` (the seq of the event
  that followed the gap); nothing is appended; the file is
  byte-identical.
- (g-capture) The capture gate on the body-edited record.
  `admit_capture` raises `CaptureRefused` carrying
  `record_chain_verification_failed: 2`; nothing is appended;
  the file is byte-identical; the capture is not admitted.

**Countercheck.** In a scratch copy with both gates' chain
checks neutralised (the pre-correction behaviour), exactly
the three (g) tests fail and the other 26 pass — the new
assertions bite on precisely the corrected defect.

**Counts after correction.** Stage 3: 29/29 (the 26 prior
tests with unchanged outcomes, plus (g) ×3). Stage 1
regression: 68/68. Stage 2 regression: 27/27. `stage1/` and
`stage2/` unmodified. The register disposition is unchanged
by this round: DR-03, DR-20 and DR-21 (established part)
remain advanced on demonstration, subject to the examiner's
re-examination of the corrected package — which has not yet
occurred.

## Correction round 3 — Gate 1 return

**The ruling answered** (VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md,
shelf commit 6f9d6048622f45eacc31079bc858b9391e2602de): the
round-2 gate corrections stand; the one remaining requirement
is the seam the round-2 submission's own scope note flagged —
`ConfigAccess.consume()` also appends to the record. It cannot
safely issue a receipt event using a stale in-memory chain
head merely because the output gate will later refuse to
honour it. The integrity rule must protect the act of issuance
as well as the later act of admission.

**The correction** (`access.py` only). `consume()` now
verifies the record's current chain (Stage 1's `verify_chain`
over `read_all()`) after argument validation and before any
append — the same discipline the freeze path and both
admission gates apply. On integrity failure it raises the new
`ConsumptionRefused` carrying `record_chain_verification_failed`
and the first bad seq, and appends NOTHING: no receipt is
issued and the record file is untouched. On a verified chain,
issuance is unchanged (receipt appended, registered by event
digest, frozen values only). With this round, all four writer
paths hold the shared rule: freeze verifies before its
writes; capture verifies before its lane call and writes;
output verifies before trusting receipt evidence and writing;
access verifies before issuing its receipt.

**New sabotage, listed separately.**

- (h) Receipt issuance attempted on a body-edited record.
  After a healthy freeze, the `SUBJECT_VERIFICATION` event's
  body is edited on disk through the real JSONL persistence
  path, its stored digest retained (an event the access path
  never itself inspects, so no cross-check stands in the
  way). `consume(...)` raises `ConsumptionRefused` carrying
  the tampered event's seq under
  `record_chain_verification_failed`; zero `CONSUMPTION_RECEIPT`
  events stand on the record, the path's registry stays
  empty, and the file is byte-identical to its tampered
  state. The positive control is not duplicated: the
  pre-existing access/admission tests already exercise
  `consume()` successfully on a healthy chain, and still pass.

**Countercheck** (run by the orchestrator, the builder's
session having ended before it): in a scratch copy with the
new chain check in `consume()` neutralised, exactly one of
the 30 tests fails — (h) — and the other 29 pass. The new
assertion bites on precisely the corrected defect.

**Counts after correction.** Stage 3: 30/30 (the 29 prior
tests with unchanged outcomes, plus (h)). Stage 1 regression:
68/68. Stage 2 regression: 27/27. `stage1/` and `stage2/`
unmodified. The register disposition is unchanged by this
round: DR-03, DR-20 and DR-21 (established part) remain
advanced on demonstration, subject to the examiner's
re-examination of the corrected package — which has not yet
occurred.
