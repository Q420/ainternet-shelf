# POOL RETRIEVAL 01 — THE FOUR CRUSHER EXCHANGES, VERBATIM

Extracted from the Crusher exchange log at Alex's request
(pb-mwc30a28-1-aggr: the exchanges inspected, not summarised).
Source log: workspace pulse-bridge/index/crusher-log.jsonl —
a workspace file, not previously shelved; this annex is its
shelf copy for these four exchanges. Requester: alex.
Run 2026-11-11 for the Approved Pool design paper.

## Exchange 1
- Timestamp: 2026-11-11T11:10:27.239438+00:00
- Question, as put: Infrastructure Gap 2 and its original definition of atomic live-head updates.
- Sections returned: exon-field-matrix-02-alex#017, exon-infrastructure-gap-register#003, exon-dictionary-03#022, exon-dictionary-04#025, exon-infrastructure-gap-register#005, exon-exact-retrieval-03#007

Answer, verbatim:

**Answer:**
Infrastructure Gap 2 is defined as **"Atomic live-head update"**. Its status is **UNKNOWN — not established by retrieved corpus**.

**Evidence:**

1.  **Definition and Status:**
    *   From `exon-infrastructure-gap-register#003`:
        > "## Gap 2 — Atomic live-head update"
        > "**Status:** UNKNOWN — not established by retrieved corpus."

2.  **Specifics of what is NOT established (Original Definition/Scope):**
    *   From `exon-infrastructure-gap-register#003`:
        > "**Not established:**
        > - A canonical live-head record for a commitment chain.
        > - An atomic compare-and-set or equivalent single-winner update.
        > - A rule for determining which successor becomes operative when two authorised successors target the same predecessor.
        > - A durable record of rejected or competing successor branches."

3.  **Machinery Required (Defining the Gap's Boundary):**
    *   From `exon-infrastructure-gap-register#003`:
        > "**Machinery required before claiming FORM enforcement:**
        > - One authoritative head per commitment chain.
        > - A single atomic operation that checks the expected predecessor and changes the head.
        > - A deterministic conflict result when the expected predecessor is no longer current.
        > - Preservation of losing successors as visible, non-operative records.
        > - A read-after-write confirmation identifying the new live head."

4.  **Corroboration in Field Matrix:**
    *   From `exon-field-matrix-02-alex#017`:
        > "2. Atomic live-head update (Gap 2)."
        > "This matrix does not claim that the following mechanisms exist..."

5.  **Corroboration in Dictionary:**
    *   From `exon-dictionary-03#022` (and identical text in `exon-dictionary-04#025`):
        > "Gap 2 — atomic live-head update (UNKNOWN)."
        > "A gap changes status only when an exact mechanism is retrieved or built, version-pinned, and independently tested. UNKNOWN is preserved as UNKNOWN throughout."

6.  **Retrieval Basis:**
    *   From `exon-infrastructure-gap-register#003`:
        > "**Retrieval basis:**
        > - Crusher Retrieval 03, verbatim answer: “UNKNOWN — the corpus does not say.”"
    *   From `exon-exact-retrieval-03#007`:
        > "Q: Retrieve the exact source records and current versions concerning live-head updates, competing successors and atomicity.
        > UNKNOWN — the corpus does not say."

## Exchange 2
- Timestamp: 2026-11-11T11:10:33.948348+00:00
- Question, as put: Existing master-ledger, registry, version-pointer or supersession mechanisms anywhere in the admitted Shelf corpus.
- Sections returned: exon-field-matrix-02-alex#017, exon-exact-retrieval-02#001, exon-infrastructure-gap-register#005, exon-replay-matrix-02#015, exon-dictionary-03#005, exon-dictionary-03-reconciliation#008

Answer, verbatim:

UNKNOWN — the corpus does not say.

The provided sections explicitly state that the following mechanisms are **not** established or are **UNKNOWN**:
*   **Task registration and registry versioning:** `exon-field-matrix-02-alex#017` states, "This matrix does not claim that the following mechanisms exist: 1. Task registration and registry versioning (Gap 1)."
*   **Atomic live-head update:** `exon-field-matrix-02-alex#017` states, "This matrix does not claim that the following mechanisms exist: 2. Atomic live-head update (Gap 2)."
*   **Concurrency and conflict resolution:** `exon-field-matrix-02-alex#017` states, "This matrix does not claim that the following mechanisms exist: 3. Concurrency and conflict resolution (Gap 3)."
*   **General supersession/reliance policy:** `exon-infrastructure-gap-register#005` states, "**Status:** Partially evidenced; general policy UNKNOWN." and "**Not established:** ... A general rule authorising one message to supersede another."
*   **Dedicated machine-readable authority registry:** `exon-field-matrix-02-alex#017` states, "This matrix does not claim that the following mechanisms exist: 5. Dedicated machine-readable authority registry (Gap 5)."

While `exon-dictionary-03#005` defines fields like `task_registry_ref` and `previous_record_hash`, `exon-dictionary-03-reconciliation#008` clarifies that these are "hash-chain design, not an existing capability claim" and that "Gaps 2–4 remain UNKNOWN until the mechanism is retrieved, inspected and independently tested."

Closest sections: `exon-field-matrix-02-alex#017`, `exon-infrastructure-gap-register#005`, `exon-replay-matrix-02#015`, `exon-dictionary-03-reconciliation#008`.

## Exchange 3
- Timestamp: 2026-11-11T11:10:55.856464+00:00
- Question, as put: Existing generation identifiers and manifest conventions that might conflict with the proposed ID grammar.
- Sections returned: qwen-ab-v2r-results#005, qwen-ab-results-v1#009, correction-matrix-r33-r65#002, exon-field-matrix-02-alex#004, qwen-ab-results-v1#011, exon-dictionary-03-reconciliation#008

Answer, verbatim:

UNKNOWN — the corpus does not say.

Closest sections provided: qwen-ab-v2r-results#005, qwen-ab-results-v1#009, correction-matrix-r33-r65#002, exon-field-matrix-02-alex#004, qwen-ab-results-v1#011, exon-dictionary-03-reconciliation#008.

## Exchange 4
- Timestamp: 2026-11-11T11:11:01.951202+00:00
- Question, as put: Any existing concurrency or compare-and-swap requirements.
- Sections returned: exon-exact-retrieval-03#012, exon-field-matrix-02-alex#014a, exon-dictionary-03-reconciliation#008, exon-flag-correction-proposal#023, exon-dictionary-03-reconciliation#010, exon-exact-retrieval-02#001

Answer, verbatim:

UNKNOWN — the corpus does not say.
Closest sections: exon-exact-retrieval-03#012, exon-dictionary-03-reconciliation#008, exon-dictionary-03-reconciliation#010, exon-flag-correction-proposal#023, exon-field-matrix-02-alex#014a
