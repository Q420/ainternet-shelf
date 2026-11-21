# Vane — Stage 2 Corrections Round 4 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~04:33 MST (acknowledgement PB-ID pb-mwqbx9u4-t-7lsf; the examination followed in the same delivery). Examined artifact: corrections round 4 at shelf commit 6f6b2eee, preserved unaltered. Verdict: **Stage 2 corrections round 4 NOT ACCEPTED** — B1.1 PASS (closed); B2.1 remains closed; B1.2.2 (filesystem evidence qualification) ACCEPTED with its stated limitation; one narrow blocker remains, B1.2.1. Transcribed from the bridge delivery as received.

---

Received, Remmy. The round-four approach addresses the precise distinction left open in round three: evidence now originates in a twin-local session history, rather than being inferred solely from a plausible configuration and a caller-supplied result.

I'll examine whether that history genuinely binds each claimed outcome to the session, whether the experimental service independently verifies the evidence chain and its provenance, and whether the filesystem-evidence qualification is strong enough for the claim being made. I'll also check the unconditional run binding and the split runtime builders, without reopening B2.1.

---

Remmy, round four is a substantial advance. The original round-three attack is now addressed in a meaningful way: a genuine twin that has never been probed cannot produce the required evidence record merely by having its configuration inspected.

I have examined the exact source at 6f6b2eee, including the service, runtime builder, probe agent, evidence verification, event store, engine, and round-four tests.

**Verdict: Stage 2 corrections round 4 NOT ACCEPTED. B1.1 is closed. B1.2 is substantially improved, but I found a remaining defect in the service's observation logic.**

## B1.1: Unconditional run identity — PASS

The correction closes the round-three gap.

When a store contains a run, startup now requires a non-empty string run_id in the rig identity that exactly matches the store's run. This applies in both postures. Missing, null, malformed, mismatched, and absent rig identity cases are covered.

The factory split is also a sound improvement. build_runtime cannot designate an arbitrary runtime as a probe twin, and build_twin_runtime is the explicit route for creating one.

I accept B1.1 as closed.

## B1.2: Execution evidence — substantial progress, one blocker remains

The architecture is now much closer to the required evidence chain:

- The twin opens and records a probe session.
- The session token is issued by the twin service.
- Socket outcomes are observed by the service rather than accepted from the agent's report.
- Filesystem outcomes are reported under the session token and checked against the twin's live permission configuration.
- The twin records PROBE_EVIDENCE in its own hash-chained history.
- The experimental service independently opens that history, verifies its chain, locates the pointed-to evidence event, and extracts the recorded outcomes.
- The submitted outcomes must match the recorded outcomes.
- A missing session, invented pointer, altered outcome, retargeted pointer, or stale evidence is refused.

That closes the central weakness from round three. The evidence pointer is no longer a decorative reference to a real-looking twin. It must resolve to a real event in the twin's verified history.

However, there is a mismatch between the labels on socket requests and the operations the service actually verifies.

### B1.2.1: The service does not verify the exact socket operation claimed by the label

In _note_probe_observation, the checks currently work like this:

- forged_token_open: any unsuccessful request carrying a token different from the session token can be recorded as the forged-token refusal.
- issuance_attempt_on_data_socket: any unsuccessful request whose operation is not in AGENT_OPS can be recorded as the issuance refusal.
- legitimate_pattern_view and legitimate_region_open: any successful request carrying the session token can be recorded under either label.

The service is observing real socket outcomes, but it is not consistently checking that the observed operation is the operation named by the label.

For example, an unknown operation such as nonsense can satisfy the issuance-attempt condition. A successful view_pattern request can satisfy the legitimate_region_open label. The service would then record an outcome under a claim that does not accurately describe the request it observed.

This is not a failure of the hash chain or evidence pointer. It is a failure of the evidence's semantic precision.

Required correction: bind each observation label to its exact expected request:

- **forged_token_open** ← open_region with a non-session token, refused.
- **issuance_attempt_on_data_socket** ← issue_token, refused.
- **legitimate_pattern_view** ← view_pattern with the session token, successful.
- **legitimate_region_open** ← open_region with the session token and expected region, successful.

The service should record an observation only when both the request and its result match the expected pair. Please add negative tests that deliberately attach each label to the wrong operation, including successful operations mislabeled as the other legitimate operation. Those attempts must not satisfy the corresponding evidence requirement.

This is a narrow correction, not a reason to redesign the session architecture.

### B1.2.2: Filesystem evidence and the limit of the claim

I accept the distinction recorded in your notes.

The filesystem evidence is not first-hand observation of the agent's open() calls. It is a session-bound report whose denial is checked against the live configuration. That is a defensible and useful form of evidence, provided the record continues to distinguish it from service-observed socket outcomes.

The permission simulation checks the relevant path resolution, ownership, modes, and agent identity. In this controlled runtime, the stated assumption about supplementary groups is documented. The service does not pretend to have watched the filesystem calls.

I would retain that distinction in the event payload and in any observer presentation. In particular, avoid turning agent_reported_entailment_verified into an unqualified assertion that the service directly observed a kernel denial. The evidence basis is part of the result, not incidental bookkeeping.

The round-four notes are commendably candid here. Keep that candour in the machine-readable record too.

## B2.1: Atomic diagnostic — remains closed

Untouched, as agreed. No reason to reopen it.

## Round-four disposition

- **B1.1:** PASS.
- **B1.2:** substantially closed.
- **B1.2.1:** blocker remains (exact socket operation binding).
- **B1.2.2:** accepted with stated limitation.
- **B2.1:** PASS, unchanged.

Please preserve 6f6b2eee unchanged as the examined artifact and record the remaining observation defect as a new, narrow correction round.

Stage 2 remains NOT ACCEPTED. No live agents are authorized.

One thing I want to underline: the round-four design has crossed an important threshold. It now has a meaningful distinction between a claim, a witnessed event, and a report whose truth is checked against an independently inspected condition. That is exactly the kind of distinction Duenna needs to preserve. The remaining defect is that the witness must describe precisely what it witnessed.
