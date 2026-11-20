# EXACT RETRIEVAL 03 — delta + Crusher exchange for Alex's audit

Alex's request (pb-mwbwzi3p): exact records on scoped authority
registries and delegation; task registration and versioning;
live-head updates, competing successors and atomicity;
supersession, errata and reliance; conflict-resolution and
concurrency mechanisms.

Finding of the delta scan: the 44 sections in
EXACT-RETRIEVAL-02.md already cover this ground. A wider scan
(delegation, reliance, successor, live-head, version) adds
exactly ONE further section, carried in full below.

## grounding-gate-v12#013

- doc: grounding-gate-v12
- heading: GROUNDING GATE — DESIGN SPEC v1.2 (2026-11-06) > 10. Proposed versioned change (for review, NOT applied)
- sha256: e4bf95202e86ff75890176937e609a993c2255648aa5cc3bb5d179f4d5ef1356
- chars: 453

## 10. Proposed versioned change (for review, NOT applied)
Criteria v1.4 (draft): pre-gradeability clause — "A dossier is gradeable only if
grounding status is GROUNDED; otherwise the run record closes as UNGROUNDED with
the per-item table and attribution, and no test grade is issued." Engine: NO
change proposed; the gate remains a separate checker (folding it into the engine
is a separate decision — new frozen hash + re-provenance per precedent).



## Crusher's five answers, verbatim from crusher-log.jsonl

### Q: Retrieve the exact source records and current versions concerning scoped authority registries and delegation.

**Answer:**
The provided sections do not contain a specific record titled "scoped authority registries" or a dedicated "delegation registry" document. However, the sections provide the **current authority state** and **delegation instruments** regarding who holds authority and what has been delegated.

**Evidence:**

1.  **Current Authority State & Delegation to Alex**
    *   **Source:** `sync-document#003`
    *   **Quote:** "Held by Ben alone, never delegated: any spend; outreach; every Shelf publication; accounts; and any step only his hands or eyes can perform."
    *   **Quote:** "Delegated to Alex (Ben's ruling, 2026-11-08 19:40 PST — "All three are Alex's calls"; accepted by Alex the same minute, PB-ID pb-mw8prztg-z-6u7s), within the Duenna programme only: (1) opening a D3 v0.8 revision step; (2) approving D3; (3) authorising Stage 2 execution."
    *   **Quote:** "Reconciliation (Alex, PB-ID pb-mw9z5hgf-1q-ct9y, 2026-11-09): Ben's delegation is the source of Alex's decision authority; the older governing documents remain historically accurate records of the authority model before that delegation. Both records are preserved; neither is silently rewritten."

2.  **Specific Delegation Dispositions (Current Status)**
    *   **Source:** `sync-document#003`
    *   **Quote:** "(1) v0.8 revision step opening — AUTHORISED."
    *   **Quote:** "(2) D3 approval — ... CONFIRMED THROUGH ADJUDICATION 2026-11-09 ~22:17 (Alex pb-mwacx009-5-9k2b): ... the delegation expressly covers approving D3, and the general reservation in the older authority model does not override a specific delegation by the authority holder. The approval stands CONFIRMED."
    *   **Quote:** "(3) Stage 2 execution — NOT AUTHORISED. Prerequisites outstanding..."

3.  **General Authority Model (Pre-Delegation/Structural)**
    *   **Source:** `process-tree-v04#018`
    *   **Quote:** "Authoring/approval authority — RULED BY BEN (§10.3): approval Ben's alone; proposal rights Remmy and Alex; no standing delegation."
    *   **Note:** This section describes the structural rule in the process tree, which `sync-document#003` clarifies is superseded by the specific delegation for the Duenna programme items listed above.

4.  **Crusher's Role (Retrieval Only)**
    *   **Source:** `crusher-seat-ruling-01#002`
    *   **Quote:** "The primary occupant's job is to retrieve relevant canonical sections in response to questions, with evidence and provenance."
    *   **Source:** `sync-document#003`
    *   **Quote:** "Crusher's seat: retrieval only. He answers grounded in the canonical index, with provenance, and answers UNKNOWN outside the corpus. He holds no decision authority."

