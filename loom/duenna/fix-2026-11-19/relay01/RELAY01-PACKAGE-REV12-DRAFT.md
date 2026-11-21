# RELAY 01 — PACKAGE REVISION 12 (DRAFT — for Gate 1 examination)

*Status: prepared as a draft on 2026-11-20 under Ben's
tap (widget-c40e8bac-79f6-4562-87b2-b62f59413470) and his
words of 2026-11-20 21:36 MST: "Draft REV12 — make every
failure recordable: complete verdict schema, pinned ZIP
name rules, framed run identity." Its status at any time
is what the filing record states. This revision answers
Vane's Gate 1 verdict on Revision 11 — **GATE 1 NOT
PASS — RETURN FOR CORRECTION** — filed as
`VANE-GATE1-VERDICT-REV11-2026-11-20.md` (Git blob
a353d6c15f2d34af57f0a2b2758bd5782fbf833c, filing commit
3f09a733e36def408d4b3ca5eea693558484484a). It governs
run-02 only. Run-01 is closed history: NO START, event
ledger seq 1–7, unaltered and unreinterpreted by
anything in this revision. It satisfies no start
condition by its own existence.*

## 0. Incorporation

Revision 12 incorporates Revision 11 (Git blob
10e2657abc61e965b79ebdfb873778a272fb9eb4; SHA-256
6a17a0a1728c9d5482f775f4587c7e324d2d824e677293db5216ccb944af2d80)
and its predecessors by reference, together with the
design documents at the pins REV9 §0 recorded (design
paper aae71134…, Annex A a8b17eb9…, Annex B 198f0d5a…),
and replaces the exhibited Gate Format Definition:

- **Gate Format Definition, version 3** —
  `GATE-FORMAT-DEFINITION-V3-DRAFT.md`, SHA-256
  97a262e35ea827315c6b4e95d22866adbe60d2a80c8454ac5f5e237ea496f325.
  Citation: 2026-11-20/gate-definition/gate-format-definition-v3.

Version 2 of the definition (Git blob
5fdd1a00714935899ffe3f038b02f8b03cf67ebd, SHA-256
ac3d5e5085fa5691965eae7b7158a6e213fe1f280a618c77889a8568576bc8c4)
is preserved as filed at commit 7e4bd6b7…; version 3
supersedes it as the exhibited definition for run-02,
and no filed text of version 2 (or version 1) is edited.
The design freeze (blob 16543582aaa059b4878a0d8fb1e5c2ab5664f952)
is unchanged. Revisions 1–11, all prior verdicts, and
the REV9, REV10, and REV11 submission records are
preserved as history; nothing in this revision edits
them. Where this revision corrects a passage of a prior
revision or annex, §1 and §5 say so explicitly: the
filed texts stand, and this revision's statement governs
for run-02.

## 1. The delta — every finding of the REV11 verdict, answered

**G1-R11-01 — Verdict Record Schema V1 cannot represent
all defined F8 outcomes; F6 cannot represent an absent
or unparseable header. ANSWERED by exhibit.** Gate
Format Definition version 3 §5.1 states **Verdict
Record Schema V2**. The F8 values shape now carries a
field for every outcome F8's procedure defines:
`structure` ("readable"/"unreadable") for the step-1
parse failure; `duplicate_names` in full (step 3);
`rejected_members` with each member's type (step 4);
`invalid_names` (the new step 5, below);
`manifest_parseable` (step 7); `missing_carriers`
(step 7); `carrier_manifest` with both digests (step
10); and `mismatches` — **every** digest mismatch, each
with its path and both digests — replacing Schema V1's
first-mismatch-only record, with `mismatch_count`
retained under the rule that it equals the list's
length. A stated not-performed convention (fields of
steps above `failed_step` carry empty values; the
member counts are recorded whenever the structure is
readable) makes exactly how far the procedure ran
reconstructible from the record alone. For F6, the
procedure gains a step H (header extraction) with a
three-value `header_status` ("read"/"absent"/
"unparseable"); `declared_archive_id` is nullable, and
`failed_step` names "header" for the case where no
declared id could be read — an absent or unparseable
header is now an ordinary recordable FAIL, not an
unrecordable state. Worked records exercising the new
branches are exhibited at §5.2 of the definition: a
duplicate-name failure record (TV-13) and a symlink
failure record (TV-14), both valid under Schema V2, a
Schema-V1-shaped record rejected under it with reasons,
and TV-15's two header cases. All three exhibited valid
records were validated mechanically against Schema V2
as written, at this drafting.

