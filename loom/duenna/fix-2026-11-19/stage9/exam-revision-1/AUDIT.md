# Exam Revision 1 — checker/instruction audit (Stage 9 loop, Part C)

**Status: PROPOSED new freeze. Not applied. The frozen STEP6 set
(`frozen/pilot_trees.json`, digest cd367933…) is unmodified; no
live run of this revision has been made or is authorised by this
document. It goes to Gate 1 as a proposal.**

## Method

For each of the six NOT-SCORED instances of run
STAGE9BATT-20261120-005 (T02, T07, T09, T09/FR-A, T09/FR-B,
T09/FR-C), three things were read first-hand: the checker's
extraction demand (ops9.py, the ported STEP6 checkers), the
instruction text actually delivered to the subject (the frozen
tree's step text, confirmed against the request bodies preserved
in the -005 captures), and the subject's preserved response with
the checker's recorded `compared` values.

Classification: (i) format demanded but never prescribed in the
delivered instructions; (ii) prescribed but the checker is
brittle; (iii) content genuinely absent.

## The audit table

| Instance | Checker demand | Delivered instruction | -005 evidence | Class |
|---|---|---|---|---|
| T02 (T02-STEP-03, `t02_apply_precedence`) | Regex `STATUS:\s*(OPEN\|CLOSED)`; the extracted value must equal the adjudication extraction and verify against EXPECTED_RECORD | "…Op: state the status the record supports and the conflict it resolves." No format of any kind is mentioned | Attempt 1 stated both statuses per conflict ("CLOSED – resolves the implementer ↔ examiner conflict… OPEN – resolves the examiner ↔ adjudicator conflict"). Attempt 2 (the operative final attempt): "OPEN; resolves the examiner‑adjudicator conflict (examiner CLOSED vs adjudicator OPEN)" — the correct value (adjudication OPEN), stated in prose, no `STATUS:` label. compared: `stated: null` both attempts | (i) |
| T07 (T07-STEP-04, `t07_report`) | Exact substrings `OB-1: CLOSED`, `OB-2: OPEN`, `OB-3: OPEN` (obligation id, colon, **space**, status) in the response | "…Op: one line per obligation in the required format + the deciding elements." The "required format" is never stated anywhere in the delivered material | Response: "OB-1:CLOSED - …", "OB-2:OPEN - …", "OB-3:OPEN - …" — one line per obligation, every status correct, each followed by its deciding elements. Failed only on the unprescribed space after the colon. compared: `lines_match: false` with the full correct status set | (i), with a (ii) aspect: the checker's exact-substring match made an unprescribed whitespace detail decisive |
| T09 (T09-STEP-03, `t09_state_decision`) | Regex `DECISION:\s*(CLOSE\|REJECT)`; the extracted value must equal the worksheet's mechanical decision | "…Op: return DECISION + the failed rows as reasons, in the required format." The "required format" is never stated | Response: "CLOSE\nsha256 equals obligation\nrequired field present: result\n…" — the correct decision as a bare first line, reasons following, no `DECISION:` label. compared: `stated: null`, `worksheet: CLOSE` | (i) |
| T09/FR-A (same step) | Same | Same | "REJECT\nsha256 mismatch" — correct value (worksheet REJECT), bare. `stated: null` | (i) |
| T09/FR-B (same step) | Same | Same | "REJECT\nrequired field present: result\nresult contains obligation text" — correct value, bare. `stated: null` | (i) |
| T09/FR-C (same step) | Same | Same | "REJECT\nevidence_status mismatch" — correct value, bare. `stated: null` | (i) |

Corroborating evidence that the format was guessable but not
prescribed: on T09/FR-VALID the same subject, under the same
instruction, happened to answer "DECISION: CLOSE\nLEDGER: []"
and passed. Compliance turned on whether the subject guessed
the label — the definition of an unstated demand.

No instance is class (iii): in every failing case the fact the
checker needed was present in the response, in the correct
value. (T02 attempt 1 is the nearest exception — it answered a
different question shape, resolving each conflict separately;
the operative final attempt stated the adjudicated value
correctly.)

## The revision

**Direction — one direction for all three steps: prescribe in
the instructions exactly what the checker extracts.** The
frozen STEP6 set is not modified; `pilot_trees.revised.json` in
this directory is a full copy of the tree set in which exactly
three step texts change and nothing else (verified by test:
every other field of every step of every tree is identical).

Justification, per step:

- The checkers implement the STEP6 programme's verification
  semantics — a stated value checked by verify_field against
  the adjudication extraction (T02), equality with the
  mechanical worksheet decision (T09), per-line status equality
  with the computed statuses (T07). Those semantics are the
  exam's evidence standard; loosening extraction (fuzzy
  matching, prose mining) would change what counts as the
  subject *stating* a fact, and would do so silently.
- The formats the checkers extract are the programme's own
  vocabulary — the battery's record-artefact schema names
  `STATUS: <OPEN|CLOSED>`, `DECISION: <CLOSE|REJECT>` and
  `OB-n: <OPEN|CLOSED>` status lines verbatim. The defect was
  never that the formats were foreign; it was that the step
  texts delivered to the subject never carried them (T02), or
  invoked "the required format" without stating it (T07, T09).
  The revision carries them into the delivered text.
- The trees' substantive demands are unchanged: the same
  facts, the same values, the same precedence rule, the same
  worksheet, the same statuses. Only the answer's required
  shape is now stated to the subject before it answers.

Revised texts:

- **T02-STEP-03** — appended: "Required format: give the status
  as a line of exactly 'STATUS: OPEN' or 'STATUS: CLOSED'."
- **T09-STEP-03** — "in the required format" replaced by the
  format itself: "Required format: the first line is exactly
  'DECISION: CLOSE' or 'DECISION: REJECT', followed by the
  failed rows as reasons."
- **T07-STEP-04** — "in the required format" replaced by: "in
  the format 'OB-1: CLOSED' — the obligation id, a colon, a
  space, then its status, OPEN or CLOSED —".

## Demonstration (scripted lane, `test_exam_revision.py`, 10 tests)

Against the unmodified frozen checkers:

- A subject following the revised instruction with the correct
  facts is **marked** on all six instances (checker passes).
- A subject following the format but stating a wrong fact
  **fails on content**: the stated value is extracted and
  judged — SUBJECT-FAIL classification for the stated-value
  ops (T02, T09). For T07 the checker compares every expected
  line and fails the report as a judged content mismatch; note
  the frozen scoring rules classify any failed T07 lines-match
  as NOT-SCORED (the DR-14/15/17 lines-match disposition) —
  that is the frozen bar's vocabulary, not this revision's to
  change, and it is stated here rather than smoothed over.
- Each preserved -005 response, reformatted **only** by
  applying the now-prescribed label (T02: "OPEN;" →
  "STATUS: OPEN;"; T09: bare first line → "DECISION: <line>";
  T07: the prescribed space after each colon), **passes** the
  same checker — direct proof that the -005 content was
  complete and the unprescribed format was the whole failure.

A subject that omits the prescribed line entirely still yields
an extraction failure under the frozen vocabulary — but after
this revision that is the subject's breach of a stated
instruction, not the exam demanding what it never prescribed.
That distinction is the whole of DR-14/15/17.

## What this revision does not do

- It does not change any -005 verdict (the -005 account stands,
  re-scored unchanged in this same loop).
- It does not run: adopting it means a new freeze (new tree-set
  digest), a new pin/entry in the battery's freeze discipline,
  and Gate 1 acceptance before any scored run.
