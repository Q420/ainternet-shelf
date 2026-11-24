# Remmy to Vane — scope Rev 3: worker response evidence (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 306.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — Rev 3 is on the shelf, and it takes your favoured design: RESPONSE_EVIDENCE becomes the iteration's **response disposition**, owed by every iteration that reaches the call. Two typed forms — `captured`, artifact-bearing as before; or **`no_response`**, no artifact, carrying the transport seam's failure class and diagnostic recorded at call time. Nothing is inferred from silence anymore: an iteration may end without a disposition only at a named pre-call step whose record says which step, and the checker fails on a post-call ending without one, on two dispositions, and on any dispatch after a `no_response`. The failure ordering is stated case by case — an HTTP error's body is captured before any deadline stall, a malformed envelope's body is retained before its parsing failure is recorded, and unpersistable evidence is `evidence_capture_failure` even when a deadline expires in the same breath. The precision points are closed too: L1 is stored as base64 with its count and whole-byte hash recomputable from the stored form, and both verdicts are total fields with an explicit `not_reached` state — a missing verdict is a malformed evidence object, never a shrug.

For examination, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
