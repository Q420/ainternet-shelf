# LLM Agent Timeout & Deadline Patterns — Research Report

## Summary

Established practice is **not** a stack of independent guessed per-call timeouts. It is a layered budget:

1. **One end-to-end deadline set at the edge / run start, propagated as remaining time** (gRPC/Google SRE, DBOS child workflows, Vercel/Mastra `totalMs`).
2. **Per-attempt caps inside that budget** to detect a crashed/hung worker (Temporal Start-To-Close, LangGraph `run_timeout`, OpenAI Agents `ModelSettings.timeout`).
3. **A progress / idle / heartbeat timeout, separate from total duration**, to distinguish *alive-but-long* from *hung* (Temporal Heartbeat, Step Functions `HeartbeatSeconds`, LangGraph `idle_timeout`, Vercel `chunkMs`/`firstChunkMs`, MCP `resetTimeoutOnProgress` + `maxTotalTimeout`).
4. **Cooperative cancellation** almost everywhere — the framework signals, the work must check a context / `AbortSignal` / heartbeat response; non-cooperating work is orphaned, not killed. Durable engines record the timeout/cancellation in history.
5. **Stage-level timing as a span/metric, not just a total**: OpenTelemetry GenAI (Development status) standardises `gen_ai.client.operation.duration`, `gen_ai.client.operation.time_to_first_chunk`, `gen_ai.server.time_to_first_token`, `gen_ai.server.time_per_output_token`, plus `gen_ai.usage.input_tokens` / `output_tokens`. Set timeouts from those measured distributions (p99 + headroom, capped by remaining budget), not guesses.
6. **Stream LLM calls.** Non-streaming calls sit silent for minutes and are killed by intermediaries (proxy/ALB/Cloudflare ~60–125s idle/read limits) long before the 600s SDK default. Anthropic's SDKs actively refuse non-streaming calls expected to exceed ~10 minutes.

No framework surveyed implements *pure* "single run-level deadline, per-call durations merely observed" as its only model — the closest are DBOS (durable workflow deadline inherited by children) and Vercel AI SDK 7 / Mastra (`totalMs` hard run deadline *plus* step/chunk/tool sub-budgets). OpenAI Agents SDK explicitly does the opposite: its model timeout "does not … bound the full run".

Confidence: high for gRPC, Temporal, Step Functions, LangGraph, Vercel, DBOS, Anthropic/OpenAI SDK defaults (primary docs opened/verified); medium for CrewAI/AutoGen/MCP-client specifics (official API refs + documented issues/guides, fewer primary timeout pages).

## Findings

### 1. Deadline propagation (gRPC / distributed systems)

**Model — deadline, not timeout.**
- gRPC: "A deadline is used to specify a point in time past which a client is unwilling to wait for a response." A timeout is a duration; a deadline is that point in time. By default gRPC sets **no** deadline — a client can wait "effectively forever" — so "always explicitly set a realistic deadline", ideally an educated guess "validated by some load testing". Past the deadline the client fails with `DEADLINE_EXCEEDED`; the server automatically cancels with `CANCELLED`, but "the server application is responsible for stopping any activity it has spawned" — it must periodically check cancellation. Source (verified open, 2026-11-23): https://grpc.p2hp.com/docs/guides/deadlines/index.html
- Propagation: when a server itself calls downstream, it should honour the original client's deadline. Automatic propagation is default in Java and Go, opt-in in C++. To avoid clock skew, gRPC does **not** send the absolute timestamp: it "converts the deadline to a timeout from which the already elapsed time is already deducted" — i.e. the wire value (`grpc-timeout` header) is *remaining* time, and the receiver re-anchors it on its own clock. Same source.
- .NET corroboration: propagate `ServerCallContext.Deadline` to child calls, or `EnableCallContextPropagation()`; if several deadlines exist, the smallest wins; a deadline also spans all retries of a call. Source (index): https://learn.microsoft.com/en-us/aspnet/core/grpc/deadlines-cancellation?view=aspnetcore-3.0

**Google SRE canonical example (Ch. 22, Addressing Cascading Failures).**
- "Rather than inventing a deadline when sending RPCs to backends, servers should employ deadline propagation." Server A picks 30s, spends 7s, so B gets 23s; B spends 4s, so C gets 19s — "the tree of RPCs emanating from an initial request will all have the same absolute deadline."
- Without it: A→B with 10s, B waits 8s then invents a fresh 20s for C instead of the 2s actually left; C dequeues it 5s later "thinking it has 15 seconds to spare" — nobody is waiting. SRE's phrase: "you don't get credit for late assignments with RPCs."
- Also: cancellation propagation — when a result is no longer needed, cancel sibling/transitive fan-out; retry amplification is multiplicative (3 retries at each of backend/frontend/JS layers = 4³ = 64 attempts on the database), so use per-request (≤3) and per-client (~10% ratio) retry budgets, randomized exponential backoff.
Sources (index, quoting SRE Ch.22): https://sre.google/sre-book/addressing-cascading-failures/ and summary at https://github.com/curiositech/windags-skills/blob/HEAD/skills/circuit-breakers-and-retries/SKILL.md