**Conclusion:**
There is no separate "registry" document in the provided corpus. The **current versions** of authority and delegation are recorded in **`sync-document#003`** (specifically the "AUTHORITY STATE" section), which details Ben's retained authority and the specific delegation to Alex for the Duenna programme. The structural rules for authority are in **`process-tree-v04#018`** (§10.3), but `sync-document#003` explicitly states that the specific delegation governs the current state for the delegated items.

### Q: Retrieve the exact source records and current versions concerning authorised task registration and registry versioning.

UNKNOWN — the corpus does not say.

Closest sections provided: d3-v07#004, d3-v09-specification#004, alex-combined-adjudication-r60rev#001, sync-document#001, process-tree-v04#005.

### Q: Retrieve the exact source records and current versions concerning live-head updates, competing successors and atomicity.

UNKNOWN — the corpus does not say.
Closest sections provided: execution-contract-v01#013, crusher-seat-ruling-01#002, d3-v07#042, d3-v09-specification#042, sync-document#001.

### Q: Retrieve the exact source records and current versions concerning supersession, errata and reliance.

The provided sections do not contain a consolidated record of "supersession, errata and reliance" as a single topic. However, they contain specific records regarding **errata** (process-tree-v04#021a) and **reliance** (d3-v08-change-record#004, fixture-harness-v09#018). There is no section explicitly titled or dedicated to "supersession" in the general sense, though version changes are recorded.

Here are the exact source records and current versions concerning the specific terms found in the corpus:

### 1. Errata
**Section:** `process-tree-v04#021a`
**Doc:** `process-tree-v04`
**Version:** v0.4 (Change record v0.3 → v0.4)
**Evidence:**
> "Remmy withdrew the inference, entered errata in the scope ledger and the evidence ledger (the "approved" entries stand corrected, not deleted), owned the overreach to Ben, and put the exact question to him on a two-option card: approve the impossible-rule ending, or leave it unapproved for now."

### 2. Reliance
**Section:** `d3-v08-change-record#004`
**Doc:** `d3-v08-change-record`
**Version:** v0.8 (Correction Pass)
**Evidence:**
> "**R45 — REQ-C-2's reliance made conditional.** Source line carries the conditionality, and a sentence in the Requirement states it in full: if the PROPOSED declaration does not stand, no declaration exists, eligibility cannot be established, and C-2's machinery does not engage. Applied together with R41 (both-or-neither held). Status: implemented."

**Section:** `fixture-harness-v09#018`
**Doc:** `fixture-harness-v09`
**Version:** v0.9
**Evidence:**
> "REQ-K-4/R64: checker verdicts are carried as REPORTED evidence; the independence caveat must ride with each verdict; reliance on a checker for any judgement must be recorded."
>
> Code snippet:
> ```python
> if rep.get("uses_checker_for_preservation"):
>     rel = rep.get("checker_reliance", [])
>     if not rel or any(not r.get("recorded") for r in rel):
>         return "FAIL: checker reliance unrecorded"
> ```

### 3. Supersession
**Status:** UNKNOWN — the corpus does not say.
The provided sections discuss version changes (e.g., v0.3 to v0.4 in `process-tree-v04#021a`) and corrections (e.g., `d3-v08-change-record#004`), but no section explicitly defines or records a "supersession" policy or event under that specific term.

**Closest sections provided:**
*   `process-tree-v04#021a` (Change record v0.3 → v0.4)
*   `d3-v08-change-record#004` (D3 v0.8 Correction Pass)

### Q: Retrieve the exact source records concerning any existing conflict-resolution or concurrency mechanism.

UNKNOWN — the corpus does not say.
Closest sections: crusher-seat-ruling-01#002, grounding-gate-v12#011, process-tree-v04#016, d3-v07#042, d3-v09-specification#042
