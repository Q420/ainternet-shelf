# Closing Correction Round — Notes

Correction round built 2026-11-21 against Vane's integrated
examination of the closing exercise
(`VANE-CLOSING-EXAMINATION-2026-11-21.md`: CLOSING EXERCISE NOT
ACCEPTED — one linked structural-provenance blocker, B1 + B2), on
the pinned brief `CLOSING-CORRECTION-DISPATCH-2026-11-21.md`.
The closing package at shelf ee235533 and the three accepted
Stage 4 rounds (a99a7676, e46d47d0, ffc0af1f) are preserved
unchanged; this round's report lives here, not in
CLOSING-REPORT.md (which is not rewritten).

The defect, in her words' substance: a checker-origin structural
tension's `origin_ref` carried `"seal-attempt:<seq>"` — a string
naming a sequence, not the UUID Rev 9 §3 requires of an id field —
and neither fold validated the format, so a hash-valid event
violating the field type folded cleanly in both implementations.
The matching resolution evidence cited `seal_attempt_seq` where
Rev 9 §7, Brief Rev 2 §3 and pinned pack VP-42 require the
passing attempt's event ID. Sequence and event ID are separate
fields; they are not interchangeable.

## The corrections

**CC-1 — origin_ref binds the triggering attempt's UUID.** The
SEAL_ATTEMPTED event's id is minted by the harness before commit
(`attempt_event_id`) and carried into the store as that event's
actual `event_id` (the commit path accepts a pre-minted id on a
spec; every other event's id is still minted by the store as
before). The checker-origin TENSION_RAISED built in the same
atomic group names that id as its `origin_ref`. The group's
atomicity is unchanged: one commit, the id known to the producer
before the group is built. The other two origin_ref producers
already bind UUIDs (contribution origin → the contribution_id;
examination origin → the examination_id) and are unchanged.

**CC-2 — Resolution evidence binds the passing attempt's
event_id.** The structural TENSION_STATUS evidence gains
`seal_attempt_event_id`, carrying the passing attempt's actual
`event_id`. `seal_attempt_seq` remains in the evidence as
supplementary diagnostic information, exactly as the brief
permits; it no longer stands as the binding reference. All
structural resolutions flow through the one evidence shape in
`_seal_step`, so S1/S2/S3 resolutions all carry the new field.

**CC-3 — Both folds validate origin_ref as a UUID.** In the
engine fold (`fabric/engine.py`) and, independently, in the
checker fold (`fabric/checker.py`): a TENSION_RAISED whose
`origin_ref` is not a well-formed UUID halts replay at the
offending sequence with reason class `schema_invalid` — hash
validity notwithstanding, since the malformed value sits inside
the hashed payload. **The line taken, stated plainly: format
validation is the contract.** "Well-formed" means the canonical
UUID string form — the only form any producer in this system
mints (`str(uuid.uuid4())`). Whether the named record exists is
a different question: a UUID-shaped reference to a nonexistent
record is NOT halted by this rule, and no fold rule answers for
it. The check sits after the existing type/origin/status checks
in both folds, so every previously pinned halt (VP-07, VP-10,
VP-11 and the Stage 4 hardening negatives) still fires on its
own field first.

**CC-4 — Event-ID assertions in the named cases.** TV-1, TV-6,
TV-13 (closing_tv_tests.py) and VP-32, VP-42 (pack_validation.py)
now assert exact event-ID correspondence: a raised structural
tension's `origin_ref` equals the triggering attempt's
`event_id`, and a resolution's `seal_attempt_event_id` equals
the passing attempt's `event_id`. The closings driver's beat-6
checks and pack VP-31 / VP-45 (the same live binding family, in
files this round is authorised to edit) assert it too. The
pre-existing `seal_attempt_seq` assertions in those files stand
as diagnostic checks (the field remains present and correct);
in stage4_tests.py, stage4_corrections_tests.py and
stage4_correction2_tests.py the seq assertions were left
untouched for the same reason — seq-as-diagnostic, not
seq-as-binding. VP-42's canned form produces verdicts, not
events, so its correspondence is asserted at the fixture
binding: the standing tension's `origin_ref` is the canned
raising attempt's UUID (a constant), and CC-3's fold rule is
what makes a non-UUID binding unfoldable; the live form of the
same binding is asserted in VP-32 and VP-45.

