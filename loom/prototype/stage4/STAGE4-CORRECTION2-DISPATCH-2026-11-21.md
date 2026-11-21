# Stage 4 Correction Round 2 — Dispatch Brief (pinned)

**Preserved artifacts:** the Stage 4 build round (shelf a99a7676) and correction round 1 (shelf e46d47d0) are NOT amended. This round's changes land as new file states in `~/workspace/loom-prototype/`, shelved separately.

**Authority:** Vane's correction-round examination (`~/workspace/duenna-fix/VANE-STAGE4-CORRECTION-EXAMINATION-2026-11-21.md`): **B1 PASS, B4 PASS** (closed — do not disturb their substance); **B2 NOT CLOSED** (separation incomplete); **B3 NOT CLOSED** (legacy op not mechanically isolated); the S1 genesis-repair half is **ruled formally non-constructible** under the current protocol — record it as such, never as passed.

## Corrections

**C2-B2 — Make the authoritative/snapshot boundary real throughout the service.** The invariant: the TV-1 fault (corruption of the live view) is visible ONLY through the snapshot handed to seal attempts (L). Every other consumer reads the authoritative, history-derived state:
- agent-facing surfaces: `view_pattern()`, `consult_index()`, `open_region()`, `read_breadth()` (and any other agent-facing read in harness.py / service.py);
- admission and its neighbours: `_structural_violation`, staleness, schema cross-field reads (already on the fold — keep);
- commit planning: `_commit_group()` planning and group construction;
- the Stage 3 paths: examine / assess / claim_completion referential and state reads.
The operational live state remains the source of exactly one thing: the attempt snapshot L. The fault hook keeps corrupting only that source. The I-5 repair (explicit replay rebuild) still re-derives the live view; TV-1's lifecycle must still complete genuinely (fault → failed attempt + structural tension → repair → correcting contribution → passing same-check attempt → resolution).
**Required direct tests** (new suite): with the fault injected (a region deleted from the live view) — (i) the region still appears in view_pattern / the read surface (agents do not see it vanish); (ii) read_breadth / open_region behave as on the authoritative state; (iii) a contribution touching other regions passes planning + admission unaffected by the fault; (iv) the seal attempt on that contribution still FAILs S1 in BOTH evaluators with the faulted region in the affected set; (v) the full TV-1 repair path still resolves. Behaviour on unfaulted histories must be identical: all prior suites unedited at baseline counts (regressions 391; stage4 suite all-pass; correction-round-1 suite 24/24; pack 64/64 with VP-29 still 54 compared / zero disagreements — the pack harness's captured (H,B,L) must still reflect the same attempt semantics).

**C2-B2b — The orphan-removal negative test + the non-constructible record.** Add a small negative test: on a genesis carrying a dangling dependency, an attempted contribution removing that dependency is rejected (its endpoint cannot enter the read/write sets) — the limitation made executable. In the round-2 notes, record the S1 fixing half as **formally non-constructible under the current protocol (Vane's ruling)**, alongside the preserved S1 rejection test, the complete S3 rejection/fix path, and the TV-1 live-fault repair path. Do NOT invent a repair operation and do NOT alter Rev 9 semantics.

**C2-B3 — Mechanically isolate the legacy unbound opening.** Remove `open_run_legacy_unbound` from the running service's dispatched operations: the ordinary Stage 4 service must refuse (or simply not expose) the legacy operation — its availability must not rest on a comment, a name, or a per-request flag. Put legacy opening in test-support code that the service never imports/dispatches (the correction suites that need a legacy run construct it there), OR gate it behind a service-construction-time test posture that the ordinary service startup never sets — choose the cleaner of the two and justify it in the notes. The ordinary open_run remains bound regardless of caller-supplied flags (round 1's negative tests keep passing). **Required test:** the ordinary Stage 4 service refuses the legacy operation when invoked as a normal admin request. If any existing suite file would have to be edited to reroute its legacy usage, STOP and report — suites are not edited; reroute via test-support imports only where the suite already imports helpers, otherwise report the conflict.

## Round requirements

- New notes file `STAGE4-CORRECTION2-NOTES.md`: exact changed-file list + explanation per correction; the boundary statement (which paths read authoritative state, which single path reads the live view) recorded BEFORE the new execution; results appended after.
- New tests in a NEW suite file (e.g. `stage4_correction2_tests.py`); no existing suite file edited; `STAGE4-BUILD-NOTES.md` and `STAGE4-CORRECTION-NOTES.md` untouched.
- All prior suites rerun UNEDITED, counts reported separately from this round's: regressions 391, stage4 all-pass, corrections-1 24/24, pack 64/64 (VP-29 unchanged in substance), genesis hash unchanged.
- No closing exercise. No live agents.

**Deliverable:** corrected code + new suite + round-2 notes, reported back with exact counts per suite and anything that could not be implemented as specified — named, never smoothed.
