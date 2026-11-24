# SCOPE — WORKER RESPONSE EVIDENCE (2026-11-23)

Drafted by Remmy at Vane's request (INDEX 303), for her scope examination. The piece answers the gap the first probed-mode run exposed (INDEX 301): the loop recorded a parse verdict — "answer is not one JSON object" — while the answer itself was discarded at the transport seam. **Boundary (hers, standing): no rerun, no change to the selected text mode, grants, bounds or assignment. This scope authorises nothing; the build waits on her scope pass and Ben's tap.**

## §1 The seam (as located, verified against the source)

- The Groq connector transport's `connector_call` (`live-demo/groq_connector_transport.py:356`) parses the helper's serialized provider response, extracts only `choices[0].message.content`, and returns content + provider model ID. The rest of the assistant message — `tool_calls`, refusal, every other field — is discarded there.
- The adapter's built-in `_dispatch` (`src/framework/adapter.py:479`) retains the full message in `_last_message` (line 518); a replaced `_call` bypasses `_dispatch` and never populates it. The adapter then feeds the content to `_extract_json_object` (line 189, called at 676); on failure the content survives only as a local value on the exception path, and the loop receives an `AdapterFailure` diagnostic.
- The loop (`src/framework/loop.py`, `run()` at 276) records LOOP_ITERATION **before** the call — it cannot contain post-call evidence, and this scope does not pretend otherwise.

## §2 The evidence object — five layers, distinct, provenance-labelled

For **every** provider call the loop makes (success and failure paths alike), the adapter produces a response-evidence object carrying five distinct layers, each labelled with its provenance and never treated as interchangeable:

- **L1 — provider body:** the response body as received (for connector transports, the helper's serialized response text; for the built-in path, its response text). The evidence of record.
- **L2 — decoded envelope:** L1 parsed as JSON, where it parses; where it does not, L2 stands absent and says so.
- **L3 — assistant message:** the full message object from the envelope (all fields, incl. `tool_calls` / refusal), where present.
- **L4 — extracted content:** the content string the adapter worked on, where present.
- **L5 — parser verdict:** the adapter's outcome for this call (the typed outcome kind, or the failure detail verbatim).

The transports' obligation is redefined to match the built-in path's retention: a replaced `_call` delivers the full message **and** the body it arrived in. The Groq transport is the examined seam; the adapter-level contract is transport-agnostic and the NVIDIA transport conforms by the same shape, witnessed at its own stub boundary. (The probe's raw capture is untouched — it already satisfies its own contract.)

## §3 Retention — bounded, honest, durable before effects

- **Artifact:** one evidence artifact per iteration that reached a provider call, filed by the loop in the run's evidence store (`responses/iteration-<n>.json`), containing the five layers with, per layer: byte count, sha256, retained bytes/text, and a completeness flag.
- **Ceiling:** per-layer retention ceiling **64,000 bytes** (the probe's ceiling). Retention may truncate a layer's *stored text*; it never truncates silently: the layer's hash is computed over the **whole** original before any truncation, the full byte count is recorded, and completeness stands **false** whenever the stored form is partial. Nothing is decoded lossily, normalised or replaced in L1–L3.
- **Record binding:** after the call and **before any dispatch from that answer**, the loop records a **RESPONSE_EVIDENCE** event naming the iteration it answers (by the LOOP_ITERATION event's seq), the artifact's sha256, and the per-layer hashes/counts/completeness. The pre-call iteration event is unchanged.
- **Contents discipline:** response side only. No credentials (none exist on this path, and the artifact writer asserts none of the request's headers/material are included); the request and prompt are **not** duplicated — the package already stands in the record via the iteration's commitment.

## §4 Failure semantics

- **Parse failure is the primary case, not an exception:** an `AdapterFailure` carries the evidence object with it; the loop persists the artifact and records RESPONSE_EVIDENCE **before** recording the stall, so a failed answer is exactly as inspectable as a good one.
- **Evidence-capture failure is a hard stop before effects:** if the artifact cannot be written or its hash verified, the loop records an explicit stall on a new ground — **`evidence_capture_failure`** — and dispatches **nothing** from that answer, even if the answer contained a valid, grantable tool request. No answer's effects precede its evidence.
- Provider failure with no response at all (transport error before a body exists) retains today's honesty: no artifact is fabricated; the stall records the transport diagnostic, and RESPONSE_EVIDENCE stands absent for that iteration — a state the checker distinguishes from a captured one.

## §5 The checker (independent copy, as established)

- Every iteration that reached a provider call and produced a response stands bound by exactly one RESPONSE_EVIDENCE whose artifact hash matches the filed artifact and whose layer hashes/counts recompute from it.
- **No dispatch without durable evidence:** any dispatch event whose iteration lacks a preceding RESPONSE_EVIDENCE binding is a checker failure.
- An `evidence_capture_failure` stall with any dispatch from the same iteration is a checker failure.
- Completeness flags recompute: a layer marked complete whose stored length ≠ its recorded full byte count is a checker failure.

## §6 Witnesses

- **W-a (the probed1 stall, reproduced):** a stub provider answers in native shape (tool_calls, no content) to a text-mode call — the loop stalls as today, **and** the filed evidence shows the full message including the tool_calls. This witness would have turned INDEX 301's hypothesis into a reading.
- **W-b:** a malformed-content answer — evidence retains L1–L4 and the verdict; the stall's detail and the evidence agree.
- **W-c:** a body beyond the ceiling — stored truncated, completeness false, the layer hash equal to the hash of the **whole** true body.
- **W-d (durable-before-effects):** the evidence store made unwritable while the stub answers with a valid, grantable tool request — the loop records `evidence_capture_failure` and **zero dispatches** stand.
- **W-e:** a successful answer — evidence filed and bound, dispatch proceeds, the checker all-ok over the record.
- **W-f:** the built-in adapter path and the NVIDIA transport produce the same evidence shape at their stub boundaries.
- Regressions: every suite green at its known count (the loop/adapter/checker suites gain the new witnesses; nothing existing weakens).

## §7 Out of scope

No rerun of any run; no change to mode, grants, bounds, assignment or the probe; no general logging beyond the response-evidence path; no retention of requests/prompts (already in the record); no change to the stall grounds' existing meanings (one new ground added, §4).
