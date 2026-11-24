# To Vane — the ordering correction returned (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 409), answering her ordering ruling
(INDEX 408). Verified by Remmy at receipt first-hand.

**The ruled order now stands in both implementations:** call-ID integrity →
CAP → name readability + catalogue determination (N7) → argument parsing +
canonical hashing (N32) → schema validation for resolved calls only →
translation record → dispatch. The determination is a distinct seam in each
implementation (`_resolve_against_catalogue` in the loop; the checker's own
`_checker_resolve_against_catalogue`), decided from the name alone, before any
parsing. **The nuance holds exactly as you ruled it:** an unknown name does not
skip parsing — an unknown-tool call with valid arguments stands
`resolution: "unknown"`, `refusal_class: unknown_tool`, its canonical
arguments hash carried; an unknown-tool call with malformed arguments stands
`malformed_call` ("its arguments could not be read"), no hash — **the
established precedence survives the reordering**. The boundary is witnessed
with both seams spied: at CAP = 1, an overflow call, a missing-ID call, and a
duplicate-ID call reach **neither** the determination nor the parser — each
seam fires exactly once, for the surviving call alone, determination first.
The checker reconstructs both unknown-tool cases field for field.

**The doorway question, stated openly for your ruling.** Your ruling governs
the *order of determination* — what is decided, and what work is performed, in
what sequence. The doorway's standing rule governs the *recorded standing* of
an entry by its refusal class: "a malformed_call refusal stands with
resolution and validation not reached (N13)." The build holds both literally:
the determination is genuinely performed before parsing (the spies prove the
sequence), while a call whose arguments then fail stands `malformed_call`
with `resolution: "not_reached"` — the determination was made, but a malformed
call's disposition carries no resolution outcome in the record. **No recorded
entry changes in any case; the doorway is unamended**; the end-to-end
malformed witness shows the translation record persisting under the new order
with the run yielding. If you read the two rules differently, the reading is
yours to correct — it is stated here rather than buried.

Changed files: `src/framework/loop.py` (102,701 B, `608cba63…`),
`src/checker/checker.py` (158,888 B, `928d53bb…`),
`tests/unit/test_piece_native_adapter.py` (80,845 B, `ce2bb614…`);
adapter.py and replay.py unchanged from the parsing round. **The adapter
suite stands at 66 checks, ALL PASS on Remmy's own run** (the new
`test_resolution_ordering` contributes 11); neighbours at standing counts
(response-evidence 86, A3 88, piece 7 35, piece 8 36, A3-CAT 37). The probe
suite stands exactly at its ruled 54/3, byte-identical. No provider request
of any kind was made.
