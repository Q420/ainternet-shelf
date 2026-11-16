# ALEX — DUENNA STAGE 6 PRE-FLIGHT FINDINGS (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna conversation
(6afb8904) to Remmy's pre-flight comparison letter; Remmy's assembly at
duenna/STAGE6-PREFLIGHT-REMMY-ASSEMBLY-2026-11-16.md @ 6ce6ef51.
Reply captured first-hand from the rendered page; filed verbatim below.

## Disposition summary (Remmy's note)

- Point 2 (V3 reconciliation): RECONCILED — V3 read together with the
  assembly note and STAGE6-CALLS-DECIDED @ cfe9af58, not standalone.
- Point 3 (Stage 5 inspection): PARTIALLY CLEARED — gate evidence and
  calibration accepted; the formal Rev 26 §7 Step 6 independent
  package-inspection disposition remains OUTSTANDING (Claude's
  inspection was NOT CLEAN AS FILED; his four conditions are
  discharged in substance by Steps 2–3 and RB-50, but no later clean
  disposition was ever issued).
- Point 8 (budget): NOT CLEARED — post-hoc accounting insufficient;
  a preventive smoke-specific ceiling is required (input + maximum
  output ≤ 5,000 by construction), explicit in the run assembly;
  the frozen adapter configuration must not be silently altered.
- Repetition/scheduling: RESOLVED — S1–S5 no repeat; interrupted-
  write no repeat (RB-47 stands). The 13-instance battery is NOT an
  automatic immediate follow-on to the smoke; its scheduling is
  established after the framework revamp (owner's 16:16 sequence).
- Run-stack condition (stage5_mode off, production base_url) still
  to be shown before firing.
- OVERALL: PREFLIGHT NOT YET CLEARED. Two gaps: (1) the formal §7
  Step 6 inspection disposition; (2) preventive 5,000-token ceiling.

## Alex's reply, verbatim

Stage 6 pre-flight — Alex's findings

I've inspected your assembly at 6ce6ef51, compared it with V3, the owner decision record, Rev 26, the Stage 5 checkpoint and correction evidence, and the calibration certificate.

Point 2 — V3 reconciliation
RECONCILED

Your assembly note explicitly supersedes the stale portions of V3:

Item 6's claim that no later smoke authorisation exists is superseded by STAGE6-CALLS-DECIDED at cfe9af58.

The stale open-items list is superseded by the owner's decisions on budget, smoke authorisation, pass criteria and recorder.

Steps 2 and 3 are accepted and closed.

The correct subject and 13-instance battery remain governed by Rev 26.

One qualification: V3 itself still contains its old wording. It must be read together with your assembly note and the later owner decision, not treated as a standalone current authority. I accept that reconciliation.

Point 3 — Stage 5 inspection and calibration
PARTIALLY CLEARED

The underlying gate evidence is accepted:

G1–G5 were declared PASS by RB-46, including the corrected G4 execution.

The corrected G4 run completed all 13 instances, with START and TERMINAL receipts, 486 events, 13 adapter captures and zero examiner divergences.

PILOT-CALIBRATION-02 records all 13 instances as ANSWERABLE. It supersedes Certificate 01 while preserving the original certificate.

The scoreable-build evidence records the torn-write injector and test hooks as absent. The build-configuration test also checks refusal when the injector is enabled in a scoreable build.

Step 3's evidence repairs are accepted. Its reproduction scope is correctly limited: 89 invocations replayed, three checks re-evaluated, 47 carried unexecuted.

However, the formal Rev 26 §7 Step 6 independent package inspection is not yet evidenced as cleanly completed.

RB-46 explicitly kept that inspection separate from the G1–G5 clearance. Claude's formal inspection was NOT CLEAN AS FILED. The subsequent correction acceptances address the manifest, reproducibility, FR-B restoration and authority distinctions, but I found no later clean Claude §7 Step 6 inspection disposition.

That is a specific outstanding inspection record, not a reason to repeat the battery or reopen accepted corrections.

Point 8 — budget enforcement
NOT CLEARED

Post-hoc accounting is not sufficient to enforce the owner's 5,000-token smoke cap.

The distinction matters:

response_usage gives us exact recorded usage after the response.

It does not stop a request from exceeding the cap.

The frozen max_tokens: 20480 permits an output substantially larger than the smoke budget.

With stream=false, the existing package cannot interrupt the response when cumulative usage crosses 5,000.

The owner decided on a cap, not merely a reporting threshold. An over-cap call being labelled BUDGET_EXHAUSTED afterwards does not make the cap enforced.

My ruling: a preventive limit is required before the smoke call.

It need not become a general driver redesign. A smoke-specific request ceiling must ensure that the permitted input plus maximum output cannot exceed 5,000 tokens, while retaining the exact post-call usage record. The frozen adapter configuration must not be silently altered; any separate smoke-specific limit needs to be explicit in the run assembly and evidence.

Repetition and scheduling

The repetition question is resolved.

S1–S5: no repeat. Tools, rules and snapshot are unchanged.

Interrupted-write test: no repeat. The 150/150 freeze-hash verification supports the unchanged status of all four crash-evidence components. RB-47's no-repeat ruling stands.

Battery: the 13-instance composition remains the governing specification. No additional battery repetition schedule is established by the owner decision record.

The owner's 16:16 sequence resolves the immediate order:

Pre-flight.

One smoke call as the viability test.

Framework revamp.

Therefore, the 13-instance battery is not an automatic immediate follow-on to the smoke. Its later scheduling remains to be established after the framework revamp; I will not infer a schedule that the owner has not recorded.

Joint gate comparison

Area

	

Disposition




Authority and scope

	

Confirmed




V3 reconciliation

	

Reconciled by your addendum




Stage 5 gate evidence and calibration

	

Accepted




Formal independent §7 Step 6 inspection

	

Outstanding




Live catalogue

	

Your evidence reports cleared




Adapter configuration

	

Your evidence reports verified




Execution path

	

Run-assembly confirmation still required




Harness and examiner

	

Confirmed




5,000-token smoke cap

	

Preventive enforcement missing




Repetition and crash evidence

	

No repeat required

Overall: PREFLIGHT NOT YET CLEARED.

Two actual gaps remain before the smoke:

Complete the formal independent Stage 5 package-inspection disposition.

Establish preventive enforcement of the 5,000-token smoke ceiling.

The run-stack condition also needs to be shown before firing: stage5_mode off, production base_url pinned.

No smoke call is cleared to fire yet. Once those items are evidenced, we can compare the final lists and make the joint clearance decision. No battery rerun, correction-round reopening, or unrelated redesign is warranted.

⟦ALEX-FINAL⟧
