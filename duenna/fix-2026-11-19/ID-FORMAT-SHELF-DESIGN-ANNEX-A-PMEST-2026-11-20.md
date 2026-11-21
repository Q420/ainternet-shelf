# ANNEX A — A BORROWED CATALOGUING SYNTAX: PMEST

*2026-11-20. Companion to `ID-FORMAT-SHELF-DESIGN-2026-11-20.md`.
Paper only. Authority: Ben's tap of 2026-11-20 20:04 MST (the
design stage), his suggestion of 20:08 MST (borrow an established
cataloguing format, one with types and categories), and his
ruling of 20:13 MST (the syntax is established on the Duenna
shelf first; EXON adopts it later, at his call; EXON develops
independently meanwhile). This annex serves the shelf design
only. It proposes; it does not enact, file, or submit anything.*

---

## A1. What is borrowed — and what is not

The borrowing is from S. R. Ranganathan's **Colon
Classification**, and it is a borrowing of **syntax only**:

- the five fundamental categories — **Personality, Matter,
  Energy, Space, Time (PMEST)**;
- **facet analysis**: the discipline of analysing a thing into
  those categories rather than assigning it a place in a
  pre-enumerated list;
- **facet formulas**: a fixed citation order (P, then M, then E,
  then S, then T) by which the analysed facets are assembled;
- **facet indicator punctuation**: in the CC6-and-later
  assignments, Personality is introduced by a comma, Matter by a
  semicolon, Energy by a colon, Space by a full stop, and Time
  by an apostrophe.

**Ranganathan's subject schedules are NOT borrowed.** None of
his class numbers for subjects, none of his schedule content,
and no claim that this programme's artefacts are library
subjects. What transfers is the grammatical insight: a small,
closed set of categories, a fixed order, and a punctuation that
shows which segment is doing which job — so that a catalogue
face is *synthesised* from facets rather than invented per
artefact. That is exactly the property the design paper's §6
question 3 was missing: a principled form for the catalogue
identity of non-letter artefacts.

Two hard constraints govern everything below, and the annex is
written to be examined against them:

1. **The two-layer principle** (Ben, adopted 2026-11-11; design
   paper §1.2). The fingerprint is the identity authority. Any
   PMEST string is the readable, indexable **face** of an
   identity — a representation and retrieval aid, never a
   competing authority.
2. **Vane's examination point** (2026-11-20 20:07 MST,
   pb-mwptulk5-4-hl1e): the machine-verifiable identity and its
   human-readable face must remain consistently related; a
   readable filename must not become an alternative identity
   authority; and a fingerprint must not be treated as proof
   that the content it identifies is valid.

A third rule follows from the design paper's own §2.4 and is
applied throughout: **no state in the face.** Outcomes and
conditions — PASS, FAILED, OPEN, DELIVERED, NOT SATISFIED, a
grade — are state, provenance, or validation claims. They live
in the index, the ledger, and the verdict records. A PMEST face
classifies what a thing *is*; it never asserts what has been
*established about it* (v3, P8).

---

## A2. The programme rendering — a stated adaptation

Colon Classification's own notation is schedule codes joined by
indicator punctuation. This programme's faces must also be
recognisable to humans and LLMs (Ben's 2026-11-10 doctrine,
design paper §1.6), so the annex adopts the following rendering
as a **programme normalisation — a proposal, not a historical
claim about Ranganathan's practice**:

- The analysis form is written
  `[P] … · [M] … · [E] … · [S] … · [T] …`, in fixed PMEST order.
- The readable face renders each present facet as its indicator
  followed by its facet name and value:

  `, PERSONALITY <value> ; MATTER <value> : ENERGY <value> . SPACE <value> ' TIME <value>`

- A facet with no honest value is **omitted, indicator and
  all**. An omitted facet is a finding about the artefact type,
  recorded in §A4 — never a gap to be papered over with a
  placeholder.
- The index stores the five facet values as **separate
  fields**; the face is a rendering of those fields. The face
  is **not a serialisation**: facet values (paths especially)
  can contain dots, slashes, and other punctuation, so the face
  must never be parsed to recover identity. Resolution runs
  through the index row to the fingerprint, exactly as the
  design paper's §2.4 prescribes.
