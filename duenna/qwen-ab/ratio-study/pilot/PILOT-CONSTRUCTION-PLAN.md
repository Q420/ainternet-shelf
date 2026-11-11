# FEASIBILITY PILOT — JOINT CONSTRUCTION PLAN (DRAFT 1)

**Status:** draft for Alex's consolidated review. Nothing
builds until this plan is agreed and frozen. Ben is the
authority on the intended system and its boundaries; his
instruction to plan before building is the controlling
direction. **Scope of this plan:** construction of the
feasibility pilot package only. The 60-run execution
requires separate authorisation after construction is
accepted. **Frozen and untouched:** V2R battery record,
V2.4.8 foundation, OPERATION-MAPS-V2 (the allocation
source). **Out of scope:** the Worker Capability
Assessment (Ben's proposal, recorded separately for the
next design discussion); identity/signatures; any claim
beyond feasibility and provisional calibration.

**Roles.** Remmy: plan author, builder, self-verifier.
Alex: independent technical review and acceptance
contract — one consolidated amendment round, not
incremental requirements. Ben: authority; plan
adoption is his if he chooses to rule on it.

---

## 1. What the pilot can and cannot establish

**Can:** that the capability-profile mechanism works
end to end — profiles derive from adjudicated evidence,
selection configures real execution, allocations differ
by level as mapped, measurements are recorded honestly,
and the first provisional profile entries for one worker
(Qwen) result from the calibration matrix.
**Cannot:** broad capability claims about any worker;
saturation points; statistical comparisons (n=1 per
cell); semantic truth of mechanical classifications;
that agreement equals understanding.

## 2. Definitions — every measurement, precisely

| Metric | Definition | Inputs | Calculation | Limitation |
|---|---|---|---|---|
| Eligibility | A run's output passed the frozen release gate | gate scorers | frozen gate result | **Not** demonstrated capability |
| Worker correctness | The worker's own output matches the frozen scoring key | worker raw output | frozen scorers on the original output | One observation per run |
| System correctness | The final artefact (after mechanical steps) is correct | final output | frozen scorers | Credits the system, not the worker |
| Adoption | Worker-after label equals the mechanical classification where worker-before differed | three probe records | per-statement comparison | Agreement is not understanding |
| Evidence-backed adoption | Adoption (or prior alignment) AND the worker identified the supporting evidence by a statement-specific route | probe records + evidence flags | §5 R-11 | Route is mechanical; interpretation may still err |
| Mechanical coverage | Share of a task's operations owned by X at a level | operation maps | count of X operations / total | Says nothing about quality |
| Confidence (profile) | LOW / MEDIUM / HIGH per the ladder: adjudicated, consistent, n≥3 for MEDIUM; HIGH unreachable inside the pilot | adjudicated observations | profile.py derivation | Pilot ceiling is MEDIUM |
| Access | A source was retrieved into a packet | tool logs | recorded retrieval | **Not** proof the content influenced the answer |

Standing distinctions (binding on all reporting):
eligibility ≠ capability · a passing fixture ≠ general
reliability · label agreement ≠ evidence-backed adoption
· evidence retrieval ≠ correct interpretation · a
mechanical check ≠ semantic judgment · a worker call is
never a mechanical operation · an access log ≠ proof of
influence.

## 3. Components, interfaces, responsibilities

- **Driver (pilot.py).** Owns: layout resolution,
  hash-verified import of frozen modules, the
  calibration matrix (fixed, per §6), the adaptive
  runtime (§5 R-08), call accounting, run records,
  authorisation refusal, stop-rule enforcement. Calls
  the worker only through run_ab.call_qwen (wrapped for
  accounting). Never edits frozen modules.
- **Profile mechanism (profile.py).** Owns: profile
  schema + validation, derivation from adjudicated
  observations, binding resolution, confidence ladder,
  selection (profile + job → template + allocation),
  cold-start behaviour. Pure functions over explicit
  inputs; no I/O beyond record files it is handed.
- **Template registry (in profile.py).** Versioned
  template objects: identity, version, requires list,
  allocation effects. Selection validates identity and
  version against the registry; an unknown or
  mismatched template fails closed to cold start.
- **Frozen tools (tools24.py) and flows (run_c.py,
  run_ab.py).** Used as-is, hash-pinned (§5 R-01).
  Their external data dependencies are declared (§5
  R-02), never hidden.
- **Fixtures (pilot_fixtures.py).** Exercise the real
  functions with transport stubbed only. Each fixture
  is isolated (fresh state, own stubs) and asserts
  exactly the properties its plan row claims.

## 4. The four activities, kept separate

**Calibration** (the fixed 60-cell matrix) establishes
what a worker has demonstrated. **Selection** uses
existing evidence to choose constraints and support for
a job. **Runtime** executes the selected configuration.
**Adjudication** (Alex, after execution) evaluates
independently. Rules: a calibration result never
becomes proof of correctness inside the same execution;
the pilot never modifies the profile from its own
in-flight outcomes — profile updates are a later,
adjudicated step; selection reads only the profile that
existed before the run.

## 5. Requirements — traceability

Format: **Requirement | Acceptance criterion | Fixture /
verification | Evidence returned.**

