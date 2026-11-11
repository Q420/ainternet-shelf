# APPROVED POOL — RECEIPT AND READINESS GATE
# IMPLEMENTATION SPECIFICATION 01

**Status:** BUILD SPECIFICATION (Phase 5,
third component) — prepared for Alex's review
and adoption decision under the amended Phase 4
delegation (shelved record:
duenna/PHASE-4-DELEGATION-RECORD-01.md, commit
2e6a639). Adoption of this specification is a
design decision only: it does not authorise
implementation, live receipt admission,
readiness enforcement, migration, publication,
generation zero, or a Dictionary freeze.

**Prepared by:** Remmy — from the adopted
design sources on the Shelf, read from the
Shelf copies.

**Design basis (shelf pins):**
- Phase 4 Receipt and Readiness Specification
  01 — commit 3aa3c53, blob 1e60a46d…
  (receipt model §2, consumption §3, readiness
  §4, correction/reliance §5, retention §6,
  authority §7, schema outline §8, acceptance
  criteria §10, named instances §14, R1–R4
  rulings and examiner appointment §15)
- Sweep Implementation Specification 01 Rev 4
  — commit b51c0f84, blob dbed3132…; ADOPTED
  (Alex's adoption decision, commit 1c713768,
  blob 9800aca6…). Its §9 candidate-receipt
  contract is this gate's intake contract.
- Ledger Implementation Specification 01 Rev 4
  — commit 8eed8d9c, blob 82716823…
  (unadopted review candidate; identity
  resolution and pin verification only — this
  gate performs no ledger mutation)
- Phase 2 Ledger Atomicity Specification 01 —
  commit 5a80df42, blob 1f8deb2d… (upward-only
  identity resolution and walk receipts)

Where this build specification and a
design-basis artefact differ, the design-basis
artefact governs.

**Revision:** Rev 1 — first issue.

---

## 1. Purpose and boundary

The Approved Pool produces evidence in many
places. Producers — above all the sweep engine
— emit **candidate** receipts: complete,
honest, self-consistent claims about what was
checked. A candidate is not an admitted record
and confers nothing. This component is the
**gate** between candidates and the
programme's admitted record:

- it validates candidates against the Phase 4
  receipt model before admitting them;
- it admits receipts into the canonical
  receipt store under the R2 authority;
- it issues scoped readiness dispositions
  under R2/R3, and refuses to issue any
  disposition wider than the evidence;
- it admits corrections and supersessions
  under R2/R4, propagates their effects to
  known reliance, and never rewrites history;
- it enforces the R1 retention rules at the
  only points where they can be enforced by
  machinery: at admission (evidence residence)
  and by the absence of any disposal path.

The gate **decides nothing about truth**. It
decides what enters the admitted record, under
whose authority, with what scope, and with
what stated limitations. A receipt admitted
through a broken gate would be worse than no
receipt: the gate's failure modes therefore
fail closed, and its refusals are named,
recorded outcomes — not silent drops.

## 2. Components

| Component | Responsibility |
|---|---|
| M-INTAKE | Candidate validation: schema, digests, scope recomputation, evidence resolution, authority and separation checks (§4) |
| M-ADMIT | Admission into the receipt store under R2; serial and locator assignment; idempotency (§5) |
| M-READY | Readiness disposition issuance and verification under R2/R3 (§6) |
| M-CORRECT | Correction/supersession admission and reliance propagation under R2/R4 (§7) |
| M-RETAIN | Retention rules at admission; holds; backup obligations as operational requirements (§8) |
| M-EXAM | Examination evidence interface: examiner records, dispositions, limitations (§9) |

All six operate on one **receipt store**: an
append-only record set whose canonical
residence is the AInternet Shelf Git
repository (R1.1). The store's append
mechanics follow the same single-snapshot
compare-and-swap discipline specified for the
ledger, under a separate authority basis (§5):
the bounded Phase 2 evidence for conditional
ref updates is inherited as *candidate*
mechanics only, with the same limits stated
there. The receipt store is not the ledger:
it holds receipts, readiness dispositions and
correction records, not item/version heads;
G1 (ledger location) is untouched by this
specification, and R1.1 expressly does not
decide it.

