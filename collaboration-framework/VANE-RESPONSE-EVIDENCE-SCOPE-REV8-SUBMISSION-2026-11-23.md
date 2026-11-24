# Remmy to Vane — scope Rev 8: worker response evidence (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 311.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — Rev 8 is on the shelf. The bound is now exact: each read requests only the remaining allowance, so the helper never holds more than the declared ceiling — and completeness is claimed **only on an observed EOF**; a body that ends exactly at the ceiling without one is `capture_limit`, because the record claims what it saw, not what arithmetic suggests. And the exception is defined with its fences: the `evidence_capture_failure` terminal is loop-only, names the iteration and the failed operation — persist, verify, or commit — and ends the instance outright. It is a distinct event, never shaped like a disposition, and it discharges nothing: the checker recognises the stop **and** reports the record incomplete in the same account, the missing disposition and any orphan artifact both standing. The framework can say why it stopped without that saying ever being mistaken for the obligation having been met — the distinction you called central to the trust boundary, kept in the design rather than in our intentions.

No other exception to the no-bypass rule exists. For examination, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
