# BATCH 3 CORRECTION — ROUND 3 CHECKPOINT REPORT (2026-11-13)

**Result: 102/102 checks PASS, suite exit 0.** Built under
Alex's round-3 plan approval (pb-mwfv87qi), which ruled no
fresh Ben go was required: a narrowly bounded correction to
the same checkpoint's evidence under the existing round-2
build go. Only the checkpoint suite and the authority
generator's docstring changed. The driver (3431caeb…), the
pin authority (e245cabc… — no re-mint, per Alex's ruling),
pilot_tools.py (df1045f7…) and pilot_record.py (ed3f5c85…)
are byte-identical to round 2. The round-2 bundle (73447eb1)
is preserved unchanged.

## Discharge of the four findings + wording

1. **§4(p) declared-input deep comparison (HIGH)** — every
   MODEL step's record-reconstructed artefact is now ALSO
   deep-compared (==) against declared inputs derived
   suite-side from pinned data only, in code that never calls
   the driver: T02's worksheet/conflicts rebuilt from the
   pack's three corpus sections under the step text's
   authority order; T05/T08's extraction maps re-derived
   through the pinned extractor over the pinned corpus and
   their failed-check lists re-derived from the runs' own
   draft artefacts against those extractions and
   PILOT-DATA-EXPECTED-01; T06's full outcome dicts re-derived
   from the pack + corpus by the A–D rules, with T06_KEY now
   read from PILOT-DATA-EXPECTED-01 instead of a suite-local
   copy; T09's worksheet recomputed from PILOT-DATA-T09-01 by
   the pinned tool. All deep comparisons hold on all eight
   records (MODEL coverage unchanged: MAIN 7/7, LANE 3/3,
   TREE-BUDGET 1/1, RUN-STOP 2/2, MODEL-BUDGET 2/2, others 0).
2. **§4(r) the exact seven (HIGH)** — (r1)…(r7) each run as
   its own transcript line under the spec's setup (one
   unconsumed extraction + one unconsumed citable artefact;
   both consumption sets snapshotted before and asserted
   byte-identical after every refusal; no LEDGER_ENTRY
   emitted): r1 {carried, operation_id}; r2 {extracted,
   citation}; r3 citation + caller-supplied value AT THE
   PRESENTATION LEVEL; r4 missing form; r5 unknown form; r6
   unexpected extra field; r7 both handles. The three round-2
   additional forms are retained as one declared unnumbered
   extras line (bare value; carried with both handles; value
   nested inside the citation) plus the citation-naming-an-
   extraction-event case at CITATION_FIELD_MISMATCH.
3. **§4(n) seq type (MEDIUM)** — schema_ok asserts
   type(seq) is int (booleans excluded) on every event of
   every record, and the per-record sequence lines assert it
   alongside contiguity.
4. **§4(o) confinement (MEDIUM)** — the before/after listing
   now maps 184 files to their CONTENT sha256; the parent
   directory's (/srv) listing is compared; the commitments
   probe stand-in is deleted and the assertion runs against
   the real /srv/nemotron-pilot/commitments/ directory
   (found empty; its recursive content listing is identical
   before and after). The suite's own channels (its scratch,
   its transcript log, bytecode caches) are the only
   exclusions, declared in the suite.
5. **Generator wording** — gen_authority2.py's docstring now
   describes the fixture operation accurately: the sections
   file's final newline is replaced by a space followed by a
   newline (net +1 byte). No re-mint follows (Alex's ruling);
   the authority is byte-identical.

## Build iterations (declared)

Two aborted suite runs precede the green one, both suite-side
defects caught before any check verdict was produced: a
TypeError (the deep-compare call passed run_dir before the
recompute signature change landed) and a NameError (the T09
derivation referenced a name defined later in the file).
Driver, authority and data were untouched throughout. The
green run is the bundle's transcript.

## Pins

CONTINUATION-BATCH3-CORRECTION-3 (in freeze/ and this bundle):
suite dc17a4a7…, generator eae6670c…, driver and authority
restated unchanged. Eight fresh runs of the round-2 scenarios
(records + ledgers + provenance reports in this bundle).
No subject call occurred. No Batch 4 opening.
