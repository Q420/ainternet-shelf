# TRANSLATION-SEAM EMPIRICAL CAPTURE (2026-11-23) — the probe build's precondition

Taken under the INDEX 279/285 build-stage precondition (empirical-first at the translation seam) immediately after Ben's tap authorised the probe build (INDEX 286), before any translation code was written. Three live calls through the corrected Groq helper, pinned `openai/gpt-oss-120b`, the probe tools offered natively. Raw artifact: `live-demo/native-translation-seam-capture-2026-11-23.json`.

**The native envelope, as actually delivered:**
- `choices[0].message` carries keys **`reasoning`, `role`, `tool_calls`**; when tool calls are present, **`content` is absent/null** in all three samples (including the call where a sentence of text was explicitly requested alongside the call — the model sent the call alone).
- `finish_reason` is **`tool_calls`**.
- Each tool call: keys **`function`, `id`, `type`**; `type` is `"function"`; the **id format is `fc_<uuid>`** (e.g. `fc_ed3f4c69-89ca-4184-a7ad-e3d811ca72ca`).
- `function` carries **`name` and `arguments`, where `arguments` is a JSON *string*** (`{"object":"brass lantern"}`), not an object — the translation must parse it, and an unparseable string is the malformed case (fail closed, per the scope).
- The message also carries a **`reasoning`** field (this model's chain-of-thought channel) — present in the envelope, not part of the contract; the translation ignores it and the record need not retain it beyond the raw capture.

**Multi-call behaviour (one observation, not a law):** asked for two lookups in one generation (two objects), the model emitted **one** tool call. Parallel multi-call emission was **not** observed in this sample; the translation must still handle a `tool_calls` array of any length, since the envelope permits it.

**Consequence for the build:** the translation contract is defined against this capture — parse `message.tool_calls[]` (id, function.name, function.arguments-as-string), tolerate absent content, ignore `reasoning`. Combined with INDEX 274: the same route also delivers text-contract responses and provider-refused hybrids, all of which the probe's capture boundary (below parsing) already anticipates.
