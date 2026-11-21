# ADOPTION SPEC — WHAT THE DESIGN TAKES FROM DUBLIN CORE AND FROM EXON

*2026-11-20. DRAFT. Paper only. Authority: Ben, 2026-11-20
20:34 MST — "establish the full spec of what needs adopted
from the languege based on our current and foreeable needs" —
read back to Ben and carried in the record (memory/2026-11-20.md
L1072) as: ONE spec covering both borrowed sources, term by
term, each adoption justified by a current or foreseeable
need. The spec sits inside the approved design stage (Ben's
tap 2026-11-20 20:04; his approval to proceed 20:31) and binds
into the Relay 01 package alongside REV9.*

*Sources read first-hand for this spec: the design paper
`ID-FORMAT-SHELF-DESIGN-2026-11-20.md` (§2, §6); Annex A
(PMEST) and Annex B (Dublin Core), same folder;
`ID-SYSTEM-DESIGN-DRAFT-V3.md`; EXON's combined shelf folder
`ainternet-shelf/duenna/exon/` — its INDEX.md, then the
dictionary and reference-matrix documents named in Part 3;
and Ben's rulings of 2026-11-20 evening as recorded in
memory/2026-11-20.md (20:13 L1057; 20:19–20:20 L1065, L1075;
20:30 L1069; 20:33 L1071; 20:34 L1072–L1073).*

*Honesty rule, Ben's standing one: established facts are
cited; forecasts are labelled FORECAST; gaps are named. EXON
terms are cited ONLY from EXON's own documents, with the
document named. Where EXON's dictionary has no term, the
entry says so. Nothing in this spec invents an EXON term,
a DC element, or a need.*

*A status warning that governs all of Part 3: EXON's own
documents are drafts. Dictionary 0.4 is titled "INTEGRATED
DRAFT FOR CHALLENGE"; the Dictionary 0.5 Supplement is a
"draft for owner review — nothing admitted or frozen"; the
Foundational Vocabulary is "draft for review; nothing
admitted or frozen," and each of its proposed dictionary
terms is marked "not currently an entry in the Dictionary
0.5 inventory." Every EXON adoption below is therefore an
adoption of a term at draft status in its home system,
carried at that status. The spec pins the term as cited;
it does not chase later EXON movement (Part 5).*

---

## Part 1 — Needs inventory

Every need below carries its source: a record, a ruling, or
a labelled forecast. No need is asserted without one.

### Current needs

**N1 — One record form for every artefact kind the programme
produces.** The design paper's §2.2 table lists seventeen
artefact types (documents, packages and revisions, verdicts,
the freeze, runs, events, envelopes, chunks, call records,
gates, corrections, obligations, questions, ledger facts,
criteria, defects, the Stage 9 archives). Each needs a
catalogue record any checker reads identically — the
requirement whose absence run-01's Gate A failure exposed
(paper §3.1: the answer's shape was prescribed, the format
under examination was not defined).

**N2 — Identity separated from description.** Exactly one
authoritative identifier per artefact (the fingerprint), and
a readable citation that is never an authority. Source: the
two-layer principle, adopted by Ben 2026-11-11 (paper §1.2);
Vane's collaboration point 2 (2026-11-20 20:30): the
fingerprint remains authoritative, the readable slug an
indexable, recognisable representation, the old-to-new index
preserving traceability without creating new identities.

**N3 — Kind distinctions inside the catalogue itself.** A
verdict, a package, a freeze and a fact must be tellable
apart by the record, not by a reader's guess from a filename.
Source: paper §2.2; Annex B §B2.3 (DCMI Type's twelve values
collapse all four into Text — the gap this need answers).

**N4 — Dates and formats pinned to external schemes.** Two
cataloguers must have nothing to phrase differently. Source:
Ben's UTC ruling (paper §1.5); Annex A §A6's admission that
its facet values were descriptive prose awaiting a pinned
vocabulary.

**N5 — Typed relations.** Part-whole (package ↔ exhibits,
ledger ↔ events, archive ↔ manifest), version and
supersession (REV1–REV8, package v1/v2), and reference
(verdict → package examined, chunk → parent manifest,
fact → cited source). Source: paper §2.2, §2.5; v3 Part II
structures (d) derivation and (e) supersession.

**N6 — A state vocabulary that lives outside the identity
record.** Gate outcomes, obligation standing, question
standing, evidence grades, and disagreement states must be
sayable — in the ledger and the index's routing columns,
never inside the artefact's own description. Source: paper
§2.4 (state rides in the routing record), §3.3 (UNEXAMINED),
§3.6 (ALLOW / CORRECT); v3 P8 (identity, provenance, state
and validation are four different claims); v3 Part II (c)
(grade as state, not identity).

**N7 — Obligation expression.** Something must be able to
say *owed, by whom, to whom, on what condition* — Ob1 (the
bundle owed to Claude, owner Remmy, due on completion +
Ben's acceptance) is live now, and K6 receipt lifecycles
stand behind it in governed runs. Source: paper §2.2 (Ob1);
Annex B §B6.1 (DC has no deontic layer — the mapping's
largest single gap); v3 K6.

**N8 — Attribution expression.** One class per failure,
minted once by the adjudicating authority, referenced and
never restated. Source: v3 K10; Annex B §B6.3 (no DC element
exists, and Description is refused as the smuggling route).

**N9 — Issuance expression.** A verdict must be bound to
its issuing instance — valid there, invalid at any other
instance even if byte-identical. Source: v3 K7; Annex B
§B6.2 (the verdict *document* describes completely in DC;
the verdict *act* not at all).

**N10 — Gate machinery vocabulary.** The Gate Format
Definition (paper §3.2) is itself a catalogued artefact;
its verdict records have a prescribed shape (§3.2(3)); and
the computed-vs-judged distinction of §3.3 must be nameable
in those records — a format verdict is the output of a
deterministic procedure, not an opinion.

**N11 — Audit-copy discipline.** Run-02 works from a copy;
the originals stay frozen as the audit baseline, and the
copy must be identifiable as a copy so the work can be
audited against the originals afterwards. Source: Ben's
ruling of 2026-11-20 20:33 ("make sure we work from a copy
so we can audit it after"), carried into REV9 as a written
provision (memory/2026-11-20.md L1071, L1073).

**N12 — Gate 2's records.** When Gate 2 runs, Alex's
adjudication, its report to Ben, the attribution records it
mints (N8), and its discrepancy resolutions must be
describable and citable in the same catalogue, under the
same rules. Source: the programme's gate structure (Ben
holds the structure; Vane examines at Gate 1; the
adjudicator decides at Gate 2 on a verified package — paper
§5.2 step 4); v3 K10 (attribution minted by the adjudicating
authority).

**N13 — Citation transition without rewriting history.**
Existing citations — the pb-YYYYMMDD-… letter slugs, the
REV1–REV8 and verdict filenames — keep resolving; the index
maps old form to new without creating new identities and
without editing the documents that contain them. Source:
Ben's ruling of 2026-11-20 20:20 (the dated slugs' *form* is
open; their *function* — indexable, recognisable, made for
the shelf — stands); paper §2.5; Vane's point 2 (20:30).

**N14 — A vocabulary two different checkers apply
identically.** The borrowed vocabulary must be plain,
standard, and small enough that independent application
converges — the property whose absence Gate A demonstrated
and whose presence in any candidate syntax is a claim to be
tested, not assumed. Source: Ben's fluency challenge and
the recorded correction (memory/2026-11-20.md L1075: models
*explaining* a syntax is established; models *applying* it
identically is unproven); Ben's steer of 20:19 to a "more
less flamboyant one."

