# ANNEX B — A BORROWED DESCRIPTIVE FORMAT: DUBLIN CORE

*2026-11-20. Companion to `ID-FORMAT-SHELF-DESIGN-2026-11-20.md`,
and sibling to Annex A (PMEST), which stands untouched as a
preserved draft. Paper only. Authority: Ben's tap of 2026-11-20
20:04 MST (the design stage); his steer of 20:19 MST — pick a
"more less flamboyant one" — away from Colon Classification;
Dublin Core proposed by Remmy as the plain candidate and carried
forward by Ben's follow-on design input; and his ruling of
20:20 MST opening the citation FORM: "The dated slugs can be
something else that's more coherent." That ruling opens the
form only. The Nov 13 ruling's function stands untouched —
citations are indexable, recognisable, and made for the shelf
(design paper §1.6, resting on the 2026-11-10 doctrine). This
annex serves the shelf design only. It proposes; it does not
enact, file, or submit anything.*

---

## B1. What is borrowed — and what is not

The borrowing is from the **Dublin Core Metadata Initiative**,
and it is a borrowing of a **descriptive record format**:

- the fifteen elements of the Dublin Core Metadata Element Set
  (DCMES, ISO 15836): Title, Creator, Subject, Description,
  Publisher, Contributor, Date, Type, Format, Identifier,
  Source, Language, Relation, Coverage, Rights;
- the **DCMI Type Vocabulary** — the closed list of resource
  types: Collection, Dataset, Event, Image, InteractiveResource,
  MovingImage, PhysicalObject, Service, Software, Sound,
  StillImage, Text;
- the standard **qualifiers**: the element refinements of the
  DCMI Metadata Terms (among them Created, Issued, Modified,
  IsPartOf, HasPart, IsVersionOf, HasVersion, Replaces,
  IsReplacedBy, References, IsReferencedBy, ConformsTo,
  Provenance, BibliographicCitation, Extent, Medium, Spatial,
  Temporal), and the encoding schemes that pin values to a
  syntax — **W3CDTF** for dates, the **IMT** list for media
  types, the DCMI Type Vocabulary itself for Type.

One difference from Annex A must be stated at the door, because
everything else in this annex follows from it. **Dublin Core is
a description standard, not a classification syntax.** Colon
Classification *synthesises an address* from facets; Dublin
Core *fills in a fixed record* about a resource. It has no
citation order, no facet grammar, and no ambition to locate a
thing inside a universe of things. What it offers instead is
that the record's fields, and several of their value
vocabularies, are already fixed by an external standard that
cataloguers, repositories, tools, and LLMs have been reading
for twenty-five years. Where Annex A borrowed a grammar and
had to propose a programme rendering of it, this annex borrows
a form and needs no rendering proposal at all.

**What is NOT borrowed, because Dublin Core does not contain
it:**

- **No identity authority.** DC's Identifier element holds an
  unambiguous reference to the resource, and DC practice permits
  several Identifier values under different schemes. DC itself
  never says which one is authoritative. The programme's rule —
  exactly one authoritative Identifier, the fingerprint — is a
  programme rule laid over DC, stated in §B2, not a DC feature.
- **No state, grade, attribution, or validation semantics.**
  DC has no element for any of them, and §B2 refuses the
  obvious smuggling route (Description prose).
- **No commitment or obligation semantics.** Nothing in DC
  expresses that something is *owed*. §B6 names the artefacts
  this leaves undescribed in their load-bearing respect.

Where Dublin Core already has a field, this annex invents
nothing. Where it has none, the gap is named as a gap, or as a
**proposed programme extension** labelled as such — never
dressed in DC's clothes.

Two hard constraints govern everything below, identical to
Annex A's:

1. **The two-layer principle** (Ben, adopted 2026-11-11; design
   paper §1.2). The fingerprint is the identity authority. Any
   readable form — a citation string, a title, a filename — is
   representation and retrieval aid, never a competing
   authority.
2. **Vane's examination point** (2026-11-20 20:07 MST,
   pb-mwptulk5-4-hl1e): the machine-verifiable identity and its
   human-readable face must remain consistently related; a
   readable name must not become an alternative identity
   authority; a fingerprint must not be treated as proof that
   the content it identifies is valid.

A third rule follows from the design paper's §2.4 and is
applied throughout, as in Annex A: **no state in the record.**
Outcomes and conditions — PASS, FAILED, OPEN, DELIVERED, NOT
SATISFIED, a Part II grade — are state, provenance, or
validation claims. They live in the ledger, the verdict
records, and the index's routing columns. A DC record describes
what a thing *is* and what it *relates to*; it never asserts
what has been *established about it* (v3, P8). Under DC this
rule needs one extra sentence, because DC always leaves a
free-text element open: **Description is not a loophole.** A
record that smuggles a grade, an attribution class, or a gate
outcome into Description prose has recreated, in prose, exactly
the claim-confusion P8 forbids — and has made it uncheckable
besides. Description carries a human summary of what the thing
is. Nothing else.

---

## B2. The programme rendering — record discipline

DC's own form needs no normalisation. What the programme must
add is discipline: which elements are mandatory, what values
they take, and how the citation form is built. All of it is
stated here as proposal for Ben's adoption ruling and Vane's
examination.

### B2.1 The mandatory core

Every programme artefact that carries an index row carries a
DC record with, at minimum:

- **Identifier** — exactly one authoritative value: the
  fingerprint (SHA-256 or Git blob, as the shelf already
  records), stated with its scheme. Further Identifier values
  (a provider response ID, a legacy PB-ID) are permitted only
  as additional, explicitly non-authoritative values. DC
  permits the repetition; the programme pins the cardinality
  of authority. Where they disagree, the fingerprint is right.
- **BibliographicCitation** — the readable citation form of
  §B2.2. DC provides this refinement for exactly this job: a
  bibliographic reference for the resource, distinct from its
  Identifier. The two-layer separation — fingerprint in
  Identifier, face in BibliographicCitation — is therefore
  available *inside the borrowed standard*, not constructed
  over it.
- **Type** — a DCMI Type value where one honestly fits, plus
  the programme type token of §B2.3.
- **Format** — an IMT media type (text/markdown,
  application/json, application/zip, text/plain), from the
  scheme, never free prose.
- **Date** — the artefact's governing date under the fitting
  refinement (Created, Issued), in W3CDTF, UTC (design paper
  §1.5). Sequence is never filed here: a ledger seq, a step
  number, and a line range are not dates, and DC — unlike a
  facet system — never tempts anyone to file them as one.
