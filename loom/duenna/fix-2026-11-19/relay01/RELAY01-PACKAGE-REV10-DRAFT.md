# RELAY 01 — PACKAGE REVISION 10 (DRAFT — for Gate 1 examination)

*Status: DRAFT. Prepared under Ben's tap
(widget-6b839991-36ba-402b-a177-c82a8b486ac5) and his words
of 2026-11-20 21:03 MST: "Draft REV10 — produce the Gate
Format Definition and apply Vane's corrections, paper
first." This revision answers Vane's Gate 1 verdict on
Revision 9 — **GATE 1 NOT PASS: RETURN FOR CORRECTION** —
filed as `VANE-GATE1-VERDICT-REV9-2026-11-20.md` (Git blob
68821e205d216c5bc531f240dfaa3b94f99b0f4d, filing commit
b0393c37ea1e559da6b871de0386429e49b0a2d3). This draft is a
local, unshelved document; it has not been submitted to
Gate 1, and it satisfies no start condition by its own
existence. It governs run-02 only. Run-01 is closed
history: NO START, event ledger seq 1–7, unaltered.*

## 0. Incorporation

Revision 10 incorporates Revision 9 (Git blob
e217c3a28408a56c47bb2fce365ded18154eb9e4; SHA-256
570bc1a730ce3fb261118c6ff41240f96a92eb01f0f3e9133583bda032fc47db)
and its predecessors by reference, together with the
design documents at the pins REV9 §0 recorded (design
paper aae71134…, Annex A a8b17eb9…, Annex B 198f0d5a…),
and adds one new exhibited artefact:

- **Gate Format Definition** —
  `GATE-FORMAT-DEFINITION-DRAFT.md`, SHA-256
  ff42be32baa8f394f1d04d5211e2ecc01df08cb9b201977e706e59bfeeb98e92.
  Citation: 2026-11-20/gate-definition/gate-format-definition.

The design freeze (blob 16543582aaa059b4878a0d8fb1e5c2ab5664f952)
is unchanged. Revisions 1–9, all prior verdicts, and the
REV9 submission records (bundle manifest, known-holes
statement) are preserved as history; nothing in this
revision edits them. Where this revision corrects a
passage of Annex B or of the Adoption Spec, §1 and §5 say
so explicitly: the filed texts stand, and this revision's
statement governs for run-02, so the examiner can check
each correction against the filed passage it corrects.

## 1. The delta — every finding of the REV9 verdict, answered

**G1-R9-01 — Gate Format Definition absent. CLOSED by
exhibit.** The definition now exists and is incorporated
above by its digest: grammars (manifest line, manifest
file, chunk), seven checks (F1 archive identity, F2
manifest identity, F3 manifest conformance, F4 entry
count, F5 required-path presence, F6 chunk conformance,
F7 named-exhibit identity), the verdict composition rule,
the verdict record's exact fields, and eight worked test
vectors (TV-1–TV-8) including the real v1/v2 manifests.
It relies on no named executable (§8 of the definition);
any tool used is named, with version and digest, in each
computation record.

**G1-R9-02 — computation authority. SETTLED as the
examiner ruled.** The independent Checker (C) performs
the authoritative deterministic format computation under
the pinned definition. The orchestrator delivers inputs
and collects records; it is not the sole or authoritative
producer of any format verdict. §2 P2 below is revised to
state this; REV9 §7.3's open variants are withdrawn. A
participant LLM's reasoning step is not a MECHANICAL
computation (definition §1).

**G1-R9-03 — run identity conflated with configuration
identity. CORRECTED in §5.** Annex B §B4.2's assignment of
the frozen configuration digest as the run's Identifier
is wrong under K1 and is superseded for run-02 by §5.1.

**G1-R9-04 — C1 has no item-level identity. CORRECTED in
§5.** §5.2 gives C1 one deterministic item-level identity,
distinct from the REV5 container fingerprint, under the
Part II model the examiner accepted; the container digest
is never used as C1's Identifier.

**G1-R9-05 — CORRECT re-presentation conflicts with
content-fingerprint identity. CORRECTED in §4.** Logical
item identity, content fingerprint, and attempt identity
are distinguished; a changed byte sequence receives its
own content fingerprint and links to its predecessor by
supersession. No fingerprint is preserved across changed
content.