### Foreseeable needs — each labelled FORECAST

**F1 — FORECAST: run-02 and later runs multiply instances
and add kinds.** The audit-copy discipline (N11) will
produce comparison records (copy against original) that do
not exist as an artefact kind yet; discrepancy records
(v3 K10) will be filed as artefacts in their own right.
The adopted vocabulary must extend by *addition to a closed
list*, never by redefinition of an adopted term. Source:
REV9's run-02 provisions (L1073); v3 K10's discrepancy
record; the run-01 → run-02 succession already in the
record (paper §5).

**F2 — FORECAST: EXON takes up the established system
later, without rework.** Ben ruled (2026-11-20 20:13): the
syntax is established on the Duenna shelf first; EXON
adopts it afterwards, at his call, its own development
continuing independently meanwhile. The adopted set should
therefore prefer EXON-sourced terms where EXON genuinely
has them, and standard schemes elsewhere, so that EXON's
later adoption is a taking-up, not a translation. Source:
memory/2026-11-20.md L1057.

**F3 — FORECAST: the catalogue outgrows the relay.** Other
Duenna work — battery reruns, briefcase cases, future
programmes — will catalogue artefacts under the same
system. Kinds not yet known argue for the closed-list-plus-
addition discipline of F1 and against any term whose
meaning is borrowed loosely. Source: the design paper's own
scope (§2 applies v3's general kinds to one programme; v3
was designed for governed runs in general).

---

## Part 2 — Adopted from Dublin Core

The borrowing, as Annex B §B1 states it: the fifteen DCMES
elements, the DCMI Type Vocabulary, the standard element
refinements, and the encoding schemes that pin values —
W3CDTF for dates, the IMT list for media types. Dispositions
use Vane's rule (her point 1, 2026-11-20 20:30): where DC
cannot faithfully express a distinction, the design extends
it *explicitly* — hence ADOPT WITH DECLARED EXTENSION is a
first-class disposition below, never a quiet stretch.
"Binds" names where the term does its work: the §2.2
artefact rows and the gate records of paper §3.

### 2.1 Elements

| Element | Disposition | Need | Binds |
|---|---|---|---|
| Identifier | ADOPT WITH DECLARED EXTENSION | N2 | Every artefact row. The extension, declared: exactly ONE authoritative value — the fingerprint (SHA-256 or Git blob), stated with its scheme; further values (provider response ID, legacy PB-ID) permitted only as explicitly non-authoritative. DC permits several Identifier values and never says which is authoritative; the cardinality-of-authority rule is the programme's, laid over DC (Annex B §B1, §B2.1). |
| BibliographicCitation | ADOPT | N2, N13 | Every artefact row. Carries the citation form of §2.4 — the readable face, distinct from Identifier inside the borrowed standard itself (Annex B §B2.1). |
| Title | ADOPT | N1 | Every row: the artefact's title as filed. |
| Type | ADOPT WITH DECLARED EXTENSION | N3 | Every row. The extension, declared: the local type-token vocabulary of §2.3, carried alongside the DCMI value, because DCMI Type alone collapses the programme's load-bearing kinds into Text (Annex B §B2.3). |
| Format | ADOPT | N4 | Every row: an IMT media type, from the scheme, never free prose — with ONE declared local value, *application/jsonl*, for the event ledger's line-delimited form (Annex B §B4.2 named it a small, named scheme extension; it is declared here, not smuggled). |
| Date | ADOPT | N4 | Every row, under the refinements of §2.2, in W3CDTF, UTC (paper §1.5). Sequence is never filed here: a ledger seq, a step number, a line range are not dates. |
| Relation | ADOPT | N5 | Every row, under the refinements of §2.2. |
| Creator | ADOPT | N1, N9 | Verdict rows (the issuing examiner), document rows (the author), correction rows (the correcting actor as authored under delegation). Records *who* — never under what authority (Part 3 and §B6.5 carry that boundary). |
| Publisher | ADOPT | N1 | Verdict and package rows: the shelf filing that makes the artefact available, with the filing commit in the index row (Annex B §B5.1). |
| Contributor | ADOPT (narrow binding) | N1 | Genuine contributors only. REFUSED USE, recorded: Contributor for an obligation's *owner* — a contributor helps make a resource; an obligation's owner owes one (Annex B §B4.3). |
| Source | ADOPT (partial fit, named) | N5 | Fact rows (G1–G10): the cited source, as a citation. The *pinning* of the source reference — digest + dual locators — is Part II machinery and the index's, not Source's (Annex B §B4.3, §B6.6). |
| Description | ADOPT WITH DECLARED EXTENSION | N1, N6 | Every row. The extension, declared — Annex B §B1's rule: Description carries a human summary of what the thing *is*, and nothing else. A grade, an attribution class, or a gate outcome in Description prose is a defect in the record, because it recreates in prose exactly the claim-confusion v3 P8 forbids, uncheckably. |
| Subject | ADOPT (narrow binding) | N1 | Verdict and package rows: the matter examined, stated as the citation of the subject artefact — not free prose. No subject scheme is pinned by this spec; see Part 5, open question 10. |
| Coverage | ADOPT (Temporal refinement only) | N1 | Run rows: the run's span, where one exists (Annex B §B4.2). REFUSED USES, recorded: Coverage for a manifest chunk's line range (Annex B §B4.2 — Coverage names the extent of the content, not a locator within a parent artefact; the range rides in the index as a micro-locator); the Spatial refinement is NOT ADOPTED (no spatial extent is load-bearing for any current artefact). |
| Language | NOT ADOPTED | — | No current artefact kind needs a language distinction in its record. If multilingual artefacts ever enter the catalogue, this is revisited by addition (F1 discipline), not assumed now. |
| Rights | NOT ADOPTED | — | No rights or licence distinction among programme artefacts is load-bearing. FORECAST note only: external publication of shelf material would reopen this. |

### 2.2 Element refinements