**R-01 Frozen imports.** The driver imports run_ab,
run_c and tools24 only after verifying each file's
sha256 against the plan-pinned values, in both the
workspace and shelf layouts. | Criterion: a byte-altered
copy of any frozen module is refused before import; the
genuine files import in both layouts. | Fixtures:
F-IMPORT (both layouts) + F-IMPORT-ALTERED (negative).
| Evidence: import record with resolved paths and
hashes per run; refusal record for the altered case.

**R-02 Declared external dependencies.** Every data
source the frozen workflow resolves outside the package
(corpus index + manifest, shelf manifest, transport
binary) is enumerated with its resolved path and sha256
in every runtime record. | Criterion: the record lists
all dependencies the frozen code actually touches; no
output claims the package is self-contained. |
Verification: dependency record compared against the
frozen modules' own path constants at runtime. |
Evidence: dependency block in MECHANISM-VERIFICATION
and RUNTIME-DEMONSTRATION outputs.

**R-03 Pack-structure fidelity.** All pack handling uses
the frozen item structure ((id, text) items) through
the tools' native interfaces. | Criterion: packets built
for multi-item, mixed-kind packs contain every item with
correct provenance. | Fixture: F-R1R2 over a real frozen
pack. | Evidence: packet record with per-item digests.

**R-04 Derivation from real records.** Profile entries
derive only from the actual adjudicated battery records
(V1 + V2R), read from disk, each observation carrying
resolvable references {file, sha256, locator},
conditions, and binding metadata. | Criterion: every
derived entry traces to named records; hand-typed
observations are impossible (derivation input is the
record files). | Fixture: F-PROFILE re-derives and
compares. | Evidence: MECHANISM-VERIFICATION with
per-observation references.

**R-05 Binding, unanimous and fail-closed.** An
observation is bound only when at least one binding
declaration exists and ALL declarations (top level and
conditions) explicitly agree on "bound". Conflict,
absence, or any non-bound declaration → legacy-unbound.
| Criterion: legacy observations and entries remain
legacy-unbound; missing metadata never defaults to
bound. | Fixture: F-BINDING incl. conflicting-
declarations and missing-metadata cases. | Evidence:
derived profile showing evidence_class per entry.

**R-06 One-directional legacy selection.** Legacy
weakness evidence may add support (select a template);
legacy demonstrated evidence may never reduce coverage
(selection falls to cold start). | Criterion: both
directions demonstrated on the real seed profile. |
Fixture: F-BINDING selection cases. | Evidence:
selection records for T05/T06 (template) and T01 (cold
start).

**R-07 Confidence ladder with consistency.** LOW is the
default; MEDIUM requires n≥3 mutually consistent
adjudicated observations; any critical failure caps at
LOW; the pilot ceiling is MEDIUM. | Criterion: three
observations containing a failure never mint MEDIUM. |
Fixture: F-PROFILE cases. | Evidence: derivation record
with sample counts and confidence basis per entry.

**R-08 Selection is operational.** Inside the adaptive
runtime, the selected template changes what the worker
is permitted/required to do (packet content, required
operations, post-checks) — not merely a printed record.
| Criterion: changing a profile entry changes the
resulting configuration AND the executed behaviour
(calls made, operations performed). | Fixture:
F-ADAPTIVE + F-ADAPTIVE-CHANGE (same job, two profiles,
different executed configurations). | Evidence: runtime
record per configuration with call logs and operation
ledgers.

**R-09 Fail-closed selection.** A missing, malformed,
conflicting or version-incompatible profile produces
the defined cold-start behaviour and a recorded reason.
| Criterion: each malformed variant selects cold start;
no exception path silently proceeds. | Fixtures:
F-PROFILE negative cases (malformed JSON, unknown
template, wrong version). | Evidence: selection records
with fail-closed reasons.

**R-10 Templates perform their declared work.** Every
operation a template declares (extraction, reference
insertion, field verification, classification) is
actually executed in the adaptive runtime through the
frozen production constructions. | Criterion: the T05
template's run shows a complete insertion ledger and
per-field verification from the real t05_record path; a
deliberately defective worker emission is caught by the
post-check and recorded as a failure, not a pass. |
Fixtures: F-ADAPTIVE + F-ADAPTIVE-NEG. | Evidence:
insertion/verification ledgers, negative-case record.

**R-11 The T06 probe.** Three records are captured
separately and in order — worker-before (unaided,
before any mechanical exposure), the mechanical
classification (from the real frozen flow, read at
process.system_classification), worker-after (revision
with the mechanical record transmitted verbatim). |
Criteria: call sequence unaided → flow-internal →
revision; all four classifications transmitted exactly;
evidence identification is statement-specific — a
verbatim quote substring-verified against the pack, or
an absence claim in which **the worker's own statement
names the artefact** and its absence verifies against
the pack; evidence-backed adoption computed and
recorded distinctly from agreement; adoption recomputed
independently in the fixture. | Fixtures: F-PROBE
(positive) + F-PROBE-NEG (agreement without evidence
identification → evidence-backed adoption empty). |
Evidence: probe records, transmission check, evidence
routes per statement.

