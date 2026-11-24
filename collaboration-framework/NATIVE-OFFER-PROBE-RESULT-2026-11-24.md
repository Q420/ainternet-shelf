# Native-offer probe — RESULT: split / inconclusive on the stated thresholds; the one delivered trial used the offered tool (2026-11-24)

Ran 2026-11-24 ~03:32 MST under the INDEX 338 release; driver exit 0. Recorded at INDEX 339. **Remmy verified first-hand** from the probe evidence artifact, including the retained provider bodies. The five authorised requests are spent; the probe stopped, as released. Output: `live-demo/native-offer-offer1/` (comparison.json + probe-evidence.json; evidence hash `375ded73…`; baseline `72f6297d…`, modified `0229b0f0…`, definitions `6f3331ac…`, differing paths `['tools']` — the admitted comparison, reproduced by the run itself).

## The trials
| Trial | Behaviour | Delivery | What stands in the record |
|---|---|---|---|
| 1 | **offered_tool_call** | provider_accepted (HTTP 200) | A native call to **`sandbox.list`** with well-formed arguments `{"path": "sources/stock-take.md"}` — one of the three offered granted tools, aimed at the first source document: the assignment's natural first step. |
| 2 | no_observable_behaviour | **provider_failed (HTTP 429)** | Rate-limit refusal body, complete: TPM limit 8,000, used 4,324, requested 4,533. |
| 3 | no_observable_behaviour | **provider_failed (HTTP 429)** | Rate-limit refusal, complete: used 4,262, requested 7,361. |
| 4 | no_observable_behaviour | **provider_failed (HTTP 429)** | Rate-limit refusal, complete: used 4,174, requested 4,533. |
| 5 | no_observable_behaviour | **provider_failed (HTTP 429)** | Rate-limit refusal, complete: used 4,100, requested 4,664. |

Settled 5 of 5 (evidence-complete). **Unoffered attempts: zero** — the shell-reach appeared in no trial (in four, no behaviour was observable at all, because the requests never reached the model).

## The reading — as stated in advance, unspun
Per the scope's thresholds (≥3 offered → locked-door supported; ≥3 unoffered → deeper-habit strengthened; else split), the result is **`split_inconclusive`**. Neither threshold is met, and this note does not dress the single delivered observation up as a verdict.

What the evidence does support, stated at its true weight:
- **The one trial that reached the model behaved exactly as the locked-door hypothesis predicts**: offered its granted actions natively, it picked one up and began the assignment — no shell-reach, no text-form, no malformed output.
- **The inconclusiveness is a delivery artifact, not model behaviour.** Trials 2–5 were refused by the provider's per-minute token budget (8,000 TPM, measured at INDEX 260) before any generation: each request carries ~4,500–7,400 tokens, and the runner fired all five inside one minute. **A build-side lesson, recorded against the probe, not the model:** the trial pacing took no account of a known budget that fits roughly one such request per minute. The evidence discipline did its part — every refusal body is retained whole and delivery is honestly recorded as failed.
- The five authorised requests are spent. A spaced repetition (trials paced against the TPM budget) is a new release decision — the examiner's, on this result — not a continuation of this one.

## For the examiner
Whether the single delivered observation plus the zero unoffered count justifies a paced re-run release, or whether the next step is the compatibility design scope on the strength of trial 1 weighed as one observation — that judgement is Vane's, and any further direction after hers is Ben's. The loop takes no further step on its own authority.
