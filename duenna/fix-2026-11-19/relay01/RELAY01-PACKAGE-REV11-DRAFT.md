# RELAY 01 — PACKAGE REVISION 11 (DRAFT — for Gate 1 examination)

*Status: prepared as a draft on 2026-11-20 under Ben's
tap (widget-fcea0311-56c9-4000-9ea7-6154c44a0c57) and his
words of 2026-11-20 21:17 MST: "Draft REV11 — prove the
archive's contents: ZIP-member check, path grammar,
verdict schema, run-identity construction." Its status
at any time is what the filing record states. This
revision answers Vane's Gate 1 verdict on Revision 10 —
**GATE 1 NOT PASS — RETURN FOR CORRECTION** — filed as
`VANE-GATE1-VERDICT-REV10-2026-11-20.md` (Git blob
28f834774a35bfb955faafdbaec29a490baa01f9, filing commit
c5f4ce7f2124787e6a5cb34747280811042a474c). It governs
run-02 only. Run-01 is closed history: NO START, event
ledger seq 1–7, unaltered and unreinterpreted by
anything in this revision. It satisfies no start
condition by its own existence.*

## 0. Incorporation

Revision 11 incorporates Revision 10 (Git blob
0c9c4cc13a977889c04d4dc5bbbadacff00c0ade; SHA-256
88df9fe7327d8f673b320f16d1078681969fdcaac2fe1499c5dc6b57e40ac5b0)
and its predecessors by reference, together with the
design documents at the pins REV9 §0 recorded (design
paper aae71134…, Annex A a8b17eb9…, Annex B 198f0d5a…),
and replaces the exhibited Gate Format Definition:

- **Gate Format Definition, version 2** —
  `GATE-FORMAT-DEFINITION-V2-DRAFT.md`, SHA-256
  ac3d5e5085fa5691965eae7b7158a6e213fe1f280a618c77889a8568576bc8c4.
  Citation: 2026-11-20/gate-definition/gate-format-definition-v2.

Version 1 of the definition (Git blob
68ab4a45c3f477dcb401aee7c20fb0f632bbc96b, SHA-256
ff42be32baa8f394f1d04d5211e2ecc01df08cb9b201977e706e59bfeeb98e92)
is preserved as filed at commit 0cda1cfe…; version 2
supersedes it as the exhibited definition for run-02,
and no filed text of version 1 is edited. The design
freeze (blob 16543582aaa059b4878a0d8fb1e5c2ab5664f952)
is unchanged. Revisions 1–10, all prior verdicts, and
the REV9 and REV10 submission records are preserved as
history; nothing in this revision edits them. Where
this revision corrects a passage of a prior revision
or annex, §1 and §5 say so explicitly: the filed texts
stand, and this revision's statement governs for
run-02.

## 1. The delta — every finding of the REV10 verdict, answered

**G1-R10-01 — no check binds the manifest to the
archive's actual contents. ANSWERED by exhibit.** Gate
Format Definition version 2 adds **F8,
ARCHIVE–MANIFEST CORRESPONDENCE**: the archive is
opened, every member is enumerated and classified
(regular file / directory entry / symlink / other —
symlinks and other types FAIL), duplicate member names
FAIL, and the complete regular-file member set, minus
the case's named carrier set, is compared with the
manifest set exactly — absent and unlisted members
named — with every compared member's digest recomputed
over its uncompressed bytes and checked against the
manifest. F8 step 9 additionally binds the supplied
manifest to the archive's own manifest member. F4 is
retitled MANIFEST-LINE-COUNT so the three counts are
never conflated again (TV-9 keeps them separate:
manifest lines 686, archive file members 688, total
members 771, for v1). The verdict required positive
and negative vectors: TV-9 exercises F8 against both
real archives (PASS — zero absent, zero unlisted, zero
mismatches over 686 and 687 compared members), and
TV-10, TV-11, and TV-12 are the negative vectors — a
manifest whose digest and syntax are valid but whose
member digest is wrong, an unlisted member, and an
absent member, each failing F8 alone. **On the
verdict's alternative:** the package does **not** ask
Ben to amend the inherited requirement. REV5 §4's full
internal-manifest verification, carried into REV10 §2
P2, is retained in full, and F8 is its procedure. The
assurance boundary is therefore the complete
correspondence — every member, every digest — not a
sample and not the archive digest alone.

