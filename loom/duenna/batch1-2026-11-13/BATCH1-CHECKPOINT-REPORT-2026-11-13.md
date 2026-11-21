# BATCH 1 CHECKPOINT REPORT — Corpus interface and pilot data

**Build:** Stage 5 (STAGE5-BUILD-SPEC-13, shelf pin bab720b2,
sha256 ebefa4a1…). **Batch:** 1 of 7 — Corpus interface and pilot
data (Spec §4). **Environment:** the Ubuntu room on Ben's laptop
(accepted by Alex, pb-mwep7new; Batch 0 re-run passed there,
894bde0b). **Authorisation:** Ben's go, 2026-11-13 ~00:22 MST —
tap on the Batch 1 scope card and his words "Start Batch 1 in the
Ubuntu room — that's my go" (scope ledger). **Visibility:** every
stage ran inside the standing watch window (tmux session raised by
the watch-window service; Ben attaches read-only), per Ben's
visibility ruling of the same night. **Subject contact:** none —
no provider contact, no model call; Stage 5 uses a scripted stub
and Batch 1 builds data and interfaces only.

## What §4 required, and what stands

1. **`CorpusSource` over the snapshot + pilot-manifest data (§3.2 /
   Harness §3.1).** Built: `corpus_source.py` — one implementation,
   reading only the two directories it is handed (the Batch 0
   snapshot in the room freeze; the Batch 1 data files). Bare
   section ids resolve against the corpus; `pilot-manifest:` refs
   resolve against the data files; a bare doc id resolves to its
   corpus manifest row. Contract tests: **10/10 PASS** (in-room
   log: batch1-corpus.log) — section resolution incl. all 13 pack
   section refs; pilot-manifest resolution of every pack fixture
   and receipt ref; NOT FOUND returned as a value (never an
   exception, never a fabricated record) for unknown sections,
   unknown fixture keys, and cross-namespace misuse; the module's
   own source carries no reference to the live index, the shelf,
   or the trial runner (the §3.2 runtime-path rule, tested).
2. **The four pilot data files, transcribed from the pinned
   `run_ab.py` constants and verified value by value (§3.3).**
   Transcription was by AST only — the trial runner was never
   imported or executed (its module level loads the live corpus
   and prepares model calls; neither entered the pilot). A
   restricted evaluator walked the constant constructions (packs,
   fixture texts, the four receipts incl. the `dict()` copy, the
   FR-B comprehension and the FR-A hash slice, `p_t09` per
   variant). Verification ran by a second, independent path
   (CPython `literal_eval` over source spans for the literal
   constants; structural invariants for the constructed ones;
   full pack rendering from the refs alone): **19/19 PASS**
   (batch1-transcription.log). The T09 gate decisions recompute
   from the data files alone: FR-A REJECT, FR-B REJECT, FR-C
   REJECT, FR-VALID CLOSE — as designed. The 12 rendered pack
   hashes are recorded in the amendment continuation (T01 and
   T05 packs are identical — one section each — and hash
   identically, as they should).
3. **`EXTRACTOR-RULES-02` finalised over every field the trees
   name (§3.2).** Six rules as data (schema exactly
   `{field, rule_id, pattern, group, value_type, version}`): the
   four V2 fields plus `version` (T05-STEP-02) and `correction_b`
   (T05-STEP-03) — the further fields the V2 process trees name
   as extraction fields. Checkpoint exercises: **12/12 PASS**
   (batch1-rules.log) — reproduction of all six extractions
   against PILOT-DATA-EXPECTED-01 ground truth on the pinned
   sections; AMBIGUOUS on a synthetic two-match section; TYPE
   FAILURE on a synthetic type-defeating section; the mixed
   valid/invalid case EXTRACTED with the rejection recorded;
   NOT FOUND for an absent field and for an undeclared field.

## Finding F-B1-1 — V2's `fixtures_passed` rule was silently ambiguous

V2's pattern `(\d+) PASS` matches **twice** on its own pinned
section (`r60-revision-change-record#009`): "38 PASS" in the
suite summary line and "37 PASS" in the FX-R60l sabotage line.
V2's `re.search` took the first match silently — the correct
value by position, not by rule. Under the pilot's §3.2 semantics
(count all valid matches; no tie-break of any kind) the original
pattern yields **AMBIGUOUS** with candidates [38, 37] —
demonstrated in the checkpoint exercises. This is Alex's
correction D instantiated in the programme's own record.

Remedy taken, per §3.2's stated remedy (a sharper pattern,
declared): rule EXT02-FP-2 anchors on the document's summary
clause — `fixtures executed, ([^\s*]+) PASS` — which matches
exactly once on the pinned section and reproduces the ground
truth (38). The sharpening, its reason, and the superseded
pattern are recorded here and the rule carries its own rule_id;
nothing was selected silently. Alex's adjudication of the
finding and the remedy is requested at this checkpoint.

A related construction decision, declared for the same review:
§3.2's semantics test each match's group against `value_type`
as a separate stage, so the rules' patterns capture the
presented token at the field's presentation site and the type
test judges it. (With V2's literal patterns — which pre-filter
by type inside the regex — TYPE FAILURE would be unreachable
and §3.2's four-outcome table dead letter.) On the pinned
sections the declared rules' behaviour is identical to V2's,
proven by the reproduction exercises.

## Builder's decisions (recorded for review)

- **D-B1-1, pack form.** PILOT-DATA-PACKS-01 holds, per tree,
  the item list as references — bare section ids and
  `pilot-manifest:` refs — per §3.3's own definition ("the list
  of corpus section ids (and pilot-manifest refs) constituting
  its pack"). Section texts are not duplicated; the snapshot
  remains the single source. Fixture texts live exactly once,
  in the data files. Per-tree task texts (from `TESTS`,
  incl. SCHEMA_TASK) are carried in the same file: §3.3 retires
  the runner's constants wholesale, and the tasks have no other
  declared home.
- **D-B1-2, NOT FOUND shape.** CorpusSource returns NOT FOUND
  as a value of a declared shape (`verification` /
  `source_ref` / `failure_reason`), mirroring the tool-result
  schema the tools will map onto in Batch 2.
- **D-B1-3, rules coverage boundary.** T02's and T03's trees
  speak of extracting "the dispositions" / status claims per
  source, T04 of extracting action lists from the arm fixture,
  and T09-STEP-01 of extracting the obligation spec's elements
  from structured pilot data. No deterministic field rules are
  honestly definable for those prose targets, and V2 had none;
  they remain **NOT FOUND by declared design**, visible here
  rather than buried. If Alex rules any of them in scope, a
  rules amendment adds them by declaration.

## Pins (Batch 1 artefacts; re-freeze continuation, same date)

Recorded in `PILOT-MANIFEST-01-REFREEZE-AMENDMENT-2026-11-13-
CONTINUATION-BATCH1.md`: the four data files, EXTRACTOR-RULES-02,
and corpus_source.py, each by sha256 — plus the 12 pack hashes
and the checkpoint machinery hashes. The Batch 0 freeze and all
earlier amendment files are untouched.

## Checkpoint statement

Every Batch 1 checkpoint condition in Spec §4 is satisfied on
the evidence in this bundle: interface contract tests pass;
data-file transcription verification is complete and recorded;
the rules data reproduces the four V2 fields' behaviour on the
pinned sections and produces AMBIGUOUS and TYPE FAILURE on the
synthetic exercises, run early as §4 directs. One finding
(F-B1-1) is carried to the reviewer with its remedy declared.

**BATCH 1: checkpoint conditions satisfied — submitted for
Alex's between-batch review. Batch 2 is not started and is not
authorised by this report.**
