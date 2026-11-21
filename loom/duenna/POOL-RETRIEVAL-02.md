# POOL-RETRIEVAL-02 — Decision-Evidence Retrieval, Questions 3–5
## Interim carrier round (Gemini), 2026-11-11

**Series:** POOL-RETRIEVAL-01 (Crusher/Qwen, 2026-11-11) →
this document. Per Ben's standing practice (2026-11-11):
each retrieval round is asked once and preserved as a
numbered document; the same question is never purchased
twice.

**Why an interim carrier:** the original five questions
were Alex's, for his three reserved decisions. Questions
1–2 were answered by Crusher (Qwen via Groq) and returned
in pb-20261111-decision-evidence-return; questions 3–5
failed on a Groq HTTP 429 limit — behaviour (persistence
across spaced retries and ~10 minutes) supports the daily
AMOUNT limit, though the Crusher helper truncates Groq's
error body, so the limit type is NOT VERIFIED from the
provider's own wording. Alex's record stands: Crusher
Q3–Q5 remain **NOT RETRIEVED**.

**Ben's authorisation (2026-11-11):** "you can use
geminis api in the mean time." These three questions were
therefore run over the IDENTICAL retrieval method —
local BM25 over the canonical index (1,156 sections),
the same FENCE as system instruction, temperature 0,
k=6 — with the answering model substituted:
**gemini-3.1-flash-lite**, the researcher model of
record since Ben's 2026-11-06 switch (gemini-3.8-flash
had shown 503s/timeouts under provider load). One 503
occurred on the first attempt here and cleared on retry,
consistent with that history.

**Evidence class:** these are interim Gemini-carried
answers over Crusher's retrieval — NOT Crusher answers.
The exchanges are also logged in crusher-log.jsonl with
explicit carrier and model fields. Alex decides what
weight they carry for his consolidation; the Crusher
originals will still be run when the Groq limit clears,
if he asks.

## Q3 — Ledger, generation, dependency and synchronisation artefacts

**Question (Alex, verbatim):** The current ledger, generation, dependency and synchronisation artefacts, if any.

**Sections retrieved (BM25, k=6):** v09-examination-findings-ledger#029, duenna-step3-mapping#002a, exon-replay-matrix-01#003a, v09-examination-findings-ledger#003b, duenna-step5-challenge#010, v09-examination-findings-ledger#001

**Answer (verbatim, gemini-3.1-flash-lite):**

UNKNOWN — the corpus does not say.

Closest sections: v09-examination-findings-ledger#029, duenna-step3-mapping#002a, duenna-step5-challenge#010.


**Remmy's remarks (labelled, not part of the answer):**
the UNKNOWN is correct — no ledger, generation,
dependency-declaration or synchronisation artefacts
exist in the corpus; the retrieved sections are
ledger-adjacent records (findings ledger, gate ledger),
not the pool mechanism. This matches the labelled
supplement in the original evidence return.

## Q4 — Infrastructure gaps and closure evidence

**Question (Alex, verbatim):** All relevant infrastructure gaps and the exact evidence required to close them.

**Sections retrieved (BM25, k=6):** exon-field-matrix-01-review#027, exon-category-neighbour-audit#018, exon-field-matrix-02-alex#003, qwen-ab-v2r-results#037b, exon-field-matrix-01-review#025, qwen-ab-v2r-results#037a

**Answer (verbatim, gemini-3.1-flash-lite):**

The infrastructure gaps and required evidence are as follows:

**Infrastructure Gaps**
*   **Gap 1:** "Registry machinery UNKNOWN" (exon-field-matrix-02-alex#003).
*   **Gaps 2–3:** "live-head/concurrency machinery UNKNOWN" (exon-field-matrix-02-alex#003).
*   **General:** "Preserve all UNKNOWN infrastructure gaps. Do not define intended registry, live-head, or concurrency behaviour as already mechanically enforced" (exon-category-neighbour-audit#018#010).
*   **Message ID:** "uniqueness enforcement UNKNOWN" (exon-field-matrix-02-alex#003).

**Required Evidence/Actions to Close Gaps and Matrix**
To close the matrix and infrastructure definitions, the following actions are required:
1.  **Matrix Reconciliation:** "Close FM-01 through FM-09 so every field's legal-type set and required/optional condition matches all nine Part IV definitions" (exon-field-matrix-01-review#027).
2.  **Definition/Rule Closure:** "Close FM-10 through FM-14 so each field/value has the promised definition, FORM rule, and MEANING route" (exon-field-matrix-01-review#027).
3.  **Lifecycle/Authority:** "Close FM-15 through FM-18 by bringing the 0.4 lifecycle and authority text into agreement with the matrix" (exon-field-matrix-01-review#027).
4.  **Message-Specific Requirements:**
    *   **RULING:** "Add/confirm decision_trigger; reconcile evidence_refs, evidence_class, reason_ref, adjudication_ref legal types; ensure exclusion_authority_ref and contested_refs exact shapes" (exon-field-matrix-01-review#025).
    *   **ACCEPT:** "Reconcile evidence fields and authority_ref; decide completeness_assessment applicability; add exact criteria/accepted/excluded/release cross-field constraints" (exon-field-matrix-01-review#025).
    *   **REQUIREMENT:** "Add owner and criteria_ref to Part IV if retained; reconcile evidence_class/evidence_refs legal types; include exact failure_action values" (exon-field-matrix-01-review#025).
    *   **RESULT:** "Reconcile artifact_ref/evidence fields; define outcome vs attempt_event vs final_outcome; close completeness_assessment values and classification requirements" (exon-field-matrix-01-review#025).
    *   **REQUEST:** "Use exact field names ask and asked_seat in Part IV; state exact FORM rules" (exon-field-matrix-01-review#025).
    *   **DELEGATION:** "Add owner if required; add task_ref exact shape; reconcile authority_ref and task registry resolution" (exon-field-matrix-01-review#025).
    *   **STOP:** "Use release_authority_ref exact name; include operation_ref, defective_field, required_correction, and any reason_ref/bounded_explanation fields with exact conditions" (exon-field-matrix-01-review#025).
    *   **REGISTER_TASK:** "Add proposed_task_id, scope, parent task, constraints, completion condition(s), authority_ref, owner, and required target task_registry_ref with exact names and rules" (exon-field-matrix-01-review#025).
    *   **CORRECTION:** "Add PENDING wait-condition field; define correction_id uniqueness domain/enforcement caveat; align reason/basis/reliance fields and flag-closing references" (exon-field-matrix-01-review#025).


**Remmy's remarks (labelled):** the substance aligns
with the gap register (registry, live-head and
concurrency machinery all UNKNOWN; the register's own
locators are exon-infrastructure-gap-register#002–#006,
control #007 — BM25 surfaced the matrix/audit restate-
ments rather than the register sections themselves).
One citation-form defect, preserved verbatim above:
"exon-category-neighbour-audit#018#010" is a doubled
locator and does not resolve as written.

## Q5 — Later superseding records

**Question (Alex, verbatim):** Any later records that supersede the pool paper or dictionary versions already inspected.

**Sections retrieved (BM25, k=6):** exon-dictionary-03#017a, exon-dictionary-04#019a, exon-infrastructure-gap-register#005, exon-exact-retrieval-03#008, exon-exact-retrieval-03#005, exon-dictionary-03-challenge#020

**Answer (verbatim, gemini-3.1-flash-lite):**

The provided sections do not contain records that supersede the pool paper or dictionary versions already inspected.

**Evidence:**
*   `exon-exact-retrieval-03#005`: "Reconciliation (Alex, PB-ID pb-mw9z5hgf-1q-ct9y, 2026-11-09): Ben's delegation is the source of Alex's decision authority; the older governing documents remain historically accurate records of the authority model before that delegation. Both records are preserved; neither is silently rewritten."
*   `exon-infrastructure-gap-register#005`: "Crusher found no consolidated or general supersession policy; exact status returned: 'UNKNOWN — the corpus does not say.'"


**Remmy's remarks (labelled):** correct for the indexed
corpus — Pool paper Rev 4 and Dictionary 0.4 Rev 3
remain the latest versions there. Note for completeness:
Alex's three decisions (freeze deferred, pool-first,
generation zero not declared) postdate the corpus and
live in the register and programme log, not yet in the
index; no corpus answer could have found them.
