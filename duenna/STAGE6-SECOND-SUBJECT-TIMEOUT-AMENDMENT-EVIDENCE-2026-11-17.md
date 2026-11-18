# STAGE 6 SECOND SUBJECT — TIMEOUT AMENDMENT: IMPLEMENTATION AND VERIFICATION EVIDENCE (2026-11-17)

Implements Alex's timeout ruling (record/ALEX-SECOND-SUBJECT-TIMEOUT-RULING-2026-11-17.md). The adapter's per-attempt timeout is a configuration value (timeout_seconds_per_attempt), so the amendment is a configuration revision: the adapter code is byte-identical throughout (pin 9b80c37a19b751f765581e0a15476559edaef16c9b85c713dcc09d7bbeca4890).

Changes, complete list:
- Battery adapter config (Q420/Battery qwen-battery-stack/stack/work/actions-adapter-config.json): timeout_seconds_per_attempt 120 → 600; new file pin sha256 37e7c1ea7ddb33fd0d928bfa7ea9e44dcbf7461e9c4e769091c97ee8c8bce378. Model fields unchanged (openai/gpt-oss-20b).
- Run watchdog (qwen-battery-stack/battery_run.py): --watchdog 3600 → 9000; file sha256 749a4caa0621a68e (prefix; full pin in the repository).
- Workflow job timeout (.github/workflows/qwen-battery.yml): timeout-minutes 120 → 180, committed @ 549f6af.
- Prep config (qwen-prep/actions-adapter-config.json): aligned to the production configuration for the verification run — model openai/gpt-oss-20b, timeout 600; file pin sha256 e33451c119ee8133caee45b4f991bcb0dce59ebe169117d1d8c12193daf1ddca, pushed @ f8958008.

(c2) re-verification against the revised configuration, owner's real credential path: Q420/Battery qwen-prep run #2 (44252349468), results committed @ 5421aea. Probe verdict CUSTODY_FEASIBLE. credential_injected: true. (c2) passed: true — all 9 checks true, including value_matched_injected_secret and secret_absent_from_capture_record. The result records adapter_config_sha256 8eb5bb20fa7bbb58caee13279cd1783bf505f67b5b80b4a161286dfda58f746f; the orchestrator re-derived this value independently: it is the RFC 8785 canonical digest of the amended prep config with instance T04's max_tokens substituted, exactly as the adapter computes it. The verification therefore ran against the amended configuration (600 s, GPT-OSS), and the request/response path is otherwise unchanged.

Disclosure: an early push of the prep config landed at the repository root as actions-adapter-config.json (GPT-OSS, 600 s). No workflow reads that path; it is inert. It is recorded here rather than silently left.

Status: ready for Alex's technical inspection. No re-fire until his acceptance. The owner's execution authorisation remains in force.
