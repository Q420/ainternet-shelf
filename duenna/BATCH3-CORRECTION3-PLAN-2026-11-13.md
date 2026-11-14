# BATCH 3 CORRECTION — ROUND 3 PLAN (2026-11-13)

**Standing:** Alex's independent review of the round-2 bundle
(73447eb1), PB-ID pb-mwfv3afi-j-rxf: the Rev 4 bootstrap
implementation is accepted as it stands — authority, binding,
provenance, records all verified by his inspection — and the
fixture deviation is ACCEPTED (with the generator-wording
correction at Item 5). Four acceptance gaps remain, all in the
TEST EVIDENCE, none in the driver. This plan corrects the suite
(and one docstring) only. The round-2 bundle and its pins are
preserved unchanged; the round-3 build touches
`test_batch3_correction2.py` and `gen_authority2.py` (wording),
and issues CONTINUATION-BATCH3-CORRECTION-3 recording the new
suite/generator pins. pilot_driver.py, the authority,
pilot_tools.py and pilot_record.py do not change; no authority
re-mint (the generator's docstring is not authority content).
Remmy verified every finding against the code and the spec text
before planning: §4(r) and §4(p)/(o) wordings below are quoted
from Rev 26 §4 at the cleared pin.

## Item 1 — §4(p): the declared-input deep comparison (HIGH)

§4(p) requires each MODEL step's manifest artefacts to be
"recomputed from the cited producing outputs **and
deep-compared to the step's declared inputs in the trees
data**". The trees data declares each MODEL step's inputs in
its step text and `depends` (T02-STEP-03: "Input: worksheet +
conflict list"; T05-STEP-06: "Input: failed checks + original
extractions only"; T06-STEP-E: "Input: the four step
outcomes"; T08-STEP-04: "Input: any failed checks" — the
validation artefact of T08-STEP-03; T09-STEP-03: "Input: the
worksheet only") — but carries no structured input VALUES. The
independent authority for the values is the pinned DATA the
trees point at (the packs name corpus sections;
PILOT-DATA-EXPECTED-01 and PILOT-DATA-T09-01 carry the ground
truth), never the driver's own procedure. The round-3 suite
derives each family's declared inputs from those sources,
independently of the record, and asserts BOTH the existing
hash recomputation AND a deep equality (==) between the
record-recomputed artefact and the independently derived one:

- **T02-STEP-03** — the suite rebuilds the worksheet rows and
  conflict list from the three sections PILOT-DATA-PACKS-01
  names for T02, read through the pinned CorpusSource, applying
  the authority order stated in the step text (adjudication >
  examiner > implementer) to the sections' stated statuses;
  attempt > 1 adds the adjudication row as the third worksheet
  row. Deep-compared to the artefact.
- **T05-STEP-06 / T08-STEP-04** — original extractions:
  re-derived by running the pinned extractor (rules_engine +
  EXTRACTOR-RULES-02) over the sections the tree's pack names,
  in the suite. failed checks: re-derived by comparing the
  run's own produced draft artefact (the record.json in the
  run's artefacts/ directory — evidence, not procedure)
  field-by-field against those extractions. Deep-compared.
- **T06-STEP-E** — the outcomes map re-derived from the pinned
  corpus by the A–D rules as written in the trees (source
  location, contradiction, support, default), with labels
  cross-checked against PILOT-DATA-EXPECTED-01's T06_KEY (the
  pinned ground truth — the suite reads it from EXPECTED
  rather than carrying its own copy). The full outcome dicts
  (label, decided_at, evidence) deep-compared.
- **T09-STEP-03** — the worksheet recomputed from
  PILOT-DATA-T09-01 by the pinned receipt_worksheet tool (the
  Batch 2 recompute pattern), deep-compared to the artefact's
  worksheet.

Each family's derivation is code in the suite that reads only
pinned data + run artefacts; none calls the driver or reuses
its handlers. If any family's derivation cannot be made
independent in this sense, the plan's fallback is to say so in
the report rather than weaken the comparison silently.

## Item 2 — §4(r): the seven cases, exactly (HIGH)

The suite's (r) block is rebuilt to the spec's enumeration,
each case its own named transcript line, against a scratch
registry holding one unconsumed extraction operation and one
unconsumed citable artefact event, with both consumption sets
snapshotted before and asserted byte-identical after every
refusal, and no LEDGER_ENTRY emitted into the scratch record:

- (r1) `{form: "carried", operation_id}`
- (r2) `{form: "extracted", citation}`
- (r3) a citation accompanied by a caller-supplied value at
  the presentation level (`{form: "carried", citation, value}`)
- (r4) a missing `form` tag
- (r5) an unknown `form` tag
- (r6) a presentation with an unexpected extra field
  (`{form: "extracted", operation_id, note}` — presentation
  level)
- (r7) a presentation carrying both handles
  (`{form: "extracted", operation_id, citation}`)

— every one refusing PRESENTATION_FORM. The round-2 block's
extra forms (bare string, value nested inside the citation
object, the citation naming an extraction event) are retained
as declared EXTRA malformed cases, unnumbered, so nothing
already demonstrated is lost; they are not counted among the
seven. The (i)/(f)/(g)/(h)/(s) sections are unchanged.

## Item 3 — §4(n): the sequence type assertion (MEDIUM)

The per-record sequence check gains the explicit type
assertion: every event's `seq` satisfies `type(seq) is int`
(booleans excluded by construction), alongside the existing
1..N ordering comparison, on every record.

## Item 4 — §4(o): confinement at the spec's wording (MEDIUM)

§4(o): "before/after listing of the pilot root's parent
compared, the only delta being the runs' own directories, and
a scratch `commitments/` directory asserted byte-unchanged
across the suite". The suite's listing now records, for every
file under the pilot root, its **content sha256** (not size);
the parent directory's (/srv) top-level entry names are
compared before/after as well. The commitments-probe stand-in
is deleted; the assertion runs against the actual
`<root>/commitments/` directory: its recursive (path, sha256)
listing is asserted identical before and after the suite. (As
found, the directory is empty and supervisor-owned; the suite
runs as root and can enumerate it. Its state is reported as
found, not staged.) The exclusion set is unchanged (the
correction's own runs/scenarios/tools scratch and the Batch 2
regression scratch).

## Item 5 — generator wording (Alex's documentation correction)

gen_authority2.py's docstring is corrected: the fixture
operation replaces the sections file's final newline with a
space followed by a newline — net increase one byte — it does
not "extend the file by two bytes". The variant entry text in
the authority is already accurate and does not change; no
re-mint follows from a docstring.

## Mechanics

Round-3 bundle at duenna/batch3-correction3-2026-11-13/:
revised suite, revised generator, CONTINUATION-BATCH3-
CORRECTION-3, the new transcript, and the new run records with
ledgers and provenance reports (fresh runs of the same eight
scenarios; driver and authority pins identical to round 2, so
the records' pins match the round-2 bundle's). The round-2
bundle stays immutable. On your approval, the build proceeds
under Ben's existing round-2 build go (the correction's scope
is the same checkpoint; if you judge a fresh go is needed,
say so and I will put the card to him).
