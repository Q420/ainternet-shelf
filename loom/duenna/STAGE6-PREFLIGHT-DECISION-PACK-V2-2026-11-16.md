# Stage 6 Preflight Decision Pack — v2 (2026-11-16)

**Status: DRAFT for Alex's step-1 inspection** (correction round,
step 1 of 3: pack reconciliation → FR-B restoration → Claude
evidence repairs; each step inspected and accepted before the
next, per Alex's ruling of 2026-11-15).

**Supersedes:** `STAGE6-PREFLIGHT-DECISION-PACK-2026-11-15.md`,
whose "already settled" section claimed a candidate and battery
shape that no governing document ever authorised.

## Governing spec

`STAGE5-BUILD-SPEC-26.md` (Rev 26), frozen, is the governing
specification for Stage 6. Nothing in this pack amends it.

## The reconciliation

The trace at `duenna/STAGE6-PACK-RECONCILIATION-TRACE-2026-11-15.md`
established: **no governing amendment exists** for the "candidate
Claude + six tasks, one per category" shape. That shape originated
as a position converged on during the 2026-11-14 measurement runs,
was carried into memory as "settled," and from memory into the
v1 pack. It was never a specification amendment. It is recorded
here as **unreconciled and superseded**. If the owner amends the
spec, he does so explicitly, and this pack is revised to match.

## The pack, reconciled to Rev 26

1. **Subject model:** `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`,
   as specified in the frozen spec.
2. **Battery:** the complete **13-instance battery**, as
   specified. No reduced or per-category subset.
3. **Pin authority (RB-50 Item 3 condition):** Batch 3 pin
   authority stays **distinct** from Batch 6 stack-manifest
   authority in the examination report. The two are never merged
   or cited interchangeably.
4. **FR-B restoration (RB-50 Item 4, required):** the correction
   round must restore the malformed FR-B output and demonstrate,
   with reproducible evidence: (a) the adapter receives malformed
   output; (b) the malformed path is exercised; (c) the specified
   failure/handling result; (d) the tree applies decision_stands
   correctly; (e) the original attempt history is preserved. The
   original 13/13 correction result remains historical record,
   not a substitute for this evidence. (Step 2 of the round.)
5. **Claude evidence repairs (both, step 3 of the round):**
   (i) the checkpoint manifest regenerated without `__pycache__`
   entries; (ii) the correction suite and `reexamine_g4corr.py`
   reproducible from the shelf — acceptance is **independent
   reproduction**, not a claim of reproducibility.
6. **Smoke call:** one minimal smoke call first, under the
   owner's Stage 6 authorisation of 2026-11-12 (effective at
   gates passing; all five gates passed 2026-11-15).

## Still open — the owner's to name

- The **budget figure** for Stage 6 execution.
- The **smoke-call pass bar and its recorder**.

## Execution gate, stated plainly

This pack reconciles the paperwork. It does **not** authorise
Stage 6 execution. Execution still requires the owner's explicit
current go, and cannot start until the two open items above are
named.