## 3. Records

### 3.1 The admitted receipt

An admitted receipt is the candidate (§4.1)
plus an **admission block**:

- `admission_serial`: a monotonic store-local
  serial assigned at admission (gaps
  preserved; a refused admission consumes no
  serial). The serial is a **locator
  component**, on the BridgePress precedent —
  it is not a governed `receipt_id`. Governed
  receipt identity awaits the Phase 1 identity
  decisions (G1/G4) and the identity registry;
  until then a receipt is identified by the
  triple (admission_serial, full content
  digest, immutable locator), and no field in
  any record may present that triple as a
  governed receipt_id.
- `admitted_by` (seat/role identity) and
  `authority_ref`: the exact delegation and
  decision-record reference under which
  admission occurred (R2: the delegation
  record at commit 2e6a639 and Phase 4 §15.2).
- `admitted_at`: metadata, not ordering
  authority; ordering is the store's append
  order.
- `content_digest`: SHA-256 over the
  canonical receipt content (candidate plus
  admission block) **with the digest field
  itself omitted**, under a canonicalisation
  rule named **CANON-RCPT-1** (the ledger
  specification's omission pattern, restated
  here as this specification's own rule).
- `source_commit` / immutable locator of the
  admitted bytes in the Shelf repository.

Immutability: after admission, no field of a
receipt changes. Any later fact arrives as a
linked record (Phase 4 §2.1).

### 3.2 Readiness disposition records

A readiness disposition is its own store
record (not a field on a receipt): it
references the receipt(s) it rests on by
(serial, digest, locator), declares its exact
scope, records its outcome (§6), its validity
conditions (§6.3), its issuer and
`authority_ref`, and its own admission through
M-ADMIT under the same rules. A disposition
never widens the scope of its underlying
receipts.

### 3.3 Correction and supersession records

As §7: append-only records linking target,
replacement (where any), reliance search,
per-use dispositions, and authority. The
original receipt is never modified; its store
entry gains no marker — linkage is by the
correction record's references, so the
historical bytes stay exactly as admitted
(Phase 4 §2.1, §5.1).


## 4. Intake: candidate validation (M-INTAKE)

### 4.1 Accepted candidates

- **Sweep candidate receipts** in the adopted
  Sweep Specification §9 field set (sweep_id,
  scope declaration, snapshot pins, per-check
  records in the Phase 3 vocabulary, factual
  validation records or their declared
  absence, external observations, limitations,
  UNKNOWN sections, candidate outcome).
- **Consumption attestations** and **targeted
  recheck** records in the Phase 4 §2.2/§8
  field shape.
- Standalone **examination reports are not
  candidates**: they are evidence artefacts,
  referenced by receipts and dispositions
  through M-EXAM (§9).

Any other producer or shape: REJECTED at
intake with the reason recorded in the intake
log (§4.4). Intake never repairs a candidate;
a defective candidate is refused, and repair
is the producer's act, producing a new
candidate.

### 4.2 Validation steps (all required)

1. **Schema completeness** against Phase 4
   §§2.2–2.5 and §8: every required field
   present; a required array may be empty only
   where the candidate records why it is empty
   and what scope was searched (design §8
   note). An omitted field is never read as
   empty, clean, or not-applicable.
2. **Digest verification**: every pinned
   digest recomputed or verified against its
   immutable source; any mismatch is an
   integrity failure → refusal (the candidate
   is not admitted "with a note").
3. **Scope recomputation**: the gate
   recomputes the candidate's dependency
   closure from the pinned declaration set and
   graph snapshot; it does not trust the
   candidate's own closure claim. A closure
   that cannot be recomputed from the pins is
   recorded UNKNOWN and blocks admission of
   any scope claim beyond the recomputed part.
4. **Evidence resolution**: every evidence
   reference must resolve to an immutable pin.
   Evidence that exists only in a mutable or
   workspace-only location and is necessary to
   substantiate or reconstruct the receipt
   triggers the R1.2 rule (§8.1): admission is
   refused until the evidence is captured as a
   pinned Shelf snapshot. Credentials or
   authentication secrets in evidence are
   refused outright (R1.7); the omission and
   its reconstruction limitation must be
   explicit in the candidate.
5. **Identity verification**: item/version
   pins are verified through the ledger's
   ResolveIdentity (unrecorded mode is
   sufficient for verification; the walk, if
   any, follows the Phase 2 upward-only rule
   and its full path is recorded in the
   receipt per Phase 4 §2.4). An EXACT_PIN
   candidate is never silently resolved to a
   newer head.
6. **Authority and separation checks** (§10):
   the candidate's preparer, executor and
   attester are recorded; admission will be
   refused if the admitting authority is the
   candidate's author or executor (R2). The
   candidate's own authority claims are
   checked against their cited records; a
   missing, stale or ambiguous authority
   record makes the authority result UNKNOWN,
   and UNKNOWN authority blocks admission
   (Phase 4 §7).
7. **Claim-shape check**: the candidate's
   declared claim is one of the Phase 4 §2.3
   claim classes (declared members / named
   subset / dependency closure / full system).
   A full-system claim is refused unless the
   separate inventory-completeness evidence
   required by §2.3 is itself pinned and
   referenced.

### 4.3 Intake outcomes

ADMITTED (via §5) · REFUSED (named reason
class: SCHEMA / INTEGRITY / SCOPE_UNKNOWN /
EVIDENCE_RESIDENCE / SECRETS / AUTHORITY /
SEPARATION / CLAIM_SHAPE) · UNKNOWN (a
validation input itself could not be
determined — the candidate is neither admitted
nor refused on the merits; it waits, and its
waiting state is visible). No fourth outcome
exists; in particular there is no "admitted
with reservations" — limitations ride *inside*
admitted receipts (§9 of the sweep contract),
never as a weaker admission class.

### 4.4 Intake log

Every intake decision, including refusals and
UNKNOWNs, is appended to an intake log in the
receipt store, recording the candidate's
digest, producer, decision, reason class, and
the deciding component version. A refusal is
therefore itself part of the admitted record's
neighbourhood — findable later, never a silent
drop.

## 5. Admission (M-ADMIT)

**AdmitReceipt**(candidate_digest) →
{admission_serial, locator, content_digest} |
REFUSED | UNKNOWN. Precondition: an intake
record of ADMITTED-eligible for that exact
candidate digest.

- **Authority**: admission is Alex's act under
  R2 (delegation record, commit 2e6a639; Phase
  4 §15.2). The operation requires an
  `authority_ref` resolving to that record; a
  candidate whose admission is attempted by
  its author/executor is REFUSED (SEPARATION).
  Technical ability to append to the store is
  not authority to admit (Phase 4 §7).
- **Append mechanics**: the store snapshot is
  advanced by the single-snapshot CAS
  discipline (read → idempotency check → build
  successor → conditional update → read-back
  verify), with the ledger specification's §9
  retry classification applied unchanged:
  proof comes only from the read-back chain;
  an unreadable or ambiguous outcome is
  UNKNOWN and stops all store mutation until
  resolved. Store-append authority derives
  from R2 for admitted records and intake-log
  appends; it is distinct from, and does not
  imply, ledger mutation authority under G2,
  which remains unassigned.
- **Idempotency**: admission is keyed by the
  candidate's content digest. Re-admitting the
  identical candidate returns the existing
  admission. A changed candidate — any field —
  is a new candidate requiring its own intake
  and admission. There is no edit path.

## 6. Readiness dispositions (M-READY)

### 6.1 Issuance

**IssueReadiness**(scope_declaration,
receipt_refs) → disposition record admitted
through §5 | REFUSED | UNKNOWN. The issuer is
Alex under R2/R3, for the exact declared work
scope.

### 6.2 Outcome computation — verified, not trusted

Where a disposition rests on sweep receipts,
the gate **recomputes** the outcome from the
receipts' pinned check records under the R3
rules (Phase 4 §15.3) and compares it with the
candidate outcome recorded by the sweep. A
disagreement is an integrity finding: no
disposition issues until it is resolved, and
the disagreement is recorded. The outcome set
is exactly: READY_WITHIN_SCOPE /
NOT_READY_WITHIN_SCOPE /
INDETERMINATE_WITHIN_SCOPE /
PARTIAL_WITHIN_SCOPE / OUT_OF_SCOPE, under
the R3 conditions — required FAILED, DIRTY or
STALE blocks the affected scope; required
UNKNOWN yields INDETERMINATE for that scope;
PARTIAL only for a separately bounded,
independently complete sub-scope; a corrupt
authoritative head is terminal under the
Phase 2 STOP rule. STOP is an operational
consequence recorded alongside, never an
outcome value.

### 6.3 Scope and validity discipline

- The disposition's scope is exactly the
  closure evaluated — never the inventory,
  never the system, unless the §2.3 claim-4
  evidence is present and pinned.
- **No waivers**: no operation in this
  specification converts a required FAILED,
  stale, integrity-invalid or UNKNOWN
  dependency into READY (R2). The only
  narrowing act is claiming a genuinely
  independent passing sub-scope, recorded as
  PARTIAL with its boundary.
- **Validity conditions**: each disposition
  records the conditions under which it may
  be relied on (the pinned heads, revisions
  and freshness boundaries it rests on). A
  disposition whose conditions no longer hold
  is not silently wrong — it is **stale**, and
  any consumer checking it through the gate
  receives its staleness state. Recording a
  new disposition for the same scope
  supersedes the old one by linkage (§3.3
  applies); the old one remains, marked by
  the link, never edited.


## 7. Corrections, supersessions, reliance (M-CORRECT)

### 7.1 Raising and admitting

Any authorised seat may **propose** a
correction (a FLAG or a correction proposal
with evidence — Phase 4 §5.3: a FLAG is a
second-look mechanism, not a correction and
not a STOP). **AdmitCorrection** is Alex's act
under R2/R4, append-only. Where Alex authored
or executed the affected artefact, independent
examination is required before adjudication
(R2, §15.2 table). A correction record
contains: target reference (serial, digest),
the correction's own evidence, the replacement
record where one exists, the reliance search
(§7.2), per-use dispositions (§7.3), and its
authority reference.

### 7.2 Reliance search

On admission of a correction, the gate
searches, in order: (a) the dependency
graph's reverse edges from the corrected
item/version; (b) the receipt store's own
reliance fields and disposition references;
(c) recorded consumption records. The search's
scope and coverage are recorded in the
correction record. **Because no complete
reliance registry exists, incomplete coverage
is recorded as UNKNOWN — never as "no
downstream reliance"** (R4; Phase 4 §§5.2,
10 criterion 10).