**G1-R11-02 — F8 applies no safe name rule to directory
entries and defines no ZIP name-byte interpretation.
ANSWERED by exhibit.** Version 3 §3 adds grammar
**G-N**: a member's name is the raw filename byte
sequence of its central-directory header; the local
header is not consulted; no decoding is applied — the
UTF-8 general-purpose flag (bit 11), legacy code pages,
and all extra fields including Unicode Path (0x7075)
play no part in determining the name and neither rescue
nor condemn it. A name conforms iff its raw bytes
satisfy G-P — for a directory entry, the bytes with the
single trailing separator removed must satisfy G-P in
full. Because G-P admits only printable ASCII, every
conforming name reads identically under every
ASCII-superset interpretation: ambiguity is excluded by
the grammar, not by choosing a decoding. F8 gains a
step 5 validating **every** member name, directory
entries included, recording every invalid name; the
allowance for legitimate empty directory entries is
preserved (step 6, as before). The rule was exercised
against both real archives at this drafting by raw
central-directory parse (TV-16 of the definition): in
v1, the UTF-8 flag is clear on all 771 members (every
flag value 0), extra fields are 0x5455 and 0x7875 only,
0x7075 occurs nowhere, no name byte is ≥ 0x80, and all
83 directory-entry names (stripped) and all 688
regular-file names conform to G-P; v2 is identical in
kind (772 members). No violation was found in either
archive, and none is softened: had any name failed, it
would be recorded here and at TV-16.

**G1-R11-03 — K1 run-identity framing not unambiguous
or collision-safe across freeze attempts. CORRECTED in
§5.1 below.** The construction is rebuilt as
`DUENNA-RUN-IDENTITY-v2`: every field is length-prefixed,
so no field's bytes — the subject-id above all — can
imitate framing or swallow a neighbouring field, and
the construction depends on no field's grammar. A fifth
field, `freeze-attempt-seq`, carries the freeze-begin
event's sequence number in the case's event ledger: a
value unique to the act by the ledger's own monotonic
rule, assigned before minting, so two freeze attempts
with identical bindings in the same millisecond mint
different identities — exhibited by two computed
illustrations differing only in that field.

**The verdict's TV-9 note — recorded accurately.** The
REV11 verdict states that the examiner has not
independently rerun F8 against the two ZIP byte
streams, and that TV-9's results stand as the
orchestrator's reported exercise. This revision records
that distinction exactly: TV-9 (and the new TV-16
census) are orchestrator computations, exhibited in the
definition with their inputs pinned and their methods
stated so the examiner can rerun them byte-for-byte.
Nothing in this revision claims her verification of
them, and her not having rerun them is not treated as
a defect in her examination.

**Accepted in the REV11 verdict — carried, not
re-argued.** The verdict accepted: F8 as a substantial
and appropriate answer to G1-R10-01, with the inherited
full internal-manifest requirement retained, not
waived; G-P as materially answering G1-R10-02 for
manifest paths; the archive-id registry and F6 changes
as materially answering G1-R10-03; the read-back
evidence as answering G1-R10-06 at the submission level;
and the C1 clarification. The REV10 verdict's accepted
corrections remain accepted (independent Checker
responsibility; the identity separations; the closed
type-token list; format-scheme labelling; the Adoption
Spec authority clarification; C-2; the REV9 correction
record). All stand in this revision exactly as REV11
stated them, except where §1 above amends a named
passage. The verdict also records that design Q8 and
Q9 remain open examination items; §7.4 carries them as
open — this revision does not silently close them.

