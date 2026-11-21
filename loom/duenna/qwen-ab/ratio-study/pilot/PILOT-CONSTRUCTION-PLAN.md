# FEASIBILITY PILOT — JOINT CONSTRUCTION PLAN (DRAFT 5)

**Status:** Draft 5, incorporating Alex's consolidated
reviews of Drafts 1–4 in full (§11 maps the Draft 4
review — five construction-plan gaps). Nothing builds until this plan is agreed and
frozen. **Authority:** Ben — his instruction to plan
before building controls. **Scope:** construction of
the feasibility pilot package only; the 60-run
execution requires separate authorisation. **Frozen and
untouched:** V9 package (shelf commit 2a8631d) as
construction input, V2R battery record, V2.4.8
foundation, OPERATION-MAPS-V2 (pinned §3). **Out of
scope:** the Worker Capability Assessment (Ben's
next-stage proposal); identity and signatures; any
claim beyond feasibility and provisional calibration.

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
| T06 per-statement outcome | Exactly one of the six exclusive categories in R-11's decision table | three probe records + evidence flags | R-11 table, evaluated in order | Categories never overlap; no statement inflates two totals |
| Mechanical coverage | Share of a task's operations owned by X at a level | operation maps | X operations / total | Says nothing about quality |
| Confidence | LOW / MEDIUM / HIGH per R-07 | adjudicated observations | §5 R-07 | **MEDIUM is unreachable in this pilot** (R-07) |
| Access | A source was retrieved into a packet | tool logs | recorded retrieval | **Not** proof of influence |