**Documented failure modes of stacking independent per-call timeouts:**
1. **Total exceeds user budget:** fixed 5s × 4 hops = 20s long after the caller gave up.
2. **Wasted / doomed work:** downstream keeps holding threads, connections, locks producing a result that will be discarded; under overload this consumes the capacity needed to recover — cascading failure via positive feedback. SRE worked example: 5% of requests hanging to a 100s deadline can turn into ~80% frontend error rate through thread exhaustion.
3. **Retry multiplication past the deadline** (above).
4. **No-deadline hang:** a stalled peer holds a connection/goroutine/thread indefinitely.
Sources (index): https://blog.oneenv.io/articles/microservice-timeout-budget-deadline-propagation-across-calls ; https://blog.oneenv.io/articles/grpc-deadlines-error-handling-status-codes-and-propagation

### 2. Durable execution / workflow engines

#### Temporal — four distinct activity timeouts (primary docs, verified open)
Source: https://docs.temporal.io/encyclopedia/detecting-activity-failures ; also https://temporal.io/blog/activity-timeouts

| Timeout | Measures | Default / rule |
|---|---|---|
| Schedule-To-Start | Scheduled (queued in Task Queue) → worker picks it up. Per Activity *Task* (per attempt). Detects worker fleet down / cannot keep up. | ∞. Non-retryable by design (retry would requeue in same queue). Docs prefer monitoring `temporal_activity_schedule_to_start_latency` over setting it. |
| Start-To-Close | Single attempt: start → close. | No own default; if only Schedule-To-Close is set, that value is used. **At least one of Start-To-Close / Schedule-To-Close is required** — service rejects the activity otherwise. "We recommend always setting this." Main use: server cannot detect a worker crash/loss of contact, so this timer forces a retry. |
| Schedule-To-Close | First schedule → last attempt reaches Closed, **including queueing, execution and all retries**. Enforced once per Activity Execution. | ∞ if unset (but see required-one-of rule). Bounds total without changing Retry Policy max attempts. |
| Heartbeat | Max gap between heartbeats from worker to service. | 0s/unset = disabled; capped at Start-To-Close. If missed, task fails and retries per Retry Policy. |

- **What heartbeat solves that a fixed timeout cannot:** a fixed Start-To-Close must be ≥ the longest legitimate execution, so a worker that crashes 10s into a 30-minute job is not detected for 30 minutes. With a short Heartbeat Timeout (e.g. 10s) + frequent heartbeats, failure is detected in ~one heartbeat interval, while a *live* long activity keeps heartbeating indefinitely and is never killed for total duration alone. Heartbeats can carry a progress payload/checkpoint; the next retry attempt can read it and resume from it. Throttling: SDKs send at most every `min(heartbeatTimeout*0.8, maxThrottle)` (defaults 30s/60s).
- **Cancellation — cooperative, delivered via heartbeat:** "Activity Cancellations are delivered to Activities from the Temporal Service when they Heartbeat. Activities that don't Heartbeat can't receive a Cancellation." Workflow cancellation is recorded as a cancel-requested event; workflow code sees it via context/`CanceledError` and can run cleanup in a disconnected context. Activity options control waiting: `WaitForCancellation` (Go, default false) / `cancellationType` = `WAIT_CANCELLATION_COMPLETED | TRY_CANCEL | ABANDON` (Java). On timeout, an `ActivityTaskTimedOut` event is written to workflow mutable state/history, attempt count increments, timer resets if retried. Termination (vs cancellation) is forceful — no workflow code runs — and records `WorkflowExecutionTerminated`.
Sources (index): https://docs.Temporal.io/develop/go/workflows/cancellation ; https://typescript.temporal.io/api/interfaces/common.ActivityOptions ; https://scimigo.com/en/learn/temporal-durable-execution/07-cancellation-and-sagas

#### Cadence (Temporal's predecessor/fork lineage — same model)
Same four timeouts with same names/definitions; "Cadence does not impose any system limit on activity duration" — application chooses. Cancellation likewise: "the only way for an activity to learn that it was cancelled is through heart beating." Sources (index): https://cadenceworkflow.io/docs/concepts/activities/ ; https://cadenceworkflow.io/docs/go-client/execute-activity/

