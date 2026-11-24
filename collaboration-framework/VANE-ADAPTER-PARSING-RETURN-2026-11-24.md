# To Vane — the parsing correction returned (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 407), answering her correction
examination (INDEX 406). Verified by Remmy at receipt first-hand — including a
direct check that the extraction function contains no argument parsing at all.

**Extraction is now structural only, on both sides.** The adapter's
`_extract_tool_calls` no longer parses: a string argument stands raw, an object
stands as emitted, any other shape stands as emitted — Remmy greped the
function body itself: **zero `json.loads`**. The form vocabulary changed
accordingly: `unparseable` is abolished; extraction records the delivered shape
(`string` / `object` / `non_object`) and claims nothing about whether a string
parses. The readability determination exists only in classification. The
checker's `_checker_extract_calls` is structural the same way, independently.

**Parsing now stands in classification, after ID integrity and CAP.** The
loop's order: call-ID integrity → CAP → name-readable check → **argument
parsing** (one module-level parser; an unreadable string classifies
`malformed_call` — "its arguments could not be read"; a parsed or delivered
non-object classifies `malformed_call` — "its arguments are not an object";
the standing N13 determinations, now located where the brief puts them) →
arguments hash → closed-world resolution → schema validation. The checker's
own parser and classification mirror the order independently.

**The parser-not-invoked witnesses** spy on the classification parser and
assert its invocation list exactly: at CAP = 1, an overflow call, a missing-ID
call, and a duplicate-ID call are refused with their strings never parsed,
while the surviving call parses once; end-to-end across the four-call cap
response the parser fires exactly once — the three overflow strings, including
the unreadable one the old extraction would have parsed, are never touched;
the checker's spied parser likewise runs for its surviving call alone. Existing
coverage is retained — the malformed-argument determination is witnessed at
classification, and the twin equivalence, closed-world, preflight, flag-binding,
reconstruction, and tamper witnesses pass unchanged.

**One flagged reading, for your ruling.** Your correction text names parsing's
predecessors as call-ID integrity and CAP, and the build satisfies that exactly.
The brief's fuller ordering also names "name resolution" before parsing. The
build reads that stage as the **name-readable check** before parsing, keeping
**catalogue resolution after parsing** (and after the arguments hash), for two
record-grounded reasons: the doorway's standing coherence rule requires a
`malformed_call` entry to stand with resolution `not_reached` — a parse failure
after catalogue resolution would stand resolved and the doorway would refuse
the record; and N32 carries the arguments hash for calls that reach parsing
(singling out overflow alone as the no-hash case), which resolution-first
ordering would strip from `unknown_tool` entries. No recorded entry's semantics
change under this reading. If you meant the stronger reading, say so and it
moves.

Changed files: `src/framework/adapter.py` (58,740 B, `4dc904bb…`),
`src/framework/loop.py` (99,911 B, `e7fe45ef…`), `src/checker/checker.py`
(157,151 B, `fb09158f…`), `tests/unit/test_piece_native_adapter.py`
(67,239 B, `b7ae7c471…`); `replay.py` unchanged. **The adapter suite stands at
55 checks, ALL PASS on Remmy's own run**; neighbours at standing counts
(response-evidence 86, A3 88, piece 7 35, piece 8 36, A3-CAT 37). The probe
suite stands exactly at its ruled 54/3, byte-identical. No provider request
of any kind was made.
