# THE APPROVED POOL — A TERRAIRIUM SYNCHRONISATION AND READINESS MECHANISM

**Design paper — PROPOSAL ONLY.** Nothing in this
paper is implementation authorisation. It does not
authorise a freeze, replay, validator, or pilot.
Decisions reserved for Ben are listed in §11.

Origin: Ben's design, stated 2026-11-11 and carried
verbatim (§1). Developed in discussion: Ben (the
mechanism, the ledger, the ID grammar) · Alex
(structure, the release receipt, adjudication of this
paper) · Remmy (this draft, the evidence record).

**Revision 2 (2026-11-11):** §12 added — designated
extension points, on Alex's design addition, with
the retrieval results of §5 complete. Revision 1
(commit 41ec1e5) was shelved moments before the
extension-point addition arrived; this revision
supersedes it as the draft of record. Nothing else
changed.

**Revision 3 (2026-11-11):** Alex's six corrections
applied — retirement's tombstone becomes the head
(status RETIRED, never NONE); unknown type moved to
REQUIRED; generation allocation specified (§3.6);
the §3.3 STOP rule corrected in place (no reader
should have to reconcile an obsolete rule against a
later note); extension compatibility precedence made
explicit (§12); chunk identity distinguished as its
own tier with Ben's chunk requirement stated as
unmet by document-level IDs (§11).

## 1. Ben's wording, verbatim

The pool, in Ben's original words (carried by Alex,
pb-20261111-terrairium-approved-pool-discovery,
unedited):

> we need a mechanism like an approved pool that we can push to the shelf that syncs all the layers. if somethig between runs isnt on the shelf ad clearly we weret equipped to tell.. this could be our true savig grace.. ever do anythig if the source is even one run out of date. but other thigs depend o the source.. so it needs to do a full sweet, and be validated against facts

The ledger and the ID grammar, in Ben's words to
Remmy (chat, 2026-11-11, unedited):

> i think every appended chuk of verified informatio should have an id. we store that id on a master ledger. as the updated approved id is added to the shelf, it overrides its corrosponding older couterpard from the ledger. i thik my idea is clunky right ow but its o the right tracj

> the id has to corrospond to the type of work/iteration/date/somethig unique. it cant just be umbers. it has to be a determied format thats idexible ad recoginzeable to llms

## 2. Demonstrated failures (evidence, not motivation)

Each failure below is in the programme record. In
every case each component behaved correctly against
its own view; the failure lived between layers.

1. **Index vs Shelf (2026-11-10/11).** Crusher's
   index held 516 sections from 45 documents admitted
   before EXON existed: zero EXON documents, zero
   occurrences of "gate_decision". A week of retrieval
   questions about shelf-resident material returned
   UNKNOWN — honest about the index, repeatedly read
   as statements about the record. Ben diagnosed it
   in one word: indexing. Repaired by the governed
   admission of 2026-11-11 (516 → 1,156 sections;
   INDEX-ADMISSION-REPORT-01).
2. **Stale source, faithful build (2026-11-11).**
   Dictionary 0.4 was assembled from Dictionary 0.3's
   text, which was one ruling-generation behind:
   Alex's D03-06 disposition existed, but the carried
   text still closed the 0.2 self-flag by itself. The
   build propagated the staleness perfectly (finding
   D04-01). A stale source can be faithfully
   propagated through a perfectly executed build.
3. **Shorthand vs artefact (2026-11-11).** A
   materials letter characterised the V1 T05 arms in
   a compressed form the underlying records do not
   support in that phrasing; ground truth had to be
   re-established from the report, the driver source,
   and the results file (the locator-mismatch
   correction). A derived artefact drifted from its
   sources with no mechanism to notice.
4. **Standing sync debt.** The shelf snapshot sync
   record (ainternet-shelf.muse-github-snapshot-sync)
   stops at commit 7b9f785 while the shelf has
   advanced far past it; the corpus copy of the plan
   list is its 2026-11-10 morning freeze while the
   plan itself lived on. Neither staleness is visible
   from inside either layer.