| Refinement | Disposition | Need | Binds |
|---|---|---|---|
| Created (Date) | ADOPT | N4 | The artefact's governing creation date: freeze, run (minted at freeze-begin), chunk, call record (its `started_at_utc`), correction, obligation, question rows. |
| Issued (Date) | ADOPT | N4, N9 | Verdict rows (filing date) and package rows — the date the artefact entered the record, distinct from its drafting. |
| Modified (Date) | ADOPT (narrow binding) | N1 | Design and governance document rows only, where a pre-filing amendment is itself recorded. Filed artefacts are immutable; nothing else takes Modified. |
| BibliographicCitation | ADOPT | N2, N13 | See §2.1 — listed here as the refinement it is in DCMI Metadata Terms. |
| IsPartOf / HasPart | ADOPT | N5 | Package ↔ exhibits and preflights; archive ↔ manifest; ledger ↔ events (by locator); envelope ↔ its file set; REV5 → C1 (names the part — naming is not digesting; Annex B §B5.3). |
| IsVersionOf / HasVersion | ADOPT | N5 | The package line and the Stage 9 archive line (v2 IsVersionOf v1). |
| Replaces / IsReplacedBy | ADOPT | N5 | Package revisions (each revision Replaces the prior *as governing*; the prior remains filed history) — the standard home for Part II's supersession structure (e) (Annex B §B4.1). Read with EXON SUPERSEDE in Part 3: DC names the relation between records; SUPERSEDE names the act and its discipline. Neither restates the other. |
| References / IsReferencedBy | ADOPT | N5 | Verdict → package examined; call record → artefact examined; chunk → parent manifest; index rows for cited sources (IsReferencedBy — the source's row names what cites it, so resolution runs both ways, paper §2.4). |
| ConformsTo | ADOPT | N10 | Gate verdict records and format computations: the record ConformsTo the pinned Gate Format Definition (paper §3.2) and to the frozen schema object (K5/K12). |
| Provenance | ADOPT (partial fit, named) | N9, N12 | Correction and verdict rows: a *pointer* to the authority record (the delegation, the exhibits, the filing commit). DC's Provenance speaks of custody history significant to authenticity; authorisation provenance is adjacent to that meaning, not inside it (Annex B §B4.3). The pointer is adopted; the force stays in the authority record it points at. |
| Extent | NOT ADOPTED | — | No load-bearing need. The manifest entry counts of paper §3.5 are computed facts in gate records, not catalogue Extent values. |
| Medium | NOT ADOPTED | — | No physical-medium distinction exists among programme artefacts. |

### 2.3 Encoding schemes and the DCMI Type Vocabulary

| Scheme / term | Disposition | Need | Binds |
|---|---|---|---|
| W3CDTF (date encoding) | ADOPT | N4, N14 | All Date values. |
| IMT (media-type encoding) | ADOPT | N4, N14 | All Format values, plus the one declared local value of §2.1. |
| DCMI Type: Text | ADOPT | N3 | Documents, packages, verdicts, the freeze, corrections, obligations, questions, facts, criteria, defect rows — always paired with the §2.4 token, which carries the distinction Text cannot. |
| DCMI Type: Collection | ADOPT | N3 | Archive rows (the zip is an aggregation — Annex B §B4.1), envelope rows (an ordered file set), the defect register's own row. |
| DCMI Type: Dataset | ADOPT | N3 | Event-ledger, chunk, and call-record rows — data encoded in a defined structure. |
| DCMI Type: Event | ADOPT | N3 | Run rows — a run is a time-based occurrence (Annex B §B4.2). |
| DCMI Type: Software | ADOPT | N3 | Exhibited code artefacts when indexed as package parts (relay_call.py, the provider helpers) — the records that bind them by digest already exist in call records (paper §2.2). |
| DCMI Type: Service | NOT ADOPTED | — | REFUSED for the gate itself (Annex B §B4.2): a gate is a checkpoint work passes through, not a service callers invoke. The gate's *definition document* is Text; the gate has no DC row. |
| DCMI Type: Image, InteractiveResource, MovingImage, PhysicalObject, Sound, StillImage | NOT ADOPTED | — | No artefact of these kinds exists in the programme's inventory (paper §2.2), and none is forecast by name. Addition discipline (F1) governs if one ever appears. |

### 2.4 The citation form — specified as part of this adoption

From Annex B §B2.2, specified here as the adopted form
(subject to Ben's adoption ruling, Part 5):

```
<YYYY-MM-DD>/<type-token>/<slug>
```

- **Date** — the record's governing date, UTC. Citations
  sort and scan by date, as Ben's doctrine requires
  (paper §1.6).
- **Type-token** — from the closed local list of §2.5.
  This is the segment the old dated slugs lacked: they told
  a reader *when* and *what it was called*, not *what kind
  of thing it is*.
- **Slug** — short distinguishing words from the artefact's
  title, lowercase, hyphenated — the shelf's existing slug
  habit, retained. Where two occurrences would collide, the
  slug carries the discriminator by rule; run-01's existing
  labels slot in as slugs unchanged, absorbed by the form
  rather than re-minted (paper §2.3).

The citation is stored in the record's
BibliographicCitation and in the index's citation column;
it resolves through the index row to the Identifier
(fingerprint). It is a face. It is never parsed to recover
identity, and it never competes with the fingerprint
(Annex B §B2.2; Vane's point 2).

**Transition discipline** (N13): existing citations — the
pb-YYYYMMDD-… letter slugs, the dated filenames of REV1–8
and the verdicts — are historical citations. They remain
valid, are entered in the index as aliases resolving to
the same fingerprint row, and are never rewritten in the
documents that contain them. New artefacts mint new-form
citations at issuance. Whether *letter* citations also
migrate form is NOT settled by this spec — letters carry
the SS4 / registration context (paper §6 Q1–Q2) that
neither annex touches. Part 5, open question 6.

### 2.5 The local type-token vocabulary — the declared extension, specified

The closed list Annex B §B2.3 proposed, carried here as
the extension's membership (its pinning is package work —
Part 5, open question 2):

document · package · verdict · freeze · run · event ·
envelope · chunk · record · gate-definition · correction ·
obligation · question · fact · criterion · defect ·
archive

Seventeen tokens, one per §2.2 artefact row. Part 3 states,
token by token, which of these EXON's established vocabulary
can source and which it cannot — because F2 (EXON's later
taking-up) is served exactly to the extent that this list
rests on EXON's own words rather than on fresh coinage.

### 2.6 Dublin Core counts

Terms considered in §§2.1–2.3: 46 — the 15 DCMES
elements, 17 refinements (the 14 adopted below plus
Extent, Medium, and Coverage's Spatial), the 2 encoding
schemes (W3CDTF, IMT), and the 12 DCMI Type values.
ADOPT: 31 (elements 10; refinements 14; schemes 2; Type
values 5). ADOPT WITH DECLARED EXTENSION: 3 (Identifier,
Type, Description — all elements). NOT ADOPTED: 12
(elements 2 — Language, Rights; refinements 3 — Extent,
Medium, Spatial; Type values 7 — Service, Image,
InteractiveResource, MovingImage, PhysicalObject, Sound,
StillImage). The citation form of §2.4 is adopted as
specified, and the local type-token list of §2.5 is the
declared extension's membership. The row-by-row record
above governs over this summary wherever the two could
be read differently.

---

## Part 3 — Adopted from EXON

EXON is proposed as the source of the design's *local*
vocabulary: the type tokens Annex B had to label as
invention (§2.5), and terms for the gaps Dublin Core
declared (Annex B §B6). Each entry gives the EXON term,
its definition **as EXON's own documents give it** (quoted
or closely carried, document named), the need served, and
the design slot it fills. Where EXON has no term, the
entry reads NO TERM — INVENTION WOULD BE REQUIRED, and is
flagged for Ben. Nothing below puts words in EXON's mouth:
a candidate that had to be bent to fit is recorded as
refused, with the reason.

EXON sources cited: **Dictionary 0.4** —
`exon-dictionary-04.md` in the combined EXON folder (Part
III is its 38-term dictionary; Part II its schema layer,
generated from the adjudicated field matrix,
`EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md`);
**Dictionary 0.5 Supplement 01** —
`EXON-DICTIONARY-05-SUPPLEMENT-01.md` (draft entries
beyond 0.4); **Foundational Vocabulary** —
`EXON-FOUNDATIONAL-VOCABULARY-RECONCILED-DRAFT-01.md`
(nine reconciled terms, each marked proposed, not admitted
to the 0.5 inventory); **Dictionary Chart 0.1** —
`EXON-DICTIONARY-CHART-01.md` (the term inventory and its
admission discipline).

### 3.0 The governing concept — adopted for the whole token list

**ARTEFACT** — "An identifiable item of produced or held
content that can be referred to, transferred, accepted or
corrected as an object in its own right." Its FORM note:
identification and hash matching do not establish that the
artefact is correct, adequately supported or accepted —
EXON's own statement of the two-layer discipline.
*Source: Foundational Vocabulary, entry 7 (Dictionary —
proposed; not currently an entry in the Dictionary 0.5
inventory).* Need: N1, N2. Slot: the concept every §2.5
type token is a kind of. The token list is a list of
artefact kinds; ARTEFACT is what makes them one list.

### 3.1 The type tokens, one by one

**correction → CORRECTION.** "An authorised repair of an
established record or claim because it was wrong." The
entry carries a full field set (target and claim by
reference; wrong value; corrected value or withdrawn; the
authority shape — SELF-CORRECTION or ADJUDICATOR-CORRECTION,
never merged; reliance accounting; the original immutable,
visible, linked; repair append-only, including against
FROZEN records). *Source: Dictionary 0.4, Part III,
Messages and records.* Need: N1, N5. Slot: the *correction*
token — and more than the token: C1 is an EXON-shaped
correction in substance, and run-02's correction records
at gates (paper §3.6) take their field discipline from
this entry.

**record → RECORD.** "The durable, addressable account of
an act or observation, stored where the seats can retrieve
it. What is not in a RECORD did not happen, for the
purposes of commitments." *Source: Dictionary 0.4, Part
III, Messages and records.* Need: N1. Slot: the *record*
token — call records are accounts of invocation acts;
gate verdict records (§3.2(3)) are accounts of gate acts.

**freeze → FROZEN.** "Content fixed and hash-pinned; any
change creates a new artefact, never an edit." Boundary:
"frozen is not unquestionable — a FROZEN record may be
flagged (⚑) and repaired append-only by CORRECTION."
*Source: Dictionary 0.4, Part III, Outcomes and states.*
Need: N1, N11. Slot: the *freeze* token names the
artefact whose defining property FROZEN states; the same
term serves the state table (§3.3) and the audit baseline
of N11 — originals are FROZEN in exactly this sense.

**obligation → REQUIREMENT.** See §3.2 — the term fills
both the token and DC's largest gap, and is entered there
in full.

**gate-definition → GATE** (with a declared divergence).
"A release control point that evaluates whether an
identified artefact may pass a named release attempt."
Its schema values: gate_decision takes the closed values
ELIGIBLE or BLOCKED, attempt-scoped — "ELIGIBLE is not
RELEASED: permission is not the event." *Source:
Foundational Vocabulary, entry 2 (Dictionary — proposed;
not admitted to the 0.5 inventory); gate_decision as
schema vocabulary in Dictionary 0.4, Part II §G.* Need:
N10. Slot: the *gate-definition* token's source concept,
and the attempt-decision vocabulary for release-style
gates. **The divergence, declared:** EXON's GATE is a
*release* gate; Duenna's check-in gates (paper §3.6) sit
in the flow and return ALLOW or CORRECT — an outcome set
EXON does not have (see §3.3, final entry). GATE is
adopted as the source concept for what a gate *is*; the
ALLOW/CORRECT outcomes stand on Ben's ruling of
2026-11-20 19:52, not on EXON. The two gate concepts must
not be merged in the package's wording — flagged in
Part 5, open question 4.

**criterion → the criteria schema.** EXON has no
dictionary term CRITERION, but its schema layer — the
layer EXON itself distinguishes from dictionary language
(Dictionary Chart 0.1: "field names and enumerated values
that structure those meanings") — establishes the
criterion as a structured unit: criterion_id, an
enumerated criteria set, each criterion naming its
verification and expected evidence, and criterion_result
in the closed set {MET, UNMET, UNASSESSED} — MET:
"verification performed; expected evidence present";
UNASSESSED: "verification not yet performed."
*Source: Dictionary 0.4, Part II §C (from the adjudicated
field matrix).* Need: N10. Slot: the *criterion* token,
sourced from EXON's schema layer with the layer stated —
and the criterion_result values are adopted for
acceptance and gate records wherever per-criterion
results are recorded.

**defect → FLAG (⚑) and its block.** "An authorised
recording of a concern about an identified record,
artefact or claim, creating an independent obligation
for review and disposition." The flag block carries
target, claim (or the WHOLE_RECORD sentinel), attributed
concerns with their raisers, an independent review
owner, and review_disposition in {OPEN, CLEARED,
CORRECTED} — CORRECTED only with a correction_ref to an
existing CORRECTION record. *Source: Foundational
Vocabulary, entry 4 (Dictionary — proposed); the flag
block's fields in Dictionary 0.4, Part II §I and Part V.*
Need: N1, N8-adjacent. Slot: the *defect* token's
recording and disposition discipline. **The boundary,
stated:** a Duenna DR row is an attribution subject
(v3 K10) — an adjudicated record — while an EXON flag is
a review obligation that "obliges review but halts
nothing" and is "not CORRECTION." What is adopted is the
defect artefact's *recording shape and disposition
vocabulary* (a defect is recorded against exactly one
target, with attributed concerns and a disposition that
cannot close without its correction record); the K10
attribution record itself remains Duenna's own machinery
(§3.2, attribution).

**document → NO TERM — INVENTION WOULD BE REQUIRED.**
EXON's dictionary has no term for a document as a kind.
ARTEFACT (§3.0) governs it — a document is an artefact —
but no EXON word names the kind. The token *document*
stands as a plain programme word in the closed list, or
Ben rules otherwise. Flagged for Ben.

**package → NO TERM — INVENTION WOULD BE REQUIRED.**
COMMITMENT was considered: "A complete operative
undertaking or position established within an identified
scope under applicable authority" (Foundational
Vocabulary, entry 5, proposed). Refused: a relay package
is a *configuration* (v3 K3) — a governing artefact set —
not an undertaking or position; bending COMMITMENT to
cover it would blur exactly the authority vocabulary
Part 3 exists to keep clean. The token *package* stands
as a plain programme word. Flagged for Ben.

**verdict → NO TERM — INVENTION WOULD BE REQUIRED.**
Two candidates considered, both refused. RULING — "The
record of an authoritative decision by the seat holding
AUTHORITY for that matter" (Dictionary 0.4, Part III,
Authority and acts): a Gate 1 verdict is an *examination*
outcome; the programme's governance keeps examiner
(Gate 1), adjudicator (Gate 2), and Ben's authority half
distinct, and Vane's collaboration point 3 (20:30) names
the confusion to avoid — provenance is not authority,
classification is not verification. Filing her verdict
under RULING would dress an examination in authority's
clothes. RESULT — "A record of an outcome, with its
evidence and evidence class" (Dictionary 0.4, Part III):
refused from the other side — RESULT "reports only —
decides nothing, accepts nothing, authorises nothing,"
while a Gate 1 PASS has operative effect (execution may
proceed on it). Neither term fits without breaking its
own boundary. The token *verdict* stands as a plain
programme word. Flagged for Ben — this is the token
where the gap bites hardest, because verdicts are the
programme's most authority-sensitive artefacts (N9).

**run → NO TERM — INVENTION WOULD BE REQUIRED.** EXON's
records are full of runs (RESULT is a terminal *run*
report; attempt_events record gated runs), but no
dictionary or foundational term defines the run itself.
The token *run* stands as a plain programme word; v3 K1
supplies the identity discipline. Flagged for Ben.

**event → NO TERM — INVENTION WOULD BE REQUIRED.** No
EXON term names an event as a kind. (The schema's
attempt_events are fields, not a term.) The token
*event* stands as a plain programme word; v3 K9 supplies
the discipline. Flagged for Ben.

**envelope → NO TERM — INVENTION WOULD BE REQUIRED —
and a collision flagged.** The word ENVELOPE is
established EXON *schema* vocabulary: the envelope is
the field set riding every message (Dictionary 0.4,
Part II §A, "Envelope and identity"; EXON-COMMON-
ENVELOPE-DRAFT-01 in the combined folder). But the
design's envelope is a different referent — a handover
artefact, an ordered file set built for a step and a
recipient role (paper §2.2). Same word, different
conclusions — precisely the collision EXON's own
admission discipline exists to split (Dictionary Chart
0.1, §3: loose English that EXON must split where
conclusions differ). The EXON envelope is therefore NOT
adopted as this token's source. The token *envelope*
stands as a plain programme word, and the collision is
flagged for Ben: if both systems are ever read side by
side (F2), the two envelopes will need distinguishing
names in at least one system — that naming is Ben's,
in whichever system he rules it. Flagged for Ben.

**chunk → NO TERM — INVENTION WOULD BE REQUIRED.**
Nothing in EXON's dictionary, foundational vocabulary,
or schema layer names a derived slice of a parent
artefact. The token *chunk* stands as a plain programme
word; its discipline (derived slice, inherits the
parent's identity plus a range) is the design paper's
own (§2.2). Flagged for Ben.

**fact → NO TERM — INVENTION WOULD BE REQUIRED.** EXON
has no FACT term. Its claim machinery is real but
differently shaped: a claim is classified (Part II §H:
SUPPORTED / CONTRADICTED / NOT_ESTABLISHED /
UNTRACEABLE), not typed as a kind. The design's *fact*
token names a canonical claim record (v3 Part II (b)) —
Duenna machinery. What EXON supplies for facts is the
classification vocabulary, adopted in §3.3. The token
*fact* stands as a plain programme word. Flagged for
Ben.

**question → NO TERM for the kind — INVENTION WOULD BE
REQUIRED.** No EXON term names a question as a kind
(REQUEST — "An ask that transfers no authority and no
ownership," Dictionary 0.4 — was considered and refused:
Q1 is not an ask addressed to a seat; it is a recorded
open matter). What EXON supplies is the question's
*state*: UNRESOLVED, adopted in §3.3. The token
*question* stands as a plain programme word. Flagged
for Ben.

**archive → NO TERM — INVENTION WOULD BE REQUIRED.**
No EXON term names an archive or aggregation as a kind.
ARTEFACT (§3.0) governs it; DCMI Collection (§2.3)
describes it. The token *archive* stands as a plain
programme word. Flagged for Ben.

### 3.2 The gap terms — where Dublin Core declared it could not carry the load

**Obligation → REQUIREMENT.** "A bounded obligation
whose completion is decidable: condition, named
(versioned) verification, expected evidence." Its FORM:
"a REQUIREMENT message carrying all three." Its
boundary: "creates an obligation only when validly
authorised; permission is not obligation satisfaction;
a wish, however strongly worded, is not a REQUIREMENT;
≠ REQUEST." The schema layer adds the accountable
party: owner — "seat accountable for the obligation or
task," required, resolving to a registered seat
(Dictionary 0.4, Part II §F) — and the obligation's
failure behaviour (failure_action in a closed set).
*Source: Dictionary 0.4, Part III, Messages and records;
Part II §F.* Need: N7 — the need DC §B6.1 declared
inexpressible. Slot: Ob1 and every obligation record.
Ob1's three DC-missing parts map one-to-one: *owed* —
a REQUIREMENT validly authorised; *by whom / who owns
it* — the owner field; *to whom* — the commitment's
named beneficiary in the case (the one element
REQUIREMENT's field set does not name separately;
carried in the obligation record as the case states it,
not invented as an EXON field); *on what condition* —
condition + verification + expected_evidence, exactly
REQUIREMENT's FORM. COMMITMENT (Foundational
Vocabulary, entry 5, proposed) is adopted alongside as
the general concept: an obligation record is a
commitment in EXON's sense — identifiable by its
complete content and scope, replaced only whole, by a
successor naming its exact predecessor.

**Attribution → NO TERM — INVENTION WOULD BE
REQUIRED.** EXON's dictionary contains no attribution
term, and its classes (SYSTEM / MODEL / INPUT / UNKNOWN)
are v3 K10's, not EXON's. The gap is recorded precisely,
with the two nearest established items named so nobody
mistakes them for the term: (i) the claim-classification
value UNTRACEABLE — "the frozen procedure could not
trace attribution within exactly the pinned index +
manifest" (Dictionary 0.4, Part II §H) — attribution
appears there as something a procedure *traces*, inside
a classification value, not as a record kind; (ii)
per-concern attribution in the flag block — concern_id,
"one attributed concern," each with its raiser_id
(Dictionary 0.4, Part II §I) — attribution of *concerns
to raisers*, not of *failures to classes*. Neither is
stretched. The attribution record and its class
vocabulary remain Duenna's own (v3 K10), and this spec
adopts nothing from EXON for N8. Flagged for Ben: if
the attribution vocabulary is ever to be EXON-sourced
(F2), EXON would need a term it does not currently
have — an EXON-side decision, on EXON's own track
(Part 5), not something this spec can supply.

**Issuance → NO TERM — INVENTION WOULD BE REQUIRED.**
No EXON term names issuance — the act by which an
instrument is put into force by its issuer and bound to
that issuer. Two adjacents, neither stretched: REGISTER
— "To enter a task into the task registry by the
authorised registration act, producing an addressable
entry in a named registry version" (Dictionary 0.4,
Part III, Authority and acts) — an issuance-shaped act
for *tasks only*, its machinery recorded in EXON itself
as UNKNOWN (Gap 1); and RULING, the issued decision
record, refused for verdicts in §3.1 above. K7's
mechanism — the retained object and its issuance
fingerprint, invalid at any other instance — has no
EXON counterpart. N9 is carried by Duenna's own K7 and
by DC's Issued refinement (the *date* of issuance is
describable; the *act* is not). Flagged for Ben.

