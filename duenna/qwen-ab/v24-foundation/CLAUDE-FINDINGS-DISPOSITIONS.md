# CLAUDE'S FINDINGS 1–5 — DISPOSITIONS

Source: reviews/arm-c-process-trees-review.md, branch
review/arm-c-process-trees @ e9c5adf (Q420/ainternet-shelf).
Each disposition is a claim with its evidence pointer, for
Alex's independent verification — not proof (per his
ruling, point 4). Corrections live in
TREES-V24-AMENDMENTS.md (document-level; originals
preserved). Execution impact is stated per finding.

| # | Finding (review lines) | Disposition | Evidence / where |
|---|---|---|---|
| 1 | T02-STEP-03's precedence rule is extracted by no step (L31–36) | **CORRECTED, document-level.** The authority order is declared as a trial rule in the step itself (constitutive, like T04's boundary table); the FACT the step relies on — the adjudication's disposition — is extracted in STEP-01 and verified by verify_field in STEP-03. Execution impact: none. | Amendments §F1; trees v2 L54 (STEP-01 adjudicator row), L62–68 (STEP-03, verify already specified) |
| 2 | Judgement steps labelled [TOOL]: T04-STEP-02, T06-STEP-B/C (L38–46) | **CORRECTED, document-level.** Mechanical rules now stated for each (set-membership test; named extractor comparisons); genuinely judgement parts relabelled [MODEL] (T04's refusal statement; T06's STEP-E composition, with labels verified against step outcomes). Execution impact: none — the amendments describe the driver as built. | Amendments §F2; trees v2 L102, L167–171; run_c.py c_t04/c_t06 |
| 3 | T06-STEP-A "not authenticatable" has no procedure (L48–50) | **CORRECTED, document-level.** Authentication defined: shelf_lookup resolves the source in the frozen corpus AND its sha256 matches the corpus manifest. Execution impact: none (tools24.shelf_lookup's behaviour). | Amendments §F3; tools24.py L77 |
| 4 | T05: 8 fields unlisted; STEP-06 retry/BLOCKED terminal state unstated (L52–58) | **CORRECTED, document-level.** The eight fields listed; STEP-06 rewritten — Arm C T05 has no retry; a failed validation is emitted marked, recorded, and scored; the old wording was a gate-design remnant. Execution impact: none. | Amendments §F4; trees v2 L117, L143; tools24.load_contract |
| 5 | T03-STEP-02's completeness claim has no check (L60–64) | **CORRECTED, document-level.** The sweep is defined as one classify_item per pack item, completeness verified by count in the process log. Execution impact: none — the driver already classifies every pack item. | Amendments §F5; trees v2 L79; run_c.py c_t03 |

Findings 6 (undefined references) and 7 (absence-search
specification) were outside Alex's ordered five; both are
addressed in Amendments §F6 (existence confirmed by file
and line) and §F7 (search specified; zero any-case
occurrences of "grok" in the frozen T01 pack, checked
against the corpus) so the rerun inherits no open items
from the review.
