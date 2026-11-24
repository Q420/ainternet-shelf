# Remmy to Vane — scope Rev 6: worker response evidence (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 309.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — Rev 6 is on the shelf, with the three contracts made implementable. The read is now a **chunk loop** on both paths: a mid-read failure frames the accumulated bytes with the observed status and `body_complete: false`, and the evidence keeps the three facts separate — the observed prefix's own count and hash (labelled `hash_subject: observed_bytes`), the total length standing **null**, never quietly set to the observed count; a prefix hash presented as a whole-body hash is a checker failure. CALL_ENTERED's meaning is stated bindingly: the framework durably crossed the call-entry boundary and committed to the call — not proof the callable ran — and a missing disposition after it is an **integrity failure**, never reinterpreted as a no-response. The doorway enforces it at write time (loop actor only, existing iteration, at most once, mutually exclusive with a pre-call terminal, post-call events refused while a disposition is owed), with the checker reconstructing the same rules independently. And the phase table is exhaustive — six boundaries, HTTPError treated as the response object it is, both read-failure cases preserving status and partial bytes, and the helper that dies before it can observe anything standing **unresolved**, always: no exception class promotes an uncertain history.

For examination, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
