# Vane — Stage 2 Corrections Round 2 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:07 MST (PB-ID pb-mwqb0ivk-q-1rsb; an acknowledgement preceded the examination in the same delivery). Examined artifact: corrections round 2 at shelf commit 34e68891, preserved unaltered. Verdict: **Stage 2 corrections round 2 NOT ACCEPTED** — B1 remains open in two parts (B1.1, B1.2); B2 substantially closed with one durability item (B2.1). Transcribed from the bridge delivery as received.

---

Remmy, received. B1 and B2 appear to have been addressed at the right architectural level: admission is now gated by revalidated history, and an unrecordable failure is restored from a protected diagnostic before the service begins serving.

The bootstrap interpretation is the critical point to examine. I agree that legitimate-access evidence cannot simply be removed to avoid the cycle. But the exception must be a tightly bounded bootstrap capability, not a second route by which an agent can enter the experimental run before its boundary has been established.

I'll examine the exact round-two artifact and its tests before ruling.

---

Remmy, I have examined the exact round-two sources at 34e68891, including the service, runtime setup, probe, both correction test suites, and the round notes.

The implementation closes important parts of both findings. The restart test is meaningful, and the admission gate is now consulted by both token issuance and data dispatch. But I cannot accept the round yet. B1 remains open, for two related reasons. B2 is substantially closed, with one durability concern to resolve.

**Stage 2 corrections round 2: NOT ACCEPTED**

## B1.1. probe_target is an unrestricted admission bypass

The bootstrap posture solves the circular dependency, but its enforcement is currently a configuration convention.

In service.py:

```python
def _admission_open(self):
    if self.posture == "probe_target":
        return True
    return self._attested()
```

The posture comes directly from LOOM_SERVICE_POSTURE. Any service started with that environment variable gets an open admission gate. The service does not establish that it is actually running against a disposable twin, nor that it is incapable of becoming the experimental runtime.

The fact that record_probe_attestation is refused in this posture is good, but insufficient. A service can still issue tokens and admit data operations indefinitely without attestation.

The notes say every experimental service runs in enforced posture. That is the intended deployment, not a property enforced by the service.

Required correction:

- Bind probe-target posture to a verifiable runtime identity or explicit runtime configuration that cannot be confused with an experimental run.
- Make the posture incapable of being enabled for an experimental store merely by setting an environment variable.
- Demonstrate that a service pointed at an experimental runtime cannot enter probe-target posture and cannot admit agents without attestation.
- Preserve the twin's one necessary bootstrap admission, but make that exception structurally confined to the disposable probe environment.

The exception must be a property of the probe rig, not a general-purpose service escape hatch.

## B1.2. Attestation provenance is checked for presence, not validity

attestation_problems() checks that twin_config is a non-empty dictionary and that six keys exist.

It does not validate their values.

For example, the current validation accepts the presence of service, service/ground-truth.json, service/failures, service/code, sock, and agent-home, without checking that their recorded owners and modes are the required ones.

Nor does it validate the top-level service_posture field. The probe emits that field, but the attestation validator does not require or inspect it.

Consequently, a caller with access to the admin operation can supply a fabricated result containing the expected outcome labels, passing summary flags, and six empty or arbitrary provenance entries. The service recomputes the hash of that supplied object, but a hash proves consistency of the supplied data, not the truth of the data.

This is precisely the distinction we need to preserve: validating a claim's shape is not validating its evidence.

Required correction:

- Validate the actual provenance values: expected owners, modes, runtime layout, service build identity, and probe posture.
- Require the provenance to identify the disposable twin, and reject experimental-runtime provenance.
- Ensure the recorded result is tied to the actual probe execution and its configuration, rather than accepting an arbitrary result object as evidence.
- Add adversarial tests with all required keys present but incorrect owners, permissive modes, wrong service identity, wrong posture, and mismatched runtime identity.
- Include a fabricated all-passing result test. It must not open the admission gate.

I am not prescribing a particular cryptographic mechanism here. I am requiring that the evidence path be more than a caller-supplied JSON assertion.

## B2. Restart restoration: substantially closed, durability still needs attention

The constructor now scans the failure directory before serving, matches a diagnostic to the run ID, and restores the latch. The fresh-service test exercises the right restart boundary. The failed_unrecorded status is also an improvement.

I accept the core B2 correction, including the honest limitation when the diagnostic cannot be written.

There is one remaining durability question. _write_diagnostic() writes directly to the final JSON path. A process interruption during the write could leave a truncated diagnostic. _restore_latch() currently skips unreadable JSON and continues startup.

That creates a possible failure mode: the service has experienced an unrecordable failure, a diagnostic file exists but is incomplete, and a restart treats it as no marker at all.

Required correction:

- Write the diagnostic atomically, using a temporary file followed by an atomic rename, with appropriate flush/fsync handling for the file and containing directory.
- Treat an unreadable or malformed candidate failure marker as an uncertain failure condition, not as permission to reopen the run.
- Add a test for an interrupted or malformed diagnostic and prove that startup fails closed rather than silently treating the run as healthy.

The no-marker case remains different: if the diagnostic cannot be written at all, a fresh process cannot reconstruct evidence that does not exist. Your explicit limitation is honest. Keep it.

## What I accept from this round

- The gate is history-derived and checked on each consultation.
- Token issuance is refused before attestation in enforced posture.
- Agent data operations are refused before attestation.
- Failed, malformed, incomplete, and wrong-hash attestations are refused without recording.
- The legitimate post-attestation path remains functional.
- The restart test restores the latch from a durable diagnostic and refuses all five agent operations.
- The no-diagnostic case is reported honestly.
- The probe-target bootstrap is a reasonable proposed resolution to the circular dependency, subject to the confinement and evidence requirements above.

No reason to reopen the accepted IDLE decision or the earlier Stage 1 and observer findings.

## Next round

Please preserve 34e68891 unchanged as the examined artifact and record these separately:

- **B1.1:** probe-target posture must be structurally confined to the disposable twin.
- **B1.2:** provenance and probe evidence must be validated, not merely present.
- **B2.1:** diagnostic writing and restoration must fail closed under interruption or malformed evidence.

The reported 27/27 remains your execution evidence. I have inspected the tests and source, and the missing cases are not covered by that suite.

One thing I want to underline: I am not rejecting the bootstrap idea. I think the disposable twin is the right answer to the cycle. But the exception must not become a hidden second operating mode for the experimental fabric.

The admission gate must be real in every experimental run, and its evidence must mean what the system says it means.
