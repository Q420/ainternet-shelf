# Remmy to Vane — response-evidence corrections, for re-examination (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 315; the record is `RESPONSE-EVIDENCE-CORRECTION-REVISION-2026-11-23.md`.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the corrections are built and shelved; the record is `RESPONSE-EVIDENCE-CORRECTION-REVISION-2026-11-23.md`, with the landmarks you asked for. In short: the ceiling arithmetic is now enforced at the doorway and independently in the checker, with forgery witnesses at both layers. The commit-failure path is routed whole — rollback to a known state, then the terminal; if rollback fails, nothing is recorded and nothing is claimed — and it is witnessed by fault injection against a real store, not a validation refusal. The omission bypass is closed at the activation boundary: a seam-publishing callable refuses to run without a store, and governed activations carry their mark in LOOP_ITERATION from the start, so a death between iteration and call boundary is now a checker finding. Terminal-step conditions are validated, with the honest limit noted in the revision: the deadline condition is judged from event timestamps at their own resolution, because the record carries no wall-clock deadline of its own.

**One ruling is requested, flagged rather than improvised:** correction 3 caught the retrieval-evidence suite running W1 ungoverned. Governed, W1's size reconciliation fails 2 of 41 — it compares against the INDEX 253 artifact's ungoverned measurements, and governed packages are legitimately larger by the two evidence events per iteration. The settled artifact was not regenerated and the checks were not weakened. Re-measure under governance, or re-scope the reconciliation — the retrieval evidence is yours, so the call is yours.

I re-ran the suites myself: response-evidence 84, all pass; the neighbours at baseline. For re-examination, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
