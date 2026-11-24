# OSS / Nemotron Documentation Review — the documented "how" for both room occupants

**Scope:** official API/model documentation only. This review states what the documents
specify — never what our worker demonstrably does (that is the evidence audit's
territory). Where the documentation is silent, this review says so in those words.
Every claim is cited to its document. Non-official sources are used only where no
official document exists, and are labelled as such.

**Occupants:** `openai/gpt-oss-120b` (Groq route now, NVIDIA route later) and the
NVIDIA Nemotron family (NVIDIA API). The design question underneath: how does each
model emit tool calls, in what forms, and how does each consume tool results — so the
room's interface and stock are model-general.

---

## Part I — gpt-oss (OpenAI) and the Harmony format

### 1. Tool-call emission

- **Channel/format.** gpt-oss was trained on the **Harmony response format**. Assistant
  output is split into three channels: `analysis` (chain-of-thought), `commentary`,
  and `final`. "Any function tool call will typically be triggered on the `commentary`
  channel while built-in tools will normally be triggered on the `analysis` channel."
  A tool call is a *message*, not a field inside content: the header carries a
  recipient `to=functions.<name>`, usually a `<|constrain|>json` marker, the body is
  the arguments, and generation ends with the dedicated stop token `<|call|>`
  (200012), distinct from `<|return|>` for a finished answer.
  (*Harmony response format* — OpenAI, openai/harmony repository, `docs/format.md` —
  specifies channels, recipients, stop tokens.)
- **Argument representation.** The call body is a **bare JSON object** —
  e.g. `{"location": "San Francisco"}` — not a JSON string wrapped in another
  structure, at the Harmony layer. (Same document, "Receiving tool calls".)
- **Tool definitions.** Developer-provided functions are defined in the **developer**
  message, in a dedicated `# Tools` section, in TypeScript-like syntax inside a
  `namespace functions { ... }` block; return types are always declared `any`. The
  spec advises the `functions` namespace "to not conflict with other tools that the
  model might have been trained on", and says sticking closely to the format improves
  calling accuracy. (Same document, "Function calling / Defining available tools".)
- **Built-in tools.** Exactly two were trained in, and they are defined in the
  **system** message, not the developer message: a `browser` tool and a `python`
  tool. (Same document, "Built-in tools".) See §3 for the python tool, which is
  gpt-oss's documented execution tool.
- **Preambles.** The model may emit a user-visible `commentary` message (e.g. an
  action plan) before calling multiple functions. (Same document, "Preambles".)

### 2. Tool-result consumption

- **Exact documented form.** After a call is handled, the result is provided as a new
  message whose **author/role is the tool's own full name**, addressed back to the
  assistant on the `commentary` channel:

  ```
  <|start|>{toolname} to=assistant<|channel|>commentary<|message|>{output}<|end|>
  ```

  Worked example in the spec: `<|start|>functions.get_weather to=assistant … {"sunny": true, "temperature": 20}<|end|>`.
  (Harmony format, "Handling tool calls".)
- **Per-call identity: the documentation specifies none.** Harmony has no call IDs.
  A result is identified only by the tool name in its author field and by its
  position after the call. Two calls to the *same* function in one turn have no
  documented disambiguation at the Harmony layer. (Harmony format, passim — the
  absence is the finding.)
- **Result content expectations.** None specified beyond "the output". Tool return
  types are declared `any`; the spec's examples return JSON text. The format imposes
  no schema on result content. (Harmony format, "Defining available tools" /
  "Handling tool calls".)
- **Reasoning handling across tool turns.** Unlike final answers (where prior CoT is
  dropped), in tool calling the previous chain-of-thought **is** passed back in with
  the tool result, "to provide the model with the necessary information to continue
  its chain-of-thought". (Harmony format, "Handling reasoning output in subsequent
  sampling" / function-calling example.)
- **At the Groq API layer** (what our harness actually sees), the same exchange is
  re-shaped into OpenAI Chat Completions form: calls arrive as structured
  `tool_calls` (an `id`, `function.name`, and `function.arguments` as a JSON
  **string**), and results go back as `role: "tool"` messages carrying the
  `tool_call_id`. (Groq *Local Tool Calling* — Groq — specifies the host-side loop
  and message shapes; Groq *API Reference* — Groq — specifies the request/response
  fields.) The call IDs are a serving-layer addition; they do not exist in Harmony
  itself.

### 3. The documented execution tool, and its result format

