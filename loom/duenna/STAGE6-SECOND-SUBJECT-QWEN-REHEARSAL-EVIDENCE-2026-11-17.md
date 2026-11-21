# STAGE 6 SECOND SUBJECT (QWEN) — ACTIONS DRESS REHEARSAL EVIDENCE (2026-11-17)

Design basis: Alex's second-subject design ruling (record/ALEX-SECOND-SUBJECT-QWEN-DESIGN-RULING-2026-11-17.md). Preparation evidence (c2 complete): duenna/STAGE6-SECOND-SUBJECT-QWEN-PREP-EVIDENCE-2026-11-17.md.

Run: Q420/Battery, workflow qwen-rehearsal #1, run ID 44207076274, dispatched 2026-11-17 17:20 MST, commit 5035cc6. Results read first-hand from qwen-rehearsal-results/ in the Battery repo.

Configuration check (fail-closed, ran before the room was built): passed = true. adapter_unchanged (9b80c37a), battery_harness_unchanged (eb7be464, byte-identical to the first battery), config_is_qwen_variant (78abeac6), model_pin_is_qwen (qwen/qwen3-next-80b-a3b-instruct in both model fields), battery_driver_corrected_pin (304310e2), rehearsal_driver_corrected_pin (304310e2). The only content changes from the first battery's stacks are the Qwen adapter config and the accepted T06 checker correction.

Rehearsal run G4CORR-20261118-001 (stub subject, no live call): events 483, tree_closed 13/13, run_closed true, adapter_captures 13, captures 12, artefacts 5 — the same profile as the first battery's accepted rehearsals (runs #5, #6, #7). The custody probe gate passed on the fresh runner (the workflow is fail-closed; the fire step ran).

Token-usage accounting: the adapter's usage path is unchanged code; the (c2) capture records provider-reported usage (prompt/completion/total) from the response. The loopback capture server's canned response is a fixed fixture (its served-model string is a fixture value, not a live measurement); served-model identity is verified from live-run captures, as in the first battery. Budget-exhaustion handling is the unchanged adapter/harness code path, evidenced by the byte-identical pins above rather than by a stub-run exercise.

Disposition: preparation is complete against the design ruling — pin applied, (c2) repeated and passed on Actions, rehearsal passed with the production configuration selecting Qwen. Next step per the ruling's sequence: Alex's inspection of the preparation evidence. Execution remains unauthorised and requires the owner's separate word.
