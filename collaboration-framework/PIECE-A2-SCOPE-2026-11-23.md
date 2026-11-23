# Piece A2 — scope: grants and dispatch (agent layer)

**Date:** 2026-11-23. **Status:** scope for examination. Scoped from SPEC SHEET Rev 6 (R44–R48) after Piece A1's pass (INDEX 164), as A1 was scoped after the Rev 6 pair's acceptance. This scope authorises nothing; the build follows scope passage through the loop.

## What A2 builds

The doorway's **grant enforcement** and the **dispatch sequence**: an activated instance requests a tool; the doorway checks the request against the grants sealed in its assembly record; on a pass it records the dispatch intent; an executor performs the operation outside the record; the outcome — result, failure, or **uncertain** — is recorded against the dispatch. A1 carried grants as judged data (shape: `tool`, `scope_ceiling`, `side_effect_class`, `bound`, `authority_trace`); A2 makes them law.

## Design points proposed

1. **Vocabulary.** `TOOL_REQUESTED` (the instance, under its instance credential: tool, parameters, `request_id`, grant reference), `TOOL_DISPATCHED` (the dispatch intent with a unique `dispatch_id`, recorded by the doorway as mechanism on a passed check — the REJECTION-actor precedent of Piece 2), `TOOL_OUTCOME` (recorded by the executor through the doorway against the `dispatch_id`: result / failure / uncertain, with the result payload or its reference), `TOOL_RECONCILED` (an authorised act establishing an uncertain dispatch's outcome, with its evidence reference). A refused check is a recorded REJECTION naming the grant ground — never a silent failure (R55).
2. **The grant source is the sealed record.** The doorway checks against the grants in the instance's ASSEMBLY_GENERATED record as judged and packed (hash-bound, A1). A grant not in that sealed object does not exist for the doorway; nothing can be granted after pack except by a new assembly (A1's regeneration rule). The authority trace is judged for substance by the examiner at ASSEMBLY_JUDGED; mechanically, the doorway requires the trace present and the grant inside the sealed record — a grant without a valid trace never reaches dispatch because it could not have been judged and packed.
3. **Request identity and deduplication (R47).** `request_id` is assigned by the instance at first presentation and is stable per request. The doorway deduplicates on (instance, request_id): a retry — including one from an instance that never learned its dispatch_id — resolves against the existing dispatch state (the recorded dispatch and its outcome, when one stands) and never creates a second dispatch.
4. **Bound accounting.** A grant's `bound` counts dispatches. The charge lands at TOOL_DISPATCHED. No outcome releases it — a failure was still an execution, and an **uncertain outcome keeps the charge** until reconciliation, and reconciliation does not refund it either: the bound is a ceiling on attempts, not on successes. A request that would exceed the bound is refused and the refusal recorded.
5. **Scope ceilings, mechanically.** Each registered tool declares how its ceiling is checked: the grant's `scope_ceiling` is structured data whose constraint keys the tool's checker understands; unknown constraint keys fail closed. The doorway invokes the registry's checker for the named tool; an unregistered tool is refused. The registry is framework code, examined with this piece.
6. **The executor and the first tools.** A framework-side executor module (machinery, like the generator — no authority) performs dispatched operations and reports outcomes through the doorway. A2's registry is deliberately small and real: `sandbox.write` and `sandbox.read` against a per-run sandbox directory (ceiling = path prefix inside it; the side effect is a real file), and `sandbox.flaky`, a test tool whose behaviour (succeed / fail / hang-past-deadline) is set by its parameters, existing so uncertain outcomes are exercised for real, not asserted. Real shelf retrieval is A4's path, not A2's; the loop that calls all this conversationally is A3's.
7. **Uncertain outcomes (R46).** A dispatch whose execution times out or whose report never arrives is recorded `uncertain` — by the executor when it can attest the timeout, and the state is visible in the fold as its own dispatch state, distinct from result and failure. Resolution is only by TOOL_RECONCILED naming the established outcome and its evidence. Nothing downstream in A2 treats uncertain as settled; the continuation block itself is A5, but A2's fold exposes the state A5 will check.
8. **Replay safety (R48).** The fold and the checker reconstruct dispatch history from events only. The checker imports no executor and executes nothing — witnessed structurally, on the observer's no-doorway-import precedent. The checker gains a `dispatch_correspondence` check: sequence order per dispatch, one dispatch per request identity, bound accounting (dispatches never exceed the bound; uncertain still charged), outcomes only against standing dispatches, reconciliation only against uncertain dispatches.

## Not in A2

The conversational loop that generates requests (A3); shelf retrieval and search (A4 — sandbox tools only here); publication (A4); yield/termination/continuation, including the continuation block on unresolved dispatches (A5 — A2 supplies the state, A5 the gate).

## Acceptance sketch (tests to be written with the build)

- The happy path end-to-end: request → check → dispatch → execution → outcome recorded, the sandbox file really written, the outcome bound to the dispatch_id.
- A request for an ungranted tool, and one beyond its ceiling, and one past its bound: each refused, each refusal recorded, nothing executed.
- A retried request (same request_id) after dispatch produces no second dispatch and no second file write; a retry after outcome returns the standing outcome.
- The flaky tool hanging past its deadline records an uncertain outcome; the grant's charge remains; reconciliation establishes the outcome by an authorised act; a second reconciliation of a settled dispatch is refused.
- A grant absent from the sealed record (hand-appended history) is caught by the checker; a tampered dispatch history (outcome without dispatch, two dispatches for one request, dispatches over bound) is divergent under `dispatch_correspondence`.
- Replay executes nothing: the sandbox is byte-identical before and after a checker run over a history containing dispatches.
- All prior suites green.

## Questions for the examiner

(a) `TOOL_DISPATCHED` recorded by the doorway as mechanism (the REJECTION precedent) — right, or should dispatch intent be the executor's first act? (b) `TOOL_OUTCOME` attribution: the executor as machinery under its own actor identity, or under the orchestrator's token like the office's acts? (c) `TOOL_RECONCILED`'s authorised actor: orchestrator, examiner, or either-with-evidence? (d) Ceiling checking via per-tool registry checkers vs a small generic constraint language the doorway interprets itself?

*End of Piece A2 scope.*