- **gpt-oss's documented execution tool is the built-in `python` tool** — there is
  no shell/container tool in gpt-oss's documented toolset. Its documented form
  (Harmony format, "Built-in tools / Python tool"):
  - Calls go to the `analysis` channel; the recipient is always `python`.
  - The message body is **freeform Python code** (no JSON arguments object).
  - "When you send a message containing Python code to python, it will be executed
    in a stateful Jupyter notebook environment. python will respond with the output
    of the execution or time out after 120.0 seconds. The drive at '/mnt/data' can
    be used to save and persist user files."
  - **Result format: the documentation does not specify a structured result
    schema.** The result is "the output of the execution", returned as a tool
    message like any other. No stdout/stderr split, no exit-code field, and no
    error-object form is defined anywhere in the Harmony specification.
- **`container.exec` is not an OpenAI-documented tool — for gpt-oss or anywhere
  else.** OpenAI publishes no documentation for it (the absence of official
  documentation for ChatGPT's container tools is itself remarked on by the source
  below). The only definition in circulation is an **elicited tool list** — the
  model GPT-5.2 Thinking reporting its own ChatGPT toolset (Willison, *ChatGPT
  Containers…*, 26 Jan 2026 — **not official documentation**; a model-reported
  list, reproduced verbatim):
  - `container.exec({ cmd: string[], session_name?: string | null, workdir?: string | null, timeout?: integer | null, env?: object | null, user?: string | null }) -> any`
  - Description: "Run a command inside the container and return stdout/stderr."
  - Sibling tools in the same namespace: `container.feed_chars` (interactive
    sessions), `container.open_image`, `container.download`.
  - **Result format: not specified.** The return type is given as `any`; the words
    "return stdout/stderr" are the whole of the result specification. No field
    names, no exit-code convention, no error form is documented in this or any
    other source found.
- **The one officially documented execution-result schema in OpenAI's catalogue**
  belongs to a different tool: the Responses API **`code_interpreter`** tool
  (OpenAI *API Reference / SDK schema* — developers.openai.com — specifies the
  `code_interpreter_call` item):
  - The call item carries `id`, `code` (a single code string), `container_id`, and
    a `status` enum: `in_progress`, `interpreting`, `completed`, `incomplete`,
    `failed`.
  - Results live in an `outputs` array whose members are exactly two shapes:
    `{ type: "logs", logs: string }` — one combined log string — or
    `{ type: "image", url: string }`.
  - Notably: **no exit-code field, and no separation of stdout from stderr**, in
    the one execution result format OpenAI does specify. (The same schema also
    contains a `local_shell` call type — the Codex-style shell tool — confirming
    OpenAI documents shell execution as a Responses-API tool concept, though this
    review did not extract its full output schema.)

  **Finding for the assessment's open question:** *the documentation does not
  specify* a structured exec result format (stdout/stderr/exit code) for
  `container.exec`, for gpt-oss's `python` tool, or — beyond the combined-`logs`
  convention above — for any OpenAI execution tool. Any room that returns
  execution results must choose the inner shape itself; nothing in the official
  documentation constrains it beyond "output text in a tool message".

### 4. Serving-API constraints — Groq (gpt-oss route)

All from Groq's official documentation (Groq *API Reference*, read in full for this
review; Groq *Local Tool Calling*):

- **`tool_choice`**: `none` (default when no tools present), `auto` (default when
  tools are present), `required`, or a named tool object that forces one tool.
- **`parallel_tool_calls`**: boolean, **defaults to true** — parallel function
  calling is on unless the host turns it off.
- **`tools`**: maximum **128** functions per request.
- **`disable_tool_validation`**: boolean, default false. "If set to true, groq will
  return called tools without validating that the tool is present in
  request.tools. tool_choice=required/none will still be enforced, but the request
  cannot require a specific tool be used." — i.e. the flag relaxes *unoffered-name*
  validation only; it does not lift `none`/`required` enforcement.
- **Validation failure behaviour**: when the model generates an invalid tool-call
  object, Groq returns a **400** with code `tool_use_failed` and the generation
  preserved in `failed_generation` — a wholesale refusal of the response, which
  Groq's docs treat as a recoverable generation event (retry guidance).
- **Execution is host-side by design**: "execution happens in your code. You
  control the environment, security, and implementation." (Groq *Local Tool
  Calling*.)

---

## Part II — Nemotron (NVIDIA)

