# Independent verification report: D3 v0.8 — Claude (primary independent reviewer)

*Delivered 2026-11-09 ~21:59 PST via Ben's ferry of the claude-ferry pack. Preserved verbatim as received.*

Scope: I worked only from the zip (the four WordPress links were never fetched). I hashed the files, read the register, matrix, and v0.8 text, re-ran the harness in an isolated copy, and only then read the implementer's reconciliation.

Headline: The package does not reconcile cleanly. Of the 33 slots, 27 pass on their own terms, and 6 fail on fixture coverage or text consistency: R42, R47, R56, R60, R63, R65. The reconciliation reports these as fully implemented and passed. Approval status is also contradicted across three sources. The four gaps are real and accurately described.

## What I verified directly

Hashes: Register d71d0a79… ✓, Matrix r4 f6ddf789… ✓, v0.8 spec 3e053efc… ✓, harness 89dc0e50… ✓. The v0.7 file is not in the zip, so its hash is unverified (see D7).
Harness re-run: 25 PASS, 0 FAIL. Apart from the Python version string, the output matches the delivered results.json exactly.

## Per-slot disposition (R33–R65)

"Text" means the v0.8 spec text. "Fixture" means the harness record.

| Slot | Kind | Derived verdict | Evidence and notes |
|---|---|---|---|
| R33 | TEXT | PASS | D-3 step (0), admission rule present. No dedicated fixture; the non-admit path is exercised only via FX-R47c. |
| R34 | TEXT | PASS | A-1 Outputs, tagged "Correction R34". |
| R35 | TEXT | PASS | C-3: "exactly as authored" retired; duplicate keys rejected at parse layer. FX-R49b. |
| R36 | TEXT | PASS | K-3 (3): "CREATION at binding" example removed; grep confirms it is gone. FX-R63b. |
| R37 | TEXT | PASS (text) / NOT VERIFIED (fixture) | K-3 (2) block rule present. FX-R63a builds its own ordered list, so block ordering is never checked. |
| R38 | TEXT | PASS (text) / GAP | H-6 LINK mechanism and both creation orders present. (v)/(vi) specified but not executed. |
| R39 | TEXT | PASS | A-1 boundary paragraph, "no semantics change". |
| R40 | FIXTURE | PASS | FX-R40a–e run and pass. R40b uses a hard-coded sequence, so it is weak. |
| R41 | STATUS | PASS | B-1 header reads PROPOSED. |
| R42 | TEXT | FAIL | K-1 now says B-1 is "enforced at binding by this check", but B-1's own Behaviour still reads "REQ-K-1 if adopted", and K-1 is PROPOSED. Inconsistent. |
| R43 | TEXT | PASS | B-2, "Correction R43". Exercised in FX-R44. |
| R44 | FIXTURE | PASS | FX-R44 landed and passes, which meets the matrix's own condition for closing R44. Closure authority is not in the zip. |
| R45 | STATUS | PASS | C-2 header and conditional-reliance clause. |
| R46 | TEXT | PASS | C-1 "correction R46"; "creation event" phrase absent. FX-R47b does not test fold start. |
| R47 | FIXTURE | FAIL | FX-R47a passes. R47b supplies no determinations, so the "trigger content would qualify" case is never tested. R47c's "INDETERMINATE" label is written by the test. |
| R48 | TEXT | PASS (text) / GAP | C-3 three-path allowlist. Text is wider than matrix wording and cites "rework direction pb-mwa9mpq7", which is not in the zip. No exclusion-boundary fixture. |
| R49 | FIXTURE | PASS | FX-R49a–d pass on re-run. |
| R50 | TEXT | PASS | B-2 and D-2. |
| R51 | TEXT | PASS | D-3 (2) availability and (4). |
| R52 | FIXTURE | PASS | FX-R52 runs the real fold. |
| R53 | TEXT | PASS (text) / GAP | C-3 consumption binding present. No fixture. |
| R54 | FIXTURE | PASS (note) | FX-R54a/b pass. The "several responses competing for one event" case is not tested; the matrix's "or" makes one case sufficient. |
| R55 | TEXT | PASS (text) / GAP | H-3 identity-bearing annotation, "correction R55". No fixture. |
| R56 | FIXTURE | FAIL | Matrix says "cover all prohibited substitutions". FX-R56 checks only author identity and a missing role. Evaluator↔examiner and examiner↔gate substitutions are untested. |
| R57 | FIXTURE | PASS (weak) | FX-R57 passes, but both inputs are hard-coded literals. |
| R58 | — | PASS | Withdrawn; the R38 mechanism in H-6 covers it. |
| R59 | — | PASS | No referent. The reconciliation misdescribes the renumbering (D3). |
| R60 | FIXTURE | FAIL | Covers reproducibility, failure paths, and pinned version. "Defined input" and "validation procedure" are not separately exercised. The checker is defined inside the test. |
| R61 | FIXTURE | PASS | Corrupted-payload case present. |
| R62 | FIXTURE | PASS | K-1 acceptance (iv) and FX-R62. Outcome (i) only, as the matrix asks. |
| R63 | FIXTURE | FAIL | Matrix's third item (stable identity and record position) is not tested. FX-R63b checks only instance identity. |
| R64 | FIXTURE | PASS | FX-R64 uses a real validator on constructed reports. |
| R65 | FIXTURE | FAIL | Matrix asks for targeted fixtures across five reference types. FX-R65 tests one mismatch (content_identity). |

## Discrepancies against the implementer's reconciliation

Each is named individually and left unresolved.

