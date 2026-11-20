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
  **[This bullet is superseded by the correction round below:
  provenance entries are no longer trusted as appended — see
  "Correction round — Gate 1 return".]**

---

## Correction round — Gate 1 return (2026-11-20)

**Verdict cited:** VANE-GATE1-VERDICT.md (Stage 2), filed on the
shelf at commit c339dd097aa2b11c533ebd7ff25f6e05e327383c —
**FAIL — RETURN TO STAGE 2 FOR CORRECTION. DR-02 NOT ADVANCED on
the first submission.** The frozen schema mechanism (finding 1)
and the three-way construction close (finding 2) PASS; the Stage 5
dependency decision is ACCEPTED (finding 5) and stands as recorded
above. The decisive finding is finding 3, the canonical provenance
boundary. This section is appended to the original report; the
original content above is preserved, and the statements it
supersedes are marked where they stand (the "What was built"
description of `append_provenance_entry` / `read_provenance_entries`
as the canonical entry path, and the final Boundaries bullet).

### The finding

`EventRecord.append()` accepts arbitrary event types and bodies.
The first submission's `read_provenance_entries()` trusted the
`PROVENANCE_ENTRY` type string, so a caller could directly append
a forged, complete, schema-matching `PROVENANCE_ENTRY` event
through the generic record API — bypassing
`append_provenance_entry()` — and the constructor would accept it.
"Canonical" described a convention, not an enforced property.
Sabotage (e) tested a foreign event type (`LEDGER_ENTRY`); it did
not cover this forgery. The verdict's instruction, followed here:
do not merely add a second comparison after reading the same
forged event — the issue is provenance authority, not equality of
its contents.

### The correction — the canonical writer

`construction.py` is revised (schema.py unchanged; stage1/
untouched):

- **`ProvenanceLog` — the canonical writer, sole issuer of
  provenance entries.** `ProvenanceLog.append_entry` validates and
  appends each entry (the validation of the old free function,
  unchanged) and registers exactly what it issued: per artefact,
  the ordered (field, value) pairs plus the record event's seq and
  digest returned at append time. The Stage 1 record is
  hash-chained, so each digest binds its registry entry to the
  exact event (seq, predecessor, type, body) the record accepted.
- **Construction takes the writer as a capability.**
  `ArtefactConstructor(log, schema)` / `construct_artefact(log,
  ...)` — there is no construction path from the raw record alone.
  The free functions `append_provenance_entry` and
  `read_provenance_entries` are removed; the writer's
  `issued_entries(artefact_id)` is the only provenance read.
- **Verification before build.** `construct` first calls
  `ProvenanceLog.verify(artefact_id)`, which cross-checks the
  record against the registry — by digest, never by trusting a
  body's claims, and never by comparing a suspect event's contents
  for equality:
  - *Sole issuer (global):* every `PROVENANCE_ENTRY` event on the
    record must carry a digest this writer issued. Any other such
    event — forged, malformed, or another writer's — is named by
    seq under `unissued_provenance_events` and refuses
    construction. A forgery poisons the close; it never sneaks in.
  - *Registry completeness (per artefact):* the record's
    `PROVENANCE_ENTRY` digests for the artefact, in record order,
    must equal the registry's digests in issue order; any issued
    entry missing or altered is named under
    `issued_entries_missing_or_altered`.
  A boundary refusal is recorded on the record as a
  `CONSTRUCTION_REFUSED` event carrying the violation details, and
  raised as `ConstructionRefused` — the same recorded-refusal
  discipline as a close refusal. Only after verification passes
  are the artefact's entries taken from the registry, built from,
  and closed by G2's three-way comparison, whose semantics are
  unchanged from the examined submission.

### New sabotage results — each separate

