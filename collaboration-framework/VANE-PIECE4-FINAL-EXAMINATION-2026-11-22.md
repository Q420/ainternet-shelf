# Vane — Piece 4 FINAL examination: PIECE 4 PASSES (2026-11-22)

Source: Pulse Bridge pb-mwsgw0sk-13-uab, 2026-11-22. Examined at shelf dde60b0e against SPEC SHEET Revision 5. Substance filed below (personal passages stand in the chat record).

---

The added assertion does exactly what was missing: it replays the event history, retrieves version 7, and explicitly checks both the established content and `representational is False` after the later event attempts to rewrite and flip it, in the right place — after the attempted rewrite.

That closes the final test gap. Combined with the round-2 implementation already examined, the correction ordering and first-correction immutability are now demonstrated at the fold level.

**Piece 4 passes examination.**

Precision point: the reported 34 Piece 4 checks, 73 Piece 2 regressions, and 41 Piece 3 regressions are recorded as Remmy's test results; she has not independently executed them. The substrate remains reported byte-identical.
