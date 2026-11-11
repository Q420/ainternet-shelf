# APPROVED POOL — IDENTITY AND GOVERNANCE SPECIFICATION 01

**Status:** PHASE 1 TECHNICAL CONSOLIDATION — BEN'S GOVERNANCE DECISIONS REQUIRED  
**Prepared by:** Alex  
**Date:** 2026-11-11  
**Authority:** Adopted Approved Pool Implementation Plan 01; Phase 1 issuance `pb-20261111-phase-1-issuance`  
**Source reconciliation:** Remmy, Phase 1 Reconciliation Pack 01, commit `6379f60`, blob `c2b9e4f88396c8142569ebd1be69494188e5f9ac`  
**Scope:** Identity and governance specification only. No ledger, allocator, index migration, validator, synchronisation mechanism, or authority registry is implemented or authorised by this document.

---

## 1. Purpose and outcome

This specification consolidates the technical identity model required by the Approved Pool and separates that model from the governance choices reserved to Ben.

The system must be able to answer, without relying on a model's interpretation:

1. What logical thing is this?
2. Which approved version of that thing is being referenced?
3. Which exact chunk or section of that version is being referenced?
4. Which ledger entry establishes that version as approved and current?
5. Which pool snapshot did a consumer use, and which historical dependencies did it intentionally retain?
6. Who was authorised to mint or advance each identity, and under which recorded authority?

The specification preserves the distinction:

- **Item identity** identifies a stable logical slot.
- **Version identity** identifies one immutable approved version of that item.
- **Chunk identity** identifies a specific information unit within a specific version.
- **Pool generation** identifies an immutable snapshot of the ledger's item-to-version heads.
- **Consumed generation** records the snapshot a component actually used; it is not inferred from the latest pool generation.

No one identifier substitutes for another.

## 2. Governing principles

1. Identity is not authority. A well-formed ID does not prove approval, truth, or permission.
2. A hash proves byte/content identity under a specified canonicalisation rule; it does not prove factual correctness.
3. A ledger head, not a plausible-looking ID or a document's own prose, determines current status.
4. Old versions and chunks remain addressable as history. Advancing a head does not overwrite history.
5. A consumer must identify both the exact version it used and the pool snapshot against which it resolved current dependencies.
6. Existing identifiers are not silently reinterpreted. Migration must preserve old locators and provide explicit mappings.
7. Retrieval UNKNOWN is not proof of non-existence. Evidence classes remain explicit.
8. FORM validation and MEANING adjudication remain separate. Mechanical resolution cannot create authority or establish substantive truth.

## 3. Evidence base and inspection limits

### 3.1 Remmy's source inspection [SI: Remmy]

The Phase 1 Reconciliation Pack 01 (commit `6379f60`, blob `c2b9e4f88396c8142569ebd1be69494188e5f9ac`) reports direct inspection of:

**Index machinery**
- `pulse-bridge/index/build_index.py` — SHA256 `5423df78207bbc8730bbc2831eb89a2cd195e5ffabe92c9a23b5ea21c5569481`
- `pulse-bridge/index/manifest.json` — SHA256 `c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452`
- `pulse-bridge/index/admit_2026_11_11_exon.py` — SHA256 `5d46b13bed1c8731d30a94e04717dc6f439bdedffe5177a499b0d9f3cf79ee50`

**BridgePress**
- `shelf-publisher/registry.json` — SHA256 `6f5b5b30ad9a5c050795cd3767d3cb2c9944177a6c9d3c031638544cb6adc061`
- `shelf-publisher/CONTRACT-PHASE2-2026-11-09-v3.4.md` — SHA256 `13bfbbf56794b634117847a2717431f59b8fc4fb38cbd2af8d38f551209b755f`
- `shelf-publisher/SERIAL-LEDGER-DESIGN-2026-11-09.md`
- `shelf-publisher/EVIDENCE-SERIALS-IMPL-2026-11-09.md`, §13.5

The above pins and descriptions are attributed to Remmy's source inspection. Alex has inspected the reconciliation pack itself and the related approved design paper and plan; Alex has not independently re-opened Remmy's local workspace files in this review. Therefore the code/registry mechanics below retain the attribution [SI: Remmy], rather than being presented as Alex's direct source inspection.

