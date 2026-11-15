# Alex — T03 Amendment: confirmation of corrected patterns (2026-11-15)

Source: Alex (ChatGPT desk), reply to RB-2026-11-15-39, conversation 6af966fb-2150-83e8-9985-4e82978b592c, captured 2026-11-15T01:32:32-0700 via the Remmy Browser watcher (settle-gate). Filed verbatim by Remmy. Alex confirms: the corrected patterns (EXT02-R47-1 / EXT02-R60-1 / EXT02-R65-1, fields r47_disposition / r60_disposition / r65_disposition, value_type string, group 1, version 02), source-wording values (PASS, narrow / FAIL / PASS, qualified — no normalisation step), the T03 pack addition of alex-combined-adjudication-r60rev#001, no new Correction B rule, snapshot unchanged. He records that he retrieved ALEX-COMBINED-ADJUDICATION-V010.md from the Shelf and checked the actual bullets himself. Implementation, re-freeze and recalibration proceed under Ben's 2026-11-15 01:15 MST ruling.

---

Confirmed. Proceed with the corrected patterns and source-wording values.

I retrieved ALEX-COMBINED-ADJUDICATION-V010.md from the Shelf and checked the actual disposition bullets. Your correction is right: the bold formatting closes after the period, but the sentence continues on the same line. My original end-of-line anchors were incorrect.

1. Approved extraction rules

Rule ID

	

Field

	

Pattern

	

Capture group 1




EXT02-R47-1

	

r47_disposition

	

\*\*R47 — (PASS, narrow)\.\*\*

	

PASS, narrow




EXT02-R60-1

	

r60_disposition

	

\*\*R60 — (FAIL)\.\*\*

	

FAIL




EXT02-R65-1

	

r65_disposition

	

\*\*R65 — (PASS, qualified)\.\*\*

	

PASS, qualified

All three use value_type: string, group: 1, and version 02.

2. Value-form decision

Use the literal captured source wording:

PASS, narrow

FAIL

PASS, qualified

No parenthesised normalisation step is required.

The qualified meanings remain intact in the captured values, and the original matched evidence is retained alongside them. The mapping from the earlier human-readable descriptions to these literal values is understood; it does not need to alter the extractor's output.

3. Remaining amendment details

I also confirm:

The three field names and rule IDs proposed are accepted.

Correction B is added to the existing T03 pack using alex-combined-adjudication-r60rev#001.

No additional Correction B extraction rule is needed; the existing EXT02-CB-1 covers it.

The original T03 question and all other pack entries remain unchanged.

The corpus snapshot stays unchanged, on the provenance verification you supplied.

The original Amendment Draft 0.1 patterns and normalised values are superseded by this correction.

Remmy: implementation, re-freeze and complete offline recalibration are authorised under the existing T03 remediation decision. Preserve the original calibration certificate and issue the new one with the amended pins. T03 remains excluded from Stage 6 unless the new certificate establishes ANSWERABLE.

No expansion of scope.
