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

**Revision:** Rev 4 — prepared in response to
Alex's review `pb-20261111-receipt-gate-rev3-
review` (report shelved at commit 3070b3a1,
blob 67fa9210…): the one remaining correction,
RG-R3-01 — CANON-RCPT-1 is now a fully
deterministic contract (RFC 8785 adopted,
input constraints and normative test vectors,
§3.1), and Alex's traceability appendix is
incorporated at §13.2 by pin. Rev 3: commit
e9e60b42, git blob b0e6fcff…; Rev 2: commit
81746fec, git blob eb43d0b1…; Rev 1: commit
2db7d59e, git blob 74ac55ae…. Prior revisions
are preserved in the repository history; this
revision supersedes them as the review
candidate only.

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

**Digest construction (exact, non-circular).**
Two digests exist and are never conflated:
- `candidate_digest`: SHA-256 over the
  candidate content under CANON-RCPT-1 with
  the digest field omitted, computed by the
  producer and verified at intake (§4.2).
- `record_digest`: SHA-256 over the **admitted
  content** under CANON-RCPT-1 with the digest
  field omitted, where the admitted content is
  exactly: the candidate (complete, as
  verified) plus the admission block fields
  `admission_serial`, `admitted_by`,
  `authority_ref`, `admitted_at`,
  `candidate_digest`, and `intake_record_ref`.

The storage commit and immutable locator of
the admitted bytes are **never part of the
digested content**: they are recorded in the
store's index entry for the serial (serial →
{record_digest, locator, commit}), a wrapper
outside the record. Phase 4 §2.2's
`source_commit` requirement is satisfied by
that index entry. Construction order is
therefore: verify candidate → assign serial →
build admission block → compute record_digest
→ append → record the resulting commit in the
index. Any implementation that places a
locator or commit inside the digested record
is non-conformant: the digest would depend on
the commit that contains it.

**CANON-RCPT-1 (deterministic byte contract).**
CANON-RCPT-1 **is** the JSON Canonicalization
Scheme, **RFC 8785**, applied as follows —
the published algorithm is the authority for
every lexical question this paragraph does
not separately constrain:

- Input is a parsed JSON value (RFC 8259
  grammar). Numbers are IEEE 754 doubles as
  RFC 8785 requires; serialisation of numbers
  follows RFC 8785 §3.2.2 (the ECMAScript
  Number::toString algorithm): 1e2 → `100`,
  1.50 → `1.5`, −0 → `0`, 1e21 → `1e+21`.
- Object keys are sorted by **UTF-16 code
  unit** order (RFC 8785 §3.2.3) — not code
  point order; the two differ for
  supplementary-plane keys against U+E000–
  U+FFFF keys, and vector V5 pins the
  behaviour.
- Strings are escaped exactly per RFC 8785
  §3.2.2.2: only `"` , `\`, and control
  characters U+0000–U+001F are escaped, using
  the short forms \b \t \n \f \r where defined
  and \u00xx (lowercase hex) otherwise; all
  other characters, including U+007F and all
  non-ASCII, are emitted raw as UTF-8.
- Output is UTF-8, no insignificant
  whitespace, no trailing newline. The digest
  is SHA-256 over those bytes. The
  canonicalisation identifier is recorded in
  every record that carries a digest.

**Input constraints (parser boundary).** A
record is admissible for digesting only if:
its text parses under the RFC 8259 grammar
with **duplicate keys rejected recursively at
every object level** before canonicalisation
(a last-value-wins parse is non-conformant);
every string is well-formed Unicode
(unpaired surrogates are rejected, never
normalised or replaced); every number is
finite (JSON cannot express non-finite
values; a producer-side value that is not a
finite double cannot enter a record). An
input failing any constraint is rejected at
the boundary, not canonicalised leniently.

**Omission rules, kept separate.** Omission
happens on the parsed object, before
canonicalisation: for `candidate_digest`,
exactly the candidate's own digest field is
removed and every other field is covered; for
`record_digest`, exactly the `record_digest`
field is removed, and `candidate_digest` is
an ordinary covered field. The default for
any unlisted field is COVERED; excluding more
changes the rule.