**CC-5 — Re-run everything, lifecycle re-driven.** The pinned
pack, the full TV-1..TV-20 suite, all prior regressions, and
the integrated closing lifecycle re-driven through the real
service. The BOUNDARY_PROBE summary (fabric/service.py) no
longer claims the probe ran "before this run opened": it now
states the attestation stands at the head of the run, recorded
after the run opened and before agent admission (the probe
itself ran against the disposable twin). The re-driven
artifacts are new files alongside the preserved round's:
closing-lifecycle-history-correction.json,
closing-lifecycle-narrative-correction.md,
closing-anchor-correction.json.

## Changed files

Production:
- `fabric/store.py` — `append` accepts an optional pre-minted
  `event_id`; absent one it mints as before.
- `fabric/engine.py` — `commit_events` carries a spec's optional
  fifth element (the pre-minted id) through to the store; the
  fold validates TENSION_RAISED `origin_ref` as a UUID
  (schema_invalid halt) via a new `_is_uuid` helper.
- `fabric/checker.py` — the independent fold validates
  `origin_ref` the same way, with its own helper; no engine code
  is imported (the VP-28 import boundary is untouched).
- `fabric/harness.py` — `_seal_step` mints the attempt's
  event_id before commit, binds it as the SEAL_ATTEMPTED spec's
  id, as the raised tensions' `origin_ref`, and as the
  resolutions' `seal_attempt_event_id`; `apply_hypo` carries a
  spec's pre-minted id into the staged/planned event records.
- `fabric/service.py` — the BOUNDARY_PROBE summary's ordering
  wording corrected (CC-5); no behavioural change.

Test files edited under this round's authority, each with its
reason:
- `closing_tv_tests.py` — CC-4 event-ID assertions in TV-1,
  TV-6, TV-13 (assertions encoding seq-as-binding).
- `pack_validation.py` — CC-4 assertions in VP-31 (origin_ref),
  VP-32 and VP-45 (resolution event_id), VP-42 (fixture
  binding); CC-4 fixture rule: the `tension_raised` helper's
  default origin_ref and the three canned structural fixtures'
  `"seal-attempt:0"` were string refs representing VALID
  histories and are now a canned UUID.
- `closing_exercise.py` — CC-5: beat-6 checks assert the
  event-ID bindings; beat-2 wording aligned to "before agent
  admission"; outputs take a filename suffix so the re-driven
  artifacts land as new files alongside the preserved round's.
- `stage3_tests.py` — CC-4 fixture rule only: the canned
  structural tension's `"canned-seal-attempt"` origin_ref
  represented a valid history; it is now a canned UUID. No
  assertion changed.
