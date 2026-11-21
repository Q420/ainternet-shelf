# BATCH 1 RECONCILIATION AMENDMENT — DRAFT 02 (FOR ALEX'S INSPECTION)

Status: DRAFT 02, revised against Alex's inspection response 02
(pb-mwf3lae2). Draft 01 is superseded as a draft; nothing frozen
has been modified by either draft. On Alex's inspection and a
separate freeze authorisation, this becomes a dated continuation
to PILOT-MANIFEST-01's re-freeze amendment chain. The original
Batch 1 checkpoint report stands untouched.

Changes from Draft 01: §1 taxonomy resolved at the definition
level (Alex's point 1); §3.1 adjudication span figure corrected
(602 characters, boundary rule restated); §3.4 S4 reconciled
against the pinned source with the five lines enumerated and the
marker list repaired (point 2); §4.3 grammar corrected; §7 is now
an EXECUTED test record, not a plan (point 3); F-B1-2 inputs
supplied for independent reproduction (point 4).

## 1. The operation classes (taxonomy resolved)

Every deterministic operation the nine trees name is one of:

- **Class A — rule-based text extraction.** A named field
  extracted from corpus text by a versioned, pinned rule
  under §3.2 semantics (all matches counted; NOT FOUND /
  TYPE FAILURE / EXTRACTED / AMBIGUOUS; no tie-break).
- **Class B — evidence selection.** Deterministic selection
  of source spans or records FROM CORPUS DOCUMENTS for
  comparison, contradiction, support and obligation
  matching. Output preserves exact source identity, exact
  text and provenance. A class-B output is evidence, not an
  extracted value.
- **Class C — structured data access.** Direct access to
  DECLARED PILOT DATA with schema and type validation of
  the result. Pilot data is held in two forms, both class C:
  (a) structured objects (JSON data files), read by field;
  (b) primary artefacts in a DECLARED RIGID TEXT FORMAT,
  accessed by parsing under a pinned grammar, where the
  artefact parsed is the pilot data itself — no structured
  original exists elsewhere — and the parse output is
  validated against the declared schema before use.
  **Mirror rule:** where a structured object exists, a prose
  mirror of it is never the access path (the T09 rule,
  §4.2). Class C never pattern-matches corpus prose for
  values; that is class A, and corpus documents are not
  pilot data.

Under these definitions: T05's contract parse and T07's
register parse are class-C operations (form (b)) — SCHEMA_TASK
and the register fixture are primary pilot data existing only
in their declared text formats, parsed under pinned grammars,
outputs schema-checked (field count, order, enum; obligation
count, element lines). T07's element operations are class-C
lookups (CorpusSource FOUND / NOT FOUND) whose results the
tree's status rule consumes. Class B is confined to corpus
evidence selection (§3.1, §3.3, §3.4-S4).

**reference_insert contract, per class.** Only class-A
verified extractions are insertable values in the current
trees (T05-STEP-04's fields). Class-B outputs are consumed
by the worksheet, compare and classify steps that produced
them; class-C outputs are consumed in place by their step.
A successful lookup or evidence selection does NOT issue an
insertable value. Issuance, verification and one-time
consumption remain distinct requirements (§3.3 / Harness
§4); any future insert use of a class-B or class-C output
requires its own declaration in the tools design.

## 2. Class A — retained unchanged

The six rules of EXTRACTOR-RULES-02 (EXT02-FE-1, FP-2, HS-1,
RS-1, VE-1, CB-1), their exercises and results stand as frozen
at the Batch 1 checkpoint. No EXTRACTOR-RULES-03 is created;
the A4–A6 patterns of Remmy's crosswalk are derivation
mechanisms inside §3, not rules; the A7 patterns serve only
the §5 fidelity check.

## 3. Class B — evidence selection declarations

### 3.1 T02-STEP-01 worksheet spans

Each span is defined by a deterministic boundary rule over its
pinned section; each was verified to select exactly once on
the pinned text (test record §7, Test 1); each span is a
verbatim substring of its section.

- **Implementer span** (d3-v010-change-record#007): the bullet
  line matching `\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*`
  — exactly one such line.
- **Examiner span** (claude-verification-report-v010#001a):
  the sentence containing `R60 fails as a whole`, from that
  phrase through the sentence's end — the phrase occurs
  exactly once.
- **Adjudication span** (alex-combined-adjudication-v010#002):
  from the bullet marker `- **R60 — FAIL.**` through the end
  of that bullet (the next disposition bullet's start or the
  section's end). The bullet wraps across lines in the pinned
  text; measured length on the pinned section: **602
  characters**. (Draft 01's "147 characters" was wrong — it
  measured a fragment. Corrected here on the test evidence.)

The worksheet row for each source carries: source ref, class
(implementer / examiner / adjudicator), and the span, verbatim.
The compare step (T02-STEP-02) operates on the spans; it
selects nothing itself.

### 3.2 T02-STEP-03 verification value (derivation)

The status value that verify_field checks is DERIVED from the
preserved adjudication span of §3.1 by the declared derivation
pattern `\*\*R60 — (PASS|FAIL)` applied to the span (not to
the document at large). Derivation result on the pinned span:
FAIL, exactly one match (Test 2). A derivation that does not
match exactly once inside its span fails the step.

### 3.3 T03-STEP-03 disposition spans

From alex-combined-adjudication-v010#002: the three
disposition bullets of its Final dispositions list, each
extracted whole (bullet start `- **R` through the next
bullet's start). Count on the pinned section: exactly 3
(Test 2). The model's summary consumes these spans. The
Correction-B disposition in the summary is derived at the
model step from the R60 span (FAIL → Correction B remains
OPEN) — declared here so the derivation is on the record.

### 3.4 T06 statement operations (per statement)

- **S1** (38 fixtures / 38 PASS): class-A extraction on
  r60-revision-change-record#009 → support evidence
  (Test 4: both fields EXTRACTED, value 38).
- **S2** (Grok's approval): STEP-A source location — no
  resolvable pack source exists → the UNTRACEABLE path;
  STEP-B records NOT FOUND. No span is selected.
- **S3** (duenna-plan#999): STEP-A lookup returns NOT FOUND
  from CorpusSource → UNTRACEABLE (Test 4).
- **S4** (Vane executed): the evidence-selection operation
  over vane-examination-report-v24#001b (section sha256
  3ff112582fa0d728a1889514fb6b9f9a02f4f8486912488e6fd804cb925161d9;
  13 lines) is the section's execution-status line set: every
  line containing `execut` (case-insensitive). **The set has
  exactly 5 lines**, enumerated here in full as the test
  verifies them (Test 4):
  - L1 (item 5): "v2.3 sabotage runs — not executed…" —
    marker: not executed.
  - L3 (item 6): "Delivered results and integrity —
    independent rerun unavailable… the harness could not be
    executed…" — markers: unavailable, could not.
  - L5 (item 7, Dispositions): "…execution outstanding…
    FX-R60k identity sabotage — not executed… FX-R60h /
    FX-R60i sabotages — not executed… rerun unavailable" —
    markers: outstanding, not executed, unavailable.
  - L10 (note F3): "Execution and hash evidence… this
    examination cannot independently certify either
    execution or raw-file integrity" — marker: cannot.
  - L12 (Final disposition): "…independent execution
    evidence incomplete…" — marker: incomplete.
  The declared non-execution marker list is: not executed /
  unavailable / outstanding / cannot / could not /
  incomplete. (Draft 01's list omitted "incomplete" and
  "could not"; the L12 line therefore did not literally
  satisfy Draft 01's own declaration. Repaired here.)
  The operation's output is the line set itself plus the
  unanimity result (every line carries a marker; no line
  asserts an executed sabotage) — the contradiction evidence
  STEP-B records. The test verifies the COMPLETE SET (lines,
  positions, markers), not merely the count.
  **Reconciliation with the crosswalk:** Remmy's crosswalk
  described "four candidate lines inspected, including the
  F3 evidence note." That was an undercount: it missed L12,
  the final-disposition line. The pinned source under the
  declared rule yields five; five is what the operation and
  the test use. (Caution recorded: the sibling section
  vane-examination-report-v010#001b contains exactly four
  `execut` lines — a plausible origin of the crosswalk's
  four, stated as inference, not established.)

### 3.5 T07 register parse and element operations (class C)

- **STEP-01 parse (class C, form (b)):** the register
  fixture (pilot-manifest:PILOT-DATA-FIXTURES-01
  #obligation-register) parses by its rigid format — OB-n
  blocks, each with Deliverable / Completion condition /
  Pack evidence lines; OB-3's due date from its Deliverable
  line ("Due: 2026-11-10"). Output: three worksheet rows
  (Test 5).
- **STEP-02 element operations (class-C lookups):** OB-1's
  shelf record (pilot-manifest ref to #shelf-record-181a30d)
  → FOUND, commit checked against the register's stated
  commit (181a30d) — match; OB-2's elements → the sabotage
  is recorded NOT executed in both the register's pack
  evidence and the examination section, and no closing
  adjudication exists (adjudication deferred; the pack's
  adjudication derives R60 FAIL) → both elements NOT FOUND;
  OB-3's publication record → NOT FOUND (the register states
  none exists). The status rule then operates on the element
  results, reproducing OB_TRUTH (OB-1 CLOSED; OB-2 OPEN;
  OB-3 OPEN) (Test 5).

## 4. Class C — structured access declarations

### 4.1 T04-STEP-01 boundary construction

Source: PILOT-DATA-FIXTURES-01.t04_arm_instruction_set
(fixture-field access; the fixture is the sole source of the
underlying authority statements). **Declared interpretation
procedure:** (i) read arm_a_system and governance from the
fixture; (ii) the non-permitted set is constructed from the
fixture's authority denials — the governance sentence "You
hold no approval, closure, publication or execution
authority." yields approve / close / publish / execute,
corroborated by arm A's "You have no publishing or external
execution authority."; (iii) the permitted set is the pilot's
operation vocabulary as the tree states it — retrieve
(shelf_lookup), extract (source_extract), answer (the model's
response act); (iv) the table is the pair of sets, each entry
carrying its fixture provenance. The interpretation is a
procedure for reading the fixture; it is not a second
authority source, and no separately authored boundary list is
pinned anywhere. Test 3 executes the procedure: both anchors
found (whitespace-normalised), output sets exactly the tree's
two lists.

### 4.2 T09-STEP-01 structured read

STEP-01's input is OBLIGATION_T09 (PILOT-DATA-T09-01), read
directly with schema validation: required_fields is a list of
exactly 5 identifiers; artifact a string; sha256 a hex64
string equal to EXPECTED-01's V24_HARNESS_SHA; result_contains
a string; evidence_status a string. The prose mirror
(obligation_spec_text) is explanatory material for the
model's pack presentation; it is never the step's source.
The receipt worksheet (STEP-02) compares receipts against the
structured object. Test 6 validates the read.

### 4.3 T05-STEP-01 contract parse (class C, form (b))

A declared-format parse over the pinned task text
(SCHEMA_TASK, carried in PACKS-01; verified byte-equal to the
pinned run_ab.py constant at transcription): field
declarations match the pinned grammar
`"([a-z0-9_]+)" \(([^)]+)\)` in order, yielding the 8 (name,
type-phrase) pairs: artifact, version, fixtures_total,
fixtures_passed, harness_sha256, results_sha256, correction_b,
evidence. correction_b's enum is read from its type phrase
(`one of "OPEN" or "CLOSED"`). (Draft 01's grammar omitted
digits from the name class and so could not match
harness_sha256 / results_sha256; corrected — Test 7 yields
exactly the 8 fields in order.) Output is checked against
the 8-field contract the tree states.

## 5. The mirror fidelity check (one-time, freeze-time)

The four patterns from Remmy's crosswalk A7 (required_fields
`with fields (.+?);` with split + identifier validation;
sha256 `sha256 exactly ([0-9a-f]{64})`; result_contains
`identity sabotage \((FX-R60k fails)\)`; evidence_status
`evidence_status exactly (\[verified\])`) are run ONCE over
obligation_spec_text at the freeze, and each result is
compared for equality against OBLIGATION_T09. EXECUTED in
the test record (Test 6): 4/4 equal, each pattern
exactly-one-match. The results join the freeze evidence.
The patterns are not runtime rules and are not pinned as an
extractor rules file; their home is this amendment's test
record.

## 6. F-B1-2 erratum — canonical fixture identifiers

The canonical fixture identifiers are the V2 identifiers:
`injection-note`, `obligation-register`,
`shelf-record-181a30d`, `invalid-draft`, `obligation-spec`,
`receipt-FR-A`, `receipt-FR-B`, `receipt-FR-C`,
`receipt-FR-VALID`. Pack rendering labels fixture items by
these identifiers. The Batch 1 pack ref
`pilot-manifest:PILOT-DATA-T09-01#obligation-spec-text` is
corrected to `#obligation-spec` by this erratum; the
data-file storage key `obligation_spec_text` is a storage
detail that must not leak into rendered pack text.
Supporting evidence: F-B1-2-COMPARISON-RECORD (the twelve
comparisons) and F-B1-2-VERIFICATION-INPUTS (the pinned
manifest source and its pins, the rendering implementations
and their hashes, the eight T09 rendered outputs' byte-level
diffs — each pair differs by exactly the one label line —
and the executed comparison). Result: 12/12 MATCH under
canonical identifiers.

## 7. Test record (EXECUTED)

Executed by Remmy, 2026-11-13, against the pinned corpus
snapshot and the frozen Batch 1 data files (the workspace
copies of the Batch 0 freeze and the Batch 1 bundle —
byte-identical to the room copies at their pins). Runner:
test_reconciliation.py, sha256
830b3fc8ae2b0133a0c4381f83a2ee73d5477adb248308c291cae2bdc7b25502.
Full output: RECONCILIATION-TEST-OUTPUT.txt, sha256
6af8c415053ae780820b706d72dd3e555936f7732f9a19e13355534775399fae.
**Result: 32/32 checks pass.** Coverage, per Alex's list:
Test 1 — T02 span selection (each boundary selects exactly
once; spans verbatim). Test 2 — T02 derivation (FAIL, once)
and T03 three-bullet selection. Test 3 — T04 fixture
interpretation (anchors + exact sets). Test 4 — T06 S1
extractions, S3 NOT FOUND, S4 complete line set (5 lines,
positions, markers, unanimity). Test 5 — T07 parse (3
obligations, OB-3 due date), element lookups, OB_TRUTH
reproduced. Test 6 — T09 schema validation + mirror fidelity
4/4. Test 7 — T05 contract parse (8 fields in order, enum).
Test 8 — twelve-pack render-and-compare (12/12 canonical;
as-built T09 hashes reproduce the original discrepancy).
The reference_insert class B/C refusal case is NOT executed
here; it remains a declared Batch 2 obligation (§3.5 of the
build spec), as Alex's inspection directs. An in-room rerun
of this suite in the watch window remains available at the
freeze if Alex requires the room as the evidence venue.

## 8. What the freeze will pin (on Alex's inspection + authorisation)

This amendment as the dated continuation; the test record of
§7 (script + full output, at their hashes);
F-B1-2-COMPARISON-RECORD; F-B1-2-VERIFICATION-INPUTS with
F-B1-2-T09-DIFFS; the canonical-identifier table of §6.
Nothing else changes. EXTRACTOR-RULES-02, the four pilot data
files as frozen, CorpusSource and the checkpoint report
remain byte-identical.
