# BUILD SCOPE — THE NVIDIA-ROUTE NATIVE-OFFER PROBE (2026-11-24)

Submitted to the examiner 2026-11-24 (INDEX 395), under her passage of the
proposal (INDEX 394). This scope governs a BUILD only. The live run keeps its
own release gate; this scope authorises no provider request.

## S1. Construction identity (her point 1)

The experimental construction is the admitted Groq native-offer construction,
unchanged in every byte. Bound in full:

- Baseline request SHA-256:
  `72f6297ddc883354ee766c4a62d2a866dc7bd7a65f3f6a4fff9f5a4885bae8ab`
- Modified request SHA-256:
  `0229b0f0055cf44ae3dda462c4436188b93bcd204363e386f0cf3a9979c7e6ae`
- Tool-definitions span SHA-256:
  `6f3331ac1a62da2e4cfd31e66ed08d3b4cd540806f2f94f87fc72918e61abfe4`
- The two requests differ at exactly one path: `["tools"]`.

The build reproduces the construction through the same real construction path
the Groq probe used, and its prepare-only comparison must reproduce all three
hashes byte-exact before anything else proceeds; a mismatch stops the build
and is reported, never repaired by editing the construction. The model field
is part of the bound construction: the build verifies the NVIDIA catalogue
serves the identical model identifier the construction names. If it does not,
that is a flagged conflict returned to the examiner — never a substitution.

## S2. Transport parity (her point 2)

Current state, verified by reading the helper this round:
`custom.nvidia/bin/nvidia_api.py` offers exactly two modes — `models` and
`chat`. It has **no raw capture and no bounded capture**; the Groq helper's
evidence modes (`chat-raw`, `chat-raw-bounded`) have no NVIDIA counterpart.
Parity is therefore real build work, bounded as follows:

- Add to the NVIDIA route a bounded raw capture mirroring the Groq helper's
  settled contract: exact response bytes returned as `{"status", "body_b64"}`;
  a bounded sibling enforcing the 64,000-byte capture ceiling with the same
  completeness indicators (body_complete, stop_reason, read_error_kind) and
  phase observations the evidence piece consumes.
- Changes are bounded strictly to the probe's evidence contract. Nothing else
  in the helper changes; the existing `chat` and `models` modes are untouched.
- Diagnostic output (stderr, exit codes, helper prose) is transport
  diagnostics, never raw provider evidence; the evidence layers keep the
  response-evidence piece's separation.
- Parity witnesses run against scripted bodies before any live use: the raw
  mode returns byte-exact bodies; the bounded mode's ceiling behaviour matches
  the Groq contract at, below, and past the ceiling; an HTTP error with a body
  is captured, a transport failure without one stands unresolved — the same
  witness shapes the Groq side passed.

## S3. Decision accounting (her point 3)

The Groq classification is carried forward exactly: each trial's first
response is classified under the settled taxonomy (offered_tool_call,
unoffered_tool_attempt, malformed, content_only, hybrid) crossed with the
delivery disposition (provider_accepted / provider_refused / provider_failed).
The decision rules are fixed here, before any result exists:

- A trial is **delivered** when the provider accepts the request and returns a
  first response. Provider failures (rate limits, 5xx, transport failures)
  are **delivery failures — never observations, and failed trials are never
  replaced**.
- Every report states the denominator beside the reading: delivered of five.
- **route_carries_q1**: at least 3 delivered, at least 3 of them
  `offered_tool_call × provider_accepted`, and zero unoffered or malformed
  classifications among the delivered.
- **insufficient_evidence**: fewer than 3 delivered — no conclusion either
  way, whatever the delivered trials show.
- **split_inconclusive**: every other delivered pattern.
- No reading stronger than this table may be drawn from the run, at any
  denominator.

## S4. Pacing (her point 4)

At least 65 seconds between actual request starts, measured on a monotonic
clock at the call boundary — the paced runner's settled discipline, carried
unchanged. Any relaxation belongs to a later examination based on NVIDIA's
own evidence; this scope does not relax it.

## S5. No execution (her point 5)

First response only. Evidence is durable before interpretation. No dispatch,
no execution, no follow-up request, no retry. The offered definitions are an
interface, never grants. `disable_tool_validation` is absent — the request
carries the provider default, exactly as the proposal settled.

## S6. Shape of the build and its gates

- The probe reuses the paced runner core the P1/P2 builds settled (shared
  pacing, taxonomy, evidence writing), with the transport swapped to the
  NVIDIA route and the construction bound per S1. One probe driver, one suite.
- Exactly five generation requests at the run, when the run is separately
  released. The build itself makes none.
- Gates, each separate: this scope's examination → the build → the build's
  examination → the run's release examination → the run → the results
  examination. The adapter implementation proceeds on its own authorised
  track throughout; neither line gates the other.
