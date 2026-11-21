# BATTERY SOURCE FOR INSPECTION — TIMEOUT AMENDMENT (2026-11-17)

Copied verbatim from Q420/Battery (private) to this public shelf directory at the owner's direction (2026-11-17 23:53 MST), so the reviewer's technical inspection can reach the source at its pins. Each file's sha256 was computed on the copied bytes and matches the pins in the amendment evidence.

| Shelf file | Repository path | sha256 (prefix) |
|---|---|---|
| battery-actions-adapter-config.json | qwen-battery-stack/stack/work/actions-adapter-config.json | 37e7c1ea7ddb33fd |
| prep-actions-adapter-config.json | qwen-prep/actions-adapter-config.json | e33451c119ee8133 |
| actions_adapter.py | qwen-battery-stack/stack/work/actions_adapter.py | 9b80c37a19b751f7 |
| battery_run.py | qwen-battery-stack/battery_run.py | 749a4caa0621a68e |
| qwen-battery.yml | .github/workflows/qwen-battery.yml | 5ae65c105934415f |
| c2_driver.py | qwen-prep/c2_driver.py | 7d9aa495d134168c |
| c2-result.json | qwen-prep-results/c2-result.json | d93cf7d37604c1e5 |
| credential-injection.json | qwen-prep-results/credential-injection.json | 8d32a448551742ed |
| probe-result.json | qwen-prep-results/probe-result.json | 91d4f9da5470605b |

What each establishes: the battery config carries timeout_seconds_per_attempt 600 and the GPT-OSS pin; the adapter file hashes to the accepted pin 9b80c37a (byte-identical, unamended); battery_run.py carries --watchdog 9000; the workflow carries timeout-minutes 180; the (c2) driver and its run #2 result artefacts are the verification implementation and outcome (passed, 9/9, config digest 8eb5bb20). The stray root-level config's inertness is checkable from qwen-battery.yml: no step reads a root-level config path.