- Facet values in §A4 are descriptive, to test whether the
  mapping holds. A **controlled vocabulary** for Matter values,
  Energy values, and Personality role-qualifiers does not yet
  exist; pinning one is work for the package revision, and is
  listed as open in §A7. Nothing in this annex should be read
  as that vocabulary already established.

Facet semantics, as applied to this programme:

- **Personality** — what the thing is: its v3 kind (§A4 gives
  the kind for each artefact type), plus a role-qualifier where
  the kind alone is too coarse (e.g. *information item,
  role = correction*). A qualifier is not a new kind and mints
  no namespace (v3, P7).
- **Matter** — the thing's material form: its medium and format
  as filed or recorded (a Markdown filing, a JSON record set, a
  ZIP archive with an internal manifest, a clause inside a
  package). For abstract items, Matter names the *canonical
  representation*, and §A6 says plainly where that stretches
  the category.
- **Energy** — the process relation by which the thing is
  produced, used, or examined (a Gate 1 examination, a provider
  invocation, a handover). Energy names a process *class or a
  recorded process*, never an outcome: "Gate 1 examination" is
  Energy; "PASS" is not.
- **Space** — where the thing resolves: its shelf path, its
  local run-tree path, or — for items with no file of their
  own — its **resolution locus** (an index row, a package
  section, a ledger). This is broader than Ranganathan's
  geographic Space and is flagged as a programme extension in
  §A6.
- **Time** — the thing's temporal coordinate: a UTC date or
  timestamp (design paper §1.5), or, in a dated series, its
  revision position attached to that date (REV8 of
  2026-11-20). Pure sequence — a ledger seq, a step number, a
  line range — is **not** Time, and §A4 refuses to file it
  there.

---

## A3. How a face resolves — the two-layer discipline

Every worked example in §A5 follows the same resolution path,
stated once here:

1. The face is read by a human or an LLM and recognised —
   that is all it is for.
2. The face (or the artefact's existing tag, per design paper
   §2.2) is looked up in the **index** (shelf index or run
   index, §2.4 of the paper).
3. The index row gives the **locator** (path / section /
   ledger position) and the **fingerprint** (SHA-256 or Git
   blob, as the shelf already records).
