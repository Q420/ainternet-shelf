# STAGE 6 SECOND SUBJECT — ATTEMPT 2 EVIDENCE (2026-11-17)

Run: STAGE6BATT-20261118-001, attempt 2 (collect side), Q420/Battery qwen-battery run 44217537496, dispatched 2026-11-18T01:39Z on the GPT-OSS config (sha f07204ec). Results at qwen-battery-results/STAGE6BATT-20261118-001-attempt2/.

Outcome shape: 72 record events, 3 TREE_CLOSED, RUN_CLOSED absent. Exactly 3 adapter captures (T01, T02, T03, one each).

Transport: all 3 captures TIMEOUT, failure_class ADAPTER_FAILURE, 0 tokens, no served model. T01's capture detail (representative): attempt 1 sent 01:40:10Z, attempt 2 sent 01:42:15Z — each read timed out at the adapter's 120-second limit ("TimeoutError: The read operation timed out"), authorization attached on both, no HTTP status, no response body.

Contrast: the preflight verification call against the same pin and credential (short prompt, max_tokens 64) returned HTTP 200 in seconds with usage metadata. Under battery conditions — full tree prompt, thinking enabled, reasoning budget 16384, per-instance max_tokens 10240 and above — the lane returned nothing within 120 seconds, twice per instance, three instances in a row.

Classification: UNSCORED — transport timeout. The subject produced no scorable output; this is not a subject failure and not a battery failure. Two candidate causes are not separable from this evidence alone: free-lane latency on long reasoning generations, or the 120-second adapter timeout being too short for this model class under these envelopes. A single battery-shaped diagnostic call with an extended timeout, timed end to end, distinguishes them.

No re-fire is attempted on this evidence. The question — timeout amendment, lane change, or new pin — goes to Alex with this record; the diagnostic call goes to the owner for his word.
