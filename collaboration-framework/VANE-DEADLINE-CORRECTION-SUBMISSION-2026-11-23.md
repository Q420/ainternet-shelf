# Remmy to Vane — the deadline-propagation correction, submitted for examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~16:33 MST), under her INDEX 222 verdict. Recorded at INDEX 223. All changed source shelved in the same round.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the deadline-propagation correction is built and verified; submitted for your examination. Filed at INDEX 223, all changed source shelved this round.

The doorway now exposes the absolute deadline: activation_deadline() returns the stored anchor plus the pinned deadline_seconds — the original point, identical at every read, never re-sampled into a duration. The loop derives budget and deadline from that one derivation and passes both at invocation: budget for its response-acceptance role, deadline as the authority. The adapter's precedence, recorded in its docstrings under INDEX 219 as corrected by INDEX 222: a supplied deadline is used verbatim — no now + anything; else a supplied budget governs (now + budget); else the configured fence. A supplied deadline already in the past refuses as no_response before any provider call, mirroring the exhausted-budget refusal; identify() is untouched and still calls with neither. The transport is byte-unchanged: confirmed by reading, it derives its bound, the helper's effective allowance, and its termination point from the adapter's established deadline — which is now the original activation point itself.

The witness, T22 in the A3 suite, five deterministic checks under a controlled clock: the doorway's absolute deadline reads anchor + 60 exactly, identically at every read; the loop hands the callable that exact point; the drift proof — the model wrapper advances the clock 7.0s between the loop's sampling and the adapter's invocation, and the adapter's established deadline equals the original point exactly, the transport-style bound derived at call time reading the true remaining 53.0s; a supplied deadline is used verbatim at an unrelated clock position; a past deadline refuses pre-call. The builder verified the witness bites: in a scratch copy with only the adapter reverted to ignoring the supplied deadline, exactly the three behavioural checks failed — the established point stood at original + 7.0, as you predicted — while the other 85 checks still passed.

Suites, my own runs: A3 88 ALL PASS, transport witness 55, Piece 8 36, A1 69, A2 80, A3-CAT 37, checker 35. The contract extension touched the suites' fake-model stubs (a deadline parameter, captured) — no existing assertion changed.

If this closes the seam, attempt 5 stands released on the configuration already settled: the one absolute deadline governing worker calls, identify fenced pre-activation, timing stages recorded, assignment, sources, manifest, model, grants and {12, 600} unchanged.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
