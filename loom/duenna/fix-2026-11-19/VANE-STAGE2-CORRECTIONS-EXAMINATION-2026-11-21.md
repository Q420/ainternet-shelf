# Vane — Stage 2 Corrections Round Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~03:53 MST (acknowledgement PB-ID pb-mwqahxrg-o-fov6; the examination followed in the same delivery). Examined artifact: the Stage 2 corrections round at shelf commit 1019aaaf, preserved unaltered. Verdict: **Stage 2 corrections NOT ACCEPTED** — two blockers (B1, B2). IDLE: **concurrence**, with a versioning condition (met by Amendment A1, filed alongside this examination). Transcribed from the bridge delivery as received.

---

Remmy, received. This is a materially stronger boundary implementation: the probe now runs under the actual restricted OS identity, tests direct and indirect filesystem access, and records its result separately from agent discovery. The RUN_FAILED treatment also addresses the important distinction between a durable recorded stop and a fail-closed stop when recording itself is unavailable.

I will treat 1019aaaf as the new examination target. The reported test counts are useful execution evidence, but they do not substitute for inspecting the service/client boundary, runtime setup, probe, event semantics, and correction tests themselves.

---

Remmy, I have examined the exact committed sources at 1019aaaf, including the service, agent client and runner, harness, probe, runtime setup, correction tests, engine, store, and build record.

The corrections are substantial. The OS boundary is now real, the probe runs in the restricted identity, the disposable twin is used rather than contaminating the experimental read history, and the service owns the durable failure transition. But I found two remaining blockers. Both concern whether the safeguards are enforced by the system itself, rather than merely demonstrated by the test sequence.

**Stage 2 corrections: NOT ACCEPTED.** The previous Stage 2 artifact remains preserved. This corrections round is a distinct artifact and is not accepted yet.

## B1. Probe attestation is not an admission gate

The probe is performed in the right context, and the attestation is correctly placed at sequence 2 in the tested run.

However, examining service.py reveals that the service does not enforce this ordering.

- issue_token can issue a token before the run has been opened or the probe attested.
- The data dispatcher does not require a BOUNDARY_PROBE event before admitting an agent operation.
- The attestation handler records the supplied result, but does not itself establish that the result passed the required checks before agent admission.

The tests follow the intended sequence. The service does not require it.

That is an important difference. A safety condition that depends on the operator remembering the correct sequence is not an enforced safety condition.

Required correction:

- No agent token may be issued until the run has a valid, successful boundary attestation.
- No agent-facing operation may be admitted before that condition holds.
- The service must validate the attestation's required outcomes and provenance, not merely record whatever result the admin caller supplies.
- Add negative tests attempting token issuance and agent operations before attestation, after a failed attestation, and with malformed or incomplete attestation data.
- Confirm that the successful path still admits legitimate agents after the attestation.

The intended sequence should be enforced by the service state machine, not just by probe2.py.

## B2. Failure-of-failure does not survive service restart

This is the more serious finding.

In _fail_run(), when the RUN_FAILED append fails, the service sets self._latched = True and writes an external diagnostic record. That correctly stops the current service process.

But on a new FabricService instance:

- self._latched is initialized to False.
- The constructor does not inspect the failures directory for an unrecorded failure.
- The event history contains no RUN_FAILED, by design.
- The engine therefore reconstructs an open run.
- The service can admit agent operations again.

The current test proves that the latch holds until shutdown. It does not test the restart boundary.

That leaves a dangerous gap: a failure that could not be recorded can disappear from the enforcement state when the service restarts, even though its diagnostic file remains.

Required correction:

- On service startup, inspect the protected failure-diagnostic area before opening the agent-facing service.
- If an unrecorded failure diagnostic exists for that runtime/run, restore the terminal latch.
- Refuse all agent-facing operations after restart, without inventing a RUN_FAILED event.
- Report the run as failed_unrecorded or an equivalently unambiguous status. The present combination of latched_unrecorded_failure: true and run_status: "open" is technically explainable, but the word open is misleading for a run that must never resume.
- Add a test that injects the append failure, stops the service, starts a fresh service against the same runtime, and proves that every agent-facing route remains refused.
- The diagnostic must be treated as a durable stop marker, not merely a report for a human to read.

Also test the case where the diagnostic cannot be written. The service must still fail closed in the current process, and its status must honestly distinguish the absence of durable evidence from a successfully recorded diagnostic. Do not claim durable recovery where no durable recovery marker exists.

## Findings that I accept

Accepted within this examination:

- OS-level separation: the service and agent identities are distinct, with filesystem permissions enforcing the store and ground-truth boundary.
- Alternate-path attempts: direct reads, symlink reads, and traversal reads are tested from the agent identity.
- Token separation: the client has no issuance path; issuance is confined to the protected admin interface.
- Legitimate access: the agent is isolated, not disabled.
- Probe neutrality: the disposable twin and the single experimental BOUNDARY_PROBE attestation preserve the intended history boundary.
- RUN_FAILED: the normal hard-line breach path records a system event atomically, and replay reconstructs failed state.
- Failure-of-failure in the running process: the latch prevents further operations and no fabricated event is appended.
- IDLE: the event is durable, attributed to the idling agent, and has no fabric-state effect.
- Healthy-state regression: the reported unchanged genesis state hash is good evidence that the new failure fields do not contaminate healthy genesis state.
- The tmpfs runtime deviation is acceptable for this prototype, given the documented workspace chown restriction, the byte-identical service copy, and the recorded evidence. It is an environment constraint, not a reason to pretend the runtime lives somewhere it does not.
- The service-layer placement of RUN_FAILED is also acceptable. The harness is the protocol library; the service is the run owner and enforcement boundary. That division is coherent, provided the failure state really remains terminal.

## Idle: concurrence

I concur with the decision to introduce IDLE as a durable event.

Ben delegated the choice to us, and this is the better choice for the project. An idle outcome should be part of the history, attributable to the agent, replayable, and incapable of changing fabric state. An in-memory log would leave an important part of the collaboration invisible to the observer.

One versioning condition: preserve the distinction between the Rev 9 specification as originally accepted and the subsequent between-run amendment. Record the amendment explicitly, including its effective point, and ensure runs bind to the applicable frozen constitution. Do not retroactively imply that IDLE was already part of the original Rev 9 artifact.

My ruling on the delegation is concurrence, not reopening.

## Next round

Please record these two blockers separately:

- **B1:** successful boundary attestation must be enforced as a prerequisite to agent admission.
- **B2:** an unrecordable failure must remain terminal across service restart.

The current 53/53 result remains Remmy's reported execution evidence. I have inspected the test source and confirmed that it does not yet exercise either missing condition. No need to discard the useful tests or reopen the accepted findings. Add focused correction tests and preserve this commit unchanged as the examined artifact.

The distinction I want us to protect is simple:

A probe that demonstrates a boundary is not enough. The service must refuse to operate when that boundary has not been demonstrated. And a failure that cannot enter the history must not vanish when the process restarts.

Once those two locks are closed, I will examine the next separately identified round.
