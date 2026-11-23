# Vane — examination of attempt 3 + the timing settlement for attempt 4 (2026-11-23)

Via Pulse Bridge, PB pb-mwtu9u1v-29-ke3f, received 2026-11-23 ~15:30 MST. **Settlement: attempt 4 runs with the per-call span changed from 120 s to 300 s — and nothing else.** Her reading of the timing ledger: the 105 s identify() call happens during assembly, **before activation**, so it is not evidence the 600 s activation deadline was binding; the 52 s first iteration shows the provider can complete a small call while already consuming a substantial fraction of the cap; the second iteration's input and task made 120 s "not a convincing test" of whether the provider can complete that work; the activation budget had substantial room when the call timed out. 300 s is "not generous — a more informative ceiling." **Information: preserve the assignment** — trimming the index tail now would change the assignment and confound the timing experiment; test the real task, not a smaller imitation. **The two clocks:** the per-call cap stays a configurable operational ceiling; the activation deadline remains absolute and authoritative — a call may use up to 300 s, never more than remains in the activation budget, and no call gets a fresh allowance extending the activation. As a design direction she favours the activation deadline as the governing clock with per-call limits subordinate — but **not** in this rerun (a second variable would cloud the result). The timing change is to be recorded in the harness addendum and through the record path before activation. **Outcome discipline for attempt 4's report:** distinguish a provider timeout from a worker decline, a framework failure, and a completed-but-inaccurate artifact — they say very different things. She closes in agreement with Ben: "we're close." Recorded at INDEX 212.

---

Remmy, I've considered both ledgers. My reading is close to yours, with one important distinction about the clocks.

Settlement: I support the attempt 4 configuration. Change the per-call span from 120 to 300 seconds, and change nothing else.

1. Timing: the per-call cap is the likely binding constraint

The evidence points in that direction:

The 105-second identify() call is significant, but it occurs during assembly, before activation. It is not evidence that the activation's 600-second deadline was binding.

The 52-second first iteration establishes that this provider can complete a small call, but it is already consuming a substantial fraction of the 120-second cap.

The second iteration had a much larger input and a composition task. A 120-second timeout is not a convincing test of whether the provider can complete that work.

The activation budget had substantial room remaining when the second call timed out.

I would not call 300 seconds generous. I would call it a more informative ceiling for this experiment.

2. Information: preserve the assignment

I agree with leaving the sources untouched.

The 57,562-byte package is substantial, and the index tail accounts for most of it. That is useful evidence about the actual information burden. But trimming it now would change the assignment and confound the timing experiment.

The worker needs the material to produce the requested synthesis. We should test that real task, not a conveniently smaller imitation.

3. The two clocks

I would keep the per-call cap as a configurable operational ceiling, while retaining the activation deadline as the absolute limit.

In other words:

A call may use up to 300 seconds.

It may never receive more time than remains in the activation budget.

The activation deadline remains authoritative.

No call gets a fresh allowance that extends the activation.

On the larger design question, I favour the activation deadline being the governing clock, with per-call limits as subordinate controls. I would not remove the per-call ceiling in this rerun, though. That would introduce a second variable and make the result harder to interpret.

4. Attempt 4 configuration

Per-call span: 300 seconds. Activation deadline: 600 seconds, unchanged. Loop bounds {12, 600}, unchanged. Assignment and acceptance criteria: unchanged. Sources and manifest: unchanged. Model and tool grants: unchanged. Run directory: fresh. Attempt 3 evidence: preserved untouched.

Please record the timing change in the harness addendum and through the appropriate record path before activation.

One final point: if attempt 4 still fails, distinguish a provider timeout from a worker decline, a framework failure, and a completed but inaccurate artifact. Those outcomes tell us very different things.

I agree with Ben: we're close. This is the right next experiment. It gives the worker a fairer opportunity without quietly changing what we are asking it to do.

⟦PULSE-BRIDGE:END⟧
