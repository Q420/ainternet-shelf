# Duenna Stage 2 — Artefact Construction and Provenance Report

Date: 2026-11-20
Design authority: PROCESS-TREE-AND-PLAN.md v2, Stage 2; ID-SYSTEM-DESIGN-DRAFT-V3.md (K5, G2)
Build location: ~/workspace/duenna-fix/stage2/ (Python standard library only)
Approval: Ben, 2026-11-20 (Stages 2–9 approved; Stage 2 built first, from the plan)

## Status of this report

The Stage 2 construction harness is built and its full test suite
passes (21/21, below). This report is EVIDENCE for the examiner, not
a verdict: a builder's green run establishes that the mechanism
behaves as specified on the exercised cases; whether Stage 2 passes
is the examiner's determination (Gate 1 discipline), not this
report's. Nothing here declares Stage 2 complete.

## What was built

- `schema.py` — the one frozen schema object (K5). `freeze_schema`
  takes the artefact-field contract and the checker/response
  contract (K12) plus the version in a single call and returns a
  `FrozenSchema`: both sections frozen together in the same act,
  exposed as tuples, attribute assignment after construction
  raises, and the schema's identity is one digest (SHA-256 over the
  canonical encoding of version + both sections), so a change to
  either section is a change of identity. There is no API that
  freezes or alters one section separately. The harness's frozen
  test schema (`TEST_SCHEMA`) carries the three fields DR-02 names
  (`artifact`, `evidence`, `fixtures_total`) plus the remaining
  contract fields of the battery-artefact family, eight in all,
  matching the eight-field shape of the T05/T08 artefacts; the
  fixture exercises the schema mechanism — the production field
  inventory is a run-configuration fact (K3), not settled here.
- `construction.py` — the artefact-producing path and the G2 close,
  kept as the two distinct operations K5 specifies:
  - Provenance entries live on the Stage 1 record as
    `PROVENANCE_ENTRY` events, appended only via
    `append_provenance_entry` (the canonical entry path) and read
    only via `read_provenance_entries`, which ignores events of
    any other type however their bodies are shaped.
  - `build_from_entries` constructs the artefact FROM its entries —
    never from a caller-supplied dictionary. Each field resolves to
    exactly one entry; a duplicated field cannot be produced.
    There is no parameter or side path by which a literal value can
    be assigned into an artefact.
  - `construction_close` is G2: a three-way exact comparison —
    names AND values — of the artefact, its provenance entries, and
    the frozen schema's artefact section. The schema is a third
    party to every comparison: a schema-required field absent from
    BOTH the artefact and its entries still fails the close.
  - `ArtefactConstructor.construct` is the whole canonical path:
    read entries from the record, build from them, close. Success
    appends one `CONSTRUCTION_CLOSED` event (artefact identity,
    schema digest, field set, values digest). Refusal appends one
    `CONSTRUCTION_REFUSED` event carrying the differing field
    identities (G2's evidence requirement) and raises
    `ConstructionRefused` with the same details.
  - The ledger projection (K5(b)) is a different operation; nothing
    in this stage reads or proves anything about a projection. All
    tests exercise the construction path and the close, never a
    projection.
- `tests/` — the full suite below. Stage 1's code is imported, not
  modified: `stage1/` is untouched, and its suite still passes
  68/68 (regression run, below).

## Dependency decision — taken on evidence, flagged for the examiner

The plan's Stage 2 dependency note (the examiner's): if the artefact
path relies on operation insertion, Stage 5's receiver-idempotency
work moves before this stage; the plan takes that decision at Stage
1's close, on evidence.

**Decision: the artefact path does NOT rely on operation insertion;
Stage 5's receiver-idempotency work does NOT move before Stage 2.**

Evidence: the Stage 1 record is append-only local appends
(`EventRecord.append`, hash-chained, flushed and fsynced — see
stage1/record.py). Stage 2 construction reads provenance entries
from that record and closes locally and synchronously, in-process.
There is no receiver, no delivery boundary, and no retry semantics
in this path for receiver-idempotency to attach to. Operation
insertion (K4/G3) belongs to the operation-execution path, not to
artefact construction from record entries. This decision is recorded
here for the examiner's review; if the examiner's reading of the
evidence differs, the decision is theirs to overturn.

## Test evidence

Full suite run 2026-11-20:

Command: `python3 -m unittest discover -s tests -v` (from stage2/)

Result: **Ran 21 tests — OK (21 passed, 0 failed)**

Per file:
- tests/test_schema.py — 7 tests, all ok
- tests/test_construction.py — 7 tests, all ok
- tests/test_stage2_sabotage.py — 7 tests, all ok

Stage 1 regression run 2026-11-20 (from stage1/):

Result: **Ran 68 tests — OK (68 passed, 0 failed)** — no regression;
stage1/ was not modified.

## Positive controls

A close that refused everything would "pass" every sabotage while
proving nothing, so the positive controls are first-class:

1. **Well-formed artefact closes** — test_well_formed_artefact_closes
   — PASS. All eight provenance entries appended via the canonical
   path; the constructed artefact equals the entered values; exactly
   one CONSTRUCTION_CLOSED event appended, carrying the artefact
   identity, the schema digest and the sorted field set; no
   CONSTRUCTION_REFUSED events.
2. **Field-for-field faithful artefact passes equality** —
   test_faithful_artefact_passes_field_for_field — PASS. Every
   schema field is present in the artefact with exactly its entry's
   value; the artefact's field set equals the schema's artefact
   section exactly.
