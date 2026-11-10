# DUENNA — STEP 6: THE SMALLEST VIABLE ARCHITECTURE

STATUS: AGREED (Alex, Chicken (1), 2026-11-10 ~07:58), subject to
three clarifications, all incorporated into the text below the same
day: the BINDER output boundary, append-discipline ownership
(RECORD owns it; the Evaluator uses it), and the Examiner's
reporting inputs; the dependency statement's phrasing is adjusted
to match (the Evaluator consumes the Binder's recorded entries via
the Record). The 48→43 count is a proposal count, not executed
changes.

Joint planning step 6 of 7. Inputs: step 5 as settled with your two
corrections, both carried into this paper verbatim where they bite:
the Pair 4 destinations, and your replacement wording for the
Examiner. What this paper asks you to agree: the component set, the
boundaries between them, the dependency statement, and the register
of conditions and open items the architecture carries without
solving. Step 7 then plans against the agreed text.

## The four components

**RECORD — discharges F2.** Preserves original content whole, with
stable identity and content digest, append-only: nothing is
silently rewritten, ever. The record is the foundation — it does
not depend on binding, so evidence of a failed or absent binding is
recordable in it (the F1→F2 split from step 3). The identity
taxonomy stays PROVISIONAL inside this component: kinds are data,
not structure, and each kind still owes a distinct failure case or
it consolidates. Implementation may separate identity storage,
canonicalisation and digest machinery inside the component; those
are its internals, not new components.

**BINDER — discharges F1.** Binds authored rules into instances of
a pinned, approved contract — mechanically, with no discretion at
binding. BINDER outputs only to the RECORD: successful binding
produces instance entries; binding failure produces an explicit
failure entry. It has no other output channel. The absence of an
instance must not read as success (your step-4 test, carried here
as this component's acceptance shape).

**EVALUATOR — discharges F3 and F4, as ONE component with TWO
independently testable guarantee sets.** One mechanism: the fold
derives lifecycle states from evidence only (F3), and accounting
states every obligation satisfied, blocked, unmet or indeterminate
with attribution that cannot be relabelled (F4). The machinery is
shared; the guarantees are not merged — F3 and F4 keep separate
acceptance suites, and a pass in one suite says nothing about the
other. The append-only preservation and identity discipline is
owned by the RECORD. The EVALUATOR uses that discipline to append
evaluation annotations, defect dispositions and LINK entries —
append kinds of one mechanism, not three; the kinds and their
semantics remain defined by their respective requirements. The
Evaluator can produce entries; it cannot decide that history may
be rewritten. LINK's equivalence on that shared mechanism remains
UNPROVEN pending the H-6 (v)/(vi) fixtures — the architecture
carries that as a condition, not a claim.

**EXAMINER SURFACE — discharges F6.** In your wording, adopted:
"The Examiner independently re-derives from the preserved original
record, using the applicable pinned contract and defined
reproduction rules, without relying on the Evaluator's derived
state or conclusions." Reports (the K-4 material) are projections
produced through this surface, not a component of their own. The
Examiner's independent derivation uses the preserved original
record, the applicable pinned contract and the defined
reproduction rules; any additional report material — registers,
verdicts, defect records and other evidence carried outside the
stream — must be obtained through its specified evidence path and
must not be inferred from the Evaluator's conclusions. No
component grades its own work: the surface reads the RECORD and
the pinned contract, never the EVALUATOR's state.

**F5 is not a component.** It is two kinds of edge crossing every
component: governance edges — external, Ben's, the only place
authority originates — and enforcement edges — mechanical checks
against pinned approved artefacts at entry and progression points.
There are no decision edges. No gate, evaluator or examiner
invents a permission; the gate evaluates evidence receipt, the
approved contract defines the consequence, the machinery applies
it.

## Dependency statement

RECORD depends on nothing. BINDER depends on RECORD. EVALUATOR
depends on RECORD, consuming BINDER's recorded instance entries
through it — the record is the shared boundary between components.
EXAMINER SURFACE depends on RECORD, the pinned contract and the
reproduction rules — never on EVALUATOR outputs. Enforcement edges
cross all four; governance edges touch the whole from outside.
This is the amended chain from step 3, with its F1→F2 split
preserved: remove BINDER and the system still records; remove
RECORD and nothing else stands.

## The consolidation register this architecture assumes

Five merges, with their conditions as settled in steps 4–5 —
conditions are requirements of the merges, not notes:

1. B-5 → D-1, with the surviving fixture scanning evaluator OUTPUT.
2. D-5 → D-3, machinery-defect residue labelled computation-layer
   in D-3's failure text; fixture asserts a machinery defect
   produces no F4 disposition.
3. D-6 → D-3, recovery sentence carried VERBATIM into G-2/F-1
   attempt material and present there normatively; dual-pointer
   tombstone.
4. D-2 split, AS CORRECTED AT STEP 5: B-2 receives the
   agent-declared-state clause only; D-3 retains the
   machinery-defect, voiding and re-derivation consequence; the
   fixture mapping names both survivors and which assertion each
   owns; tombstone and clause-level inventory preserve every part's
   destination.
5. J-2 → A-2, clean; the omission case joins A-2's fixtures.

Pair 6 stays OUT: H-7 is a standalone requirement in the proposal;
J-1 is owner-ruled and untouched. Net effect on the proposal:
48 requirement bodies → 43. C-3 remains one requirement with
obligations grouped by function, its machinery distributed across
RECORD (identity), EVALUATOR (fold order) and EXAMINER SURFACE
(re-derivation) as implementation placement, not as a split.

## What the architecture carries, unsolved, by name

- Stream-entry correction — step-7 DESIGN OBLIGATION (acceptance
  shape: preserve original, no silent rewrite, re-derivable).
- Checker-verdict correction — step-7 DESIGN OBLIGATION
  (acceptance shape: original preserved, later finding recorded,
  operative verdict identifiable for reporting).
- Discharge-record supersession — an UNRESOLVED SPECIFICATION
  DISPOSITION, not a design obligation; it is carried as a named
  open item and must not disappear through assumed inheritance.
- LINK equivalence on the shared append mechanism — unproven,
  pending the H-6 (v)/(vi) fixtures.
- Identity taxonomy — provisional; failure cases owed per kind.
- CANON-1 excluded paths and the Family E schema — unresolved from
  the audit (U-1, U-3), untouched by this architecture.

## The ask

Agree, amend or challenge: the four components and their
boundaries; the dependency statement; the register above as the
architecture's assumed consolidation set; and the carried items
list. On your agreement, step 7 is a drafting exercise: one
implementation plan — stages, dependencies, acceptance criteria —
against this text, and nothing in it invents machinery for the
carried items.
