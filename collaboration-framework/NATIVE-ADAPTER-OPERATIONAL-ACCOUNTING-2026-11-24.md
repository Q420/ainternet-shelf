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
documented context window (131,072 tokens) and the provider's byte-size refusal
(evidenced at 134,844 bytes, HTTP 413, attempt 6). A 7,979-token prompt is not
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
  treated as approximate). A refusal therefore happens **at admission, whole,
  before any generation or effect** — the cleanest failure the system has.
- **The window decays continuously:** retry-after figures of ~6–7 seconds to
  free a few hundred tokens show a sliding window, not a fixed minute reset.
  Under the standing pacing discipline (≥ 65 s between request starts), Used
  stands at ≈ 0 for each request — evidenced directly: the paced repetition's
  five requests were all admitted at exactly that spacing (INDEX 352).

## 3. CAP = 1's worst case under the corrected semantics

The worst-case next prompt remains **7,979 tokens** (4,388 measured fixed +
≈ 3,591 converted growth from a ceiling-sized 12,000-byte result; the
conversion labelled approximate, as before). Charged at admission:
Requested ≈ 7,979 × 1.033 ≈ **8,242 > 8,000** — **refused at admission, even
in a fresh window.** The same result holds on the additive reading
(7,979 + 145 = 8,124). So at the absolute worst case the request does not run:
it is refused whole, before generation, recorded as a delivery failure, and
the work rolls over to the next agent with the record intact — precisely the
failure mode Ben's ruling accepts, now demonstrated rather than asserted.

The refusal zone is narrow. Admission in a fresh window needs Requested
≤ 8,000, i.e. a prompt of ≈ 7,744 tokens, i.e. a result content of
**≈ 11,000 bytes** at the measured conversion. Results from 0 to ~11,000 of
the 12,000-byte ceiling are admitted; only the top ~1,000 bytes of the
permitted result range lands in the refusal zone. (Approximate, as the
conversion is approximate; the zone's existence and rough size are robust
across the conversion's plausible range.)

## 4. Completion and concurrent-usage accounting

- **Completions are small in this work's evidenced range** — 69 and 81 tokens
  for tool-call responses (provider usage, paced trials 1–2; reasoning tokens
  are counted inside completion tokens). The largest completion the standing
  assignment can produce is the composition itself, bounded by the assignment
  at ~600 words (≈ 800 tokens plus reasoning).
- **Completions enter the window's Used for subsequent requests** (the
  evidenced Used figures sit at the scale of one prior request's total), and
  the ≥ 65 s pacing decays Used to ≈ 0 before the next request — so
  completions do not compound across a run's iterations. Admission of the
  current request is charged on Requested (prompt-based, §2), before its
  completion exists.
- **Concurrent usage:** this accounting holds under the programme's standing
  operating condition — one run at a time on this account, requests strictly
  sequential. No other traffic shares the window during a run. Stated as a
  condition, not assumed away.

## 5. The safety claim, restated honestly

CAP = 1 is safely governed not because a worst-case request fits inside a
per-request envelope — there is no such envelope at 8,000 — but because:

1. the per-request bounds that do exist (context window; byte size) are an
   order of magnitude above anything this construction produces;
2. the rate window refuses oversize requests **at admission, before any
   effect**, and the refusal is a recorded delivery failure under the
   standing evidence discipline — never a disguised success;
3. the refusal zone is only the top ~1,000 bytes of the permitted result
   range, under a pacing discipline that gives every request a fresh window;
4. resumption is the briefcase's designed function: the record carries the
   work's exact state, completed side effects are not replayed (dispatches
   are recorded before effects and checked on continuation, per the standing
   record design), and the next agent finishes the task — Ben's rollover.

That is the whole accounting. The build waits on the examiner's word.