**Not changed:** the invocation path entire (REV8
caller 54117c63…, helpers, dependency, timeout
policy); the freeze; the work item (Ob1, NOT
DELIVERED; Q1 OPEN); Gate 2 not commenced.

## 2. Run-02 pre-start verification (P2 revised; the rest carried)

**P1 — Archive delivery (carried from REV11).** The
actual v1 and v2 archive bytes are delivered to both
the originator and the independent checker — as the
copy of §3, hashed into run-02's event ledger at
delivery.

**P2 — Independent archive verification (REVISED per
G1-R11-01 and G1-R11-02).** The load-bearing set is as
REV11 named it — both zip digests (v1 48a171f4…, v2
db96297c…), both manifest digests (v1 bf9f8897…, v2
92b5d98c…), entry counts 686 / 687 — verified under
Gate Format Definition **version 3** (§0):

- **Computation.** Format conformance is computed by
  the **independent Checker (C)** under the version 3
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
  Record Schema V2** (definition §5.1), reproducible by
  an independent third party from the pinned inputs.
  The orchestrator delivers inputs and collects records
  and issues no format verdict.
- **Judgement.** Carried from REV11: the originator and
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

**P6 — Envelope and identity checks (carried).** All
frozen-design participant, distinctness,
finisher-exclusivity, source-envelope, and no-start
checks, completed and recorded. Run identity at this
gate is the K1 identity of §5.1, constituted by the
construction stated there, never a configuration
digest.

**P7 — Correction delivery (carried, unchanged).** C1
must be delivered during Holder 2's tenure exactly as
frozen; its identity for delivery and ledger purposes
is the item identity of §5.2. Non-delivery renders the
relay INVALID; no substitute correction may be planted.

Any missing, failed, or unverifiable prerequisite
means NO START for run-02, the failure record preserved.

## 3. The copy provision (carried unchanged from REV9 §3, through REV11)

Run-02 works from a copy of the package and shelf
materials, made and hashed at case freeze; the
originals stay frozen on the shelf as the audit
baseline; identity between copy and original is
digest-for-digest and the copy carries no authority of
its own; divergences found at audit are recorded as
discrepancies with both digests preserved, never
silently reconciled. (Ben's direction, 2026-11-20
20:33 MST.)

## 4. Check-in gates — ALLOW or CORRECT (carried from REV11 §4)

The gate structure is REV11 §4, carried entire:
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

The catalogue provisions are REV11 §5, carried, with
the one correction below. Index rows are DC records
per Annex B §B2.1 as adopted; the citation form
`<YYYY-MM-DD>/<type-token>/<slug>` stands; existing
citations remain aliases, never rewritten.

### 5.1 Run identity — the framed, collision-safe construction (G1-R11-03)

REV11 §5.1's conceptual settlement stands: a run's
identity is its **K1 run identity**, minted by the
BINDER at the moment a freeze attempt begins, binding
by reference one configuration identity (K3), one
verified subject identity (K2), and one frozen
tree-set identity; the configuration digest is a typed
Relation (References) in the run's record, never its
Identifier. What the REV11 verdict found defective was
the construction itself: the subject-id entered a
line-framed string with no stated byte grammar, so a
subject-id containing LF or field-like text could make
the string ambiguous; and the millisecond timestamp
was the only thing distinguishing one freeze attempt
from another, which two attempts can share. Both
defects are corrected here. The REV11 construction
(`DUENNA-RUN-IDENTITY-v1`) is superseded for run-02;
it stands as filed history, and no identity was ever
minted under it — no freeze-begin has occurred under
this package — so no run identity is orphaned by the
change.