#### AWS Step Functions — two timeouts, execution history
Source (verified open): https://docs.aws.amazon.com/step-functions/latest/dg/state-task.html
- `TimeoutSeconds`: max time a Task/Activity can run before failing with `States.Timeout`; count starts at `TaskStarted`/`ActivityStarted` in execution event history (for activities, when `GetActivityTask` returns a token). **Activities / `.sync` / `.waitForTaskToken` have no default** — they can run until the execution's maximum duration. HTTP Tasks are capped at 60s regardless.
- `HeartbeatSeconds`: must be < `TimeoutSeconds`; default 99,999,999 (effectively off). If more than that elapses between heartbeats, the Task fails with `States.Timeout` — note Step Functions conflates heartbeat-miss and total-timeout into the same error name, unlike Temporal's distinct events. Example in docs: `TimeoutSeconds: 300, HeartbeatSeconds: 60`.
- No schedule-to-start equivalent in the Task state (queueing is inside the activity poll model).

#### DBOS — durable, propagated workflow deadline (closest to run-level-only)
Sources (index): https://docs.dbos.dev/python/tutorials/workflow-tutorial ; https://docs.dbos.dev/golang/tutorials/workflow-tutorial
- `SetWorkflowTimeout` / `WithTimeout` / `timeoutMS`: **start-to-completion** (queue wait does not consume it), **durable** — stored in the database, persists across restarts, so very long timeouts work.
- On expiry the workflow **and all its children are cancelled**, status becomes `CANCELLED`. Cancellation preempts at the beginning of the next step by default; a step must be marked `preemptible` (Python) or observe `ctx.Done()` / `stepStatus.cancelSignal` to stop mid-step — again cooperative.
- **Propagation is explicit in the model:** "A child workflow started under its parent's context inherits the parent's deadline, even when it is enqueued" (Go); in Java a child without its own timeout inherits the parent's deadline so it "can't outlive its parent", and can be detached only by giving it its own timeout or `Timeout.none()`.

### 3. LLM agent frameworks

| Framework | Model-call timeout | Run / graph-level | Idle / progress variant | Default / notes |
|---|---|---|---|---|
| **LangGraph (Python, v1.2 fault tolerance)** | Per-node attempt via model's own client timeout (below) plus node `timeout=` | No single graph deadline in the docs surveyed; defaults are per-node via `set_node_defaults` (not inherited by subgraphs) | **Yes — two clocks** | See detail below |
| **LangChain model layer** | `ChatOpenAI(timeout= / request_timeout=, max_retries=2 in reference example)` — per request, passed to OpenAI SDK/httpx | n/a | No | Underlying OpenAI SDK default is 600s (see §5); guides warn not to leave it for interactive services |
| **OpenAI Agents SDK** | `ModelSettings.timeout` (Py, seconds) / `timeoutMs` (JS): "Maximum duration for each model-call attempt… enforced cooperatively through normal asyncio cancellation… does not replace provider-specific phase timeout configuration or bound the full run, tool calls, or retry backoff" | **No time-based run deadline.** Run is bounded by turns: `max_turns` default **10** → `MaxTurnsExceeded`. A run-level AbortSignal cancels the whole run (JS docs) | No idle/chunk timeout of its own | Default model timeout = **none**. `@function_tool(timeout=…)` per tool, default none; default `timeout_behavior="error_as_result"` returns a timeout string to the model instead of failing the run, `"raise_exception"` raises `ToolTimeoutError` |
| **Vercel AI SDK 7** | Inside `stepMs` / provider call | **`totalMs` — whole `generateText`/`streamText`/agent call, all steps** | **Yes, richest set** | No defaults stated in release docs — all opt-in. See detail below |
| **Mastra** | `stepMs`: single model call incl. consuming its stream | **`totalMs`: "maximum duration of the entire agent run across every loop iteration, tool call and retry" — a hard deadline; on `totalMs` it does NOT try fallback models, on `stepMs` it advances to next fallback model** | `firstChunkMs` (streaming) + presumably chunk handling | Fails with `MastraTimeoutError`. Also exposes caller `abortSignal`; `Run.cancel()` triggers AbortSignal, prevents subsequent steps, but a step that doesn't check the signal "runs to completion" |
| **CrewAI** | `LLM(timeout=60 in examples)` — enforced by LiteLLM at HTTP level | `Agent(max_execution_time=…)` seconds per task; `max_iter` default 20–25 (sources disagree by version), `max_rpm`, `max_retry_limit` default 2 | No | **Documented failure:** `max_execution_time` uses `ThreadPoolExecutor` + `future.cancel()`, which only works if the task hasn't started; a hung in-flight LLM call is not cancelled, leaving orphaned threads (issues #4135, #2503). Fix recommended: set the real network timeout on `LLM`, use `max_execution_time` only as secondary guard |
| **AutoGen (Microsoft)** | `OpenAIChatCompletionClient(timeout=float seconds, max_retries=…)` — passed to underlying client | No run-time timeout found; runs end via termination conditions / `CancellationToken` passed to `run`/`run_stream`/`on_messages` | No | Cancellation is a first-class `autogen_core.CancellationToken` threaded through calls. Documented issue #6202: MCP tools via AutoGen timed out at **5s** (runtime request timeout) for a 20–30s image tool while the same function as a native FunctionTool waited fine — a hidden layer's timeout, not the tool's |
| **MCP clients (TS/Python SDKs)** | Per-request timeout | `maxTotalTimeout` caps total even with progress resets | **Progress resets timer** if `resetTimeoutOnProgress: true` **and** an `onprogress` handler is set — both required, off by default | **TS SDK `DEFAULT_REQUEST_TIMEOUT_MSEC = 60000`**, error `-32001 Request timed out`, client sends `notifications/cancelled`. Python client: no default in one tested version / 60s in others (sources disagree — version-dependent). Spec: implementations *should* set a timeout on every request, on expiry send cancellation and stop waiting; receiver *should* stop but may ignore if unknown/finished/uncancellable |