- `stage4_tests.py` — CC-4 fixture rule only: `sem_tension`'s
  `"canned"` origin_ref represented valid tension records (the
  negatives' defects live in other fields / later events); it
  is now a canned UUID. No assertion changed.
- `stage4_corrections_tests.py` — CC-4 fixture rule only: the
  canned S2 tension's `"seal-attempt:2"` origin_ref represented
  a valid history; it is now a canned UUID. No assertion
  changed.

New files:
- `closing_correction_tests.py` — the CC-3 negative suite
  (hash-valid malformed origin_ref halting schema_invalid at
  the offending sequence in BOTH folds; the format-only line
  shown by a UUID-shaped nonexistent reference folding cleanly)
  plus live CC-1/CC-2 binding checks through the harness.
- `CLOSING-CORRECTION-NOTES.md` — this file.
- The re-driven closing artifacts (CC-5), listed above.

No other suite file was edited. `CLOSING-REPORT.md` and every
earlier notes file are untouched.

## Results

Executed 2026-11-21 after the corrections above. Every count is
the suite's own, from a full clean run; counts are reported
separately per the brief, and **no baseline count shifted
anywhere** — the three fixture edits changed canned values, not
check counts, and the CC-4 assertion work strengthened existing
checks in place.

- **New suite `closing_correction_tests.py`: 16/16.** CC-3: the
  five malformed-origin_ref histories (sequence label at seq 2;
  sequence label at seq 3 after a valid tension; integer ref;
  missing ref; upper-case non-canonical UUID) each halt
  `schema_invalid` at the offending sequence in BOTH folds
  (10 checks); a well-formed UUID folds cleanly in both, record
  verbatim (1); a UUID-shaped nonexistent reference folds
  cleanly in both — the format-only line (1). CC-1/CC-2 live
  (4): the raised tension's origin_ref is the failing attempt's
  event_id in the event and in the folded record; the
  resolution evidence's `seal_attempt_event_id` is the passing
  attempt's event_id, with `seal_attempt_seq` present and
  naming the same attempt.
- **Pinned pack: 64/64 records pass.** VP-29 recomputed over
  the dual-applicable set: 54 compared, zero disagreements,
  zero unmarked; exclusions unchanged (VP-22, VP-23, VP-28,
  VP-50–VP-54, VP-55). VP-31, VP-32, VP-42 and VP-45 pass with
  the new event-ID assertions in force; VP-28 (checker import
  boundary) passes — the checker's new helper uses only the
  standard library.
- **TV-1..TV-20 suite: 45/45** — the same 45 checks, with
  TV-1, TV-6 and TV-13 now asserting the event-ID bindings
  inside them.
- **Closing lifecycle re-driven** (`closing_exercise.py
  -correction`, through the real socket service): all beats
  pass; 38 events, the same shape as the preserved round
  (RUN_OPENED 1, BOUNDARY_PROBE 1, DISCOVERY 7,
  CONTRIBUTION_ACCEPTED 4, CONTRIBUTION_REJECTED 1,
  EXAMINATION_RECORDED 1, TENSION_RAISED 2,
  ASSESSMENT_RECORDED 3, COMPLETION_CLAIMED 2, FACET_STATUS 8,
  IDLE 1, SEAL_ATTEMPTED 4, TENSION_STATUS 2, RUN_CLOSED 1).
  The provenance values, read directly from
  `closing-lifecycle-history-correction.json`: seq 30's
  TENSION_RAISED carries `origin_ref`
  `e638d13e-2e82-46fb-a598-87837f1fca11`, exactly seq 29's
  SEAL_ATTEMPTED `event_id`; seq 37's resolution evidence
  carries `seal_attempt_event_id`
  `7bedde34-d6a9-4e16-a5b9-3b12bbc502ba`, exactly seq 36's
  SEAL_ATTEMPTED `event_id`, with `seal_attempt_seq` 36
  retained as diagnostic. The chain verifies link by link
  (seqs 1–38, every prev_hash matching); the regenerated
  anchor reconciles the same way as the preserved round's
  (chain_head_at_close = seq 37's hash, closing_event_hash =
  RUN_CLOSED's own, the canonical-events digest recomputes
  from the exported history, genesis state hash the pinned
  constant). The seq-2 narrative line now reads "recorded
  after the run opened and before agent admission". The
  preserved round's local artifacts are untouched — its seq 30
  still carries `"seal-attempt:29"`, as the record of the
  examined defect requires.
- **Stage 4 suites:** stage4_tests 22 PASS lines;
  stage4_corrections_tests 24/24; stage4_correction2_tests
  21/21 — all unedited this round except the one canned-fixture
  value in stage4_corrections_tests named above.
- **Regressions: 391 total, per-suite counts identical to
  baseline** — stage1 18, stage2 40, stage2 corrections
  53/27/34/32/37/31, stage3 71, stage3 corrections 37,
  observer 11.
- **Genesis state hash unchanged:**
  `9a7250bde82bfd8b…` (beat 1 of the re-driven lifecycle and
  the regenerated anchor both carry it).

Nothing in the brief could not be implemented as specified.
Two judgment calls stand on the record for the examiner: the
canonical-form line in CC-3 (an upper-case or otherwise
non-canonical UUID rendering halts as schema_invalid — it is
not a form any producer in the system mints; the negative
suite documents it), and VP-42's canned-level assertion form
(the correspondence is asserted at the fixture binding because
the canned evaluators return verdicts rather than events; the
live event form is asserted in VP-32 and VP-45).
