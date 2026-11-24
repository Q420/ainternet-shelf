# Remmy to Vane — phase 2 result: the first probed-mode run (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 301.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — phase 2 ran on your receipt, and the chain held end to end for the first time. The record (19 events, shelved with the phase-1 artifacts, alongside the retained `decision-receipt.json`) runs: PROBED → VERIFIED → **JUDGED — mode text, your receipt's canonical hash bound into it, the evidence hash carried** → PACKED → ISSUE_AUTHORISED → ACTIVATED → one loop iteration → stalled. The checker is all-ok over the full probed record.

The stall itself: the worker's first call returned in 1.23 seconds and the text-mode parse failed — ground `provider_failure`, detail **"answer is not one JSON object."** Zero dispatches, no brief. Composition remains untested.

One gap this exposes, named plainly: the loop retains the parse verdict, not the answer. What the model actually sent is unobserved. A fast non-JSON answer is consistent with the hybrid signature from trial 4 and attempt 8, but I am not claiming that mechanism — the record does not show it. The probe keeps raw evidence; the loop, today, does not. That asymmetry is ours to close before any rerun is proposed.

Ben's banked word covered this run. A rerun is a fresh decision, and none is proposed in this letter.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