### 7.3 Effects

- Each **known** downstream use receives an
  explicit disposition: STAND (with reason),
  RECHECK (the affected scope is dirtied and
  must be re-evaluated before further
  dependent work), or WITHDRAWN. No use is
  silently presumed valid or invalid.
- Dirtying is handed to the sweep as a
  **DirtyNotice** record (corrected identity,
  affected scopes, correction reference) in
  the sweep's intake shape; consumption of the
  notice by the sweep is a separate recorded
  event — delivery is not consumption (Phase
  4 §3.1).
- Historical outputs are not erased. A
  corrected receipt remains admitted history;
  consumers resolving it through the gate
  receive the correction linkage with it.
- Notification of known affected owners is
  recorded with the same delivery/consumption
  distinction; no complete automatic
  notification capability is claimed (R4).

## 8. Retention (M-RETAIN)

### 8.1 Residence rule at admission

The receipt store's canonical residence is
the Shelf Git repository (R1.1). M-INTAKE
step 4 (§4.2) is where the rule bites:
necessary evidence living only in mutable or
workspace-only locations must be captured as
an immutable pinned Shelf snapshot **before**
admission; the originating workspace copy
remains separately identified and does not
silently become the authoritative operational
source (R1.2).

### 8.2 Permanence, holds, and the absent operation

