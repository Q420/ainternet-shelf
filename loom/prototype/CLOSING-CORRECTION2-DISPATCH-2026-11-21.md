# Closing Correction Round 2 — Dispatch Brief (pinned, narrow)

**Preserved artifacts:** ca2a8c16, ee235533, and all accepted Stage 4 rounds are NOT amended. This round's changes land as new file states in `~/workspace/loom-prototype/`, shelved separately.

**Authority:** Vane's closing-correction examination (`~/workspace/duenna-fix/VANE-CLOSING-CORRECTION-EXAMINATION-2026-11-21.md`): the central repair PASSES (CC-1, CC-2, CC-3 folds, the regenerated history independently hash-verified by her); two blockers remain. Both of her claims were verified first-hand by Remmy (pack_validation.py's VP-42 literal fixture; engine.py:153's lowercase-canonical comparison).

## Corrections

**CC2-B1 — VP-42 asserts a real event-ID correspondence.** In pack_validation.py's VP-42 case: put a valid SEAL_ATTEMPTED event into the fixture history, carrying the referenced ID as its actual `event_id`; assert the tension's `origin_ref` against THAT event's event_id (read from the fixture event, not a literal). The case remains a canned evaluator case. Check the sibling canned cases that use the same literal pattern (VP-31/32/45 fixtures and the tension_raised helper defaults) and apply the same standard wherever an assertion claims an origin/resolution correspondence: the referenced ID must be the event_id of an actual SEAL_ATTEMPTED event present in the same fixture. Where a canned history legitimately has no attempt event (pure fold-validation cases), no correspondence is claimed and none is asserted — say which cases those are in the notes.

**CC2-B2 — The folds accept valid UUID textual representations (her option (a)).** In fabric/engine.py's and fabric/checker.py's `_is_uuid` (independently in each): validity = the value is a string that parses as a UUID (RFC 4122 textual representation, hexadecimal case-insensitive) — uppercase and mixed-case valid UUIDs are ACCEPTED; malformed values (non-string, bad shape, non-hex) still halt `schema_invalid` exactly as before. Minting is unchanged (the system mints lowercase canonical IDs; only validation widens). Update the negative suite (closing_correction_tests.py): the uppercase case moves from the malformed set to a positive case (an uppercase-UUID origin_ref folds cleanly in BOTH folds); the malformed set keeps its remaining members. State the line plainly in the notes: validation follows the pinned `format: "uuid"` contract as written; no amendment was sought or made.

## Re-runs (her list)

The affected pack cases, the complete pack (VP-29 unchanged in substance: 54 compared / zero disagreements), TV-1..TV-20 (45/45), the negative suite, the integrated closing lifecycle (re-driven or re-verified — if the production change cannot affect the lifecycle's minted lowercase IDs, the existing correction-round history may stand; state which and why in the notes), and all prior regressions (391 at baseline; stage4 22; corrections-1 24/24; correction-2 21/21; closing corrections 16/16 as amended by CC2-B2's case move — report the suite's new composition explicitly). Genesis hash unchanged. No baseline count shifted silently: any change is named with its cause.

## Round requirements

- New notes file `CLOSING-CORRECTION2-NOTES.md`: exact changed-file list with reasons; the CC2-B1 sibling-case audit result; the CC2-B2 line and its authority (her option (a)); results after execution.
- No earlier notes or reports rewritten. No live agents.

**Deliverable:** corrected validators + the VP-42 fixture/assertion repair + updated negative suite + re-run evidence, reported back with exact counts and anything that could not be implemented as specified — named, never smoothed.
