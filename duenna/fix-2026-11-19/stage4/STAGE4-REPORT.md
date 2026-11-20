# Duenna Stage 4 — Verdict Issuance and Procedure Dispatch Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md, Stage 4; ID-SYSTEM-DESIGN-DRAFT-V3.md (K7, K8)
Build location: ~/workspace/duenna-fix/stage4/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 4 built from the plan, after Stage 3 cleared Gate 1)

## Status of this report

The Stage 4 harness is built and its full test suite passes
(34/34), with the Stage 1 (68/68), Stage 2 (27/27) and Stage 3
(38/38) suites green as regression. This report is EVIDENCE for
the examiner, not a verdict: whether Stage 4 passes is the
examiner's determination (Gate 1 discipline), not this report's.

Stage 4's scope, per the plan, is twofold: build verdict
issuance identity (K7) and procedure dispatch (K8), AND execute
the outstanding independent examinations as first-class work —
DR-24's original cross-contract replay, the FX-R60k
object-identity sabotage, the FX-R60i restored-global-dispatch
sabotage, and the FX-R60l re-confirmation. Each examination is
reported in its own section below, with its own outcome. They
are never compressed into a single combined statement: they
establish different properties. FX-R60h is NOT re-run in this
stage — its existing independent evidence stands as recorded.

## What was built

`contract.py` — one factory-built checker system, following the
R-era v2.4 reference mechanism (R60 change record, addenda 2
and 3), rebuilt as this stage's own harness.

**K8 — procedure identity.** The one true registry (a
MappingProxyType over a dict no other reference exists to) and
the pinned anchor hashes live inside the factory's closure.
Construction dispatches through the closure cell: an
unrecognised or fictitious procedure identity is refused at
construction, and the identity a contract claims IS its
dispatch key, so a contract cannot claim one procedure while
executing another. The identity a verdict carries is minted by
the contract that ran the callable. The module-level name
PROCEDURE_REGISTRY refers to the same registry object for
inspection, but neither dispatch nor validation reads the
module global. Validation compares a verdict's implementation
hash against the PINNED hash captured at definition for the
claimed identity — held independently of the dispatch path —
never merely against the contract's own callable.

**K7 — verdict issuance identity** (scoped to checker verdicts,
as the design narrows it). The factory closure holds a private
issuance record. Every verdict run() returns is recorded before
return: the actual contract instance, the actual verdict
object, and a fingerprint of the verdict's canonical contents
at issuance. The record retains references, so a recorded
object cannot be garbage-collected out from under the record.
Validation requires BOTH: the submitted object IS the retained
object issued by this contract instance (`is`, not a copyable
identifier, not content matching), AND its current contents
agree with the issuance fingerprint. The field checks (the
reproducibility trio: procedure, version, pinned implementation
hash, input identity) fire first, unchanged from v2.3/v2.4.