**State → the state vocabulary of §3.3.** DC holds no
state at all (Annex B §B6.4); the design holds state in
the ledger and routing columns (paper §2.4). The words
those columns speak are adopted from EXON in §3.3 —
the largest single EXON contribution to the design.

### 3.3 State, grade, and decision vocabulary adopted from EXON

Each term below passed EXON's own admission test
(Dictionary Chart 0.1): its presence, absence or change
alters what a reader is entitled to conclude. Slots are
the ledger, the index's routing columns, and gate
records — never the artefact's DC record (N6).

| Term | Definition (EXON's, document named) | Slot |
|---|---|---|
| FROZEN | "Content fixed and hash-pinned; any change creates a new artefact, never an edit." (Dictionary 0.4, Outcomes and states.) | Standing of filed artefacts and of the N11 audit baseline. |
| LIVE | "The currently operative version of a commitment: the version that governs action now." (Dictionary 0.4.) | Routing columns: which revision *governs* — the fact DC's Replaces names as a relation, stated as a standing. |
| UNRESOLVED | "A matter explicitly recorded as not decided, with no decision trigger specified: the matter stands open, awaiting a decision no occasion has been named for." Boundary: ≠ DEFERRED (postponement to a named occasion); ≠ UNKNOWN. (Dictionary 0.4.) | Q1's standing — Q1 has an owner and no named occasion, so UNRESOLVED is its exact state word, replacing the design's bare OPEN for questions. |
| CONTESTED | "Two records bearing on the same named matter disagree, and no adjudication has resolved them." (Dictionary 0.4.) | The standing of a matter under a K10 discrepancy before resolution — the evidence state, where K10's record supplies the machinery (resolution states UNRESOLVED / RESOLVED BY AUTHORISED DECISION / INDETERMINATE are v3's own). |
| UNKNOWN | "The named record or scope does not establish the matter. A statement about the record, never about the world." (Dictionary 0.4.) | The attribution class of last resort (shared with v3 K10) and the general not-established standing; never evidence of non-existence. |
| REPORTED | "Carried from another seat's statement, not reproduced by the carrier." Repetition never raises class. (Dictionary 0.4, Evidence and claims.) | Part II grade (c), lowest — the grade relayed content arrives at. |
| VERIFIED | "An independent check reproduced the claim from its evidence by a named method." (Dictionary 0.4.) Read with Ben's 2026-11-16 ruling (Dictionary 0.5 Supplement, reading flag 1): VERIFIED means researched and checked against its source. | Part II grade (c), middle. |
| HARDENED | "A grade above VERIFIED… HARDENED records that something beyond that base verification has also been established." Read under Ben's 2026-11-16 ruling: HARDENED means *proven*; the supplement's three promotion candidates are WITHDRAWN, and what constitutes proof remains the named open boundary. (Dictionary 0.5 Supplement 01, Part C §3, with its reading flag.) | Part II grade (c), terminal — the grade REFLUX admission presupposes (v3 Part II). The open boundary is carried to Part 5, question 7. |
| SETTLED | "The named matter has reached a recorded resolution and is no longer open for decision in that matter." Boundary: a resulting state, not the act; ≠ COMPLETE; "does not establish that an associated obligation is COMPLETE or discharged." (Dictionary 0.5 Supplement 01, Part A — draft status.) | The standing of a decided matter (a ruled question, a resolved discrepancy) in routing columns — distinct from an obligation's discharge, which SETTLED expressly does not assert. |
| REVIEW | "The recorded holding state for an item requiring a second look, without itself halting the operation… subject to its second-look obligation until that obligation receives its recorded disposition." (Dictionary 0.5 Supplement 01, Part C §1 — draft status.) | The holding state of an artefact returned at a gate under CORRECT (paper §3.6): work held for its second look, not halted as a run, not passed. |
| OPEN / CLEARED / CORRECTED | review_disposition values: "OPEN = non-terminal, no disposition yet assigned; CLEARED and CORRECTED are the ONLY terminal values; OPEN is never a disposition in the terminal sense and never implies resolution." (Dictionary 0.4, Part II §I.) | Dispositions of flag/obligation records — Ob1's standing is OPEN in exactly this sense until its disposition exists; CORRECTED only with its CORRECTION record. |
| ELIGIBLE / BLOCKED | gate_decision's closed values: "ELIGIBLE — the attempt passed the gate; BLOCKED — release was prevented at that attempt." Attempt-scoped only, never the run's outcome. (Dictionary 0.4, Part II §G; BLOCKED's dictionary entry, Outcomes and states.) | Attempt records at release-style gates — run-02's run-start gates (§5.1 of the paper) record attempts in exactly this shape. |
| MET / UNMET / UNASSESSED | criterion_result's closed values (Dictionary 0.4, Part II §C): MET — "verification performed; expected evidence present"; UNMET — verification performed, evidence absent or failing; UNASSESSED — "verification not yet performed." | Per-criterion results in acceptance records and in gate records wherever criteria are checked one by one. |
| PENDING | A disposition value for identified reliance awaiting its disposition, valid only with its pending_condition stated. (Dictionary 0.4, Part II §I, reliance_dispositions.) | Correction records' reliance accounting (with CORRECTION, §3.1): known reliance awaiting disposition is PENDING with its condition — never encoded as UNRESOLVED. |

**Two boundary entries, recorded so the table is not
misread:**

- **ALLOW / CORRECT have no EXON counterpart.** EXON's
  gate vocabulary is {ELIGIBLE, BLOCKED} for release
  attempts. Duenna's check-in-gate outcomes ALLOW and
  CORRECT are Ben's own ruled words (2026-11-20 19:52
  MST, MEMORY.md) — they stand on his authority and
  need no EXON source; this spec invents none and
  borrows none. NOT an invention-required gap: a
  ruling, not a vacancy.
