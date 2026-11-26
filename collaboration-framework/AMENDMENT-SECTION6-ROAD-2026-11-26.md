# AMENDMENT — Plan §6 (The Road), 2026-11-26

**Status:** DRAFT for the examiner. Ordered by Ben, 2026-11-26 01:33 MST
("Implement it"), on the strength of the research brief of the same night
(`agent-token-budgeting-practices`, research notes 2026-11-26). This paper
amends §6 of `PLAN-OFFICE-CYCLE-2026-11-25.md`. It changes nothing until
the examiner has examined it and Ben rules. The §6 accounting fix built
earlier tonight (the budget binds the whole rendered request) stands as
built; this amendment decides what replaces the regime it corrected.

**Ben's words for why:** "What we're doing over and over isn't working.
I have to know when to let the outside influence me."

---

## 1 · What §6 currently rules, and what the night showed

§6 as approved: a per-call budget — no single request may exceed 4,000
estimated tokens, estimated as ceil(bytes ÷ 4) — designed against the
proven 8,000 tokens-per-minute (TPM) limit on the Groq route, so that two
calls colliding in one minute cannot cross it. The opening is designed to
the budget first; the 65-second operating pacing stands as the interim
pacing rule.

Three findings, all measured first-hand:

1. **The build counted less than the request.** As originally built, the
   estimate covered the package's committed core only; the contract
   framing and, in native mode, the tool definitions rode uncounted.
   The accounting fix (Remmy's hands, 2026-11-26, verified: adapter,
   loop, probe suites pass; door 69/69; combined 49/49) now estimates
   over the adapter's rendered request. Under the corrected accounting
   the rehearsal's cycle-honest scenario stalls at zero iterations —
   its v1-era opening is over budget on the whole wire — and passes
   525/525 with the new method removed. The fix is honest; the regime
   it serves is the question.

2. **The live walk exceeds the cap in its normal course.** demo-gptoss11's
   own call ledger (wire estimates from captures): opening 2,748 —
   inside. Second call **5,735** against a package estimate of 532 — a
   cycle call carrying a block's content. Third call 2,764 against a
   package estimate of 3,596. Under the corrected accounting, the
   standard cycle walk refuses at its second call.

