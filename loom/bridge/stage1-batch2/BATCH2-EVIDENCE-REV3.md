# Stage 1 Batch 2 — Evidence, Revision 3 (focused correction)

Date: 2026-11-11 (America/Dawson_Creek)
Answers: Alex's Batch 2 Rev2 review (pb-mwd1c29y) — one focused correction. Batch 3 remains paused for this recheck only.

## The correction

`recordIntakeRefusal` defaulted correlation to EXACT for anything not exactly 'UNKNOWN' — silently upgrading unestablished correlation into an exact match, against Contract Rev02 SS4.3 / SS7.2A. The boundary is now fail-closed: only an explicitly valid 'EXACT' value is exact; missing or unrecognised values stay UNKNOWN.

## Fixtures

ledger.fixtures.js: **56/56 passed, 0 failed** (54 carried + 2 new).
identity.fixtures.js re-run unchanged: **44/44**. Stage 1 running total: **100/100**.

New fixtures: omitted correlation stays UNKNOWN and never promotes (admission held for that item); unrecognised value ('PARTIAL') stays UNKNOWN and never promotes.

Disclosed: the correction exposed two carried R-2 fixtures that had silently relied on the old default — they omitted correlation while exercising promotion. Both now state `correlation: 'EXACT'` explicitly, which is what they always meant. No other call site relied on the default: the UNKNOWN-hold fixture already stated UNKNOWN, and the retrievability fixture's intake is never promoted in either world.

The neighbouring default was checked and left, deliberately: intake `type` defaults to REFUSED unless REFUTED — that defaults to the weaker claim (a system refusal), never an upgrade toward the authority-bearing kind, so it is not the same fault family.