**LangGraph detail** (verified open): https://docs.langchain.com/oss/python/langgraph/fault-tolerance
- `timeout=` on `add_node` (seconds / `timedelta` / `TimeoutPolicy`), also settable graph-wide with `set_node_defaults` and overridden per-dispatch on `Send`.
- `run_timeout`: "a hard wall-clock cap on a single attempt. It is never refreshed, regardless of node activity." On firing: `NodeTimeoutError` (with `node`, `elapsed`, `kind: "idle"|"run"`, configured values), writes from the attempt are cleared, retry policy decides.
- `idle_timeout`: progress-resetting — resets on state writes, stream output, child-task scheduling, stream-writer calls, and any LangChain callback (LLM tokens, tool calls, chain start/end). `refresh_on="heartbeat"` narrows it to explicit `runtime.heartbeat()` calls only — a direct analogue of Temporal heartbeating for work with no natural progress signals. Whichever of run/idle fires first cancels the attempt. Timeout clock resets per retry attempt, so `run_timeout=30` × `max_attempts=3` = up to 90s total for the node — stacking is explicit, not hidden.

**Vercel AI SDK 7 detail** (index): https://vercel.com/blog/ai-sdk-7 ; https://vercel.com/changelog/ai-sdk-7
- `timeout: { totalMs, stepMs, chunkMs, toolMs, tools: { <name>Ms } }` on `generateText`/`streamText`/`ToolLoopAgent`/`WorkflowAgent`. `stepMs` covers one step incl. model generation, retries and local tool execution, and starts a fresh budget per step; `chunkMs` aborts if no chunk arrives for that long (does not cover wait for first chunk — `firstChunkMs` in later/.NET docs); `toolMs` cancels only that tool via its CancellationToken and ends it as a tool error the model can react to.
- Timeout aborts use `TimeoutError` as the AbortSignal reason and propagate through stream/UI protocols; model/tools "must observe the token to stop early", and a later fix ensures a timeout "ends a model step even when the provider stream ignores the abort signal".
- Pre-v7 hang postmortem pattern: a `streamText` call with no `chunkMs`/`stepMs`/`totalMs` stalled **2h10m** when the upstream connection stayed open but sent no data — exactly the failure `chunkMs` exists for. Source: https://github.com/link-assistant/agent/blob/HEAD/docs/case-studies/issue-146/README.md

**"Single run-level deadline, per-call merely observed?"** — No surveyed framework does exactly that. DBOS comes closest (one durable deadline, children inherit, steps are checkpointed/observed in the DB). Vercel/Mastra implement run-level `totalMs` as a hard cap *in addition to* enforced step/chunk/tool caps. OpenAI Agents explicitly separates them and provides no run time cap. LangGraph enforces per-attempt, not per-run. In practice the consensus is run-level **plus** per-attempt **plus** idle — each catches a failure the others cannot (see Synthesis).

Sources for this section (index unless noted): https://openai.github.io/openai-agents-python/ref/model_settings/ ; https://openai.github.io/openai-agents-js/openai/agents/type-aliases/modelsettings/ ; https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI ; https://mastra.ai/reference/streaming/agents/stream ; https://mastra.ai/reference/workflows/run-methods/cancel ; https://microsoft.github.io/autogen/0.5.3//reference/python/autogen_ext.models.openai.html ; https://github.com/microsoft/autogen/issues/6202 ; https://markaicode.com/errors/crewai-docker-deployment-failed-fix/ ; https://www.bigiron.cc/guides/mcp-tool-calls-timing-out-at-60-seconds-the-job-id-pattern ; https://lsquarem.com/docs/learn/troubleshooting/mcp-request-timed-out

### 4. Observability — where did the time go?

