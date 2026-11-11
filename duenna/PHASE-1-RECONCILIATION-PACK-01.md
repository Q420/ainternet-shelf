# PHASE 1 — RECONCILIATION PACK 01 (Remmy)

For Alex's consolidation of APPROVED-POOL-IDENTITY-AND-
GOVERNANCE-SPEC-01, per his request in pb-mwc6w5go-p-kv2y.
Part A and Part B are **direct source inspection
[SI: Remmy]**. Part C is **Crusher retrieval**, carried
unedited and kept distinct, per carrier discipline.

---

## Part A — Index identity machinery [SI: Remmy]

Sources (workspace paths + sha256 pins):
- pulse-bridge/index/build_index.py —
  5423df78207bbc8730bbc2831eb89a2cd195e5ffabe92c9a23b5ea21c5569481
- pulse-bridge/index/manifest.json —
  c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452
- pulse-bridge/index/admit_2026_11_11_exon.py —
  5d46b13bed1c8731d30a94e04717dc6f439bdedffe5177a499b0d9f3cf79ee50

**Fields (per chunk record in sections.jsonl):**
section_id, doc, seq, heading_path, chars, sha256,
chain_sha256, embed_text, text.

**Generation rules (from build_index.py):**
- Canonicalisation first: canon_version **CANON-1**
  (canonicalize()); a document is admitted only if its
  raw file sha256 matches its register entry — the
  builder asserts and halts on REGISTER MISMATCH.
- doc_digest = sha256 of the canonical text
  (manifest field canonical_sha256; distinct from
  file_sha256, the raw bytes).
- Sections split by heading ranges; **section_id =
  `<doc_id>#<seq:03d>`** (seq from 1, per document).
- Subdivision rule **S1**: a section over 3,500 chars
  is split into exact line slices; **chunk_id =
  section_id + letter suffix** (a, b, c…). A section
  within the limit keeps section_id as its chunk_id.
  The section_id field of every chunk record holds the
  chunk_id — one identity field serves both tiers.
- Per-chunk **sha256** = sha256 of the chunk's exact
  canonical text (lines each LF-terminated).
- **chain_sha256**: a per-document hash chain. Seed =
  doc_digest; per chunk, in order:
  chain = sha256((chain + chunk_sha256) as text).
  The manifest records each document's
  final_chain_sha256.
- **Manifest** (manifest.json): canon_version,
  subdivision_rule, per-document {doc, source path,
  file_sha256, canonical_sha256, sections, chunks,
  final_chain_sha256}, total_chunks. Current state:
  79 documents, 1,156 chunks.
- **JSON sources** (2026-11-11 admission, per Alex's
  clearance): one section per run record plus
  document-level sections; **source locators retained
  as JSON Pointers**; no field flattened or discarded;
  the VOID V2 battery results JSON was excluded by
  rule (VOIDED.md admitted instead).

**Retention rules:**
- sections.jsonl + manifest.json are the retained
  artefacts; pre-admission backups are kept
  (sections.jsonl.bak-20261111, manifest.json.bak-20261111).
- The original 45-document canon digest was verified
  UNCHANGED across the 2026-11-11 admission — identity
  of previously admitted chunks is stable across
  admissions that do not alter their sources.
- **Limit, stated plainly:** chunk identity is
  positional and content-derived. If a document's text
  changes, its seq numbering, chunk suffixes and chain
  all change; there is no stable item identity above
  the document slug, no version identity, and no head
  pointer. The index has chunk identity only — the
  pool's item/version tiers do not exist here today.

## Part B — BridgePress serial mechanism [SI: Remmy]

Sources:
- shelf-publisher/registry.json —
  6f5b5b30ad9a5c050795cd3767d3cb2c9944177a6c9d3c031638544cb6adc061
- shelf-publisher/CONTRACT-PHASE2-2026-11-09-v3.4.md —
  13bfbbf56794b634117847a2717431f59b8fc4fb38cbd2af8d38f551209b755f
