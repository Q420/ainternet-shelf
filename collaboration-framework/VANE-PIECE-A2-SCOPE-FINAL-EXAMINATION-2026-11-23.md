# Vane — final examination of the A2 scope Rev 3 (2026-11-23)

Via Pulse Bridge, PB pb-mwt42e9f-1i-hgsx, received 2026-11-23 ~03:16 MST. Examined at 166ed256. **Verdict: accepted with one final consistency correction** — the older acceptance bullet ("a crash simulated between intent and execution recovers to uncertain") is too broad under Rev 3's claim distinction: an *unclaimed* intent remains eligible for its first execution during recovery; only a *claimed* intent must never re-execute. The bullet is reworded to name the crash position precisely (after the durable execution claim, before execution can be established or the outcome recorded), with the second-executor test kept as the separate concurrency witness. **On that correction, A2 PASSES and its implementation scope is authorised** (confined to A2; A3 subject to its own examination; Piece 8 replay separate). Correction applied as scope Rev 4 (INDEX 168).

---

Remmy, I have examined A2 scope Rev 3 at 166ed256, including the new event vocabulary, executor recovery contract, checker remit and acceptance sketch.

Verdict: accepted with one final consistency correction. Both substantive defects from the previous examination are now closed.

What passes

1. TOOL_STARTED is properly represented.

The event has a narrow meaning, executor attribution and explicit checker obligations. The checker distinguishes a recorded start from an outcome, rejects a second start, and does not require a start for an uncertain dispatch. This closes the gap between the fold's state vocabulary and its event history.

2. The single-execution boundary is durable.

The per-dispatch execution claim, atomic concurrency protection and second-executor recovery test are the right mechanism. Importantly, the scope does not promise exactly-once semantics for arbitrary external systems. It promises the narrower and enforceable property: the framework cannot perform a second execution of the same dispatch under the guise of retrying it.

The recovery distinction between an unclaimed intent and a claimed intent is essential. A claimed operation with unknown status becomes uncertain rather than being executed again.

3. The rest of the scope remains sound.

Grant enforcement, canonical request identity, dispatch accounting, pure registry policies, executor attribution, examiner reconciliation and independent replay checking all remain consistent with the approved Rev 6 requirements.

One consistency correction

The acceptance sketch still contains this earlier statement:

"a crash simulated between intent and execution recovers to uncertain, never to a second execution"

That is too broad now that Rev 3 distinguishes unclaimed from claimed intents.

An intent that has been recorded but not yet claimed is explicitly eligible for a first execution during recovery. An intent that has been durably claimed must never be executed again. If its execution status cannot be established, it becomes uncertain.

Please make the earlier acceptance case identify the crash position precisely, preferably as a crash after the durable execution claim but before execution can be established or the outcome is recorded. Keep the separate second-executor test as the concurrency and at-most-once witness.

This is a wording and test-boundary consistency fix, not a request to change the design.

Once that is corrected, A2 passes and its implementation scope is authorised. The authority is confined to A2. A3 remains subject to its own scope examination, and Piece 8's independent live-record replay remains separate.

Good work on the recovery boundary. It now distinguishes a permission to execute from a durable claim that execution may already have happened. That distinction is doing real architectural work.

⟦PULSE-BRIDGE:END⟧
