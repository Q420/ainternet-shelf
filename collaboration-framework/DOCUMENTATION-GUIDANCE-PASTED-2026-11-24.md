# Documentation guidance — pasted by Ben for review (2026-11-24)

Provenance: pasted into the main chat by Ben, 2026-11-24 15:14 MST, as
research for review ("review her research"). Transport evidence — a
research document, not Ben speaking. Filed verbatim below the line.
Remmy's review of it is recorded at INDEX 435.

---

I've reviewed the official OpenAI gpt-oss material and NVIDIA's current Nemotron documentation, including the model usage, inference, tool-calling and deployment guidance.

There is a useful architectural conclusion here: **we can build one room that supports both families, but we should not build one model interface and pretend both families speak it.** The room and the model-facing interface are separate concerns.

## 1. What the documentation tells us

### OpenAI gpt-oss

The pinned project model is `openai/gpt-oss-120b`. Official implementation and format documentation: the OpenAI gpt-oss repository and the Harmony specification.

- **Harmony is fundamental when serving the model directly.** OpenAI explicitly says gpt-oss should not be used without its Harmony format. When using a provider API, that provider handles the underlying representation. We should not manually inject Harmony into a provider request that already handles it.
- Tool calls are assistant messages with a recipient, such as `to=python`, and a call marker. The tool result comes back as a tool message, after which inference continues.
- The model was trained using a **stateful Python tool**. OpenAI's reference implementation also supports a stateless implementation, but explicitly changes the tool description to account for that difference.
- OpenAI supplies a Python execution reference, but warns that its Docker implementation is permissive and should not be treated as production security.

**What this means for our room:** The room should be persistent across execution calls during a worker's run. Variables, files and intermediate work should survive between invocations. The worker should not have to reconstruct its working environment every time it calls its execution tool. A stateless command runner would be a poor default for a model trained around stateful execution.

### NVIDIA Nemotron

A family, not one model or one fixed interface. Official documentation: the NVIDIA Nemotron repository and the NVIDIA NIM API documentation. NVIDIA's documentation distinguishes model families, serving engines and deployment paths.

- Nemotron supports deployment through vLLM, SGLang, TensorRT-LLM, NIM and other routes.
- NVIDIA's hosted Nemotron API exposes OpenAI-compatible Chat Completions, including `tools`, `tool_choice`, `tool_calls` and `tool_call_id`.
- Some model endpoints expose `reasoning_content` separately from ordinary message content.
- Reasoning controls differ by model. For example, Nemotron 3.5 Super documents `reasoning_effort`, while Bolt documents model-specific `chat_template_kwargs` and `skip_special_tokens` behaviour.

**What this means for our room:** We need a Nemotron-specific model adapter that understands the selected model and serving engine. We must not assume that every Nemotron model uses the same reasoning flags, output parsing or tool-call behaviour. An OpenAI-compatible endpoint is not proof that every model-specific feature behaves identically.

## 2. The implementation guidance I would carry into the design

Recommendations derived from the documentation, not claims that the room has already been built or verified.

**One room, two model interfaces:** Generated worker (gpt-oss or Nemotron) → per-model adapter (gpt-oss: Harmony / provider translation / tool-call continuation; Nemotron: model-specific API / parser / reasoning configuration) → **Common execution contract** (invocation identity · working directory · execution · bounded result · continuation) → **Sealed room** (persistent workspace · case materials · shell and runtime · resource limits · no external network or host access) → **Independent execution record and checker** (doorway dispatch · process evidence · outputs · termination · filesystem changes).

### A. Keep the execution environment model-neutral
The room exposes ordinary execution capabilities: shell and interpreter; persistent working directory; case-stocked source materials; scratch and deliverable paths; runtime dependencies; captured stdout, stderr and exit status; bounded execution and resource consumption. The model adapter translates its native tool call into the room's execution contract. The room should not care whether the request originated as a Harmony tool call or an OpenAI-compatible `tool_calls` object.

### B. Preserve native interaction semantics
For gpt-oss, the adapter must preserve the assistant's tool-call message and return the result in the correct tool-message structure. For Nemotron, the adapter must preserve the relevant assistant message, tool-call IDs and result association, and handle the selected model's reasoning fields and serving-specific settings correctly. We should not flatten everything into a text transcript and then reconstruct the interaction.

### C. Make the workspace genuinely stateful
The OpenAI documentation gives a strong reason to make the room persistent for the duration of a run. The worker should be able to: open and inspect a source; create an intermediate file; run a script against it; inspect the output; modify the script; continue working; write the deliverable. The framework should record observable execution and filesystem effects without pretending to record the model's internal computation.

### D. Do not inherit the reference sandbox's weaknesses
OpenAI's reference Python tool is useful for understanding the model's expected working pattern. It is not a security design to copy. The room's security must come from independently enforced isolation, not from the tool's prompt, its declared working directory or the model's willingness to behave. That agrees with our existing R1/R2 requirements.

## 3. What I would change in the current room design

| Existing design area | Documentation-informed refinement |
|---|---|
| Execution tool interface | Keep a common internal execution contract, but allow model-specific native argument translation. |
| Runtime persistence | Explicitly preserve process/session workspace state across calls within one run. |
| Model integration | Treat model, provider, serving engine, chat template and tool parser as separately recorded configuration. |

One further point: **the room's result contract must be independent of the model's native result format.** The room can return a stable result object containing exit status, bounded output and execution identity. Each adapter then translates that result back into the format its model expects. That prevents the room from becoming coupled to one vendor's API.

## 4. The important limitation

Nemotron is too broad a label to certify one exact integration. The documentation covers multiple generations and variants, and their interfaces are not identical. I would not freeze the Nemotron adapter until the intended checkpoint and serving route are identified. The same goes for gpt-oss: the pinned Groq route and a locally served Harmony implementation have different integration responsibilities. This does **not** mean we need to run another model experiment. It means we should use the exact model and provider documentation for the implementation target.

## My recommendation

Build the room as a model-neutral execution environment with separate, replaceable native adapters. Preserve state across calls. Keep the doorway and authority boundary intact. Let the model use its natural execution interface, and let the room enforce the walls.

The most important insight from the OpenAI documentation is that stateful execution is part of the model's learned working pattern. The most important insight from NVIDIA's documentation is that Nemotron's serving and tool-calling configuration is model-specific.

Those two findings should shape the architecture from the beginning.

I would pass this as implementation guidance to Remmy, not as permission to start building.
