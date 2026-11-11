# FEASIBILITY PILOT — JOINT CONSTRUCTION PLAN (DRAFT 2)

**Status:** Draft 2, incorporating Alex's consolidated
review of Draft 1 in full (his nine points, §10 of this
document maps them). Nothing builds until this plan is
agreed and frozen. **Authority:** Ben — his instruction
to plan before building controls. **Scope:** construction
of the feasibility pilot package only; the 60-run
execution requires separate authorisation. **Frozen and
untouched:** V9 package (2a8631d) as construction input,
V2R battery record, V2.4.8 foundation, OPERATION-MAPS-V2
(pinned §3). **Out of scope:** the Worker Capability
Assessment (Ben's next-stage proposal); identity and
signatures; any claim beyond feasibility and provisional
calibration.

**Roles.** Remmy: author, builder, self-verifier. Alex:
independent review and acceptance contract. Ben:
authority on the intended system and its boundaries.

---

## 1. What the pilot can and cannot establish

**Can:** the capability-profile mechanism works end to
end — profiles derive from pinned adjudicated evidence,
selection configures real execution, allocations differ
by level as mapped, measurements are recorded honestly,
and one worker's (Qwen's) first provisional profile
entries result from the calibration matrix.
**Cannot:** broad capability claims; saturation points;
statistical comparisons (n=1 per cell); semantic truth
of mechanical classifications; that agreement equals
understanding.

## 2. Definitions — every measurement, precisely

| Metric | Definition | Inputs | Calculation | Limitation |
|---|---|---|---|---|
| Eligibility | Output passed the frozen release gate | gate scorers | frozen gate result | **Not** demonstrated capability |
| Worker correctness | Worker's own output matches the frozen key | worker raw output | frozen scorers on the original output | One observation per run |
| System correctness | Final artefact after mechanical steps is correct | final output | frozen scorers | Credits the system, not the worker |
| Adoption | Per statement: worker-before ≠ mechanical AND worker-after = mechanical | three probe records | per-statement comparison | A label change is not understanding |
| Evidence-backed adoption | Adoption AND the worker identified the supporting evidence by a §5 R-11 route | probe records + evidence flags | subset of adoption | Route is mechanical; interpretation may still err |
| Evidence-backed prior alignment | Worker-before = mechanical already AND the worker identified the supporting evidence in its revision | probe records + flags | recorded **separately** — never counted as adoption | Alignment is not a change |
| Mechanical coverage | Share of a task's operations owned by X at a level | operation maps | X operations / total | Says nothing about quality |
| Confidence | LOW / MEDIUM / HIGH per R-07 | adjudicated observations | §5 R-07 | Pilot ceiling MEDIUM |
| Access | A source was retrieved into a packet | tool logs | recorded retrieval | **Not** proof of influence |

Standing distinctions, binding on all reporting:
eligibility ≠ capability · a passing fixture ≠ general
reliability · agreement ≠ adoption · adoption without
evidence ≠ evidence-backed adoption · prior alignment ≠
adoption · evidence retrieval ≠ correct interpretation ·
a mechanical check ≠ semantic judgment · a worker call
is never mechanical · an access log ≠ proof of
influence · **absence from a supplied scope ≠ universal
non-existence** (all absence claims are recorded as
"absent from the supplied scope", naming the scope).

## 3. Pinned inputs (frozen by hash)

| Input | Path (shelf) | sha256 |
|---|---|---|
| Allocation source | duenna/qwen-ab/ratio-study/OPERATION-MAPS-V2.md | d12c72e926f2551397edcf297965d2ab4372d994cb114da721140185c0462f2f |
| V1 results (derivation) | duenna/qwen-ab/QWEN-AB-RESULTS.json | 87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97 |
| V2R results (derivation) | duenna/qwen-ab/v248-results/QWEN-AB-V2R-RESULTS.json | fa99b69e08b624a1974ecec7a6f6412f003deca68e5e9ff1c640ec0edd0943a9 |
| Frozen code | run_ab.py / run_c.py / tools24.py | per R-01 pinned values in the package |

