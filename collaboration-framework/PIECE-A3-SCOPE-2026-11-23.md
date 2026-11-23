# Piece A3 scope — the bounded loop (R49–R51)

**Date:** 2026-11-23. **Status:** scope for examination. **Basis:** SPEC SHEET Rev 6, R49–R51 and COLLABORATION Rev 6 §8, read first-hand; grounded in the built adapter (Piece 8), the seat driver (Piece 4), and the A2 dispatch machinery as passed. **Authorises nothing by itself**; implementation is confined to A3 if the scope passes. A1 gave an instance an identity; A2 gave it hands. A3 gives it the working loop: perceive → act → see the result → act again, inside bounds, until it yields or is stopped by the record.

## Where the loop sits

- A **new module, `src/framework/loop.py`** — the runtime for generated instances. The seat `Driver` (Piece 4) is seat-bound: it wakes on recorded reasons, once per wake. The loop is **activation-bound**: it starts when an instance is activated (A1) for its part and runs iterations until the instance yields, declines, or a bound stops it. The seat driver is untouched.
- The loop is machinery, never an authority (§8): a model requesting a tool does not authorise it (A2's doorway check does); the loop reporting success does not establish completion (the record does).
- The loop depends on a **narrow model-callable contract** — package in, typed outcome out — which is the adapter's existing `__call__` signature, extended (§3 below). A scripted fake model implements the same contract in tests (Pieces 4/8 precedent). No contract term — identity, grants, record acts, retrieval rules, lifecycle — lives in the callable (R51): substituting the runtime changes nothing the checker or the doorway enforces.

## The iteration

1. **Package.** Each iteration presents: the case view (as the driver builds it, boundary-narrowed per R11), the **new record state** since the loop's last presented position (the record delta, not a re-send of history), the **tool results** settled since the last iteration (each against its dispatch identity, including uncertain outcomes presented *as* uncertain), the **standing dispatch states** for this instance, and the **bounds state** (steps used / ceiling, time remaining) — the bounds live in the case (§8), so they are already the instance's own knowledge; the loop states them per iteration so no iteration proceeds on a stale picture.
2. **Response.** The instance responds with any mix of: **record acts** (the existing proposal vocabulary), **tool requests** (new, §3), a **yield** response, or a **decline**. Whole-response strict validation, per the adapter's established pattern: unknown fields, mixed malformed entries, or an unparseable answer fail the iteration as a whole — nothing partial takes effect.
3. **Adjudication before effect.** Every record act in the response goes through `doorway.act` under the instance's credential (A1: instance credentials authenticate while the fold derives "active"; acts bind to the seat the instance fills, provenance-stamped with the instance_id, as A2's TOOL_REQUESTED established). Every tool request goes through A2's `doorway.request_tool` and, on dispatch, the executor; the loop never executes a tool itself and never retries a request on its own motion (R47: a retry resolves against the standing dispatch).
4. **Step.** One iteration = one model call and the adjudicated effects of its response. The step ceiling counts iterations per activation.

## The adapter extension

- The response vocabulary gains two typed outcomes beside acknowledge / contribute / decline: **`tool_requests`** — a list of `{tool, parameters}` entries (request identity per question (b) below); and **`yield`** — the instance declares its bounded work done, with its own summary text (strict: yield carries its summary and nothing else). Record acts continue to ride the proposals outcome, unchanged.
- The A6 discipline carries over and tightens: the adapter's per-call deadline is set from the **activation's remaining budget**, computed by the loop at each iteration — never a fresh per-call allowance. A call that would start after the activation deadline does not start.

## Bounds and the recorded stall (R49, R50)

