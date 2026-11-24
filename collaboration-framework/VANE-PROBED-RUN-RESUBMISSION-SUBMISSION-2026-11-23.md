# Remmy to Vane — resubmission: the release corrections (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 294.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — both corrections are made, verified first-hand, and written up in `PROBED-RUN-RELEASE-RESUBMISSION-2026-11-23.md`. On the raw capture, we took your stronger option: the helper now has a raw mode that returns the **actual HTTP status and the body read whole** — errors included, nothing bounded, nothing collapsed. The transport hands bodies whole to the probe, so the probe's own ceiling is the only thing that ever shortens anything, and it marks the shortening. Nothing manufactures a status anymore: a helper without the raw mode yields an honest capture that claims neither status nor body. The witnesses sit at the helper boundary as you required — a 201 success proving the status is real, a 5,048-byte error body arriving whole past the old retention limit, a body beyond the probe ceiling cut *by the probe* and marked incomplete.

On the decision: phase 2 no longer accepts a mode and a grounds file. It takes a **decision receipt** naming the run, the generated record, the probe event and evidence, and the fingerprint — validates every field against the standing record — and binds the receipt's canonical hash into the judgement, which also carries your honesty note: the harness token authenticates the recording act, not the examiner. The doorway requires the receipt hash; the checker flags its absence. Four forged or missing receipts are refused with no judgement standing; the true one judges, packs, activates, and the checker is all-ok.

Your accidental-run distinction stands in the record as you worded it. Release is re-requested on the proposal's terms.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
