# THE EMPIRICAL-FIRST FIX — FIRST APPLICATION: A LIVE PROBE OF THE PINNED MODEL (2026-11-23)

Ben's order, 19:16 MST, on the centre-of-gravity flaw (governance perfected before the worker was ever proven): **"Let's immediately fix that.."** The fix, adopted as the programme's rule from this entry: **empirical before architectural — any piece resting on an assumption about how a model or a provider behaves gets a cheap live probe first, before the scope and the witnesses, the way the chain simulation did.** Its first application, run within the hour: the native-probe suite of the INDEX 273 scope, executed by hand against the real pinned model **before** the probe piece is built — measurement first, architecture second.

**Method.** Five identical trials of the scope's synthetic probe case (the brass-lantern toy task), `probe.lookup`/`probe.note` offered **natively** (provider tool definitions, `tool_choice: auto`) and described in the text contract at once, temperature 0.2, via the corrected Groq helper (INDEX 262 — its preserved error bodies are what make trials 3–4 readable at all). Raw responses retained in `live-demo/native-probe-empirical-2026-11-23.json`. Nothing executed; the probe tools have no performers. Cost: ~380 tokens and ~0.15 s per accepted trial.

**Results — classified in the scope's two dimensions** (a first-pass scratch classifier labelled trials 3–4 bare provider failures; their preserved error bodies show the attributable attempts, and the classifications below are the corrected readings):

| Trial | Behaviour observed | Delivery |
|---|---|---|
| 1 | native_catalogue (`probe.lookup`) | provider_accepted |
| 2 | text_contract | provider_accepted |
| 3 | unoffered-tool attempt — see below | provider_refused |
| 4 | unoffered-tool attempt — see below | provider_refused |
| 5 | native_catalogue (`probe.lookup`) | provider_accepted |

**The hybrid (trials 3–4).** The model emitted a **native tool call to a tool named `commentary`** — a channel name from the model's own response format — **whose arguments were the framework's text-contract JSON** (`{"tool_requests": [{"tool": "probe.lookup", …}]}`). Groq's validation refused delivery: "attempted to call tool 'commentary' which was not in request.tools", code `tool_use_failed`. A third collision shape, distinct from attempt 8's `container.exec`: not a reach for power, but the model's two languages fused in one generation — its native envelope carrying our text payload.

**What the measurement establishes.**
1. **Native works when offered:** 2 of 5 trials were clean native catalogue calls, correctly formed, in ~0.15 s. The channel Ben directed us to meet the model in is real and fast.
2. **The text contract also works** (1 of 5) — the model is genuinely bilingual, and *which* language it answers in varies generation to generation, exactly the variability Vane's INDEX 266 qualification predicted.
3. **Under the scope's own quorum rule, this distribution is INCONCLUSIVE:** 5 settled trials, no strict majority (native 2, text 1, unoffered-attempt 2) — so no mode recommendation. A single-trial probe would have concluded "native" from trial 1 alone and been wrong to conclude anything. **The quorum and the two dimensions earned their keep on first contact with reality.**
4. The probe suite as drafted **detects the hybrid only via the refusal body**; whether the hybrid classifies cleanly as an unoffered-tool attempt, or wants a named place in the suite (it is one call that is simultaneously native in form and text in content), is put to Vane with this evidence.

**Status:** a measurement, not a governed run — no assembly, no activation, no framework code. The probe piece's build remains gated on Vane's Rev 2 examination, which now has a real distribution to examine against.

**Provenance note (added 2026-11-23 at INDEX 277, at Vane's correction):** in the committed artifact, the `raw` field for trials 3–4 is the **helper's diagnostic output (its traceback string)**, which *contains* the provider's error body verbatim inside the RuntimeError message — it is not itself the raw HTTP response body. The classifications above rest on the provider's explanation as preserved in that diagnostic output. The probe scope's evidence model (Rev 3) distinguishes the exact provider error body, HTTP status/metadata, and helper diagnostics as separate retained objects, each hashed.