## 3. The mechanism

### 3.1 The pool
The Approved Pool is the set of source artefacts
authorised as the working basis of TerrAIrium at a
moment. Membership is not residence: the Shelf holds
much that is not current (historical drafts, voided
records, superseded versions), all preserved, none of
it currency. The pool is the *approved subset*,
identified exactly.

### 3.2 The master ledger (Ben's mechanism)
Every appended chunk of verified information carries
an ID. IDs are recorded on a **master ledger**. When
an updated approved version is shelved, its ID
**overrides** the corresponding older counterpart in
the ledger. The ledger therefore always names, for
each logical item, exactly one current version. What
is current is a lookup, not an opinion.

Two identities per thing (the correspondence rule):
- **Item ID** — the stable slot; never changes.
- **Version ID** — one approved generation of the
  item. Shelving a new approved version moves the
  ledger's pointer for that item; the old version
  remains on the Shelf as history and holds no
  pointer.

Minting rule: a version ID is minted only for
**verified** information — verification and approval
precede the ledger entry, they do not follow it.
Unledgered material may exist on the Shelf; it is
not consumable as current by any layer.

### 3.3 The ID grammar (Ben's requirement)
Determined format; indexable; recognisable to LLMs;
each segment one job.

- Item ID: `WORKSTREAM-TYPE-ITEM`
  e.g. `EXON-DOC-DICTIONARY`
- Version ID: item ID + `-GEN<nn>-<YYYYMMDD>-<hash6>`
  e.g. `EXON-DOC-DICTIONARY-GEN04-20261111-0717BB`
  (0717BB is the first six of Dictionary 0.4
  Revision 3's sha256 — the readable name and the
  cryptographic pin in one string).

Segment jobs: the **generation counter** carries the
ordering claim; the **date** is informational only,
never proof; the **hash tail** carries integrity.
The disagreement rule, stated once and governing
everywhere: **generation disagreement with the
ledger is a STOP; full-digest disagreement with the
ledger is a STOP; date disagreement is metadata
drift — recorded, and never used to infer
ordering.**
Type vocabulary (proposed closed starter set, for
ruling): DOC document · SPEC specification · DATA
record set/results · CODE harness/tool · RPT report ·
MAN manifest · LED ledger/register.

Consequence: staleness becomes visible in text. Any
artefact citing GEN03 where the ledger says GEN04
flags itself to any reader, model or human, without
a tool.

### 3.4 Generations and receipts
A **generation** is a numbered snapshot of the
ledger: the full item → version mapping at a moment,
itself hashed and shelved. A **release receipt** is
issued for every successful synchronisation,
recording: the generation identifier; the pool
manifest and source hashes; the dependency graph and
required versions; validation results and their
evidence; which components synchronised; which failed
or remain stale; outstanding UNKNOWNs and conflicts.

Pool generation ≠ consumed generation (Alex's
distinction, adopted): a component's own receipts
identify the pool generation it consumed AND any
earlier pinned artefacts it legitimately retains. A
historical evaluation stays pinned to the generation
it evaluated; it is not silently re-based.

### 3.5 Distinctions adopted on Alex's review
From pb-20261111-doc-id-ledger-addendum-response,
adopted into this draft:

1. Item ID and version ID are separate identities.
   Advancing the head never overwrites or erases a
   previous version.
2. The ledger is authoritative for current status.
   A version ID identifies an artefact; it does not
   by itself prove approval. The ledger entry
   establishes verification, approval, and headship.
3. Item generation ≠ pool generation. GEN⟨nn⟩ is the
   item's own revision sequence; a pool generation
   is one snapshot of all heads, and may deliberately
   pin some dependencies to older item versions.
4. **Correction to §3.3, Alex's:** the date is
   informational metadata. Generation and the full
   content hash are checked against the ledger; a
   date disagreement is recorded as metadata drift,
   never treated as a competing ordering claim. (The
   draft's three-way STOP rule is narrowed
   accordingly: STOP attaches to generation or hash
   disagreement.)