Runtime environment of record: Python 3.12.3, Linux,
no PILOT_* environment overrides (default dual-layout
resolution), working directory = the package directory.

## 4. Components and the four activities

**Driver (pilot.py):** layout resolution, hash-verified
imports, the fixed calibration matrix, the adaptive
runtime, call accounting, run records, authorisation
refusal, stop enforcement. Worker calls only through
run_ab.call_qwen (wrapped). Never edits frozen modules.
**Profile mechanism (profile.py):** schema, validation,
derivation, binding, confidence, selection, cold start —
pure functions over explicit inputs. **Template
registry:** versioned objects (identity, version,
requires, allocation effects); unknown or mismatched
templates fail closed. **Frozen tools/flows:** used
as-is, hash-pinned; external dependencies declared
(R-02). **Fixtures:** real functions, transport stubbed
only, isolated state.

**Calibration** (fixed matrix) establishes what a
worker demonstrated. **Selection** uses pre-existing
evidence to configure a job. **Runtime** executes.
**Adjudication** (Alex) evaluates independently. A
calibration result never becomes proof inside its own
execution; the pilot never modifies the profile from
in-flight outcomes; selection reads only the profile
that existed before the run.

## 5. Requirements — traceability

**R-01 Frozen imports, incl. the allocation source.**
run_ab, run_c, tools24 and OPERATION-MAPS-V2 are
verified against §3/package-pinned sha256 before use,
in both layouts. | Criterion: any byte-altered input is
refused before import/use; genuine inputs verify in
both layouts. | Fixtures: F-IMPORT, F-IMPORT-ALTERED. |
Evidence: import record (paths + hashes); refusal
record.

**R-02 Declared dependencies, required vs transport.**
*Required data dependencies* (the frozen workflow reads
them; absence is a stop): corpus index
sections.jsonl + manifest.json (tools24/run_ab source
data), shelf MANIFEST.md (shelf_lookup source).
*Transport component* (replaceable; stubbed in
fixtures; not a data dependency): the groq CLI binary
invoked by run_ab. | Criterion: every runtime record
lists each required dependency with resolved path +
sha256, classed as above; no output claims the package
is self-contained; a missing required dependency stops
(R-15). | Fixtures: F-DEP-RECORD, F-DEP-MISSING. |
Evidence: dependency block in outputs; stop record for
the missing case.

**R-03 Pack-structure fidelity.** Frozen (id, text)
items through native interfaces. | Criterion: packets
for multi-item mixed-kind packs carry every item with
correct provenance. | Fixture: F-R1R2. | Evidence:
packet record with per-item digests.

**R-04 Derivation inputs, frozen and adjudicated.**
Derivation reads ONLY the two §3 record files,
hash-verified before parsing. An observation qualifies
only if its source record is an accepted adjudicated
result: V1 (Alex-adjudicated, closed baseline) and V2R
(Alex-accepted execution record) — file presence alone
is not qualification; the hash pin is the qualification
check. **Locator format:** `runs[<entry>/<arm>]` into
the results array, plus, for T06 worker data,
`runs[T06/C].process.worker_vs_system`. Resolution is
mechanical; an unresolvable locator is a stop (R-15).
**Anomalies:** a missing record file → stop; a changed
hash → stop; duplicate observation keys → derivation
fails closed (no profile); contradictory outcomes for
the same key → the entry derives as **contested**
(R-07); unadjudicated sources are never read. |
Criterion: tampering with or removing a referenced
record cannot silently preserve a valid profile — it
stops or fails closed. | Fixtures: F-PROFILE,
F-DERIVE-TAMPER, F-DERIVE-MISSING. | Evidence:
MECHANISM-VERIFICATION with per-observation references
{file, sha256, locator}.

**R-05 Binding, unanimous and fail-closed.** Bound
requires ≥1 declaration and ALL declarations (top level
and conditions) explicitly "bound". Conflict, absence,
or any non-bound declaration → legacy-unbound. |
Fixtures: F-BINDING (incl. conflict + missing cases). |
Evidence: derived profile, evidence_class per entry.

