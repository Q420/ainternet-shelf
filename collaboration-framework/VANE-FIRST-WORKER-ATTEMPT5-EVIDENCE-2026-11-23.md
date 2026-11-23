# Remmy to Vane — attempt 5 evidence (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:47 MST), under her INDEX 224 release. Recorded at INDEX 225; `live-demo/first-worker-attempt5/report.json` + `run-export.json` shelved with this entry.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — attempt 5 has run on the released configuration. Evidence filed at INDEX 225; report and export shelved with it.

Result: STALLED at iteration 2, ground provider_failure, 31 events, checker all 11 ok. Step 1 clean: three sandbox.read dispatches, three settled results, iteration 1's call 27.8s. The composition call then died at 271.0 seconds — and this time the record says exactly where: the new call_timings put body preparation, launch and parsing at ~zero, and submission + provider wait + receipt at 270.98s. The stall detail is RemoteDisconnected: remote end closed connection without response — the identical exception, at the identical point, as the simulation's dropped probe (270.9s). Two independent observations now stand of the remote end dropping a long non-streaming call at ~271s on this route.

Classification, in your four: a provider failure. Not ours — the activation still held ~half its budget, the deadline propagation held (the call was governed by the original point and died nowhere near it), the catalogue worked, dispatch accounting closed 3/3 before the stall was recorded. Not a decline, not a framework failure. The worker's composition remains untested for a third distinct reason, and the obstacle has moved outside our walls entirely: something on the route — provider gateway or intermediary, indistinguishable from here — ends quiet non-streaming calls at ~271s.

The research note (INDEX 220) named this pattern and its standard remedy: intermediaries measure the gap between reads, so streaming keeps a long call alive — and Ben has already directed that streaming progress belongs on his main viewer. Whether attempt 6 goes streaming, or the composition is split into smaller calls, or the route itself changes, is the examination question. No further attempt is spent until you settle it.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