5. The ledger retains the FULL digest of every
   version. The six-character tail is recognisability
   only, never a sufficient integrity check, and a
   collision or disagreement is never resolved by
   choosing the plausible-looking value.
6. The override is the critical operation and its
   machinery DOES NOT EXIST yet (Gap 2, §5). The
   paper specifies the required behaviour — a single
   atomic check-and-advance; two approvals racing
   the same item produce a detected conflict, never
   a silent overwrite — without claiming it is built.
7. The type vocabulary is closed and governed: each
   type carries a boundary definition, additions
   follow a named process, and similarity between
   types implies nothing.

A further condition (Alex's): the visible GEN
mismatch warns only if dependent artefacts record
the exact version ID they consumed AND the ledger
snapshot they were evaluated against. The identifier
makes staleness legible; the dependency record makes
it machine-checkable. Both are required.

### 3.6 Generation allocation (Alex's correction 3)
The counter's rules, specified: generation numbers
are **unique within an item** and **monotonically
advancing**. A number is allocated when a version is
proposed, not when it is approved — so two competing
successors to the same predecessor each hold their
own number, and only the atomic override decides
which becomes head; the loser remains recorded,
visible and non-operative, and must never silently
become current. A proposed version that is rejected
or abandoned **consumes its number permanently**:
numbers are never reused, because a reused number
would let two different contents answer to one
version stem. Gaps in an item's accepted sequence
are therefore normal and are explained by the
ledger's candidate history (§10's skipped-generation
rule states the same from the reader's side).

## 4. Dependency declarations and graph ownership
Each layer declares its own dependencies: which items
it consumes, at which version IDs, evaluated against
which ledger snapshot. Declarations are pool
artefacts — versioned, inspectable, themselves
ledgered items. The dependency graph is the union of
the declarations; it is owned by the pool, not by
any layer. Generation zero — the first declarations
and the first ledger — is declared by Ben as an
initial authority decision, recorded as such, never
disguised as an automatically verified fact.

## 5. What already exists (retrieval, 2026-11-11)
Checked before designing over old ground, per Alex's
request. Crusher answers are in Remmy's return
letter verbatim; summary of the established state:

- **Gap 2 (atomic live-head update)** —
  exon-infrastructure-gap-register#003. Status
  UNKNOWN. Its "machinery required" list is, in
  effect, the specification this paper's override
  must meet: one authoritative head per chain; a
  single atomic operation checking the expected
  predecessor; a deterministic conflict result;
  losing successors preserved as visible,
  non-operative records; read-after-write
  confirmation of the new head. The ledger does not
  close Gap 2 by being described; it closes when
  that machinery exists and is independently tested.
- **Gap 3 (concurrency)** — the same register, #004,
  UNKNOWN. Compare-and-set language appears in the
  corpus only inside Gap 2's machinery list. No
  established concurrency mechanism exists.
- **Gap 4 (supersession/reliance)** — #005:
  partially evidenced, general policy UNKNOWN.
  Dictionary fields (supersedes, task_registry_ref,
  hash chains) are design, explicitly not capability
  claims (exon-dictionary-03-reconciliation#008).
- **No "master ledger" exists in the corpus** (exact
  scan: zero sections) — Ben's term and mechanism
  are new. The nearest living relative is
  BridgePress's serial ledger: serials extracted
  from the artefacts themselves, ledger generated
  from the shelf — a working single-purpose instance
  of the pattern, outside the retrieval corpus.
- **No competing generation/manifest convention**
  was retrieved or found by scan. Absence labelled
  as a scan result, not proof.

## 6. Factual validation, by dependency class
A hash proves identity and integrity, not factual
correctness (Alex's line). The sweep's checks are
enumerated per class in advance; each check names
its source, method, expected relationship, result.

- **Documents/dictionaries:** hash identity against
  the ledger; status claim against the challenge
  record (a dictionary is "current" only if its
  ledger entry and its review state agree).
- **Indexes:** integrity verification recomputed
  (the corpus verify); coverage assertions (every
  pool document present; named field-strings counted
  — the gate_decision 0→73 test is the template).
- **Schemas/definitions:** version pinned in the
  consuming component's declaration must equal the
  ledger head, or be an explicit historical pin.
- **Harnesses/code:** fixture-suite results pinned
  by artefact hash; a harness whose results artefact
  is not the ledger version is stale by definition.
- **Derived artefacts** (summaries, letters,
  shorthand): spot claims re-derived from sources —
  the class that failed in §2, failure 3; the check
  is re-derivation, not re-reading.

## 7. Partial synchronisation and failure behaviour
A sweep may partially succeed. The receipt records
exactly which components are current, at which pool
generation, and which remain stale, at which older
one. No layer may report the environment as current
because it received an update. A failed component
keeps its last-good generation, visibly. Work that
depends on a stale component is blocked for that
dependency only; unrelated work proceeds (Ben's
dependency-aware qualification, not blanket
invalidation).

## 8. The readiness gate
Before a task that consumes pool material — a
battery, a replay, a build, a review — a sweep
receipt for the current pool generation must exist
and be clean for the components and dependencies
that task touches. The gate's claim is scoped: a
clean sweep proves readiness for the declared scope
and generation only, never for all of TerrAIrium
(Alex's distinction). In Duenna's shape this is a
pre-flight obligation with a verification, not a
posture.

## 9. Freeze and bootstrap sequencing — Ben's call
The design paper describes both; it selects neither.

**A. Pool first.** The mechanism is designed,
reviewed, and generation zero declared; the freeze
of Dictionary 0.4 becomes the first ledgered
generation event, receipted like any other.
Consequence: the freeze waits for the design to
settle; the dictionary's first currency is
machine-witnessed from birth.

**B. Freeze as generation zero.** Ben freezes 0.4
by hand now; the pool, when built, inherits the
frozen dictionary as its declared starting state.
Consequence: the dictionary is usable sooner; its
initial currency rests on a manual declaration
(like every generation-zero fact), and the pool's
first sweep must verify the inheritance rather than
assume it.

Either way, generation zero is an authority
decision by Ben, recorded as one.

## 10. Foreseeable cases — the design principle (Alex's)
**Design rule: identify foreseeable cases; classify
them; make the default behaviour explicit.** Three
classes: REQUIRED (defined behaviour before any
implementation), OPTIONAL (may be inspected or
ignored unless they arise — but each carries a
*recorded default disposition*, so silence is never
mistaken for a decision), OUT OF SCOPE (genuinely
speculative; recorded, and not allowed to burden
the design). We design for resilience, not for every
imaginable possibility.

Initial candidate register (Alex's set, classified
here for adjudication; not frozen, not exhaustive):

REQUIRED:
- New approved version → advance the item's head.
- Historical version referenced → permitted only
  when explicitly pinned as historical.
- Unledgered material → not consumable as current.
- Two approvals race → conflict detected; no silent
  overwrite; losing successor preserved visibly.
- Same ID, different content → rejected as an
  identity/integrity conflict.
- Generation skipped → allowed only if the ledger's
  history explains the skip.
- Dependency points to an old version → flagged
  stale unless the historical pin is intentional
  and declared.
- Ledger unavailable → no claim of current status
  may be made by anyone.
- Partial synchronisation → receipt reports exactly
  which components are current.
- Ledger corruption or conflicting heads → affected
  operations stop pending reconciliation.
- Type unknown → quarantined pending classification;
  not consumable meanwhile. A safety invariant, not
  a convenience: a type cannot become consumable
  merely because nobody has classified it yet.
  (Moved here from OPTIONAL on Alex's correction.)

OPTIONAL (default dispositions recorded):
- Date differs from the ledger's record → metadata
  drift, logged; ordering never inferred from it.
- Item retired with no successor → a tombstone
  record is minted as a version of the item and
  BECOMES its head, with status RETIRED and no
  active successor; the chain remains addressable.
  (Head is never NONE: Gap 2 requires one
  authoritative head per chain. Corrected on Alex's
  review.)
- Item splits or merges → new item IDs minted; the
  old item's head points to a SPLIT/MERGE record
  naming the successors. (Added here.)
- Workstream renamed → item IDs immutable; the alias
  lives in prose, never in the grammar. (Added here.)

OUT OF SCOPE (recorded, not designed for):
- Forgery of ledger entries by a credentialed seat —
  a security incident with its own handling, not a
  synchronisation case.
- Federation of ledgers across organisations.

## 11. Open questions and decisions reserved
**Reserved for Ben:** the freeze itself; §9's
sequencing choice; the generation-zero declaration;
the type vocabulary's adoption and its addition
process; where the ledger physically lives (a shelf
artefact is proposed; alternatives open); who may
mint (the adjudication roles are proposed; the
authority is Ben's to grant).

**Open design questions:** sweep triggers (on
change, pre-flight only, or both); receipt retention
and where receipts are ledgered; the exact atomicity
mechanism for the override, which is Gap 2's
machinery and remains to be built and independently
tested before any FORM claim.

**Chunk identity (Alex's correction 6).** Three
identity tiers must stay distinct: document/item
identity, version identity, and section/chunk
identity. Ben's original requirement is at the chunk
tier — "every appended chunk of verified
information" — and document-level IDs do NOT by
themselves satisfy it; this paper does not claim
otherwise. The corpus index already mints section
identities (section_id, per-section sha256, chain
hashes). The open design task is to investigate
governing those existing section identities under
this same identity model — item, version, head —
rather than inventing a competing scheme.

**Closing honesty:** everything in §§3–10 is a
proposed mechanism. What exists today is: a shelf,
an index that can now see it, a dictionary that has
passed challenge, and a written record of the ways
they fell out of step. The pool is the proposal to
make the record keep itself.

*End of design paper — proposal only.*

## 12. Designated extension points (Alex's addition)
**Principle: the architecture anticipates change
without pretending to know what the changes will
be.** New types, dependency classes, validation
rules, edge cases, synchronised components, and
metadata will be discovered; the system should not
need its plumbing rebuilt each time. So the design
reserves explicit extension points now, activated
later — a placeholder is a defined socket, not an
unrestricted blank field.

Every extension point carries, from its reservation:
1. A reserved location and identifier.
2. A declared purpose and permitted data shape.
3. A compatibility rule for components that do not
   recognise it.
4. An activation process requiring registration,
   validation, and approval.
5. A rule that an unrecognised extension never
   silently changes current behaviour.

Candidate extension points:
- **Identifier and type categories** — new
  workstream or type values enter only through the
  governed addition process (§3.5, point 7).
- **Validation rules** — new sweep checks register
  against a dependency class without altering the
  ledger's identity model.
- **Dependency classes** — new declaration shapes
  for new kinds of dependency.
- **Synchronised components** — a registration
  mechanism by which a new layer joins the pool
  (declares its dependencies, its consumed-
  generation stamping, its receipt format) without
  redesigning the process.
- **Edge-case classifications** — the §10 register
  is itself an extension point: new cases enter
  with a classification and a default disposition.
- **Versioned metadata** — optional fields under a
  versioned extension namespace; unknown fields are
  handled predictably: preserved, ignored for
  behaviour, and recorded.

Failure rule, with its precedence made explicit: a
component encountering an extension it does not
understand may preserve and ignore it **only when
the extension is genuinely inert to that
component**. Where an extension affects a required
dependency, an authority decision, or a required
validation result, the component **fails closed** —
that precedence overrides the preserve-and-ignore
default in every case. Reserved capacity is not
implemented functionality: an extension point's
existence claims nothing about what will fill it,
and activation is a separate, approved event.