- **Relation** — the typed links of §B4, using the standard
  refinements (IsPartOf, HasPart, IsVersionOf, HasVersion,
  Replaces, IsReplacedBy, References, ConformsTo) wherever the
  relation is one DC names.

Elements beyond the core (Creator, Publisher, Contributor,
Source, Subject, Title, Description) are used where the
artefact honestly supplies them, per §B4. An element with no
honest value is **omitted**. An omitted element is a finding
about the artefact type, recorded in §B4 and §B6 — never a gap
to be filled with a plausible value.

### B2.2 The citation form — Ben's 20:20 opening, answered

Ben ruled the dated slugs' *form* open ("can be something else
that's more coherent") while their function stands. This annex
proposes a citation assembled from the DC record itself, in a
fixed order, from three segments:

```
<YYYY-MM-DD>/<type-token>/<slug>
```

- **Date** — the record's governing date (UTC), the segment
  the Nov 13 slugs already lead with; citations sort and scan
  by date exactly as Ben's doctrine requires.
- **Type-token** — the programme type token of §B2.3
  (verdict, package, freeze, record, chunk, correction, …).
  This is the segment the old slugs lacked: the dated slug
  told a reader *when* and *what it was called*, but not *what
  kind of thing it is*. The token makes the kind explicit and
  drawn from a closed list, instead of the letter codes of the
  unadopted PB-ID thesis (§1.3 of the paper) — plain words, no
  codes to memorise, recognisable to LLMs and humans alike.
- **Slug** — short distinguishing words from the artefact's
  title, lowercase, hyphenated: the shelf's existing slug habit
  (§1.6), retained. Where two distinct occurrences would
  otherwise collide (two attempts on the same day), the slug
  carries the discriminator by rule — run-01's existing labels
  slot in as slugs unchanged (`av-o-v1-r4-c11-r3`), so the
  historical labels are *absorbed* by the form rather than
  re-minted (compare §2.3 of the paper).

Examples, from the worked records of §B5:
`2026-11-20/verdict/gate1-rev8`;
`2026-11-20/package/relay01-rev5`;
`2026-11-21/record/av-o-v1-r4-c11-r3`;
`2026-11-20/correction/c1-audience-ruling`;
`2026-11-20/document/readme-execution-stage9-v1`.

The citation is stored in the record's BibliographicCitation
and in the index's citation column; it resolves through the
index row to the Identifier (fingerprint), exactly as the
paper's §2.4 prescribes. It is a face. It is never parsed to
recover identity, and it never competes with the fingerprint.