**OpenTelemetry GenAI semantic conventions — they exist, status = Development (not Stable).**
- Moved in 2026 from the main semconv repo to `open-telemetry/semantic-conventions-genai`; names can still change — "build on the shape, not the spelling."
- **Spans:** one CLIENT span per model call named `{gen_ai.operation.name} {gen_ai.request.model}` (e.g. `chat gpt-4o`); operation vocabulary also includes `execute_tool`, `invoke_agent`, `invoke_workflow`, `create_agent`, `plan`, `retrieval`, `embeddings`. Attributes: `gen_ai.provider.name` (formerly `gen_ai.system`), `gen_ai.request.model` / `gen_ai.response.model`, temperature/top_p/max_tokens, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` (plus cache-read tokens), and on streaming spans `gen_ai.response.time_to_first_chunk`.
- **Metrics (histograms, seconds):** `gen_ai.client.operation.duration` (total, required, buckets 0.01–81.92s), `gen_ai.client.operation.time_to_first_chunk` (streaming), `gen_ai.client.token.usage`; server-side `gen_ai.server.time_to_first_token`, `gen_ai.server.time_per_output_token`, `gen_ai.server.request.duration`; orchestration `gen_ai.invoke_agent.duration`, `gen_ai.execute_tool.duration`, `gen_ai.workflow.duration`.
Sources (index): https://ai-infrastructure.net/genai-observability-otel/ ; https://docs.bronto.io/ai-features/llm-observability ; https://genkit.dev/docs/observability/otel-genai-semantic-conventions/

**Stage decomposition is standard practice:**
- End-to-end LLM latency is routinely decomposed as **queueing + prefill/input processing (→ TTFT) + generation**, with `E2E ≈ TTFT + (output_tokens − 1) × TPOT`. TTFT is driven by prompt length/prefill, queueing, cold starts, network; TPOT/ITL (inter-token latency) by generation. vLLM exposes the same as `vllm:time_to_first_token_seconds` etc. Source: https://clickhouse.com/resources/engineering/llm-inference-latency
- **LangSmith** (LangChain's tracer) records nested runs/traces — root run → retriever / tool / LLM child runs — each with latency, token usage and cost, and TTFT checked separately from total latency for streamed responses; dashboards chart p50/p99 latency, tokens, cost, error rate grouped by model/feature. It also accepts OTLP spans, so OTel and LangSmith views can share trace IDs. Sources (index, secondary): https://www.masterclassbuddy.com/workflows/ls-cost-latency
- **OpenAI Agents SDK / Vercel / Mastra** all emit traces/spans per model call, tool call and step (Vercel AI SDK 7 redesigned its tracing on OTel/tracing channels; timeout abort reasons flow through the stream protocol, making the *reason* a run ended observable, not just its duration).
- **Providers expose:** streaming chunks (the only way to observe TTFT/first-chunk and inter-chunk gaps client-side), and final `usage` input/output token counts (in the response / final stream chunk). They generally do **not** expose internal queueing/prefill splits to API clients — server-side TTFT metrics exist only for self-hosted inference (vLLM etc.). So client-side stage timing in practice = request→first chunk, first→last chunk, per-step/tool span durations, token counts.

**Temporal/Step Functions observability analogue:** timeout type is itself recorded — Temporal writes `ActivityTaskTimedOut` (with timeout type) / cancel-requested / terminated events to durable Event History and exposes `temporal_activity_schedule_to_start_latency`; Step Functions logs `TaskStarted`/`ActivityStarted`/heartbeat events in execution history (retained 90 days for Standard workflows). You can therefore distinguish "never picked up" vs "ran too long" vs "stopped heartbeating" after the fact — the durable-engine equivalent of a trace.

### 5. Guidance / postmortems — guessed timeouts, provider disconnects, streaming

**The layered-timeout race (the central postmortem pattern):**
- OpenAI and Anthropic Python SDKs both default to **600s total, 5s connect, 2 retries**. Almost nothing in a real path allows that long: Cloudflare proxy read ~125s (524 at ~100s of origin silence), AWS ALB idle 60s, nginx read 60s, Vercel/Cloud Run 300s. "The layer that kills it is nearly always one you did not configure", and the failure shape identifies it (SDK `APITimeoutError` = yours; branded 524 = CDN; blank 504 = other proxy). Source (index): https://continuumcode.ai/guides/llm-api-timeout-errors/
- Same pattern inside frameworks: CrewAI's ineffective `max_execution_time` (§3), AutoGen's hidden 5s MCP runtime timeout, MCP's hidden 60s client default, LangChain guides warning that the 600s SDK default / 60s httpx read default are both wrong for different uses. **Lesson: enumerate every timer in the path; the tightest wins whether you set it or not.**

**Provider-side / SDK enforcement of streaming for long calls:**
- Anthropic Python SDK docs (primary, index): "By default requests time out after 10 minutes… Avoid setting a large `max_tokens` without using streaming. Some networks might drop idle connections… The SDK raises a `ValueError` if a non-streaming request is expected to take longer than approximately 10 minutes" — estimated as `3600 × max_tokens / 128,000` (threshold ≈21,333 tokens); passing `stream=True` or an explicit timeout disables the guard. It also sets TCP keep-alive to mitigate idle drops. Source: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
- Anthropic API itself returns 504 `timeout_error` for server-side timeouts, with docs recommending the streaming Messages API for long-running requests, or the Message Batches API instead of holding a connection.
- General rule stated across sources: **stream anything that might take >~60–100s.** A proxy read/idle timeout measures the *gap between reads*, not total duration, so a streaming response that emits tokens regularly can run 10 minutes through a 60s-read-timeout proxy, while a non-streaming one cannot. Streaming helpers can still assemble the final message (`get_final_message()`), so there is no functional reason to stay non-streaming for long outputs. Sources: https://continuumcode.ai/guides/llm-api-timeout-errors/ ; https://oneaiapikey.com/resources/streaming-vs-non-streaming-responses

**Set timeouts from measured distributions, not guesses:**
- gRPC docs: start with an educated guess, validate by load testing (above).
- Deadline-budget guides: set each dependency's timeout from its observed latency distribution — "p99 plus modest headroom, capped at the remaining budget. If the dependency's p99 is already larger than its slot, raising the timeout will not help" — fix the design instead. Source: https://blog.oneenv.io/articles/microservice-timeout-budget-deadline-propagation-across-calls
- CrewAI loop guide: "Set it from historical p95 latency of the same crew, not a guess." Source: https://www.n4n.ai/blog/why-crewai-crews-get-stuck-in-infinite-loops/
- Suggested starting budgets by operation type (Continuum guide, index): classification/extraction 30s non-streaming; human-waiting chat 120s streaming; high-effort reasoning 600s streaming; agent turn 900s/turn streaming with **resume, not retry** (background mode / Batch API) for longer work.

**Long work should not hold one call open at all:**
- MCP 60s postmortems converge on the **job-ID / handle pattern**: start the job, return an ID immediately, poll for result — a 150s job completed in 4 polls with no call >45s, surviving proxies and restarts (with durable job state + idempotency key). Retrying a timed-out synchronous call restarts from zero and can never finish, and may double-execute side effects. Sources: https://www.bigiron.cc/guides/mcp-tool-calls-timing-out-at-60-seconds-the-job-id-pattern ; https://automatelab.tech/blog/ai-agents/mcp-remote-tool-60s-timeout/

## Comparison table

| System | Model | Cancellation semantics | Timing observability |
|---|---|---|---|
| gRPC / Google SRE | Propagated absolute deadline (remaining time on wire); child may tighten, never extend | Cooperative: server auto-cancels call (`CANCELLED`), app must check context and stop spawned work; cancellation propagates to fan-out | Via tracing context in metadata; `time_remaining()` readable server-side; `DEADLINE_EXCEEDED` distinct status |
| Temporal | Per-activity: Schedule-To-Start + Start-To-Close (per attempt) + Schedule-To-Close (total incl. retries) + Heartbeat (progress) | Cooperative, delivered **only via heartbeat**; `WaitForCancellation`/`cancellationType` controls whether workflow waits; termination is forceful alternative | Durable Event History records scheduled/started/timed-out/cancelled per attempt; schedule-to-start latency metric; heartbeat payload = progress checkpoint |
| Cadence | Same four timeouts as Temporal; no system limit on duration | Cooperative via heartbeat only | Event history (same lineage) |
| AWS Step Functions | Per-Task `TimeoutSeconds` (total, no default for activities) + `HeartbeatSeconds` (progress) | Service marks task failed `States.Timeout` on either timer; worker learns via heartbeat response / token | Execution event history (`TaskStarted`, `ActivityStarted`, heartbeats) |
| DBOS | **Durable run-level deadline**, start-to-completion; children inherit parent's deadline unless detached | Cooperative: preempts at next step; `preemptible`/`ctx.Done()` for mid-step; status `CANCELLED` persisted | Workflow/step status persisted in DB |
| LangGraph | Per-node attempt: `run_timeout` (hard) + `idle_timeout` (progress-resetting / heartbeat) ; no graph deadline found | Attempt cancelled when either fires; writes discarded; `NodeTimeoutError{kind, elapsed}` retryable | LangSmith traces per node/LLM/tool run with latency, tokens, TTFT |
| OpenAI Agents SDK | Per-model-attempt `timeout` (none default, cooperative asyncio) + per-tool `timeout`; run bounded by `max_turns=10`, **not time** | Model timeout cancels that attempt only; run AbortSignal cancels whole run; tool timeout default returns error-as-result to model | Built-in tracing spans per model/tool call |
| Vercel AI SDK 7 | Layered: `totalMs` (run) + `stepMs` (per step, fresh budget) + `firstChunkMs`/`chunkMs` (idle) + `toolMs`/per-tool | AbortSignal with `TimeoutError` reason, propagates through streams; tool timeout cancels only that tool → tool error | OTel-based tracing; abort reason observable in stream/UI protocol |
| Mastra | `totalMs` (hard run deadline, no fallback after) + `stepMs` (per model call, fallback advances) + `firstChunkMs` | Caller `abortSignal`; `Run.cancel()` signals steps, non-checking steps run to completion | Agent/workflow traces via its observability layer |
| CrewAI | LiteLLM per-call `timeout` (effective) + agent `max_execution_time` (ineffective in-flight) | Thread-pool `future.cancel()` — fails once running; orphaned threads documented | Event listeners / OTel in production tooling |
| AutoGen | Model-client per-request `timeout`; no run time cap | Explicit `CancellationToken` threaded through run/model/tool calls | Model-client usage / events |
| MCP clients | Per-request 60s (TS default) + optional `maxTotalTimeout`; progress optionally resets per-request timer | Client sends `notifications/cancelled`; server *should* stop, may ignore; timed-out server work may already have completed — retry can double-execute | Progress notifications are the progress signal; no standard span model in spec surveyed |

## Synthesis — which patterns are considered best practice, and why

1. **Set one deadline at the run/edge and propagate remaining time, never a fresh timeout per hop.** This is the single most consensus item (SRE, gRPC, DBOS inheritance, Vercel/Mastra `totalMs`). It guarantees the whole loop cannot outlive the caller's patience and that doomed work stops instead of consuming recovery capacity.
2. **Layer three different timers — they detect three different failures:**
   - *Total / schedule-to-close* — "this run as a whole has spent its budget" (also caps retries: retries must live inside the total, as in Temporal Schedule-To-Close and gRPC deadlines spanning retries).
   - *Per-attempt / start-to-close / step* — "this one try is stuck or its worker crashed" — kept as short as the longest legitimate attempt, because it is the crash detector.
   - *Idle / heartbeat / chunk* — "no progress for X" — the only timer that can be short without killing legitimate long work. This is the direct answer to LLM calls that legitimately take minutes: a streaming model call heartbeats itself with every token, so an idle timeout (LangGraph `idle_timeout`, Vercel `chunkMs`, Temporal heartbeat, MCP progress) distinguishes *generating* from *hung* in seconds, while a total cap would have to be set to the worst case and detect hangs that late.
3. **Make cancellation cooperative and explicit, and design work to check it.** Every system surveyed signals (context, AbortSignal, CancellationToken, heartbeat response) rather than kills — and every documented disaster (CrewAI orphan threads, Temporal activities that never heartbeat, Mastra steps that ignore the signal, gRPC handlers that don't check) is work that never checked. Budget for a "does not cooperate" backstop (process/worker isolation, Vercel's step-termination even if the stream ignores abort).
4. **Record which timer fired, durably.** Temporal's distinct timeout events, LangGraph's `NodeTimeoutError.kind`, Vercel's `TimeoutError` abort reason, Step Functions' history — post-hoc distinguishability of queueing vs execution vs no-progress is what makes timeouts tunable instead of guessable.
5. **Instrument stage timing first, then set timeouts from percentiles.** OTel GenAI spans/metrics (duration, time-to-first-chunk/token, time-per-output-token, token usage) plus per-step/tool spans give the distributions; set per-attempt ≈ p99 + headroom, idle ≈ a multiple of normal inter-chunk gap, total ≈ the user/product budget — and if p99 doesn't fit the budget, change the design (parallelise, cache, split, background job) rather than raising the timeout.
6. **Stream by default; for work longer than a call should live, don't hold a call open.** Streaming defeats intermediary idle/read timeouts and supplies the progress signal for idle timers. Beyond a few minutes, use background/batch/job-ID-and-poll patterns with idempotency keys and resume — retrying a timed-out long call restarts from zero and risks duplicate side effects.
7. **Audit every timer in the path.** SDK (600s), HTTP library, framework node/tool/runtime (MCP 60s, AutoGen-MCP 5s), proxy/ALB/CDN (60–300s), and your own run deadline form a stack where the tightest — often an undocumented default — wins.

## Could not verify

- A primary OpenTelemetry page for the GenAI conventions was not opened directly; attributes/metrics above are from three independent secondary sources that agree (Bronto, ClickHouse, AI-Infrastructure/Genkit). Status "Development" is consistently reported.
- LangSmith TTFT/latency specifics are from secondary guides, not LangChain's own LangSmith docs page.
- CrewAI `max_iter` default is reported as 20, 25 in different version-dependent sources; treat as version-dependent.
- MCP Python SDK default timeout: sources disagree (no default vs 60s) by version; TS SDK 60s default is consistently reported.
- Cadence coverage is from its official docs site via search index only; no separate Cadence postmortem was surveyed.
- No framework was found that documents a pure "run-level deadline only, per-call durations merely observed" mode — this is reported as an absence in the surveyed docs, not proof none exists anywhere.

## Sources

All read 2026-11-23. Verified open = fetched in full; index = search-result excerpts.

- gRPC Deadlines — https://grpc.p2hp.com/docs/guides/deadlines/index.html — verified open
- Google SRE, Addressing Cascading Failures (Ch.22) — https://sre.google/sre-book/addressing-cascading-failures/ — index (via quoting sources)
- Microsoft, Reliable gRPC with deadlines and cancellation — https://learn.microsoft.com/en-us/aspnet/core/grpc/deadlines-cancellation?view=aspnetcore-3.0 — index
- Temporal, Detecting Activity failures — https://docs.temporal.io/encyclopedia/detecting-activity-failures — verified open
- Temporal blog, The four types of Activity timeouts — https://temporal.io/blog/activity-timeouts — index
- Temporal, Cancel a Workflow (Go) — https://docs.Temporal.io/develop/go/workflows/cancellation — index
- Temporal TS API, ActivityOptions — https://typescript.temporal.io/api/interfaces/common.ActivityOptions — index
- Cadence, Activities — https://cadenceworkflow.io/docs/concepts/activities/ — index
- Cadence, Executing activities — https://cadenceworkflow.io/docs/go-client/execute-activity/ — index
- AWS Step Functions, Task state — https://docs.aws.amazon.com/step-functions/latest/dg/state-task.html — verified open
- DBOS, Workflows (Python) — https://docs.dbos.dev/python/tutorials/workflow-tutorial — index
- DBOS, Workflows (Go) — https://docs.dbos.dev/golang/tutorials/workflow-tutorial — index
- LangGraph, Fault tolerance — https://docs.langchain.com/oss/python/langgraph/fault-tolerance — verified open
- LangChain, ChatOpenAI reference — https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI — index
- OpenAI Agents SDK (Python), ModelSettings — https://openai.github.io/openai-agents-python/ref/model_settings/ — index
- OpenAI Agents SDK (JS), ModelSettings — https://openai.github.io/openai-agents-js/openai/agents/type-aliases/modelsettings/ — index
- Vercel, AI SDK 7 — https://vercel.com/blog/ai-sdk-7 — index
- Vercel, AI SDK 7 changelog — https://vercel.com/changelog/ai-sdk-7 — index
- Mastra, Agent.stream() reference — https://mastra.ai/reference/streaming/agents/stream — index
- Mastra, Run.cancel() — https://mastra.ai/reference/workflows/run-methods/cancel — index
- AutoGen, OpenAI model client reference — https://microsoft.github.io/autogen/0.5.3//reference/python/autogen_ext.models.openai.html — index
- AutoGen issue #6202 (MCP tool 5s timeout) — https://github.com/microsoft/autogen/issues/6202 — index
- CrewAI hung-call / orphaned threads analysis — https://markaicode.com/errors/crewai-docker-deployment-failed-fix/ — index
- MCP 60s timeout / job-ID pattern — https://www.bigiron.cc/guides/mcp-tool-calls-timing-out-at-60-seconds-the-job-id-pattern — index
- MCP request timed out explainer — https://lsquarem.com/docs/learn/troubleshooting/mcp-request-timed-out — index
- ClickHouse, LLM inference latency (TTFT/TPOT, OTel) — https://clickhouse.com/resources/engineering/llm-inference-latency — index
- Bronto, LLM Observability (OTel GenAI) — https://docs.bronto.io/ai-features/llm-observability — index
- AI Infrastructure, GenAI Observability with OpenTelemetry — https://ai-infrastructure.net/genai-observability-otel/ — index
- Genkit, OpenTelemetry GenAI semantic conventions — https://genkit.dev/docs/observability/otel-genai-semantic-conventions/ — index
- Anthropic Python SDK docs (timeouts / long requests) — https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python — index
- Continuum, LLM API timeout errors (SDK/proxy/524) — https://continuumcode.ai/guides/llm-api-timeout-errors/ — index
- OneEnv, Microservice Timeout Budget / Deadline Propagation — https://blog.oneenv.io/articles/microservice-timeout-budget-deadline-propagation-across-calls — index
- LangSmith cost & latency from traces — https://www.masterclassbuddy.com/workflows/ls-cost-latency — index
