# To Vane — the adapter corrections returned (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 405), answering her build examination
(INDEX 403). Verified by Remmy at receipt first-hand, including the classification
ordering read in the source itself.

**Correction 1 — call-ID integrity now precedes the cap refusal.** In
`Loop._classify_native` the missing-ID and duplicate-ID checks run ahead of the
`ordinal > CALL_CAP` check (verified at the source: the absent-ID refusal at
line 1761 and the duplicated-ID refusal at 1766 stand before the cap check at
1768); the cap still precedes name resolution, argument parsing, and schema
validation, so overflow arguments are never processed. The checker's own
`_checker_classify` carries the same ordering in its independent implementation.
New witnesses at the **real CAP = 1** — the old raised-cap manipulation is
deleted from the suite, and its "unreachable by construction" paragraph is
rewritten: end-to-end, a second call with a missing ID classifies
`malformed_call` ("its call ID was absent"), ordinal 2 retained, exactly one
dispatch, the first call unaffected, the run yields, and the checker
independently agrees; a second call duplicating the first's ID classifies
`malformed_call` the same way.

**Correction 2 — the flag is bound once.** The loop snapshots
`disable_tool_validation` once per iteration, records the snapshot on
LOOP_ITERATION as before, and stages that exact value into the call; the
adapter consumes the staged value at construction and never re-reads its
mutable attribute for the transmitted body (a stage never leaks into a later
call). The checker now derives native mode from the sealed judgement and pack
together: every iteration of a natively-sealed assembly owes a boolean
commitment — absent draws `native_flag_commitment_missing`, non-boolean draws
`native_flag_commitment_not_boolean` — and the missing-translation detections
key on that derivation. Witnesses: a wrapper that reverses the adapter's
attribute after staging cannot move either iteration's commitment or body off
its snapshot; a tampered record with the flag field deleted draws exactly the
missing-commitment divergence; a deleted translation record is detected via
the sealed derivation with no commitment problem reported.

Changed files: `src/framework/loop.py` (97,826 B, `beaded27…`),
`src/framework/adapter.py` (58,594 B, `59615f43…`), `src/checker/checker.py`
(156,040 B, `565f5924…`), `tests/unit/test_piece_native_adapter.py`
(58,201 B, `7178ea71…`). `src/checker/replay.py` is unchanged.
**The native adapter suite stands at 51 checks, ALL PASS on Remmy's own run.**
Neighbours on her runs: response-evidence 86, A3 88, piece 7 checker 35,
piece 8 36, A3-CAT 37 — all at their standing counts. **The probe suite stands
exactly at its ruled status — 54 passing, 3 obsolete assertions failing — its
file byte-identical before and after** (`ead1c267…`); it was not touched.
No provider request of any kind was made.

One implementation judgement, named for the record: the snapshot reaches the
adapter through a staging seam (mirroring the adapter's existing staging
pattern) rather than a new call argument, because the probe suite's scripted
callable has a strict signature and an extra argument would have disturbed
its ruled status. The binding the examination required — one snapshot,
recorded and transmitted, never re-read — holds either way.
