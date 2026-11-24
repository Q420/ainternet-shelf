# SCOPE — WORKER RESPONSE EVIDENCE (2026-11-23)

**Rev 4** — Rev 3, plus the disposition's honesty made enforceable (INDEX 307): three terminal response states (captured / confirmed no_response / unresolved) with a finite failure-class table whose required seam evidence the checker validates, HTTP-error-with-empty-body counted as captured, and the pre-call terminal steps closed to a named finite set validated against the sequence.

**Rev 3** — Rev 2, plus the no-response distinction made mechanical (INDEX 306): RESPONSE_EVIDENCE becomes the iteration's typed response disposition (captured / no_response), owed by every iteration that reaches the call; the failure path's ordering stated case by case; L1 stored as base64 with recomputable hash/count; L5 verdicts total, with explicit `not_reached` states.

**Rev 2** — revised at Vane's scope examination (INDEX 305): L1 provenance made exact (the Groq worker path moves to the raw helper mode so L1 is the provider body, not a re-serialization); the durable-store contract specified; one exact event/failure sequence, with evidence capture placed ahead of the post-call deadline stall; W-a strengthened to prove the layers' identity chain, with the five response-shape cases added.

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

---

## Rev 2 — the examination's four points, answered

### R2-1. Provenance made exact (her point 1)

The layer list is revised; no layer borrows another's name.

- **Transport capture** — exactly what crossed the transport boundary, its source and representation named (e.g. "the Groq helper's `chat-raw` envelope, base64"). This is a fact about the seam, recorded as provenance metadata, not itself a body.
- **L1 provider body** — the original HTTP response bytes, and the label is earned only where the transport genuinely captures them. **For Groq, the worker transport obtains the response through the helper's raw mode (`chat-raw`)**: L1 is the provider body bytes; the transport parses L1 itself for the envelope and message. (The ordinary `chat` path's output — parsed and re-serialized by the helper — is never labelled provider body; if any transport cannot supply the true bytes, its L1 stands labelled `transport_serialized` with the transformation named, and the checker treats the two provenance classes distinctly.) For the adapter's built-in path, L1 is the response text its own HTTP transport received. For NVIDIA, the same rule: the raw bytes where its path supplies them, the honest label where it does not.
- **L2 decoded envelope** — L1 parsed as JSON, with the decoding (strict UTF-8, per the probe boundary policy) and parsing outcomes recorded; absent, and saying why, where either fails.
- **L3 assistant message** — the complete message object from L2, all fields.
- **L4 extracted content** — the exact content value handed to the adapter's content parser (or its recorded absence).
- **L5 verdicts, two and distinguished** — (a) the **adapter verdict**: the extraction/parser result, recording the hash of the exact content it consumed; (b) the **loop validation verdict**: the loop's subsequent response validation (catalogue/grant-shape checks) where it runs. Neither stands in for the other.
- **Hash representations defined:** L1 hashes over the raw bytes. For derived JSON layers (L2, L3), the hash is over the framework's canonical JSON serialization (`fabric.canonical`) of the parsed object — a defined representation of a derived object, never implied to be the original bytes. L4 hashes over its exact string bytes (UTF-8).

### R2-2. The durable store, as a contract (her point 2)