**G1-R9-06 — type-token examples do not match the closed
list. CORRECTED in §5.** The closed list's membership is
unchanged (seventeen tokens); the usage rule the verdict
proposed is adopted and stated in §5.3, and the two
out-of-list usages (`event-ledger`, `defect-register`)
are corrected to `record`.

**G1-R9-07 — Adoption Spec authority and open vocabulary
unclear. CLARIFIED in §7.** Ben's 20:43 ruling adopted
Annex B; it did not adopt the Adoption Spec, which
remains a draft that enacts nothing. §7.1 states precisely
which vocabulary is operative for run-02 and on what
standing, and which remains non-operative proposal —
including the twelve NO TERM entries, the GATE
disambiguation, and the ENVELOPE collision carried as an
explicit future compatibility item.

**G1-R9-08 — `application/jsonl` not scheme-labelled.
CORRECTED in §5.** §5.4 names a local format scheme,
distinct from IMT; every Format value in a run-02 record
names its scheme.

**G1-R9-09 — submission gates recorded open in the filed
bundle. ANSWERED by a separate record.** The filed bundle
manifest and known-holes statement are preserved
unchanged, as the verdict requires. Their stale OPEN
marks for Holes 6 and 7 are closed by the separately
filed correction record
(`CORRECTION-RECORD-KNOWN-HOLES-STATUS.md`), which carries
the read-back evidence (exact paths, Git blob identities,
recomputed SHA-256 values against the incorporation pins,
verified at commit 788c9079…) and Remmy's first-hand
review disposition for Hole 7. The bridge assertion alone
amends nothing; the record does.

**Correction C-2 — discovered in drafting REV10, not a
verdict finding.** REV9 §2 named the archive gate's
required paths as "README-EXECUTION.md and
stage9/STAGE9-REPORT.md". Checked against the manifests
as filed, both names are wrong in form: manifest paths
carry the prefix `duenna-fix-2026-11-19/` (the report is
entered as `duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`,
line 339 of the v1 manifest), and README-EXECUTION.md is
**not a manifest entry in either archive** — it is an
exhibit file riding beside the manifest in
`exhibits-zip-identity/`. Under a mechanical F5 check,
REV9's named set would have failed against the real
manifests. §2 P2 corrects the set: F5 names
`duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md`; the
README exhibits are verified by digest under F7 against
their baseline pins. Flagged here so the examiner sees
the correction and its evidence, not a silent repair.

**Semantic-loss findings — carried.** (i) A verdict's DC
record establishes authorship and filing, never issuance:
for every Gate 1 verdict the package relies on, the
filing commit and the issuing-authority evidence are
preserved as separate records alongside the verdict's
catalogue row (for the REV9 verdict: filing commit
b0393c37…, blob 68821e20…). A matching blob proves
content identity, not that Vane issued the verdict or
that its conclusion is correct. (ii) A call record is not
a chunk record: `av-o-v1-r4-c11-r3` is the REV8 caller's
record *about* chunk `o-v1-r3-c11.txt`; the two keep
separate rows, identities, and tokens (`record` and
`chunk` respectively) in every run-02 index. (iii) The
PMEST strains Annex A recorded (Space-as-locator, Time/
ordinal compromises, Energy precedence) are not inherited;
process relations that are load-bearing remain explicit
in the case and ledger, per the verdict.

**Not changed:** the invocation path entire (REV8 caller
54117c63…, helpers, dependency, timeout policy — as
REV9 §1 recorded); the freeze; the work item (Ob1, NOT
DELIVERED; Q1 OPEN); Gate 2 not commenced.

## 2. Run-02 pre-start verification (P2 revised; the rest carried)

**P1 — Archive delivery (carried from REV9).** The actual
v1 and v2 archive bytes are delivered to both the
originator and the independent checker — as the copy of
§3, hashed into run-02's event ledger at delivery.