**Identifier discipline.** The byte rules
above are frozen under the identifier
CANON-RCPT-1. Any future incompatible change
takes a new identifier (CANON-RCPT-2, …); an
existing identifier's rules never change
silently, and a digest computed under one
identifier is never verified under another.

**Comparability status.** The Rev 3 claim of
byte-identity with the ledger's
CANON-LEDGER-1 is **withdrawn**: that rule
remains defined only in an unadopted
candidate and in looser wording. Cross-
component digest comparability holds only if
and when the ledger adopts a compatible
deterministic rule; no comparability is
claimed today. (D3-CANON-1 remains what the
retrieval found it to be: a proposal, cited
as background, never as authority.)

**Normative test vectors.** Canonical outputs
below are byte-exact (shown as text); the
SHA-256 is over the UTF-8 bytes of the
canonical form. Any conforming implementation
must reproduce all of them, and an
implementation claim requires identical
outputs from at least two independent
implementations.

| # | Input (parsed value) | Canonical form | SHA-256 |
|---|---|---|---|
| V1 | {"b":1,"a":2} | {"a":2,"b":1} | d3626ac30a87e6f7a6428233b3c68299976865fa5508e4267c5415c76af7a772 |
| V2 | {"x":1e2,"y":-0,"z":1.50} | {"x":100,"y":0,"z":1.5} | 3e37129d5927dd422f2dbc4819295edb18f72dff6a3e15481bcf7b870b980ce6 |
| V3 | {"p":0.1,"q":1e21,"r":123.456e-3} | {"p":0.1,"q":1e+21,"r":0.123456} | 4d1bb4a122fde76aea7ee3b06a9df1db58f94dc965db7cca53f4474a82253338 |
| V4 | {"é":1,"e":2} (é = U+00E9) | {"e":2,"é":1} | ae0cc153856ae8fdab2420c8f8e36a9f9cd47c4b1a73531be4bd7dc8092fa69e |
| V5 | {"�":1,"𐀀":2} (U+FFFD; U+10000) | {"𐀀":2,"�":1} — UTF-16 order: D800 < FFFD | 2be8040fe3029f9de464f315235716337d3ef13fe83fe32a481281b77a32112c |
| V6 | {"s": a, LF, b, U+0001, ", c, \, d} | {"s":"a\nb\u0001\"c\\d"} | b521568ec863cd24625c5c269d0fc4a0cc125e2205e1bd8dde231ea868631272 |
| V7 | candidate {"x":1,"candidate_digest":…} with the digest field omitted | {"x":1} | 5041bf1f713df204784353e82f6a4a535931cb64f1f4b4a5aeaffcb720918b22 |
| V8 | record {"candidate_digest":"abc123","x":1,"record_digest":…} with record_digest omitted | {"candidate_digest":"abc123","x":1} | 8f70dbc4bf2db7f472d789faaeaacb80c4369e98f586ffb16c7d397fb5d52921 |
| V9 | {"a":{"x":1,"x":2}} (recursive duplicate key) | — | REJECTED at parse; no digest exists |
| V10 | Two records identical except their store index locator/commit | identical canonical forms | identical record_digest (locator/commit are never inputs) |

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

### 3.4 Read-side resolution

Consumers never receive a bare record from the
gate. **ResolveRecord**(serial | record_digest
| locator) returns the admitted record plus a
**resolution bundle**:

1. **Reverse correction linkage.** The store
   maintains a reverse-link index (target
   serial → correction/supersession record
   serials). The index is not a separate
   source of truth: every correction admission
   appends its reverse-link entries **in the
   same store transition** as the correction
   record itself, so the index is exactly as
   complete as the store's admitted correction
   records. The bundle lists every linked
   correction and supersession, in store
   order.