**R-12 Total call accounting.** Every worker call —
the driver's, the probe's, and any internal call inside
a frozen flow — is recorded with a purpose tag. No
worker call is ever counted or described as mechanical.
| Criterion: a frozen flow with an internal call shows
that call in the ledger under its own purpose; totals
reconcile with the transport stub's count. | Fixture:
F-CALLS. | Evidence: per-run call ledger.

**R-13 Coverage completeness.** All 12 entries (T01–T08
+ T09 FR-A/B/C/VALID) × all 5 levels (R0–R4) have
explicit per-operation allocations taken from
OPERATION-MAPS-V2, and the driver's resolved
configuration for each cell matches the maps. No
operation disappears between maps, driver, logs and
results. | Criterion: a coverage verification enumerates
every cell and every operation, comparing driver
configuration against the maps mechanically. | Fixture:
F-COVERAGE (60 cells). | Evidence: coverage record,
cell by cell, with discrepancies listed (none allowed).

**R-14 Level integrity.** Each level changes exactly
the allocations its map path declares and nothing else;
governance and independent (J) scoring apply at every
level including R0. | Criterion: configuration diffs
between adjacent levels equal the declared transfers. |
Fixture: F-COVERAGE diff assertions. | Evidence:
per-level configuration records.

**R-15 Stop conditions.** Any of: missing dependency,
hash mismatch, unresolvable record reference, fixture
failure during construction verification, missing or
invalid authorisation at execution — halts the work,
writes PILOT-STOPPED.lock, and produces no apparently
valid result. | Criterion: each stop condition,
triggered deliberately, halts with the lock and a
reason record. | Fixtures: F-STOP cases (altered hash;
missing record file). | Evidence: lock + reason records.

**R-16 Fixture discipline.** Fixtures use isolated
state and controlled stubs; stubs replace transport
only, never the logic under test; records are
snapshotted at capture (no live references); fixture
data never leaks between cases; no live model calls
occur in any fixture. | Criterion: the full suite passes
run twice in sequence with identical results; each
fixture's assertions are enumerated in this plan's
traceability rows (a fixture asserts only what its row
claims, and its row claims everything it asserts). |
Verification: double-run comparison. | Evidence:
FIXTURES-OUTPUT from both runs + diff (empty).

**R-17 Reproducibility.** All committed outputs are
regenerated from the checked-in shelf tree with the
exact commands, working directory and environment
recorded in the package note; a fresh execution
regenerates them byte-identically (modulo recorded
timestamps). | Criterion: regeneration from the shelf
tree in a clean process reproduces the committed
outputs. | Verification: the V6–V9 regeneration
procedure, recorded verbatim in PILOT-PACKAGE. |
Evidence: regenerated outputs + the recorded commands.

**R-18 Authorisation and freeze discipline.** The
driver refuses to execute the calibration matrix
without a PILOT-AUTHORISATION.json created after
construction acceptance, bound to the foundation hash
and the framing commit. This plan, once agreed, is
frozen by hash; changes require a plan amendment round.
| Criterion: execution attempt without the artefact
refuses and records the refusal. | Fixture: F-AUTH. |
Evidence: refusal record.

## 6. The calibration matrix (fixed in advance)

60 cells: 12 entries × R0–R4. Allocations per cell are
exactly OPERATION-MAPS-V2's paths (mechanical
verification split from semantic judgment per the V2
rules; T06 capture order is a hard specification at
every level). The matrix is fixed during calibration —
the profile under calibration is never consulted to
configure the cells that calibrate it (§4).

## 7. Negative-fixture catalogue (consolidated)

Conflicting binding declarations (R-05) · missing
binding metadata (R-05) · altered frozen dependency
(R-01) · invalid template version (R-09) · malformed
profile (R-09) · unresolvable evidence reference (R-15)
· unsupported profile claim / demonstrated-on-legacy
(R-06) · incorrect task-to-operation mapping —
deliberately mis-mapped cell (R-13) · missing internal
worker-call record — suppressed accounting wrapper
(R-12) · mechanical result not transmitted (R-11,
transmission assertion) · worker agreement without
evidence identification (R-11 F-PROBE-NEG) · defective
worker emission (R-10) · a task that cannot complete
under its selected allocation — recorded as a failed
run with reason, never silently re-allocated (R-08).

## 8. Build and inspection protocol

1. Alex's consolidated review amends this draft; the
   amended plan is frozen (sha256 recorded in the plan
   and in the return letter).
2. Remmy builds ONCE against the frozen plan and
   self-verifies against every criterion, returning the
   full evidence set the traceability rows name.
3. Alex inspects once, against the plan. Every finding
   is classified **plan defect** (the agreed
   requirements were incomplete, contradictory or
   insufficient) or **build defect** (the implementation
   failed an agreed requirement). Plan defects amend the
   plan first; build defects are corrected against the
   unchanged plan. Neither is silently absorbed.
4. On construction acceptance, Alex decides execution
   authorisation for the 60 runs. Construction
   acceptance does not itself authorise execution.

*Draft 1 — authored by Remmy, 2026-11-11. Awaiting
Alex's consolidated review.*