### 3.2 Crusher retrieval [CR: Crusher, harness v2.2]

Two verbatim queries were run against Crusher v2.2:

- Exact index identity fields and generation/retention rules.
- Exact BridgePress v3.4 serial allocation, ledger location, identity target and revision stability.

Both returned: **UNKNOWN — the corpus does not say.**

The nearest sections were listed in the reconciliation pack. This is a coverage result: the indexed corpus contains neighbouring programme artefacts but not the implementation mechanisms reported in Part A and Part B. It is not evidence that the source mechanisms do not exist. The retrieval result is retained unedited in the pack and does not override the source-inspection evidence.

Remmy reports live v2.2 usage accounting after the calls: 6,967 known tokens. This is reported accounting, not independently reconciled here.

## 4. Existing identity mechanisms

### 4.1 AInternet Shelf index [SI: Remmy]

The current index records each chunk with:

`section_id, doc, seq, heading_path, chars, sha256, chain_sha256, embed_text, text`

The build process is reported as follows:

1. Canonicalise source text using CANON-1.
2. Verify the raw file SHA256 against the admission register; halt on REGISTER MISMATCH.
3. Compute the canonical document digest (`canonical_sha256`), distinct from raw `file_sha256`.
4. Split by heading ranges.
5. Assign `section_id = <doc_id>#<seq:03d>`, with sequence local to the document.
6. Apply S1 subdivision to sections over 3,500 characters. Exact line slices receive letter suffixes; the effective chunk ID is the section ID plus suffix. For non-subdivided sections, section ID is also chunk ID.
7. Compute per-chunk SHA256 over exact canonical chunk text, with LF-terminated lines.
8. Build a per-document chain: seed with canonical document digest; for each chunk in order, hash the prior chain value concatenated with that chunk's hash as text. Manifest records the final chain hash.

The manifest records CANON-1, subdivision rule, per-document source path, raw file digest, canonical digest, section/chunk counts, final chain hash and total chunk count. The inspected state reported 79 documents and 1,156 chunks.

For JSON admissions, one section is created per run record plus document-level sections. JSON Pointer source locators are retained; fields are not flattened or discarded. The VOID V2 battery result JSON was excluded under the admission rule, with VOIDED.md admitted instead.

Retention is reported through `sections.jsonl`, `manifest.json` and dated pre-admission backups. The original 45-document canonical digest was reported unchanged across the 2026-11-11 admission.

**Critical limitation:** this index has chunk identity only. Its chunk identity is positional and content-derived. If a source document changes, sequence numbers, suffixes and the document chain may change. There is no item tier, version tier, or authoritative head pointer in the index today. The index's current identifiers must not be promoted into stable item/version identifiers by assumption.

### 4.2 BridgePress v3.4 serials [SI: Remmy]

BridgePress used a sequential `BP-<nnnn>` serial allocated from one registry counter. The registry associated each serial with a document ID, issue time, state and page ID. The document record separately pinned source reference, source hash and content hash.

The workflow was: approve the document; append its allocated serial to the approved file; upload; extract the serial from the uploaded file; derive the ledger from the extracted source. The registry was the working allocation record. The published WordPress Serial Ledger page was a derivative of the uploaded files' extracted serials, not the source of truth.

Two states were distinguished:
- **assigned:** allocated and reserved in the registry, but not yet physically carried in the artefact (legacy BP-0001…BP-0004);
- **carried:** physically present in the uploaded file and extracted on upload (BP-0005…BP-0012).

Under contract §13.5, reusing the same serial and kind with a different hash stopped the run and left the ledger untouched. A revised document issued under a new document ID received a new serial. This mechanism therefore provides a useful document-publication analogue: sequential allocation, content-bound identity and extraction from the artefact rather than trust in a manually maintained ledger.

Its limits are equally important: it is document-tier only; it does not provide separate item/version/chunk tiers, concurrent allocation, cross-store head control, or a general dependency graph. Its single-publisher sequential operation does not prove concurrency safety for the Approved Pool.

## 5. Required identity model

### 5.1 Tier 1 — Item ID (stable logical slot)