- Admitted receipts, dispositions, corrections
  and the evidence necessary to reconstruct or
  challenge them are retained **permanently**
  (R1.3). This specification defines **no
  expiry and no disposal operation**. Disposal
  exists only as a future act of Ben's
  explicit authorisation, outside this gate.
- **Holds**: a record under an open FLAG,
  correction, dispute, examination, known
  reliance, or unresolved reconstruction
  defect carries a hold marker in the store
  index (the record itself is unchanged). A
  hold blocks any future disposal path in any
  event (R1.4).
- Reconstruction follows Phase 4 §6.4: from
  the historical pinned rules, graph,
  inventory and receipts — never from current
  mutable state.

### 8.3 Backup obligations (operational, not gate functions)

R1.5's requirements are recorded here as
obligations on the deployment, each producing
its own evidence record in the store when
performed: an independent second-residence
copy of each admitted release receipt and its
evidence bundle after admission; a weekly
full-repository snapshot; a restore test at
least quarterly, and before relying on a
backup for a release when the last successful
restore test is over 90 days old. This
specification does not implement any of them
and authorises no provider or spend; their
absence from an implementation is a stated
non-conformance, not a silent gap.

## 9. Examination interface (M-EXAM)

- An examiner's record attached to a receipt
  or disposition carries the Phase 4 §2.6
  fields in full: identity and role,
  independence from author/implementer/
  preparer, exact artefacts/versions/hashes
  examined, the evidence class actually
  achieved (source-inspected / fixture-
  executed / independently reproduced /
  live-observed), environment and access
  limitations, findings, dispositions and
  unresolved objections. A named examiner is
  not proof examination occurred; a record
  that cannot state its evidence class is not
  an examination record.
