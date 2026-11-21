# Vane — Stage 2 Corrections Round 3 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:19 MST (acknowledgement PB-ID pb-mwqbfwph-s-k8sr; the examination followed in the same delivery). Examined artifact: corrections round 3 at shelf commit e4e35db6, preserved unaltered. Verdict: **Stage 2 corrections round 3 NOT ACCEPTED** — B2.1 CLOSED; B1.1 substantially closed with one narrow identity-binding defect; B1.2 remains an open, substantive blocker. Both round-3 interpretations ACCEPTED. Transcribed from the bridge delivery as received.

---

Received, Remmy. I'll examine the round-three source at e4e35db6 against the three outstanding findings, keeping the two interpretations separate from the implementation fixes. In particular, I'll distinguish a probe result that was validly verified at the moment of admission from a claim that the same twin must remain available forever.

The central question remains whether the experimental runtime can establish admission only through evidence bound to its actual, independently identified probe twin, and whether failure markers remain fail-closed when their contents or identity cannot be trusted.

---

Remmy, I have examined the actual round-three source at e4e35db6, including the service, runtime builder, probe, and new correction tests.

**Verdict: Stage 2 corrections round 3 NOT ACCEPTED. B2.1 is closed. B1.1 is substantially improved but retains a narrow identity-validation defect. B1.2 has a more fundamental evidence-provenance gap.**

## B1.1: Probe posture confinement — substantially closed, one remaining blocker

The principal correction works: an experimental runtime carrying an experimental rig identity refuses probe_target at startup. The environment variable is no longer sufficient to open the gate. The missing-identity and flipped-identity cases are also handled.

There is, however, a hole in the run-identity check.

In FabricService.__init__, the startup comparison is conditional on both store_run and rig_run being non-null:

```python
if store_run is not None and rig_run is not None \
        and rig_run != store_run:
```

Consequently, an existing store with a run can be paired with a rig identity whose run_id is missing or null, and the service will not refuse the probe posture. That is weaker than the notes' claim that the identity binds to the store's actual run on restart.

Required correction: if the store already has a run, the rig identity must contain a valid run ID equal to that store run. Missing, null, malformed, or mismatched run identity must refuse startup. Add a restart test for each relevant case.

One related design point: build_runtime(base, name, rig="experimental") accepts probe_twin for any runtime name. The intended flow uses that designation only for the disposable twin, but the factory itself does not enforce that restriction. I would prefer the build interface to make the distinction explicit and difficult to misuse, rather than leave the role assignment as a caller convention.

## B1.2: Attestation evidence bound to actual probe execution — blocker remains

This is the important one.

The round-three implementation does considerably more than round two. It checks provenance values, compares live filesystem metadata, verifies the twin's rig identity and run ID, and compares the twin's live service code hashes. Those are real improvements.

But the live verification currently establishes that a suitably configured twin exists. It does not establish that the claimed probe outcomes were actually produced by a probe running against that twin.

The distinction is visible in the two relevant functions:

- attestation_problems() validates the supplied attempt names and outcome labels.
- _verify_twin_live() validates the twin's rig, store run ID, filesystem metadata, and code hashes.

Neither function verifies the claimed attempts against evidence of their execution.

Consider this case:

1. Build a genuine probe_twin runtime.
2. Open its run, but do not execute the boundary probe.
3. Collect its actual rig identity, store run ID, filesystem metadata, and code hashes.
4. Construct a probe-result object containing the expected all-passing attempt labels and outcomes.
5. Submit that object to the experimental service.

The live checks can all pass. The twin exists, its identity is consistent, its layout is correct, and its code matches. The claimed outcomes are syntactically valid. Yet no probe established those outcomes.

The existing fabricated-result test does not catch this. It points to a nonexistent round3ghost runtime, so it tests whether a nonexistent twin is rejected, not whether fabricated outcomes can be attached to a real one.

Required correction: the attestation must be bound to evidence of the actual probe execution, not just to the runtime that supposedly hosted it. The service needs a way to distinguish a genuine probe result from an operator-supplied JSON object with plausible values. The twin's recorded history may contribute evidence, but it cannot by itself prove denied direct reads; those outcomes need an independently verifiable execution result too.

Please add the adversarial test above: a real, correctly configured twin, no probe execution, fabricated passing outcomes, and an expected refusal with no BOUNDARY_PROBE event. Also test altered outcomes against a genuine twin.

I am not prescribing a particular cryptographic mechanism. I am requiring that the evidence establish more than the consistency of a caller's assertions.

## B2.1: Atomic failure diagnostics — PASS

This correction closes the finding.

- The diagnostic is written to a temporary file in the failures directory.
- The file is flushed and fsynced before rename.
- The rename is atomic.
- The containing directory is fsynced.
- A stranded .json.tmp is treated as a candidate marker.
- An unreadable or malformed candidate restores the latch as an uncertain failure.
- No RUN_FAILED event is invented.
- Status distinguishes unreadable from a complete written or restored diagnostic.

The conservative choice to latch the runtime when the marker's run cannot be determined is correct. A system must not reopen a possibly failed run merely because the evidence needed to identify it has become unreadable.

The reported 34/34 suite covers the relevant cases. I inspected the test source, but have not independently executed the suite; the count remains your reported run evidence.

## The two interpretations

**Interpretation 3: live verification at recording time, claim-based revalidation thereafter. I accept this principle.** The twin is disposable. Requiring it to remain available indefinitely would make admission depend on scaffolding that is explicitly allowed to be rebuilt. The recorded attestation should become durable evidence once it has been validly established. Subsequent gate consultations should verify the integrity and validity of that recorded evidence, not require the original twin to remain alive. But this interpretation depends on the recording event actually being a verified act. B1.2 is not yet there. Once the execution-evidence gap is closed, I support the claim-based gate.

**Interpretation 4: an unreadable marker latches this runtime, even when its run is indeterminable. Accepted.** The false-latch cost is preferable to silently reopening a run whose failure may have become unrecordable. This is an honest fail-closed policy, and the status representation preserves the uncertainty rather than disguising it.

## Round-three disposition

- **B1.1:** one narrow identity-binding correction remains.
- **B1.2:** open, substantive blocker.
- **B2.1:** closed.

The improvements are real, and I would preserve e4e35db6 unchanged as the examined artifact. Please record these remaining findings as a new correction round, not as changes to the existing one.

Stage 2 remains NOT ACCEPTED. No live agents are authorized. Stage 1 core and the observer remain accepted within their previously examined scopes.

One distinction is worth keeping at the centre of this work: a verified runtime configuration is not a verified experiment. Round three has made the former considerably stronger. The remaining work is to establish the latter.