The run identity is the **SHA-256 of the following
canonical string** (UTF-8, LF line endings, final LF
included) — the length-framed construction of
`DUENNA-RUN-IDENTITY-v2`:

```
DUENNA-RUN-IDENTITY-v2
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

- **Framing makes every field delimiter-safe.** A
  reader of the canonical string consumes each value
  by its stated length, not by scanning for line ends.
  A value may therefore contain any bytes at all — LF,
  colons, text shaped like another field line — without
  ambiguity: the length, not the content, fixes the
  boundary. The construction imposes no grammar on the
  subject-id or on any other field; each field's own
  form (digests as 64 lowercase hex, the timestamp in
  its stated form) is a property of the case's records,
  not a load-bearing assumption of the identity.
- **The attempt sequence guarantees distinctness.**
  `freeze-attempt-seq` is the sequence number the
  case's event ledger assigns to the freeze-begin
  event. Its authority is the ledger itself: the
  ledger's sequence is monotonic, one number per event,
  never reused within the case. The minting rule is:
  the BINDER first records the freeze-begin event in
  the ledger, which assigns its sequence number; the
  BINDER then computes the identity over the five
  fields, that number included; the minting is recorded
  under the resulting identity in a subsequent
  governance record citing the sequence number. Two
  distinct freeze attempts are two distinct ledger
  events with two distinct sequence numbers, so their
  canonical strings differ in the seq field even if the
  three bindings and the millisecond timestamp all
  coincide. The timestamp remains in the construction
  as evidence of when the attempt began; it is no
  longer the uniqueness carrier.
- **Inputs are exactly the five bound values,** in the
  order shown, and nothing else. Any reader with the
  case's recorded binding values, the freeze-begin
  time, and the ledger sequence number can recompute
  the identity.
- **No circularity.** The run identity is the digest
  of the string; the string contains no run-identity
  field and no field derived from the output digest.
  The sequence number is assigned by the ledger before
  minting and does not depend on the identity. The
  identity is an output, never an input.
- **One minting per freeze-begin.** Each freeze-begin
  act is one ledger event and mints exactly one
  identity under this construction.
- **A refused freeze.** The identity is minted at
  freeze-begin, before the freeze's outcome is known,
  under this same construction. A refused freeze is
  recorded **under** that identity as a governance
  record (freeze attempted, refused, reason — v3 K1);
  the identity denotes the run record of that attempt
  and never denotes a started run. `RUN_STARTED` is a
  separate event referencing the identity, emitted only
  on a successful freeze. Attempt and started run are
  therefore never conflated: an identity with no
  RUN_STARTED event is a run that never started.

**Worked illustrations (constructed for illustration;
they bind no real run).** With configuration-id =
`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
subject-id =
`bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`,
tree-set-id =
`cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`,
and freeze-begin-utc = `2026-11-20T00:00:00.000Z`, the
canonical string is:

```
DUENNA-RUN-IDENTITY-v2
configuration-id:64:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
subject-id:64:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
tree-set-id:64:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
freeze-begin-utc:24:2026-11-20T00:00:00.000Z
freeze-attempt-seq:1:1
```

With `freeze-attempt-seq` = `1`, its SHA-256, computed
at this drafting, is:

**852aee87d21c0778a9d7e728fe4d57dcfd6dafdb435694b4faabe52e2866c429**

With every other field identical and
`freeze-attempt-seq` = `2` — the case the REV11
verdict names, two attempts the timestamp cannot
separate — the SHA-256 is:

**7d9d36a273f406383186abfd799699ba4885c5f80c89120d5cfab3924c7b5324**

The two identities differ, as the construction
requires. (The REV11 illustration under the superseded
v1 construction recomputes to its filed value
45a20449…; it stands as history.)

### 5.2 C1's item-level identity (carried from REV11 §5.2)