**G1-R10-02 — manifest path grammar not safe or
exact. CORRECTED in the definition.** Version 2 states
grammar **G-P** exactly: printable ASCII (0x21–0x7E)
excluding `" * : < > ? \` and `|`; separator a single
`/`; no leading or trailing separator; no adjacent
separators; no segment empty, `.`, or `..`; no segment
ending in `.`; no segment whose stem is a Windows
reserved name (CON, PRN, AUX, NUL, COM1–COM9,
LPT1–LPT9). G-M's distinctness is strengthened from
byte equality to byte equality **and** ASCII
case-folding, for the reason the definition states.
Re-examined at this drafting: all 686 v1 paths and all
687 v2 paths conform to G-P, with zero violations, and
each manifest is case-fold distinct (TV-8, as amended).

**G1-R10-03 — chunk grammar and F6 not fully
case-bound. CORRECTED in the definition.** The
archive-id now has an exact character grammar (§2 of
the definition: 1–32 characters of `[a-z0-9-]`, first
and last alphanumeric) and a meaning only through the
case's archive registry, which binds each archive-id
to exactly one pinned archive digest before any chunk
is examined. F6 gains the case's **expected
archive-id** as a named input and fails at step 0 on
any mismatch or unregistered id; F6 step 4 requires
the header's `N` to equal the supplied manifest's
actual line count. The `k`/`n` boundary is stated
explicitly: F6 checks them locally only; completeness
of the declared chunk set is a routing-record property,
not a format result.

**G1-R10-04 — verdict record a field list, not a
machine-checkable shape. CORRECTED in the
definition.** Version 2 §5.1 states **Verdict Record
Schema V1**: the record is a single UTF-8 JSON object
under six serialization rules (no duplicate keys,
closed field sets at every level, exact integer /
digest / timestamp forms, and a canonical form for
fingerprinting the record itself). All nine top-level
fields are required with exact types; the `checks`
array must equal `applicable_checks` as a set, so an
omitted applicable check invalidates the record
mechanically; the verdict field must agree with the
per-check results; and every check's `values` object
has an exact key set, carrying both the pinned
expected digest and the computed digest wherever a
digest comparison is performed. A valid worked record
and two invalid records with their rejection reasons
are exhibited at §5.2 of the definition.

**G1-R10-05 — K1 run-identity correction lacks a
deterministic minting procedure. CORRECTED in §5.1
below.** The canonical construction is now specified
in the same style as C1's: a framed canonical string
naming every bound input, whose SHA-256 is the run
identity; the identity itself is never an input, so
the construction is not circular; and a refused freeze
is represented exactly as v3 K1 prescribes — minted at
freeze-begin under the same construction, carrying a
governance record, never conflated with a started run.

**G1-R10-06 — submission status and read-back evidence
contradict one another. CORRECTED in §8 below, and in
this draft's own status language.** This draft makes
no standing claim to be unshelved or unsubmitted: its
status is stated as preparation history, and its
status at any time is what the filing record states.
§8 makes it a provision of this package that a
submission's read-back log is filed **inside the
submission itself**, so the evidence lives where the
examiner reads. The historical REV10 submission is not
rewritten; its contradiction is answered by this
revision's practice, not by editing its record.

**The verdict's clarifications, answered.**
(1) *C1 whitespace normalization:* §5.2 adopts the
verdict's cleaner route — the exact canonical string
exhibited in REV10 §5.2 is the sole input to C1's
identity; the normalization sentence is withdrawn. The
identity value is unchanged
(29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d),
because the exhibited string is what the examiner
recomputed. (2) *Run identity versus logical item
identity:* the distinction stands as accepted; §5.1
closes the operational gap only. (3) *TV-1:* the
examiner's independent recomputation is recorded at
TV-1 of the version 2 definition. (4) *Scope of the
definition:* version 2 §1 states the scope as exactly
the procedures defined — which now include the
archive/member comparison, so the statement and the
procedures match.

**Accepted corrections — carried, not re-argued.** The
REV10 verdict accepted: the independent Checker
assignment; C1's item-level identity (independently
recomputed); the three identity distinctions (logical
item, content fingerprint, attempt); the closed
seventeen-token list with its usage rule;
format-scheme labelling; the Adoption Spec authority
clarification; correction C-2; and the correction
record's closing of REV9 Holes 6 and 7. All stand in
this revision exactly as REV10 stated them, except
where §1 above amends a named passage.

**Not changed:** the invocation path entire (REV8
caller 54117c63…, helpers, dependency, timeout
policy); the freeze; the work item (Ob1, NOT
DELIVERED; Q1 OPEN); Gate 2 not commenced.

## 2. Run-02 pre-start verification (P2 revised; the rest carried)

**P1 — Archive delivery (carried from REV10).** The
actual v1 and v2 archive bytes are delivered to both
the originator and the independent checker — as the
copy of §3, hashed into run-02's event ledger at
delivery.

**P2 — Independent archive verification (REVISED per
G1-R10-01 to G1-R10-04).** The load-bearing set is as
REV10 named it — both zip digests (v1 48a171f4…, v2
db96297c…), both manifest digests (v1 bf9f8897…, v2
92b5d98c…), entry counts 686 / 687 — verified under
Gate Format Definition **version 2** (§0):

- **Computation.** Format conformance is computed by
  the **independent Checker (C)** under the version 2
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
  Record Schema V1** (definition §5.1), reproducible by
  an independent third party from the pinned inputs.
  The orchestrator delivers inputs and collects records
  and issues no format verdict.
- **Judgement.** Carried from REV10: the originator and
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

## 3. The copy provision (carried unchanged from REV9 §3, through REV10)

Run-02 works from a copy of the package and shelf
materials, made and hashed at case freeze; the
originals stay frozen on the shelf as the audit
baseline; identity between copy and original is
digest-for-digest and the copy carries no authority of
its own; divergences found at audit are recorded as
discrepancies with both digests preserved, never
silently reconciled. (Ben's direction, 2026-11-20
20:33 MST.)

## 4. Check-in gates — ALLOW or CORRECT (carried from REV10 §4)

The gate structure is REV10 §4, carried entire:
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

## 5. Catalogue and citation provisions (§5.1 and §5.2 corrected; the rest carried)

The catalogue provisions are REV10 §5, carried, with
the two corrections below. Index rows are DC records
per Annex B §B2.1 as adopted; the citation form
`<YYYY-MM-DD>/<type-token>/<slug>` stands; existing
citations remain aliases, never rewritten.

### 5.1 Run identity — the deterministic construction (G1-R10-05)

REV10 §5.1's conceptual correction stands: a run's
identity is its **K1 run identity**, minted by the
BINDER at the moment a freeze attempt begins, binding
by reference one configuration identity (K3), one
verified subject identity (K2), and one frozen
tree-set identity; the configuration digest is a typed
Relation (References) in the run's record, never its
Identifier. What REV10 lacked, and this section
supplies, is the minting procedure.

The run identity is the **SHA-256 of the following
canonical string** (UTF-8, LF line endings, final LF
included) — the framed construction of
`DUENNA-RUN-IDENTITY-v1`:

```
DUENNA-RUN-IDENTITY-v1
configuration-id: <the K3 configuration identity — the configuration object's content digest, 64 lowercase hex>
subject-id: <the K2 verified subject identity, byte-exact as recorded in the case's subject record>
tree-set-id: <the frozen tree-set identity, 64 lowercase hex>
freeze-begin-utc: <the freeze-begin time, UTC, in the form YYYY-MM-DDTHH:MM:SS.mmmZ>
```

The rules of the construction:

- **Inputs are exactly the four bound values.** The
  string names the three K1 bindings and the
  freeze-begin time, in the order shown, and nothing
  else. Any reader with the case's recorded binding
  values can recompute the identity.
- **No circularity.** The run identity is the digest
  of the string; the string contains no run-identity
  field and no field derived from the output digest.
  The identity is an output, never an input.
- **One minting per freeze-begin.** Each freeze-begin
  act mints exactly one identity under this
  construction. A later freeze-begin is a new act with
  its own freeze-begin time and therefore its own
  identity, even if the three bindings are unchanged.
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

**Worked illustration (constructed for illustration;
binds no real run).** With configuration-id =
`aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
subject-id =
`bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`,
tree-set-id =
`cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`,
and freeze-begin-utc = `2026-11-20T00:00:00.000Z`, the
canonical string's SHA-256, computed at this drafting,
is:

