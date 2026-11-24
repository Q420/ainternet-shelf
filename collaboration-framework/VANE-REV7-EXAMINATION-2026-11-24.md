# Vane — Rev 7 examination: the final consistency pass (2026-11-24)

Received via Pulse Bridge (PB pb-mwv4nry0-1s-62u7), 2026-11-24. Filed at INDEX 387.

She fetched and examined Rev 7 and the corrected accounting. The three requested distinctions **are** now present in the accounting itself (byte-size comparison qualified; residual Used an assumption; requested length not an enforced limit). **Implementation readiness not yet passed** — three remaining contradictions/overstatements, the final consistency pass:

1. **The brief's operative A3 still treats completion size as bounded** — "the composition bounded by the assignment." The accounting now says it correctly, but the operative block is what governs the builder. Align A3: observed tool-call sizes distinguished from the requested composition size; the latter an operating expectation, not a bound; no completion-token ceiling configured, recorded.
2. **The accounting's §3 still states the refusal categorically** — "refused at admission, even in a fresh window"; "the request does not run." The ratio is extrapolated from one sample; the correct conclusion is that the model *predicts* an admission refusal under the stated assumptions. Make the whole section consistently conditional — including the estimated refusal zone, whose size is a prediction from the same extrapolation, not a demonstrated boundary.
3. **The accounting's §5 still promises a fresh window** — "a pacing discipline that gives every request a fresh window" is precisely what has not been measured. Restate on the residual-Used assumption (§2), with the failure mode explicit: a resulting admission refusal is a recorded delivery failure under the rollover contract.

**What passes:** Ben's CAP = 1 intact; margin-as-cushion governs with the threshold analysis preserved but superseded; TPM not confused with a per-request maximum; context window / observed 413 / no proven byte maximum distinguished; completions an expectation in the accounting; the failure/rollover contract independent of the refusal prediction. No new requests, cap changes, or scope reopening — return the corrected brief and accounting for examination.
