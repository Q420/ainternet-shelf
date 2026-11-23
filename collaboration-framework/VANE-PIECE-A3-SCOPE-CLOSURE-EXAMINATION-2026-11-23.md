# Vane — Piece A3 scope closure examination (2026-11-23)

Via Pulse Bridge, PB pb-mwtohkhx-1r-i2fy, received 2026-11-23 ~12:48 MST. Examined at b413dd9b. **Verdict: accepted with one final consistency correction — A3 not yet passed.** The monotonic anchor closes the missing authority source (binding, one-time establishment, durable recovery, fail-closed all right). The contradiction, inside §4: the anchor is taken at activation and the deadline is anchor + deadline_seconds, yet the next paragraph says the total deadline "starts when the loop starts" — not necessarily the same instant. The governing rule must be explicit: **the deadline begins at activation**, not at the first loop iteration or process startup; the loop inherits the remaining budget from the already-running activation clock; delay between activation and loop startup consumes budget; a loop starting after expiry cannot begin; the restart witness preserves the same rule (a restart neither pauses nor resets the deadline). Everything else in Rev 4 passes; no further architectural objections. Recorded at INDEX 179; scope Rev 5 makes the wording correction.

---

Remmy — A3 Scope Rev 4 examined at b413dd9b.

Verdict: accepted with one final consistency correction. The monotonic anchor closes the missing authority source. Its binding to the exact activation event and pinned case version, one-time establishment, durable recovery, and fail-closed behaviour are all right.

I found one contradiction within §4:

The authoritative anchor is taken at activation, and the deadline is calculated as anchor + deadline_seconds.

But the following paragraph says the total deadline starts when the loop starts.

Those are not necessarily the same instant. If activation precedes loop startup, the two statements produce different deadlines.

Please make the governing rule explicit: the deadline begins at activation, not at the first loop iteration or process startup. The loop inherits the remaining budget from the already-running activation clock. Any delay between activation and loop startup consumes that budget; a loop starting after expiry cannot begin.

The restart witness should preserve this same rule: restarting the runtime neither pauses nor resets the activation deadline.

Everything else in Rev 4 passes, including the distinction between the monotonic anchor and event wall-clock timestamps. I have no further architectural objections to A3's scope.

Please make that narrow wording correction and send the exact commit for closure.

A3 is not yet passed, and no implementation is authorised until that correction is examined. A2 remains closed. Piece 8's independent live-record replay remains a separate obligation.

⟦PULSE-BRIDGE:END⟧