**Record discipline.** These mechanisms write no records. K7's
scope boundary in the design is in-process only — no
cross-process or persisted provenance, no claim against
arbitrary rewriting of the hosting process (closure-cell
surgery, rewriting the module's own functions). The Stage 1
record / Stage 3 verify-then-extend discipline therefore has
nothing to attach to in this stage, and none is bolted on
decoratively.

**Fixture judgements.** None were needed: every mechanism and
every case in this stage comes entire from the record — the
design's K7/K8 sections, the v2.4 reference implementation, and
the FX-R60j finding with its two addenda. No field, case or
threshold was invented. One scope judgement IS stated plainly
where it belongs (the examination sections): the three sabotage
examinations execute against THIS STAGE's implementation of the
v2.4 mechanism, not against the historical v2.4 file itself.

## Test 4 acceptance — every case, separately

Verdict issuance (test_verdict_issuance.py, 18 tests):

- Genuine verdict accepted by its issuer — PASS.
- Forged verdict carrying the genuine pinned hash rejected —
  PASS (FX-R60j: every checked field copied from the genuine
  verdict, the pinned hash included, the outcome fabricated;
  rejected as not issued by this contract).
- The same forgery offered as the outcome for an artefact whose
  actual run returned the failure path rejected — PASS.
- Issuer A's verdict rejected by issuer B, different expected
  digests — PASS (FX-R60k).
- Issuer A's verdict rejected by issuer B, identical issued
  contents — PASS (FX-R60k: the two verdicts are byte-equal and
  are different objects; content equality is not issuance
  identity; both directions asserted).
- A byte-identical copy of an issued verdict rejected — PASS
  (FX-R60k).
- Same-contract control: a genuine verdict validates for its
  own contract — PASS.
- A mutated issued object rejected — PASS (FX-R60l).
- The mutated object's rejection reason is "verdict altered
  after issuance" — PASS, asserted as its own test so the
  reason is attributable separately from the outcome.
- An issued object mutated and then restored exactly is
  accepted — PASS (Addendum 2's stated consequence: the
  fingerprint is over contents as issued).
- Field checks, each separate: not-a-verdict, procedure
  mismatch, missing version, version mismatch, missing
  implementation hash, altered implementation hash, missing
  input identity, input identity mismatch — all rejected with
  the specific defect named — PASS (8 tests).

Procedure dispatch (test_dispatch.py, 11 tests):

- Fictitious procedure identity refused at construction —
  PASS (FX-R60g form; DR-09's case).
- The declared identity is the executed callable: the verdict's
  procedure identity is the construction identity and its
  implementation hash is the pinned anchor hash of the
  canonical procedure's source — PASS.
- Repeated runs produce byte-identical verdicts — PASS.
- Registry remapping refused (TypeError from the proxy), and
  the recognised identity still dispatches to its originally
  bound callable, with a tampered payload still failing —
  PASS. This is the mechanism's behaviour in this stage's
  suite (FX-R60h's form); it is builder-run evidence about
  this stage's registry only — see the DR-10 register note.
- Module-level registry-name rebinding does not redirect
  dispatch (a tampered artefact still takes the failure path),
  and a forged verdict stamped with the substitute's hash
  fails pinned-anchor validation — PASS (FX-R60i).
- Run paths, each separate: missing artefact, wrong input
  artefact, corrupt artefact, wrong digest with no corrupt
  flag (refused by the digest comparison itself), unpinned
  contract refusing to run, the verdict recording the pinned
  version — PASS (6 tests).

## Examination — DR-24's original cross-contract replay, EXECUTED

(test_exam_dr24_replay.py, 2 tests)

Until this stage, the replay stood established by SOURCE
INSPECTION only: the implementer's 2026-11-10 execution attempt
was blocked by her tooling and was not routed around, and
DR-24's register entry preserves that classification. This
examination executes it, against harness v2.3 exactly as
shelved.

The artefact: stage4/evidence/harness-v23-as-shelved.py,
retrieved from the shelf repo's history (commit
de6c4d015198d01772dccd721a89cd69b71be547, "R60 rebind repair
(harness v2.3, 35/35)") and admitted only on its pinned digest
— sha256 30bdd25ead4ab6085106a1f91f09b24c2ef563e3eaaedc93f127344055f54a2a,
the digest the R60 change record and the FX-R60j finding record
for v2.3 as shelved. The first test verifies the digest against
the file's actual bytes; the examination claims nothing against
any other bytes.

The case executed is the original one (the 2026-11-10
repro-fx-r60k.py specification): two contracts sharing
procedure identity, version and input ID, protecting different
expected digests. Outcome, by execution:

- Contract A runs successfully on its payload; its genuine,
  unaltered verdict validates for A — ACCEPTED (control).
- The same verdict submitted to Contract B validates —
  **ACCEPTED. The defect reproduces.** B accepts a verdict it
  did not issue, for a digest it does not protect, because
  v2.3's four validation checks are instance-independent.
- B's own run on the very payload A's verdict certifies takes
  the failure path — B accepts as preserved an outcome B itself
  refuses to produce.

What this establishes: the DR-24 defect is now EXECUTED
evidence, not inspection only. What it does not establish:
anything about the repaired mechanism — that is the FX-R60k
fixture's and sabotage's separate work, below. The execution
is builder-run within this stage; the examiner's independent
execution remains hers at Gate 1.

## Examination — FX-R60k object-identity sabotage, EXECUTED

(test_exam_fx_r60k_identity_sabotage.py, 1 test)

The outstanding sabotage from DR-24/DR-25's re-examination
list: remove the object-identity check and demonstrate that
FX-R60k fails. The weakening is the historically specified one
— the serialised-content design of the FX-R60j finding's first
addendum, which Alex's second addendum refuted: the issuance
lookup accepts any submission whose current contents
fingerprint-match a verdict this contract issued, instead of
requiring the submitted object to BE the retained object. The
variant is constructed in a scratch tree by an exact, uniquely
anchored replacement in this stage's contract.py, and the
stage's two mechanism suites (29 tests) are run against it.

Outcome, by execution — exactly three tests fail, 26 pass:

- test_a_verdict_rejected_by_b_identical_contents — FAILS
  (A's verdict is now wrongly ACCEPTED by B: content equality
  is mistaken for issuance identity, the precise weakness
  Addendum 2 named).
- test_byte_identical_copy_rejected — FAILS (a copy is now
  wrongly ACCEPTED by its issuer's contract).
- test_mutated_issued_object_rejection_reason — FAILS, as an
  explained cross-effect: under content membership the mutated
  object is refused at the identity branch ("not issued by
  this contract"), so the altered-after-issuance reason is
  never reached. FX-R60l's OUTCOME test still passes — the
  mutated object is still rejected — so the integrity property
  does not depend on the identity check; only the reason string
  moves. This cross-effect is reported, not smoothed: it is
  what the mechanism actually does under this weakening.

Every other case holds under the weakening — including the
different-digests cross-contract case (B issued nothing with
A's contents, so content membership still refuses it) and the
FX-R60j forgery (its fabricated contents match no issuance).

What this establishes: FX-R60k's identical-contents and copy
cases depend on the object-identity check, demonstrated by
execution against this stage's implementation of the v2.4
mechanism. What it does not establish: the same sabotage
against the historical v2.4 file (sha256 854a3e86…) — that file
was not patched and run; the mechanism sabotaged here is this
stage's rebuild of the same design (factory-closure issuance
record, `is` identity plus issuance fingerprint).

## Examination — FX-R60i restored-global-dispatch sabotage, EXECUTED

(test_exam_fx_r60i_restored_global_dispatch.py, 1 test)

The outstanding sabotage from DR-11's assurance reconciliation,
in the form the R60 rebind repair proposal itself specifies:
restore the old dispatch — module-global read plus
self-referential validation — and FX-R60i must fail while the
rest of the suite stays green. Both halves of the old behaviour
are restored together, as the proposal specifies; they were one
defect (construction and validation trusting the same
compromised source). Three exact, uniquely anchored
replacements in a scratch copy of this stage's contract.py:
construction resolves the registry through the module global;
the bound callable is taken from the module global; validation
compares the verdict's implementation hash against the
contract's own bound callable instead of the pinned anchor.

Outcome, by execution — exactly one test fails, 28 pass:

- test_module_registry_rebinding_does_not_redirect_dispatch —
  FAILS. Under the restored dispatch the rebinding attack
  succeeds end to end: the substitute is bound at construction,
  the tampered artefact is certified "preserved", and a forged
  verdict stamped with the substitute's hash validates
  self-referentially.

Everything else holds: fictitious identities are still refused
(the restored global is the genuine registry until rebound),
remapping is still refused by the proxy, and every
verdict-issuance case still holds, because none of them rebinds
the global.

What this establishes: the FX-R60i fixture's protection depends
on BOTH halves of the v2.3 repair — closure dispatch and the
independently held pinned anchor — demonstrated by execution
against this stage's implementation of that mechanism. What it
does not establish: the same sabotage against the historical
v2.3/v2.4 files; and nothing beyond the stated threat model
(ordinary module-level attribute assignment — not closure-cell
surgery, not rewriting the module's functions).

## Examination — FX-R60l re-confirmation, EXECUTED

(test_exam_fx_r60l_reconfirmation.py, 1 test)

The implementer executed this sabotage against the R-era v2.4
harness: with the fingerprint comparison removed, FX-R60l
failed alone (37 PASS / 1 FAIL at fixture granularity). The
plan schedules FX-R60l re-confirmed in this stage — the same
sabotage executed against this stage's implementation,
confirming the result holds. The weakening is one exact,
uniquely anchored replacement: the fingerprint comparison in
validate_verdict() is removed; object identity still stands.

Outcome, by execution — exactly two tests fail, 27 pass, and
both failing tests are the FX-R60l fixture's own:

- test_mutated_issued_object_rejected — FAILS (the mutated
  object now validates: identity alone cannot see the
  alteration).
- test_mutated_issued_object_rejection_reason — FAILS (there
  is no rejection to carry the reason).

Every other test holds: forgery, cross-contract replay, copies
and the field checks are all still refused by the checks that
remain. At fixture granularity this matches the implementer's
v2.4 result — FX-R60l alone fails — re-confirmed against this
stage's implementation.

What this establishes: the issuance-integrity property depends
on the fingerprint check, and on nothing else in the mechanism.
What it does not establish: anything about the historical v2.4
file beyond consistency with its recorded result.

## FX-R60h — not re-run

Per the plan: FX-R60h's existing independent evidence stands as
recorded (Vane's independent execution: immutable baseline 8/8
in the focused R60 run; mutable variant 7/8 with FX-R60h
failing; the recorded limitation — the complete 34-fixture
harness was not executed under sabotage — is preserved). This
stage does not re-run it and adds no claim to it.

## Register effects — per row, strictly per the evidence

- **DR-09** (declared procedure identity not bound to the
  executed callable): demonstrated within this stage's harness
  — a fictitious identity is refused at construction, and the
  verdict's implementation hash is the pinned anchor hash of
  the canonical procedure the identity dispatches to. Builder-
  run demonstration; the row's examiner disposition is the
  examiner's to update at Gate 1.
- **DR-10** (mutable procedure registry remapping): NOT
  re-examined in this stage. FX-R60h's independent evidence
  stands as recorded, with its limitation. This stage's suite
  contains the mechanism behaviour in FX-R60h's form (remap
  refused, dispatch unchanged) as builder-run evidence about
  this stage's registry only; it adds nothing to DR-10's
  independent-evidence status and claims nothing for it.
- **DR-11** (module-level registry rebinding): the FX-R60i
  fixture passes in this stage's harness, and the
  restored-global-dispatch sabotage — the outstanding sabotage
  evidence for this row — is now EXECUTED (against this stage's
  implementation of the v2.3 mechanism): restoring the old
  dispatch fails FX-R60i alone. The assurance reconciliation
  for the historical v2.3 file remains the examiner's to close.
- **DR-23** (forged verdict accepted without issuance
  provenance): the FX-R60j cases are demonstrated in this
  stage's harness — genuine accepted; forgery with the genuine
  pinned hash rejected; the forgery offered against a
  failure-path artefact rejected. (The v2.3 reproduction was
  already executed evidence and is not re-claimed here.) Final
  approval of the repair remains the examiner's.
- **DR-24** (cross-contract verdict replay): both outstanding
  items now have executed evidence — the original v2.3 replay
  is EXECUTED against the hash-verified v2.3 artefact (the
  register's "established by source inspection, not executed"
  classification is superseded by this execution), and the
  object-identity sabotage is EXECUTED against this stage's
  implementation of the v2.4 mechanism, failing FX-R60k's
  dependent cases. Independent examination of both remains the
  examiner's act at Gate 1.
- **DR-25** (verdict object integrity after issuance): the
  integrity sabotage is RE-CONFIRMED against this stage's
  implementation — removing the fingerprint check fails
  FX-R60l alone at fixture granularity, consistent with the
  implementer's executed v2.4 result. The identity sabotage's
  explained cross-effect on the rejection-reason string is
  recorded in the FX-R60k section above.

## Counts

- Stage 4: 34/34 (verdict issuance 18; procedure dispatch 11;
  examinations 5 — DR-24 replay 2, FX-R60k sabotage 1, FX-R60i
  sabotage 1, FX-R60l re-confirmation 1). Under-sabotage inner
  runs (the 29 mechanism tests): identity sabotage 26 pass /
  3 fail; restored-global-dispatch sabotage 28 pass / 1 fail;
  fingerprint sabotage 27 pass / 2 fail — each failing set
  asserted exactly by its examination.
- Regressions: Stage 1, 68/68. Stage 2, 27/27. Stage 3, 38/38.
  stage1/, stage2/ and stage3/ are unmodified.

## Boundaries, stated plainly

In-process provenance only: no cross-process or persisted
provenance is claimed. The threat model covers ordinary
module-level attribute assignment (rebinding, remapping,
substitution); it claims nothing against an actor who rewrites
the module's own functions or reaches into closure cells
directly. All Stage 4 evidence is builder-run within the
harness scope; independent demonstration and production
integration remain separate obligations, as in every prior
stage.

## Correction round 1 — Gate 1 return

**The ruling answered** (VANE-GATE1-VERDICT.md, shelf commit
bdc586c56fa037271a7803917f0d2878a8a45f31): Gate 1 FAIL, one
targeted K8 correction. K7 is accepted as built
(retained-object identity plus issuance fingerprint), as are
the closure-held registry and the independently held pinned
anchor. The one defect: construction stored the
closure-selected procedure in an ordinary instance attribute
and `run()` dispatched through it, so any caller could
reassign the attribute after construction and a substitute
would execute under a contract constructed with the canonical
procedure identity — the pinned-hash verdict check catching
the result only after the wrong callable had already run. K8
requires the declared identity bound to the executed
callable, not merely detected after the fact. Ordinary
instance-attribute reassignment is inside the threat model;
no redesign was asked for.

**The correction** (`contract.py` only). The contract
instance is sealed at the end of construction — the FrozenRun
discipline of Stage 3, carried to this class. `__init__`
completes every binding exactly as before (construction's
registry-selection line is untouched; it is also an anchor
the FX-R60i examination patches by exact string, and all five
examination anchors in the file were verified to still occur
exactly once after this correction), then sets the seal flag
as its last act. From that moment `__setattr__` raises
AttributeError on any assignment — the bound callable above
all, and the seal flag itself, which cannot be switched off
by assignment — and `__delattr__` raises on any removal.
Reassignment is refused at the attempt, loudly: it neither
silently succeeds nor silently no-ops, and dispatch remains
tied to the callable construction selected from the closure
registry.

Why this seal over holding the callable in the factory
closure: per-instance state in this class already lives in
instance attributes, and the construction line that selects
the callable is both the mechanism's existing shape and an
examination anchor; a closure-held per-instance store would
have been the redesign the ruling said was not needed. The
guard is the smallest change that makes reassignment itself
refused.

**New tests, listed separately** (`tests/test_instance_binding.py`
— a separate file by design: the FX-R60 examinations copy
exactly the two mechanism suites into their sabotage variants
and assert exact failing sets over those 29 tests, and this
correction does not change their composition; the full-suite
discovery run includes the new file normally).

- (sabotage) Rebinding the instance procedure is refused.
  After construction, assigning a substitute callable to the
  instance's bound procedure raises AttributeError, as does
  assigning the seal flag off. The binding is asserted to
  still be the canonical procedure object, and a tampered
  artefact run through that contract still takes the
  canonical failure path ("FAILURE-PATH: invalid artefact") —
  the canonical procedure executed and refused it; the
  substitute, which returns the expected digest for any
  payload and would have certified the artefact, never ran.
- (control) Healthy control. A sealed contract executes the
  canonical procedure on the genuine artefact, the verdict
  carries the pinned implementation hash, and
  `validate_verdict` returns "ACCEPTED".

**Countercheck.** In a scratch copy with the seal's guard
condition neutralised (both the assignment and deletion
guards), exactly one of the two new tests fails — the
sabotage, at "AttributeError not raised" (the reassignment
succeeds and the defect is live again) — and the healthy
control passes. The new assertion bites on precisely the
corrected defect.

**Counts after correction.** Stage 4: 36/36 — the 34 prior
tests with unchanged outcomes (verdict issuance 18, procedure
dispatch 11, examinations 5; the three sabotage examinations'
asserted failing sets over the 29 mechanism tests are
unchanged and still exact), plus the 2 new binding tests.
Stage 1 regression: 68/68. Stage 2 regression: 27/27.
Stage 3 regression: 38/38. `stage1/`, `stage2/` and `stage3/`
unmodified. DR-09 / DR-11's K8 disposition awaits the
examiner's re-examination of the corrected package, which has
not yet occurred.
