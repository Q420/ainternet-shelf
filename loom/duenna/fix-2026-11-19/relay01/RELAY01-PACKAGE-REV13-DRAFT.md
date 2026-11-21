# RELAY 01 — PACKAGE REVISION 13 (DRAFT — for Gate 1 examination)

*Status: prepared as a draft on 2026-11-20 under Ben's
tap (widget-97bf221e-3b28-4c7f-a7de-3eeb65173e69) and his
words of 2026-11-20 21:53 MST: "Draft REV13 — close the
last two locks: type-first member classification, case
identity bound into the run identity." Its status at
any time is what the filing record states. This
revision answers Vane's Gate 1 verdict on Revision 12 —
**GATE 1 NOT PASS — RETURN FOR CORRECTION** — filed as
`VANE-GATE1-VERDICT-REV12-2026-11-20.md` (Git blob
d1d756679ef91f34aede8d2b43790c94da5775a8, filing commit
5ddff2840e7eb154a8aba856936fd6a30a468a33). It governs
run-02 only. Run-01 is closed history: NO START, event
ledger seq 1–7, unaltered and unreinterpreted by
anything in this revision. It satisfies no start
condition by its own existence.*

## 0. Incorporation

Revision 13 incorporates Revision 12 (Git blob
063e495e92e36d14e77a59d15412e77b079170fd; SHA-256
a486b290bd093c0028f0952b03493f2a6954a85a259e3b05d5b8e71e0a2b9119)
and its predecessors by reference, together with the
design documents at the pins REV9 §0 recorded (design
paper aae71134…, Annex A a8b17eb9…, Annex B 198f0d5a…),
and replaces the exhibited Gate Format Definition:

- **Gate Format Definition, version 4** —
  `GATE-FORMAT-DEFINITION-V4-DRAFT.md`, SHA-256
  e9e49721dfa8a2477d66710c64316f0599df5dd2729c44a89e97192a431806ba.
  Citation: 2026-11-20/gate-definition/gate-format-definition-v4.

Version 3 of the definition (Git blob
706d0a7c36f50da41a8efeb1cc7fff4417aa177b, SHA-256
97a262e35ea827315c6b4e95d22866adbe60d2a80c8454ac5f5e237ea496f325)
is preserved as filed at commit 7dfcff19…; version 4
supersedes it as the exhibited definition for run-02,
and no filed text of version 3 (or version 2, or
version 1) is edited. The design freeze (blob
16543582aaa059b4878a0d8fb1e5c2ab5664f952) is unchanged.
Revisions 1–12, all prior verdicts, and the REV9,
REV10, REV11, and REV12 submission records are
preserved as history; nothing in this revision edits
them. Where this revision corrects a passage of a prior
revision or annex, §1 and §5 say so explicitly: the
filed texts stand, and this revision's statement
governs for run-02.

## 1. The delta — every finding of the REV12 verdict, answered

**G1-R12-01 — F8 classification permits non-directory
members to bypass rejection and correspondence.
ANSWERED by exhibit.** Gate Format Definition version
4 rebuilds F8's classification **type-first** (§2 of
the definition states the type-metadata reading; §4 F8
step 2 states the classification):

- A member's type is read from its type metadata —
  the file-type field of its Unix mode, present only
  where the member's host is Unix — **before** its
  name is consulted for anything. Directory
  (0o040000), regular file (0o100000), symlink
  (0o120000), any other nonzero file-type field
  **other**. Only where type metadata is absent (the
  definition enumerates the three absence cases:
  non-Unix host, mode 0, file-type field 0) does the
  name form classify — terminated → directory,
  otherwise regular file — and an untyped member
  cannot conflict, its classification resting on its
  name.
- The name suffix alone never establishes type, and a
  typed member whose name form contradicts its type
  is **not** reclassified to fit its name. F8 step 4
  fails on both disagreement forms, each recorded:
  (a) a symlink or other type, **whatever its name —
  including a trailing-separator name** — is recorded
  in `rejected_members` with its type, exactly as
  Schema V2 already provided; (b) a regular-file type
  with a terminated name, and (c) a directory type
  with an unterminated name, are recorded in the new
  `type_conflicts` field. A conflicted member is
  rejected: neither counted as a directory entry for
  exclusion nor admitted to the correspondence set.