3. **The cap is not how the field handles TPM.** The research brief
   (sourced, 2026-11-26) establishes the standard stack:
   - TPM is a **per-minute bucket across all requests** (input + output),
     not a per-request size limit. The standard mechanisms are pacing
     (a token bucket that reserves counted tokens and waits for refill)
     and SDK retry with exponential backoff honouring Retry-After.
     A per-request token cap appears in none of the mainstream
     frameworks surveyed (LangChain/LangGraph, CrewAI, AutoGen,
     OpenAI Agents SDK, Anthropic's published guidance).
   - Counting is done with a **model-matched tokenizer** (e.g. tiktoken
     via `encoding_for_model`) or a **provider counting endpoint**
     (Anthropic's `count_tokens` accepts the full structured request —
     system, tools, history) over the **whole assembled request**,
     with per-message overhead added. Bytes÷4 is a labelled fallback,
     and it fails worst on this workload: measured ratios are ~4.98
     chars/token for English prose but **2.11 for JSON**, 2.10 CSV,
     1.55 for hashes — our packages and tool results are JSON, so the
     estimator undercounts them by roughly half.
   - **Large tool results are capped at the tool boundary**: the full
     content spills to a file; the context receives a path plus a short
     preview, re-read on demand (Deep Agents: spill above 20,000
     tokens; Claude Code: MCP results above 25,000 tokens saved to a
     session file and replaced with a reference). Just-in-time
     retrieval — paths, search, bounded reads — replaces inlining.
   - A **running total** is maintained, with an automatic shedding
     ladder as context grows: clear old tool results → trim oldest
     messages → summarize/compact old history, recent material kept
     verbatim (Anthropic context editing defaults: clear tool uses at
     100k input tokens keeping the last 3; compaction at 150k).

## 2 · The amendment — §6 rewritten

Replace §6's per-call budget regime with the standard stack, in five
parts. Everything else in the plan stands.

**A. Counting.** Requests are counted, not estimated from bytes, wherever
a counting route exists for the occupant's model: a tokenizer matched to
the model, applied to the whole rendered request (the rendered-request
construction built tonight is the input), or the provider's counting
endpoint where one exists. The provider's own usage figures, where a
response carries them, remain the retrospective record and govern. The
bytes÷4 estimator is retained only as a labelled fallback for a route
with no counting route, and any figure it produces is named an estimate
wherever it stands. Per-message overhead is counted where the route's
accounting charges it.

**B. Pacing replaces the cap.** The per-call token budget (4,000) and
its refusal gate are **retired**. In their place: a minute-bucket
pacing rule — before each call, the loop accounts the counted tokens
of the request plus a reserved output allowance against the route's
TPM budget for the current minute and waits for the bucket rather
than refusing. The existing 65-second operating pacing stands until
the measured figures under the new counting replace it, per §6's
original "measured before paced" rule, which is retained. A run-level
token budget (against the route's daily pool — Groq's rolling
200,000 TPD, proven 2026-11-25) is a separate, legitimate budget and
may be sealed per run; it is a property of the run, not of any call.
The budget-refusal event and its record remain in the doorway for the
contracts that already carry them; no new contract issues them.

**C. Tool results spill.** A tool result whose counted size exceeds a
sealed threshold does not ride into the next package whole: its full
content is written to the room (it already stands in the record), and
the package carries a reference — the result's identity, its size,
and a bounded preview — with re-reading available through the existing
pull machinery in bounded slices. The cycle's block presentation is
re-based on this rule: a block's content is presented in slices sized
by counted tokens, not by the 12,000-byte line ceiling alone. The
threshold figure is the examiner's to propose at assembly from the
route's measured figures; this paper names the mechanism, not the
number.

**D. Running total and shedding.** The loop maintains a running counted
total of the working context and applies the ladder before a call
would carry the context past a sealed fraction of the model's window:
clear spent tool results first (their contents stand in the record),
then trim the oldest cycle material, then summarize — the journal is
the summary's standing home, which is what it was designed to be.
Nothing is shed that the record does not already hold.

**E. The report.** The run's report continues to state each call's
figures — now counted tokens beside the provider's returned usage —
and adds the pacing record: waits taken, bucket state at each call,
and any shedding applied. The call ledger's wire estimates are
superseded by counted figures where counting stood.

## 3 · What this does NOT change

- The opening's shape, the cycle's file-as-work-unit design, the
  delivery contract, the delivery floor, the ten sealed grants, the
  working-set carriage ceiling — untouched. This amendment is the
  road only: how requests are counted, paced, and kept lean.
- Composition competence remains untested; this amendment does not
  claim otherwise. A run under the new road proves the road, and
  whatever else it proves is stated separately.
- The platform safeguard named in the standing briefings is untouched
  and unaddressed by this paper, as before.

## 4 · What will still be wrong if this works perfectly

Pacing and counting make calls legal and honest; they do not make the
worker good. The known unproven matters stand exactly where they
stood: composition across a whole job, the blind handoff, A5/A6. The
new road also spends the daily pool faster per run if calls grow —
the run-level budget (B) is the guard, and it is a guard, not a fix.

## 5 · Acceptance, in Ben's terms

A proof run under the amended road, on the Groq GPT-OSS seat, in
which: the worker is woken once, pulls all three sources through the
spill-and-reference machinery, and files a brief meeting the delivery
floor — with **no call refused for size**, every call's counted
tokens in the report, pacing waits visible in the ledger, and the
run's total counted spend inside its sealed run budget. The rehearsal
suite re-based to the amended road passes whole, cycle-honest
included, before the live run is attempted.

## 6 · Questions put to the examiner

1. The spill threshold (C) and the shedding fraction (D): figures to
   propose at assembly, or figures this paper should carry?
2. The budget-refusal machinery: retire from new contracts as
   proposed, or retain as a sealed option a contract may still elect?
3. The run-level budget (B): sealed by the office at stocking, or
   declared per run in the opening's grounds?
4. Counting for the Groq GPT-OSS seat specifically: which counting
   route does the examiner accept as matched to that model, given
   the provider returns usage figures retrospectively?

— Remmy, 2026-11-26. Drafted at Ben's order; the shelf copy is the
transport; examination invited first-hand.