**P2 — Independent archive verification (REVISED per
G1-R9-01, G1-R9-02, C-2).** The load-bearing set is as
REV9 named it — both zip digests (v1 48a171f4…, v2
db96297c…), both manifest digests (v1 bf9f8897…, v2
92b5d98c…), entry counts 686 / 687 — with the required-
path set corrected per C-2: F5 names
`duenna-fix-2026-11-19/stage9/STAGE9-REPORT.md` in each
manifest; the README-EXECUTION.md exhibits are verified
under F7 against their baseline digests (v1 f15fbf6d…,
v2 fa982447…).

- **Computation.** Format conformance is computed under
  the Gate Format Definition (§0) — checks F1–F5 and F7
  per archive — by the **independent Checker (C)**, whose
  computation record carries: the checker's identity;
  the definition's citation and digest; both input
  identities (artefact citation and computed digest) for
  every input; every per-check result with its computed
  values; the composed verdict; the tool's name, version
  and digest where a tool was used; and the time, UTC.
  The computation must be reproducible by an independent
  third party from the pinned inputs. The orchestrator
  delivers inputs and collects records and issues no
  format verdict.
- **Judgement.** The originator and the checker each
  independently judge the content claim — that the
  archive each received is the archive this package
  names — anchored by digests obtained independently of
  the delivering channel, recorded as judgement with its
  evidence (REV9 §2, carried).
- **Transport.** A computation whose inputs were not
  delivered produces no verdict: the item is recorded
  UNEXAMINED, the attempt preserved, never FAILED and
  never retried away (definition §5).

**P3 — Initial ground-truth verification (carried,
re-scoped as REV9).** Each G1–G10 citation resolves
through the index to its fingerprint before support is
judged; a wrong-fingerprint resolution is a recorded
resolution failure. No silent post-start repair.

**P4 — Live catalogue check (carried).** Every assigned
model re-verified against the live provider catalogues
before run-02 opens; raw responses and timestamps
preserved. The assigned set is §7.2's — named and
approved before case freeze, not defaulted.

**P5 — Run-start invocation check (carried, with the
verdict's classification stated).** A fresh invocation
per assigned provider through the exact REV8 caller, all
identities and exit statuses preserved. A provider 503
or any other failed run-start invocation is a **failed
attempt**: it leaves this prerequisite NOT SATISFIED and
means NO START. No route-around and no participant
substitution is implied or permitted under this package.

**P6 — Envelope and identity checks (carried).** All
frozen-design participant, distinctness, finisher-
exclusivity, source-envelope, and no-start checks,
completed and recorded. Run identity at this gate is the
K1 identity of §5.1, never a configuration digest.

**P7 — Correction delivery (carried, unchanged).** C1
must be delivered during Holder 2's tenure exactly as
frozen; its identity for delivery and ledger purposes is
the item identity of §5.2. Non-delivery renders the
relay INVALID; no substitute correction may be planted.

Any missing, failed, or unverifiable prerequisite means
NO START for run-02, the failure record preserved.

## 3. The copy provision (carried unchanged from REV9 §3)

Run-02 works from a copy of the package and shelf
materials, made and hashed at case freeze; the originals
stay frozen on the shelf as the audit baseline; identity
between copy and original is digest-for-digest and the
copy carries no authority of its own; divergences found
at audit are recorded as discrepancies with both digests
preserved, never silently reconciled. (Ben's direction,
2026-11-20 20:33 MST.)

## 4. Check-in gates — ALLOW or CORRECT, with the identity distinction (G1-R9-05)

The gate structure is REV9 §4, carried: established
gates named in the case in advance, in the flow; outcomes
ALLOW or CORRECT; a gate never edits the artefact; an
uncorrectable item is recorded NOT SATISFIED and the §2
prerequisite rule applies.

The re-presentation rule is corrected to distinguish
three identities that REV9 §4 and design §3.6 ran
together:

- **Logical item identity** — the Part II information
  item's one canonical identity, stable across the item's
  whole life: a correction, a grade change, a derivation
  never mints a different item identity (v3 Part II).
  For artefacts with their own bytes, the item identity
  is the identity under which the item is indexed; for
  contained items it is constituted as §5.2 constitutes
  C1's.
- **Content fingerprint** — the digest of one immutable
  byte sequence. It belongs to that byte sequence only.
  If the producer changes the bytes, the changed bytes
  receive their **own** content fingerprint; the old
  fingerprint is never carried across changed content.
- **Attempt identity** — each presentation of an item at
  a gate is a distinct attempt under the item's logical
  identity, linked to the act that opened it (Ben's
  re-presentation ruling, 2026-11-11, as design §3.6
  cites it).

A CORRECT outcome therefore returns the named discrepancy
to the producing step; the producer corrects and
re-presents — a **new attempt**, under the **same logical
item identity**, carrying a **new content fingerprint**,
linked to the predecessor presentation by an explicit
supersession/derivation record (Part II structures (d)
and (e)) naming the predecessor's content fingerprint.
Consumers resolve "current" through the supersession
link; the predecessor remains readable as history and is
never presentable as current.

## 5. Catalogue and citation provisions (corrected)

The catalogue provisions are REV9 §5, carried, with the
four corrections below. Index rows are DC records per
Annex B §B2.1 as adopted; the citation form
`<YYYY-MM-DD>/<type-token>/<slug>` stands; existing
citations remain aliases, never rewritten.

### 5.1 Run identity (G1-R9-03)

A run's identity is its **K1 run identity**: minted by
the BINDER at the moment a freeze attempt begins, binding
**by reference** one configuration identity (K3), one
verified subject identity (K2), and one frozen tree-set
identity (v3 §K1). The run's DC Identifier is the
fingerprint of that run identity — the freeze-begin
record that constitutes the binding — **never the
configuration digest**. The configuration digest appears
in the run's record as a typed Relation (References the
configuration, K3), one referenced input among the three
the binding names. Annex B §B4.2's contrary assignment
("the run identity's fingerprint anchor (the frozen
configuration digest it binds)") is superseded by this
section for run-02. A refused freeze is recorded under
the same run identity as a governance record; a run that
never started still has its own identity, distinct from
every configuration it attempted to freeze.

