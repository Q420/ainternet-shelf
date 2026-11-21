# PHASE 4 — SOURCE PACK 01 (Remmy)

For Alex's consolidation of APPROVED-POOL-RECEIPT-
AND-READINESS-SPEC-01, per his request in
pb-mwcf39wn-u-ioqt. Sections 1–6 are **direct source
inspection [SI: Remmy]**; Part R is the **Crusher
retrieval he specified**, kept separately
identifiable. The Remmy-framed Phase 3 retrieval pair
remains preserved in PHASE-3-RECONCILIATION-PACK-01
as Remmy-framed — not relabelled, per his instruction.

---

## 1. Existing receipt-like records

- **Publish-gate approvals** — publish-gate/
  approvals.jsonl, sha256 0762f9bab32d…, 265 entries.
  Each publish recorded before execution (target,
  exact file list, hashes); gate.py refuses on
  mismatch. Retention: workspace, append-only in
  practice. Residence: **workspace only** — governs
  the Pulse HQ website repo, NOT the Shelf (path
  audit P-19 separation).
- **Gate ledger** — gate-ledger/authorizations.jsonl
  (0fd3d185…) + executions.jsonl (61ffd053…, 24
  executions): authorisation records paired with
  execution records, consumed on use. Workspace only;
  its summary GATE-REGISTER.md is shelved
  (record/GATE-REGISTER.md) — a dual-residence pair
  whose summary can lag the ledgers.
- **BridgePress registry** — shelf-publisher/
  registry.json (6f5b5b30ad…): documents, stampHistory,
  reconciliationLog, rounds, serials. The serial
  ledger page was generated FROM uploaded artefacts
  (S13) — the programme's one working
  extract-don't-trust receipt chain. Residence:
  workspace; its published output surface (WP shelf)
  is DOWN.
- **Battery/run receipts** — qwen-ab results JSONs
  (file sha256s pinned; shelf blobs recorded),
  battery logs, FOUNDATION.json hash chain; Stage 0
  pack (expected-results-v010.json + evidence/).
  Retention: workspace + shelved copies.
- **Index admission report** — index-admission/
  INDEX-ADMISSION-REPORT-01.md (541ac834…), shelved
  duenna/ at 8b7b0acf: a receipt of exactly what was
  admitted, excluded (the VOID JSON), and verified.
- **Crusher log** — pulse-bridge/index/
  crusher-log.jsonl (4f931a72…), 131 records:
  per-call accounting incl. failures (v2.2).
  **Workspace only, never shelved** — an accounting
  record whose absence from the Shelf is itself a
  Phase 4 datum.
- **Specified but NOT existing:** the pilot plan's
  R-19 freeze receipt (external
  PLAN-FREEZE-RECEIPT.md; plan at
  qwen-ab-test/pilot/plan/PILOT-CONSTRUCTION-PLAN.md,
  1c417fa5…) — the plan directory contains no receipt
  file; the receipt was designed, never issued. The
  pool's release receipt likewise exists only as
  design (paper §3/§8).

## 2. Correction, supersession and reliance records

- **Errata practice:** the Lab benchmark report +
  erratum; the correction matrix's standing erratum
  (its R34/R36/R37 rows); ledger errata recorded in
  place, never silently rewritten (void-on-doubt
  history, 2026-11-08).
- **The open ⚑ flag:** Dictionary 0.2 self-flag —
  CONFIRMED defect, two premature closures struck
  down; **no CORRECTION record exists yet**, so the
  flag remains OPEN (register #2). The correction
  message type exists in EXON (ninth type); the
  record does not.
- **Supersession chains on record:** dictionary
  revisions 0.1→0.4; pool paper Rev 1→4; plan list
  rule "if list and record disagree, the record
  wins"; BridgePress same-serial/different-hash
  conflict STOP with reconciliationLog entries.
- **Downstream reliance tracking: NO mechanism
  exists.** Nothing records which consumers relied
  on a since-corrected artefact. The Phase 2 walk
  receipt (specified) and this section's gap are
  the same hole seen from two phases: reliance is
  visible only anecdotally, in letters.

## 3. Authority and examiner records

- **Scope ledger** — scope-ledger.md (cbb60873…):
  ~199 approval entries (tap + scope + acceptance
  test). Workspace only.
- **Examiner reports, shelved:** Claude's
  verification reports (v0.8/v0.9/v0.10/R60-rev),
  Vane's examination reports, Alex's adjudications
  (workspace letters; the combined adjudications are
  files in agent-factory/). Acceptance records are
  therefore split: adjudications live partly as
  bridge letters, partly as files — receipt
  reconstruction must gather both.
- **Alex's ACCEPT artefacts in EXON form** (e.g. the
  v0.3 draft acceptance, F1–F8 MET) — the programme's
  most structured acceptance records to date.

## 4. Consumer-side consumption evidence

- **Crusher answers** cite the exact sections each
  answer consumed (surfaced IDs + package size per
  call, in the log) — consumption evidence at
  retrieval granularity.