- **UNEXAMINED has no exact EXON term.** Paper §3.3's
  UNEXAMINED names an item no verdict exists for
  because its call never landed (transport failure).
  UNASSESSED (above) is the nearest EXON value —
  "verification not yet performed" — and is NOT adopted
  as a substitute: a check not yet performed and a
  check that could not be delivered differ in what a
  reader may conclude (the first invites scheduling;
  the second is evidence about the transport), so by
  EXON's own admission test they are different words.
  UNEXAMINED stands as the design's word, coined in
  the design paper, flagged here for Ben — the one
  place this spec records a design-side coinage
  rather than an adoption.

### 3.4 Further EXON terms adopted, beyond tokens and gaps

**MECHANICAL** — "Performed by a deterministic procedure
with no judgement inside the step; inputs, outputs, and
the procedure's version are recorded." Boundary: "a call
to a worker is never MECHANICAL, however constrained its
prompt." *Source: Dictionary 0.4, Part III, Evidence and
claims.* Need: N10. Slot: the name of what paper §3.3's
format computation *is* — a format verdict is the output
of a MECHANICAL procedure under the pinned Gate Format
Definition, and gate records say so in this word. Its
boundary does the design a service: a participant model's
step-by-step evaluation is a worker call, hence never
MECHANICAL in itself — the *procedure* is mechanical,
and the record distinguishes the procedure from its
performer.