8. **(g) Forged canonical-type event set (the verdict's required
   case)** — test_sabotage_g_forged_canonical_events_refused —
   REFUSED, as required. A complete, schema-matching set of eight
   `PROVENANCE_ENTRY` events is appended directly via
   `record.append`, bypassing the canonical writer; the bodies are
   exactly right, so any content comparison would admit them. The
   actual constructor refuses, naming all eight events by seq
   under `unissued_provenance_events`; the refusal is recorded;
   no CONSTRUCTION_CLOSED event.
9. **(mixed) Genuine entries plus one forged entry** —
   test_mixed_genuine_and_forged_entries_refused — REFUSED, as
   required. All eight fields are issued by the canonical writer
   (a set that would close on its own), then ONE forged
   `PROVENANCE_ENTRY` is appended via the generic API. The
   constructor refuses, naming the forged event's seq under
   `unissued_provenance_events`; the refusal is recorded; no
   CONSTRUCTION_CLOSED event.
10. **(malformed) Malformed canonical-type bodies** —
    test_malformed_canonical_bodies_controlled_refusal — REFUSED,
    as required, in a controlled and recorded way. Six malformed
    bodies are appended via the generic API under the
    `PROVENANCE_ENTRY` type: a dict missing field/value, a field
    of None, an unhashable (list) field, a dict with no
    artefact_id, a string body, and a null body. Construction
    raises `ConstructionRefused` naming all six seqs under
    `unissued_provenance_events`, records the refusal, and admits
    nothing — no uncaught exception (the unhashable field in
    particular never reaches the comparison code).

Sabotages (a)–(f) and the value-mismatch companion are preserved
as separate cases, re-expressed through the writer API where they
previously used the removed free functions; all still REFUSE with
the same differing-field evidence as reported above. The positive
controls still close. One positive control is added:
**fresh writer over an existing record refuses** —
test_fresh_writer_over_existing_record_refuses — PASS (i.e. the
refusal occurs as the boundary states): a new `ProvenanceLog` over
the reloaded record (chain intact) has an empty registry and
refuses construction of a fully-entered artefact, naming all
eight entries as unissued.

### Honest boundary of the correction

Enforcement holds where the canonical writer is the sole issuer
within the construction process: provenance authority in this
harness is the continuity of the writer and its registry. A fresh
writer over a reloaded record refuses everything (fail-closed) —
it cannot distinguish the record's genuine entries from forged
ones, and says so by refusing rather than by trusting. Wholesale
replacement of the record itself is outside this boundary: the
same out-of-scope class as Stage 1's C3 limitation (a coordinated
record+anchor rewrite is not defeated), which belongs to the
external anchor, not to this stage. Nothing in this correction
claims past that line.

### Test evidence — correction round (builder-run)

Full suite run 2026-11-20, after the correction:

Command: `python3 -m unittest discover -s tests -v` (from stage2/)

Result: **Ran 25 tests — OK (25 passed, 0 failed)**, exit code 0.

Per file:
- tests/test_schema.py — 7 tests, all ok (unchanged)
- tests/test_construction.py — 8 tests, all ok (7 carried over to
  the writer API; 1 added — the fresh-writer boundary control)
- tests/test_stage2_sabotage.py — 10 tests, all ok ((a)–(f) and
  the value-mismatch companion preserved; (g), (mixed) and
  (malformed) added)

Stage 1 regression run 2026-11-20 (from stage1/):

Command: `python3 -m unittest discover -s tests`

Result: **Ran 68 tests — OK (68 passed, 0 failed)**, exit code 0 —
no regression; stage1/ was not modified.

These counts are builder-run evidence, as before; no independent
examiner execution has yet occurred on the corrected package.

### Register effect — corrected disposition

Per the verdict, DR-02 was **NOT ADVANCED** on the first
submission, and the "Register effect" section above is superseded
to that extent: it described advancement on demonstration before
the examiner's examination had occurred. The corrected position:
the boundary defect the examiner found is corrected in the
harness and demonstrated by sabotages (g), (mixed) and
(malformed) above; whether DR-02 advances on this corrected
evidence is the examiner's determination on re-examination, which
has not yet occurred. This report claims nothing further.