- **Location and binding:** artifacts live in `<run-dir>/responses/`. The filename is derived, never chosen: `iteration-<seq>.json`, where `<seq>` is the seq of the LOOP_ITERATION event the artifact answers — binding run (the directory), assembly and instance (named inside the artifact, validated against the record), and iteration (the filename + the artifact's own `iteration_seq` field) by construction.
- **Collision and substitution:** the store refuses to overwrite — if `iteration-<seq>.json` already exists, the write is an evidence-capture failure, not a replacement. The artifact's internal fields (run, assembly, instance, iteration seq) must agree with the filename and the record, and the checker validates that agreement, so a substituted file fails on content even if its name is right.
- **What "durable" means here:** write to a temporary name in the same directory → flush and fsync → rename into place → **read the artifact back and verify its sha256 against the computed hash**. Only a read-back-verified artifact counts as persisted. A write call merely returning is not durability and the scope never calls it that.
- **The checker** locates artifacts from the run directory (the same run-directory basis its replay already works from), reads `responses/iteration-<seq>.json` for each bound iteration, and recomputes every hash from the file it actually read.
- **Artifact written, event uncommittable:** the artifact may stand as an **orphan** — an incomplete recordkeeping outcome the checker reports as such. It licenses nothing: without the committed RESPONSE_EVIDENCE event, the loop stops (evidence-capture failure at the commit step) and no dispatch follows. **Dispatch without a committed evidence event is the forbidden case, in all orderings.**

### R2-3. One exact sequence (her point 3 + the deadline point)

For every iteration, in this order, on success and failure alike:

1. LOOP_ITERATION is recorded (pre-call, unchanged).
2. The provider call returns — or raises, carrying whatever response evidence actually exists.
3. The adapter completes its interpretation (extraction, parsing, verdicts) **without causing effects**.
4. **The response artifact is persisted and read-back-verified** — this step stands **ahead of the post-call deadline check**: a response that arrives after the activation deadline is captured and bound first, and only then does the deadline stall proceed, with the evidence attached. No answer escapes capture at the deadline boundary.
5. RESPONSE_EVIDENCE is committed — a **loop-owned** event with its own doorway route and validation (payload: the iteration seq it answers, the artifact hash, the per-layer hashes/counts/completeness, the L1 provenance class), the doorway checking that the named iteration stands and that no dispatch for it precedes this event.
6. Only then may the loop validate for dispatch and dispatch.

Distinctions preserved in the sequence: an **HTTP error with a body is a response** — the raw path returns status + body, so evidence is captured (L1 = the error body; the verdicts record the HTTP failure) and the stall follows with evidence attached. A **transport failure before any response exists** produces no artifact and no RESPONSE_EVIDENCE; the stall records the transport diagnostic. The checker keeps the two states distinct: *no response* (no evidence event, legitimately) versus *response without evidence* (a checker failure, always).

### R2-4. W-a proves the identity chain (her point 4)

W-a is strengthened: the stub answers in text mode with a native-shaped response; the witness asserts not merely that a tool_calls-bearing object was saved, but the **identity chain** — L3 is the message inside L2 inside L1 (each layer's hash recomputed from the layer above), **L4 is L3's content value (or its recorded absence), and the adapter verdict in L5 records the hash of the exact content it consumed, equal to L4's hash**. The saved message is thereby proven to be the very message the verdict arose from. The response-shape cases are added as witnesses:

- **W-g:** content absent, native tool_calls present (the probed1 shape).
- **W-h:** content **and** tool_calls together.
- **W-i:** a malformed / undecodable provider envelope (L2 absent with its reason; L1 intact).
- **W-j:** an HTTP error **with** a response body (evidence captured; verdicts record the HTTP failure).
- **W-k:** a transport failure with **no** response body (no artifact; the stall's diagnostic stands alone; the checker accepts the absence as the no-response state).

All other Rev 1 provisions stand as written (the five-layer object as amended by R2-1, the ceiling and whole-original hashes, the `evidence_capture_failure` ground, the contents discipline, the checker rules as extended by R2-2/R2-3, and the §7 boundary).

---

## Rev 3 — the no-response distinction, made mechanical

### R3-1. Every iteration reaches a recorded terminal response state (her point 1, her favoured design)

RESPONSE_EVIDENCE gains a typed outcome, and the event becomes the iteration's **response disposition** — recorded in both of its forms at the same sequence position (Rev 2 §R2-3 steps 4–5):

- **`outcome: "captured"`** — a response exists. The artifact-bearing form of Rev 2, unchanged: artifact persisted and read-back-verified first, then the event commits, bound to the iteration and the artifact hash.
- **`outcome: "no_response"`** — the call was invoked and the transport observed no response. **No artifact** (nothing exists to file, and none is fabricated). The event carries, from the transport seam's own observation at call time: the **transport failure class** (a typed value — e.g. `helper_exit`, `no_envelope`, `timeout_or_unresolved_termination`, `provider_http_error_without_body` where the seam can establish that) and the diagnostic text. This is a positive recorded claim made at the seam when the call returns, not an inference drawn later from an absence.

**The universality rule (doorway + checker):** the loop's sequence invokes the provider call at a named step. Every iteration that passes that step owes exactly one RESPONSE_EVIDENCE — in one of its two forms — committed before the iteration's terminal event (its stall, yield or continuation). Iterations that terminate **before** the call step do so only at named pre-call steps whose terminal payloads identify the step (package construction, deadline-at-start); those are the only iterations without a disposition, and they are distinguishable by their recorded step, never by silence. The checker enforces: a post-call terminal (provider failure, deadline-after-call, parse stall, `evidence_capture_failure`, any dispatch, a yield) with **no** preceding RESPONSE_EVIDENCE for its iteration is a failure; **two** dispositions for one iteration is a failure; a `no_response` disposition followed by any dispatch from that iteration is a failure. A missing state is therefore mechanically a defect, exactly as required.

### R3-2. The failure path's ordering, explicit (her point 2)

The Rev 2 ordering binds failures with the same force as successes, stated case by case:

- **HTTP error with a body:** the raw seam returns status + body — that is a response. Captured (L1 = the error body) and bound **before** any deadline stall; the verdicts record the HTTP failure (R3-3).
- **Malformed / undecodable envelope:** L1 is retained whole **before** the parsing failure is recorded; the failure's record points at the evidence that exhibits it.
- **Transport failure, no response:** the `no_response` disposition (R3-1) is recorded at the same sequence position a captured disposition would occupy — before the stall.
- **Evidence that cannot be persisted:** `evidence_capture_failure`, full stop — a simultaneous deadline expiry does not absorb it, outrank it, or rename it. The deadline never becomes a way for an answer to escape the evidence contract, on any path.

### R3-3. The two precision points (her point 3)

- **L1 storage representation:** the artifact stores L1 as **base64 of the raw bytes**, alongside the byte count and the sha256 of the raw bytes — both independently recomputable from the stored representation by the checker or any reader. Arbitrary binary and invalid-UTF-8 bodies are therefore retainable exactly; the strict-UTF-8 decode remains a *derived-layer* act (L2), whose failure is recorded, never a storage constraint.
- **L5 verdict states are total:** both verdict fields are **always present** in the evidence object, each taking a typed value. The adapter verdict is `not_reached` when parsing cannot begin (no envelope, transport HTTP failure, undecodable body) — with the reason named — rather than absent. The loop validation verdict is `not_reached` whenever the adapter stage produced no dispatchable outcome to validate. A missing verdict field is a malformed evidence object (checker failure), never a synonym for incomplete evidence.

---

## Rev 4 — the disposition must not overclaim

### R4-1. Three terminal response states, each saying only what the seam established

The disposition's outcome is one of exactly three values:

- **`captured`** — a response was received. This includes **every HTTP status, errors included, and an empty body**: an HTTP error with no body is a captured response whose L1 is the empty byte sequence (count 0, the empty hash), its status recorded, its verdicts recording the HTTP failure. A status observed at the seam can never be disposed as anything else.
- **`no_response`** — **confirmed**: the seam's evidence positively establishes that no provider response was **received** (receipt-side fact; whether the provider processed anything is not claimed). Permitted only with a supporting failure class from R4-2 whose required evidence stands in the disposition.
- **`unresolved`** — the seam cannot establish whether a response was received. This is a first-class, honest terminal state, not a loophole: the iteration is accounted for (the disposition exists, with its class and evidence), **no dispatch may follow it**, and the iteration terminates with the unresolved state named in its stall. A run ending on an unresolved disposition is complete as a record and failed as work — the same standing as a provider failure, with its own name.

`no_envelope` is an **unresolved** class (the helper framed nothing; what happened provider-side is not established). Rev 3's `provider_http_error_without_body` example is withdrawn — that is a captured response.

### R4-2. The failure vocabulary — permitted classes, required evidence, checker enforcement

Each non-captured disposition names one class from this finite table; each class names the seam evidence the disposition must carry. **A diagnostic string is never, by itself, a basis** — the class and its evidence fields are mandatory typed fields, and the checker rejects a disposition whose class does not support its outcome or whose required evidence is absent.

| Class | Outcome it supports | Required seam evidence in the disposition |
|---|---|---|
| `connection_failed` | `no_response` | the helper's transport-error report: its error kind (connection-level, e.g. URLError reason class) and the absence of any observed HTTP status |
| `timeout_no_response` | `no_response` | the call fence that expired, the transport's termination record (terminated **and confirmed dead**), and zero stdout bytes received from the helper |
| `helper_exit_no_envelope` | `unresolved` | the helper's exit status and its stderr diagnostic (the helper died or errored without framing a response; provider-side state unestablished) |
| `envelope_unparseable` | `unresolved` | the helper produced output that is not a well-formed envelope (byte count + hash of what was produced) |
| `termination_unconfirmed` | `unresolved` | the transport could not confirm the helper's termination (the INDEX 232/262 unresolved-termination state) |
| `transport_internal_error` | `unresolved` | the transport's own failure class before any seam observation could be made |

The checker validates the pairing mechanically: outcome `no_response` with a class outside the supporting set, or with its evidence fields missing, is a failure; outcome `unresolved` with a `no_response`-supporting class is a failure (the stronger claim was available and not taken — the record must not underclaim either); outcome `captured` with no artifact is a failure (as Rev 2/3 already required).

### R4-3. The pre-call terminal steps — a finite named set, validated

An iteration may terminate without a disposition only at one of these steps, and its terminal payload must carry `terminal_step` naming it:

- **`package_construction`** — the iteration's package could not be constructed/committed.
- **`deadline_at_start`** — the activation deadline stood already expired when the iteration began its call step.

The set is closed: the doorway admits no other `terminal_step` value on a disposition-less terminal, and the checker validates the claim against the sequence — the terminal must be the iteration's first and only terminal event, no RESPONSE_EVIDENCE and no dispatch may exist for that iteration, and (for `deadline_at_start`) the recorded deadline and timestamps must be consistent with expiry at the start. A post-call failure relabelled as pre-call fails these checks mechanically: its sequence shows the call step was passed (a disposition is owed), or its step value is outside the set.
