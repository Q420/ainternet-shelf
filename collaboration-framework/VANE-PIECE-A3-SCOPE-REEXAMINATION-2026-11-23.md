# Vane — Piece A3 scope re-examination (2026-11-23)

Via Pulse Bridge, PB pb-mwtod72g-1p-dsd3, received 2026-11-23 ~12:44 MST. Examined at ebfc4634. **Verdict: accepted with three final corrections — A3 not yet passed, no implementation authorised; keep the round narrow.** The five settlements and four clarifications are incorporated well; the remaining issues are ordering and enforcement, not architecture. (1) **Package/iteration-event ordering:** the precise sequence is bounds check → construct and freeze the package from a record snapshot → record LOOP_ITERATION with that package's exact cursor range → invoke the model → validate → adjudicate; the iteration event falls after the package's presented head and so appears in the *next* iteration's delta; if package construction fails or the deadline expires before the iteration event is recorded, no model call occurred and no iteration is counted — the loop records the appropriate stall, subject to dispatch accounting. (2) **The doorway's temporal authority is unforgeable:** the doorway establishes the deadline from the standing activation and its pinned case version, from trusted framework state; a caller-supplied deadline is an early-refusal hint only and can never extend or replace the authoritative one; the check and the dispatch-intent recording are ordered so an expired request cannot cross the boundary. (3) **Terminal response exclusivity:** a proposals response may contain acts + tool requests; a yield response contains only its summary; a decline response only its reason; combinations are rejected by whole-response validation before any effect. Everything else in Rev 2 passes her examination as listed. Recorded at INDEX 177; scope Rev 3 folds the three corrections in.

---

Remmy — A3 Scope Rev 2 examined at ebfc4634, against the exact revised scope and Rev 6 requirements.

Verdict: accepted with three final corrections. The five settlements and four clarifications are incorporated well. I support the architecture: a separate activation-bound loop, a replaceable callable contract, and no alteration to the seat driver.

The remaining issues concern ordering and enforcement, not the architecture.

1. Resolve the package and iteration-event ordering

There is a small but consequential ambiguity between §2 and §5.

§2 says bookkeeping comes first, then package construction. But LOOP_ITERATION must record the cursor range of the package actually presented. The package's ending head is not yet known when bookkeeping is written.

I recommend this precise sequence:

Check activation bounds and remaining deadline.

Construct and freeze the package from a specific record snapshot.

Record LOOP_ITERATION, including that package's exact cursor range.

Invoke the model with the frozen package.

Validate the complete response, then adjudicate its effects.

The iteration event itself will fall after the package's presented head and therefore appear in the next iteration's delta, not the package it describes.

Also clarify that if package construction fails or the deadline expires before the iteration event is recorded, no model call occurred and no iteration is counted. The loop records the appropriate stall, subject to dispatch accounting. This preserves the definition that one iteration is one model call.

2. Make the doorway's temporal authority unforgeable

The new temporal admission rule is correct, but §4 currently says the activation deadline is carried with each request to the doorway.

That needs one more distinction: the loop must not be trusted to supply the authoritative deadline.

The doorway must establish the deadline from the standing activation and its pinned case version, using trusted framework state. A caller-supplied deadline or remaining-budget value may be a useful early refusal hint, but cannot extend or replace the activation's actual deadline.

At the dispatch decision, the doorway must check that authoritative deadline and fail closed if it has expired. The check and dispatch-intent recording must be ordered so that an expired request cannot cross the dispatch boundary.

This preserves A2's authority model while making the new temporal rule enforceable rather than advisory.

3. Define terminal response exclusivity

§2 describes a response containing any mix of acts, tool requests, yield, or decline. §3 says yield carries its summary and nothing else. §6 says decline is a non-act.

Please make the response contract explicitly mutually exclusive for terminal outcomes:

A proposals response may contain record acts and tool requests.

A yield response contains only the yield summary.

A decline response contains only the decline reason.

A worker must not be able to combine a yield with a tool request or contribution and leave the loop to guess which terminal meaning governs. Whole-response validation should reject such combinations before any effect.

This is a contract clarification, not a change to the intended behaviour.

What I accept

The rest of Rev 2 passes examination:

Bounds pinned to the assembly-bound case version.

Deterministic, loop-assigned, fingerprint-bound request identities.

One stall event with constrained grounds, including runtime_failure.

Decline as a non-act.

Iteration bookkeeping under a constrained machinery identity.

Stall only after dispatch accounting closes, without waiting for uncertainty resolution.

Late attributable outcomes accepted after stall, with post-stall instance activity refused.

Activation deadline propagated to the adapter and governing all phases.

Cursor ranges recorded and checked.

Whole-response validation separated from per-act adjudication.

Runtime replacement without changing the worker contract.

I particularly support the distinction between accounted and resolved dispatches. It keeps the loop honest about what has happened without making it responsible for decisions belonging to the examiner or A5.

Please fold in these three corrections and send the exact commit for final examination. Keep the round narrow.

A3 is not yet passed, and no implementation is authorised. A2 remains closed. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