- **D1 (approval state, three-way):** The handoff says the v0.8 revision was "APPROVED WITH STATED CONDITIONS by Alex". The reconciliation says "D3 approval: NOT given". The v0.8 header says "NOT APPROVED". These cannot all be true.
- **D2 (approval authority):** The handoff says Alex holds delegated approval authority from Ben. Spec REQ-J-1 says "Approval… belongs to Ben alone… No standing delegated approval exists." The spec header says approval is "Alex's".
- **D3 (R59):** The reconciliation says "the R60/R61 renumbering". The matrix says the REQ-I-3 finding was numbered R59 and renumbered R61. R60 is a different finding.
- **D4 (R42):** The reconciliation says "Implemented (Stage 2)". B-1 was never amended, so the correction is only partly carried (see the R42 row).
- **D5 (coverage overstated for R47, R56, R63, R65):** The reconciliation reports these as implemented, executed, and passed. The matrix's named items are not all exercised (see the table).
- **D6 (R60):** The reconciliation says "all five properties" are tested. Two are not separately exercised.
- **D7 (v0.7 identity):** The reconciliation says the file is a14cad05… with canonical hash 28718d26…. The register gives 28718d26… as the file's SHA-256. The results document also cites a14cad05…. The v0.7 file is not in the zip, so this is NOT VERIFIED.
- **D8 (harness identity in the results document):** It cites harness v1.1, SHA 20a6767f…, 27,971 bytes. The delivered harness is 89dc0e50…, 28,324 bytes, self-labelled v1.2, as the reconciliation and JSON say.
- **D9 (results.json identity):** The results document cites SHA fd3378ef…. The delivered file hashes to 4df5c0ba…. Its size, 8,881 bytes, does match.
- **D10 (R34 erratum):** The reconciliation cites a "matrix-row erratum" in the change record. I found no such erratum in the matrix, and the change record is not in the zip. NOT VERIFIED.

Where the derivation and the reconciliation agree: R33–R58 text placement, the 15/2/14 kind counts, the R58 withdrawal, the 25/25 result, and all four gap descriptions.

## Authority and status checks

- **S1. UX-1…UX-5 open and non-binding: PASS.** Each is marked UNRESOLVED or PROPOSED, and the spec states that PROPOSED and UNRESOLVED items "bind nothing" ("What this specification is not"). Label note: UX-3 (A-6), UX-4 (K-1), and UX-5 (K-3) carry PROPOSED headers, not UNRESOLVED.
- **S2. PROPOSED requirements have not acquired binding status: FAIL.** K-1 is PROPOSED, yet its text makes it the enforcement point for B-1, which is also PROPOSED. Separately, K-4 (CONVERGED) requires citing C-3 (v) and (vi) and D3-CANON-1, all of which are PROPOSED. I did not check whether the K-4 dependence predates v0.8.
- **S3. No approval condition silently converted into a requirement: PASS.** The UX items, the PROPOSED items, and the gaps are all still marked as open in the text.
- **S4. No Stage 2 work begun: NOT VERIFIED.** The spec text says Stage 2 is not executed. Nothing in the zip shows the programme state.
- **S5. Frozen artefacts unaltered (v0.7, execution contract): NOT VERIFIED.** Neither file is in the zip, and the v0.7 hash conflicts (D7).
- **S6. Approval binds to hash 3e053efc…: hash PASS, approval itself NOT VERIFIED.** The file hash matches. The approval record is not in the zip, and D1 and D2 apply.

## Approval conditions against the text

- **C1. UX-1…UX-5 unresolved: PASS (S1).**
- **C2. Several requirements PROPOSED and not settled: FAIL on K-1 (S2).** Headers are otherwise correct.
- **C3. Four fixture gaps open: PASS (see gaps below).**
- **C4. Serialiser is a limited reference implementation with no RFC 8785 conformance claim: PASS.** The harness docstring disclaims conformance. C-3 says the procedure "follows" RFC 8785, which states the required standard, not a claim about the harness.
- **C5. 25/25 certifies reference procedures only: PASS in the results document ("TEST BOUNDARY").** The v0.8 text does not mention fixture results.

## The four gaps

Each is checked individually.

- **R38 (v)/(vi), reciprocal-link fixtures: CONFIRMED.** Specified in H-6's acceptance text. No H-6 fixture in the harness.
- **R48, exclusion boundary: CONFIRMED.** FX-R49 tests composition, duplicate keys, member order, and numbers. None of the three excluded paths or the envelope boundary is tested.
- **R53, consumption binding: CONFIRMED.** Text in C-3, no fixture. The matrix lists R53 as TEXT, not FIXTURE, so "fixture gap" is the approval's framing. C-3's own acceptance list also has no consumption-binding case.
- **R55, supersession annotation: CONFIRMED.** Text in H-3 with acceptance wording. No fixture.

## Caveats

Several fixtures test procedures defined inside the test itself, as the results document acknowledges. A PASS shows internal consistency, not that the spec is correct.
Not in the zip: v0.7, the execution contract, the change record, the evidence pack, approval and checkpoint records, and the mechanical verifier's output (including its two UNKNOWNs).

## Suggested adjudication order

D1 and D2: establish the approval state and who holds approval authority.
S2 and D4: resolve the K-1 / B-1 enforcement inconsistency.
The six FAIL slots: either add the missing fixtures or correct the reconciliation's claims.
D7 to D9: fix the hash references in the results and v0.7 records.

*"If you want this as a shareable page for Alex, I can publish it." — Claude's closing offer, relayed by Ben.*