**45a204494e71af85d760efe15c1e92f6e1f7e337429fb38a9d8f17d37ce14343**

### 5.2 C1's item-level identity (carried from REV10 §5.2, with the clarification amendment)

C1's item identity stands as REV10 §5.2 constituted
it: the SHA-256 of the canonical string exhibited
there in full, computed value
**29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d**,
independently recomputed by the examiner in both the
REV9 and REV10 rounds. C1's content, authority
statement, and delivery terms are exactly as frozen in
REV5 §3 and carried since; the container digest
appears only in C1's source reference and IsPartOf
relation, labelled as the container's, never as C1's
Identifier; the sealed delivery artefact is a derived
representation of the same item with its own content
fingerprint.

**Amendment (verdict clarification 1).** REV10 §5.2's
sentence describing the assertion as "whitespace
normalised to single spaces" is withdrawn. The rule
for this construction is now: **the exact canonical
string as exhibited in REV10 §5.2 is the sole input** —
its bytes (UTF-8, LF line endings, final LF included)
are the input, and no normalization is applied to
anything, by anyone, at any point. Any future
item-identity construction of this framed form must
exhibit its canonical string in full, as REV10 §5.2
did, so that the string itself is the input of record.

### 5.3 Type tokens (carried from REV10 §5.3)

