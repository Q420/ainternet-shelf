# STAGE 6 SECOND SUBJECT — TIMED DIAGNOSTIC CALL (2026-11-17)

Authorised by the owner's tap, 2026-11-17 20:51 MST ("Run the one timed test call"). One call, separately identified, not a scored instance.

Shape: the battery's own envelope — model openai/gpt-oss-20b, temperature 0.6, top_p 0.95, stream false, max_tokens 10240 (T01's ceiling), chat_template_kwargs {enable_thinking: true, reasoning_budget: 16384} — sent through the owner's NVIDIA connector credential path with the read timeout extended to 600 seconds. The prompt was a proxy governance problem (461 prompt tokens), not scored calibration material.

Result: HTTP 200 in 95.4 seconds. Served model: openai/gpt-oss-20b. finish_reason: stop. Usage: prompt 461, completion 1,694 (of which reasoning_tokens 1,034), total 2,155. The response was complete and well-formed (2,981 characters).

Reading: the lane does serve this subject under battery conditions — generation simply runs long. A 461-token prompt consumed 95.4 seconds, close to the adapter's 120-second limit; the battery's real tree prompts are substantially larger, so attempt 2's uniform 120-second timeouts are explained without positing a lane refusal. The binding constraint is the adapter's per-attempt timeout (120 s), with the run watchdog (3,600 s) and the workflow job timeout (120 min) as companions if per-call times grow.

Question carried to Alex: rule on a timeout amendment (adapter per-attempt timeout, watchdog, job timeout) as a pinned change with (c2) re-verification, versus a lane change or a new pin.