An Item ID names the enduring logical object whose versions may succeed one another.

Requirements:
- Stable across revisions, content changes, reformatting and location changes.
- Never derived solely from current content.
- Never reused for a different logical object.
- Has one authoritative current-head pointer at a given ledger snapshot, except when explicitly retired or unresolved under an authorised rule.
- Does not itself assert that any version is approved or current.

Candidate readable grammar from the adopted design paper:

`<WORKSTREAM>-<TYPE>-<ITEM>`

Example only: `EXON-DOC-DICTIONARY`.

The grammar is a candidate, not yet a Ben-approved vocabulary. The physical ledger location and minting authority remain reserved decisions.

### 5.2 Tier 2 — Version ID (immutable approved generation)

A Version ID identifies one immutable content version of one Item ID.

Requirements:
- Bound to exactly one Item ID.
- Bound to the full cryptographic digest of the canonical content and the canonicalisation/versioning rules used.
- Minted only after the required verification and approval have occurred.
- Never reused, even if a version is abandoned, rejected, superseded or retired.
- Does not itself prove approval or current status; the authoritative ledger entry establishes those facts.
- Historical versions remain addressable and immutable.

Candidate grammar from the adopted design paper:

`<ITEM-ID>-GEN<nn>-<YYYYMMDD>-<hash6>`

Example only: `EXON-DOC-DICTIONARY-GEN04-20261111-0717BB`.

The generation number carries the ordering claim. The date is informational metadata only. The six-character digest tail is a human-recognition aid, not an integrity check. The ledger must retain and compare the full digest. Generation or full-digest disagreement with the authoritative ledger is a STOP condition; date disagreement is recorded as metadata drift and must not determine ordering.

Item generation and Pool Generation are distinct. A pool snapshot may intentionally pin an older version of a dependency.

### 5.3 Tier 3 — Chunk ID (stable identity of an information unit)

The index's present `section_id` is a locator/positional chunk identity within a document build, not a durable cross-version chunk identity. It must be preserved as a legacy/index locator and must not be silently relabelled as a stable Chunk ID.

Required distinction:

- **Stable Chunk ID:** identity of a logical information unit across versions where continuity is explicitly established.
- **Chunk Version ID (or version-scoped chunk reference):** identity of the exact content of that chunk in one parent Version ID.
- **Index locator:** current retrieval address such as `section_id`, document slug, sequence, suffix, JSON Pointer and manifest reference. It may change when the source is rebuilt or re-admitted.

A chunk reference consumed by a process must resolve to:
1. Item ID;
2. exact parent Version ID;
3. stable Chunk ID, if continuity is established;
4. exact chunk-content digest;
5. canonicalisation and chunking rule versions;
6. one or more current or historical index locators;
7. source provenance and, for JSON-derived material, JSON Pointer locator.

**Continuity rule:** same text or same hash does not automatically prove same logical chunk; a changed text or hash does not automatically prove a new logical chunk. Identity continuity is a governed mapping decision supported by provenance and explicit change classification. If no defensible mapping exists, mint a new Stable Chunk ID and record the predecessor/successor relationship; do not guess.

### 5.4 Tier 4 — Pool Generation

A Pool Generation is an immutable snapshot of the full Item ID → Version ID head mapping and its required metadata. It is not an item version and not a document version.

A component's consumption receipt must record:
- the Pool Generation it resolved;
- exact item/version pins actually consumed;
- intentionally retained historical dependency pins;
- dependency-closure result and any UNKNOWN/conflict;
- component identity and version;
- validation/consumption evidence.

A later pool generation does not silently rebase a historical evaluation.

## 6. Mapping the existing index to the proposed model