- **Schema, field by field.** Outcome (a) was
  recordable under Schema V2 (`rejected_members`) and
  is unchanged. Outcomes (b) and (c) were not:
  `rejected_members` records rejection for type, and
  these types are admissible — what fails is the
  agreement of type and name form; `invalid_names`
  records G-P failures, and (c)'s name may satisfy
  G-P exactly, so (c) had no recordable form at all.
  Version 4 §5.1 therefore states **Verdict Record
  Schema V3**: one added F8 field (`type_conflicts`:
  name, mode_type, name_terminated), `schema_version`
  3, an explicit changelog, and nothing else changed.
- **G-N amended to match.** A member's name is still
  its raw central-directory bytes under no decoding —
  but G-N now states expressly that a name is not a
  type: directory-entry name validation (the stripped
  name against G-P) applies only to members
  classified as directory entries under the type-first
  rule.
- **Vectors.** TV-17 is the verdict's case (a) — a
  symlink named `link/` — and fails F8 at step 4 as a
  rejected symlink (directory entries 0; it is never
  excluded as a directory). TV-18 is case (b) — a
  regular-file member named `file/` — and fails at
  step 4 as a recorded type conflict. TV-19 is case
  (c) — a directory-type member named `dir` — and
  fails the same way. All three archives were
  constructed and computed at this drafting; their F8
  record items are exhibited at §5.2 of the definition
  (Records D, E, F).