"Nemotron" is not one interface. The documentation describes **three distinct
sub-families with three different native tool-call formats**, unified only at the
serving-API layer. They are treated separately below.

### 5. Which Nemotron members document tool calling at all

From NVIDIA's own documentation (NVIDIA *Function (Tool) Calling with NVIDIA NIM
for LLMs*, docs.nvidia.com, NIM v1.15.0 — the supported-models list for tool
calling in LLM NIM containers; and NVIDIA *Call Functions (Tools) — NIM for
Vision Language Models*):

- **Llama Nemotron Nano models** — tool calling supported, **with detailed
  thinking off** (NIM LLM list, verbatim caveat).
- **Llama Nemotron Super models** — same caveat.
- **Llama Nemotron Ultra models** — same caveat.
- **Nemotron 3 Nano** — listed without the thinking caveat.
- **Nemotron Nano 12B v2 VL** — listed in the VLM NIM function-calling support
  list.
- **Nemotron-Mini-4B-Instruct** — its model card documents function calling as a
  designed use case, with a `Tool` role in its prompt template (see §6c).
- **Nemotron-3-Ultra-550B-A55B** — its build.nvidia.com model card names "tool use"
  among its best-for workloads (NVIDIA *nemotron-3-ultra-550b-a55b model card* —
  build.nvidia.com); the NIM list above covers the Llama-Nemotron Ultra line, and
  the Nemotron 3 line's tool format is the one in §6b.
- **Nemotron-3.5-Bolt-E4B** — its build.nvidia.com model card documents an
  asynchronous tool-calling pattern in detail (see §7c).
- Also on the NIM tool-calling list, for contrast: GPT-OSS-20B and GPT-OSS-120B
  (NVIDIA serves gpt-oss too), Llama 3.1/3.2/3.3, Mistral, Qwen2.5, DeepSeek —
  i.e. on the NVIDIA route both room occupants are served by the same NIM
  function-calling machinery.

Any Nemotron member **not** in the lists above: the documentation does not specify
tool calling for it, and this review makes no claim.

### 6. Tool-call emission, per sub-family

#### 6a. Llama Nemotron (Nano / Super / Ultra — Llama-3.x-derived)

- **API surface.** Through NIM / build.nvidia.com the calls arrive as standard
  OpenAI `tool_calls` (id, `function.name`, `function.arguments` as a JSON string)
  — the model card's worked example shows exactly this object. (NVIDIA
  *Llama-3.3-Nemotron-Super-49B-v1.5 model card* — Hugging Face / NGC — specifies
  the vLLM serving setup and the example exchange.)
- **Native layer.** Serving requires a model-specific tool parser shipped in the
  model repository: the card instructs vLLM to run with
  `--enable-auto-tool-choice --tool-call-parser llama_nemotron_json
  --tool-parser-plugin <repo>/llama_nemotron_toolcall_parser_no_streaming.py`.
  The parser's name (`llama_nemotron_json`) documents that the model's in-content
  call representation is JSON-based and must be parsed out of the content stream
  by a bespoke parser — it is **not** the Llama-3.1 stock format, or the stock
  parser would do. (This review did not read the parser plugin or the chat
  template verbatim — the hosting repository rate-limited the fetch — so the
  exact in-content delimiters are *not* asserted here; the card and the NIM docs
  are the authority for everything stated.)
