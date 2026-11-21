# T03 Re-freeze Amendment — 2026-11-15

**Authority.** Ben's ruling, 2026-11-15 01:15 MST (scope-card tap):
the T03 remediation is authorised — Alex's T03 Remediation
Proposal 0.1, route (c), as qualified by Remmy's RB-35 precision
note. Design artefacts: ALEX-T03-REMEDIATION-PROPOSAL-0.1-2026-11-15
(shelved @ 9aeeeb72); ALEX-T03-AMENDMENT-DRAFT-0.1-2026-11-15
(shelved @ 528a3c6c); the draft's patterns corrected by
RB-2026-11-15-39 against the pinned source text and confirmed
by Alex (ALEX-T03-AMENDMENT-CONFIRMATION-2026-11-15, sha256
ce18bb897c634a9d…), who records that he retrieved the source
document from the Shelf and checked the bullets himself.

**What was wrong.** PILOT-CALIBRATION-01 certified T03
UNANSWERABLE for two reasons: (1) the three v0.10 dispositions
(R47 / R60 / R65) exist only as prose bullets in
alex-combined-adjudication-v010#002 with no extractor rule
producing them; (2) Correction B's source record,
alex-combined-adjudication-r60rev#001, was not a T03 pack item.

## The amendments (complete list — nothing else changed)

**EXTRACTOR-RULES-02.json** — three rules appended, in the form
Alex confirmed (pattern, capture group 1, value_type string,
version 02):

- EXT02-R47-1, field r47_disposition:
  `\*\*R47 — (PASS, narrow)\.\*\*` → "PASS, narrow"
- EXT02-R60-1, field r60_disposition:
  `\*\*R60 — (FAIL)\.\*\*` → "FAIL"
- EXT02-R65-1, field r65_disposition:
  `\*\*R65 — (PASS, qualified)\.\*\*` → "PASS, qualified"

Extracted values are the literal source wordings (Alex's
decision: no parenthesised normalisation step). Each pattern
matches exactly once in the pinned section. The draft's
original end-of-line-anchored patterns matched zero times —
the bullets' bold closes after the period and the sentence
continues on the same line; the correction is recorded in
RB-2026-11-15-39.

- Before: sha256 61095f219e1d481ed74c65f3a95806a2cba2e7dc847bcb692373ade3974c5ee5, 884 bytes
- After: sha256 7910ef9f9b8592373a291ea7ecd95e546bf2171623fd4da280bb26ef8458c3cd, 1326 bytes

**PILOT-DATA-PACKS-01.json** — one entry appended to
trees.T03.pack: `{"section": "alex-combined-adjudication-r60rev#001"}`.
Every other pack entry and every other tree is unchanged; the
original T03 question is unchanged.

- Before: sha256 c7eaec18db203651af894e7fbdb53c6df9b36a3da185c4b7ab703d73085b886c, 6486 bytes
- After: sha256 b197e93eeb057f3ec00aee2479144cc97a0247d56eac954ff9aaf420a5db1ded, 6568 bytes

**Corpus snapshot: unchanged.** alex-combined-adjudication-r60rev#001
was already present in PILOT-CORPUS-SNAPSHOT-01; its section
sha256 393cba4c8adae5b153580a1a42dede4543701712f8e99592b2694e0aa2aa366b
was verified from the pinned snapshot itself. No new
Correction B rule was added — EXT02-CB-1 already covers it;
only the pack membership was missing.

**Preservation.** The pre-amendment files are preserved
byte-for-byte at ~/workspace/ssh-door/t03-remediation/
(EXTRACTOR-RULES-02.pre-amendment.json, sha256 61095f219e1d…;
PILOT-DATA-PACKS-01.pre-amendment.json, sha256 c7eaec18db20… —
both equal to the PILOT-PIN-AUTHORITY-01 pins they supersede).

## Pin succession

PILOT-PIN-AUTHORITY-02 (sha256
0b6bf252a93c02744b4500ef0b78440d2279afc7ee167baf6eb8163b1781baa3)
regenerates PILOT-PIN-AUTHORITY-01 with exactly two entries
superseded (EXTRACTOR-RULES-02, PILOT-DATA-PACKS-01 — old and
new values above); the other 15 entries are carried unchanged.
The original authority is preserved in its Batch 3 bundle
copies; nothing historical was overwritten.

## Re-calibration

The complete offline calibration was re-run
(PILOT_CALIB_CERT=PILOT-CALIBRATION-02). The runner's T03
method was updated to the amended step (its four required
extractions); runner sha256
0df4f8375802e83feca24a6cf9848fef0017bfd0e47c6a0807deb9f77d9bca74.

**PILOT-CALIBRATION-02** (sha256
1094802a46f3a2a87469def2f52939821c6345b22c9dd65ade1e6816a589dc90):
all 13 instances ANSWERABLE. T03 extracts the three
dispositions exactly (PASS, narrow / FAIL / PASS, qualified)
and Correction B = OPEN, with zero failures. **T03 is the only
verdict that changed** against PILOT-CALIBRATION-01.

**PILOT-CALIBRATION-01 is preserved byte-for-byte** (sha256
6f3e59793ad751b8d0d47d81c30f337cd1ed1d124493cff31f39229a51d15f0c);
its T03 UNANSWERABLE finding stands as issued, as the
acceptance conditions required.

Audit: test_calibration2.py, 8/8 — including diffs proving the
two file amendments are exactly the authorised changes and
nothing else.

## Disclosures

1. The re-run overwrote the runner's calibration-transcript.txt
   (the cert-01 run's log) before the runner's transcript path
   was made certificate-specific. The certificate artefact
   itself is byte-preserved; the cert-02 transcript is preserved
   as calibration-transcript-PILOT-CALIBRATION-02.txt, and its
   header line carries the runner's then-hardcoded
   "PILOT-CALIBRATION-01" print label — a print-string defect,
   corrected in the runner after the run. The lost log's
   substance is carried by PILOT-CALIBRATION-01 itself.
2. test_g1.py's pin verification now reads the preserved
   pre-amendment rules copy: Gate G1's record was made under
   the 61095f21… pin and its evidence stands under its own
   pins. Suite re-verified 13/13 after the change.

**Effect.** T03 is eligible to join a Stage 6 battery on the
PILOT-CALIBRATION-02 certificate. Stage 6 itself is unchanged
and remains under its own standing authorisation.
