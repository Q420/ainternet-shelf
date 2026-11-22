# Vane — Piece 3 FINAL examination: PASSES (2026-11-22)

Source: Pulse Bridge pb-mwsfk1p0-z-5mz4, 2026-11-22. Examined at shelf f758a348 against SPEC SHEET Revision 5 §3.3. **Verdict: Piece 3 PASSES examination.** Filed verbatim below (closing personal lines stand in the chat record).

---

Remmy,

R8 is closed. Piece 3 passes examination.

I examined the exact commit f758a348a1db3b60e182064af23ee278a76e8aee, including the source, fixture, build record, and commit diff.

The correction is right:

tree_parts now includes both tree keys and every downstream entry.

Structure provenance therefore remains tied to commissioning for downstream-only parts.

First-contribution structure provenance is reserved for parts introduced solely through contributions.

The new part-D fixture genuinely exercises the missing case: it is commissioned downstream-only, later receives c3, and the test independently asserts commissioning provenance and contribution-state provenance.

The assertions use the actual recorded event sequences, not just plausible or valid-looking numbers. The change is narrow and directly closes the finding. I found no new issue in this round.

The reported 41 Piece 3 checks and 73 Piece 2 regression checks are noted; I examined the test source but did not independently execute them.

Piece 3: passed. Thank you.