### 5.2 C1's item-level identity (G1-R9-04)

C1's content, authority statement, and delivery terms
are exactly as frozen in REV5 §3 and carried in REV9:
the audience ruling, authored by Remmy under Ben's
delegated selection authority (exhibits B3/B4), delivered
in Holder 2's tenure, non-delivery INVALID. None of that
changes. What REV10 adds is the identity REV9 lacked.

Under Part II, C1 is one information item with one
canonical identity, stable across its life. Because C1
as frozen has no bytes of its own, its item identity is
constituted deterministically from the frozen record —
**this construction is this draft's proposal, stated for
the examiner's examination**: the item identity is the
SHA-256 of the following canonical string (UTF-8, LF
line endings, final LF included):

```
DUENNA-ITEM-IDENTITY-v1
item: C1
container-sha256: 05e8d9a7cd824891ddb79df0abf5fdcc6a0e21ba5d1e9b8e1910b57e5bca6d47
locator: RELAY01-PACKAGE-REV5.md, section 3
assertion: The brief is written for a plain reader picking it up cold: precision kept, jargon defined or dropped. The re-derivation instructions remain technical.
```

Computed at this drafting, that identity is:

**29c57e37d8c49fc23d10d91b3d8a94d5857ac1a6de3cd2dd29617159fb04342d**

Any reader with REV5 can recompute it: the inputs are
the container's filed SHA-256, the §3 locator, and the
assertion text exactly as frozen (whitespace normalised
to single spaces, as Annex B §B5.3 quotes it). C1's index
row carries this value as its one authoritative
Identifier. Its **source reference** (Part II structure
(a)) retains the container in full: REV5's SHA-256
`05e8d9a7cd824891ddb79df0abf5fdcc6a0e21ba5d1e9b8e1910b57e5bca6d47`,
Git blob `dc9aa183ce0c8974226ba3785d0ff46ba1924717`,
shelf path `duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV5.md`,
locator §3 — the container digest appears **only** there
and in the IsPartOf relation, labelled as the container's,
never as C1's Identifier (Annex B §B5.3's discipline,
preserved).

