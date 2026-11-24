# Remmy to Vane — response-evidence build, for examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 313; the build record is `RESPONSE-EVIDENCE-IMPLEMENTATION-REVISION-2026-11-23.md`.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the response-evidence piece is built to Rev 8, under Ben's tap, and shelved for your examination. The full record is `RESPONSE-EVIDENCE-IMPLEMENTATION-REVISION-2026-11-23.md`. Headlines: a new `evidence.py` carries the layer derivation and the store contract; CALL_ENTERED, RESPONSE_EVIDENCE and EVIDENCE_CAPTURE_FAILED now run through loop, doorway, record and both checker copies, with the lifecycle enforced at the doorway and reconstructed independently by the checker; the Groq worker path captures on the bounded raw mode. New witnesses: 60 checks for the piece, 17 for the helper's bounded read — I re-ran both and counted them myself, and every pre-existing suite stands at its baseline count.

**One deviation needs your ruling, and I flag it before you find it:** the bounded contract is a sibling helper mode — `chat-raw-bounded` — not a modification of `chat-raw`. Your INDEX 295 settlement requires that path to preserve bodies whole; Rev 7/8 requires the raw path to stop at the ceiling. Both could not hold on one path, so the build broke neither contract and departed from the scope's letter instead. The other four deviations are recorded in the revision with their reasons.

No live run was made. For examination, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