**Transition discipline.** Existing citations — the
pb-YYYYMMDD-… letter slugs, the dated filenames of REV1–8 and
the verdicts — are *historical citations*. They remain valid,
are entered in the index as aliases resolving to the same
fingerprint row, and are **never rewritten** in the documents
that contain them (P1 applied to citations themselves; the
paper's §2.5 nothing-rewritten rule, extended). New artefacts
mint new-form citations at issuance. Whether *letter* citations
also migrate form is **not** settled here: letters carry the
SS4 / registration context (paper §6 Q1–Q2) that neither annex
touches, and Ben's 20:20 remark was made over artefact
citations. Flagged open in §B8.

### B2.3 The programme type vocabulary — a named extension

DCMI Type's twelve values are too coarse for this programme's
load-bearing distinctions. A Gate 1 verdict, a package
revision, a design freeze, and a ledger fact are all, to DC,
Text — yet telling them apart is most of what the catalogue is
for. PMEST did not have this problem: its Personality facet
took the v3 kind directly. DC does. The honest remedy is a
**proposed programme extension, labelled as one**: a closed
local type vocabulary, drawn from the v3 kinds and the paper's
§2.2 table — document, package, verdict, freeze, run, event,
envelope, chunk, record, gate-definition, correction,
obligation, question, fact, criterion, defect, archive —
carried in Type alongside the DCMI value (DC permits Type
values from local schemes when the scheme is declared). The
extension dents the "nothing invented" claim by exactly this
much, and §B7 counts it in the comparison: DC supplies the
frame and most of the vocabularies; the programme must still
coin its kind tokens. The tokens are few, closed, and pinned
in the package revision — the same work Annex A owed for its
facet values, owed here for one field instead of three.

---

## B3. How a record resolves — the two-layer discipline

Identical in shape to Annex A's §A3, restated for the record
form:

1. The citation (or the artefact's existing tag, per paper
   §2.2) is read by a human or an LLM and recognised — that is
   all it is for.
2. It is looked up in the **index** (shelf index or run index,
   paper §2.4). Under this annex the index row *is* the DC
   record, extended with the index's own routing columns
   (path, grade/state where Part II applies) — one row, one
   home (P1), the standard fields doing the describing and the
   programme columns doing the routing.
3. The row gives the **locator** (path / section / ledger
   position) and the **fingerprint** (the Identifier value).
4. The fingerprint is checked against the artefact as found.
   A match establishes *content identity only*. Provenance,
   state, and validation are separate claims, established by
   their own records — filing commits, ledger entries, verdict
   issuances — never by the fingerprint and never by the
   citation (v3, P8; Vane's point, §B1).

Where two distinct occurrences would receive identical DC
records (two identical chunks, two attempts at the same call),
the records will in fact be identical in their descriptive
fields. That is expected and harmless **because the record is
not the identity**: the index rows are distinct, carrying the
occurrence discriminators (attempt, response ID, ledger seq,
component digests) in the programme columns that the
descriptive fields do not. DC's repeatability makes this
easier to state than PMEST's synthesis did — a DC record never
pretends to be an address, so nobody asks it to carry a
difference alone. Similar is not the same, and this design
never asks a description to do an identifier's job.

---

## B4. The mapping — §2's artefact table, in Dublin Core

The design paper's §2.2 table, artefact type by artefact type.
Each row names the elements that carry the load, and — where DC
has no honest home for a distinction the programme treats as
load-bearing — says so in the row rather than forcing a field.
"Omitted" follows §B2.1: no honest value, no value.

### B4.1 Documents, configurations, verdicts

| Artefact (v3 kind) | DC record — what carries what |
|---|---|
| Design / governance document (Part II information item) | Type: Text + token *document*. Format: text/markdown (IMT). Date: Created (drafting) / Issued (filing), W3CDTF. Creator: the author. Title: as filed. Identifier: blob digest. Relation: IsPartOf the programme collection. **No honest home:** the *authority* behind the document (Ben's ruling, a tap, a commission) — Creator records who wrote it, not under what authority it stands; Provenance can point at the authorising record but cannot carry its force (see §B6.5). Its standing (current draft vs. superseded draft) is state — omitted, per §B1. |
| Relay package & revision (K3 configuration) | Type: Text + token *package* (the package *file*; its exhibits and preflights are separate records linked by HasPart — DC's part-whole refinements do this natively). Format: text/markdown. Date: Issued. Identifier: blob digest. Relation: IsVersionOf the package line; each revision Replaces the prior *as governing* while the prior remains filed history — DC's Replaces/IsReplacedBy pair expresses supersession of currency without deletion, the closest standard home either annex has found for Part II's supersession structure (e). **No honest home:** the package's governing *force* (that a run must obey it) — a K3 claim, not a description. |
| Gate 1 verdict (K7 verdict issuance) | Type: Text + token *verdict*. Format: text/markdown. Creator: Vane, the issuing instance. Publisher: the shelf (the filing that makes it available), with the filing commit in the index row. Date: Issued (filing date). Identifier: blob digest. Relation: References the package revision examined; IsPartOf the relay collection. **No honest home — the sharpest in this table:** the verdict's *outcome* and its *issuance binding*. PASS is a validation/state fact and stays out (§B1); and K7's mechanism — the verdict is the exact object retained by the issuing contract instance, fingerprint-bound at issuance, invalid at any other instance even if byte-identical — is not metadata at all. DC describes the verdict *document* completely and the verdict *act* not at all. |
| Design freeze (K3 configuration) | Type: Text + token *freeze*. Format: text/markdown. Date: Created (the freeze act's date). Identifier: blob digest (16543582… as pinned). Relation: References the package line it governs; IsPartOf the relay collection. **No honest home:** frozenness itself — that this configuration may not change is a governance fact recorded in the case, not a property DC can assert about a document. |
| Stage 9 execution package (K5 artefact / K3 configuration) | Type: **Collection** + token *archive* — the one row where a DCMI value other than Text does real work: the zip is an aggregation of resources, and Collection says so. Format: application/zip (IMT). Date: Created. Identifier: the zip SHA-256 (v1 48a171f4…, v2 db96297c…) — the cleanest mapping in this annex; the artefact's minted identity and DC's Identifier coincide with no adaptation. Relation: References its identity exhibits (the filed manifests and READMEs under exhibits-zip-identity/); HasPart the manifest *as a relation* — the per-part digests themselves live in the manifest file, not in DC fields. Relation: v2 IsVersionOf the v1 line. **No honest home:** v1's Gate 1 PASS and its non-inheritance by v2 — state/validation, omitted; the index's routing column carries it, exactly as paper §2.5 prescribes. |

### B4.2 Run artefacts

| Artefact (v3 kind) | DC record — what carries what |
|---|---|
| Run (K1 run identity) | Type: **Event** + token *run* — DCMI Type has a value for a time-based occurrence, and a run is one; the second row where the standard vocabulary earns its keep. Date: Created (minted at freeze-begin, per K1); Coverage: Temporal for the run's span where one exists. Identifier: the run identity's fingerprint anchor (the frozen configuration digest it binds, per K1/K3) — with the honest note that a run's identity is a *binding of references*, and DC records the binding's anchor, not the binding. Relation: References its configuration (K3); IsPartOf the relay collection. **No honest home:** the run's disposition (NO START, in run-01's case) — state, in the ledger and routing columns only. |
| Event (K9 event identity) | Described at **collection level**: the event ledger itself is Type: Dataset + token *event-ledger* (a structured, append-only data set — Dataset fits without stretching), Format: application/json lines (recorded as text/plain with the JSONL structure named in Description, or application/jsonl as a declared local Format value — a small, named scheme extension). Individual events are parts: the ledger record carries HasPart relations by locator, and each event resolves by its seq locator in the ledger, per paper §2.4. **No honest home:** the event's transition semantics — that seq 5 *is* GATE1_REV8_PASS as a machine-readable transition is K9/ledger structure; DC can title it, not type it. Per-event DC records are possible but buy nothing the ledger doesn't already state; the mapping declines them. |
| Envelope (K5 artefact) | Type: Collection + token *envelope* — programme rule, stated for uniformity: an envelope is an ordered file set as built, and a one-file envelope is a set of one, so the type does not flip with file count (a converter never has to judge which it is). Format: the set's media types, or the envelope file's where single. Identifier: content digest of the envelope as built. Relation: IsPartOf the run; References the step and recipient role — **with a named strain:** DC has no element for "addressed to role H2 at step 3." Audience (the class for whom a resource is intended) was considered and refused: a protocol role is not an audience class, and borrowing Audience would be a forced field. Step and role ride in the index row and the envelope's own tag (paper §2.2), not in DC. Date: Created (run date where recorded; otherwise omitted — a step position is not a date). |
| Manifest chunk (K5 artefact, derived slice) | Type: Dataset + token *chunk* — the slice is data encoded in a defined structure (the paper's §3 grammar), and Dataset says exactly that. Format: text/plain. Identifier: the chunk digest. Relation: IsPartOf the parent manifest/archive record — clean, standard, and the strongest relation in this table. **No honest home:** the line range (601 TO 650 OF 686). Coverage was considered and refused: Coverage names the spatial or temporal extent *of the content*, not a byte-or-line locator *within a parent artefact*; filing the range there would be a forced field. The range rides in the index row as a micro-locator — the same external-locator outcome Annex A reached by stretching Space, reached here by declining to stretch anything (§B7 counts this a tie with a cleaner conscience). |
| Call record (K9 event-adjacent record) | Type: Dataset + token *record*. Format: application/json (the record), with body / response / stderr as HasPart relations — DC's part-whole refinements carry the set structure natively, though the component *digests* live in the record file and the index, not in DC fields. Date: Created = the record's `started_at_utc`, W3CDTF. Identifier: the record file's SHA-256 (authoritative); the provider response ID as a second, non-authoritative Identifier value under its scheme (§B2.1's cardinality rule exists for exactly this row). Relation: References the artefact examined (the *examines* link — References is DC's generic relation; "examines" as a named refinement is a possible programme extension, not proposed here: References + the index's relation column suffices). **No honest home:** the machinery bindings — caller, helper, dependency digests are *inside* the record as its content; DC Contributor names agents, not digests, and no element binds a record to the code that produced it. That binding is the REV8 caller's own mechanism, and DC neither helps nor hinders it. |
| Gate (part of the case, K3 configuration) | The **Gate Format Definition document** describes cleanly: Type: Text + token *gate-definition*, Format: text/markdown, Identifier: its pinned digest in the frozen schema object, Relation: IsPartOf the schema object / case. **The gate itself** — the established control point in the flow — has **no honest DC home, and this annex refuses the near miss:** Service (a system that provides one or more functions) was considered and rejected; a gate is not a service callers invoke, it is a checkpoint work passes through. DC describes resources; a gate is a position in a process. Its ALLOW / CORRECT outcomes are acts — state transitions on other artefacts — and are doubly outside DC. The definition document is catalogued; the gate is established by the case, exactly as paper §2.2 already had it. |

### B4.3 Information items and contract items

| Artefact (v3 kind) | DC record — what carries what |
|---|---|
| Correction C1 (Part II information item; K6-family commitment per the paper) | Type: Text + token *correction*. Creator: Remmy (selected and authored under delegation — provenance of record, exhibits B3/B4). Date: Created 2026-11-20 (REV5 package date). Relation: IsPartOf RELAY01-PACKAGE-REV5, at the §3 locator (the locator rides in the index row; DC's IsPartOf names the whole, not the section). Provenance: a statement pointing at exhibits B3 (Ben authorised the selection) and B4 (Remmy authored under that delegation) — **partial fit, named as such:** dcterms Provenance speaks of ownership and custody history significant to authenticity; an *authorisation* provenance is adjacent to that meaning, not inside it. The claim record carries the authority; the DC record carries the pointer. Identifier: **the known strain, unchanged** — see §B5.3. DC gives C1 a complete descriptive record and no fingerprint of its own, because as frozen C1 has no separate bytes to fingerprint. HasPart, asserted from the package's record, *names* C1 as a part; naming a part does not digest it. |
| Obligation Ob1 (Part II information item) | Type: Text + token *obligation* — the commitment *record* (in the package / run index) describes as a document. Date: Created (the freeze, when the obligation arose). Relation: IsPartOf the package; References the eventual deliverable when one exists (a different artefact, with its own record). **No honest home — a headline failure, §B6.1:** the obligation itself. That the bundle is *owed* to Claude, that Remmy owns its production, that its due condition is bundle completion + Ben's acceptance — none of this is description of a resource; it is a commitment with a debtor, a creditor, and a condition, and DC has no element for any of the three. Contributor was considered for the owner and refused as a stretch (a contributor helps make a resource; an obligation's owner owes one). The record describes the paper the commitment is written on. The commitment lives in the case and the ledger, where paper §2.2 already put it. |
| Open question Q1 (Part II information item) | Type: Text + token *question*. Date: Created (freeze date). Relation: IsPartOf the package / run index. **No honest home:** OPEN — state, omitted by rule (§B1), and correctly: DC has no element whose absence could be misread as closure, which is the one kindness the gap does the design. The deliberation process and any future ruling (a supersession event, per Part II (e)) are ledger facts, not fields. |
| Initial-ledger fact G1–G10 (Part II canonical claim record) | Type: Text + token *fact*. The numbered statement as frozen (REV5 §4) is the record's Title/Description content. Source: the cited source — **a genuine but partial fit:** DC's Source element exists for "a related resource from which the described resource is derived," and a fact's cited source is honestly that. But Part II (a) requires a *pinned* source reference — digest + dual locators — and Source carries a citation, not a binding; the digest and locators live in the Part II source-reference structure and the index, with Source holding the human-readable citation. **No honest home:** Part II (b)'s three-way split — item, assertion, representation. DC describes resources; it has no assertion layer, and two sources making the same claim (one claim record, several source items) cannot be expressed. The claim record is programme machinery under either annex. |
| Reconstruction / safe-continuation item R1–R14, SC1–SC5 (K12 contract items) | Type: Text + token *criterion*. The frozen textual criterion is the record's content. Relation: IsPartOf the freeze and the frozen schema object (K5/K12) — clean. **No honest home:** the item's *role* — that R1–R14 form a scoring denominator and SC1–SC5 a safe-continuation test is contract semantics inside the pinned schema object (K12). DC can catalogue the criteria as texts; the denominator exists only in the schema object that binds them, under either annex. |
| Defect (K10 attribution subject) | The register itself: Type: Collection + token *defect-register*; each DR row: Type: Text + token *defect*, Date: Created where the register records one (the DR ordinal is a slug segment, not a date), Relation: References its linked evidence set; the register row's repair/disposition is a linked record (paper §2.2), expressible as a References relation. **No honest home — refused explicitly:** the attribution class (SYSTEM / MODEL / INPUT / UNKNOWN). It is a K10 adjudicated claim, and §B1's Description rule exists largely for this row: Description is exactly where a hurried cataloguer would write "SYSTEM defect," and doing so would put an adjudication into an unadjudicated field. The class lives in the attribution record, nowhere else. |

**Reading note.** Three refusals in this table are deliberate
and load-bearing, mirroring Annex A's three: outcomes, grades,
and attribution classes are never filed anywhere in a record;
a near-miss element (Audience for a protocol role, Coverage
for a line range, Service for a gate, Contributor for an
obligation's owner) is refused even when it would make the
table look complete — a forced field is the Dublin Core
equivalent of Annex A's forced facet, and it fails the same
acceptance test, because the next cataloguer, applying the
forced reading differently, produces a different record for
the same artefact; and a relation refinement is used only
where DC's own semantics cover the relation, with the
programme's index carrying everything DC's semantics stop
short of.

---

## B5. Worked examples

The same artefacts as Annex A's §A5, in the same order, so the
two annexes compare artefact-for-artefact — plus the pilot
file of Conversion Test 01, which Annex A never rendered.

### B5.1 Vane's REV8 Gate 1 verdict

**The artefact.** `VANE-GATE1-VERDICT-REV8-2026-11-20.md`,
filed on the shelf at
`duenna/fix-2026-11-19/relay01/VANE-GATE1-VERDICT-REV8-2026-11-20.md`;
canonical blob `347de01eb875bd39040e078132664346763f2eb1`,
filing commit `512be9b904d097f22f41cb6fd0fe959b373f2670`;
recorded in run-01's event ledger at seq 5.

**The DC record.**

```
Title:                VANE-GATE1-VERDICT-REV8-2026-11-20.md
Type:                 Text · verdict            (DCMI Type · programme token)
Format:               text/markdown             (IMT)
Creator:              Vane
Publisher:            ainternet-shelf (filing commit 512be9b9…)
Date (Issued):        2026-11-20                (W3CDTF)
Identifier:           347de01eb875bd39040e078132664346763f2eb1   (Git blob — authoritative)
BibliographicCitation: 2026-11-20/verdict/gate1-rev8
Relation (References): RELAY01-PACKAGE-REV8 (the revision examined)
Relation (IsPartOf):   the relay01 collection
Description:          Gate 1 verdict on Relay 01 Package Revision 8, filed by the examiner.
```

**Resolution, and how the constraints hold.** The index row
for this record gives the path and the Identifier — blob
`347de01e…`. A reader who finds a file at that path checks the
blob: a match establishes that *these are the filed bytes*.
It does **not** establish that the verdict's content is
correct, nor even, by itself, that Vane issued it: provenance
rests on the filing commit and the ledger's seq 5 record, and
K7 binds a verdict to its issuing instance, not to its bytes
alone. The verdict's outcome — PASS — appears **nowhere in
this record**: it is a validation/state fact, recorded at
ledger seq 5 and in the index's routing column. A same-titled
copy with a different blob — the REV5 corrigendum's lesson, in
which a bridge-message copy (a439e2ee…) was nearly filed as
the verdict (fdebe61c…) — is exposed by the Identifier,
however perfect its descriptive record. Record describes;
index resolves; fingerprint identifies; commit and ledger
provenance; the PASS stands in the routing record. No layer
does another layer's job — and the descriptive layer here is
one any repository tool on earth can already read.

### B5.2 A run-01 archive-verification chunk record

**The artefacts — two, and the distinction is the example**
(unchanged from Annex A). The chunk under examination is the
envelope `relay01/run-01/envelopes/chunks50/o-v1-r3-c11.txt`:
ARCHIVE v1, CHUNK 11 OF 12, MANIFEST LINES 601 TO 650 OF 686 —
a header and 50 manifest lines, SHA-256
`bb445056f6be535b65ae55fc53fa17d7109d6679f3d9d54a13b281b6af3dfc45`.
The record rendered here is the call record
`relay01/run-01/calls/av-o-v1-r4-c11-r3.record.json`, the REV8
caller's record of the NVIDIA/Kimi attempt on that chunk.

**The DC record (the call record).**

```
Title:                av-o-v1-r4-c11-r3 (label as recorded — a historical local label, paper §2.3)
Type:                 Dataset · record          (DCMI Type · programme token)
Format:               application/json          (IMT)
Date (Created):       2026-11-21T02:06:39Z      (W3CDTF — the record's started_at_utc)
Identifier:           f3cbd812fb8c5cf9e239b3d46911c66179aa29e23bad7605c26cf6b85af3b6d4   (SHA-256 — authoritative)
Identifier:           chatcmpl-c3e3baf4-2f3e-4cb6-a788-940a4ea758df   (provider response ID — non-authoritative)
BibliographicCitation: 2026-11-21/record/av-o-v1-r4-c11-r3
Relation (HasPart):   body b8c54b37… · response d451ff86… · stderr e3b0c442… (empty)
                      — relations named here; the digests themselves are the record's content and the index's columns
Relation (References): the chunk envelope o-v1-r3-c11.txt (bb445056…) — the artefact examined
Relation (IsPartOf):   run-01
Description:          Record of the NVIDIA/Kimi archive-verification attempt on v1 chunk 11 under the REV8 caller.
```

For completeness, the chunk's own record is three lines of
the same form: Type: Dataset · chunk; Format: text/plain;
Identifier `bb445056…`; Relation (IsPartOf): the v1 manifest /
archive record — with the line range 601 TO 650 OF 686 carried
in the index row as a micro-locator, **not** in Coverage
(§B4.2's refusal, applied).

**Resolution, and how the constraints hold.** The run index
row for this record carries the record file's own SHA-256,
`f3cbd812…` — the same value as the record's Identifier;
under DC the index and the record agree by construction,
because the index row *is* this record (§B3). Inside, the
record binds its components by digest — body `b8c54b37…`,
response `d451ff86…`, stderr (empty) `e3b0c442…` — and its
machinery by digest: caller `54117c63…` (the REV8 caller),
helper `56ca6a4d…`, dependency `8b1f42e8…`. None of those
machinery bindings is a DC field (§B4.2); they are the
record's content, and DC's HasPart names the set without
pretending to bind it. The response's content — FORMAT_OK:
NO / VERDICT: FAILED — is a validation claim preserved inside
the response file. It appears in **no** field of either
record, and the response's fingerprint proves only that these
response bytes are the preserved ones — not that the judgement
in them was right (the orchestrator's mechanical cross-check
of this envelope found zero format violations; that
disagreement lives where the design puts it, in the
discrepancy layer, with both positions intact). This is Vane's
point operating on the programme's most sensitive record:
identity, all the way down, never once standing in for
validity — now stated in a record format that did not have to
be invented to state it.

### B5.3 C1, the correction, as frozen in REV5

**The artefact.** C1, the audience ruling — *the brief is
written for a plain reader picking it up cold: precision kept,
jargon defined or dropped; the re-derivation instructions
remain technical* — frozen at §3 of
`RELAY01-PACKAGE-REV5.md` (shelf:
`duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV5.md`; the
package's Git blob `dc9aa183ce0c8974226ba3785d0ff46ba1924717`,
SHA-256 `05e8d9a7cd824891ddb79df0abf5fdcc6a0e21ba5d1e9b8e1910b57e5bca6d47`).

**The DC record.**

```
Title:                C1 — the audience ruling
Type:                 Text · correction         (DCMI Type · programme token)
Format:               text/markdown (a clause within a Markdown package)
Creator:              Remmy (selected and authored under Ben's delegation — exhibits B3/B4)
Date (Created):       2026-11-20                (W3CDTF — the REV5 package date)
Identifier:           [NO ITEM-LEVEL FINGERPRINT EXISTS — see below]
                      container: dc9aa183ce0c8974226ba3785d0ff46ba1924717 (Git blob, REV5 package)
                      container: 05e8d9a7cd824891ddb79df0abf5fdcc6a0e21ba5d1e9b8e1910b57e5bca6d47 (SHA-256, REV5 package)
                      — both values are the CONTAINER's, labelled as such; neither is C1's
BibliographicCitation: 2026-11-20/correction/c1-audience-ruling
Relation (IsPartOf):   RELAY01-PACKAGE-REV5, §3 (section locator carried in the index row)
Provenance:           Statement pointing at exhibits B3 (Ben authorised the selection)
                      and B4 (Remmy authored under that delegation) — partial fit, §B4.3
Description:          The audience ruling: the brief is written for a plain reader picking
                      it up cold; re-derivation instructions remain technical.
```

**Resolution — and the honest limit, identical to Annex A's.**
The index row for C1 resolves to a **container fingerprint
plus a locator**: the REV5 package's blob/SHA-256, at §3.
That establishes the package's bytes and locates the clause
exactly. It does **not** give C1 a fingerprint of its own,
because as frozen, C1 has no separate bytes to fingerprint —
and Dublin Core changes this not at all. DC's HasPart,
asserted on the package's record, can *name* C1 as a part of
REV5; a named part is not a digested part, and entering the
container's digest in C1's Identifier field *without* the
container label would be precisely the substitution the
two-layer principle forbids — the record above therefore
carries the label in the field itself, so the strain is
visible to any reader rather than filed away. What C1 has,
under v3 Part II, is a source reference (the package, at its
digest, with dual locators: shelf path + §3) and a canonical
claim record. A C1-specific fingerprint comes into existence
only when the sealed delivery artefact is created and hashed
into the event ledger at delivery — at which point the index
adds that artefact as a delivery representation of the same
item, linked by derivation, while C1's identity remains the
one minted at the freeze. **The strain is syntax-independent:**
PMEST classified C1 cleanly and could not resolve it; DC
describes C1 cleanly and cannot resolve it. The borrowing —
either borrowing — runs out at the container wall, and the
programme's own Part II machinery does the work. §B6 records
this as a shared limit, not a DC defect.

Authority, for completeness, sits where it should: Ben
authorised the selection among candidate corrections (exhibit
B3); Remmy selected and authored the ruling under that
delegation (exhibit B4 corroborates). The DC record points at
that provenance; it does not carry its force, and no field in
it should be read as doing so.

### B5.4 The pilot file, in Dublin Core

**The artefact.** `exhibits-zip-identity/v1/README-EXECUTION.md`
— the execution readme of the Stage 9 independent execution
package v1; the file Conversion Test 01 converted under PMEST,
against a baseline frozen before conversion
(`~/workspace/colon-test/BASELINE-HASHES.txt`). Its own
fingerprint (baseline): `f15fbf6d5f0448b3dbee131d3ffcea83bdf9a397c30971705e1b3c2f07479582`.
Not to be confused with the archive it describes (zip v1,
SHA-256 48a171f4…) — the readme is a document ABOUT the
package, not the package; the pilot's first discipline, and
this record keeps it: the zip appears under Relation, never
under Identifier.

**The DC record.**

```
Title:                README-EXECUTION.md — execution readme, Stage 9 execution package v1
Type:                 Text · document           (DCMI Type · programme token)
Format:               text/markdown             (IMT)
Date (Created):       2026-11-20                (W3CDTF — the file states "Built 2026-11-20")
Identifier:           f15fbf6d5f0448b3dbee131d3ffcea83bdf9a397c30971705e1b3c2f07479582   (SHA-256 — authoritative)
BibliographicCitation: 2026-11-20/document/readme-execution-stage9-v1
Relation (IsPartOf):   exhibits-zip-identity/v1 (the identity-exhibit set)
Relation (References): the Stage 9 execution package v1 (zip, 48a171f4…) — the artefact described
Description:          Execution readme of the Stage 9 independent execution package v1:
                      what the package is, and how its manifest is verified after unpacking.
Creator:              — omitted. The pilot baseline records the build date, not an author
                      statement this record may rest on; DC does not require the element,
                      and §B2.1 omits rather than infers.
```

**Against the pilot's pass mark** (stated before Conversion
Test 01, applied unchanged): *no field forced; no one-off
exceptions; the same rules applied by anyone land on the same
record.*

- **No field forced: PASS.** Every populated element comes
  from the file's own statements (its role, its build date),
  its format, or its baseline fingerprint. Two candidate
  fields were refused rather than forced: Creator (above) and
  any element for the execution process (below).
- **No one-off exceptions: PASS.** Standard elements, standard
  refinements, scheme-pinned values throughout. The only
  programme extension in the record is the type token
  *document* (§B2.3), which is a declared scheme, not an
  exception invented for this file.
- **Same rules, same record: PASS — and stronger than the
  PMEST pilot on the fields DC schemes pin.** Date is W3CDTF,
  Format is IMT, Type's first value is from a closed
  twelve-value vocabulary: three of the pilot's five facets
  (Time, Matter, and Personality's type half) are here
  scheme-pinned rather than descriptive prose, so two
  cataloguers have nothing to phrase differently. The honest
  residue is the same slow-drift caveat Annex A raised for its
  facet values, confined here to the free-text fields: two
  cataloguers could word Title or Description differently.
  That costs retrieval neatness, not identity — the Identifier
  is identical either way — and the citation form (§B2.2) is
  built from the pinned segments (date, type token, title
  slug), so the drift touches the record's prose, not its
  address.

**The pilot's soft spot — does it survive under DC?** The
PMEST pilot's one named soft spot was Energy precedence: the
readme honestly fits two process relations (the independent
execution it *instructs*; the Gate 1 examination the package
*underwent*), PMEST's single Energy facet forced a choice,
and a second converter could choose the other and land on a
different face. **Under Dublin Core the soft spot does not
shrink and does not grow. It dissolves — by omission.** DC has
no process element. Neither process relation is asked for, so
no converter can diverge on one: agreement is achieved by
saying less. Whether that is a win depends entirely on whether
the process relation was load-bearing. For this readme it was
not — nothing routes on which process the readme serves; its
Energy value in the pilot was catalogue colour. For artefacts
where a process relation *is* load-bearing (a gate's
definition, a run's configuration), the relation lives in the
case and the schema object under either annex, and DC's
silence costs nothing the design was using. The verdict,
stated without advocacy: PMEST's soft spot was the price of
expressiveness — a facet that can hold a process can hold two
and force a precedence rule. DC pays no such price because it
buys no such expressiveness. A programme that needs process
relations *in the catalogue face* should weigh that in §B7's
comparison; this programme, on its own record, routes process
through cases, ledgers, and schema objects — not through
catalogue faces.

---

## B6. Where Dublin Core cannot honestly carry the load — stated plainly

DC describes every artefact type in §2's table *as a
resource*. It fails — or is silent — at the following
load-bearing distinctions. None is smoothed over; each is
either a stated refusal (which keeps the mapping honest) or a
limit the programme's own machinery must carry under any
borrowing.

1. **Commitment force (Ob1; K6 receipts generally).** DC has
   no deontic layer — nothing that says *owed*, *due*, *by
   whom*, *to whom*, *on what condition*. The obligation
   record describes perfectly; the obligation is not in it.
   This is the mapping's largest single gap, because Ob1 is
   not catalogue colour: the relay's ground truth includes
   that the bundle is owed to Claude and NOT DELIVERED, and
   the second half of that sentence is a state DC cannot hold
   and the first half a commitment it cannot express. The
   case, the ledger, and the index's routing columns carry
   obligations. DC carries their paperwork.
2. **Verdict issuance (K7).** The verdict document describes
   completely; the verdict act — issuance by a retained
   instance, fingerprint-bound at issuance, invalid elsewhere
   even if byte-identical — is a mechanism, not metadata.
   Any design that let a DC record stand in for issuance
   would fail Vane's examination point on the programme's
   most authority-sensitive artefact.
3. **Attribution (K10).** No element exists, and the one
   always-available field (Description) is refused by rule.
   Attribution remains a single adjudicated record, minted by
   the adjudicating authority, referenced — never restated —
   by everything else (P1, K10). DC's silence here is safe
   only because the refusal is stated; an unstated silence
   would invite prose.
4. **Grade and standing state (Part II (c); OPEN; NOT
   DELIVERED; NOT SATISFIED).** DC's Date refinements record
   *events of change* (Created, Issued, Modified); nothing
   records a *standing* — and a grade is a standing,
   established by a verification act and travelling with every
   reference. Filing a grade anywhere in a DC record would
   also break Part II's rule that grade is state, not
   identity, in the most literal way available: by writing it
   into the identity's own description. Both annexes exclude
   state from the face; DC makes the exclusion harder to
   police, because the record is roomy and prose is always
   permitted somewhere. The §B1 Description rule is the
   policing, and it is a programme rule, not a DC property.
5. **Authority provenance.** Creator, Publisher, and
   Contributor record *who produced and published*. They do
   not record *under whose authorisation, resolvable to a
   pinned governance record* — Ben authorised C1's selection;
   a delegation issued and was accepted; a verdict was filed
   under an examiner's mandate. Provenance (the refinement)
   gestures at custody history significant to authenticity;
   authorisation provenance is adjacent, not contained. DC
   carries the pointer to the authority record. The authority
   record — delegation, acceptance, exhibits — carries the
   claim. A catalogue that blurred this would let a byline
   stand in for a mandate: P8's provenance/authority confusion
   in its most ordinary clothes.
6. **The assertion layer (Part II (b)).** Item, assertion,
   and textual representation are three things in v3; DC sees
   one resource. Two sources asserting the same claim, one
   claim in several representations, a representation whose
   source is unresolvable — none is expressible. The canonical
   claim record is programme machinery under either annex;
   DC's Source element covers the *citation* half of the
   source reference and none of its *pinning*.
7. **Micro-locators.** A line range inside a manifest, §3 of a
   package: DC's Relation can carry a URI with a fragment by
   convention, but DC semantics do not define fragment
   locators into arbitrary files, and Coverage was refused
   (§B4.2). The index carries micro-locators. **Tie with
   Annex A**, which reached the same wall and proposed
   stretching Space over it; this annex reaches it and
   declines to stretch. The wall is the same wall.
8. **The gate as a control point.** Only the gate's
   definition *document* is describable. The gate — an
   established point where work is allowed or corrected — is
   a position in a process, and its outcomes are acts. A
   catalogue of resources has no row for a checkpoint, under
   either annex (PMEST's gate row likewise described the
   definition and the verdict-record shape, not the gate).
9. **Occurrence discrimination.** Two identical chunks, two
   attempts at one call: identical DC records, exactly as
   Annex A's faces were identical PMEST faces. The index's
   programme columns discriminate occurrences under both
   annexes. **Tie** — and under DC the tie is cheaper to hold,
   because a description never claimed to be an address
   (§B3).
10. **Container items (C1; in lesser degree G1–G10, R/SC
    items).** No item-level fingerprint exists for a clause
    inside a package, and no DC field mints one. §B5.3 states
    the limit in full. **Tie with Annex A** — the principal
    strain of the PMEST mapping is also this mapping's
    principal strain, because it was never a property of the
    syntax. It is a property of containers.

A further limit, not a failure: **the local type vocabulary
(§B2.3) is real invention, honestly labelled.** "Borrow
Dublin Core and invent nothing" is true of the record's
frame, its date and format schemes, and its relations. It is
not true of the kind distinctions, where DCMI Type's twelve
values run out and the programme coins its own tokens. The
invention is small, closed, and declared — but a comparison
that hid it would be advocacy, and §B7 does not.

---

## B7. The comparison with Annex A — stated without advocacy

The two annexes borrow different *kinds* of thing. Annex A
borrowed a **grammar for synthesising addresses**; this annex
borrows a **standard form for describing resources**. Most of
the comparison follows from that single difference.

**Where Dublin Core is stronger.**

- **The record form is off-the-shelf.** Annex A had to propose
  a programme normalisation — an analysis notation, a face
  rendering, indicator assignments — before its first example
  could be written, and that normalisation is itself a design
  artefact the examiner must accept before the borrowing can
  be examined. DC's record needs no rendering proposal: the
  fields, their refinements, and their order of presentation
  are the standard's. There is simply less programme-invented
  surface for two cataloguers — or two checkers — to diverge
  on.
- **Two of the open vocabulary problems are pre-solved.**
  Annex A's §A6 closed by admitting its Matter and Energy
  values were descriptive prose and that a controlled
  vocabulary "must be pinned in the package revision." DC
  pins Date by scheme (W3CDTF) and Format by scheme (IMT)
  *in the standard*, and Type's first value from a closed
  list of twelve. The vocabulary work that remains under DC
  is one local list (the type tokens, §B2.3); under PMEST it
  was three facet vocabularies.
- **Relations exist.** PMEST has no relations at all: a face
  describes its artefact and nothing else — derivation,
  supersession, part-whole, and examined-by lived entirely
  outside the face, in the index. DC's Relation refinements
  give Part II's supersession (Replaces / IsReplacedBy),
  derivation neighbourhood (Source, References), and
  part-whole structure (IsPartOf / HasPart) standard,
  machine-readable homes *inside* the record. Of the two
  borrowings, only DC touches Part II's relationship
  structures (d) and (e) at all.
- **The two-layer separation is a standard feature, not a
  construction.** Identifier and BibliographicCitation are
  distinct elements with distinct jobs in DC itself. Annex A
  had to state its face/fingerprint separation as a programme
  discipline over a syntax that does not know fingerprints
  exist. Both annexes hold the separation; DC holds it with
  standard parts.
- **Recognisability by ubiquity.** Ben's doctrine (§1.6 of
  the paper) asks that IDs be indexable and recognisable to
  LLMs. PMEST serves that by grammar — a century-old facet
  logic a reader can reason from. DC serves it by exposure:
  the element set is among the most widely replicated
  metadata forms in existence, in every repository, harvester,
  and training corpus. A checker that has never seen this
  programme has seen Dublin Core.

**Where PMEST was stronger.**

- **Synthesis.** A PMEST face is *built* — for an artefact
  type nobody has catalogued before, facet analysis produces
  an address from first principles, in the borrowed grammar.
  DC produces no address at all: §B2.2's citation form is a
  programme rule assembled from record fields, which is to
  say that under DC the programme still invents its address
  form (a small, fixed invention — but Annex A's central
  claim, that the address grammar itself can be borrowed,
  has no DC counterpart). A programme expecting a steady
  stream of *new artefact kinds* gets more from a grammar
  than from a form.
- **The face is self-locating.** PMEST's Space facet carries
  the resolution locus *in the face*: the string itself says
  where the thing resolves. A DC citation says when, what
  kind, and what it is called — the locator lives in the
  index row, and the citation is mute about it. For a reader
  holding only the citation, PMEST tells them where to go;
  DC tells them what they will find when the index takes
  them there.
- **Kind-first analysis.** PMEST's Personality facet forced
  the cataloguer to answer "what *is* this, in the system's
  own kinds?" as the first act, and the v3 kinds slotted in
  directly. DC's Type answers a coarser question, and the
  programme's kinds re-enter through a local token list —
  present, but as an extension rather than as the borrowed
  syntax's own spine.
- **Expressiveness about process.** PMEST's Energy facet
  could hold a process relation in the face — at the price
  of the pilot's precedence soft spot (§B5.4). DC cannot
  hold one at all. On this programme's record, process
  relations route through cases and ledgers rather than
  catalogue faces, so the loss is theoretical here; it is
  recorded because a different programme — or this one,
  later — could feel it.

**Where they tie.** Container items (§B6.10) strain
identically, because the strain is in containers, not
syntaxes. Occurrence discrimination is external under both.
Micro-locators are external under both. State, grade,
attribution, and authority are excluded under both — by the
programme's own P8, not by either borrowing's generosity.
And both borrowings leave the same programme machinery
standing underneath: the index, the ledger, the Part II claim
records, the K7 issuance mechanism, and the gate format
definition of the paper's §3, which neither annex touches
and neither annex's catalogue can replace.

---

## B8. What this settles for §6 Q3 and the citation form — and what it leaves open

Design paper §6 Q3 asked: whether the exploratory Index-ID
form (IDX-YYYYMMDD-nnnn) is adopted as the index identity for
programme artefacts, or the dated-slug citation plus the index
table suffices for non-letter artefacts. *Owner: Ben.* Annex A
answered it by synthesis (a PMEST face as the catalogue form).
This annex answers it independently, by record:

**What this annex settles — a second direction for the form.**
The index row for a non-letter artefact can *be* a Dublin
Core record: a fixed, standard field set in which the
Identifier element carries the fingerprint, the
BibliographicCitation element carries the readable citation
(§B2.2's form — date, type token, slug), and the Relation
refinements carry the artefact's typed links. On this
direction, Q3's either/or dissolves by a different route than
Annex A's: not a synthesised face over the index, but a
standard record *as* the index row — the programme invents
neither a slug grammar nor a facet rendering, only a citation
assembly rule and a closed type-token list. The Index-ID form
is unnecessary for artefact cataloguing on this direction
too — for the record-standard reason rather than the
face-synthesis reason. The dated-slug convention's function
(indexable, recognisable, shelf-made) is preserved, and its
form is succeeded per Ben's 20:20 opening, with the transition
discipline of §B2.2 (aliases in the index; nothing rewritten).

**What it does not settle.**

- Whether Ben **adopts** this form, Annex A's form, or
  neither. The adoption ruling is his, and it is now a choice
  between two worked proposals (plus the standing option of
  the unamended §1.6 convention). This annex is a proposal,
  as Annex A was.
- The **type-token list** (§B2.3) — its exact membership is
  package-revision work, pinned there, not here.
- Whether **letter citations** migrate form (§B2.2). The SS4
  item-6 question and the letter-registration context (paper
  §6 Q1–Q2) are untouched by this annex, as by Annex A.
- The **micro-locator convention** (§B6.7) — carried in the
  index under both annexes; if a future design wants it
  inside records, that is a programme convention for the
  examiner to accept or refuse, not a DC feature to invoke.
- **Part II's consolidated model** (paper §6 Q4) — DC's
  Relation and Source elements describe pieces of its
  neighbourhood; the model itself, and the examiner's
  acceptance of it, are exactly where they stood.
- **Coverage**: which artefact types *must* carry a DC record
  in the index from adoption forward. The history half is
  already answered by the paper's §2.5: indexed, never
  rewritten — records about historical artefacts are index
  data, not edits to them.

---

## B9. Route

Unchanged from the design paper's §5.2, with this annex riding
as part of the same paper, alongside Annex A:

1. **Ben reviews the paper and both annexes.** His approval —
   including his ruling on which borrowed form, if either, the
   programme adopts, and on §B8's open adoption questions —
   is the gate for everything after.
2. **Remmy incorporates the approved design** (paper + the
   adopted annex) into a new Relay 01 package revision: the
   Gate Format Definition, the index forms, the type-token
   vocabulary, and the §B6 limits stated as package positions
   for examination.
3. **The revision goes to Vane for Gate 1 examination.** Her
   stated focus (2026-11-20 20:07 MST) — identity unambiguous
   across shelf, gates, and run records; face and fingerprint
   consistently related; no readable name as identity
   authority; no fingerprint as proof of validity — is the
   examination this annex was written to face.
4. **No execution before a fresh Gate 1 PASS** and
   satisfaction of the applicable start conditions. Run-01's
   NO START, its archive discrepancies, and its Gemini
   failures remain preserved evidence, exactly as they stand.

EXON's place in this is Ben's ruling of 20:13 MST and nothing
more: the syntax is established on the shelf first; EXON may
adopt it later, at his call, in EXON's own time. This annex
designs nothing for EXON.

---

## Disposition

Annex B to the design paper of 2026-11-20, drafted the same
evening under Ben's direction, steer, and rulings as cited
above. It proposes a plainer borrowed form than Annex A's and
tests it against the programme's actual artefacts, including
where it fails. It enacts nothing. Annex A stands as a
preserved draft beside it; the choice between them — or
neither — is Ben's, on his review, with the paper.

[END EXTERNAL CONTENT: source=file file=~/workspace/duenna-fix/ID-FORMAT-SHELF-DESIGN-ANNEX-B-DUBLIN-CORE-2026-11-20.md tool_name=read]