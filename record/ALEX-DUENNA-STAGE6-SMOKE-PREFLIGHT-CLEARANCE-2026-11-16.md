# Alex — Stage 6 Smoke Pre-flight Gate Ruling

**Date:** 2026-11-16  
**Disposition:** CLEARED — one smoke call authorised  
**Authority:** Owner decision `record/STAGE6-CALLS-DECIDED-2026-11-16.md` @ `cfe9af58`, together with the owner's delegation to Alex to make the pre-flight decision and the owner's direction that Remmy fire the call on Alex's clearance.

## Evidence reviewed

- Smoke assembly: `duenna/stage6-smoke-assembly-2026-11-16/` @ `8ac3c811`.
- Smoke assembly inspection: `record/ALEX-DUENNA-SMOKE-ASSEMBLY-INSPECTION-2026-11-16.md` @ `81cd839e`.
- Prior pre-flight comparison: `record/ALEX-DUENNA-PREFLIGHT-FINDINGS-2026-11-16.md` @ `615807de`.
- Claude's final Rev 26 §7 Step 6 disposition: `record/CLAUDE-DUENNA-STEP6-DISPOSITION-CLEAN-2026-11-16.md` @ `a3ae8274`.
- RB-50 Items 3 and 4 re-issued ruling: `record/ALEX-DUENNA-RB50-ITEMS-3-4-REISSUED-2026-11-16.md` @ `3da638caaace1f4bfed71b877eb432551aaae249`.
- Step 2 FR-B restoration evidence and formal orphan-run addendum: `duenna/STEP2-FRB-RESTORATION-EVIDENCE-2026-11-16.md` @ `9ceca1fcee37535a926103189ce6ded46f1ae5de`.
- Controlling Stage 6 call, budget, recorder and pass-bar decision: `record/STAGE6-CALLS-DECIDED-2026-11-16.md` @ `cfe9af58`.

## Gate findings

1. **Authority and sequence — CLEARED.** The owner decision authorises one smoke call after correction Steps 2 and 3 have been inspected and accepted, before any battery instance. The owner's delegation and instruction in this exchange make this Alex's final pre-flight decision; Remmy is to fire only on this clearance.
2. **Decision-pack reconciliation — CLEARED.** The later owner decision and the filed pre-flight reconciliation control over stale standalone wording in V3. The owner's sequence remains: pre-flight, one smoke call, framework revamp. The 13-instance battery is not an automatic immediate follow-on.
3. **Stage 5 evidence and calibration — CLEARED.** G1–G5 and the corrected G4 evidence remain accepted under RB-46; PILOT-CALIBRATION-02 records all 13 instances ANSWERABLE. Correction Steps 2 and 3 remain accepted. No repeat of the prior battery or interrupted-write test is required.
4. **Rev 26 §7 Step 6 independent inspection — CLEARED.** Claude's re-inspection is filed CLEAN, with two explicitly non-blocking notes. All four conditions are discharged: checkpoint manifest; correction suite and reproduction (with its scope limit stated); pin authority under the Batch 3/Batch 6 distinction; and FR-B restoration under R1. The event 384/388 reference error was corrected in Alex's acceptance. The orphaned runs are formally dispositioned: no evidence drawn, retained as historical artefacts, and G4CORR-20261116-003 alone remains the run of record. Claude's stated limitation that he did not independently re-verify hashes or underlying artefacts is noted; this ruling relies on the prior Alex inspections and accepted evidence for those matters, not on an expanded claim about Claude's inspection.
5. **Live model catalogue — CLEARED** on the previously inspected assembly evidence; no new catalogue change is reported.
6. **Adapter configuration and execution path — CLEARED.** The inspected smoke-specific adapter pins the derived config; the frozen adapter remains unchanged. Live harness configuration selects `stage5_mode=False` and the production endpoint, with the documented credential-surrogate/proxy differences isolated in the smoke variant. The connectivity/construction probes are setup evidence, not a model result.
7. **Harness and examiner readiness — CLEARED.** T04 is selected. It has one MODEL step, no recovery path, and one adapter call by tree definition. The dry-run qualification is a path demonstration with the subject failure honestly recorded, not a model pass.
8. **Smoke token ceiling — CLEARED.** The smoke config contains exactly the two authorised changes: `max_tokens=4355` and `max_attempts=1`. The input ceiling is 645 tokens (597 content bytes plus 48 framing allowance), leaving 4,355 output tokens within the owner's 5,000-token total cap. The config hash begins `ebb83d77`; the smoke adapter pins the derived hash. One attempt prevents an automatic second spend.
9. **Repetition and interrupted-write evidence — CLEARED.** No S1–S5 or interrupted-write repeat is required under the accepted no-repeat ruling. The battery remains governed by Rev 26 and the owner decision; this clearance does not schedule or authorise it.

## Final ruling

**The Stage 6 pre-flight gate is CLEARED. Remmy is authorised to fire exactly one live smoke call**, and no other Stage 6 call, with the following fixed conditions:

- Tree: **T04**.
- Smoke config: pinned derived config hash beginning **`ebb83d77`**.
- `max_attempts=1`.
- `max_tokens=4355`.
- Production endpoint, with the inspected smoke adapter variant and pilot supervisor.
- Enforce the owner's **5,000-token total cap** (input + output).
- Do not retry, substitute a paid route, run a battery instance, or otherwise expand the call.
- Preserve and file the complete examiner run record, adapter capture, supervisor START/TERMINAL commitments and associated evidence for Alex's adjudication.

The smoke pass bar remains exactly as the owner decided: full harness traversal and a complete, well-formed run record. Task brilliance is not the smoke-gate criterion. A failed, incomplete, malformed or over-budget call is not a pass; report the actual result without retrying.

This ruling authorises the one smoke call only. It does not authorise the 13-instance battery or alter the owner's sequence. After the smoke, Alex adjudicates the complete record and sets the battery pass bar from the smoke evidence, as directed by the owner.

**Signed:** Alex  
**⟦ALEX-FINAL⟧**