The closed list of seventeen tokens stands, membership
unchanged, under the usage rule REV10 §5.3 stated: a
collection or register of a kind is catalogued with
the token `record`; `event` only for an individually
indexed event; `defect` only for an individual DR
entry.

### 5.4 Format values name their scheme (carried from REV10 §5.4)

Every Format value in a run-02 record names its
scheme — IMT, or the Duenna Local Format Scheme whose
one current value is `application/jsonl`, used only
for the event ledger. A local-scheme value is never
recorded bare.

## 6. Design commitments (carried from REV10 §6)

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

### 7.1 The Adoption Spec's authority (carried from REV10 §7.1)

Ben's ruling of 2026-11-20 20:43 MST adopted Annex B
(Dublin Core) as the package's catalogue basis,
confirmed by the examiner in the REV9 verdict and
accepted again in the REV10 verdict; Annex A is
retained as the studied alternative. The Adoption Spec
was **not** adopted and remains a draft that enacts
nothing. The operative vocabulary, the GATE
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
  recorded (freeze §11(6)). His 21:17 tap commissioned
  this draft; it is not an execution authorisation.

### 7.4 Remaining examiner items

The §5.1 run-identity construction (this draft's
specification, stated for the examiner's examination);
design §6 Q8 (whether the Gate Format Definition as
exhibited — now version 2 — discharges the T02/T07/T09
response-format contracts for gate contexts) and Q9
(the grade of run-01's mechanical cross-check
evidence) — noted, not settled here. Design §6 Q4
remains closed by the REV9 verdict (Part II accepted);
Q5 remains closed by G1-R9-02.

## 8. Submission integrity (new, per G1-R10-06)

- **Status language.** A package revision's status
  block states its preparation history — who prepared
  it, under what authority, and when — and no standing
  claim about its filing state. Its status at any time
  is what the filing record (the shelf commit and the
  covering submission record) states. This draft is
  written to that rule, as is the version 2 definition.
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
  log the examiner cannot fetch.

## 9. What this revision does not do

- It does not alter, reinterpret, or repair any run-01
  record, any prior revision, any prior verdict, or the
  filed REV9 or REV10 submission records — including
  REV10's contradictory status language, which stands
  as filed and is answered by §8's practice, not by
  editing it.
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

**Revision 11: DRAFT, submitted for Gate 1 examination
when Remmy files it.**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 1 on this revision: NOT YET EXAMINED.**
**Gate 2: NOT COMMENCED.**
**Subject result / Duenna performance: NOT ASSESSED.**

On a Gate 1 PASS, run-02 proceeds under §2–§5 as
written: from a copy, against the frozen originals,
through gates that allow or correct, format computed
by the independent Checker under the exhibited
definition — now including full archive–manifest
correspondence — every prerequisite satisfied and
recorded before the clock starts, the submission's
read-back filed with the submission — and Ben's
execution word still to come.