- **The real archives re-exercised (TV-20).** F8 was
  rerun under the corrected classification against
  both real archives at this drafting, by raw
  central-directory parse. Every member of both
  archives is Unix-hosted and carries full type
  metadata — no member's metadata is absent. v1:
  directory type (0o40770) ×83, all terminated;
  regular-file type ×688, all unterminated; no
  symlinks, no other types, no conflicts; **F8 PASS**
  with TV-9's values throughout (688 file members, 83
  directory entries, 0 mismatches of 686). v2:
  directory type ×83, all terminated; regular-file
  type ×689, all unterminated; none of any other
  kind; **F8 PASS** (689 / 83 / 0 of 687). The
  corrected classification changes no outcome on the
  real archives — as the verdict itself anticipated
  ("not a finding that either real archive is
  non-conforming") — and the bypass is closed by
  construction, not by their innocence.

**G1-R12-02 — K1 run identity is not globally unique
across cases. CORRECTED in §5.1 below.** The
construction is rebuilt as `DUENNA-RUN-IDENTITY-v3`:
a sixth field, `case-id`, length-prefixed like every
field, binds the case's own identity into every run
identity minted under it. §5.1 defines the case-id
exactly (the SHA-256 of the case's frozen case
record, constituted at case freeze), states the
minting order, and exhibits the collision the verdict
names — two cases minting one identity under the v2
construction — resolved under v3, with the
seq-distinctness pair recomputed under the amended
construction.

**Accepted in the REV12 verdict — carried, not
re-argued.** The verdict accepted as substantially
answering the REV11 findings: Schema V2's completion
of the verdict record (carried into Schema V3 with
the single addition above); G-N's pinning of member
names to raw central-directory bytes (carried, with
the name-is-not-type amendment above); and the K1 v2
length-framing (carried into the v3 construction;
superseded for the case-identity reason only). It
verified the REV12 submission's read-back content,
and the REV10 and REV11 accepted corrections remain
accepted as carried forward (independent Checker
responsibility; the identity separations; the closed
type-token list; format-scheme labelling; the
Adoption Spec authority clarification; C-2; the REV9
correction record). All stand in this revision exactly
as REV12 stated them, except where §1 above amends a
named passage. The verdict also records that design
Q8 and Q9 remain open examination items; §7.4 carries
them as open — this revision does not silently close
them.

**The verdict's scope note — recorded accurately.**
The REV12 verdict states that the examiner has not
independently rerun F8 against the two ZIP byte
streams, and that TV-9's and TV-16's results stand as
the orchestrator's reported computations. TV-20 is
the same class of evidence: an orchestrator
computation, exhibited in the definition with its
inputs pinned and its method stated so the examiner
can rerun it byte-for-byte. Nothing in this revision
claims her verification of it.

**Not changed:** the invocation path entire (REV8
caller 54117c63…, helpers, dependency, timeout
policy); the freeze; the work item (Ob1, NOT
DELIVERED; Q1 OPEN); Gate 2 not commenced.

## 2. Run-02 pre-start verification (P2 and P6 revised; the rest carried)

**P1 — Archive delivery (carried from REV12).** The
actual v1 and v2 archive bytes are delivered to both
the originator and the independent checker — as the
copy of §3, hashed into run-02's event ledger at
delivery.

**P2 — Independent archive verification (REVISED per
G1-R12-01).** The load-bearing set is as REV12 named
it — both zip digests (v1 48a171f4…, v2 db96297c…),
both manifest digests (v1 bf9f8897…, v2 92b5d98c…),
entry counts 686 / 687 — verified under Gate Format
Definition **version 4** (§0):

- **Computation.** Format conformance is computed by
  the **independent Checker (C)** under the version 4
  definition: checks F1–F5 and F8 per archive, and F7
  for each named exhibit, with the case's carrier set
  for F8 named as exactly {`MANIFEST.sha256`,
  `README-EXECUTION.md`}. The required-path set for F5
  is as correction C-2 established:
  `duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md` in
  each manifest; the README-EXECUTION.md exhibits are
  verified under F7 against their baseline digests (v1
  f15fbf6d…, v2 fa982447…). Every computation is
  recorded as a verdict record conforming to **Verdict
  Record Schema V3** (definition §5.1), reproducible by
  an independent third party from the pinned inputs.
  The orchestrator delivers inputs and collects records
  and issues no format verdict.
- **Judgement.** Carried from REV12: the originator and
  the checker each independently judge the content
  claim — that the archive each received is the archive
  this package names — anchored by digests obtained
  independently of the delivering channel, recorded as
  judgement with its evidence.
- **Transport.** Carried: a computation whose inputs
  were not delivered produces no verdict; the item is
  recorded UNEXAMINED, the attempt preserved, never
  FAILED and never retried away.

**P3 — Initial ground-truth verification (carried).**
Each G1–G10 citation resolves through the index to its
fingerprint before support is judged; a
wrong-fingerprint resolution is a recorded resolution
failure. No silent post-start repair.

**P4 — Live catalogue check (carried).** Every assigned
model re-verified against the live provider catalogues
before run-02 opens; raw responses and timestamps
preserved. The assigned set is §7.2's — named and
approved before case freeze, not defaulted.

**P5 — Run-start invocation check (carried, with the
classification REV10 stated).** A fresh invocation per
assigned provider through the exact REV8 caller, all
identities and exit statuses preserved. A provider 503
or any other failed run-start invocation is a **failed
attempt**: it leaves this prerequisite NOT SATISFIED
and means NO START. No route-around and no participant
substitution is implied or permitted under this package.

**P6 — Envelope and identity checks (carried, with the
run-identity construction updated).** All frozen-design
participant, distinctness, finisher-exclusivity,
source-envelope, and no-start checks, completed and
recorded. Run identity at this gate is the K1 identity
of §5.1, constituted by the v3 construction stated
there — case identity bound in — never a configuration
digest.

**P7 — Correction delivery (carried, unchanged).** C1
must be delivered during Holder 2's tenure exactly as
frozen; its identity for delivery and ledger purposes
is the item identity of §5.2. Non-delivery renders the
relay INVALID; no substitute correction may be planted.

Any missing, failed, or unverifiable prerequisite
means NO START for run-02, the failure record preserved.

## 3. The copy provision (carried unchanged from REV9 §3, through REV12)

Run-02 works from a copy of the package and shelf
materials, made and hashed at case freeze; the
originals stay frozen on the shelf as the audit
baseline; identity between copy and original is
digest-for-digest and the copy carries no authority of
its own; divergences found at audit are recorded as
discrepancies with both digests preserved, never
silently reconciled. (Ben's direction, 2026-11-20
20:33 MST.)

## 4. Check-in gates — ALLOW or CORRECT (carried from REV12 §4)

The gate structure is REV12 §4, carried entire:
established gates named in the case in advance, in the
flow; outcomes ALLOW or CORRECT; a gate never edits
the artefact; an uncorrectable item is recorded NOT
SATISFIED and the §2 prerequisite rule applies. The
identity distinction G1-R9-05 established stands
unchanged: **logical item identity** (stable across an
item's life), **content fingerprint** (the digest of
one immutable byte sequence, never carried across
changed content), and **attempt identity** (each
presentation at a gate a distinct attempt under the
item's logical identity, linked to its predecessor by
an explicit supersession/derivation record).

## 5. Catalogue and citation provisions (§5.1 corrected; the rest carried)

The catalogue provisions are REV12 §5, carried, with
the one correction below. Index rows are DC records
per Annex B §B2.1 as adopted; the citation form
`<YYYY-MM-DD>/<type-token>/<slug>` stands; existing
citations remain aliases, never rewritten.

### 5.1 Run identity — case-bound, framed, collision-safe (G1-R12-02)

REV12 §5.1's conceptual settlement stands: a run's
identity is its **K1 run identity**, minted by the
BINDER at the moment a freeze attempt begins, binding
by reference one configuration identity (K3), one
verified subject identity (K2), and one frozen
tree-set identity; the configuration digest is a typed
Relation (References) in the run's record, never its
Identifier. REV12's length-framing also stands and is
carried unchanged. What the REV12 verdict found
defective was the construction's uniqueness scope:
`freeze-attempt-seq` is assigned by one case's event
ledger and is unique within that ledger, but the
canonical input carried no case identity, so two
distinct cases with identical bindings, timestamp, and
sequence number produced the same canonical string and
the same run identity. That defect is corrected here.
The REV12 construction (`DUENNA-RUN-IDENTITY-v2`) is
superseded for run-02; it stands as filed history, and
no identity was ever minted under it — no freeze-begin
has occurred under this package, under either the v1
or the v2 construction — so no run identity is
orphaned by the change.

**The case-id.** The case-id is the **SHA-256 of the
case's frozen case record**. The case record is the
single record the BINDER constitutes at case freeze,
fixing the case's terms; its body states:

- the case's **designation** — the run designation the
  case is constituted for (for this package,
  `relay-01/run-02`, the designation the programme's
  records already use);
- the design freeze, by its pin;
- the governing package revision, by its pin;
- the exhibited Gate Format Definition, by its pin;
- the participant assignments, as named in the case
  and approved by Ben (§7.2);
- the K2 subject record, by its identity;
- the K3 configuration identity;
- the frozen tree-set identity;
- the archive registry; the carrier set; and the
  required-path set — the sets the case names for the
  archive gate.

The case-id is computed once, at constitution, and
recorded at the head of the case's event ledger; every
later record of the case cites it. A case record may
not be constituted under a designation another case's
record already bears: the BINDER checks the shelf
index at constitution, and a designation already borne
refuses constitution. Distinct cases therefore carry
distinct designations in their frozen records and —
the fingerprint being the identity authority, per the
programme's settled two-layer principle — distinct
case-ids. The case-id contains no run identity and
nothing derived from one.

**The construction.** The run identity is the
**SHA-256 of the following canonical string** (UTF-8,
LF line endings, final LF included) — the
length-framed construction of
`DUENNA-RUN-IDENTITY-v3`:

```
DUENNA-RUN-IDENTITY-v3
case-id:<len>:<the case identity — the SHA-256 of the case's frozen case record, 64 lowercase hex>
configuration-id:<len>:<the K3 configuration identity>
subject-id:<len>:<the K2 verified subject identity, byte-exact as recorded in the case's subject record>
tree-set-id:<len>:<the frozen tree-set identity>
freeze-begin-utc:<len>:<the freeze-begin time, UTC, in the form YYYY-MM-DDTHH:MM:SS.mmmZ>
freeze-attempt-seq:<len>:<the freeze-begin event's sequence number in the case's event ledger, decimal>
```

Each field line is the field's label, a colon, the
field value's **byte length** in decimal with no
leading zeros (the length of the value's UTF-8
encoding), a colon, the value's bytes exactly, and an
LF. The rules of the construction:

- **Framing makes every field delimiter-safe.**
  Carried from REV12 §5.1: a reader consumes each
  value by its stated length, not by scanning for line
  ends; no field's bytes can imitate framing or
  swallow a neighbouring field, and the construction
  imposes no grammar on any field's value.
- **The case-id makes uniqueness global.** Two freeze
  attempts in distinct cases now differ in the
  canonical string's first field, because their cases'
  frozen records — and so their case-ids — differ,
  even if the three bindings, the timestamp, and the
  sequence number all coincide. Uniqueness no longer
  rests on one ledger's sequence: the sequence still
  distinguishes attempts **within** a case, and the
  case-id distinguishes cases from one another.
- **Minting order is fixed.** (1) The case is frozen:
  the BINDER constitutes the case record, and the
  case-id is computed from it. (2) A freeze attempt
  begins: the BINDER records the freeze-begin event in
  the case's event ledger, which assigns its sequence
  number. (3) The BINDER computes the run identity
  over the six fields. The minting is recorded under
  the resulting identity in a subsequent governance
  record citing the case-id and the sequence number.
- **Inputs are exactly the six bound values,** in the
  order shown, and nothing else. Any reader with the
  case record, the case's recorded binding values, the
  freeze-begin time, and the ledger sequence number
  can recompute the identity.
- **No circularity.** The run identity is the digest
  of the string; the string contains no run-identity
  field and no field derived from the output digest.
  The case-id is constituted at case freeze, before
  any freeze attempt under the case, and contains no
  run identity. The sequence number is assigned by the
  ledger before minting and does not depend on the
  identity. The identity is an output, never an input.
- **One minting per freeze-begin.** Each freeze-begin
  act is one ledger event and mints exactly one
  identity under this construction.
- **A refused freeze.** Carried from REV12 §5.1: the
  identity is minted at freeze-begin, before the
  freeze's outcome is known, under this same
  construction; a refused freeze is recorded **under**
  that identity as a governance record (freeze
  attempted, refused, reason — v3 K1); `RUN_STARTED`
  is a separate event referencing the identity, emitted
  only on a successful freeze. Attempt and started run
  are never conflated.

**Worked illustrations (constructed for illustration;
they bind no real case and no real run).** With
configuration-id =
`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
subject-id =
`bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`,
tree-set-id =
`cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`,
freeze-begin-utc = `2026-11-20T00:00:00.000Z`, and two
illustrative cases whose case-ids are
`dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd`
(case A) and
`eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`
(case B), the canonical string for case A at
`freeze-attempt-seq` = `1` is:

```
DUENNA-RUN-IDENTITY-v3
case-id:64:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
configuration-id:64:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
subject-id:64:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
tree-set-id:64:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
freeze-begin-utc:24:2026-11-20T00:00:00.000Z
freeze-attempt-seq:1:1
```

Its SHA-256, computed at this drafting, is:

**b9253aa942fa0ff6a2f303d03648f81f2faff5acfb9de4fb1816381ca7e0addb**

**The collision vector (the case the REV12 verdict
names).** Under the superseded v2 construction, case
A's attempt and case B's attempt at sequence 1 have
identical canonical strings — the v2 string has no
case field — and both mint the one identity
`852aee87d21c0778a9d7e728fe4d57dcfd6dafdb435694b4faabe52e2866c429`
(REV12 §5.1's sequence-1 illustration). Under the v3
construction, case B's otherwise-identical attempt
(case-id `eeee…`, sequence 1) mints:

**1647b21ad9a74bcaf4326cfec0c96d58f932442979e1c9c56129293cc064c7ea**

— different from case A's, as the construction
requires. Two distinct cases can no longer mint one
run identity on identical bindings, timestamp, and
sequence number.

**The sequence pair, recomputed under v3.** With
every other field identical to case A's illustration
and `freeze-attempt-seq` = `2`, the SHA-256 is:

**77328ad66a625d0a057b9f9429bde3cf44903a27d716236d9b3acf0fd94a5e0f**

— different from sequence 1's, so the within-case
distinctness REV12 established is preserved under the
amended construction. (The REV11 and REV12
illustrations under the superseded v1 and v2
constructions recompute to their filed values,
45a20449… and 852aee87… / 7d9d36a2…; they stand as
history.)

### 5.2 C1's item-level identity (carried from REV12 §5.2)

C1's item identity stands as REV10 §5.2 constituted it
and REV11 §5.2 and REV12 §5.2 carried it: the SHA-256
of the canonical string exhibited in REV10 §5.2 in
full, computed value
**29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d**,
independently recomputed by the examiner in the REV9
and REV10 rounds, and its clarification accepted in
the REV11 verdict: **the exact canonical string as
exhibited is the sole input** — its bytes (UTF-8, LF
line endings, final LF included) are the input, and no
normalization is applied to anything, by anyone, at
any point. C1's content, authority statement, and
delivery terms are exactly as frozen in REV5 §3 and
carried since; the container digest appears only in
C1's source reference and IsPartOf relation, labelled
as the container's, never as C1's Identifier; the
sealed delivery artefact is a derived representation
of the same item with its own content fingerprint.

### 5.3 Type tokens (carried from REV12 §5.3)

The closed list of seventeen tokens stands, membership
unchanged, under the usage rule REV10 §5.3 stated: a
collection or register of a kind is catalogued with
the token `record`; `event` only for an individually
indexed event; `defect` only for an individual DR
entry.

### 5.4 Format values name their scheme (carried from REV12 §5.4)

Every Format value in a run-02 record names its
scheme — IMT, or the Duenna Local Format Scheme whose
one current value is `application/jsonl`, used only
for the event ledger. A local-scheme value is never
recorded bare.

## 6. Design commitments (carried from REV12 §6)

Vane's four collaboration points stand as commitments
of this package, unaltered: description is not
authority, state, or validation, and gaps are extended
explicitly, never disguised; the fingerprint is
authoritative and the citation a readable
representation only; classification is not
verification, description is not evidence, provenance
is not authority; and the examiner's semantic-loss
examination of the worked artefacts is welcomed on the
record.

## 7. Open items — clarified, carried, and Ben's

### 7.1 The Adoption Spec's authority (carried from REV12 §7.1)

Ben's ruling of 2026-11-20 20:43 MST adopted Annex B
(Dublin Core) as the package's catalogue basis,
confirmed by the examiner in the REV9 verdict and
accepted again in the REV10, REV11, and REV12 verdicts;
Annex A is retained as the studied alternative. The
Adoption Spec was **not** adopted and remains a draft
that enacts nothing. The operative vocabulary, the
GATE disambiguation, the twelve NO TERM entries as
open vocabulary questions for Ben, and the ENVELOPE
collision as an explicit future compatibility item all
stand exactly as REV10 §7.1 stated them.

### 7.2 Run-02 participant assignments (carried; verdict condition)

This revision names no participant set, and REV9's
unasserted default remains withdrawn. Before run-02's
case freeze, the assignment set — every role, every
model — must be **named explicitly in the case and
approved by Ben**; the run-01 set has no default
standing. Any material participant or model change is
expressly authorised and reviewed; there is no silent
substitution. Gemini's run-01 503s remain evidence on
the record, and P5's classification (§2) governs any
recurrence.

### 7.3 Carried conditions from the verdicts

- **Fluency (Known Hole 3 — still UNTESTED).** Before
  run-02 relies on model-produced DC records, one of
  two routes must be satisfied and recorded at case
  freeze: either a cold multi-model conformance test is
  run and passed against a pass mark declared before
  the test, or record construction is made
  deterministic and mechanically validated so that
  fluency is not a trust assumption. This revision
  chooses neither route; the choice and its record are
  case-freeze items.
- **Cost (Known Hole 5 — still UNMEASURED).** Actual
  verification time and cost are recorded during run-02
  and reported against Ben's constraint (2026-11-20
  19:50 MST). No claim is made that the end-to-end cost
  has been proven.
- **Execution.** Ben's separate execution word for
  run-02 remains required after a Gate 1 PASS on this
  revision and the §2 prerequisites satisfied and
  recorded (freeze §11(6)). His 21:53 tap commissioned
  this draft; it is not an execution authorisation.

### 7.4 Remaining examiner items

The §5.1 run-identity construction in its v3 form
(this draft's specification, stated for the examiner's
examination); design §6 Q8 (whether the Gate Format
Definition as exhibited — now version 4 — discharges
the T02/T07/T09 response-format contracts for gate
contexts) and Q9 (the grade of run-01's mechanical
cross-check evidence) — both expressly left open by
the REV11 and REV12 verdicts, noted here, not settled.
Design §6 Q4 remains closed by the REV9 verdict (Part
II accepted); Q5 remains closed by G1-R9-02.

## 8. Submission integrity (carried from REV12 §8)

- **Status language.** A package revision's status
  block states its preparation history — who prepared
  it, under what authority, and when — and no standing
  claim about its filing state. Its status at any time
  is what the filing record (the shelf commit and the
  covering submission record) states. This draft is
  written to that rule, as is the version 4 definition.
- **Read-back inside the submission.** A submission's
  read-back log is filed **inside the submission
  itself**: the submission manifest carries the
  read-back table — for each filed file, its exact
  shelf path, its Git blob identity read back from the
  shelf, the locally staged file's identity, its
  recomputed SHA-256, and the comparison result —
  completed at filing and filed as part of the
  submission commit, or, where the push must precede
  the read-back it reports, in the submission's
  immediate recorded successor commit, which the
  manifest names. A submission whose read-back table is
  absent or incomplete is not a complete submission.
  The evidence lives where the examiner reads; no
  submission of this package may again point to a local
  log the examiner cannot fetch. The REV11 and REV12
  submissions were filed under this provision; the
  REV11 verdict accepted the read-back evidence and the
  REV12 verdict verified the read-back content. This
  submission is filed the same way.

## 9. What this revision does not do

- It does not alter, reinterpret, or repair any run-01
  record, any prior revision, any prior verdict, or the
  filed REV9, REV10, REV11, or REV12 submission records.
- It does not satisfy any start condition. No archive
  has been delivered for run-02, no computation or
  re-derivation has been performed under it, no
  catalogue has been queried for it, no participant set
  is named.
- It does not commence Gate 2, assess the subject, or
  assess Duenna.
- It does not shelve itself, submit itself, or speak
  for the examiner.

## Closing disposition

**Revision 13: DRAFT, submitted for Gate 1 examination
when Remmy files it.**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 1 on this revision: NOT YET EXAMINED.**
**Gate 2: NOT COMMENCED.**
**Subject result / Duenna performance: NOT ASSESSED.**

On a Gate 1 PASS, run-02 proceeds under §2–§5 as
written: from a copy, against the frozen originals,
through gates that allow or correct, format computed
by the independent Checker under the exhibited
definition — now with member type determined from type
metadata before any name is consulted, every type/name
disagreement a recorded rejection rather than a silent
exclusion, and run identities bound to their case so
no two cases can mint one — every prerequisite
satisfied and recorded before the clock starts, the
submission's read-back filed with the submission — and
Ben's execution word still to come.