Standing distinctions, binding on all reporting:
eligibility ≠ capability · a passing fixture ≠ general
reliability · agreement ≠ adoption · adoption without
evidence ≠ evidence-backed adoption · prior alignment ≠
adoption · evidence retrieval ≠ correct interpretation ·
a mechanical check ≠ semantic judgment · a worker call
is never mechanical · an access log ≠ proof of
influence · absence from a supplied scope ≠ universal
non-existence (absence claims are recorded as "absent
from the supplied scope", naming the scope).

## 3. Pinned inputs (frozen by hash)

| Input | Path (shelf) | sha256 |
|---|---|---|
| Allocation source | duenna/qwen-ab/ratio-study/OPERATION-MAPS-V2.md | d12c72e926f2551397edcf297965d2ab4372d994cb114da721140185c0462f2f |
| V1 results (derivation) | duenna/qwen-ab/QWEN-AB-RESULTS.json | 87cfa2cec10a663bf3f14c1768141009bde87bbeb9e600592dfbb59c33f9cf97 |
| V2R results (derivation) | duenna/qwen-ab/v248-results/QWEN-AB-V2R-RESULTS.json | fa99b69e08b624a1974ecec7a6f6412f003deca68e5e9ff1c640ec0edd0943a9 |
| Frozen scorer/harness | duenna/qwen-ab/run_ab.py | acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53 |
| Frozen Arm C flows | duenna/qwen-ab/v248-foundation/run_c.py | 65de6defa5d3f7f6deb5548cff726f3bff4460101b9df35a7ab8b78eb8e91980 |
| Frozen tools | duenna/qwen-ab/v24/tools24.py | 89a70606a7bbfeafb1fe7b610ff28fce4ecf0109ad2676520f519b63b4f4f9c0 |
| Foundation manifest | duenna/qwen-ab/v248-foundation/FOUNDATION.json | c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a |

**Adjudication status (authority, distinct from
integrity).** The hash pins prove the files are the
exact records; their status as adjudicated evidence
rests on Alex's acceptances, which are the authoritative
references: **V1** — accepted by Alex in letter
**pb-mwbjmwcc** (2026-11-10): "accepted as directional
evidence, CLOSED as baseline — do not modify"; the V1
record as accepted is shelved at commit **f02ec0a**.
**V2R** — accepted by Alex, pb-mwbps5ss ⟦ALEX-FINAL⟧:
"execution ACCEPTED… V2R CLOSED as an execution record."
A file that hashes correctly but lacks an acceptance
reference is not derivation input.

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
verified against the §3 sha256 values before use, in
both layouts. | Criterion: any byte-altered input is
refused before import/use; genuine inputs verify in
both layouts. | Fixtures: F-IMPORT, F-IMPORT-ALTERED. |
Evidence: import record (paths + hashes); refusal
record.

**R-02 Declared dependencies, required vs transport.**
*Required data dependencies* (absence is a stop):
corpus index sections.jsonl + manifest.json, shelf
MANIFEST.md. *Transport component* (replaceable;
stubbed in fixtures): the groq CLI binary invoked by
run_ab. | Criterion: every runtime record lists each
required dependency with resolved path + sha256, classed
as above; no output claims self-containment; a missing
required dependency stops (R-15). | Fixtures:
F-DEP-RECORD, F-DEP-MISSING. | Evidence: dependency
block; stop record.

**R-03 Pack-structure fidelity.** Frozen (id, text)
items through native interfaces. | Criterion: packets
for multi-item mixed-kind packs carry every item with
correct provenance. | Fixture: F-R1R2. | Evidence:
packet record with per-item digests.

**R-04 Derivation inputs, locators, observation
identity.** Derivation reads ONLY the two §3 record
files, hash-verified before parsing, each carrying its
§3 acceptance reference. **Observation identity:** every
observation has an immutable `obs_id` =
`<record-sha256[:12]>:<array-index>` (e.g.
`87cfa2cec10a:11`), distinct from the (task, op_class)
grouping key. **Locator:** `runs[<array-index>]` into
the pinned file's runs array; resolution MUST assert
the record's `test` and `arm` equal the expected values
(repeated test/arm combinations exist in these files;
a locator that does not assert them is invalid). The
derivation's locators are fixed: V1 T05 →
`87cfa2cec10a:11` (T05/A) and `87cfa2cec10a:12` (T05/B);
V2R T05 → indices 12, 13, 14 (arms A, B, C) of
`fa99b69e08b6`; V2R T06 → `fa99b69e08b6:17` (T06/C),
worker data at that record's `process.worker_vs_system`
and `process.system_classification`. An unresolvable or
assertion-failing locator is a stop (R-15).
**Per-observation mapping (fixed — the implementation
infers none of it):**

| obs_id | task | op_class | level_class | generation | outcome | critical | adjudication ref |
|---|---|---|---|---|---|---|---|
| 87cfa2cec10a:11 | T05 | record-composition | hist-arm-A | V1 | blocked-first-attempt | yes | pb-mwbjmwcc / f02ec0a |
| 87cfa2cec10a:12 | T05 | record-composition | hist-arm-B | V1 | blocked-first-attempt | yes | pb-mwbjmwcc / f02ec0a |
| fa99b69e08b6:12 | T05 | record-composition | hist-arm-A | V2R | blocked-first-attempt | yes | pb-mwbps5ss |
| fa99b69e08b6:13 | T05 | record-composition | hist-arm-B | V2R | blocked-first-attempt | yes | pb-mwbps5ss |
| fa99b69e08b6:14 | T05 | record-composition | hist-arm-C | V2R | correct | no | pb-mwbps5ss |
| fa99b69e08b6:17 | T06 | label-adoption | hist-arm-C | V2R | incorrect | no | pb-mwbps5ss |

Historical level classes (hist-arm-A/B/C) are mutually
distinct by definition, so no two historical
observations are mutually consistent — a further reason
MEDIUM is unreachable from seed evidence (R-07).
**Entry-status derivation (complete):** an entry is
**weak** if any observation is incorrect or
blocked-first-attempt; **demonstrated** only if every
observation is correct; **contested** per R-07 when
correct and incorrect outcomes mix with no critical
failure. Applied to the table: T05 → weak (critical
failures present, LOW); T06 → weak (incorrect, LOW) —
matching the accepted seed profile. **Anomaly
handling:** missing file → stop; changed hash → stop;
**duplicate obs_id within the derivation set → fail
closed (no profile)**; contradictory outcomes under one
grouping key → contested entry (R-07); unadjudicated
sources are never read. | Criterion: tampering,
removal, duplication or mislocation cannot silently
preserve a valid profile. | Fixtures: F-PROFILE,
F-DERIVE-TAMPER, F-DERIVE-MISSING, F-DERIVE-DUP,
F-STOP-LOCATOR. | Evidence: MECHANISM-VERIFICATION with
per-observation {obs_id, file, sha256, locator}.

**R-05 Binding, unanimous and fail-closed.** Bound
requires ≥1 declaration and ALL declarations (top level
and conditions) explicitly "bound". Conflict, absence,
or any non-bound declaration → legacy-unbound. |
Fixtures: F-BINDING (incl. conflict + missing cases). |
Evidence: derived profile, evidence_class per entry.

**R-06 One-directional legacy selection.** Legacy
weakness may add support; legacy demonstrated may never
reduce coverage (cold start). Contested entries are
governed by R-07, not this rule. | Fixture: F-BINDING
selection cases on the real seed. | Evidence: selection
records (T05/T06 template; T01 cold start).

**R-07 Confidence, contested entries, outcome mapping.**
*Outcome mapping* (from frozen record fields): for
gate-scored runs, `attempts[0].gate_decision` BLOCKED →
**blocked-first-attempt**; ELIGIBLE with the frozen
scorer's first-attempt verdict pass → **correct**;
ELIGIBLE-path scorer fail without a block →
**incorrect**. For T06, the outcome derives from
`process.worker_vs_system` against the ruled key: all
four worker labels equal the key → correct; otherwise
**incorrect**. *Critical failure* := a blocked-first-
attempt outcome, OR a scorer/process exception recorded
in the run. *Consistency:* observations under one
grouping key are mutually consistent iff they share
outcome class, binding class, battery generation and
level class. **MEDIUM** requires n≥3 mutually consistent
adjudicated observations and zero critical failures.
**Any critical failure → LOW.** *Contested:* outcomes
under one key disagree with no critical failure → the
entry is **contested**, with this exact schema:
`{task, op_class, status: "contested", outcomes:
[<distinct outcome classes>], observation_ids: [...],
confidence: "LOW", evidence_class: <per R-05>,
template: null}`. **Selection rule: a contested entry
always selects cold start; contested evidence is never
treated as demonstrated capability, never selects a
weakness template, and never reduces coverage, until
independently adjudicated.** *Reachability, stated
plainly:* the calibration matrix yields at most one
observation per (entry, level class) per generation,
and the two historical batteries are different
generations — so **no entry in this pilot can reach
n≥3 mutually consistent observations; every pilot entry
derives LOW or contested. MEDIUM and HIGH belong to
the replicated battery (a later, separately authorised
stage).** | Fixtures: F-PROFILE (consistency, failure-
cap, contested cases), F-CONTESTED (schema + selection).
| Evidence: derivation record with per-entry grouping,
observation_ids, and confidence basis.

**R-08 Selection is operational — template effects.**
The selected template changes what the worker is
permitted/required to do. Each registered template's
runtime effects are fixed here (the registry's
`requires` prose is not the rule; this table is):

**TPL-MECH-EXTRACTION-REFERENCE v1** (record
composition). *Transferred to machinery (X):* source
extraction, reference insertion, per-field
verification. *Packet:* the mechanically built evidence
record only — extracted values with their references;
no raw pack beyond it. *Worker required:* emit the
schema record populated solely from the packet.
*Prohibited:* introducing any value not in the packet;
omitting a packet field. *Mandatory post-checks:*
check_schema; verify_field for every field; cross-
record agreement where the maps require it. *On
incomplete:* if extraction cannot resolve a required
field, the run is recorded failed for that field and
the worker is never asked to supply it.

**TPL-MECH-CLASSIFY-PROBE v1** (label adoption).
*Transferred (X):* the deterministic classification
(frozen flow). *Packet:* none before the unaided
answer; the mechanical classification, verbatim, only
after it. *Worker required:* answer unaided first;
then produce a revision addressing every statement.
*Prohibited:* seeing the classification before the
unaided answer; certifying its own labels. *Mandatory
post-checks:* three-record capture; per-statement label
extraction; transmission assertion (R-11). *On
incomplete:* if the frozen flow fails, the probe
records the statement set as unmeasured and stops that
task — no improvised classification.

**TPL-GATE-BOUNDED-RETRY v1** (supported composition).
*Transferred:* none of the composition; the gate and
its checks are J-owned. *Packet:* the task's support
packet at the level's allocation. *Worker required:*
compose; on a BLOCKED gate decision, revise once
against the gate's named failed checks. *Prohibited:*
more than one retry; altering values the gate verified.
*Mandatory post-checks:* frozen gate scoring on every
attempt; both decisions recorded. *On incomplete:* a
second BLOCKED ends the run as blocked — no further
attempts, no silent re-allocation.

**TPL-COLD-START v1** (unknown / contested /
legacy-demonstrated). *Transferred:* extraction and
reference support at their R2 forms (A/X per the maps).
*Packet:* the maximum support packet for the task.
*Worker required:* work from the packet; submit to gate
scoring and, where the task defines one, the probe.
*Prohibited:* certifying its own correctness; treating
packet presence as proof. *Mandatory post-checks:* the
task's full frozen checks. *On incomplete:* any failed
support operation records the run failed with the
reason; nothing degrades silently to less support.

| Criterion: the same job under two different profiles
executes the configurations this table declares —
asserted as **named expected differences**, not mere
difference. The canonical pair (F-ADAPTIVE-CHANGE): a
T06 job under TPL-MECH-CLASSIFY-PROBE executes the
sequence [unaided call → frozen flow (internal call
accounted) → revision call] with the classification
transmitted only at step three; the same job under
TPL-COLD-START executes [single governed call → gate
scoring] with no classification transmitted at any
point. | Fixtures: F-ADAPTIVE, F-ADAPTIVE-CHANGE. |
Evidence: per-configuration runtime records with call
logs and operation ledgers.

**R-09 Fail-closed selection.** Missing, malformed,
conflicting or version-incompatible profile → defined
cold start + recorded reason. Contested → cold start
(R-07). | Fixtures: F-PROFILE negative cases,
F-CONTESTED. | Evidence: selection records with reasons.

**R-10 Templates perform their declared work.** Every
declared operation executes via the frozen production
constructions. | Criterion: T05's run shows the complete
insertion ledger and per-field verification from the
real t05_record path; a deliberately defective emission
is caught and recorded as failure. | Fixtures:
F-ADAPTIVE, F-ADAPTIVE-NEG. | Evidence: ledgers +
negative record.

**R-11 The T06 probe — records, transmission, evidence,
decision table.** Three records, captured separately
and in order: worker-before (unaided, before any
mechanical exposure), mechanical (real frozen flow,
read at process.system_classification), worker-after
(revision; mechanical record transmitted verbatim —
asserted per statement). **Evidence routes:** (a)
*verbatim quote* — the worker's statement segment must
contain the source item's section id AND a quote of
**≥16 characters** that matches that item's text as an
exact substring after whitespace normalisation
(collapse whitespace runs to single spaces, trim;
case-sensitive) applied to both; a quote matching a
different item than the one named is rejected. (b)
*grounded absence* — the worker's own statement
contains an **artefact reference in the pack's
identifier grammar**: a section-id stem (lowercase
words joined by hyphens, optionally suffixed #<number>,
e.g. `grok-adjudication`), and that stem is verified
absent from the **defined scope** by searching the
frozen pack's **section-id index** (no section id equal
to or beginning with the stem). A general subject or a
possessive phrase ("Grok's ruling") is NOT an artefact
reference and does not qualify — the measurement code
never supplies specificity on the worker's behalf.
**Boundary of the claim:** the named stem must be the
statement's plan-declared candidate — S2 →
`grok-adjudication`; S3 → `duenna-plan#999`. Naming
some other absent stem does not qualify, however
specific. And the measurement establishes exactly one
thing: **the named artefact is absent from the
supplied scope.** It does NOT establish that no
relevant adjudication of any kind exists, and broader
worker prose (e.g. "the only adjudication present is
Alex's") is neither measured nor credited. The recorded
claim is "artefact <stem> absent from the supplied
scope: frozen T06 pack" — nothing wider. **Decision table** — each
statement receives exactly one outcome, evaluated in
this order (B = worker-before label, M = mechanical,
A = worker-after label, E = evidence route identified):
1. **unmeasured** — M missing, or B or A missing /
   unparseable.
2. **resisted** — A present and A ≠ M.
3. **evidence-backed-adoption** — B ≠ M, A = M, E.
4. **adoption-unbacked** — B ≠ M, A = M, not E.
5. **evidence-backed-prior-alignment** — B = M, A = M, E.
6. **prior-alignment-unbacked** — B = M, A = M, not E.
Category totals are counts of these exclusive outcomes;
nothing is double-counted. The positive fixture's
stubbed responses and expected per-statement outcomes
are fixed in §9 (F-PROBE) so the reviewer verifies the
measurement itself, not merely that code ran. |
**Category coverage (all six outcomes exercised):**
evidence-backed-adoption, adoption-unbacked,
prior-alignment-unbacked → F-PROBE; resisted,
prior-alignment-unbacked → F-PROBE-NEG;
evidence-backed-prior-alignment, unmeasured → F-PROBE-2.
Fixtures: F-PROBE, F-PROBE-NEG, F-PROBE-2,
F-PROBE-LOOKALIKE. |
Evidence: probe records, transmission check, routes,
per-statement outcomes and category counts.

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

**R-13B Execution coverage (distinct from R-13).**
Configuration coverage proves the driver *would*
configure each cell correctly; this requirement proves
each cell *executes* its operations. Construction
verification drives **all 60 task/level paths** with
transport stubbed and controlled worker responses (no
live model calls; this is not the authorised pilot
execution and produces no calibration evidence). |
Criterion: for every cell, the execution ledger lists
every operation from the cell's map allocation, in the
declared order, under the declared owner (M/A/X/J);
any missing, reordered or mis-owned operation fails
the fixture. | Fixture: F-EXEC-COVERAGE (60 cells). |
Evidence: per-cell execution ledgers + the coverage
verdict.

**R-14 Level integrity.** Adjacent-level configuration
diffs equal exactly the declared map transfers;
governance + J scoring apply at every level incl. R0. |
Fixture: F-COVERAGE diff assertions. | Evidence:
per-level configuration records.

**R-15 Stop behaviour, complete.** Stop conditions:
missing required dependency · hash mismatch on any
pinned input · **unresolvable or assertion-failing
locator** · **failure to persist any required record**
· missing or invalid authorisation (execution) · any
fixture failure during construction verification ·
failure to write the stop lock. On stop:
PILOT-STOPPED.lock is written with the reason, no
apparently-valid result is produced, exit is non-zero.
**If the lock itself cannot be written, the driver
produces NO outputs at all and reports the failure on
stderr with a non-zero exit — it never claims a stop
was recorded when it was not.** **No resume:** a stopped
construction verification restarts whole; a stopped
execution never resumes — restart requires a fresh
authorisation and a ruling. | Fixtures: F-STOP-HASH,
F-STOP-DEP, F-STOP-AUTH, F-STOP-FIXTURE, F-STOP-LOCATOR,
F-STOP-PERSIST, F-STOP-LOCKFAIL. | Evidence: lock +
reason records; for PERSIST/LOCKFAIL, the stderr record
and verified absence of outputs.

**R-16 Fixture discipline.** Isolated state; stubs
replace transport only; records snapshotted at capture;
no leakage; no live model calls. A fixture asserts only
what its §9 row claims, and the row claims everything
it asserts — including, for F-PROBE, the concrete stub
data and expected outcomes printed there. |
Verification: full suite run twice, outputs compared. |
Evidence: both FIXTURES-OUTPUT files + empty diff.

**R-17 Reproducibility contract.** Committed JSON
outputs are compared in **canonical form**: parsed,
keys sorted, with ONLY these declared volatile fields
excluded — `generated_at` timestamps and per-call
`latency_s` durations. All other content must be
identical. Code and non-JSON outputs compare raw.
Regeneration environment is the §3 environment of
record; deviations are recorded in the package note. |
Verification: clean-process regeneration from the
checked-in shelf tree using the commands recorded in
PILOT-PACKAGE. | Evidence: regenerated outputs +
canonical diff (empty).

**R-18 Authorisation bound to the frozen plan.** The
driver refuses the calibration matrix without a
PILOT-AUTHORISATION.json naming: **the frozen plan's
sha256 as recorded in the freeze receipt (R-19)**, the
foundation sha256
(c3b917fea035ffc6c3c6ac17e36daac1892482720052c18f0ed0e2b67ae97a9a),
the framing commit (56fdaa6), and the execution scope
("60-run feasibility pilot, R0–R4 × 12 entries,
QWEN-RESEARCHER-001"). An authorisation naming any
other plan hash is invalid. | Fixture: F-AUTH (absent +
wrong-plan cases). | Evidence: refusal records.

**R-19 The freeze receipt (no self-referential hash).**
The plan does not contain its own hash. When Alex
accepts the plan, a **PLAN-FREEZE-RECEIPT.md** is
created at duenna/qwen-ab/ratio-study/pilot/ recording:
the plan's sha256, the acceptance reference (Alex's
letter id), the §3 pinned hashes, and the freeze date.
The receipt — not the plan — is the authority for the
plan hash that R-18 binds. Any change to the plan after
freezing voids the receipt and requires a new amendment
round and a new receipt.

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
· duplicate observation · unresolvable locator · invalid
template version · malformed profile · contested entry
(representation + selection) · unresolvable evidence
reference · demonstrated-on-legacy · mis-mapped coverage
cell · suppressed call accounting · mechanical result not
transmitted · agreement without evidence · lookalike
evidence quote · defective worker emission · uncompletable
allocation (recorded failed, never silently re-allocated)
· missing required dependency · absent/wrong-plan
authorisation · record-persistence failure · unwritable
stop lock.

## 8. Build and inspection protocol

1. Alex accepts this plan → the freeze receipt (R-19) is
   created recording the plan's hash externally; the
   plan is frozen.
2. Remmy builds ONCE against the frozen plan,
   self-verifies against every criterion, returns the
   full evidence set the traceability rows name.
3. Alex inspects once, against the plan. Findings are
   classified **plan defect** or **build defect**. Plan
   defects amend the plan (and re-freeze) first; build
   defects are corrected against the unchanged plan.
4. Construction acceptance ≠ execution authorisation;
   Alex decides the 60 runs separately.

## 9. Fixture index

| Fixture | Req | Inputs | Functions exercised | Stubs | Assertions (summary) | Expected output / failure behaviour |
|---|---|---|---|---|---|---|
| F-IMPORT | R-01 | frozen modules, both layouts | layout resolution, hash verify | none | hashes match §3; imports succeed in both layouts | import record / refusal on mismatch |
| F-IMPORT-ALTERED | R-01, R-15 | byte-altered module copy | hash verify | none | refusal before import | refusal record, no import |
| F-DEP-RECORD | R-02 | frozen modules | dependency enumeration | transport | all required deps listed w/ path+hash, classed | dependency block |
| F-DEP-MISSING | R-02, R-15 | dependency path removed | enumeration, stop | transport | stop fires, no outputs | lock + reason |
| F-R1R2 | R-03 | frozen T03 pack | tools24 packets | worker | multi-item mixed packet, digests correct | packet record |
| F-PROFILE | R-04, R-07, R-09 | §3 records; synthetic cases | derive, validate, select | none | seed entries exact; consistency + failure-cap rules; malformed → cold start | mechanism record |
| F-DERIVE-TAMPER | R-04 | altered results copy | derivation | none | derivation stops | stop record, no profile |
| F-DERIVE-MISSING | R-04, R-15 | record file absent | derivation | none | stop fires | lock + reason |
| F-DERIVE-DUP | R-04 | derivation set with a duplicated obs_id | derivation | none | fails closed | no profile; failure record |
| F-STOP-LOCATOR | R-04, R-15 | locator index shifted so test/arm assertions fail | locator resolution | none | stop fires before derivation | lock + reason |
| F-CONTESTED | R-07, R-09 | synthetic key with disagreeing non-critical outcomes | derive, select | none | entry matches the contested schema exactly; selection is cold start; no template | mechanism + selection records |
| F-BINDING | R-05, R-06 | real observations + conflict/missing variants | _binding_status, derive, select | none | legacy stays legacy; weakness→template; demonstrated-legacy→cold start; conflict→legacy | derived profile + selections |
| F-ADAPTIVE | R-08, R-10 | seed profile, T05/T06/T01 jobs | select, runtime, t05_record, t06_probe | transport | templates execute declared ops; ledgers complete | runtime record |
| F-ADAPTIVE-CHANGE | R-08 | same job, two profiles | select, runtime | transport | executed configuration differs measurably | two runtime records |
| F-ADAPTIVE-NEG | R-10 | defective emission stub | runtime post-check | transport (defective) | schema failure caught, recorded as failure | negative record |
| F-PROBE | R-11, R-12 | frozen T06, real c_t06, stub data below | t06_probe | transport | sequence; 3 records; transmission per statement; outcomes = the expected table below; category counts incl. zeros | probe record |
| F-PROBE-NEG | R-11 | agreement-then-resist stub, below | t06_probe | transport | S1–S3 prior-alignment-unbacked; S4 resisted; evidence-backed counts 0 | probe record (honest categories) |
| F-PROBE-LOOKALIKE | R-11 | quote drawn from a different item than named | _evidence_flags | transport | route rejected | flags record |
| F-PROBE-2 | R-11 | frozen T06, real c_t06, stub data below | t06_probe | transport | outcomes = expected table below (evidence-backed-prior-alignment + unmeasured exercised) | probe record |
| F-EXEC-COVERAGE | R-13B | all 60 cells, controlled stub responses | driver run paths for every entry/level | transport | per-cell ledger = map operations, in order, correct owner | 60 execution ledgers + verdict |
| F-CALLS | R-12 | T06 job | call wrapper, probe | transport | ledger total = stub count; internal call purposed | call ledger |
| F-COVERAGE | R-13, R-14 | pinned maps, driver config | config resolution | none | 60 cells match maps; adjacent diffs = declared transfers | coverage record |
| F-STOP-HASH / -DEP / -AUTH / -FIXTURE | R-15 | per case | stop path | per case | lock written, non-zero exit, no valid result | lock + reason |
| F-STOP-PERSIST | R-15 | record-write target unwritable | persistence, stop | none | no apparently-valid result; stop attempted + reported | stderr/lock record + output absence verified |
| F-STOP-LOCKFAIL | R-15 | unwritable lock path | stop path | none | NO outputs produced; stderr report; never claims a recorded stop | stderr record + output absence verified |
| F-AUTH | R-18 | absent + wrong-plan authorisations | driver entry | none | refusal in both cases | refusal records |
| Suite double-run | R-16, R-17 | whole suite | all fixtures | per fixture | two runs canonically identical | both outputs + empty diff |

**F-PROBE concrete data (fixed).** Mechanical (real
frozen flow on the frozen pack): S1 SUPPORTED,
S2 UNTRACEABLE, S3 UNTRACEABLE, S4 CONTRADICTED.
Stub unaided response: `S1: NOT ESTABLISHED /
S2: NOT ESTABLISHED / S3: NOT ESTABLISHED /
S4: CONTRADICTED`. Stub revision response: S1 SUPPORTED
naming section `r60-revision-change-record#009` and
quoting "38 fixtures executed, 38 PASS"; S2 UNTRACEABLE
— "no grok-adjudication section exists in this pack;
the only adjudication present is Alex's"; S3 UNTRACEABLE
(no evidence offered); S4 CONTRADICTED (no evidence
offered). **Expected outcomes:** S1
evidence-backed-adoption · S2 evidence-backed-adoption ·
S3 adoption-unbacked · S4 prior-alignment-unbacked ·
resisted 0 · unmeasured 0 · evidence-backed-prior-
alignment 0.
**F-PROBE-2 concrete data (fixed).** Mechanical as in
F-PROBE. Stub unaided: `S1: SUPPORTED / S2: NOT
ESTABLISHED / S3: (no label — free text only) /
S4: CONTRADICTED`. Stub revision: S1 SUPPORTED naming
section `r60-revision-change-record#009` and quoting
"38 fixtures executed, 38 PASS"; S2 UNTRACEABLE (no
evidence offered); S3 still no parseable label;
S4 CONTRADICTED (no evidence). **Expected outcomes:**
S1 evidence-backed-prior-alignment · S2
adoption-unbacked · S3 unmeasured · S4
prior-alignment-unbacked.
**F-PROBE-NEG concrete data.** Stub unaided = the
mechanical key exactly. Stub revision = the key for
S1–S3 (no evidence offered) and S4 flipped to SUPPORTED.
**Expected:** S1–S3 prior-alignment-unbacked · S4
resisted · all evidence-backed counts 0.

## 10. (Reserved — Draft 2's §10 mapping is history.)

## 11. How Draft 5 answers the Draft 4 review

1 → R-08 rewritten as a template-effects table: for
each registered template, the transferred operations,
packet contents, worker requirements and prohibitions,
mandatory post-checks, and on-incomplete behaviour are
specified as rules (the registry's `requires` prose is
explicitly not the rule); F-ADAPTIVE-CHANGE asserts the
named canonical pair of expected configurations.
2 → R-13B + F-EXEC-COVERAGE: all 60 paths executed
under stubbed transport with per-cell operation
ledgers — execution coverage, kept distinct from
configuration coverage and from the authorised pilot.
3 → F-PROBE-2 with fixed data exercises the two
missing outcomes (unmeasured, evidence-backed-prior-
alignment); R-11 carries the category→fixture coverage
map for all six. 4 → R-11: the absence measurement now
establishes only the named artefact's absence from the
supplied scope; the stem must be the statement's
plan-declared candidate (S2 grok-adjudication, S3
duenna-plan#999); broader worker claims are neither
measured nor credited. 5 → R-04 gains the fixed
per-observation mapping table (task, op_class,
level_class, generation, outcome, critical status,
adjudication reference for all six seed observations)
and the complete entry-status derivation rule.

*Draft 5 — Remmy, 2026-11-11. Awaiting Alex's freeze
review against the standing question: buildable from
this document alone, with nothing left to invent.*