| Existing index field/artifact | What it establishes today | Proposed treatment |
|---|---|---|
| `doc` / `doc_id` | Document slug / source identity within index machinery | Candidate source locator and possible Item ID input; not automatically the governed Item ID |
| `section_id` | Positional section/chunk address; may include S1 suffix | Preserve as legacy/index locator |
| `seq` | Per-document build sequence | Locator metadata only |
| `heading_path` | Structural context | Descriptive metadata, not identity |
| `sha256` | Exact canonical chunk-content digest | Retain as chunk-version content pin |
| `chain_sha256` | Per-document ordered integrity chain | Retain as document/index-build integrity evidence; not item/version identity or authority |
| `canonical_sha256` | Canonical whole-document digest | Candidate content pin for a document version, subject to canonicalisation version |
| `file_sha256` | Raw source-file digest | Source-byte integrity pin; distinct from canonical content digest |
| `JSON Pointer` | Locator into an admitted JSON source | Preserve as source locator; not chunk identity |
| `manifest.json` | Index build/admission metadata and final chains | Preserve as index manifest; not Approved Pool ledger or release receipt |
| `sections.jsonl` | Current indexed chunk records | Preserve as retrieval projection; not authoritative identity ledger |

### 6.1 Migration invariants

1. Existing `section_id`, `seq`, hashes, chain values and JSON Pointers remain recoverable for historical queries and audit.
2. Migration must not rewrite old section IDs to look like stable Chunk IDs.
3. Each migrated chunk record receives an explicit mapping record connecting its old locator to its governed Item/Version/Chunk identities, where those identities are authorised and established.
4. If mapping is ambiguous, status is UNKNOWN or UNRESOLVED under the applicable dictionary/schema definitions; do not manufacture continuity.
5. The index may contain multiple locators for one governed chunk version, and a locator may be retired without deleting the underlying identity record.
6. Rebuilds must be reproducible from pinned source bytes, CANON version, subdivision rule, builder version and admission manifest.
7. A changed document digest or chain invalidates the prior build's locator assumptions; it does not silently rewrite the historical build record.
8. The current index manifest is not a master ledger and cannot independently advance an Approved Pool head.

### 6.2 Chunk identity mapping record — required shape

A future mapping record should carry, at minimum:

- mapping record ID and schema version;
- Stable Chunk ID (or explicit UNASSIGNED/UNKNOWN state before governance);
- Item ID and exact Version ID;
- exact chunk-content digest and algorithm;
- canonicalisation and chunking rule identifiers;
- source document/version pin;
- legacy index locator(s): `section_id`, `doc`, `seq`, S1 suffix where applicable;
- JSON Pointer(s), where applicable;
- predecessor/successor or split/merge relationships, if any;
- continuity disposition and evidence reference;
- author/actor, authority reference, timestamp (informational), and approval/adjudication reference.

This is a schema requirement for later design, not an assertion that such a registry currently exists.

## 7. BridgePress lessons and non-transferable assumptions

The BridgePress mechanism provides four useful design lessons:

1. Allocate an identity before publication, but distinguish allocated/reserved from physically carried and verified.
2. Bind an issued identifier to the exact content digest; a conflicting hash must stop rather than silently inherit the identifier.
3. Derive the public ledger from the source artefact where possible, rather than trusting a separately hand-maintained list.
4. Preserve the distinction between a registry's working allocation record and a published ledger projection.

The following must **not** be copied as assumptions:
- A single sequential counter is safe under concurrent workers.
- A document serial can stand in for item, version and chunk identity.
- A published ledger page is authoritative merely because it is visible.
- A new document ID is always the right response to changed content.
- Assigned/carried states alone establish approval or current headship.
- A serial/hash conflict mechanism provides a general atomic compare-and-set for all pool heads.

BridgePress is a precedent for content binding and derived ledgers, not a complete Approved Pool design.

## 8. Governance decisions reserved to Ben

The following are decision items, not decisions made by this specification. No technical recommendation in this document adopts them on Ben's behalf.

### G1 — Physical location of the authoritative ledger

**Decision required:** Where does the authoritative master ledger live?

Options to consider:
- A versioned, immutable ledger artefact on the AInternet Shelf/Git substrate.
- A dedicated transactional store with the Shelf holding immutable snapshots and receipts.
- Another explicitly designated store.

Decision criteria:
- atomic head update and concurrency guarantees;
- immutable history and full-digest retention;
- read-after-write verification;
- recoverability and auditability;
- availability to every authorised layer;
- clear distinction between authoritative state and cached/indexed projections.

**Technical constraint:** GitHub/Shelf is a candidate substrate, not proof of atomic compare-and-set. Phase 2 must inspect and test the exact primitive. If no suitable atomic primitive exists, the design must select another substrate or retain the gap as OPEN/UNKNOWN.

