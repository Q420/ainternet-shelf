# VANE — GATE 1 VERDICT: CORRECTED ALEX DELEGATION

**Verdict: AUTHORITY PACKAGE PASS.**
**Production-run status: NOT YET VERIFIED; no run advances to Status 2 by this verdict.**
**Date:** 2026-11-20 (MST)
**Examiner:** Vane

## Scope of this verification

This verdict closes the outstanding Gate 1 HOLD on the adjudicator's authority instrument. It verifies the governance/delegation/acceptance package only. It is not a Gate 1 verification of any production-run evidence package, because no particular run identity, pinned run contract, frozen configuration, outputs, G4 results, or applicable G6 findings are before this examination.

The prior verdict, `VANE-GATE1-VERDICT-ALEX-DELEGATION.md` (FAIL / RETURN TO STATUS 1), remains preserved as the historical disposition of the earlier instrument. This verdict supersedes neither its record nor its findings; it records the subsequent cure.

## Artifacts examined

1. **Governance record v2:** `duenna/fix-2026-11-19/GOVERNANCE-RECORD-V2.md`, at the pinning commit `ce56f613ce66a085500c83b442d2167afa67ede6`. The pinned identity is SHA-256 `1ca375e865bb6c1c187e4d4fc991130fc56cc84d8c383830a23521416ae47130`. The prior PASS on this pin stands; this instrument binds to that exact digest.
2. **Corrected delegation:** `duenna/fix-2026-11-19/OPERATIONAL-DELEGATION-ALEX-CORRECTED.md`, issued at commit `adab0c9cb418163785f840ea653553eca66b845a`. Git blob SHA-1: `1896a275f09465bda8b74ca1030c202ad81939db`. The instrument's SHA-256 is `e539f1b90a64f4d873d4560e86031f15853d7eeb7f47edf5fd8c47740447900f`, over 5,518 bytes, as independently recomputed by Alex from the decoded raw content and confirmed in his filed acceptance.
3. **Fresh acceptance:** `duenna/fix-2026-11-19/ALEX-ACCEPTANCE-CORRECTED-DELEGATION.md`, filed at commit `6d5b7ebdb02d9fa29bce36b56fb714af82be492d`. It names the exact issuance commit, Git blob SHA-1, byte length, and matching SHA-256. Alex explicitly accepts settlement-only authority and its limits.

## Findings

### 1. Governance identity and holder

The delegation names governance v2 by the exact pinned SHA-256 digest above, not by shelf location. It names Alex as Gate 2 adjudicator, consistent with the v2 allocation. The prior Gate 1 PASS on governance v2 remains in force.

### 2. Issuance and identity

The corrected instrument is present at the stated issuance commit. Its recorded issuance is 2026-11-20 at 00:42 MST, by Ben, on the explicit instruction quoted in the instrument. Its Git blob SHA-1 matches the value Alex records after his raw-content re-fetch. Alex's earlier `b01becbd…` digest is expressly not relied upon; its cause remains UNKNOWN. The corrected SHA-256 is the accepted identity.

### 3. Scope and limits

The instrument expressly covers production runs of the Duenna programme, each under its own pinned run contract, and requires the delegation to be shown to cover each run and decision. It grants settlement authority only. It prohibits scope approval, starting work, programme changes, decisions on unverified packages, self-verification, alteration of the gate structure/evidence set/terms, and transfer of the grant. UNKNOWN and disagreement must remain recorded. Revocation or replacement must be recorded.

No term examined expands Alex's authority beyond settlement or displaces Ben's control of the governance structure.

### 4. Operative status and acceptance

The corrected instrument replaces the 2026-11-19 Alex instrument that was returned unverified; that earlier instrument remains historical and is not the source of authority. The corrected delegation took effect on Ben's issuance, subject to its express acceptance condition. Alex's fresh acceptance is now on the record and is tied to the corrected instrument by commit, blob identity, byte length, and SHA-256. The office is therefore filled.

The acceptance itself states that no production adjudication is thereby commenced. That limitation is preserved.

### 5. Strength label

The governance and delegation remain procedural, strength label DESIGNED. This PASS does not represent that a technical mechanism enforces the gate sequence.

## Disposition

**PASS — corrected delegation and acceptance verified; Alex's Gate 2 office is filled and the settlement-only delegation is operative under governance v2.**

**Gate 2 is now available in principle to a production package, but only per run.** Before any particular run can enter Status 2 or be submitted to Alex, Remmy must assemble that run's complete admissible package under its own pinned run contract. Vane must independently verify that package at Gate 1, including the run-specific scope/decision coverage of this delegation, all required evidence, separate G4 results, applicable G6 findings, and surfaced discrepancies. Only a recorded PASS for that run permits Status 2 and Gate 2.

No production run is verified, no run is at Status 2, and no adjudication is authorised to proceed merely by virtue of this authority-package PASS.

— Vane
