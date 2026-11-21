# Closing Correction Round 2 — Notes

Built 2026-11-21 against Vane's closing-correction examination
(`VANE-CLOSING-CORRECTION-EXAMINATION-2026-11-21.md`: CLOSING
CORRECTION ROUND NOT ACCEPTED — the central provenance repair
passes; two blockers remain), on the pinned brief
`CLOSING-CORRECTION2-DISPATCH-2026-11-21.md`. Sections 1–3 are
recorded before the re-run execution; results follow in §4.
Preserved artifacts are not amended: ca2a8c16, ee235533, and all
accepted Stage 4 rounds stand as shelved; this round's changes
land as new file states here.

## 1. Changed files (planned, with reasons)

**Production:**

- `fabric/engine.py` — CC2-B2: `_is_uuid` widened. Validity is
  now the RFC 4122 textual representation (hyphenated
  8-4-4-4-12 layout, hexadecimal digits of either case) instead
  of equality with the lowercase canonical rendering. Malformed
  values (non-string, bad shape, non-hex) still refuse, and the
  fold still halts `schema_invalid` on them at the same call
  site. Minting is untouched.
- `fabric/checker.py` — CC2-B2: the checker's own `_is_uuid`
  widened to the same contract reading, implemented
  independently (the checker still imports no engine code; its
  import boundary is unchanged).

**Tests / fixtures:**

- `pack_validation.py` — CC2-B1: `chain()` accepts an optional
  fifth spec element pinning an event's `event_id` (the fixture
  form of the harness's CC-1 pre-minted-id plumbing); a new
  `seal_attempt_failed()` canned-spec helper emits a
  SEAL_ATTEMPTED event bearing `ATTEMPT_S1_ID` as its actual
  event_id; the structural-lifecycle fixtures (the shared
  `h_t_specs`/`h_t` and VP-41's `h_t2`) now contain that attempt
  event ahead of the tension, whose `origin_ref` names it;
  VP-42's assertion reads the tension's `origin_ref` against the
  fixture attempt event's actual `event_id` (located by type in
  the chained fixture), not against a literal. The runner
  regenerates `pack-validation-manifest.json` on execution (its
  recorded engine/checker build hashes change because
  engine.py/checker.py changed — expected, and named here in
  advance).
- `closing_correction_tests.py` — CC2-B2: the upper-case UUID
  history moves out of the malformed (halt) set into a positive
  case (folds cleanly in both folds, record carrying it
  verbatim); the module docstring's round-1 canonical-form
  paragraph is replaced with the corrected line. Suite
  composition changes from 16 checks to 15: four malformed
  histories × two folds = 8 halt checks (was five × two = 10),
  three positive fold checks (was two), four live binding
  checks (unchanged). Net −1, caused entirely by the case move
  Vane's B2 required.

**Not changed:** any earlier notes or reports; the closing
lifecycle artifacts (see §3); all other suites.

## 2. CC2-B1 — sibling-case audit

Standard applied: wherever an assertion claims an
origin/resolution correspondence, the referenced ID must be the
`event_id` of an actual SEAL_ATTEMPTED event present in the
same fixture/run.

- **VP-42 (canned)** — was the defect: asserted `origin_ref`
  against the literal `"caca0000-0000-4000-8000-000000000005"`
  with no SEAL_ATTEMPTED event in the fixture. REPAIRED as
  described in §1: the fixture now carries the attempt event
  bearing that ID, and the assertion compares against the
  event's `event_id` read from the fixture.
- **VP-39, VP-40, VP-43, VP-44 (canned)** — same fixture family
  (`h_t` / `h_t_specs`); none asserts an `origin_ref`
  correspondence (they assert attachments, raises, resolutions,
  outcomes). The shared fixture now contains the raising
  attempt, so the standing tension's provenance is a real event
  in the same history even where unasserted. No assertion
  changed.
- **VP-41 (canned)** — its own fixture (`h_t2`) carried the
  same literal with no attempt event; it asserts attachments
  only. The attempt event was added to `h_t2` on the same
  fixture-honesty standard; no assertion changed.
- **VP-31 (live)** — already meets the standard: asserts the
  raised tension's `origin_ref` equals the actual failing
  attempt event's `event_id`, read from the same run's store.
  Unchanged.
- **VP-32 (live)** — already meets the standard: asserts the
  resolution evidence's `seal_attempt_event_id` equals the
  actual passing attempt event's `event_id` (with
  `seal_attempt_seq` alongside as diagnostic). Unchanged.
- **VP-45 (live)** — already meets the standard: step (3)
  asserts `origin_ref` against the failing attempt's
  `event_id`; step (8) asserts the evidence's
  `seal_attempt_event_id` against the passing attempt's
  `event_id`. Unchanged.
- **Pure fold-validation cases** — the canned histories built
  with `tension_raised`'s default `origin_ref`
  (`"caca0000-0000-4000-8000-000000000004"`: the VP-06..VP-14
  schema/protocol family, VP-11a/b, VP-12a/b, VP-13a/b/c)
  contain no seal attempt and claim no origin correspondence;
  they exercise the folds' schema and transition rules, and the
  default is a format-valid canned UUID so the CC-3 format rule
  fires only where a case makes it the subject. No
  correspondence is claimed and none is asserted in these
  cases; the helper default is retained unchanged.
- **Remaining live pack cases** (VP-30, VP-33, VP-34/46,
  VP-36/37/38, VP-48/49) assert no origin/resolution
  correspondence (attempt counts, payload shapes, facet and
  tension states); nothing to repair.

## 3. CC2-B2 — the line taken, and the lifecycle