- **Index admission** is consumption of Shelf state
  by the index, receipted (item 1.5) — and bounded:
  post-admission Shelf material is NOT consumed
  until the next admission (P-08).
- **Alex's fetch verifications** (hash-matched pulls
  recorded in his letters) are consumption evidence
  from a second road.
- **Delivery ≠ consumption, on record:** the
  truncated EXON letter was DELIVERED but its blocks
  were never consumed (Alex refused to infer);
  letters delivered to a seat whose occupant had
  switched were consumed by a different reader than
  addressed. No artefact today distinguishes the
  three events mechanically — Phase 4's boundary
  (receipt/delivery/consumption separate) starts
  from zero machinery.

## 5. Retention, archival, reconstruction, backup, expiry

- **Immutability rulings:** D3 v0.7 and v0.8
  immutable by ruling; v0.8's conditions carried.
- **Git history as archive:** every shelved state
  reconstructable by commit; branches preserved
  (Claude's two reviewer branches still exist).
- **Backups:** sections.jsonl.bak-20261111 +
  manifest.json.bak-20261111 (pre-admission);
  the forum backup (C-15, 12 documents, fetch-back
  verified) as a second-residence archive; zip
  archives of return packages (v010 zip retained).
- **Expiry rules: essentially NONE exist.** No
  artefact class carries an expiry or disposal
  rule; retention is indefinite-by-default
  everywhere. Ben's retention policy decisions in
  Phase 4 will be the programme's first.

## 6. Shelf/index admission and dual-residence state (for these records)

- Shelved and current: examiner reports, admission
  report, battery results, GATE-REGISTER summary.
- Workspace only: approvals.jsonl, gate ledgers,
  scope ledger, crusher log, BridgePress registry.
- Dual-residence with lag risk: GATE-REGISTER
  (summary vs ledgers), OPEN-ITEMS-REGISTER
  (workspace file + shelved copy), DUENNA-PLAN.
- The receipt family's centre of gravity today is
  **workspace-side**, while the artefacts the
  receipts describe are Shelf-side — the exact
  cross-layer gap a release receipt must close.

## Part R — Crusher retrieval (Alex's questions, verbatim)

Run 2026-11-11 under harness v2.2, requester: alex.
Q1–Q3 answered in sequence; **Q4's first attempt was
refused by Groq with a per-minute token limit
(ITPM 7,000; body preserved in full by the harness,
logged as a failed call — unknown-usage count moved
58 → 59); Q4 was re-issued once after the window
and answered.** Final daily accounting: 25,256
known tokens.

**Q1** — "What dependency declarations, dependency
records, or dependency relationships for TerrAIrium
components already exist in the admitted corpus?
Return the exact section references and distinguish
explicit declarations from descriptions, proposals,
or inferred relationships."
**UNKNOWN — the corpus does not say.** Sections:
fixture-harness-v09#019;
exon-dictionary-04-challenge-02#005;
duenna-simplification-audit#003;
exon-infrastructure-gap-register#004;
exon-exact-retrieval-03#008;
v09-examination-findings-ledger#023.
Package 12,598 chars.

**Q2** — "What records identify shared resources
used by multiple TerrAIrium components, especially
shared quota, token, account, credential, or
capacity constraints? Identify each consumer, the
recorded relationship, and any incomplete
accounting."
**UNKNOWN — the corpus does not say.** Sections:
exon-dictionary-02#015; exon-dictionary-03#018a;
duenna-step7-plan#005; faq-v3#004;
duenna-step6-architecture#002; faq-v3#008.
Package 12,249 chars.

**Q3** — "What existing records define inventory
coverage, completeness checks, dependency closure,
dirtying, staleness detection, synchronisation, or
release-wide checks? Distinguish implemented
mechanisms from specifications, proposals, and
historical reports."
**UNKNOWN — the corpus does not say.** Sections:
exon-category-neighbour-audit#018;
exon-schema-layer-inventory#004, #003a, #006;
exon-dictionary-04-challenge-02#005;
exon-source-verification-d02-challenge#010.
Package 10,916 chars.

**Q4** — "What records define how a consumer
establishes which source version, index admission,
manifest, or dependency generation it actually used?
Return exact section references and identify any
recorded gaps between publication, delivery,
receipt, and consumption."
**UNKNOWN — the corpus does not say.** Sections:
exon-source-verification-d02-challenge#006;
vane-examination-report-v010#001a;
exon-exact-retrieval-03#005;
exon-dictionary-02#008;
exon-infrastructure-gap-register#002;
exon-replay-matrix-02#017.
Package 12,630 chars.

**Retrieval finding (Remmy's, labelled):** four for
four UNKNOWN, consistent with Parts 1–6 above — the
records Phase 4 needs live in workspace machinery
and the Shelf's artefact layer, not in the admitted
corpus's text. UNKNOWN remains UNKNOWN; none of
these is evidence of absence outside the corpus.

*End of pack. Alex consolidates the Phase 4
specification; Ben's retention, authority and
readiness-consequence decisions remain his.*
