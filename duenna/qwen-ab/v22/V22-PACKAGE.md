# QWEN–DUENNA A/B V2.2 — PROVENANCE-INTEGRITY CORRECTIONS

Prepared under Alex's authorisation (pb-mwbk6099). **V2 and
V2.1 are preserved unchanged. No battery runs.** Files:
tools22.py · demo22.py · DEMO22-RESULTS.json (60 tool calls
logged). Process trees and the step mapping are unchanged
from V2.1 — this revision touches provenance integrity only.

## The three corrections

1. **Evidence-line integrity.** The digest payload now
   includes `evidence_line` itself (v2.1 covered only its
   number), and re-derivation compares **both** the evidence
   line and its line number against the fresh result. Root
   cause worth naming: the digest key list existed in two
   places (issue and insert) and they had drifted. V2.2 makes
   it a **single constant, DIGEST_KEYS**, shared by issue,
   insert, and the fixtures — the drift cannot recur
   silently.
2. **Source-hash recheck.** Re-derivation now compares the
   freshly retrieved source hash against the extraction's
   recorded source hash, first among the comparisons, with
   its own failure reason. A recomputed digest no longer
   stands in for source identity.
3. **extract_line offsets.** Computed cumulatively from the
   actual line position while iterating — the text is never
   searched a second time, so there is no first-occurrence
   ambiguity.

## New fixtures (all executed; D1–D3 and N1–N3 re-run green under the v2.2 tools)

- **N4a — evidence line altered, stale digest** → insert
  FAIL (digest mismatch — the digest now covers the line).
- **N4b — evidence line altered, digest recomputed** →
  insert FAIL: "evidence line differs from the retrieved
  source" (recorded fabricated line vs the real one quoted).
- **N5 — evidence line number altered (+5), digest
  recomputed** → insert FAIL: "evidence line number
  differs: recorded 31, retrieved 26."
- **N6 — source hash replaced (all zeros), digest
  recomputed** → insert FAIL: "source hash differs from the
  source actually retrieved," both hashes quoted.
- **N7 — duplicate identical lines.** A real corpus section
  (process-tree-v04#018) contains the line "assembled by
  Remmy, 2026-11-08, under Alex's authorisation" **twice**
  (lines 33 and 35). extract_line reports line 33; the
  recorded offsets slice exactly that line, begin at a true
  line start, and the line index computed from the offset
  equals the reported number. (An earlier draft of this
  fixture used a looser anchor, matched a neighbouring
  near-identical line instead, and reported 1 occurrence —
  caught and corrected before delivery; the fixture now
  asserts the occurrence count is 2.)

Each failure names its specific reason and inserts nothing.

## What this establishes

The provenance record now means what it claims: value,
location, evidence line, and source identity are each
checked against the source actually retrieved, and the
strongest forgery this layer models — alter the content,
recompute the seal correctly — fails on re-derivation in
every field, not only the value.

## Asked of Alex

Review of the three corrections and the new fixtures.
Battery authorisation remains his.
