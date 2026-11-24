# OPERATIONAL ACCOUNTING — CAP = 1 UNDER THE ACTUAL PROVIDER LIMITS (2026-11-24)

Prepared for the examiner's remaining question on the build brief Rev 4
(INDEX 380): demonstrate that CAP = 1 is safely governed by the actual provider
limits, including completion and rate-window accounting. Ben's ruling and
CAP = 1 are preserved throughout; nothing here changes the cap, the retrieval
ceiling, or the margin.

## 1. The premise, corrected

The examiner is right, and the brief's phrasing is corrected by this accounting:
**8,000 TPM is an organization-level per-minute rate limit, not a per-request
prompt maximum.** The per-request bounds are different quantities: the model's
documented context window (131,072 tokens), and one observed byte-size
refusal point (HTTP 413 at 134,844 bytes, attempt 6) — an observed point,
not a proven maximum request-body size. A 7,979-token prompt is not
"inside a hard per-request envelope," and §3's sentence to that effect is
withdrawn (brief Rev 5 note). What governs a large request in practice is the
rate window's **admission accounting**, which the account itself states —
next section.

## 2. The account's own limit configuration, from its own statements

Two retained refusal bodies, issued by this account (organization
`org_01jjsrdxw8fr2vg66v1e8p6wef`, service tier `on_demand`, model
`openai/gpt-oss-120b`):

- "Rate limit reached … on tokens per minute (TPM): **Limit 8000, Used 4324,
  Requested 4533**. Please try again in 6.4275s." (native-offer run, trial 2)
- "… Limit 8000, **Used 4152, Requested 4798**. Please try again in 7.125s."
  (P2 run, trial 1)

Established from the account's own mouth, not the published table:

- **Admission test:** a request is refused when **Used + Requested > 8,000**,
  where Used is the window's consumption so far and Requested is the charge
  the provider computes for this request at admission, **before generation**.
- **Requested ≈ the prompt, plus a small provider-side allowance:** for the
  request whose prompt the provider's own usage later measured at 4,388
  tokens, Requested was 4,533 — a ratio of ≈ 1.033 (one evidenced sample;
  treated as approximate). A **TPM admission refusal** therefore happens
  **at admission, whole, before any generation or effect** — the cleanest
  failure the system has. The qualification is deliberate: that timing is
  established for refusals under the TPM admission test described here, not
  for every provider refusal whatever its cause — a 413 or a 400 has its
  own shape. The rollover contract (§5) covers provider refusals generally
  without claiming they all occur before generation.
- **The window decays continuously:** retry-after figures of ~6–7 seconds to
  free a few hundred tokens show a sliding window, not a fixed minute reset.
  Under the standing pacing discipline (≥ 65 s between request starts), the
  residual Used at each request is treated as ≈ 0 — **an operating
  assumption, not a measurement.** The evidence supports the assumption
  without proving it: the paced repetition's five requests were all admitted
  at exactly that spacing (INDEX 352), but five admissions expose no residual
  Used value, and the only Used figures in evidence are the provider-reported
  ones inside refusal bodies (4,324 and 4,152, §2 above). If the assumption
  fails on some request — residual Used higher than expected — the
  consequence is an admission refusal, which is the contract's recorded
  delivery failure (§5), not a breach of it.

## 3. CAP = 1's worst case under the corrected semantics