- **Bounds live in the case** (§8's words): the issued case content for the instance's part carries `loop_bounds: {step_ceiling, deadline_seconds}`. An instance whose case carries no bounds **cannot loop** — fail closed; there is no default bound. (Placement is question (a).)
- The total deadline is per **activation**: it starts when the loop starts for that activation and governs every phase of every provider call and every dispatch decision inside it.
- **Reaching a bound without a yield act is a recorded stall** (R50): a new event kind **`LOOP_STALLED`**, extending the DRIVER_FAILURE pattern — recorded when (i) the step ceiling is reached, (ii) the activation deadline expires, (iii) a provider/adapter failure ends an iteration, or (iv) a response is malformed — each with its **ground** named in the payload, the iteration count, and the instance/case binding. A stall is a fact in the record, never a silent stop; after a stall the loop does not resume for that activation (a fresh activation is a new assembly's business, A1/A5).
- A **decline** is not a stall: following Piece 8's precedent (decline = a structured non-act), a decline ends the loop and is reported to the loop's caller as its outcome, unrecorded. (Question (c).)
- **In-flight dispatches at a bound:** the loop starts no new iteration, request, or dispatch after the deadline; a dispatch already executing settles under A2's own rules and its outcome stands as recorded — if uncertain, it stands uncertain, visible in the record for A5's yield accounting. The stall is recorded once the loop is quiescent or the executor's own accounting closes, whichever the examiner settles. (Question (e).)

## Record completeness (R55, this piece's increment)

- New event kind: `LOOP_STALLED` (fold + both projection-schema copies + checker), with the checker's correspondence: a stall names a standing activation, its ground is one of the settled set, its iteration count does not exceed the case's ceiling, and no instance act, request, or dispatch for that activation follows a stall.
- **Iteration accounting** is question (d): either a `LOOP_ITERATION` bookkeeping event per iteration (recorded by the loop as machinery, on the executor-identity precedent), or the checker derives iteration counts from effects + the stall record. The scope's recommendation is the bookkeeping event: an iteration whose response produced no record effect (all acts refused are REJECTIONs — visible; but a yield or a pure tool-request response leaves only dispatches) should still be countable against the ceiling from the record alone, since the record is the only account of the instance's acts.
- Replay executes nothing, as everywhere: the fold and checker read recorded outcomes only (R48).

## Working memory

The loop's context — the packages it built and the responses it received — is a local object held by the loop for the activation's duration and **dropped when the loop returns**; no module-level state, nothing persisted outside the record. Its disposal as *evidenced* termination is A5's scope (R54); A3's obligation is the construction: nothing exists to inherit.

## Questions for the examiner

(a) **Bounds placement.** Design §8 says bounds "live in the case." The grants live in the sealed assembly record (A2). Do the loop bounds ride the issued case content (office-issued, per part), as scoped — or belong in the assembly record beside the grants, with the case view presenting them? The scope follows the design's words; flagging that the two placements differ in who can change them mid-run (a case correction could move a bound; a sealed record cannot).

(b) **Request identity in the loop.** A2 binds a stable `request_id` at first presentation. In the loop, who assigns it: the instance (model-supplied, preserved verbatim across its retries), or the loop (deterministic per instance + iteration + ordinal, so a response re-presented after a lost outcome resolves against the standing dispatch by construction)? The scope leans loop-assigned: the model cannot be relied on to repeat an identity exactly, and R47's "retry from a worker that never received its dispatch identity" is met structurally if identity never depends on the model's memory.

(c) **Stall taxonomy and the decline.** One `LOOP_STALLED` kind with a `ground` field over the settled set {step_ceiling, deadline, provider_failure, malformed_response} — or distinct kinds per ground? And the decline: caller-reported non-act (as scoped, Piece 8 precedent) or recorded?

(d) **Iteration accounting.** `LOOP_ITERATION` bookkeeping events recorded by the loop as machinery under a distinct constrained identity (the executor precedent from A2: reporting only, against standing activations) — or derivation from effects? If bookkeeping events: is the loop's reporting identity distinct from the executor's?

(e) **Stall timing with an in-flight dispatch.** When the deadline expires mid-dispatch: stall recorded immediately (the dispatch's later outcome then follows a stall — the checker correspondence above forbids instance acts after a stall, but an executor outcome is not an instance act), or stall recorded after the executor's accounting closes for that dispatch?

## Acceptance tests (all against scripted fake models + the real doorway/executor; the A2 sandbox registry is the tool set)

- A worker that writes, reads the result back in its next package, and yields — the read package's tool result is the write's recorded outcome (uptake inside the loop, witnessed from the record).
- Step ceiling: a worker that never yields stalls at exactly the ceiling; `LOOP_STALLED` stands with ground step_ceiling; no iteration beyond it.
- Deadline: a slow provider call is governed by the activation's remaining budget, not a fresh allowance; expiry stalls with ground deadline.
- Tool sequence end-to-end per R45 inside the loop; a refused grant inside a loop response records its REJECTION and the loop continues (a refusal is information, not a crash).
- An induced uncertain outcome is presented to the instance *as* uncertain in the next package; the instance may yield with the uncertainty standing (A5 accounts it; A3 does not reconcile).
- Malformed response → stall, ground malformed_response, nothing partial in effect. Provider failure → stall, ground provider_failure.
- Decline ends the loop as a caller-reported outcome; no stall stands.
- A case without `loop_bounds` cannot loop: refused before the first model call, nothing recorded but the refusal path the examiner settles.
- Checker: `loop_correspondence` verifies stall bindings, grounds, ceiling arithmetic, and no post-stall instance activity; the two schema copies agree; replay executes nothing (structural witness, as in A2).
- Runtime replaceability: the same scripted scenario runs against a second trivial loop client implementing the contract, with identical record effects (R51).

## Not in this piece

Retrieval, skills, and publication (A4: R41–R43, R52–R53 — the loop presents the case view and tool results only; no retrieval path exists yet for the loop to present). Yield/termination recording and continuation (A5: R54 — the yield *response* ends A3's loop; the yield *act* and the two deaths are A5's). The blind-handoff demonstration (A6). Live provider runs (a live A3 demonstration is Stage 3's business, chosen with Ben).