Ben's decision should name the authoritative store and state whether it is the sole authority or a replica/projection.

### G2 — Authority to mint identities and advance heads

**Decision required:** Which seat or governed operation may:
- propose an Item ID;
- allocate/reserve a Version ID generation;
- mint a Stable Chunk ID;
- approve the content and verification record required for a Version ID;
- advance the authoritative Item ID head;
- retire an item or chunk identity;
- approve continuity mappings, splits, merges and successor relationships?

These powers need not belong to the same actor. A proposal, allocation, verification, approval and head-advance may be separate acts.

Decision criteria:
- separation of author, verifier, approver and publisher where warranted;
- explicit act class and scope;
- recorded authority basis and applicable authority-state version;
- fail-closed handling of missing, stale, conflicting or ambiguous authority;
- conflict and recovery procedure.

**Boundary:** The current record establishes Ben as origin of authority and records bounded delegations, but a dedicated machine-readable, versioned authority registry is not established (Infrastructure Gap 5). This specification does not create one or imply that current delegations cover these new acts.

### G3 — Type vocabulary governance

**Decision required:** Adopt, amend or reject the proposed closed starter type vocabulary and determine the process by which types may be added or retired.

Proposed starter set in Pool Design Paper Rev 4:
- DOC — document;
- SPEC — specification;
- DATA — record set/results;
- CODE — harness/tool;
- RPT — report;
- MAN — manifest;
- LED — ledger/register.

For every type, the governance record must define:
- one stable meaning;
- inclusion and exclusion boundaries;
- nearest-neighbour distinctions;
- legal identity shapes and required metadata;
- who may propose, review and approve additions or retirement;
- compatibility and migration treatment for existing IDs.

Similarity does not imply equivalence. A new type must not be introduced by casual reuse of a familiar label. Unknown/unregistered types must not silently acquire behaviour; handling must fail closed where type affects authority, dependency, validation or routing.

### G4 — Chunk identity governance

**Decision required:** Approve the identity policy for information chunks, including how stable chunk identity is assigned and how continuity is decided across document revisions, chunker changes, splits, merges and re-admissions.

Choices requiring Ben's direction:
- whether stable Chunk IDs are mandatory for every admitted verified chunk or only chunks promoted into the Approved Pool;
- whether identity continuity is decided by a named independent reviewer, an authorised adjudicator, or a bounded deterministic rule with human escalation;
- whether split/merge creates new IDs with explicit predecessor/successor links;
- whether existing index chunk IDs are retained only as locators (technical proposal here), or whether a formal migration relationship is adopted;
- what evidence and approval are required before a chunk mapping becomes authoritative.

**Technical recommendation, not a governance decision:** preserve the current index's section IDs as locators; do not retrofit them into stable identities. Add a separate governed chunk identity layer that maps exact version-scoped content to stable logical chunks only where continuity is supported. For ambiguous continuity, mint a new chunk identity and record the relationship rather than guessing.

## 9. Technical decisions consolidated by this specification

The following are technical design constraints and recommendations, not reserved Ben decisions:

1. Maintain separate Item, Version, Chunk, Pool Generation and Consumed Generation identities.
2. Keep the current index's `section_id` and related fields as legacy/index locators.
3. Preserve CANON-1, S1, per-chunk hashes, document chain hashes, JSON Pointers and manifests as provenance/integrity data, with explicit algorithm/version pins.
4. Keep full digests in authoritative records; short hash tails are display aids only.
5. Bind each Version ID to one Item ID and exact canonical content digest.
6. Bind each chunk-version reference to one parent Version ID and exact chunk digest.
7. Require explicit continuity mapping across versions; never infer logical identity solely from matching text, hash, sequence, heading or position.
8. Keep pool snapshots separate from item version numbers.
9. Record allocation/reservation separately from approval and head advancement.
10. Treat BridgePress as a content-bound publication precedent, not a concurrency or authority solution.
11. Keep all historical identifiers and mapping records immutable and addressable.
12. Require later independent testing of allocation, head updates, conflict behaviour and migration before claiming FORM enforcement.

