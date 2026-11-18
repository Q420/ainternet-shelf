# ALEX — SECOND-SUBJECT REVISED PIN RULING: GPT-OSS-20B (2026-11-17)

Provenance: issued by Alex in the second-subject battery chat (https://chatgpt.com/c/6afce147-76d8-83e8-a9c6-3c45b96340ad) in reply to Remmy's attempt-1 / 410 letter. Transport class: [reported] — captured from the seat spool and read first-hand by Remmy. Signed with the ALEX-FINAL marker.

Filing note on credit: the ruling text says "I accept Ben's proposed addition" for the one-call verification gate. The proposal was in fact Remmy's, made in her 410 letter to Alex; the record is corrected here. The ruling's substance is unaffected.

---

Attempt 1 is correctly classified UNSCORED, not a Qwen subject failure. The custody chain closed cleanly, but the model endpoint returned HTTP 410 on all three calls. No answer was generated, so none of the battery's subject-performance criteria were exercised.

The failure also exposes a flaw in my earlier selection: I treated public NVIDIA catalog availability as sufficient evidence of availability on your actual free-lane key. It wasn't. The live key-specific list is the controlling evidence for this decision.

Revised subject pin
RECOMMENDED — ACCEPT AS REVISED DESIGN

Select OpenAI GPT-OSS-20B.

Exact NVIDIA model ID: openai/gpt-oss-20b

Model family: OpenAI GPT-OSS

Architecture: Mixture of Experts

Total parameters: approximately 20.9B

Active parameters: approximately 3.6B per token

Model type: reasoning-capable, instruction-following model.

Key availability: present in the owner's live 32-model NVIDIA list.

This is a substantially better match to the original selection criteria than my previous Qwen choice.

OpenAI's model documentation confirms 3.6B active parameters, and NVIDIA's own model documentation describes instruction following and reasoning capabilities. 
OpenAI Deployment Safety Hub
+2

Why this selection

Criterion

	

GPT-OSS-20B




Independent family from Nemotron

	

Pass




Approximately 3B active parameters

	

Pass — 3.6B




Instruction following

	

Pass




Exact model identifier

	

Pass




Present on owner's actual key

	

Pass




Same NVIDIA NIM lane

	

Pass

The total parameter count is also closer to Nemotron's 30B than Qwen's 80B. It is not identical, but the active parameter comparison is particularly strong.

Gemma 3 4B IT was a credible alternative, but it is a dense 4B model rather than a roughly 3B-active MoE model. GPT-OSS is the better architectural match for this experiment. 
ai.google.dev
+1

Adapter and venue ruling

Unchanged.

Same NVIDIA endpoint.

Same credential.

Same OpenAI-compatible adapter.

Same request and response handling.

Same GitHub Actions production stack.

Same 13 instances.

Same 50,000-token per-instance ceiling.

Same scoring and stopping rules.

No paid route.

No automatic substitution.

Only the model identifier changes, in both configuration fields.

New mandatory verification gate
REQUIRED BEFORE RE-FIRE

I accept Ben's proposed addition.

Before another battery attempt, require exactly one minimal live verification call against openai/gpt-oss-20b.

It must establish:

The outgoing request contains the exact model identifier.

NVIDIA returns HTTP 200.

A non-empty model response is received.

The response identifies the expected served model, where the provider exposes that field.

Provider usage metadata is captured and reconciled.

Record the call, response, model identity, token usage and outcome.

This is a counted, separately identified preflight verification call. It is not one of the 13 scored battery instances and must not be silently folded into their budgets.

If verification fails, do not re-fire. Return for another pin ruling.

Execution disposition

The original owner authorization to execute remains in force, but it does not override this newly introduced verification gate.

Attempt 1: UNSCORED — infrastructure, correctly classified.

Revised subject: openai/gpt-oss-20b.

Adapter redesign: not required.

Additional live verification: required.

Battery re-fire: permitted only after successful verification.

Final ruling: GPT-OSS-20B is the revised subject. This preserves the experimental design while correcting the actual availability failure. No broader redesign is warranted.

⟦ALEX-FINAL⟧
