# STAGE 6 SECOND SUBJECT — ATTEMPT 3 EXECUTION EVIDENCE (2026-11-18)

Run: STAGE6BATT-20261118-001, attempt 3 (collect side), Q420/Battery qwen-battery run 44257013046, dispatched 2026-11-18T07:10Z on the timeout-amended configuration, after Alex's technical acceptance of the amendment. Results at qwen-battery-results/STAGE6BATT-20261118-001-attempt3/. This is the first scored attempt for the GPT-OSS subject; attempts 1 (pin not served) and 2 (read timeouts) remain UNSCORED.

Custody: launch 2026-11-18T07:12:12Z; STAGE1 checks pass; LAUNCH_EVIDENCE comparison PASS; termination observed 08:00:38Z; launcher exit code 0; ATTEMPT_CLOSED with outcome S9_CLOSED. Elapsed 48 minutes 26 seconds, inside the 9,000-second watchdog.

Record: 495 events, RUN_CLOSED present. The orchestrator's independent re-derivation with the stack's pilot_record.verify_chain: 495 events, chain intact. RUN_STARTED configuration hashes match the accepted pins: adapter config 37e7c1ea, adapter 9b80c37a, pilot_driver 304310e2 (the corrected T06 checker).

Instances: all 13 trees closed COMPLETED — T01, T02, T03, T04, T05, T06, T07, T08, T09, T09/FR-A, T09/FR-B, T09/FR-C, T09/FR-VALID. T06 completed under the corrected checker. The record also carries 11 STEP_FAILED and 2 RECOVERY_TAKEN events; every tree nevertheless reached completion.

Adapter captures: 13, all transport RESPONSE_RECEIVED, every capture served by openai/gpt-oss-20b (the live-run served-model check). Captures are distributed over 11 instances (T01 and T02 two each); T05 and T08 completed with no adapter capture. Total provider usage across captures: 14,911 tokens; no instance over its ceiling; no budget exhaustion.

Status: execution complete. Formal per-instance verdicts and the run determination belong to Alex's adjudication against the Stage 6 pass bar.
