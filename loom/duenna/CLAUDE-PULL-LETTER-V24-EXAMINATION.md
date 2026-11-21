# CLAUDE — PULL LETTER: independent examination of harness v2.4 (verdict provenance)

Claude — Alex has reviewed the v2.4 implementation as
provisionally satisfactory and directed independent examination
against the exact shelved commit — not a working copy.

**Repository:** Q420/ainternet-shelf, **commit 0f62dd3**.
- `duenna/harness-r60rev.py` — v2.4, sha256
  854a3e8644817ef1acb9c83be01a0164d3f987ada19e25fe972d86a7e0b2f9d5
- `duenna/results-r60rev.json` — sha256
  902936d8aa27e6e75b48644cb2961f1ccbeeaa2344cf79c8573a77f9b470ad66
- `duenna/R60-REVISION-CHANGE-RECORD.md` (addendum 3),
  `duenna/FX-R60J-FINDING-AND-PROPOSAL.md` (addenda 1–2).

For the v2.3 reproduction you will also need the **v2.3**
harness: the same path at **commit de6c4d0** (sha256
30bdd25e…), retrievable from the repo's history.

**Your examination list (Alex's, verbatim in substance):**

1. Reproduce the v2.3 cross-contract replay, including the
   identical-content case. (This finding currently stands as
   established by inspection; your execution settles it.)
2. Verify the v2.4 cases: same-contract acceptance;
   different-digest replay rejection; identical-content replay
   rejection; byte-identical copy rejection.
3. Verify post-issuance mutation rejection.
4. Execute the **identity sabotage** (remove the
   object-identity provenance check) and confirm FX-R60k fails
   for the intended reason, with other fixtures unaffected.
   (The implementer's tooling blocked constructing this
   variant; it is assigned to you.)
5. Independently verify the integrity sabotage and its
   isolation (implementer-reported: fingerprint check removed
   → FX-R60l fails alone, 37/1).
6. Re-run all 38 fixtures; verify the delivered results and
   hashes.
7. Report any failures, exceptions, or scope limitations
   **without smoothing them into a PASS**.

The implementation is **frozen** during examination: if you
find a defect, report the finding (and, if you wish, a proposed
correction) separately — do not patch the examined artefact.
Also in scope from the earlier rounds (Alex's confirmation,
pb-mwbi61jz): the v2.3 sabotage runs (mutable registry vs
FX-R60h under the factory; restored global dispatch vs
FX-R60i), and the v2.3 cross-contract replay above — the
identical-content case stands as established by inspection
until an examiner's execution confirms or challenges it.

Correction B remains OPEN; v0.10 remains NOT APPROVED. Your
dispositions go to the record in your own words; Alex
adjudicates the combined review.
