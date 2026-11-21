# Closing Correction Round — Dispatch Brief (pinned)

**Preserved artifacts:** the closing package (shelf ee235533) and all three accepted Stage 4 rounds (a99a7676, e46d47d0, ffc0af1f) are NOT amended. This round's changes land as new file states in `~/workspace/loom-prototype/`, shelved separately.

**Authority:** Vane's integrated examination (`~/workspace/duenna-fix/VANE-CLOSING-EXAMINATION-2026-11-21.md`): CLOSING EXERCISE NOT ACCEPTED — one linked structural-provenance blocker (B1 origin_ref not a UUID; B2 resolution evidence cites a sequence, not the event_id). Both claims verified first-hand by Remmy against the shipped history and source (harness.py:1486 constructs `origin_ref` as `f"seal-attempt:{attempt_seq}"`; harness.py:1506 writes `seal_attempt_seq` as the resolution evidence). The Stage 4 implementation acceptance remains on record; this round repairs the evidence contract.

## Corrections

**CC-1 — origin_ref binds the triggering attempt's UUID.** In fabric/harness.py, the checker-origin structural tension's `origin_ref` becomes the actual `event_id` (UUID) of the SEAL_ATTEMPTED event that raised it. Any other producer of origin_ref values is aligned to the same rule (origin_ref is an id field everywhere Rev 9 uses it).

**CC-2 — Resolution evidence binds the passing attempt's event_id.** The TENSION_STATUS resolution evidence gains the binding field carrying the passing attempt's actual `event_id` (name it plainly, e.g. `seal_attempt_event_id`); `seal_attempt_seq` may remain as supplementary diagnostic information. The same binding applies wherever resolution evidence is produced (the harness's structural resolution path and any S2/other-check resolution using the same evidence shape).

**CC-3 — Both folds validate origin_ref as a UUID.** In fabric/engine.py's fold AND fabric/checker.py's independent fold: a TENSION_RAISED (or any event carrying origin_ref) whose origin_ref is not a well-formed UUID halts replay at the offending sequence with reason `schema_invalid` — including hash-valid events (the malformed value is inside the hashed payload by construction of the test). Add the negative cases to the new round suite: a hash-valid history with `origin_ref: "seal-attempt:29"` halts schema_invalid at that seq in BOTH folds; a UUID-shaped but nonexistent reference is NOT this correction's concern unless the spec's schema says otherwise (format validation is the contract here — say so in the notes if that is the line taken).

**CC-4 — Event-ID assertions in the named cases.** Assert exact event-ID correspondence (origin_ref == the triggering attempt's event_id; resolution evidence's event_id == the passing attempt's event_id) in: TV-1, TV-6, TV-13 (closing_tv_tests.py), VP-32 and VP-42 (pack_validation.py). This round is explicitly authorised to edit the assertions that encode the old seq-based behaviour in closing_tv_tests.py and pack_validation.py, and in any other suite ONLY where the assertion encodes seq-as-binding (name every edited test file in the notes with the reason; seq-as-diagnostic assertions may stand where seq remains present). All other suites unedited. Canned fixtures that used string origin_refs to represent VALID histories are updated to UUID refs; fixtures representing invalid histories keep their malformed values as negative cases.

**CC-5 — Re-run everything.** The pinned pack (VP-29 still computed over the dual-applicable set; if any baseline count shifts because a fixture's semantics changed, report the shift and its cause explicitly — never silently), the full TV-1..TV-20 suite, the integrated closing lifecycle (re-driven; the new history must show origin_ref as the seq-29-equivalent attempt's UUID and the resolution evidence carrying the passing attempt's event_id), and all prior regressions. The re-driven lifecycle's narrative corrects the probe wording: the probe runs **before agent admission** (after RUN_OPENED), per her observation. The anchor is regenerated for the new history and reconciles the same way.

## Round requirements

- New notes file `CLOSING-CORRECTION-NOTES.md`: exact changed-file list (production + test files separately) with the explanation per correction; the format-validation line taken in CC-3 stated plainly; results appended after execution.
- New tests for CC-3's negative cases in a NEW suite file (e.g. `closing_correction_tests.py`); the CC-4 assertion updates land in the named existing files under this round's authority.
- Counts reported separately: pack, TV suite, closing lifecycle beats, new suite, regressions (391 baseline; stage4 22; corrections-1 24/24; correction-2 21/21) — any deviation from baseline named with its cause.
- Genesis hash unchanged. No live agents.

**Deliverable:** corrected code + updated assertions + new negative suite + re-driven closing package (history, narrative, anchor, report addendum in the new notes — do NOT rewrite CLOSING-REPORT.md; the correction round's report lives in its own notes, with the re-driven artifacts as new files alongside), reported back with exact counts and anything that could not be implemented as specified — named, never smoothed.