**VALID / MALFORMED** — VALID: "A message satisfies
every applicable FORM rule: structural, dictionary,
schema, cross-field, and reference checks, each in its
own layer… VALID is conformance, never truth."
MALFORMED: "A message fails VALID. It is not interpreted,
repaired, or partially honoured." *Source: Dictionary
0.4, Part III, Messages and records.* Need: N10. Slot:
the conformance vocabulary of gate format records — the
computed side of §3.3 speaks of conformance in these
words, and MALFORMED's no-partial-honouring rule is the
record-level form of §3.3's "an opinion is not a
verdict."

**REFERENCE** — "A pointer resolving to exactly one
record: an identifier, plus a hash where the target is
an immutable artefact. A description is not a
reference." And: "a resolving reference proves location,
never support, truth, or authority." *Source: Dictionary
0.4, Part III, Evidence and claims.* Need: N2, N5, N13.
Slot: the word for what a citation *does* — every
citation in the catalogue is a REFERENCE in this sense,
and its boundary sentence is Vane's examination point
stated in EXON's own words.

**EVIDENCE** — "The identified material a claim rests
on: resolvable references or a named observation record.
A claim without evidence is an assertion; an assertion
is not evidence." *Source: Dictionary 0.4, Part III.*
Need: N10, N12. Slot: gate verdict records and Gate 2
records name their supporting material as EVIDENCE in
this sense — with SUPPORTED ("The cited evidence, under
the frozen method for the claim type or by adjudication,
establishes the claim") and CONTRADICTED ("The
applicable frozen method, or an authorised adjudication,
establishes the named claim is false") and
NOT_ESTABLISHED ("the frozen procedure completed and did
not establish the claim") adopted alongside as the claim-
classification values for fact records (Dictionary 0.4,
Parts II §H and III) — the vocabulary in which a checker
re-derivation's per-fact results are stated (paper §5.1).

**ACCEPT** — "Formal acceptance of an artefact against
named criteria, by the seat holding AUTHORITY to accept
it." Full acceptance requires every criterion MET; the
accepted scope contains only MET criteria; decisions
ACCEPTED / PARTIAL / REJECTED under the §C-1 combination
rules. *Source: Dictionary 0.4, Part III, Messages and
records; Part II §C–C-1.* Need: N12, F1. Slot:
acceptance records — the relay's joints already record a
human acceptance after findings are revealed (design
freeze); run-02's acceptance records take ACCEPT's shape
and its criterion discipline (with §3.1's criterion
values), so an acceptance can never claim a scope its
criteria do not support.

**SEAT** — "A named, registered participant identity to
which messages, acts, responsibilities and authority may
be attributed." *Source: Foundational Vocabulary, entry
1 (Dictionary — proposed; not admitted to the 0.5
inventory).* Need: N9, N10. Slot: the word for the
identities gate records name — checker identity in the
verdict record (§3.2(3)), the obligation owner
(REQUIREMENT's owner "resolves to a registered seat"),
the correcting actor. Adopted at its proposed status,
flagged in Part 5, question 8.

**AUTHORITY** — "The recorded right of a named seat to
perform a named class of act within a named scope.
Originates with Ben; delegation transfers exactly what
it lists, nothing by implication." *Source: Dictionary
0.4, Part III, Authority and acts.* Need: N9, N12. Slot:
the concept DC's Provenance pointer points *at* — the
authority records (delegations, acceptances of office)
that verdicts and corrections cite. Adopted so that the
design's authority talk and EXON's are the same talk
when F2 arrives.

**SUPERSEDE** — "To replace a LIVE commitment wholly and
prospectively with an authorised successor naming its
exact predecessor… The predecessor remains in the
record." *Source: Dictionary 0.4, Part III, Authority
and acts.* Need: N5, N13. Slot: the act-discipline
behind DC's Replaces relation (§2.2) and Part II's
supersession structure (e): DC names the relation
between two records; SUPERSEDE states what kind of act
may create it — whole, prospective, predecessor named,
history never deleted.

### 3.5 EXON counts

Type tokens (§2.5's seventeen): sourced from EXON —
7 (correction, record, freeze, obligation,
gate-definition with declared divergence, criterion from
the schema layer, defect via the flag machinery). NO
TERM — 10 (document, package, verdict, run, event,
envelope, chunk, fact, question-as-kind, archive), each
flagged for Ben in §3.1. Gap terms (§3.2): obligation
sourced (REQUIREMENT, counted above); attribution —
NO TERM; issuance — NO TERM; state — sourced as the
nineteen-term vocabulary of §3.3, with UNEXAMINED
recorded as a design-side coinage and ALLOW/CORRECT as
Ben's ruled words needing no source. Further adoptions
(§3.4): 9 entries (MECHANICAL; VALID/MALFORMED;
REFERENCE; EVIDENCE with SUPPORTED / CONTRADICTED /
NOT_ESTABLISHED; ACCEPT; SEAT; AUTHORITY; SUPERSEDE;
and ARTEFACT in §3.0). Total NO TERM entries in Part 3:
12, every one flagged for Ben below.

---

## Part 4 — Not adopted, and why

### 4.1 From Dublin Core

- **Language** — no current artefact kind needs a
  language distinction (§2.1). Adopting it would be
  boilerplate: a field every record fills and no reader
  uses.
- **Rights** — no rights distinction is load-bearing
  among programme artefacts (§2.1). FORECAST only:
  external publication reopens it.
- **Extent, Medium** — no load-bearing need (§2.2).
  Entry counts live in gate records as computed facts,
  not in the catalogue as Extent.
- **Coverage (Spatial)** and **Coverage as a locator** —
  refused uses, not merely omissions: Spatial names a
  geography no artefact has; Coverage for a chunk's line
  range would file a locator as an extent (Annex B
  §B4.2). The range rides in the index as a micro-locator.
- **DCMI Type: Service** — refused for the gate
  (Annex B §B4.2): a gate is a checkpoint, not a service.
  **Image, InteractiveResource, MovingImage,
  PhysicalObject, Sound, StillImage** — no such artefacts
  exist in the inventory; not adopted against a
  hypothetical.
- **Audience** (a DCMI refinement Annex B considered) —
  refused for an envelope's recipient role: a protocol
  role is not an audience class, and borrowing it would
  be a forced field (Annex B §B4.2). Step and role ride
  in the index row and the envelope's tag.
- **Description as a carrier of state, grade, or
  attribution** — refused as a *use* (§2.1's declared
  extension): the one route by which every DC gap could
  be disguised in prose. Vane's point 1 (20:30) is the
  authority for the refusal: extend explicitly or name
  the gap — never disguise it.

### 4.2 From EXON

- **STOP** — "A recorded halt of a named operation, with
  a reason from the closed schema list and the condition
  for its release" (Dictionary 0.4). Not adopted: the
  design's gates do not halt operations — they ALLOW or
  CORRECT (paper §3.6) — and a run-level halt is a
  governance act recorded in the ledger under v3 K9, not
  a catalogue word this design needs. Adopting STOP
  would import a halt semantics the flow deliberately
  replaced.
- **DELEGATION and REQUEST as catalogue vocabulary** —
  both are message acts (Dictionary 0.4), and the
  catalogue sends no messages. The *records* of
  delegations are artefacts the catalogue describes
  (AUTHORITY, §3.4, is adopted for what those records
  establish); the acts themselves belong to the
  governance layer that already holds them (the
  delegation and acceptance records of record). Not
  adopted as design vocabulary.
- **RESULT as the verdict's source** — refused in
  §3.1 (verdict): RESULT decides nothing, and a Gate 1
  verdict has operative effect. RESULT's own outcome
  vocabulary (COMPLETED / INCOMPLETE / FAILED /
  EVIDENCE_FOUND / EVIDENCE_NOT_FOUND / NOT_DETERMINED,
  Dictionary 0.4 Part II §G) is likewise not adopted:
  run closure is a typed K9 terminal record with its
  own schema (v3), and importing a second outcome set
  would give closure two vocabularies — the duplicated-
  authority defect v3 P1 exists to prevent.
- **DISTILLATION / DISTILLED** — the Chart lists
  DISTILLATION as CONTESTED and DISTILLED as MISSING
  (Dictionary Chart 0.1); the 0.5 drafts carry
  DISTILLED as a comparison disposition. Not adopted:
  the design's distillation machinery is v3's own
  (Part II's derivation record and the REFLUX admission
  with its attested distillation record), already
  specified. Adopting EXON's contested candidate for
  the same neighbourhood would import an unsettled term
  into a settled mechanism.
- **ADOPTION and ALIGNMENT** (Dictionary 0.4) — terms
  for a worker's answer changing, or already agreeing,
  after exposure to an established answer. No design
  slot: the catalogue records artefacts and gates, not
  answer-convergence phenomena; both terms' instance
  status in EXON itself is recorded as UNKNOWN (no live
  event established). Not adopted.
- **DESTINATION** — the Foundational Vocabulary's own
  recommendation is "Retain Neither" (entry 8): EXON
  itself declines to promote it, since RELEASED already
  carries the operative meaning. Followed. Not adopted.
- **WAKE** — the Chart's recommendation is to keep it
  outside the dictionary as machinery vocabulary
  (Dictionary Chart 0.1 §4). Followed. Not adopted.
- **The ⚑ marker as a catalogue symbol** — the flag
  *machinery* is adopted (§3.1, defect); the marker
  itself is EXON schema representation, and the design
  records defects as DR rows and index entries, not by
  marking target documents. The marker stays EXON's.

### 4.3 PMEST

Not adopted — the whole borrowing. Ben's steer of
2026-11-20 20:19 ("a more less flamboyant one") set
Colon Classification aside in favour of the plainer
candidate, and Annex A stands preserved as the studied
alternative beside Annex B (Annex B §B9; memory/
2026-11-20.md L1065, L1067). Recorded without
relitigation, with its one unmatched property named so
the cost of the steer stays visible: PMEST *synthesises*
an address for an artefact kind nobody has catalogued
before, from first principles; Dublin Core produces no
address, and §2.4's citation form is a small programme
rule assembled from record fields (Annex B §B7). If F3
(growth beyond the relay) ever makes unseen kinds a
steady stream rather than an occasion, that is the
point at which the preserved Annex A earns a second
look — Ben's look, on his call.

---

## Part 5 — Boundaries, and what this spec could not settle

### 5.1 Boundaries

1. **Adoption is one-directional drawing.** This spec
   takes terms from EXON's documents into the Duenna
   design. It creates no obligation in the other
   direction: EXON's development stays independent
   (Ben, 2026-11-20 20:13 — EXON "can keep developing…
   independently while that's already established"), and
   nothing in this spec asks EXON to change a term, admit
   a term, or freeze anything. The NO TERM entries of
   Part 3 are gaps in *this design's* sourcing, recorded
   for Ben — they are not requests to EXON, and if EXON
   ever fills one, it will do so on its own track, by
   its own admission discipline, at Ben's call there.
2. **The spec pins; it does not chase.** Each EXON term
   is adopted as cited, from the document named, at the
   status that document carries (Part 3's status
   warning). If EXON later amends a term, the design's
   adopted meaning does not move with it; reconciliation,
   if wanted, is a separate recorded act. This is the
   same discipline the design applies to its own history
   (paper §2.5: indexed, never rewritten).
3. **Adoption changes no identity.** Nothing in this
   spec renames an artefact, re-mints an ID, or alters a
   filed record. The vocabulary governs records written
   from adoption forward and index rows written about
   the existing record (paper §2.4, §2.5).
4. **The spec is a draft.** It enacts nothing. Ben's
   approval governs it; Vane examines it as part of the
   package it binds into (alongside REV9); her Gate 1
   PASS remains necessary before anything executes, and
   Ben's separate execution word remains required after
   PASS plus prerequisites (REV9's recorded position,
   memory/2026-11-20.md L1073). EXON terms are adopted
   here as *sources for the design's vocabulary* — Ben's
   adoption of this spec does not admit anything into
   EXON's dictionary, which is his separate ruling on
   EXON's own track.
5. **Work from a copy.** When this spec is applied —
   in the package revision and in run-02 — the work is
   done from a copy of the materials, originals frozen
   as the audit baseline (Ben, 2026-11-20 20:33; N11).
   This spec itself was drafted without touching any
   source it cites.

### 5.2 Open questions — everything the spec could not settle from the record

1. **Formal adoption of Annex B.** This spec is written
   on Annex B as the operative direction (Ben's steers
   of 20:19–20:31; REV9 incorporates it), but the formal
   adoption ruling — Annex B, Annex A, or neither — is
   Ben's to confirm in package terms (Annex B §B8; REV9
   flags it as open). If Ben rules otherwise, Part 2 of
   this spec falls and Part 3's token sourcing must be
   re-pointed at Annex A's faces. *Owner: Ben.*
2. **The type-token list's exact membership.** §2.5
   carries Annex B's seventeen tokens as the proposed
   membership. Pinning the list — additions, removals,
   renames — is package-revision work, and REV9 records
   the type-token list's adoption as an examiner's item.
   *Owners: Ben (adoption), Vane (examination).*
3. **The twelve NO TERM entries.** Document, package,
   verdict, run, event, envelope, chunk, fact,
   question-as-kind, archive (tokens); attribution;
   issuance. Each stands in the closed list as a plain
   programme word unless Ben rules otherwise — by
   accepting the plain word, by directing a programme
   definition (which would be Duenna coinage, recorded
   as such, not EXON adoption), or by commissioning an
   EXON term on EXON's track. The spec recommends no
   silent filling, in any of the three directions.
   *Owner: Ben.*
4. **The two gates.** EXON's GATE (release; ELIGIBLE /
   BLOCKED) and Duenna's check-in gate (in-flow; ALLOW /
   CORRECT) share a word and differ in outcome set and
   position. §3.1 adopts GATE as source concept with the
   divergence declared; whether the package's wording
   keeps one word with two declared senses or splits the
   words is for the package revision, under examination.
   *Owners: the package revision, for Vane.*
5. **The envelope collision.** EXON's schema envelope
   (fields riding a message) and the design's handover
   envelope (an ordered file set) are different referents
   under one word (§3.1). Under F2 the collision becomes
   live the day EXON takes the system up. A distinguishing
   name in at least one system will be needed; which
   system renames is Ben's. *Owner: Ben, when F2 arrives.*
6. **Whether letter citations migrate form.** Untouched
   by this spec, as by both annexes: letters carry the
   SS4 / registration context (paper §6 Q1–Q2), including
   the unadopted PB-ID thesis and the exploratory
   Index-ID form. *Owner: Ben, on that evidence.*
7. **What constitutes proof for HARDENED.** Ben ruled
   the gloss (2026-11-16: HARDENED means proven; the
   three promotion candidates withdrawn) and the
   supplement records that "what constitutes proof
   remains the named open boundary." The design adopts
   the grade (§3.3) at that boundary's current position;
   REFLUX admission criteria that depend on the boundary
   inherit its openness (v3 Part II). *Owner: Ben.*
8. **The proposed-status EXON terms.** SEAT, GATE, FLAG,
   ARTEFACT, COMMITMENT are adopted from the Foundational
   Vocabulary, where each is marked proposed and "not
   currently an entry in the Dictionary 0.5 inventory";
   SETTLED, REVIEW, HARDENED come from the 0.5 draft,
   itself unadmitted. The design adopts them at draft
   status because the design is itself a draft — but
   when the package freezes its vocabulary, whether it
   may freeze terms their home system has not admitted
   is a question for Ben and for the examiner, not for
   this spec to pre-answer. *Owners: Ben, Vane.*
9. **Who performs the format computation in run-02.**
   Unchanged from paper §6 Q5 — orchestrator machinery,
   a participant-side tool, or both — with its G5
   independence consequences. §3.4's MECHANICAL entry
   names the computation's nature; it does not choose
   its performer. *Owner: the package revision, for
   Vane's examination.*
10. **Subject's vocabulary.** §2.1 adopts Subject with a
    narrow binding (the subject artefact's citation) but
    pins no subject scheme. If Subject use grows beyond
    verdict and package rows, a scheme must be pinned
    then, by addition. *Owner: the package revision.*
11. **application/jsonl as a Format value.** Declared
    as a local extension of the IMT scheme (§2.1). Whether
    the examiner accepts a declared local value inside a
    borrowed scheme — or requires the ledger's form to be
    recorded as text/plain with its structure in
    Description, Annex B's alternative — is hers to say.
    *Owner: Vane, at examination.*
12. **Part II's consolidated model.** Unchanged from
    paper §6 Q4: the model awaits the examiner's
    acceptance as a model. This spec adopts vocabulary
    *around* the model (grades, classifications,
    supersession) and settles nothing about the model
    itself. *Owner: Vane, as examiner.*

---

## Disposition

Adoption Spec, draft, 2026-11-20. Drafted under Ben's
commission of 20:34 MST inside the approved design stage.
It specifies what the design adopts from Dublin Core
(Part 2: 31 terms ADOPT, 3 ADOPT WITH DECLARED EXTENSION,
12 NOT ADOPTED, plus the citation form) and from EXON
(Part 3: 7 of 17 type tokens sourced, the obligation gap
sourced to REQUIREMENT, a nineteen-term state vocabulary,
9 further term adoptions — and 12 NO TERM entries,
flagged, none filled). It binds into the Relay 01
package alongside REV9. It enacts nothing: Ben's approval
and Vane's examination govern it, and the route of the
design paper's §5.2 and Annex B's §B9 is unchanged.