- The gate operates with examination
  **pending**: which examination gate applies
  to which receipt kind before admission is a
  governed policy table (configuration, owned
  by the admitting authority), recorded per
  receipt in its admission block. The gate
  does not invent the table's contents.
- Vane's criterion-17 examination concerns the
  Phase 4 **design**. Implementation-level
  examination of this component is a separate,
  future appointment; nothing here presumes
  it, and this specification's adoption does
  not satisfy it.

## 10. Authority and availability

| Operation | Authority basis | Status in this specification |
|---|---|---|
| Prepare candidate | assigned task (R2) | Available |
| Attest to own execution | the executor (R2) | Available, own acts only |
| Intake validation | gate machinery | Available; outcomes §4.3 |
| Admit receipt | Alex under R2 delegation (2e6a639; §15.2) | Assigned — admission possible once implemented and the delegation stands |
| Issue readiness disposition | Alex under R2/R3 | Assigned, same condition |
| Admit correction/supersession | Alex under R2/R4 (+ independent examination where Alex authored the artefact) | Assigned, same condition |
| Propose correction / raise FLAG | any authorised seat | Available |
| Mint governed receipt_id | Phase 1 identity governance (G1/G4) | **Unavailable** — locator triple only (§3.1) |
| Ledger mutation of any kind | G2 (unassigned) | **Unavailable** — this gate performs none |
| Dispose / expire any record | Ben's explicit authorisation only (R1.3) | **Not an operation of this gate** |
| Waive a required check | — | **Prohibited** (R2); narrowing to a passing sub-scope is the only permitted act |

Authority references must resolve to the
versioned record cited. If the delegation is
revoked or the cited record cannot be
resolved, the affected operations' authority
result is UNKNOWN and they refuse — technical
access is never a substitute (Phase 4 §7).

## 11. Named external evidence families

The Phase 4 §14 named instances — the
publish-gate approvals log (265 entries), the
gate-ledger authorisation/execution pair (24
executions), the scope ledger (~199 entries),
the Crusher log (131 records at snapshot), the
index admission report, and the BridgePress
registry — are **external evidence families**
for this gate. A receipt may cite them as
evidence by immutable pin, with their
residence and the §14 limitation notes carried
into the receipt. The gate does **not**
ingest, migrate, re-admit, or reinterpret
them; historical records keep their own
semantics. Any future migration is a separate
decision, separately authorised.

