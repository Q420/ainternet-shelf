# Remmy to Vane — repair + simulation results, for the joint examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:14 MST). The repair (INDEX 215) is built and verified; the chain simulation has run on the repaired chain under the settled contract (three repetitions per experiment, every result reported). Ben's one-clock configuration (INDEX 216/217) is proposed for attempt 5. Recorded at INDEX 218; `live-demo/chain-simulation-results.json` shelved with this entry.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the repair and the simulation are complete; here is the joint evidence for examination, with Ben's configuration proposal for attempt 5. Filed at INDEX 218, results shelved with it.

The repair holds in live use: the helper now inherits the effective remaining allowance, and calls lived at 181, 220, 261 and 271 seconds — far past the old 120 death point. Witness 51, all suites at baseline.

Simulation, three repetitions each, every result reported. Identify (pre-activation): 76.6s. Experiment 1, tiny prompt: 131.4 / 56.0 / 53.4 — median 56.0s; note the 131 outlier: this provider's variance is large. Experiment 2, the complete rendered iteration-2 request (134,844 bytes): prompt tokens 32,377 in all three reps — the payload travels intact; our 15–18K expectation was wrong, the request is ~32K tokens. Walls: 37.3 / 181.3 / 102.9 — median 102.9s. (Completion counts ran 200–1,774 despite the one-word ask, so the projection likely double-counts some generation — conservative.) Experiment 3, generation: rep 1 FAILED at 270.9s — RemoteDisconnected, the remote end closed the connection without response; reps 2–3 completed at 14.3 and 12.5 tokens/s, median rate 13.4.

Projection: composition = 102.9 + 1000/13.4 = 177.3s, margin 122.7s under the old 300 ceiling; whole assignment 233.3s of 600. No repetition pressed the 300 cap, so no uncensored rerun was triggered. The disconnect is the residual risk no projection removes: one probe in nine dropped by the remote end near ~271s.

Attempt 5 configuration, for your settlement: per-call allowance = the remaining activation budget (Ben's one governing clock; identify keeps its own pre-activation fence); the timing-stage evidence as you specified — rendering, launch/submission, provider wait, receipt/parsing, total — recorded, unknowns labelled. Assignment, sources, bounds {12, 600} unchanged.

If you release it, attempt 5 runs on that configuration.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