4. The fingerprint is checked against the artefact as found.
   A match establishes *content identity only*. Provenance
   (who issued it, under what authority), state (what has
   happened to it), and validation (what has been independently
   established about it) are separate claims, established by
   their own records — filing commits, ledger entries, verdict
   issuances — never by the fingerprint and never by the face
   (v3, P8; Vane's point, §A1).

Where two distinct occurrences share every facet (two identical
chunks, two attempts at the same call), the faces will be
similar or identical. That is expected and harmless **because
the face is not the identity**: the index rows are distinct,
carrying the occurrence discriminators (attempt, response ID,
ledger seq, component digests) that the face does not. Similar
is not the same, and this design never asks a face to carry the
difference alone.

---

## A4. The mapping — §2's artefact table, faceted

The design paper's §2.2 table, artefact type by artefact type.
"—" means the facet is honestly unused for that type.

### A4.1 Documents, configurations, verdicts

| Artefact (v3 kind) | Personality | Matter | Energy | Space | Time |
|---|---|---|---|---|---|
| Design / governance document (Part II information item) | Information item — design/governance document | Markdown document as filed | Drafting, examination, filing (the lifecycle processes material to its provenance) | Shelf path; local `duenna-fix/` path before filing | Design/filing date (UTC); draft version where a series exists (v1/v2/v3) |
| Relay package & revision (K3 configuration) | Configuration — Relay 01 execution package | Markdown package file; its bound exhibits and preflights are separate indexed artefacts, not part of this face | Gate 1 submission, examination, revision | Shelf path under `relay01/` | Package date; revision position (REVn) |
| Gate 1 verdict (K7 verdict issuance) | Verdict issuance — Gate 1 verdict | Markdown filing | Gate 1 examination of the named package revision | Shelf path under `relay01/` | Filing date; the examined revision's position |
| Design freeze (K3 configuration) | Configuration — design freeze | Markdown frozen design | The freeze act; governing run setup | Shelf path under `relay01/` | Freeze date |
| Stage 9 execution package (K5 artefact / K3 configuration) | Execution package, version v1 or v2 (qualifier, not a kind) | ZIP archive + internal `MANIFEST.sha256` + `README-EXECUTION.md` | Stage 9 execution; independent-execution examination | Local custody, resolved via the shelf locus `exhibits-zip-identity/v1\|v2/` (the zip itself is not shelved — text-only push route) | Package date; version position in the v1/v2 series |

### A4.2 Run artefacts

| Artefact (v3 kind) | Personality | Matter | Energy | Space | Time |
|---|---|---|---|---|---|
| Run (K1 run identity) | Run — Relay 01 run-NN | The governed record set: frozen configuration + tree set + append-only event ledger and run artefacts | Freeze attempt; relay execution; closure | Local run tree (`relay01/run-NN/`); from run-02, the shelf `runs/run-NN/` locus of §4.2 of the paper | Freeze-attempt date; run ordinal as series position |
| Event (K9 event identity) | Event | JSONL ledger entry | The named transition the event records (e.g. GATE1_REV8_PASS) — see the P/E overlap note in §A6 | The run's event ledger, at its seq locator | UTC timestamp of the event. The seq is an ordering locator in Space, **not** Time |
| Envelope (K5 artefact) | Artefact — handover envelope, qualified by step and recipient role (O/H1/H2/H3/X/C/F) | The envelope file or ordered file set as built | Handover: delivery, recipient understanding, findings, acceptance | Run `envelopes/` path, with step/recipient as locators | Run date where recorded; otherwise — . Step position is Energy/locator, **not** Time |
| Manifest chunk (K5 artefact, derived slice) | Derived artefact — manifest chunk of a named parent archive | Plain-text manifest slice: header + the stated number of manifest lines in the §3 grammar of the paper | The verification process that examines it (in run-01: Gate A archive verification) | Envelope path **plus the parent-manifest line range** as a micro-locator (programme extension, §A6) | — in the usual case. The line range is a location, **not** a time |
| Call record (K9 event-adjacent record) | Record — provider call record | JSON record plus its linked body / response / stderr files (a set; the index enumerates the component digests) | The provider invocation and the attempt it records (attempt ordinal belongs here) | Run `calls/` path, under its label | `started_at_utc` timestamp from the record |
| Gate (part of the case, K3 configuration) | Configuration component — the named gate (Gate A, Gate B, Joint 1–3) | The pinned Gate Format Definition + the gate's verdict-record shape | Format computation; content judgement; ALLOW-or-CORRECT decision | The case/package clause that establishes it; the ledger locus where its record appends | — . A gate's position in the flow is established in the case, not carried as a date |

### A4.3 Information items and contract items

| Artefact (v3 kind) | Personality | Matter | Energy | Space | Time |
|---|---|---|---|---|---|
| Correction C1 (Part II information item; K6-family commitment per the paper) | Information item, role = correction — the audience ruling | As frozen: the canonical clause in RELAY01-PACKAGE-REV5 §3. At delivery: a sealed instruction artefact, a new representation of the same item | Supersession of the commission's default register; delivery into Holder 2's tenure; conformity of later work | Now: the REV5 §3 locus. At delivery: the event-ledger entry and the sealed artefact's path | REV5 package date (2026-11-20). The delivery timestamp, when it exists, is an event — not the frozen item's Time |
| Obligation Ob1 (Part II information item) | Information item, role = obligation — the outside-eyes bundle owed to Claude | The commitment record in the package / run index (not the eventual deliverable, which is a different artefact) | The fulfilment process: production, delivery, acceptance | Run index row + event-ledger locus; owner carried as an index attribute | Date the obligation arose (the freeze). Its due condition is an attribute; its state (NOT DELIVERED) is **not** in the face |
| Open question Q1 (Part II information item) | Information item, role = open question — the delivery-form question | The canonical question record in the package / run index | Deliberation; a ruling, if one comes, is a supersession event | Package / run-index locus + ledger locus | Freeze date. OPEN is state, **not** identity and not Time |
| Initial-ledger fact G1–G10 (Part II canonical claim record) | Claim record — fact Gn | The numbered statement as frozen (REV5 §4) + its cited source's representation | Checker re-derivation and judgement before the clock | Run-index row + the cited source's dual locators | Initial-ledger freeze position (package revision + date) |
| Reconstruction / safe-continuation item R1–R14, SC1–SC5 (K12 contract items) | Contract item — reconstruction denominator item / safe-continuation criterion | The frozen textual criterion in the freeze / frozen schema object | Finisher reconstruction; examiner scoring and safe-continuation judgement | The freeze and the frozen schema object (K5/K12) that contain it | Freeze date / revision position |
| Defect (K10 attribution subject) | Defect register entry, DR-nn (the number is a Personality qualifier) | Markdown register row + its linked evidence set | Investigation, repair, disposition — as process classes; the attribution class and disposition themselves are separate K10/state records | `DEFECT-REGISTER.md`, at its row | Registration date where the register records one; otherwise — . The DR ordinal is **not** Time |

**Reading note.** Three refusals in this table are deliberate
and load-bearing: ledger seq, step position, and line range are
never filed under Time; outcomes are never filed anywhere in a
face; and a role-qualifier (correction, obligation, question,
version) never promotes itself into a new identity kind. Each
refusal is the two-layer principle and v3's P7/P8 doing their
work inside the borrowed syntax.

---

## A5. Worked examples

### A5.1 Vane's REV8 Gate 1 verdict

**The artefact.** `VANE-GATE1-VERDICT-REV8-2026-11-20.md`,
filed on the shelf at
`duenna/fix-2026-11-19/relay01/VANE-GATE1-VERDICT-REV8-2026-11-20.md`;
canonical blob `347de01eb875bd39040e078132664346763f2eb1`,
filing commit `512be9b904d097f22f41cb6fd0fe959b373f2670`;
recorded in run-01's event ledger at seq 5.

**Facet analysis.**

- **Personality** — K7 verdict issuance: a Gate 1 verdict. The
  package it examines (REV8) is a *relation* recorded in the
  index, not part of this artefact's Personality.
- **Matter** — a Markdown filing: one document, as filed.
- **Energy** — Gate 1 examination. The examination's *outcome*
  (PASS) is deliberately absent: it is a validation/state fact,
  recorded at ledger seq 5 and in the index row, not a facet.
- **Space** — the shelf path above.
- **Time** — 2026-11-20, with REV8 as the examined series
  position.

**Readable face.**

```
, PERSONALITY K7 Gate 1 verdict ; MATTER Markdown filing : ENERGY Gate 1 examination . SPACE duenna/fix-2026-11-19/relay01/VANE-GATE1-VERDICT-REV8-2026-11-20.md ' TIME 2026-11-20 · REV8 examined
```

**Resolution, and how the constraints hold.** The shelf index
row for this face gives the path and the fingerprint — blob
`347de01e…`. A reader who finds a file at that path checks the
blob: a match establishes that *these are the filed bytes*.
It does **not** establish that the verdict's content is
correct, nor even, by itself, that Vane issued it: provenance
rests on the filing commit and the ledger's seq 5 record, and
K7 binds a verdict to its issuing instance, not to its bytes
alone. Conversely, a same-titled copy with a different blob —
the REV5 corrigendum's lesson, in which a bridge-message copy
(a439e2ee…) was nearly filed as the verdict (fdebe61c…) — is
exposed by the fingerprint, however convincing its face. Face
recognises; index resolves; fingerprint identifies; commit and
ledger provenance; the PASS stands in the routing record. No
layer does another layer's job.

### A5.2 A run-01 archive-verification chunk record

**The artefacts — two, and the distinction is the example.**
The chunk under examination is the envelope
`relay01/run-01/envelopes/chunks50/o-v1-r3-c11.txt`: ARCHIVE v1,
CHUNK 11 OF 12, MANIFEST LINES 601 TO 650 OF 686 — a header and
50 manifest lines, SHA-256
`bb445056f6be535b65ae55fc53fa17d7109d6679f3d9d54a13b281b6af3dfc45`.
The record examined here is the call record
`relay01/run-01/calls/av-o-v1-r4-c11-r3.record.json`, the REV8
caller's record of the NVIDIA/Kimi attempt on that chunk. The
chunk and the record of an attempt on it are different
artefacts with different identities; run-01's confusion was
never helped by labels that blurred exactly this.

**Facet analysis — the call record.**

- **Personality** — K9 event-adjacent record: a provider call
  record, label `av-o-v1-r4-c11-r3` (a historical local label,
  per §2.3 of the paper — the index maps it; nothing here
  re-mints it).
- **Matter** — a JSON record set: the record itself, its body
  file, its response file, its stderr file, each digest-bound
  inside the record.
- **Energy** — a provider invocation: NVIDIA,
  moonshotai/kimi-k3.1-pro, an archive-verification attempt on
  chunk 11 (the label's r3 attempt segment is mapped by the
  index, not parsed from the label as authority).
- **Space** — `relay01/run-01/calls/av-o-v1-r4-c11-r3.record.json`.
- **Time** — the record's `started_at_utc`,
  2026-11-21T02:06:39Z.

**Readable face.**

```
, PERSONALITY K9 call record — av-o-v1-r4-c11-r3 ; MATTER JSON record with linked body, response and stderr files : ENERGY NVIDIA/Kimi archive-verification attempt . SPACE relay01/run-01/calls/av-o-v1-r4-c11-r3.record.json ' TIME 2026-11-21T02:06:39Z
```

**Resolution, and how the constraints hold.** The run index
row for this record carries the record file's own SHA-256,
`f3cbd812fb8c5cf9e239b3d46911c66179aa29e23bad7605c26cf6b85af3b6d4`.
Inside, the record binds its components by digest — body
`b8c54b37…`, response `d451ff86…`, stderr (empty)
`e3b0c442…` — and its machinery by digest: caller
`54117c63…` (the REV8 caller), helper `56ca6a4d…`, dependency
`8b1f42e8…`; the provider's response ID is
`chatcmpl-c3e3baf4-2f3e-4cb6-a788-940a4ea758df`. The body, in
turn, carries the chunk's text, and the index links the record
to the chunk's own row and fingerprint (`bb445056…`) by an
*examines* relation. Two index rows, two fingerprints, one
relation — the face of neither artefact borrows the other's
identity.

The response's content — FORMAT_OK: NO / VERDICT: FAILED — is
a validation claim preserved inside the response file. It
appears in **no** facet of either face, and the response's
fingerprint proves only that these response bytes are the
preserved ones — not that the judgement in them was right
(the orchestrator's mechanical cross-check of this envelope
found zero format violations; that disagreement lives where
the design puts it, in the discrepancy layer, with both
positions intact). This is Vane's point operating on the
programme's most sensitive record: identity, all the way down,
never once standing in for validity.

### A5.3 C1, the correction, as frozen in REV5

**The artefact.** C1, the audience ruling — *the brief is
written for a plain reader picking it up cold: precision kept,
jargon defined or dropped; the re-derivation instructions
remain technical* — frozen at §3 of
`RELAY01-PACKAGE-REV5.md` (shelf:
`duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV5.md`; the
package's Git blob `dc9aa183ce0c8974226ba3785d0ff46ba1924717`,
SHA-256 `05e8d9a7cd824891ddb79df0abf5fdcc6a0e21ba5d1e9b8e1910b57e5bca6d47`).

**Facet analysis.**

- **Personality** — a Part II information item, role =
  correction. Not a new kind: v3 consolidated information
  identity into one item identity with mandatory structures,
  and C1 sits inside that consolidation.
- **Matter** — as frozen, a canonical clause inside a Markdown
  package (§3 of REV5). The sealed instruction artefact C1
  becomes at delivery is a *later representation of the same
  item*, not the item itself and not a new identity.
- **Energy** — supersession of the commission's default
  technical register; delivery into Holder 2's tenure;
  conformity of Holders 2 and 3 and the finisher's source
  material. (Delivery and conformity are *prescribed* process
  relations here — the run has not started; the face classifies
  the item's process relations, it does not assert they have
  occurred. Occurrence will be ledger fact.)
- **Space** — the REV5 §3 locus. C1's authority sources
  (exhibits B3/B4 of the package's exhibits file) are
  *provenance* locators and are carried in the claim record,
  not in Space.
- **Time** — 2026-11-20, the REV5 package date. (REV8 later
  incorporated REV5 by reference; C1's frozen home remains
  REV5 §3.)

**Readable face.**

```
, PERSONALITY information item — correction C1, the audience ruling ; MATTER canonical clause in Relay 01 Package REV5 §3 : ENERGY supersession of the default register; delivery into Holder 2's tenure . SPACE duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV5.md §3 ' TIME 2026-11-20
```

**Resolution — and an honest limit.** The index row for C1
resolves to a **container fingerprint plus a locator**: the
REV5 package's blob/SHA-256, at §3. That establishes the
package's bytes and locates the clause exactly. It does **not**
give C1 a fingerprint of its own, because as frozen, C1 has no
separate bytes to fingerprint — and this annex will not pretend
the package's digest is the item's digest; that substitution is
precisely the move the two-layer principle forbids. What C1
has, under v3 Part II, is a source reference (the package, at
its digest, with dual locators: shelf path + §3) and a canonical
claim record. A C1-specific fingerprint comes into existence
only when the sealed delivery artefact is created and hashed
into the event ledger at delivery — at which point the index
adds that artefact as a delivery representation of the same
item, linked by derivation, while C1's identity remains the
one minted at the freeze. The PMEST face classifies C1
cleanly; the *resolution* of an intra-package item is where
the borrowing runs out and the programme's own Part II
machinery has to do the work. §A6 records this as the mapping's
principal strain.

Authority, for completeness, sits where it should: Ben
authorised the selection among candidate corrections (exhibit
B3); Remmy selected and authored the ruling under that
delegation (exhibit B4 corroborates). None of that is in the
face, and none of it is established by any fingerprint — it is
provenance, carried by the claim record and the exhibits,
exactly as the package itself states it.

---

## A6. Where the mapping strains — stated plainly

The mapping is clean for filed documents, packages, verdicts,
and call records. It strains in five named places. None of
these is smoothed over; each is either a stated refusal (which
keeps the mapping honest) or a **proposal for the examiner**,
not an established fact.

1. **Space is stretched.** Ranganathan's Space is geographic.
   This programme needs Space to mean *resolution locus* —
   shelf path, local run path, package section, ledger
   position, and (for a manifest chunk) a line range *inside*
   a parent artefact. The two-scale use (a chunk is located
   both on the shelf and within its parent) has no counterpart
   in the borrowed syntax. **Proposal:** the package revision
   adopts "Space = resolution locus, at shelf scale and, for
   derived slices, at parent scale" as a programme extension,
   for Vane's examination — or rejects it, in which case
   derived slices need a locator mechanism outside PMEST.
2. **Time vs. ordinal.** Revision position (REV8, run-02, v2)
   is a series coordinate, not a moment. §A4 admits it under
   Time only when attached to a date in a dated series, and
   refuses it for ledger seq, step numbers, and DR numbers.
   Even the admitted use is a normalisation, not Ranganathan's
   category. If the examiner finds it impure, the fallback is
   honest: Time carries dates only, and series position moves
   to the Personality qualifier (where §A4 already puts v1/v2
   and DR-nn).
3. **Process-bearing artefacts blur P and E.** A run, an
   event, a gate, and a call record are all *records of
   processes*; their Personality (what the record is) and
   Energy (the process it records) sit close together, and a
   careless formula collapses into tautology ("event —
   eventing"). The mapping's discipline — Personality names
   the *record kind*, Energy names the *process relation*,
   and Energy is omitted where no distinct process relation
   exists — holds in the table, but it is a discipline, not a
   guarantee the syntax itself provides.
4. **Abstract items have no material.** A fact, an obligation,
   and a question are not made of anything. §A4 files their
   canonical *representation* under Matter (a numbered
   statement, a commitment record, a question record). That is
   defensible — Matter as "the form in which the item is
   carried" — but it is the programme speaking, not
   Ranganathan, and a stricter reading would leave Matter
   empty for all three. The table chose the representation
   reading because an empty Matter on every information item
   would make the facet useless exactly where Ben directed the
   information family be given the same treatment as authority.
5. **Container items have no fingerprint of their own.** C1
   (§A5.3) is the worked case: frozen inside a package, it
   resolves by container digest + locator, and any claim of an
   item-level fingerprint before its delivery artefact exists
   would be fabrication. The same applies, in lesser degree,
   to G1–G10 and R/SC items. PMEST classifies them; Part II's
   source-reference machinery resolves them; the face alone
   does not. A design that hid this would fail Vane's
   examination point on its most important items.

A further limit, not a strain: **facet values are not yet a
controlled vocabulary.** §A4's Matter and Energy values are
descriptive prose. Two cataloguers writing faces independently
could describe the same format differently ("Markdown filing"
vs. "Markdown document"), producing different faces for one
identity. Because the face is not the authority, that costs
retrieval neatness, not identity — but a catalogue whose faces
drift is a catalogue failing Ben's recognisability doctrine in
slow motion. The vocabulary must be pinned in the package
revision, with the index storing facet values as fields drawn
from it.

---

## A7. What this settles for §6 Q3 — and what it leaves open

Design paper §6 Q3 asked: whether the exploratory Index-ID form
(IDX-YYYYMMDD-nnnn) is adopted as the index identity for
programme artefacts, or the dated-slug citation plus the index
table suffices for non-letter artefacts. *Owner: Ben.*

**What this annex settles — the direction of the form.** The
catalogue face for non-letter artefacts does not need an
invented slug grammar, and it does not need to wait on the
Index-ID question. It can be a **PMEST rendering**: five
facets, fixed order, indicator punctuation, synthesised from
the artefact's v3 kind, its material form, its process
relation, its resolution locus, and its date — recognisable to
humans and LLMs because the grammar is a century old and
widely known, and safe because the fingerprint underneath
remains the sole identity authority. Q3's either/or dissolves:
the dated-slug convention (ruled for letters) and the PMEST
face (proposed here for programme artefacts) are the same
layer doing the same job — a readable, dated, indexable
representation — over one index and one fingerprint rule.

**What it does not settle.**

- Whether Ben **adopts** the PMEST face as the programme's
  catalogue form. That is his ruling to make on this annex;
  the annex is a proposal.
- Whether the **Index-ID form** is adopted, retained for
  letter registration only, or dropped. The PMEST face makes
  it unnecessary for artefact cataloguing; SS4 item 6 and the
  letter-registration context in which the Index-ID arose
  (design paper §1.4, §6 Q1–Q2) are untouched by this annex.
- The **Space and Time extensions** of §A6 (1) and (2) —
  proposals for the examiner, not rulings.
- The **controlled facet vocabulary** (§A6) — to be pinned in
  the package revision.
- **Coverage**: which artefact types *must* carry a PMEST face
  in the index from adoption forward, and whether faces are
  written for the historical record (REV1–8, run-01) as index
  rows only — the design paper's §2.5 already answers the
  history half: indexed, never rewritten. The faces, if
  adopted, are index data about those artefacts, not edits
  to them.

---

## A8. Route

Unchanged from the design paper's §5.2, with this annex riding
as part of the same paper:

1. **Ben reviews the paper and this annex.** His approval —
   including his ruling on the PMEST borrowing and on §A7's
   open adoption question — is the gate for everything after.
2. **Remmy incorporates the approved design** (paper + annex)
   into a new Relay 01 package revision: the Gate Format
   Definition, the index forms, the facet vocabulary, and the
   §A6 extensions stated as package positions for examination.
3. **The revision goes to Vane for Gate 1 examination.** Her
   stated focus (2026-11-20 20:07 MST) — identity unambiguous
   across shelf, gates, and run records; face and fingerprint
   consistently related; no readable name as identity
   authority; no fingerprint as proof of validity — is the
   examination this annex was written to face.
4. **No execution before a fresh Gate 1 PASS** and satisfaction
   of the applicable start conditions. Run-01's NO START, its
   archive discrepancies, and its Gemini failures remain
   preserved evidence, exactly as they stand.

EXON's place in this is Ben's ruling of 20:13 MST and nothing
more: the syntax is established on the shelf first; EXON may
adopt it later, at his call, in EXON's own time. This annex
designs nothing for EXON.

---

## Disposition

Annex A to the design paper of 2026-11-20, drafted the same
evening under Ben's direction, suggestion, and ruling as cited
above. It proposes a borrowed syntax and tests it against the
programme's actual artefacts, including where it fails. It
enacts nothing. Next step: Ben's review, with the paper.
