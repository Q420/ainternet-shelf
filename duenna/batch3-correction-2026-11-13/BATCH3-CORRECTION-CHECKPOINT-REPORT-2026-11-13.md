# BATCH 3 CORRECTION — CHECKPOINT REPORT — 2026-11-13

Built in the room (/srv/nemotron-pilot/batch3/correction/) under
Ben's tap of 2026-11-13 18:52 MST, from STAGE5-BUILD-SPEC-26 at
pin 52a73273 (Rev 22 as amended by Revs 23–26; the chain CLEARED
by Alex, pb-mwfrk7w4). **Checkpoint result: 46/46 PASS, exit 0**
(suite transcript batch3-correction.log in this bundle), plus the
Batch 2 regression battery at 39/39 against the corrected tools.
Submitted for Alex's independent inspection of this bundle. No
subject call of any kind was made — the stub subject only.

## What the correction changed

- **PILOT-TOOLS-01 (correction form)** — sha256 df1045f7…:
  reference_insert is one tool taking the exact tagged-union
  presentation {form: "extracted", operation_id} |
  {form: "carried", citation}; malformed presentations refuse
  PRESENTATION_FORM before any registry access; the carried
  path accepts a same-tree PRODUCED_ARTEFACT value by citation
  with full record recomputation (existence, payload hash,
  producing check PASS, single consumption) and the evidence
  special case (ordered extraction sequence, duplicates
  preserved); ledger entries on both paths carry the full §2.3
  field set with exactly one provenance form (operation_id +
  rule_id on EXTRACTED, carried_from on CARRIED, source_ref
  null only on CARRIED). The extracted path's rules are
  unchanged from the Batch 2 correction pin word-for-word.
- **The driver (correction form)** — sha256 916eab80…:
  preflight verifies the consumed set against
  PILOT-PIN-AUTHORITY-01 (sha256 16b2392e…, 18 entries, every
  pre-existing hash asserted against its chain pin at
  generation; the authority's own hash is recorded in the
  correction continuation, which is its anchor); RUN_STARTED
  carries the complete consumed inventory by name; step budget
  adjudication happens before any terminal step event
  (STEP_TIMEOUT for [TOOL]/[RULE], ADAPTER_TIMEOUT for
  [MODEL]); T05/T08 STEP-02 locate work parses the artifact
  name from the manifest text (no literal anywhere) and
  produces it as a PRODUCED_ARTEFACT event; the extraction
  step produces the evidence artefact; constructions insert
  eight fields — six extracted, artifact + evidence carried.
- **PILOT-RUN-RECORD-01** — unchanged at ed3f5c85… (see the
  declared finding below).

## Chunk sheet discharge (CC-1..CC-9)

- CC-1 pin authority + continuation: generated and anchored as
  above; the suite's preflight tests run against them.
- CC-2 preflight/inventory: acceptance (a)–(d) PASS.
- CC-3 tagged union: (r1)–(r7) PASS with byte-identical
  before/after registry state; form tag asserted present in
  every reference_insert invocation in the tools tests.
- CC-4 carried path + schema: (f), (g), (i), (s) PASS; the
  entry-schema assertion runs over every LEDGER_ENTRY in the
  MAIN record.
- CC-5 produced artefacts + eight entries: (e) PASS — T05 and
  T08 records each carry exactly eight LEDGER_ENTRYs; T05's
  record equals EXPECTED_RECORD on the seven ground-truth
  fields and its evidence is [CR ×5, adjudication] by the
  Rev 23 rule.
- CC-6 budget order: (k) TOOL and (l) MODEL demonstrations
  PASS; (m) coherence invariant PASS over all seven records.
- CC-7 vocabulary: EVENT_TYPES == the frozen sixteen,
  asserted directly.