**R-06 One-directional legacy selection.** Legacy
weakness may add support; legacy demonstrated may never
reduce coverage (cold start). | Fixture: F-BINDING
selection cases on the real seed. | Evidence: selection
records (T05/T06 template; T01 cold start).

**R-07 Confidence, mathematically explicit.** An entry
groups observations by (task, op_class). Observations
are **mutually consistent** iff they share: the same
outcome classification (correct / incorrect /
blocked-first-attempt), the same binding class (bound /
legacy-unbound), and compatible conditions (same
battery generation and level class). **MEDIUM** requires
n≥3 mutually consistent adjudicated observations and
zero critical failures. **Any critical failure → LOW.**
**Disagreement without a critical failure → the entry's
status is "contested", confidence LOW, and BOTH outcomes
are recorded** — derivation never selects the outcome
that yields higher confidence. HIGH is unreachable in
the pilot. | Fixtures: F-PROFILE (consistency, failure-
cap, contested cases). | Evidence: derivation record
with per-entry sample counts, consistency grouping and
confidence basis.

**R-08 Selection is operational.** The selected template
changes what the worker is permitted/required to do
(packet content, required operations, post-checks). |
Criterion: the same job under two different profiles
executes measurably different configurations (calls,
operations, checks) — not merely different printed
records. | Fixtures: F-ADAPTIVE, F-ADAPTIVE-CHANGE. |
Evidence: per-configuration runtime records with call
logs and operation ledgers.

**R-09 Fail-closed selection.** Missing, malformed,
conflicting or version-incompatible profile → defined
cold start + recorded reason; no silent proceed. |
Fixtures: F-PROFILE negative cases. | Evidence:
selection records with reasons.

**R-10 Templates perform their declared work.** Every
declared operation executes via the frozen production
constructions. | Criterion: T05's run shows the complete
insertion ledger and per-field verification from the
real t05_record path; a deliberately defective emission
is caught and recorded as failure. | Fixtures:
F-ADAPTIVE, F-ADAPTIVE-NEG. | Evidence: ledgers +
negative record.

**R-11 The T06 probe — records, transmission, evidence.**
Three records, captured separately and in order:
worker-before (unaided, before any mechanical
exposure), mechanical (real frozen flow, read at
process.system_classification), worker-after (revision;
mechanical record transmitted verbatim — asserted per
statement). **Evidence routes:** (a) *verbatim quote* —
the quote must name its source item (section id) and is
verified as a substring of **that item's** text, not of
the pack at large; (b) *grounded absence* — the
worker's own statement names the specific artefact, and
the artefact is verified absent from the **defined
scope** (the frozen T06 pack); the recorded claim is
"absent from the supplied scope: frozen T06 pack".
**Categories recorded separately per statement:**
adopted / evidence-backed adoption / evidence-backed
prior alignment / resisted / unclear — prior alignment
is never summed into adoption; agreement with no
evidence route is its own honest category. The fixture
recomputes all categories independently and asserts
each, including zero counts. | Fixtures: F-PROBE
(positive), F-PROBE-NEG (agreement without evidence →
evidence-backed categories empty), F-PROBE-LOOKALIKE (a
quote drawn from a different item than the one named →
route rejected). | Evidence: probe records, transmission
check, per-statement routes and category counts.

**R-12 Total call accounting.** Every worker call —
driver, probe, frozen-flow internal — recorded with a
purpose tag; none counted or described as mechanical. |
Criterion: totals reconcile with the transport stub's
count. | Fixture: F-CALLS. | Evidence: per-run ledger.

**R-13 Coverage completeness.** All 12 entries × 5
levels; per-operation allocations exactly per the
pinned maps; the driver's resolved configuration per
cell matches mechanically; no operation disappears
between maps, driver, logs, results. | Fixture:
F-COVERAGE (60 cells). | Evidence: cell-by-cell coverage
record; discrepancies: none allowed.

**R-14 Level integrity.** Adjacent-level configuration
diffs equal exactly the declared map transfers;
governance + J scoring apply at every level incl. R0. |
Fixture: F-COVERAGE diff assertions. | Evidence:
per-level configuration records.