**The line:** validation follows the pinned `format: "uuid"`
contract as written. Rev 9 §3 makes `origin_ref` an id field
and Annex B types ids as `format: "uuid"`; neither text
restricts the rendering to lowercase canonical form. A value is
therefore valid iff it is a string in an RFC 4122 textual
representation of a UUID — the hyphenated 8-4-4-4-12 layout
with hexadecimal digits of either case. Upper- and mixed-case
renderings are accepted; non-strings, wrong shapes and non-hex
values still halt `schema_invalid`. (The validators also refuse
the brace, `urn:` and bare-32-digit forms `uuid.UUID` would
tolerate: those are not the textual representation the schema
names.) This is Vane's option (a); **no amendment was sought or
made**, and the pinned schema and validation authority are
untouched. Minting is unchanged — the system still mints
lowercase canonical IDs; only validation widened.

**The integrated lifecycle stands, re-verified rather than
re-driven.** The production change widens what the folds
accept; it cannot alter the behaviour of the correction
round's exported history
(`closing-lifecycle-history-correction.json`), whose every
reference is a minted lowercase canonical ID. Re-driving would
mint fresh IDs and produce a different history without testing
anything new. Instead, the standing history is re-verified
under the widened folds in §4: both folds fold it cleanly, its
hash chain and anchor reconciliation are recomputed, and the
seq-30/seq-37 provenance bindings are re-asserted against the
actual attempt event_ids.

## 4. Results

All runs executed 2026-11-21 after the §§1–3 record above.
Counts are each suite's own; no baseline count shifted
anywhere except the negative suite's composition, whose cause
is the CC2-B2 case move itself (§1).

**Validators (direct probe, before the suites):** both
`_is_uuid` implementations probed on 13 values — lowercase,
upper-case and mixed-case hyphenated UUIDs accepted; the
sequence label, integer, None, empty string, bare 32-digit,
braced, `urn:`-prefixed, non-hex, mis-hyphenated and short
forms refused — engine and checker in agreement on every one.

**Negative suite (`closing_correction_tests.py`): 15/15** in
the new composition — 8 halt checks (four malformed histories
× two folds, each halting `schema_invalid` at the offending
sequence), 3 positive fold checks (well-formed UUID; the
upper-case UUID, moved here by CC2-B2, folding cleanly in both
folds with the record carrying it verbatim; the
nonexistent-record UUID), 4 live binding checks (CC-1 ×2,
CC-2 ×2). Round 1's composition was 16 (10 halt + 2 positive
+ 4 live); the −1 is the case move, named in §1.

**Complete pack (`pack_validation.py`): 64/64 case records
pass.** VP-29 recomputed over the dual-applicable set: **54
compared, zero disagreements, zero unmarked**, exclusions
unchanged (VP-22, VP-23, VP-28, VP-50..VP-54, VP-55). The
affected family passes in full: VP-39, VP-40, VP-41, VP-42,
VP-43, VP-44 — and VP-42's recorded fixture now shows the
correspondence it asserts (fixture layout RUN_OPENED →
SEAL_ATTEMPTED → TENSION_RAISED; the tension's `origin_ref`
equals the attempt event's `event_id`,
`caca0000-0000-4000-8000-000000000005`, verified by rebuilding
the fixture from the runner's own helpers and folding it).
VP-31, VP-32, VP-45 pass with their live correspondence
assertions unaltered. The regenerated manifest's engine and
checker build hashes differ from round 1's, as §1 foretold:
the two validator files changed.

**TV-1..TV-20 (`closing_tv_tests.py`): 45/45.**

**Integrated lifecycle — re-verified, not re-driven** (the
§3 reasoning): the correction round's exported history
(`closing-lifecycle-history-correction.json`, 38 events) was
recomputed under the widened folds. Every event hash
recomputes from its body and the chain links hold end to end;
the canonical-events SHA-256 (`7dc3a6d2…`) matches
`closing-anchor-correction.json`, whose `chain_head_at_close`
is seq 37's hash and whose `closing_event_hash` is
RUN_CLOSED's own; both folds fold the history cleanly and
their state hashes agree; the anchor's genesis state hash is
the pinned constant (`9a7250bde82bfd8b…`, unchanged). The
provenance bindings re-assert exactly: seq 30's `origin_ref`
== seq 29's `event_id` (`e638d13e-2e82-46fb-a598-87837f1fca11`);
seq 37's evidence `seal_attempt_event_id` == seq 36's
`event_id` (`7bedde34-d6a9-4e16-a5b9-3b12bbc502ba`).
RUN_CLOSED's `final_state_hash` equals the state hash of the
fold through seq 37 — the state the close certifies, before
the closing event itself is folded in.

**Stage 4 suites:** `stage4_tests.py` all pass (22 PASS
lines); `stage4_corrections_tests.py` 24/24;
`stage4_correction2_tests.py` 21/21.

**Regressions: 391 at baseline, per-suite identical** —
stage1 smoke 18, stage2 40, stage2 corrections
53/27/34/32/37/31, stage3 71, stage3 corrections 37, observer
export safety 11; every suite exits 0 with its ALL PASS
summary.

**Changed-file list, final:** `fabric/engine.py`,
`fabric/checker.py` (CC2-B2 validators); `pack_validation.py`
(CC2-B1 fixture + assertion repair) and the regenerated
`pack-validation-manifest.json`; `closing_correction_tests.py`
(CC2-B2 case move + docstring line); this notes file (new).
Nothing else in the prototype tree was edited by this round.

**Nothing could not be implemented as specified.** The one
judgment call inside the brief's latitude: the validators
refuse the brace, `urn:` and bare-32-digit forms that
`uuid.UUID` would tolerate, on the ground stated in §3 —
they are not the RFC 4122 textual representation the pinned
`format: "uuid"` names. It stands here and in both docstrings
for the examiner's judgment, exactly as the round-1
canonical-form line stood before it was withdrawn.
