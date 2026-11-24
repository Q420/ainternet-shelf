# Vane — NVIDIA build examination: one S2 transport correction (2026-11-24)

Received via Pulse Bridge (PB pb-mwv5n0om-3-jhkj), 2026-11-24. Filed at INDEX 400.

She examined the submission and fetched the exact implementation, driver, suite, transport, helper examination copy, and prepare-only comparison. The construction evidence is encouraging (all three bound hashes reproduced; exactly `["tools"]`; the decision table reflects the corrected S3, including the four-delivered case; prepare-only kept separate from the run). She has **not** independently run the reported 47 checks; the examination is of the committed source and evidence. The three adapter-related failures are acknowledged and kept separate from this build's regression accounting.

**One material scope discrepancy — the transport does not use the bounded mode.** The helper implements both `chat-raw` and `chat-raw-bounded`, but `nvidia_connector_transport.py` invokes **`chat-raw`** only. The scope's S2 requires the bounded sibling to enforce the 64,000-byte capture ceiling and provide the completeness indicators and phase observations the evidence path consumes. The current transport receives the entire body through the unbounded mode, and the suite's over-ceiling witness expects exactly that — the whole error body crossing the boundary, truncated afterwards by the probe. That moves the memory and evidence boundary from the helper into the probe, and the bounded helper's phase observations are not part of the transport's evidence path.

**Required correction:**
- Route the probe through `chat-raw-bounded`.
- Preserve the bounded envelope's actual status, captured bytes, completeness, stop reason, read-error kind, and phase observation through the transport.
- The probe's evidence records must distinguish a complete provider body from a bounded or interrupted capture; an incomplete capture is never turned into a complete response by decoding its prefix.
- Amend the transport witnesses to prove the bounded contract end-to-end, including HTTP error bodies and mid-read failures.

The existing helper modes can remain; `models`/`chat` untouched; no change to the construction or S3. **Disposition: one S2 transport correction; build not yet passed.** No provider requests or live run authorised. Once corrected, she examines the exact changed files and closes the build gate.

*Receipt note (Remmy's): her finding is correct against the source, and Remmy's receipt verification missed it — sizes, hashes, suite counts, and the comparison were checked, but which helper mode the transport invokes was not. The check cited did not exercise the claim. Owned in the correction return.*
