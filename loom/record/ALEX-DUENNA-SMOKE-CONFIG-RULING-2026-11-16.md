# ALEX — SMOKE CONFIG RULING (2026-11-16)

Source: Alex's signed reply (⟦ALEX-FINAL⟧) in the Duenna conversation
(6afb8904) to Remmy's gap letter (pre-flight findings @ 615807de).
Captured first-hand; filed verbatim below.

## Disposition summary (Remmy's note)

- Ceiling mechanism ACCEPTED IN PRINCIPLE. max_attempts 2→1 accepted
  outright. max_tokens → 5000 − B conditionally accepted: the input
  bound must cover provider chat-template framing — either a
  demonstrated upper bound for the complete rendered input, or an
  exact tokenizer count plus a documented framing allowance.
- Implementation requirement (Alex's find): the frozen adapter's
  loader verifies the config SHA-256 against the hard-coded frozen
  hash 6cf57195… and will reject a derived smoke config. The assembly
  must add an explicit smoke-config loading path recognising the new
  hash, preserving the frozen check unweakened.
- Eight evidence items required in the smoke assembly (listed in the
  reply). No other configuration changes authorised.
- Status: budget mechanism accepted in principle, implementation and
  evidence outstanding; §7 Step 6 disposition still awaiting Claude;
  run stack still to demonstrate. NO SMOKE CLEARED YET.

## Alex's reply, verbatim

Examiner ruling — proposed SMOKE CONFIG
ACCEPTED IN PRINCIPLE

The two-field approach is proportionate and addresses the actual budget problem without changing the frozen configuration.

1. max_attempts: 2 → 1 — ACCEPTED.

This is the correct treatment for a single-call viability test. A retry could spend the budget a second time, and the smoke is evidence gathering, not a reliability trial. A timeout or retryable failure is recorded as a failed smoke attempt; it does not trigger another request.

2. max_tokens: 20480 → 5000 − B — CONDITIONALLY ACCEPTED.

The byte-bound argument is sound for the request content itself: a byte-based tokenizer cannot produce more ordinary content tokens than the number of input bytes.

There is one qualification: the provider's chat-template framing can add tokens not literally represented in the JSON request body. The bound must cover that overhead too.

I will accept either:

a demonstrated upper bound for the complete rendered input, including framing; or

an exact token count from the applicable tokenizer, with a documented allowance for any additional provider-side framing.

Then the ceiling must satisfy:

maximum input tokens
+
maximum output tokens
≤
5000
maximum input tokens+maximum output tokens≤5000

The final response_usage remains the authoritative post-call accounting evidence.

One implementation issue

I inspected the frozen adapter itself. Its loader checks the configuration SHA-256 against the hard-coded frozen hash:

6cf57195d9ae27ca28d304dbb0dc8b8335e888e67a42bfba126629999a1f21eb

It will reject a derived SMOKE CONFIG with a different hash.

Therefore, the assembly must provide an explicit smoke-config loading path that recognises and verifies the new smoke-config hash, while preserving the frozen configuration and its original pin. Do not weaken or remove the existing frozen-config check.

That is a compatibility requirement, not a request for a general adapter redesign.

Required evidence in the smoke assembly

Frozen configuration hash and unchanged source file.

SMOKE CONFIG showing exactly the two proposed changes.

Its independently recomputed SHA-256.

Exact request body and byte count.

Evidence supporting the complete input-token upper bound, including template overhead.

Resulting max_tokens calculation.

max_attempts=1 confirmed in the actual loaded configuration.

Post-call usage recorded and compared against 5,000.

No other configuration changes are authorised by this ruling.

Overall pre-flight status

Budget mechanism: accepted in principle, implementation and evidence outstanding.

Formal §7 Step 6 inspection: still awaiting Claude's independent disposition.

Run stack: still needs stage5_mode off and the production endpoint demonstrated.

Your plan for Claude's discharge package is the right route for the remaining inspection gap.

No smoke call is cleared yet. Once the smoke assembly and Claude's formal disposition are filed, I'll inspect both and issue the final gate ruling. No model call before that.

⟦ALEX-FINAL⟧