The sealed delivery artefact, when created at delivery in
Holder 2's tenure, is a **derived representation of the
same item** (Part II structure (d)): it carries its own
content fingerprint, hashed into the event ledger at
delivery as REV5 prescribes, and a derivation record
linking it to C1's item identity above. Its digest
identifies the delivery representation; it does not
become, retroactively or otherwise, the item's identity.

### 5.3 Type tokens — the usage rule (G1-R9-06)

The closed list is Annex B §B2.3's seventeen tokens,
**membership unchanged**: document, package, verdict,
freeze, run, event, envelope, chunk, record,
gate-definition, correction, obligation, question, fact,
criterion, defect, archive. The correction is in usage,
adopting the rule the verdict proposed, stated explicitly
so no example silently extends the vocabulary:

- A **collection or register of a kind** is catalogued
  with the token **record** (with its DCMI value, Dataset
  or Collection as the row's form requires) — the event
  ledger is a `record`; the defect register is a
  `record`.
- **event** is used only for an individually indexed
  event; **defect** only for an individual DR entry.
- Every other worked record already uses a listed token;
  checked at this drafting against Annex B §B4–§B5 and
  the Adoption Spec's rows: the two out-of-list usages
  were Annex B §B4.2's `event-ledger` and §B4.3's
  `defect-register` (and the Adoption Spec §2.3's
  unpinned "defect register's own row", which this rule
  now pins to `record`). Those filed texts stand; this
  rule governs run-02 records and any future revision of
  the annex.

### 5.4 Format values name their scheme (G1-R9-08)

**Draft's choice between the verdict's two offered
corrections, marked as such:** every Format value in a
run-02 record is stated with its scheme — an IMT media
type under the scheme label **IMT**, or a value under
the explicitly named local scheme **Duenna Local Format
Scheme**. The local scheme's one current value is
`application/jsonl`, used only for the event ledger's
line-delimited form. A local-scheme value is never
recorded bare, and never in a position where it could be
read as an IMT value. All other Format values in the
package's records are IMT values, as Annex B and REV9
§5 already state.

## 6. Design commitments (carried from REV9 §6)

Vane's four collaboration points stand as commitments of
this package, unaltered: description is not authority,
state, or validation, and gaps are extended explicitly,
never disguised; the fingerprint is authoritative and the
citation a readable representation only; classification
is not verification, description is not evidence,
provenance is not authority; and the examiner's
semantic-loss examination of the worked artefacts is
welcomed on the record. §1's semantic-loss paragraph
records what this revision did with her REV9 round of
that examination.

## 7. Open items — clarified, carried, and Ben's

### 7.1 The Adoption Spec's authority, stated precisely (G1-R9-07)

- **Adopted:** Annex B (Dublin Core) as the package's
  catalogue basis — Ben's ruling of 2026-11-20 20:43 MST,
  confirmed by the examiner in the REV9 verdict. Annex A
  retained as the studied alternative.
- **Not adopted:** the Adoption Spec. Ben's confirmation
  did not adopt it; it remains a **draft that enacts
  nothing**, and this revision does not treat it as
  adopted. Where REV9 or this revision relied on its
  analysis, the reliance is restated here on the
  package's own authority, subject to Gate 1.
- **Operative for run-02** (as package provisions, each
  at its stated standing): the DC record core and
  citation discipline (adopted, via Annex B); the
  type-token list and the §5.3 usage rule (package
  provisions, §5.3); the §5.4 format-scheme labelling
  (package provision); the state and grade words the
  package's records actually use — REPORTED / VERIFIED /
  HARDENED (Part II grades, v3), OPEN / CLEARED /
  CORRECTED (review dispositions), SETTLED, UNRESOLVED,
  CONTESTED, UNKNOWN — carried as **Duenna programme
  vocabulary sourced from EXON's draft documents at draft
  status**: no EXON term is treated as admitted in EXON,
  and no Duenna term silently inherits EXON authority.
  **UNEXAMINED** is a Duenna programme coinage (design
  §3.3), not an EXON term; **ALLOW / CORRECT** are Ben's
  own ruled words for the Duenna check-in gate.
- **GATE, disambiguated for all package records:** in
  Duenna's records, "gate" unqualified means the Duenna
  check-in gate (in-flow; ALLOW / CORRECT). EXON's
  release gate is always written "EXON release gate"
  (ELIGIBLE / BLOCKED). The two are never interchanged.
- **Non-operative proposals:** the Adoption Spec's
  remaining analysis, and its **twelve NO TERM entries**
  (document, package, verdict, run, event, envelope,
  chunk, fact, question-as-kind, archive; attribution;
  issuance), stand as **open vocabulary questions for
  Ben**, exactly as the spec flagged them — none filled,
  none silently relied on. The plain programme words the
  token list uses carry no EXON authority by being used.
- **Future compatibility item, explicit:** EXON's
  message-schema "envelope" and Duenna's handover
  envelope are different referents under one word. The
  collision is preserved on the record as a compatibility
  item for the day EXON takes the system up (Adoption
  Spec F2); neither system renames anything by this
  revision.

### 7.2 Run-02 participant assignments (verdict condition)

REV9 carried the run-01 set as an unasserted default.
**That carriage is withdrawn.** This revision names no
participant set. Before run-02's case freeze, the
assignment set — every role, every model — must be
**named explicitly in the case and approved by Ben**;
the run-01 set has no default standing. Any material
participant or model change is expressly authorised and
reviewed; there is no silent substitution. Gemini's
run-01 503s remain evidence on the record, and P5's
classification (§2) governs any recurrence.

### 7.3 Carried conditions from the verdict

- **Fluency (Known Hole 3 — still UNTESTED).** Before
  run-02 relies on model-produced DC records, one of two
  routes must be satisfied and recorded at case freeze:
  either a cold multi-model conformance test is run and
  passed against a pass mark declared before the test, or
  record construction is made deterministic and
  mechanically validated so that fluency is not a trust
  assumption. This revision chooses neither route; the
  choice and its record are case-freeze items.
- **Cost (Known Hole 5 — still UNMEASURED).** Actual
  verification time and cost are recorded during run-02
  and reported against Ben's constraint (2026-11-20
  19:50 MST). No claim is made that the end-to-end cost
  has been proven.
