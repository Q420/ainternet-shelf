# DUENNA — STEP 7: THE JOINT IMPLEMENTATION PLAN

STATUS: AGREED AS THE JOINT IMPLEMENTATION PLAN (Alex, Chicken (1),
2026-11-10 ~08:03), subject to three amendments, all incorporated
into the text below the same day: the sabotage criterion (every
dependent fixture must fail, unrelated fixtures unaffected), the
obligation-level mapping rule for Stage 2, and the three-role
ownership naming for Stage 3 briefs; plus his Stage 4 precision
(available-and-applicable fixtures, gated ones reported as
outstanding). With those incorporated, the seven-step planning
loop is COMPLETE. The plan's product is a route to a proposal,
not a simplified specification.

Joint planning step 7 of 7 — the loop's final paper. Inputs: the
step-3 mapping as amended, the step-4 examination as verified, step
5 as settled with your corrections, and the step-6 architecture as
AGREED (DUENNA-STEP6-ARCHITECTURE.md, clarifications incorporated).

What this plan is: the staged route from the current specification
(v0.10 working text) to a SIMPLIFIED PROPOSAL built on the agreed
architecture, with equivalence evidence at every stage. What it is
not: it authorises nothing by itself. Executing any stage needs its
own authorisation; adopting the proposal at the end is Ben's
decision, on independent examination. No existing artefact changes
under this plan — v0.8, v0.9 and v0.10 stay exactly as they are;
the proposal is a new document, seeded and built separately.

## Stage 0 — Seed and baseline

Seed the Simplified Proposal from the v0.10 specification text
byte-identical; record the seed hash. Carry the 31 v0.10 fixture
cases unchanged as the baseline suite and run them against the
seed. ACCEPTANCE: baseline suite green on the unmodified seed;
seed hash and suite results recorded in the proposal's change
record. Nothing proceeds on a red baseline.

## Stage 1 — The five consolidations, one at a time

Executed in risk order, each as its own change with its own record,
under the execution rule: every retired body leaves a tombstone
(historical ID, never reused), a clause-level inventory of where
every part went, and its guarantee re-proven by running the fixture
against the survivor.

1. **J-2 → A-2** (clean). The omission case joins A-2's fixtures.
2. **B-5 → D-1.** Surviving fixture must scan evaluator OUTPUT,
   not only validate the state set internally.
3. **D-5 → D-3.** Machinery-defect residue labelled
   computation-layer in D-3's failure text; fixture asserts a
   machinery defect produces no F4 disposition.
4. **D-6 → D-3.** Recovery sentence carried VERBATIM into G-2/F-1
   attempt material, present there normatively; dual-pointer
   tombstone (D-3 for the body, G-2/F-1 for the sentence).
5. **D-2 split** (highest content-loss risk, last). B-2 receives
   the agent-declared-state clause ONLY; D-3 retains the
   machinery-defect, voiding and re-derivation consequence; the
   fixture names both survivors and which assertion each owns.

ACCEPTANCE, per merge: the survivor's fixture (with its new
assertions) passes; the full baseline suite stays green; and a
sabotage check: disabling the relocated guarantee makes every
fixture that depends on that guarantee fail, while unrelated
fixtures remain unaffected, and the evidence identifies the
failures attributable to the disabled guarantee. A merge that
cannot pass its sabotage check is not complete, whatever the
green suite says.

## Stage 2 — Architectural conformance, no normative change

Reframe the proposal's structure onto the agreed architecture:
requirements grouped under RECORD / BINDER / EVALUATOR / EXAMINER
SURFACE, F5 present only as governance and enforcement edges,
C-3's obligations labelled by function, the identity taxonomy
marked provisional in the text. Requirement bodies remain
byte-identical except for Stage 1's merges. ACCEPTANCE: a
normative diff against the seed shows Stage 1's changes and
nothing else; every requirement OBLIGATION maps to exactly one
component — a requirement containing obligations across multiple
functions may span components, but each obligation has one
identifiable component responsibility and acceptance path; the
Examiner wording stands as agreed at step 6, unaltered.

## Stage 3 — The carried items, dispositioned, not solved

No machinery is invented in this stage. Its products are papers:

- **Stream-entry correction** (design obligation): a design brief
  stating the problem, the binding constraints (original content
  preserved, no silent rewrite, examiner re-derivability), and
  candidate shapes explicitly labelled UNRULED, ending with the
  decision it needs and whose it is.
- **Checker-verdict correction** (design obligation): the same
  shape — constraints per the agreed problem statement (original
  verdict preserved, later finding recorded, operative verdict
  identifiable for reporting).
- **Discharge-record supersession**: carried into the proposal's
  register as a NAMED OPEN ITEM, in those words. Not briefed, not
  solved, not inherited away.
- **LINK equivalence**: the H-6 (v)/(vi) fixtures run against the
  shared append mechanism, or the item stays UNPROVEN in the
  register — the plan records the dependency honestly: those
  fixtures belong to the separately authorised gap package (plan
  register C-1), and this stage does not presume it.

Each brief names three roles SEPARATELY: who prepares the brief,
who has authority to decide the disposition, and who implements an
authorised decision. Candidate shapes in a brief are UNRULED; a
brief cannot turn them into approved machinery. (Ben's delegation
to Remmy governs pending decisions inside the planning loop; it
does not transfer Ben's reserved owner authority over the
specification or the proposal's adoption.)

ACCEPTANCE: both briefs exist with constraints and the three roles
named; the register carries every unresolved item by name; nothing
in the proposal text resolves a carried item by implication.

## Stage 4 — Equivalence evidence and examination

All fixtures available and applicable to the proposal are run
against it — with any unavailable or separately gated fixtures
explicitly reported as outstanding, so a green available suite
never implies the four gaps or the H-6 tests are satisfied;
per-merge sabotage evidence collected; a traceability record mapping every
retired body to its destination, fixture and tombstone. The
proposal, its change records and its evidence then go to
independent examination on the established pattern (examiners
outside the build; adjudication on their reports). ACCEPTANCE:
examination complete and adjudicated; the adoption decision —
Ben's — is taken on the examiners' findings, not on the builder's
report. Until then the proposal is a proposal: the current
specification line (v0.10) remains the newest examined text.

## Dependencies and order

Stages run in order; none starts on an unaccepted predecessor.
Stage 1's order is risk order and is not interchangeable (the D-2
split goes last because split destinations are where content
dies). Stage 3's LINK item alone depends on an outside
authorisation (the C-1 gap package); the rest of Stage 3 does not.
Stage 4 depends on all of it.

## What stays true throughout

The four fixture gaps (C-1…C-4) and UX-1…UX-5 keep their statuses.
No PROPOSED or UNRESOLVED status changes except as the register
records. OWNER-RULED text (J-1, H-5) is untouched; H-7 stands
alone. The plan's own execution, stage by stage, is authorised
work — this document is the plan, not the authorisation.

## The ask

Agree this as the joint implementation plan — stages, order,
acceptance criteria and guardrails — or amend it. On agreement,
the seven steps are complete: state, functions, mapping,
examination, challenge, architecture, plan. The loop's record then
goes where Ben directed it: into the shared record for both seats,
and into Qwen's corpus, so the settled state can be tested against
a reader who wasn't in the room.
