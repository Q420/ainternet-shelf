# CRUSHER INDEX ADMISSION — REPORT 01 (2026-11-11)

Authority: Ben's indexing proposal (his diagnosis:
Crusher's UNKNOWNs were index-coverage facts), cleared
by Alex, pb-20261111-exon-index-admission-clearance,
with refinements. Source manifest:
INDEX-ADMISSION-MANIFEST-01.md (produced before
indexing; every source a Shelf copy, git-blob
verified at staging, 34 of 34 MATCH).

## What was done

- 34 documents admitted by the governed delta pattern
  (admit_2026_11_11_exon.py): the EXON shelf family
  (24 documents: Dictionaries 0.1–0.4, their
  challenges, the field matrices and the adjudicated
  merge, the reconciliation table, the gap register,
  the flag/correction proposal, the audits, the replay
  matrices, the exact-retrieval records) and the Qwen
  A/B battery artefacts (10 documents: V1 spec, report,
  evidence manifest and results; V2R results, report,
  execution log, spent authorisation; the v2.4.8
  foundation; the VOID notice as incident record).
- JSON treatments per the clearance: one section per
  run record with JSON Pointer locators (heading_path
  `/runs/<i>`), all fields intact; document-level
  sections for non-run material; foundation admitted
  per component (`/components/<name>`).
- EXCLUDED, per the clearance's boundary: the VOID
  Battery 2 result records (v2-battery-voided/
  QWEN-AB-V2-RESULTS.json). The VOID notice is
  admitted; the voided runs are not retrievable as
  results.
- Index size: 516 → 1,156 sections (640 new).
  Sections containing "gate_decision": 0 → 73.

## Verification

- Canon integrity of the 45 pre-existing documents:
  digest UNCHANGED across the admission (asserted in
  the admission run).
- `query.py verify`: **VERIFY PASS — all hashes and
  chains recompute clean.**
- Cross-check by the index itself: Dictionary 0.4's
  §D section and the merged matrix's §D section hash
  identically (89c48e6293e4…) — the derivation of 0.4's
  Part II from the matrix is visible in the index.

## The four retrievals, re-run verbatim (requester: alex)

Full exchanges are logged in crusher-log.jsonl.
Results, faithfully summarised with their verdicts:

1. **Serialized EXON examples / canonical schemas /
   fixtures (ACCEPT combinations)** — UNKNOWN. True:
   no serialized EXON message exists in any admitted
   source. Closest sections are now EXON sections
   (field-matrix review, replay matrices) — retrieval
   reaches the right neighbourhood; the artefact
   class itself does not exist.
2. **gate_decision canonical schema/fixture** —
   substantive answer, correctly bounded: Crusher
   retrieved Dictionary 0.4's own definition
   (exon-dictionary-04#012b) and Challenge 02 and
   concluded the values {ELIGIBLE, BLOCKED} rest on
   the frozen result records, NOT on a canonical
   schema — the schema remains unestablished, the
   definition and its pinned provenance are now
   retrievable. (73 sections now carry the field
   itself, in the run records.)
3. **A CORRECTION record for the 0.2 self-flag** —
   UNKNOWN. Correct: no such record exists among the
   admitted sources; the closest sections are the
   challenges discussing the flag. Records about the
   flag are not the record. The flag remains OPEN.
4. **Evidence/reference usage by message type** —
   partial: Crusher retrieved the reconciliation
   table and the schema-layer inventory and reported
   (accurately, of those sections) that they carry no
   per-type mapping. The mapping itself IS now in the
   index — exon-field-matrix-03-merged#006 and
   exon-dictionary-04#009 (the §D table, sha
   89c48e6293e4…) — but BM25 ranking did not surface
   it in the top results. Recorded as a retrieval-
   ranking limit, not a coverage gap: the standing
   caveat that Crusher's UNKNOWN means "not
   retrieved" applies in the new direction too.

## Boundary

This admission changes retrieval coverage only. It
alters no EXON definition, evidence standard, or
authority boundary. UNKNOWN keeps its meaning. The
0.2 self-flag remains OPEN. No freeze, replay,
validator, or pilot is authorised by this work.

*Admission executed by Remmy, 2026-11-11. Index
backups: sections.jsonl.bak-20261111,
manifest.json.bak-20261111.*