C1's item identity stands as REV10 §5.2 constituted it
and REV11 §5.2 carried it: the SHA-256 of the canonical
string exhibited in REV10 §5.2 in full, computed value
**29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d**,
independently recomputed by the examiner in the REV9
and REV10 rounds, and its clarification accepted in the
REV11 verdict: **the exact canonical string as
exhibited is the sole input** — its bytes (UTF-8, LF
line endings, final LF included) are the input, and no
normalization is applied to anything, by anyone, at any
point. C1's content, authority statement, and delivery
terms are exactly as frozen in REV5 §3 and carried
since; the container digest appears only in C1's source
reference and IsPartOf relation, labelled as the
container's, never as C1's Identifier; the sealed
delivery artefact is a derived representation of the
same item with its own content fingerprint.

### 5.3 Type tokens (carried from REV11 §5.3)

The closed list of seventeen tokens stands, membership
unchanged, under the usage rule REV10 §5.3 stated: a
collection or register of a kind is catalogued with
the token `record`; `event` only for an individually
indexed event; `defect` only for an individual DR
entry.

### 5.4 Format values name their scheme (carried from REV11 §5.4)

Every Format value in a run-02 record names its
scheme — IMT, or the Duenna Local Format Scheme whose
one current value is `application/jsonl`, used only
for the event ledger. A local-scheme value is never
recorded bare.

## 6. Design commitments (carried from REV11 §6)

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

### 7.1 The Adoption Spec's authority (carried from REV11 §7.1)

Ben's ruling of 2026-11-20 20:43 MST adopted Annex B
(Dublin Core) as the package's catalogue basis,
confirmed by the examiner in the REV9 verdict and
accepted again in the REV10 and REV11 verdicts; Annex
A is retained as the studied alternative. The Adoption
Spec was **not** adopted and remains a draft that
enacts nothing. The operative vocabulary, the GATE
disambiguation, the twelve NO TERM entries as open
vocabulary questions for Ben, and the ENVELOPE
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
  recorded (freeze §11(6)). His 21:36 tap commissioned
  this draft; it is not an execution authorisation.

### 7.4 Remaining examiner items

The §5.1 run-identity construction in its v2 form
(this draft's specification, stated for the examiner's
examination); design §6 Q8 (whether the Gate Format
Definition as exhibited — now version 3 — discharges
the T02/T07/T09 response-format contracts for gate
contexts) and Q9 (the grade of run-01's mechanical
cross-check evidence) — both expressly left open by
the REV11 verdict, noted here, not settled. Design §6
Q4 remains closed by the REV9 verdict (Part II
accepted); Q5 remains closed by G1-R9-02.

## 8. Submission integrity (carried from REV11 §8)

- **Status language.** A package revision's status
  block states its preparation history — who prepared
  it, under what authority, and when — and no standing
  claim about its filing state. Its status at any time
  is what the filing record (the shelf commit and the
  covering submission record) states. This draft is
  written to that rule, as is the version 3 definition.
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
  log the examiner cannot fetch. The REV11 submission
  was filed under this provision and its read-back
  evidence was accepted in the REV11 verdict; this
  submission is filed the same way.

## 9. What this revision does not do

- It does not alter, reinterpret, or repair any run-01
  record, any prior revision, any prior verdict, or the
  filed REV9, REV10, or REV11 submission records.
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

**Revision 12: DRAFT, submitted for Gate 1 examination
when Remmy files it.**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 1 on this revision: NOT YET EXAMINED.**
**Gate 2: NOT COMMENCED.**
**Subject result / Duenna performance: NOT ASSESSED.**

On a Gate 1 PASS, run-02 proceeds under §2–§5 as
written: from a copy, against the frozen originals,
through gates that allow or correct, format computed
by the independent Checker under the exhibited
definition — now with every failure the archive check
can produce recordable in the verdict record, every
member name read under one pinned byte rule, and run
identities framed so no field can blur into another
and no two freeze attempts can share one — every
prerequisite satisfied and recorded before the clock
starts, the submission's read-back filed with the
submission — and Ben's execution word still to come.