2. **Coverage proof.** The bundle states its
   lookup coverage explicitly: the store
   revision R at which the bundle is computed,
   and the coverage basis for exactly R.
   Coverage for R is **proven** only when one
   of these holds: (a) the index was verified
   by rebuild-and-compare against the store at
   revision R itself; or (b) the index was
   verified at some earlier revision R0, and a
   **proven transition chain** R0 → R accounts
   for every intervening store transition —
   each transition in the chain read back and
   its correction entries (or proven absence
   of any) matched against the index. A
   verification cadence or a last-verified
   revision, on its own, proves nothing about
   a newer returned revision. In every other
   case — divergence, unreadable snapshot,
   gap in the correction history, or a chain
   link that cannot be proven — the coverage
   statement is **UNKNOWN**, and the bundle
   must say so: a consumer is never told "no
   corrections exist" on unproven coverage; it
   is told "none found, coverage UNKNOWN."
   (No adopted rule governs this verification;
   a Crusher retrieval on 2026-11-11 returned
   UNKNOWN. This paragraph is this
   specification's own rule.)
3. **Disposition staleness evaluation.** For a
   readiness disposition, the bundle adds a
   staleness evaluation computed at read time:
   each validity condition (§6.3) is re-checked
   against the current pins it names (ledger
   heads/revisions, freshness boundaries,
   correction linkage from step 1). Result:
   **VALID** (every condition re-checked and
   holding), **STALE** (the lapsed conditions
   named), or **UNKNOWN** (any condition that
   cannot be evaluated — an unreadable head, an
   incomplete event history, an unverifiable
   coverage statement). UNKNOWN never defaults
   to VALID.
4. The original record's bytes are returned
   exactly as admitted, in all cases. The
   bundle is a read-time artefact, not a store
   record; it is identified by the store
   revision and evaluation time it was computed
   at, as metadata.


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
- **Readiness disposition candidates**,
  prepared by the readiness function (§6.1):
  scope declaration, the receipt references it
  rests on, the recomputation record (§6.2),
  and its proposed validity conditions (§6.3).
- **Correction and supersession candidates**,
  prepared by the correction function (§7.1):
  target reference, correction evidence,
  replacement reference where one exists, the
  reliance search record (§7.2), and per-use
  dispositions (§7.3).

The last two kinds close the gate's own
admission path: every record type the store
holds — receipts, dispositions, corrections —
enters through the same intake (§4.2) and the
same admission (§5). M-READY and M-CORRECT
**prepare** candidates; they hold no separate
write path to the store.
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

**Kind-specific checks** (in addition to the
seven steps, which apply to every kind):
- *Disposition candidates*: the recomputation
  record must be present and must reproduce
  from the referenced receipts' pinned check
  records at intake; a candidate whose outcome
  the gate cannot reproduce is REFUSED
  (INTEGRITY), and the disagreement is logged.
  The declared scope must equal the evaluated
  closure (§6.3).
- *Correction candidates*: the target must
  resolve to an admitted record; the reliance
  search record must be present with its
  coverage statement (UNKNOWN coverage is
  admissible — an *absent* search is not);
  every known use must carry a disposition;
  where the admitting authority authored or
  executed the target artefact, the
  independent-examination precondition (R2) is
  checked at intake and blocks admission until
  satisfied.

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
through §§4–5 | REFUSED | UNKNOWN. The
readiness function prepares the disposition
candidate (§4.1); its issuance is its
admission, by Alex under R2/R3, for the exact
declared work scope. There is no issuance
outside the intake-and-admission path.

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
under R2/R4, append-only, performed by
admitting a correction candidate through
§§4–5 (§4.1). Where Alex authored
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
(c) recorded consumption records. The search
is recorded in the correction record with
exactly the fields R4 requires (Phase 4
§15.4(2)): the **exact sources** searched,
the **query/scope** applied to each, the
**time** of the search, the **results**
(each known downstream receipt, decision,
component and work item identified), and the
**method** used. A search record missing any
of those fields is incomplete and blocks
admission of the correction until completed.
**Because no complete reliance registry
exists, incomplete coverage is recorded as
UNKNOWN — never as "no downstream
reliance"** (R4 §15.4(3); Phase 4 §10
criterion 10).

### 7.3 Effects