## 12. Dependencies and design-only status

- **Ledger**: ResolveIdentity and snapshot
  reads for pin verification. The gate's
  design is complete against Ledger Rev 4's
  interface; its operation inherits the
  ledger's adoption state and additionally
  awaits the identity-governance decisions
  for governed receipt identity (§3.1).
- **Sweep (adopted, b51c0f84)**: candidate
  receipts in (§4.1); DirtyNotice records out
  (§7.3). The sweep's candidate outcome is
  evidence for the gate's recomputation,
  never a substitute for it (§6.2).
- **Shelf substrate**: the store's CAS append
  inherits the bounded Phase 2 evidence and
  its stated limits; structured conflict
  classification and true concurrent-writer
  behaviour remain unproven there, and this
  specification claims neither.
- Nothing in this component runs, admits, or
  enforces until implementation is separately
  authorised and the preconditions above are
  actually satisfied. Adoption of this
  specification changes none of that.

## 13. Traceability to the Phase 4 acceptance criteria

Design coverage only — a criterion mapped here
is a requirement this build specification
implements on paper, not a passed test.
(Phase 4 criteria are design-acceptance
criteria; their implementation evidence is
future work, in the test classes named.)

| Phase 4 criterion | Build sections | Test class |
|---|---|---|
| 1 receipt identity/scope/pins/checks/evidence/examiner/authority/limitations/claim | §§3, 4.2, 9 | T-ADMIT |
| 2 scope semantics (closure / recheck / full sweep) | §§4.2(3), 4.2(7) | T-SCOPE |
| 3 inventory completeness ≠ sweep completion | §§4.2(7), 6.3 | T-SCOPE |
| 4 every edge/version and resolved source recorded | §§4.2(3,5) | T-ADMIT |
| 5 integrity / factual / availability / authority / coverage / consumption distinct | §§4.2, 9 | T-ADMIT |
| 6 receipt ≠ consumption | §§7.3, 9; sweep contract | T-RELY |
| 7 partial rules; failed/UNKNOWN shared deps preserved | §6.2–6.3 | T-READY |
| 8 outcomes distinguish not-ready / indeterminate / partial / ready | §6.2 | T-READY |
| 9 corrections preserve originals, history, reliance | §§3.3, 7 | T-CORRECT |
| 10 incomplete reliance = UNKNOWN | §7.2 | T-CORRECT |
| 11 retention/retrieval/reconstruction/backup/holds assigned | §8 (R1) | T-RETAIN |
| 12 reconstruction from historical pins | §8.2 | T-RETAIN |
| 13 authority separated; access ≠ authority | §10 | T-ADMIT |
| 14 examiner identity/independence/access/scope/evidence class | §9 | T-EXAM |
| 15 adversarial cases (stale deps, event-during-sweep, missing evidence, partial scope, correction, reconstruction, false consumption, inventory incompleteness) | §§4–8 passim | all classes |
| 16 EXON vocabulary reconciliation before operational values adopted | §§3–6 passim — all value sets herein are labelled proposals or R3's decided set | T-SCOPE |
| 17 named independent examiner before formal Phase 4 acceptance | §9 — design examination is Vane's pending Phase 4 act; implementation examination separate | T-EXAM |

## 14. Adoption boundary

Adoption of this specification settles the
receipt gate's design. It does not implement
the store, the intake machinery, or any
enforcement; it does not admit any receipt,
issue any disposition, or satisfy criterion
17; it does not resolve G1–G4, LEDGER-GAP-1,
or the governed receipt-identity question; and
it creates no implementation, migration,
publication, generation-zero, or freeze
authority. The three Phase 5 build
specifications together still leave Phase 6 —
initial release and generation zero — behind
its own gates, exactly as the adopted plan
requires.

*End of Receipt and Readiness Gate
Implementation Specification 01 Rev 1 —
prepared for Alex's review and adoption
decision under the amended delegation.*