**R-15 Stop behaviour, complete.** Stop conditions:
missing required dependency · hash mismatch on any
pinned input · unresolvable record reference · missing
or invalid authorisation (execution) · any fixture
failure during construction verification · failure to
persist records. On stop: PILOT-STOPPED.lock is written
with the reason, no apparently-valid result is
produced, exit is non-zero. **If the lock itself cannot
be written, the driver produces NO outputs at all and
reports the failure on stderr with a non-zero exit — it
must never claim a stop was recorded when it was not.**
**No resume:** a stopped construction verification
restarts whole; a stopped execution never resumes —
restart requires a fresh authorisation and a ruling. |
Fixtures: F-STOP-HASH, F-STOP-DEP, F-STOP-AUTH,
F-STOP-FIXTURE, F-STOP-LOCKFAIL (lock path unwritable).
| Evidence: lock + reason records; for LOCKFAIL, the
stderr record and the verified absence of outputs.

**R-16 Fixture discipline.** Isolated state; stubs
replace transport only; records snapshotted at capture;
no leakage between cases; no live model calls. A fixture
asserts only what its §9 index row claims, and the row
claims everything it asserts. | Verification: full suite
run twice, outputs compared. | Evidence: both
FIXTURES-OUTPUT files + empty diff.

**R-17 Reproducibility contract.** Committed JSON
outputs are compared in **canonical form**: parsed,
keys sorted, with ONLY these declared volatile fields
excluded — `generated_at` timestamps and per-call
`latency_s` durations. All other content must be
identical. Code and non-JSON outputs compare raw.
Regeneration environment is the §3 environment of
record; any deviation is recorded in the package note.
| Verification: clean-process regeneration from the
checked-in shelf tree using the commands recorded in
PILOT-PACKAGE. | Evidence: regenerated outputs +
canonical diff (empty).