- Each **known** downstream use receives an
  explicit disposition in R4's exact value
  set (Phase 4 §15.4(5)): **REMAINS_VALID**,
  **REQUIRES_RECHECK** (the affected scope is
  dirtied and must be re-evaluated before
  further dependent work), **WITHDRAWN**,
  **SUPERSEDED** (the use now rests on a
  superseding record, which is named), or
  **UNKNOWN** (the evidence cannot establish
  whether the prior result remains valid — in
  which case neither validity nor invalidity
  is presumed). (The Rev 1–2 labels STAND /
  RECHECK are superseded by this mapping:
  STAND = REMAINS_VALID; the SUPERSEDED and
  UNKNOWN dispositions, previously missing,
  are now distinct values and are never
  folded into another.) No use is silently
  presumed valid or invalid.
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
- Notification of known affected owners goes
  through a verified available route and is
  recorded with the delivery/consumption
  distinction; where no verified route exists,
  the notification is marked **NOT_DELIVERED**
  or **UNKNOWN** as applicable (R4 §15.4(6)).
  No complete automatic notification
  capability is claimed.

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

### 13.1 Implementation traceability matrix (concrete cases)

Fixture classes: **F-STORE** (synthetic
receipt store), **F-AUTH** (synthetic
authority records, including a revoked
delegation variant — TEST-ONLY assignments
inside fixtures, conferring no real
authority), **F-GRAPH** (synthetic
declarations and graph snapshots), **F-LEDGER**
(synthetic ledger snapshot and heads), **F-EXT**
(mutable workspace-evidence stand-in).
Fixtures run against synthetic stores only,
isolated from any production record, and are
discarded or reset on rollback; no fixture
writes to the real Shelf store. Each case's
evidence is its fixture run record (inputs,
store revisions before/after, emitted
records). An independent examiner must be able
to reproduce each case from its fixture
definition; cases marked † additionally
require the examiner to inspect the
construction, not only the outcome.

Examiner evidence classes: **SI** =
source-inspected, **FE** = fixture-executed,
**IR** = independently reproduced. Authority
basis for every admission-class case is the
F-AUTH TEST-ONLY assignment unless stated.