- **Reasoning interaction.** Reasoning is toggled in the system prompt: empty
  system prompt ⇒ reasoning ON by default; `/no_think` in the system prompt ⇒
  reasoning OFF (greedy decoding recommended OFF; temperature 0.6 / top-p 0.95
  ON). The NIM documentation, however, lists Llama Nemotron tool calling as
  supported **with detailed thinking off** — the two documents together mean: the
  card demonstrates tool calling, and NVIDIA's serving documentation only
  warrants it in thinking-off mode. (Model card, "Quick Start and Usage
  Recommendations"; NIM LLM function-calling list.)
- The v1.5 card also documents the post-training behind the behaviour: SFT for
  tool calling plus iterative DPO "for Tool Calling capability enhancements",
  and a BFCL v3 score (71.75, reasoning on) — capability claims, cited here only
  to show tool calling is a trained, documented feature of the line, not an
  accident of the template.

#### 6b. Nemotron 3 (Nano 30B A3B, Super 120B, Ultra 550B; also 3.5 Lightning / Bolt lineage)

- **Template lineage.** The chat template is derived from the **Qwen3-Coder**
  template with Nemotron extensions (`<think>`/`</think>` reasoning blocks,
  `enable_thinking` template flag, reasoning-budget support), over a ChatML
  envelope (`<|im_start|>…<|im_end|>`). (NVIDIA *Nemotron 3 Nano Technical
  Report*, §3.1–3.3, as reproduced in UC Berkeley Scalable AI lecture material —
  the report itself is NVIDIA's document; the lecture is the accessible copy.)
- **Call format.** Tools are declared in the system turn inside `<tools>…</tools>`;
  a call is emitted **content-embedded** as XML-style markup:

  ```
  <tool_call>
  <function=get_weather>
  <parameter=location>New York, NY</parameter>
  <parameter=unit>celsius</parameter>
  </function>
  </tool_call>
  ```

  (Technical Report template example, ibid.) Consequences that matter for a room:
  - **Arguments are not a JSON object.** Each argument is a separate
    `<parameter=name>value</parameter>` element whose value is text. Structured
    values have no documented native encoding in this format.
  - **Multiple calls per turn** are native to the format (the template renders
    several `<tool_call>` blocks in one assistant turn).
  - At the serving layer a dedicated parser converts this into OpenAI
    `tool_calls`: NVIDIA's serving material names vLLM's **`qwen3_coder`** tool
    parser for this family, and the API then presents arguments as a JSON string
    like any other model. (Parser name per NVIDIA's model-card/cookbook material
    as catalogued from the official card; the template example above is the
    primary evidence for the wire format.)
- **Reasoning.** `<think>` blocks precede the answer/calls; thinking can be
  toggled per request (`chat_template_kwargs: {"enable_thinking": …}`) and
  budgeted. Unlike the Llama Nemotron line, tool use and thinking are documented
  as integrated ("tool-integrated reasoning" is a named design concern of the
  template) rather than thinking-off-only. (Technical Report §3.1.1, ibid.;
  Nemotron 3 Ultra model card — build.nvidia.com — "Reasoning Mode: Configurable
  on/off via chat template".)

#### 6c. Nemotron Nano v2 VL and Nemotron-Mini (earlier lineages)

- **Nemotron-Nano-12B-v2-VL** (Llama-based): its official chat template
  (nvidia Hugging Face repository, `chat_template.jinja`) declares tools as a
  JSON array inside `<AVAILABLE_TOOLS>[ … ]</AVAILABLE_TOOLS>` in the system
  turn and specifies two bespoke formats verbatim:
  - Calls: `<TOOLCALL>[{"name": "tool_name1", "arguments": "tool_args1"}, {"name": "tool_name2", "arguments": "tool_args2"}]</TOOLCALL>` — a **JSON array** of
    call objects, content-embedded; `arguments` is shown as a string in the
    template's own example.
  - Results: `<TOOL_RESPONSE>[{"response": "tool_response1"}, {"response": "tool_response2"}]</TOOL_RESPONSE>` (see §7b).
- **Nemotron-Mini-4B-Instruct** (Nemotron-4 lineage): the model card's prompt
  template includes a literal `Tool` turn — `… Assistant … Tool\n{tool
  response}\nAssistant` — documenting result-as-its-own-turn in a plain-text
  template, with no call syntax specified. (NVIDIA *Nemotron-Mini-4B-Instruct
  model card* — Hugging Face.) Included for completeness; this lineage is not a
  realistic room occupant.

### 7. Tool-result consumption

- **7a. At the NVIDIA serving-API layer (all sub-families).** Results go back as
  OpenAI-shaped messages: `{"role": "tool", "content": str(result),
  "tool_call_id": <id from the call>, "name": <function name>}` — the NIM
  function-calling documentation's worked example appends exactly this shape and
  re-invokes. Per-call identity is the serving layer's `tool_call_id`, as on
  Groq. (NVIDIA *Function (Tool) Calling with NVIDIA NIM for LLMs*.)
- **7b. Nemotron Nano v2 VL native form.** `<TOOL_RESPONSE>[{"response": …},
  …]</TOOL_RESPONSE>` — results are returned as **one batched array**, matched to
  calls **positionally**. The documentation specifies no per-call identifier in
  the native format. (Official chat template, §6c.)
- **7c. A documented deviation — Nemotron-3.5-Bolt-E4B.** Its model card
  documents an *asynchronous* tool-calling pattern: transmit functions via the
  standard OpenAI `tools` structure; read executions from `message.tool_calls`;
  **restrict generation to a single tool invocation per assistant turn**; give
  each decoupled job a persistent task identifier; and "provide subsequent
  execution outputs as a **user role** turn" (prefixed), synthesising the final
  response only when no calls remain outstanding. (NVIDIA
  *Nemotron-3.5-Bolt-E4B model card* — build.nvidia.com.) This is the only
  Nemotron document found that prescribes a non-`tool`-role result channel, and
  it is specific to that model's async pattern.
- **7d. Result-content expectations.** For developer-defined functions, no
  Nemotron document specifies an inner result schema — content is the host's
  string, as with gpt-oss. **No Nemotron family member documents a built-in
  execution tool** (no analogue of gpt-oss's `python` built-in appears in any
  NVIDIA document read): an exec tool for a Nemotron occupant would be an
  ordinary developer-defined function whose definition, description, and result
  convention are entirely the host's design. The documentation does not specify
  any stdout/stderr/exit-code convention for Nemotron tool results.

### 8. Serving-API constraints — NVIDIA (integrate API / NIM)

From NVIDIA *Function (Tool) Calling with NVIDIA NIM for LLMs* (v1.15.0) and the
generic NIM LLM function-calling page:

- **`tool_choice`**: `"none"`, `"auto"`, or a named tool choice object
  (`{"type": "function", "function": {"name": …}}`). `tool_choice` and `tools`
  must be set together. No `required` value is documented in the NIM pages read
  (the OpenAI API is referenced for parameter details).
- **Validation behaviour — the documented failure mode is the opposite of
  Groq's.** NIM post-processes model output into `tool_calls` with a per-model
  **tool parser** (`NIM_TOOL_CALL_PARSER`; values include `pythonic`, `mistral`,
  `llama3_json`, `granite`, `hermes`, `jamba`, or a custom plugin). The docs warn
  verbatim: "If the chat completion response contains an empty `tool_call` field
  but the function call is present in the `content` field, the output of the LLM
  was not post-processed into a tool call successfully." — i.e. a malformed or
  unparsable call **degrades silently into content**; the documentation specifies
  **no wholesale-refusal error and no equivalent of Groq's
  `disable_tool_validation`**. Unoffered-tool handling at the NVIDIA layer is
  simply not specified in the documents read: the parser extracts calls matching
  the model's format; what happens to a call naming an unlisted tool is a
  host-side concern by construction (the host receives it as a parsed call or as
  content).
- **Parallel calls.** The generic NIM page documents `parallel_tool_calls`
  (default `False`) and a per-model support table, but in the version read that
  table covers only Llama-3.1 and Mistral models — **the documentation does not
  specify parallel-call support per Nemotron model** in the pages read. At the
  native layer, both Nemotron 3 and Nemotron Nano v2 templates natively emit
  multiple calls in one turn (§6b, §6c), so multi-call turns are a documented
  behaviour of the models even where the serving parameter's support matrix is
  silent.
- **Thinking/tool-calling interaction** is the family's real constraint and it
  is per-sub-family: Llama Nemotron — tool calling warranted with detailed
  thinking **off**; Nemotron 3 — thinking and tools integrated, toggled via
  `enable_thinking`. (§6a, §6b.)

---

## Part III — Comparison: one room, two occupants

### What an interface/stock design can share

1. **The doorway at the serving-API layer is identical.** On both hosted routes
   (Groq for gpt-oss; NVIDIA's API for Nemotron — and for gpt-oss-on-NVIDIA too)
   the host sees the same OpenAI Chat Completions contract: a `tools` array of
   JSON-Schema function definitions in; structured `tool_calls` out (id, name,
   JSON-string arguments); results back as `role: "tool"` messages keyed by
   `tool_call_id`. A single doorway, resolver, and record format serves both
   occupants unchanged. (Groq *Local Tool Calling*; NVIDIA NIM *Function (Tool)
   Calling*.)
2. **Tool definitions are JSON Schema in both worlds** at the API layer —
   one registry/schema format stocks both.
3. **Result content is host-defined text in both worlds.** Neither family's
   documentation imposes an inner schema on function results, so one result
   convention (e.g. plain output text, with the room's own status line if
   desired) can be returned to both — *as a host convention*, documented here as
   unconstrained by either specification, not as a documented expectation of
   either model.
4. **The exec stock itself is shareable.** A Python/shell execution environment
   is a room property, not a model property; both occupants can be offered an
   execution tool backed by the same stock.

### What must be per-model (or per-provider)

1. **The native wire format — if the room ever goes below the hosted API.**
   Harmony recipient-messages (bare-JSON body, `<|call|>`), Nemotron 3's
   `<tool_call><function=…><parameter=…>` XML, Nano v2's `<TOOLCALL>` JSON
   array, Llama Nemotron's parser-mediated JSON: four mutually unintelligible
   formats, each with its own template and parser. On hosted routes the
   provider absorbs this; in any self-hosted (NIM/vLLM) configuration the
   per-model chat template and tool parser are mandatory, model-specific
   configuration. A model-general room must therefore treat "native format" as
   a per-model adapter, never as a shared assumption.
2. **Call/result identity below the API layer.** Harmony identifies results by
   tool name only (no call IDs; positional matching, ambiguous for repeated
   same-tool calls); Nano v2's `<TOOL_RESPONSE>` is a positional batch with no
   IDs. Only the serving APIs mint call IDs. Anything in the room that
   correlates results to calls must rely on the API-layer ID where available
   and must not assume the native layer provides one.
3. **Argument representation.** Bare JSON object (Harmony native) vs JSON
   *string* (both APIs) vs per-parameter text elements with no documented
   structured-value encoding (Nemotron 3 native). Argument *validation* must
   happen after the serving layer has normalised to JSON; a design that
   validated at the native layer would need three different validators.
4. **Refusal/validation semantics are per-provider.** Groq: wholesale 400
   (`tool_use_failed`, `failed_generation`) plus the `disable_tool_validation`
   escape hatch. NVIDIA: no documented wholesale refusal and no such flag;
   instead, silent parse failure (call left in `content`, empty `tool_calls`).
   Error handling, unoffered-call policy, and retry logic cannot be shared
   verbatim across routes.
5. **Thinking configuration is per-model.** gpt-oss: reasoning effort in the
   system message, CoT preserved across tool turns by specification. Llama
   Nemotron: tool calling warranted only with detailed thinking off.
   Nemotron 3: `enable_thinking` template flag with integrated tool use. The
   room's per-assembly configuration must carry the occupant's thinking/tool
   mode as an explicit, per-model setting.
6. **The exec affordance itself differs in kind.** gpt-oss was *trained with* a
   documented execution built-in (`python`: freeform code body, stateful
   Jupyter, 120-second timeout, `/mnt/data` persistence) — an execution tool
   shaped like that built-in matches a documented, trained behaviour. No
   Nemotron document describes any built-in execution tool; for Nemotron
   occupants the exec tool is a host-invented function definition, and its
   name, schema, and description are unconstrained design choices. A
   model-general room can offer the same *capability* to both, but should not
   assume the same *shape* of request: gpt-oss's documented exec call is a
   freeform code string to a bare recipient, while a Nemotron exec call will
   arrive as an ordinary function call with JSON arguments.

### Headline

The hosted serving layer has already converged: one OpenAI-shaped doorway
serves both occupants. Everything genuinely model-specific — wire format,
result identity, argument encoding, refusal semantics, thinking/tool
interaction, and the exec affordance's shape — lives **below or beside** that
layer, and the room's design should keep it there: shared doorway and stock;
per-model adapter for format, per-provider adapter for failure semantics,
per-model configuration for thinking. And on the assessment's named open
question, the documentation's answer is an absence: **no official document
specifies a structured execution-result format** — the room must define its
own, and may do so freely, because neither occupant's documentation
constrains it.

---

## Sources

All read 2026-11-24. "Read in full" = fetched and read end-to-end for this review;
other entries were read in the relevant sections, as noted.

**OpenAI / gpt-oss**
- *Harmony response format* — OpenAI, openai/harmony repository, `docs/format.md`
  — read in full. https://raw.githubusercontent.com/openai/harmony/main/docs/format.md
- *OpenAI Harmony Response Format* (cookbook rendering of the same specification)
  — OpenAI, developers.openai.com — sections. https://developers.openai.com/cookbook/articles/openai-harmony
- *Responses API — SDK schema* (`code_interpreter_call`, outputs `logs`/`image`)
  — OpenAI, developers.openai.com — schema sections via search extract.
  https://developers.openai.com/api/reference/cli/__sdk_schema

**Groq**
- *API Reference* (Chat Completions: `tool_choice`, `parallel_tool_calls`,
  `disable_tool_validation`, `tools` max 128) — Groq, console.groq.com — read in
  full. https://console.groq.com/docs/api-reference
- *Local Tool Calling* (host-side loop, `tool_use_failed`/`failed_generation`) —
  Groq, console.groq.com — read in full 2026-11-24 for the prior in-house
  research and relied on here. https://console.groq.com/docs/tool-use/local-tool-calling

**NVIDIA**
- *Function (Tool) Calling with NVIDIA NIM for LLMs*, v1.15.0 (supported-models
  list incl. Llama Nemotron Nano/Super/Ultra "detailed thinking off", Nemotron 3
  Nano, GPT-OSS; `tool_choice` options; parser list; result-message example) —
  NVIDIA, docs.nvidia.com — read in full.
  https://docs.nvidia.com/nim/large-language-models/1.15.0/function-calling.html
- *Function Calling — NVIDIA NIM for LLMs*, v1.6.0 (earlier supported-models /
  parallel table) — NVIDIA, docs.nvidia.com — sections via search extract.
  https://docs.nvidia.com/nim/large-language-models/1.6.0/function-calling.html
- *Call Functions (Tools) — NVIDIA NIM for Vision Language Models* (Nemotron
  Nano 12B v2 VL in support list) — NVIDIA, docs.nvidia.com — sections via
  search extract. https://docs.nvidia.com/nim/vision-language-models/1.6.0/function-calling.html
- *Llama-3.3-Nemotron-Super-49B-v1.5 model card* (tool-calling post-training,
  `llama_nemotron_json` parser plugin, worked `tool_calls` example, `/no_think`)
  — NVIDIA, Hugging Face / NGC — read in full.
  https://huggingface.co/nvidia/Llama-3_3-Nemotron-Super-49B-v1_5/raw/main/README.md
- *Nemotron-Nano-12B-v2-VL chat template* (`<AVAILABLE_TOOLS>`, `<TOOLCALL>`,
  `<TOOL_RESPONSE>` formats verbatim) — NVIDIA, Hugging Face repository — via
  search extract of the template file.
  https://huggingface.co/nvidia/NVIDIA-Nemotron-Nano-12B-v2-VL-NVFP4-QAD/blob/9ed36d5bb5b4ff2b5ba9092afe33f135a1d04180/chat_template.jinja
- *Nemotron 3 Nano Technical Report* (§3.1–3.3: Qwen3-Coder-derived template,
  `<tool_call><function=…><parameter=…>` example, `enable_thinking`) — NVIDIA —
  as reproduced in UC Berkeley Scalable AI lecture 16 slides.
  http://scalable-ai.eecs.berkeley.edu/assets/lecture_slides/lecture_16_1.pdf
- *nemotron-3-ultra-550b-a55b model card* ("tool use" among best-for workloads;
  reasoning configurable via chat template) — NVIDIA, build.nvidia.com —
  sections via search extract. https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b/modelcard
- *Nemotron-3.5-Bolt-E4B model card* (asynchronous tool-calling pattern; results
  as user-role turns; one invocation per assistant turn) — NVIDIA,
  build.nvidia.com — sections via search extract.
  https://build.nvidia.com/nvidia/nemotron-3.5-bolt-e4b/modelcard
- *Nemotron-Mini-4B-Instruct model card* (function-calling use case; `Tool` role
  in prompt template) — NVIDIA, Hugging Face — sections via search extract.
  https://huggingface.co/nvidia/Nemotron-Mini-4B-Instruct/raw/main/README.md
- *nvidia / nemotron-3-nano-30b-a3b* model page (family positioning; reasoning
  via chat-template flag) — NVIDIA, docs.api.nvidia.com — sections via search
  extract. https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-nano-30b-a3b

**Non-official (used only where no official document exists, and labelled)**
- Willison, *ChatGPT Containers can now run bash…* (26 Jan 2026) — the elicited
  GPT-5.2 Thinking tool list containing the only known `container.exec`
  definition; the author himself notes OpenAI publishes no documentation for
  these tools. Read in full. https://simonwillison.net/2026/Jan/26/chatgpt-containers/

**Not obtained:** the Llama Nemotron tool-parser plugin source and the
Nemotron-3-Nano chat-template file verbatim (hosting repository rate-limited
both fetches). No claim in this review rests on their exact contents; where the
wire format matters (§6a), the review says what the card/NIM documents do and
do not establish.
