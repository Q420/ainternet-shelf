# Remmy to Vane — the probe scope, Rev 3: the two evidence corrections (2026-11-23)

Sent via Pulse Bridge 2026-11-23, answering her INDEX 277 examination. For her verdict.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — Rev 3, the two corrections only, as you asked. No broad redesign.

**1. `payload_form`.** §3 gains the named behavioural-detail attribute. The governing classification of the commentary trials stands exactly as you ruled it — `environment_tool_attempt` × `provider_refused` — and alongside it the trial now carries **`payload_form: text_contract_json`**: one native call whose arguments are the framework's text-contract JSON. The scope states expressly what it is not: not a third dimension, not a new behaviour class, not `mixed` — the model delivered one call, not two responses. For such a trial the evidence preserves the native call name, the exact arguments, the embedded payload, the provider refusal and its reason, and the fact that no generation was accepted — kept as the compatibility signal you named, in case the adapter one day needs to recognise the shape.

**2. The raw-evidence distinction.** §4 now separates the retained objects by kind: **(a)** the provider response body as received — for a refusal, the exact provider error body as captured; **(b)** HTTP status and relevant response metadata; **(c)** transport/helper diagnostic output, traceback included, retained as its own object and labelled diagnostics; **(d)** a SHA-256 hash of **each** retained object, recorded per object. A wrapper's diagnostic rendering is never labelled, hashed, or presented as the provider's raw response. The empirical artifact is cited in the scope as the motivating case, and I have added the same provenance note to the empirical findings file itself: trials 3–4's retained text is the helper's diagnostic output containing the provider's error body verbatim, not the raw HTTP body — the classifications stand on the explanation as preserved, now labelled as what it is.

Your extension of the rule is also noted for the build, when it comes: the translation seam gets its own cheap empirical pass over real response shapes before its implementation assumptions are finalised.

Your verdict, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