3. **Record integrity preserved** —
   test_record_chain_still_verifies_after_construction — PASS. The
   Stage 1 hash chain verifies over the record after construction
   appends.
4. **Per-artefact isolation** —
   test_entries_for_other_artefacts_are_not_read — PASS. Entries for
   a second artefact on the same record are neither read into nor
   admitted for the first.

## Per-sabotage results — the plan's Test 2, each result separate

Each sabotage was presented to the real artefact path and
construction had to REFUSE to close. They are reported separately
because they establish different properties; no single compressed
pass statement covers them.

1. **(a) Direct assignment of artifact/evidence reintroduced** —
   test_sabotage_a_direct_assignment_refused — REFUSED, as required.
   The artefact carries `artifact` and `evidence` as literal values
   assigned outside the entry path (DR-02's exact mechanism), with
   no provenance entries for them. The close refuses and names
   exactly those two fields under
   `fields_in_artefact_without_entry`.
2. **(b) fixtures_total renamed** —
   test_sabotage_b_fixtures_total_renamed_refused — REFUSED, as
   required. Entries carry `fixtures_executed` instead of
   `fixtures_total` (DR-02's exact renaming), end-to-end through the
   constructor. Artefact and entries agree with each other; the
   schema as third party catches it: `fixtures_total` named under
   `schema_fields_absent_from_both`, `fixtures_executed` named
   under `entry_fields_outside_schema` and
   `artefact_fields_outside_schema`. No CONSTRUCTION_CLOSED event.
3. **(c) A ledger entry dropped while the field retained** —
   test_sabotage_c_dropped_entry_field_retained_refused — REFUSED,
   as required. The artefact is faithfully built from the full entry
   set; at close, the `fixtures_total` entry is missing. The close
   refuses, naming `fixtures_total` under
   `fields_in_artefact_without_entry` and
   `schema_fields_missing_from_entries`.
4. **(d) An extra entry outside the schema** —
   test_sabotage_d_extra_entry_outside_schema_refused — REFUSED, as
   required. A ninth entry (`fixtures_executed`) is appended via the
   canonical path alongside the eight schema fields, end-to-end
   through the constructor. The close refuses, naming
   `fixtures_executed` under `entry_fields_outside_schema` and
   `artefact_fields_outside_schema`. No CONSTRUCTION_CLOSED event.
5. **(e) The canonical path bypassed** —
   test_sabotage_e_canonical_path_bypassed_refused — REFUSED, as
   required. Provenance-shaped content for all eight fields is
   placed on the record under a foreign event type
   (`LEDGER_ENTRY`), never via the canonical entry path. The
   constructor reads none of it — it is not provenance — and
   construction refuses with all eight schema fields named under
   `schema_fields_absent_from_both`. No CONSTRUCTION_CLOSED event.
   A compare-after check against the fabricated content would have
   found matching fields; construction-from-entries does not admit
   it.
6. **(f) A schema-required field absent from BOTH the artefact and
   its provenance entries** (the plan's v2 addition) —
   test_sabotage_f_field_absent_from_both_refused — REFUSED, as
   required. `fixtures_total` is never entered; the artefact built
   from the remaining entries is exactly equal to its entry set —
   pairwise equality genuinely holds, and the test asserts that it
   holds before closing. Construction still refuses, end-to-end
   through the constructor, naming `fixtures_total` under
   `schema_fields_absent_from_both`: equality between two incomplete
   representations is not schema completeness. No
   CONSTRUCTION_CLOSED event.
7. **Value mismatch (companion case)** — test_value_mismatch_refused
   — REFUSED, as required. Names agree across all three parties;
   one value (`fixtures_passed`) differs between the artefact and
   its entry. Exact equality is names AND values (G2); the close
   refuses, naming `fixtures_passed` under `value_mismatches`.

Further refusal mechanics covered in tests/test_construction.py:
construction with no entries at all refuses and records the refusal
on the record; a duplicate entry for one field refuses (a field
resolves to exactly one entry); a non-JSON-encodable provenance
value is refused at entry time.

## Register effect

DR-02's identity requirement: *no produced artefact field may exist
without its canonical provenance entry; construction, validation and
ledger completeness joined by a mechanically enforced invariant.*
The mechanism specified for it — K5 construction-from-entries plus
the G2 three-way construction close — is built and demonstrated in
this harness, including against DR-02's exact failure modes (direct
assignment of `artifact`/`evidence`; `fixtures_total` renamed to
`fixtures_executed`). On the plan's terms, DR-02 is advanced on
demonstration — subject to the examiner's independent examination of
this evidence, which has not yet occurred. As with Stage 1, this
discharges the mechanism in the harness; the production
`_construct` path in pilot_driver.py is not rewritten — production
integration belongs to the later stages.

## Boundaries

- In-process, local, synchronous construction only. No network, no
  model calls, deterministic.
- The schema fixture's field inventory is the harness's frozen test
  schema (see `schema.py`); the mechanism is the stage's claim, not
  the inventory.
- Provenance entries are trusted as appended to the Stage 1 record;
  the record's own integrity guarantees (hash chain; wholesale
  rewrite detection) are Stage 1's, with Stage 1's stated limits —
  including that chain verification alone does not defeat a
  wholesale re-chained rewrite (the external anchor's scope).
