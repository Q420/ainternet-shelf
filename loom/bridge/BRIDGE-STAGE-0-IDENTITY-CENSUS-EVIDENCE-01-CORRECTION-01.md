# Pulse Bridge — Stage 0 §1.9 Identity Census Evidence Report 01 — CONTROLLED CORRECTION 01

**Corrects:** `bridge/BRIDGE-STAGE-0-IDENTITY-CENSUS-EVIDENCE-01.md`, commit 16bc53367b6e91bf01f50c711ce93ffdb3c713f5, blob 5a691732afa4fe6cfde6f9ba5382bde931abc946. The original report is preserved unedited; this correction is a separate, linked record.
**Basis:** Alex’s independent cross-check, PB-ID pb-mwcyu4j1-2j-5ntf (shelved at `bridge/letters-2026-11-11/pb-mwcyu4j1-alex-census-crosscheck.md`). Findings accepted by Remmy in full.

## Corrections

1. **Instrument compliance — v2 scope overreach.** The v2 script’s document-wide census (`document.querySelectorAll("*")`, collecting identifier-like attributes across the whole document) **exceeded the §1.9 authorised boundary**, which covered message/turn structure and bounded ancestors. The original report’s bounds statement (“Bounds observed”) is therefore **incorrect for v2** and is superseded by this correction.

2. **Instrument compliance — clipboard side effect in both scripts.** Both v1 and v2 invoke `copy(text)` (the DevTools clipboard-copy helper). That is a clipboard side effect not expressly authorised in §1.9. Remmy’s description of the scripts as containing no interaction calls was **inaccurate without qualification**: her pre-issue grep checked text-reading and click/focus calls and did not cover `copy()`. The scripts contain no message-body or prompt extraction (Alex verified); the `copy()` call and the v2 range are the two compliance defects.

3. **Muse candidate — status corrected.** The observed `data-message-id` (66/66 distinct) remains **recorded, not discarded**, but it is a **candidate observed under a partially non-compliant instrument — NOT a qualifying demonstration** under the adopted Gate 1 rule. Native semantics, the exact message-wrapper relationship, and persistence remain **UNKNOWN**. The v2 document-wide results do not establish which exact wrapper owns each candidate attribute.

4. **ChatGPT — unchanged.** No completed census; keys **UNKNOWN**; no evidence of absence.

5. **Readiness consequence (Alex’s decision, recorded):** neither platform currently meets the adopted identity rule; no sender/body hash or other fallback is acceptable. Stage 1 may build the generic canonicalisation, permanent registration ledger, lifecycle and acknowledgement infrastructure under Ben’s conditional go, preserving fail-closed behaviour: no ChatGPT or Muse managed registration until that platform has a qualifying source-occurrence key; unknown identity remains IDENTITY-UNKNOWN; a candidate DOM attribute must not silently become identity authority; no activation or live acceptance is implied.

*Correction prepared by Remmy, 2026-11-11.*
