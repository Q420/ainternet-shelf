# QWEN–DUENNA A/B V2.3 — MANDATORY EVIDENCE PROVENANCE

Prepared under Alex's authorisation (pb-20261110-v22-review-
findings). **V2, V2.1 and V2.2 are preserved unchanged. No
battery runs.** Files: tools23.py · demo23.py ·
DEMO23-RESULTS.json (62 tool calls logged). One correction,
exactly as specified; nothing else redesigned.

## The correction

Alex's finding: in V2.2 the evidence fields were checked
*when present* but their presence was not mandatory — strip
`evidence_line` (or its number), recompute the digest, and
the conditional comparisons in `_rederive()` were skipped.

V2.3 makes all provenance fields mandatory for
`source_extract` and `extract_line` results at
`reference_insert()`:

- `source_ref`, `source_hash`, `result_digest`,
  `evidence_line`, `evidence_line_no`, `value_offsets`.

Missing or null fields are rejected at the
provenance-completeness check, **before** re-derivation,
with each missing field named. In `_rederive()` the
conditional comparisons are gone: for extraction tools,
absent evidence is itself a failure ("missing evidence
provenance in extraction"), never a skipped check.

## New fixtures (all executed; D1–D3 and N1–N7 re-run green under the v2.3 tools)

- **N8a — `evidence_line` removed, digest recomputed** →
  insert FAIL at completeness: "missing provenance:
  evidence_line." Nothing inserted.
- **N8b — `evidence_line_no` removed, digest recomputed** →
  FAIL: "missing provenance: evidence_line_no."
- **N8c — both removed, digest recomputed** → FAIL:
  "missing provenance: evidence_line, evidence_line_no."

Side effect worth noting: N1 (V2.1's strip fixture, which
removed hash/digest/offsets without recomputing) now fails
naming `evidence_line_no` as well — the completeness check
catches the older strip set harder than before. Expected,
not a regression.

## State of the provenance claim

After V2.2 + V2.3, an extraction result reaching insertion
must carry a complete provenance record — source identity,
value, offsets, evidence line and its number — and every
element of that record is compared against the source
actually retrieved, with alteration and removal both
covered, each failing with its specific reason.

## Asked of Alex

Review of the correction and fixtures N8a–c. Battery
authorisation remains his.