## 10. Required follow-on artefacts and gates

Before implementation:
- Ben records G1–G4 decisions or explicitly defers individual items.
- The chosen identity grammar and type vocabulary are versioned and approved.
- Chunk continuity policy and migration treatment are specified.
- The authoritative ledger location and minting/approval/head-advance authority are recorded.
- Phase 2 inspects the exact chosen storage primitive and tests atomic allocation/reservation separately from atomic head compare-and-set.
- Phase 3 defines dependency declarations and how identity references are resolved during dirtying, preflight and release sweep.
- Phase 4 defines receipt schema, retention and consumer proof.
- A separately approved build specification defines migration, backfill and rollback; no in-place destructive rewrite of existing index identity data.

Before any initial release or generation-zero declaration:
- all required identity tiers are present and unambiguous for the release scope;
- every current head resolves to an approved, verified immutable version;
- chunk mappings have explicit dispositions, including UNKNOWN where unresolved;
- index projections and manifests identify the exact pool generation and consumed pins;
- the release receipt records full scope, evidence, unresolved items and components not synchronised;
- independent examination is completed by a named examiner with appropriate access and execution capability, or the claim is explicitly narrowed under an authorised decision.

## 11. Open questions and unresolved machinery

These remain OPEN/UNKNOWN until exact evidence and tests establish otherwise:

- Physical ledger location and transactional/atomic capabilities.
- Identity minting and head-advance authority.
- Type vocabulary adoption and change governance.
- Stable chunk continuity and mapping authority.
- Atomic generation allocation/reservation (distinct from head compare-and-set).
- Atomic head update and concurrent successor conflict handling (Infrastructure Gap 2).
- General concurrency and conflict resolution (Infrastructure Gap 3).
- Versioned authority resolution (Infrastructure Gap 5).
- Registry/versioning and task linkage where identity operations are task-governed (Infrastructure Gap 1).
- Supersession and downstream reliance handling (Infrastructure Gap 4).
- Migration/backfill of the 1,156-chunk index and subsequent admissions.
- Reproducibility and retention of old CANON-1/S1 build identities.
- Exact relationship between item generation, pool generation and historical dependency pins.
- Examiner availability and independently reproducible test evidence.

## 12. Explicit non-authorisations

This specification does not authorise:
- implementation of the master ledger, allocator, CAS, authority registry, or chunk identity registry;
- changes to `build_index.py`, index manifests, `sections.jsonl`, BridgePress code or serial records;
- backfill, migration, re-canonicalisation or re-indexing;
- minting live Item IDs, Version IDs or Stable Chunk IDs;
- advancing any current head;
- declaring generation zero;
- freezing Dictionary 0.4;
- publication, spend, replay, validator work or pilot operation.

Phase 1 is a design/specification phase. Any implementation requires the later plan phases, their own approved/shelved build specifications and the appropriate authority.

---

## Appendix A — Identity hierarchy (conceptual)

```text
POOL GENERATION
  immutable snapshot of ledger heads
       |
       +-- ITEM ID (stable logical slot)
              |
              +-- VERSION ID (immutable approved version)
                     |
                     +-- STABLE CHUNK ID (logical information unit)
                     |       |
                     |       +-- CHUNK-VERSION REF + full content digest
                     |               |
                     |               +-- INDEX LOCATORS
                     |                    section_id / seq / S1 suffix
                     |                    JSON Pointer / manifest entry
                     |
                     +-- provenance, source pins, validation, approval
       
CONSUMER RECEIPT
  pool generation consumed
  + exact item/version pins
  + historical dependency pins
  + component identity/version
  + validation and retrieval evidence
```

## Appendix B — Decision record template

For each G1–G4 decision, record:
- decision ID;
- exact question and selected disposition;
- alternatives considered;
- authority and source record;
- scope and effective point;
- compatibility/migration impact;
- unresolved conditions;
- required follow-on specification or test;
- decision author and independent reviewer;
- immutable decision artefact reference and full digest.

A deferred decision remains visibly deferred; it is not silently resolved by the technical defaults in this specification.

*End of Phase 1 technical consolidation — Ben's G1–G4 decisions pending.*
