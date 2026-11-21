# QWEN–DUENNA A/B V2 — IMPLEMENTATION PACKAGE FOR ALEX'S REVIEW

Prepared under Alex's authorisation (pb-mwbjmwcc §9: DESIGN
APPROVED — BUILD AUTHORISED). **No battery runs have been
made.** This package is the precondition Alex set: completed
process trees, tool inventory, schemas, and a fixture test
demonstrating reference insertion, field verification and
receipt comparison.

Files: PROCESS-TREES.md (nine trees) · tools.py (the tool
implementation) · demo_tools.py + DEMO-RESULTS.json (the
fixture demonstration, executed).

## Tool inventory (Alex's five proposed interfaces, implemented)

All five exist and run. Every call returns the structured
result Alex specified: `{operation_id, tool, source_ref,
source_hash, value, verification, failure_reason}`.

| Tool | Implementation | Notes |
|---|---|---|
| shelf_lookup | Corpus section by id (frozen pack/corpus), or a shelf-manifest row by path | Returns the section's stored sha256, or for a manifest row the stated artifact hash + the manifest's own hash |
| source_extract | Named deterministic extractors (regex + typed conversion) over a looked-up source; returns the value AND its evidence line | An extraction that finds nothing returns NOT FOUND with a reason — it never guesses |
| reference_insert | Copies a verified tool result into a record field byte-exactly; emits the ledger entry | The model never supplies the value; it can only name the extraction |
| verify_field | Equality of a value against its source value or contract enum; PASS/FAIL + reason | Method recorded per call (source_equality) |
| receipt_worksheet | One row per obligation requirement (presence, hash equality, result content, status class) → mechanical CLOSE/REJECT + obligation state | Generalises the v1 gate's receipt check into inspectable rows |

## Schemas

**Accountability ledger entry** (one per produced field):
`{field, value, process_step, source_ref, source_hash,
operation, verification, verification_method}` — exactly the
shape Alex proposed in §6; the demo's ledger entries carry
real hashes from the execution environment.

**Tool result:** `{operation_id, tool, source_ref,
source_hash, value, verification, failure_reason}` (+
`evidence_line` on extractions, `verification_method` on
field checks).

## Execution model (how the battery will run, once authorised)

A driver executes each tree step in order. [TOOL] steps run
deterministically. [MODEL] steps call Qwen with **only the
step's declared inputs** (worksheets, extractions, boundary
tables) — the worker never hunts the raw pack for a value it
must copy, which is the process arm's defining difference.
Step verification runs at the step; failure follows the
tree's recovery branch (bounded, criteria fixed) or STOPs
with the failure recorded. Arm C receives **no** end-of-run
generic gate (Alex §2): the final output is assembled from
ledger-verified fields, and prose claims are admitted only
with an extraction mapping (provenance completeness is scored
from the ledger). Every tool invocation is logged.

## Fixture demonstration (executed; DEMO-RESULTS.json, 19 tool calls)

1. **Reference insertion (T05 construction).** The status
   record was built entirely by process: shelf_lookup took
   the artifact identifier + stated hash from the shelf
   manifest row; source_extract took the four values from
   change-record section #009; a cross-record check confirmed
   the manifest's hash and the change record's hash **agree**
   (two independent records, one value); reference_insert
   populated all eight fields. **The constructed record
   matches the expected record exactly**, and every field
   verifies PASS against its source.
2. **Field verification.** The actual v1 error value (the
   section heading both arms submitted as the artifact) was
   submitted to verify_field: **FAIL**, with the reason
   recorded — the v1 defect is caught at the step where it
   was made.
3. **Receipt comparison.** Worksheets: FR-A REJECT (hash
   row), FR-B REJECT (missing result field), FR-C REJECT
   (status class row), FR-VALID CLOSE — obligation OPEN on
   all three defective receipts, CLOSED on the valid one.

**One defect found and fixed during the demo** (recorded
because Alex's rule is that limitations are stated, not
smoothed): the first extraction patterns for the two hashes
assumed the value sat on the same line as its label; the
change record wraps it to the next line, so both extractions
returned NOT FOUND and the demo's cross-check failed loudly —
the tool's failure, surfaced by the process, fixed in the
extractor patterns, demo re-run green. This is also a small
honesty proof for the design: the failure was a recorded
NOT FOUND, never a fabricated value.

## Limitations (stated before any run)

- source_extract's extractor set is small and specific to
  these packs (four named extractors + manifest rows). A
  value with no extractor is NOT FOUND by design.
- T04's boundary enforcement remains behavioural (the tree
  loads the boundary table mechanically; the refusal is
  still the model's). Alex's caution stands.
- T01/T02/T03 prose composition is a [MODEL] step: the
  process constrains its inputs and maps its claims, but
  prose judgement is not mechanised.
- The tools operate on the frozen corpus and the local shelf
  manifest; no live-shelf access is claimed.

## What is asked of Alex

Review of: the nine process trees; the tool implementations
against his §4 interfaces; the schemas; the demonstration
results. The battery (Arm C runs over the nine frozen packs,
scored on his §7 measures — first-attempt correctness, step
compliance, reference accuracy, verification coverage,
recovery frequency, provenance completeness, tokens, time)
runs only on his authorisation after this review.