The worst-case next prompt remains **7,979 tokens** (4,388 measured fixed +
≈ 3,591 converted growth from a ceiling-sized 12,000-byte result; the
conversion labelled approximate, as before). Charged at admission on the
§2 model: Requested ≈ 7,979 × 1.033 ≈ **8,242 > 8,000** — so the model
**predicts refusal at admission, even in a fresh window**. The same
prediction holds on the additive reading (7,979 + 145 = 8,124). Stated
accurately (examiner's corrections, INDEX 382/385): this refusal is a
**credible, evidenced hypothesis**, extrapolated from one admission
sample — not a demonstrated fact. In conditional form, what the prediction
says is: *if* the model holds at the worst case, the request does not run —
refused whole, before generation, recorded as a delivery failure, and the
work rolls over to the next agent with the record intact, the failure mode
Ben's ruling accepts. The safety does not depend on the prediction: if the
worst-case request were admitted instead, its estimated prompt would sit
well inside the documented context window (131,072) — the prompt's fit is
what that comparison supports; the completion's length is bounded by no
configured ceiling (§4, A3), and its tokens would enter the window's Used,
which the pacing assumption in §4 addresses. Either branch
is inside the contract; the hypothesis only predicts which branch the
worst case takes.

On the same model, the predicted refusal zone is narrow. Admission in a
fresh window would need Requested ≤ 8,000, i.e. a prompt of ≈ 7,744 tokens,
i.e. a result content of **≈ 11,000 bytes** at the measured conversion — so
results from 0 to ~11,000 of the 12,000-byte ceiling are predicted admitted,
and only the top ~1,000 bytes of the permitted range is predicted to land
in the refusal zone. The zone is a prediction from the same extrapolation,
not a demonstrated boundary between admitted and refused results; its rough
size is robust across the conversion's plausible range, its exact edge is
not measured.

## 4. Completion and concurrent-usage accounting

- **Completions are small in this work's evidenced range** — 69 and 81 tokens
  for tool-call responses (provider usage, paced trials 1–2; reasoning tokens
  are counted inside completion tokens). The largest completion expected is
  the composition itself: the assignment *requests* ~600 words (≈ 800 tokens
  plus reasoning). That is a requested output size, **not a bound** — the
  construction sets no completion-token ceiling (no `max_tokens` anywhere in
  the adapter, loop, probe, or harness), so the figure stands as an operating
  expectation, and an unexpectedly long completion would simply consume more
  of the window's Used for subsequent requests, under the assumption below.
- **Completions enter the window's Used for subsequent requests** (the
  provider-reported Used figures sit at the scale of one prior request's
  total). Whether the ≥ 65 s pacing returns the residual Used to ≈ 0 before
  the next request is the operating assumption stated in §2 — under it,
  completions are not expected to compound across a run's iterations, but
  non-compounding is an expectation under an assumption, **not an established
  fact**. Admission of the current request is charged on Requested
  (prompt-based, §2), before its completion exists.
- **Concurrent usage:** this accounting holds under the programme's standing
  operating condition — one run at a time on this account, requests strictly
  sequential. No other traffic shares the window during a run. Stated as a
  condition, not assumed away.

## 5. The safety claim, restated honestly

CAP = 1 is safely governed not because a worst-case request fits inside a
per-request envelope — there is no such envelope at 8,000 — but because:

1. the estimated prompt sits comfortably inside the one documented
   per-request bound — the 131,072-token context window — and the worst
   case's serialized size sits comfortably below the one observed byte-size
   refusal point (134,844 bytes): comparisons that establish the prompt's
   fit, not that everything the construction produces necessarily fits —
   the completion is a separate quantity (point 2);
2. on the evidenced admission model, an oversize request is predicted to
   be refused **at admission, before any effect** (hypothesis, §3) — and a
   refusal, whenever it occurs, is a recorded delivery failure under the
   standing evidence discipline, never a disguised success; if the request
   is admitted instead, its prompt fits as compared in point 1 — but
   admission guarantees nothing about the completion: with no configured
   completion ceiling, the completion remains subject to the provider's
   own limits and observed response disposition, and any resulting refusal
   or incomplete response is handled under the same evidence and rollover
   rules;
3. the predicted refusal zone is only the top ~1,000 bytes of the
   permitted result range (§3 — a prediction, not a demonstrated boundary),
   under a pacing discipline that operates on the residual-Used assumption
   of §2, whose failure, if it comes, arrives as an admission refusal: a
   recorded delivery failure under point 4's rollover contract;
4. resumption is the briefcase's designed function: the record carries the
   work's exact state, completed side effects are not replayed (dispatches
   are recorded before effects and checked on continuation, per the standing
   record design), and the next agent finishes the task — Ben's rollover.

That is the whole accounting. The build waits on the examiner's word.