| Case | Refs (requirement · build § · operation) | Fixture → expected outcome | Durable evidence | Authority | Examiner |
|---|---|---|---|---|---|
| RG-01 Idempotent admission | Ph4 §10.1 · §5 · AdmitReceipt | F-STORE+F-AUTH; one valid candidate admitted twice → one admission, one serial; second call returns the existing admission | Store snapshots before/after; both call results | F-AUTH test assignment | FE |
| RG-02 Changed candidate | Ph4 §2.1 · §§4–5 · intake | Candidate resubmitted with one field altered → new candidate, new intake record, no relation to the first admission | Two intake-log entries; digests differ | producer role | FE |
| RG-03 Disposition candidate intake † | Ph4 §10.8 · §§4.1–4.2, 6.1 · IssueReadiness | F-GRAPH+F-LEDGER; reproducible recomputation → admitted through §§4–5; interface audit shows no side path | Admission record; recomputation record | F-AUTH readiness assignment | SI+FE |
| RG-04 Correction candidate intake † | Ph4 §10.9–10 · §§4.1–4.2, 7.1 · AdmitCorrection | Reliance search present, coverage UNKNOWN → admitted with UNKNOWN recorded; absent-search variant → REFUSED | Correction record incl. §7.2 search fields | F-AUTH correction assignment | SI+FE |
| RG-05 Digest construction † | Ph4 §2.2 · §3.1 · record build | Locator/commit withheld until after digest → record_digest verifies from content alone; locator-inside-digest variant rejected as non-conformant | Canonical bytes + digest recomputation transcript | n/a (construction) | SI+IR |
| RG-06 Authority revocation | Ph4 §7 · §§5, 10 · AdmitReceipt | F-AUTH revoked variant cited → REFUSED (authority UNKNOWN); no append | Intake-log refusal entry; store unchanged | revoked F-AUTH record | FE |
| RG-07 Author self-admission | R2 · §§4.2(6), 10 · AdmitReceipt | Candidate's author attempts admission → REFUSED (SEPARATION), logged | Intake-log entry naming both roles | n/a (refusal) | FE |
| RG-08 Missing evidence | R1.2 · §4.2(4) · intake | Evidence reference unresolvable → REFUSED (EVIDENCE_RESIDENCE) or UNKNOWN per §4.3; never admitted | Intake-log entry with reason class | n/a | FE |
| RG-09 Mutable evidence | R1.2 · §4.2(2,4) · intake | F-EXT evidence changed after candidate issued → REFUSED (INTEGRITY); snapshot-first variant admits | Digest transcripts for both variants | n/a / F-AUTH | FE |
| RG-10 Secrets in evidence | R1.7 · §4.2(4) · intake | Evidence bundle containing a credential → REFUSED (SECRETS); omission + limitation path exercised | Intake-log entry; limitation text | n/a | SI+FE |
| RG-11 Full-system claim, incomplete inventory | Ph4 §2.3 · §4.2(7) · intake | Claim-4 candidate without completeness evidence → REFUSED (CLAIM_SHAPE) | Intake-log entry | n/a | FE |
| RG-12 Scope recomputation disagreement | Ph4 §10.2 · §4.2(3) · intake | Candidate closure exceeds recomputed closure → excess scope UNKNOWN; its admission refused | Recomputation record with both closures | n/a | FE+IR |
| RG-13 Outcome recomputation disagreement | R3 · §6.2 · IssueReadiness | Sweep candidate outcome ≠ gate recomputation → no disposition; disagreement recorded as integrity finding | Finding record; absence of disposition proven by store read | F-AUTH readiness assignment | FE+IR |
| RG-14 Waiver attempt | R2 · §6.3 · (no operation) | Attempt to convert required UNKNOWN → READY → fails at the interface; no such operation exists (negative test) | Interface surface listing; attempt log | n/a | SI |
| RG-15 Correction, incomplete reliance | R4 §§15.4(2–5) · §7.2–7.3 · AdmitCorrection | F-GRAPH partial reverse coverage → correction admitted; coverage UNKNOWN; known uses carry R4 dispositions incl. SUPERSEDED/UNKNOWN variants; no "no reliance" claim | Correction record with exact search fields (sources, queries, time, results, method) | F-AUTH correction assignment | FE |
| RG-16 DirtyNotice delivered, not consumed | Ph4 §3.1 · §7.3 · notice issue | Notice delivered; no consumption record → reliance state unchanged; delivery ≠ consumption in the records | Notice record; state comparison | F-AUTH correction assignment | FE |
| RG-17 Stale disposition read | R3 · §§3.4, 6.3 · ResolveRecord | F-LEDGER head advances past a validity condition → bundle returns STALE naming the lapsed condition; unevaluable-condition variant → UNKNOWN, never VALID | Resolution bundles for both variants | reader role | FE |
| RG-18 Reverse-link coverage † | Ph4 §10.9 · §3.4 · ResolveRecord | Index entry removed (divergence) → coverage UNKNOWN, never "no corrections"; proven-chain variant (R0→R accounted) → coverage proven | Bundle coverage statements; chain transcripts | reader role | SI+FE |
| RG-19 Interrupted append | Ph4 §10.1 · §5 · AdmitReceipt | Append interrupted mid-transition → read-back classification; no partial record; ambiguous variant stops all store mutation | Store revisions; classification record | F-AUTH test assignment | FE |
| RG-20 Reconstruction from historical pins | Ph4 §6.4 · §8.2 · reconstruct | Rules/graph/inventory advanced after admission → reconstruction reproduces the receipt's meaning from its historical pins, not current state | Reconstruction transcript pinned to historical artefacts | reader role | IR |

### 13.2 Alex's traceability appendix (incorporated)

Alex's traceability appendix is incorporated
into this specification by reference and forms
part of the complete specification against
which the adoption decision is made:

**duenna/ALEX-RECEIPT-GATE-REV3-TRACEABILITY-
APPENDIX-01.md** — commit 9d90cdfe, git blob
e7f1f7573b3ad588e1c7cd3779c0e20ec32889e6,
15,140 characters (independently recomputed
and matched from Remmy's side, 2026-11-11).

It expands RG-01–RG-20 with exact operation
inputs, expected branches, durable evidence,
authority, fixture isolation and examiner
evidence requirements, and distinguishes
design coverage from test execution. It is a
companion to §13.1, not an override: where the
appendix and §13.1 differ on a case's expected
outcome, the difference is a finding to
reconcile, not a silent override by either
side.

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
Implementation Specification 01 Rev 4 —
prepared for Alex's review and adoption
decision under the amended delegation.*