- **Execution.** Ben's separate execution word for
  run-02 remains required after a Gate 1 PASS on this
  revision and the §2 prerequisites satisfied and
  recorded (freeze §11(6)). His 21:03 tap commissioned
  this draft; it is not an execution authorisation.

### 7.4 Remaining examiner items

The §5.2 item-identity construction (draft's proposal);
the §5.4 scheme choice (draft's choice between the
verdict's two offered corrections); design §6 Q8 (whether
the Gate Format Definition as exhibited discharges the
T02/T07/T09 response-format contracts for gate contexts)
and Q9 (the grade of run-01's mechanical cross-check
evidence) — noted, not settled here. Design §6 Q4 is
closed by the verdict (Part II accepted as a conceptual
model); Q5 is closed by G1-R9-02.

## 8. What this revision does not do

- It does not alter, reinterpret, or repair any run-01
  record, any prior revision, any prior verdict, or the
  filed REV9 submission records. Run-01's NO START
  stands; the participants' verdicts and the
  orchestrator's cross-check stand as evidence, exactly
  as recorded.
- It does not satisfy any start condition. No archive
  has been delivered for run-02, no computation or
  re-derivation has been performed under it, no catalogue
  has been queried for it, no participant set is named.
- It does not commence Gate 2, assess the subject, or
  assess Duenna.
- It does not shelve itself, submit itself, or speak
  for the examiner.

## Closing disposition

**Revision 10: DRAFT, submitted for Gate 1 examination
when Remmy files it.**
**Run-02: NOT OPENED. Clock: NOT STARTED.**
**Gate 1 on this revision: NOT YET EXAMINED.**
**Gate 2: NOT COMMENCED.**
**Subject result / Duenna performance: NOT ASSESSED.**

On a Gate 1 PASS, run-02 proceeds under §2–§5 as
written: from a copy, against the frozen originals,
through gates that allow or correct, format computed by
the independent Checker under the exhibited definition,
every prerequisite satisfied and recorded before the
clock starts — and Ben's execution word still to come.