- CC-8 fidelity: (n) schema/nullability field-by-field over
  the MAIN record incl. the GOVERNANCE_EVENT three-row
  mapping (the run-scoped row is exercised by the INTEGRITY
  run's SNAPSHOT_HASH_MISMATCH event); (o) pilot-root listing
  compared before/after (140 files) with the commitments
  stand-in byte-unchanged; (p) manifest recomputation from
  the record's own events for T02/T05/T08/T09 MODEL steps
  (T06-E's manifest presence is asserted; its outcomes
  artefact is assembled by the tree's A–D procedures and is
  not recomputed — declared limitation); (q) partial-run
  elements PASS; (j) regression PASS (below). The retained
  Batch 3 demonstrations all PASS: chains verify on every
  record; MAIN all-COMPLETED; T02 return-once; decision-
  stands; LANE stop; TREE_TIMEOUT; integrity stop finality.
- CC-9 bundle: this bundle carries every run record AND its
  ledger.json as named artefacts (below).

## Acceptance list (a)–(s)

(a) PASS · (b) PASS · (c) PASS · (d) PASS · (e) PASS ·
(f) PASS · (g) PASS · (h) PASS · (i) PASS (as the
CITATION_CONSUMED half of the carried-path check) · (j) PASS
with the declared translation below · (k) PASS · (l) PASS ·
(m) PASS · (n) PASS · (o) PASS · (p) PASS with the declared
T06-E limitation · (q) PASS · (r1)–(r7) PASS · (s) PASS.

## Declared items for the inspector

1. **(j) translation.** The Batch 2 suites call
   reference_insert(field, step, operation_id) in the Batch 2
   signature and assert the refusal token
   MALFORMED_PRESENTATION. Rev 25 settled the signature as
   reference_insert(field, process_step, presentation) and
   Rev 24/25 named the malformed refusal PRESENTATION_FORM,
   so a literally unmodified battery cannot run against the
   settled interface. The regression runner
   (run_batch2_regression.py, in this bundle) executes the
   suites with exactly two mechanical translations on copies:
   T1 wraps each call site's third argument as
   {"form": "extracted", "operation_id": X}; T2 renames the
   refusal token. Every assertion, count and expectation is
   otherwise byte-identical; the battery passes 39/39. The
   battery also caught a real defect of mine during the
   build: I had changed IssuanceRegistry.snapshot()'s shape,
   which Batch 2's property-5 test depends on; the shape was
   reverted (citations are exposed by a separate
   citations_snapshot()) and the battery then passed.
2. **pilot_record docstring.** The Rev 25 plan anticipated
   correcting a "17 types" count in the writer's docstring.
   Full-text verification at the pin ed3f5c85… finds no
   numeric type count anywhere in the module; the miscount
   lived only in Rev 25's §4(n) prose (corrected by Rev 26).
   No edit was made; the artefact stands at its Batch 3 pin,
   and the suite asserts its EVENT_TYPES equals the frozen
   sixteen. Recorded also in the correction continuation.
3. **Build readings.** verification_method strings are
   "source_extract <rule_id> (recomputed at insert)" on the
   extracted path and "carried: <producing step>" on the
   carried path, per Rev 24's field table. The evidence
   artefact's producing step is the extraction step (T05-
   STEP-03 / T08-STEP-02), whose CHECK_RESULT precedes the
   construction — the citation contract's check-after rule
   holds literally. At the integrity stop the driver now
   also writes the §2.3 GOVERNANCE_EVENT (kind
   SNAPSHOT_HASH_MISMATCH, both identifiers null) before
   RUN_STOPPED. RUN_STARTED's snapshot block records the two
   snapshot file pins and names the constituent pins as
   manifest-recorded.
4. **Iteration.** Three build iterations preceded the green
   run (a suite sys.path ordering fault, a T08 evidence
   step argument, and two authority re-mints as the driver
   and tools pins moved during fixing). All were scratch;
   the artefacts in this bundle are the final pinned forms
   and the green run was executed against exactly them
   (preflight enforces it).

## Bundle inventory (duenna/batch3-correction-2026-11-13/)

This report; pilot_tools.py (df1045f7…); pilot_driver.py
(916eab80…); pilot_record.py (ed3f5c85…, unchanged);
PILOT-PIN-AUTHORITY-01.json (16b2392e…); the correction
re-freeze continuation; gen_authority.py;
run_batch2_regression.py; stub_script_budget.json
(793d7b58…); test_batch3_correction.py (c8004f33…);
batch3-correction.log (the 46-check transcript); and the
seven scratch runs, each as <run>-record.jsonl +
<run>-ledger.json: B3CORR-20261114-001 MAIN (record
9bbb2649…, ledger 6cb5a2d0…), 002 LANE (1def696b…, 4f53cda1…),
003 TREE-BUDGET (4aeedbf7…, b94357e7…), 004 RUN-STOP
(82541e35…, 4f53cda1…), 005 INTEGRITY (9119c0de…,
4f53cda1…), 006 TOOL-BUDGET (2738a50e…, 4f53cda1…), 007
MODEL-BUDGET (12ab8a61…, 4f53cda1…). (Runs 002/004–007
contain no ledger entries — their ledgers materialise to
the same empty-list bytes, 4f53cda1….)