- shelf-publisher/SERIAL-LEDGER-DESIGN-2026-11-09.md
- shelf-publisher/EVIDENCE-SERIALS-IMPL-2026-11-09.md (§13.5)

**Mechanism (contract v3.4, S13 workflow):**
- Serial form: **BP-<nnnn>**, allocated sequentially
  from a single counter (registry serials.next = 13;
  BP-0001…BP-0012 issued).
- A serial identifies **one document's publication**:
  registry serials.issued[BP-nnnn] = {document_id,
  issued_at, state, page_id}. The documents table is
  keyed by document_id and pins source_ref,
  source_hash and content_hash.
- **Assignment flow:** approve first → append the
  serial to the approved file itself → upload →
  BridgePress extracts the serial from the uploaded
  file → the ledger is generated from that extracted
  source, its hash including the serial.
- **States:** "assigned" — serial allocated and
  recorded, not yet carried inside the artefact
  (BP-0001…BP-0004, grandfathered from before S13);
  "carried" — serial physically in the published file
  and extracted on upload (BP-0005…BP-0012).
- **Stability across revisions/republishes:** a serial
  is bound to its document_id AND content hash.
  Contract §13.5 (fixture-verified): same serial and
  kind with a **different hash stops the run**, ledger
  untouched — changed content cannot silently inherit
  a serial. A revised document published as a new
  document_id takes a **new serial** (e.g. BP-0001
  evidence-pack-birch-v0140 → BP-0005
  evidence-pack-v0150). The four "assigned" serials
  are held for their documents and become "carried"
  only when those documents are republished with the
  serial appended.
- **Where the ledger lived:** the workspace registry
  (registry.json) as the working record; the published
  Serial Ledger page on the WordPress shelf was
  generated FROM the uploaded files' extracted
  serials, not from the registry — the artefact was
  the source, the ledger its derivative. (The WP shelf
  is suspended; the registry persists locally.)

**Analogue value for Phase 1, labelled as Remmy's
reading:** BridgePress serials are a working
single-counter allocation + content-bound identity +
extract-don't-trust ledger, at document tier only.
They do not address item/version separation, chunk
identity, concurrency (single publisher, sequential
by construction), or cross-store heads.

## Part C — Crusher retrieval (carried unedited)

Run 2026-11-11 under harness v2.2, requester: alex.
Daily accounting after both calls: 6,967 known tokens
+ 58 unknown-usage calls of the 200,000 ceiling —
usage reporting is live in v2.2.

**Q1** (Alex's question, verbatim): "What are the exact
index identity fields and their generation and
retention rules: section_id, per-section SHA256, chain
identity, JSON Pointer locators and manifest
references?"
**Answer: UNKNOWN — the corpus does not say.**
Closest sections: exon-source-verification-d02-challenge#006,
#002; exon-dictionary-03-reconciliation#004;
exon-replay-matrix-02#017, #018;
qwen-ab-foundation-v248#018. (Package 11,631 chars.)

**Q2** (Alex's question, verbatim): "How did the
BridgePress v3.4 serial mechanism work: how serials
were assigned, where the ledger lived, what the serial
identified, and whether it was stable across revisions
or republishes?"
**Answer: UNKNOWN — the corpus does not say.**
Closest sections: sync-document#002, #004e, #001,
#004a; exon-flag-correction-proposal#022; faq-v3#025.
(Package 12,700 chars.)

**Finding the two UNKNOWNs establish:** the admitted
corpus documents the programme's artefacts, not the
identity machinery that produced them — those rules
live in code and workspace registries (Parts A/B).
Any Phase 1 specification that relies on the corpus
alone will not find them. Labelled as a coverage
finding, not a retrieval failure: the closest-section
lists show the corpus holds neighbours (the serial
ledger's existence is indexed via sync-document), not
the mechanisms.

*End of pack. Alex consolidates; Ben's four governance
decisions remain his, framed in Alex's draft.*
