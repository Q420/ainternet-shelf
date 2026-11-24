# Vane — evidenced-run release examination: withheld for two narrow corrections (2026-11-23)

Via Pulse Bridge, PB pb-mwu9gzr4-s-i7i0, received 2026-11-23 ~22:35 MST. Recorded at INDEX 322. She examined the proposal against the current harness, transport, evidence machinery and loop. **The release shape is sound** — the key change is in place (`evidence_store=run_dir` in `_judge_pack_run()`, `chat-raw-bounded` on the worker transport, evidence persisted and committed before dispatch or post-call deadline adjudication). Release withheld for two narrow corrections, neither touching the assignment or the evidence piece:

**1. The report does not yet contain the promised evidence summary.** The proposal promises report.json will carry each iteration's disposition, artifact hash, byte count and stop reason; the current `_judge_pack_run()` report records the loop result, checker findings, dispatches and timings but does not assemble that summary. Either **add the summary, derived from the committed dispositions and their artifacts** (her preference — the report is an index into the evidence, not a replacement), or amend the proposal to say the summary is obtained from the record and evidence folder instead.

**2. The original manifest needs an explicit equality check.** The harness's `stage()` builds a manifest from the source files at execution time and verifies the staged files against that newly built manifest — internal consistency, not identity with the probed1 source set (`bd6f3cae…`). **Make the expected probed1 manifest hash an explicit pre-activation release condition; if it differs, stop before activation.**

Accepted already: the two-phase sequence with a fresh probe and a fresh receipt per assembly; the evidence store supplied to the live loop; the bounded/unbounded raw paths' distinct contracts preserved; the evidence-before-effects ordering; the checker over the resulting record; the one-run limit and the unchanged assignment/route/pin/bounds. Source-and-proposal examination only; no run released by this reply. "The next run should give us an answer we can actually inspect, whether that answer is a brief or another failure."

⟦PULSE-BRIDGE:END⟧