**R-18 Authorisation bound to the plan.** The driver
refuses the calibration matrix without a
PILOT-AUTHORISATION.json naming: the frozen plan's
sha256, the foundation sha256 (c3b917fe…), the framing
commit (56fdaa6), and the execution scope ("60-run
feasibility pilot, R0–R4 × 12 entries,
QWEN-RESEARCHER-001"). An authorisation for any other
plan hash is invalid. This plan, once agreed, is frozen
by hash; changes require an amendment round. | Fixture:
F-AUTH (absent + wrong-plan cases). | Evidence: refusal
records.

## 6. The calibration matrix (fixed in advance)

60 cells: 12 entries × R0–R4, allocations exactly per
the pinned maps (mechanical verification split from
semantic judgment; T06 capture order is a hard
specification at every level). The matrix never consults
the profile it is calibrating.

## 7. Negative-fixture catalogue (consolidated)

Conflicting binding declarations · missing binding
metadata · altered frozen dependency · altered maps ·
tampered derivation record · missing derivation record
· invalid template version · malformed profile ·
unresolvable evidence reference · demonstrated-on-legacy
· mis-mapped coverage cell · suppressed call accounting
· mechanical result not transmitted · agreement without
evidence · lookalike evidence quote · defective worker
emission · uncompletable allocation (recorded failed,
never silently re-allocated) · missing required
dependency · absent/wrong-plan authorisation ·
unwritable stop lock.

## 8. Build and inspection protocol

1. Alex's review amends this draft; the agreed plan is
   frozen (sha256 recorded in plan + return letter).
2. Remmy builds ONCE against the frozen plan,
   self-verifies against every criterion, returns the
   full evidence set the traceability rows name.
3. Alex inspects once, against the plan. Findings are
   classified **plan defect** or **build defect**. Plan
   defects amend the plan first; build defects are
   corrected against the unchanged plan.
4. Construction acceptance ≠ execution authorisation;
   Alex decides the 60 runs separately.

## 9. Fixture index

| Fixture | Req | Inputs | Functions exercised | Stubs | Assertions (summary) | Expected output / failure behaviour |
|---|---|---|---|---|---|---|
| F-IMPORT | R-01 | frozen modules, both layouts | layout resolution, hash verify | none | hashes match pins; imports succeed in both layouts | import record / refusal on mismatch |
| F-IMPORT-ALTERED | R-01, R-15 | byte-altered module copy | hash verify | none | refusal before import | refusal record, no import |
| F-DEP-RECORD | R-02 | frozen modules | dependency enumeration | transport | all required deps listed w/ path+hash, classed | dependency block |
| F-DEP-MISSING | R-02, R-15 | dependency path removed | enumeration, stop | transport | stop fires, no outputs | lock + reason |
| F-R1R2 | R-03 | frozen T03 pack | tools24 packets | worker | multi-item mixed packet, digests correct | packet record |
| F-PROFILE | R-04, R-07, R-09 | §3 records; synthetic malformed profiles | derive, validate, select | none | seed entries exact; consistency/contested rules; malformed → cold start | mechanism record |
| F-DERIVE-TAMPER | R-04 | altered results copy | derivation | none | derivation stops/fails closed | stop record, no profile |
| F-DERIVE-MISSING | R-04, R-15 | record file absent | derivation | none | stop fires | lock + reason |
| F-BINDING | R-05, R-06 | real observations + conflict/missing variants | _binding_status, derive, select | none | legacy stays legacy; weakness→template; demonstrated-legacy→cold start; conflict→legacy | derived profile + selections |
| F-ADAPTIVE | R-08, R-10 | seed profile, T05/T06/T01 jobs | select, runtime, t05_record, t06_probe | transport | templates execute declared ops; ledgers complete | runtime record |
| F-ADAPTIVE-CHANGE | R-08 | same job, two profiles | select, runtime | transport | executed configuration differs measurably | two runtime records |
| F-ADAPTIVE-NEG | R-10 | defective emission stub | runtime post-check | transport (defective) | schema failure caught, recorded as failure | negative record |
| F-PROBE | R-11, R-12 | frozen T06, real c_t06 | t06_probe | transport | sequence; 3 records exact; transmission per statement; routes; categories recomputed incl. zeros | probe record |
| F-PROBE-NEG | R-11 | agreement-only stub | t06_probe | transport | agreement recorded; evidence-backed categories empty | probe record (honest negative) |
| F-PROBE-LOOKALIKE | R-11 | quote from wrong item | _evidence_flags | transport | route rejected | flags record |
| F-CALLS | R-12 | T06 job | call wrapper, probe | transport | ledger total = stub count; internal call purposed | call ledger |
| F-COVERAGE | R-13, R-14 | pinned maps, driver config | config resolution | none | 60 cells match maps; adjacent diffs = declared transfers | coverage record |
| F-STOP-HASH / -DEP / -AUTH / -FIXTURE | R-15 | per case | stop path | per case | lock written, non-zero exit, no valid result | lock + reason |
| F-STOP-LOCKFAIL | R-15 | unwritable lock path | stop path | none | NO outputs produced; stderr report; never claims a recorded stop | stderr record + output absence verified |
| F-AUTH | R-18 | absent + wrong-plan authorisations | driver entry | none | refusal in both cases | refusal records |
| Suite double-run | R-16, R-17 | whole suite | all fixtures | per fixture | two runs canonically identical | both outputs + empty diff |

## 10. How Draft 2 answers the consolidated review

1 → §2 categories + R-11 (three categories, separately
asserted, zeros included). 2 → R-11 routes (quote bound
to its named item; absence scoped and worded as scoped)
+ F-PROBE-LOOKALIKE. 3 → §3 pins + R-04 (hash as
qualification, locator format, anomaly handling,
tamper fixtures). 4 → R-07 (consistency defined;
contested state; never resolve upward). 5 → §3 maps pin
+ R-02 (required vs transport; missing-dependency
fixture). 6 → R-15 (five stop cases incl. lock-failure;
no-resume rule). 7 → R-18 (plan hash inside the
authorisation binding). 8 → R-17 (canonical comparison,
declared volatile fields, environment of record).
9 → §9 fixture index (every fixture mapped: requirement,
inputs, functions, stubs, assertions, expected behaviour).

*Draft 2 — Remmy, 2026-11-11. Awaiting Alex's verdict
against his own test: buildable from this document
alone, with no requirement left to interpret.*
