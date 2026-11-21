# Vane — Stage 3 Implementation Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:21 MST (PB-ID pb-mwqdicj2-v-d1q0-verdict; an ACK and a first-pass note preceded it under PB pb-mwqdicj2-v-d1q0-ack). Examined artifact: Stage 3 build at shelf commit 1e69f5d3, preserved unaltered. Verdict: **Stage 3 NOT ACCEPTED — one blocking correction (B1): the event fold accepts illegal tension transitions.** The contribution-ID extension and the TV-13 canned fixture are both ACCEPTED. The Stage 3 design remains settled at Rev 4; this is an implementation correction. Transcribed from the bridge delivery as received.

---

## Stage 3 implementation verdict — NOT ACCEPTED. One blocking correction required.

Examined commit: 1e69f5d3c9fc23df374bddd4f5e6a9d4be0c389f

The Stage 3 design remains settled at Rev 4. This is an implementation correction, not a request to reopen the design.

### B1. The event fold accepts illegal tension transitions

In fabric/engine.py, the TENSION_STATUS handler checks that the event's from value matches the currently folded status, then assigns to without checking whether that transition is permitted for that tension type.

That is insufficient for the lifecycle Rev 9 specifies.

For example, the current fold would accept all of these if their from values matched:

- A semantic tension moving directly from open to resolved.
- A structural tension moving from open to standing.
- A terminal resolved tension moving to another status.
- A structural tension moving to examined.

The same general validation gap exists in two adjacent places:

- TENSION_RAISED accepts its supplied type, origin and initial status without enforcing the permitted combinations.
- FACET_STATUS checks its from value, but does not validate that to belongs to the six permitted facet statuses.

This matters even though agents cannot write these events directly. The event history is authoritative, and replay must not derive an impossible lifecycle state from a hash-valid but protocol-invalid event. Stage 4 will also depend on these rules.

**Required correction:**

Enforce TENSION_RAISED type/origin/status combinations:

- semantic: contribution or examination origin, initially open;
- structural: checker origin, initially open.

Enforce type-specific TENSION_STATUS transitions:

- semantic: open → examined; examined → resolved or standing;
- structural: open → resolved only;
- resolved and standing are terminal.

Validate FACET_STATUS against the six-status enumeration.

Add negative replay tests that construct hash-valid histories containing illegal transitions and assert that replay halts. Include structural and semantic cases, terminal transitions, and an invalid facet status.

The existing positive lifecycle tests should remain intact. Do not solve this by weakening replay or by making the checker responsible for repairing invalid history.

### Accepted: the contribution-ID extension — ACCEPTED

The extension is justified and properly bounded.

The source assigns an ID before validating a recordable contribution submission, places it in the outcome event, and reconstructs an all-submissions registry that distinguishes accepted from rejected contributions.

The key distinction is preserved:

- A rejected contribution can be cited.
- Its existence resolves the reference.
- Its rejected status prevents it from satisfying the evidence predicate.
- The claim is still recorded, rather than refused.

The PIN test is well constructed: it creates a real stale rejection, cites its ID, and checks both the recorded claim event and the resulting unexamined facet status.

This is not a loophole in completion evidence. It makes the negative evidence condition testable.

One boundary to preserve: a rejected contribution's ID is an identifier for the recorded submission, not an accepted contribution record in the engine's accepted-contributions state.

### Accepted: TV-13's canned structural tension — ACCEPTED

The fixture is an acceptable Stage 3 test setup.

It injects a clearly labelled checker-origin structural tension through the engine's event path, then tests the Stage 3 responsibility: a schema-valid assessment is rejected as structural_target, no assessment record is created, no tension transition occurs, and the tension remains open.

It does not claim to demonstrate a failed seal attempt. The resolution half is explicitly deferred and not counted as a pass. That is the correct boundary between stages.

Keep that distinction in the test output and build record. Stage 4 must still demonstrate the real checker-origin event and passing-seal resolution.

### Other examination findings

The source review supports the following:

- The three operations use the shared ordered ladder, with the expected action-specific identity and idempotency rules.
- The claim's two-level recordability distinction is implemented.
- Claim referential checks resolve the facet before cited contributions.
- The three claim evidence conditions are fold-computed counting conditions.
- Historical versions are treated as legitimate evidence, not as current evidence.
- Examination snapshots come from the authenticated agent's latest harness-recorded openings.
- Multi-match examination handling and terminal-tension recurrence are implemented.
- Tension and facet transitions are grouped atomically with the triggering submission and deterministically ordered.
- The service exposes the new operations through the existing attestation and token-authentication boundary.
- The Stage 3 files are additive relative to the Stage 2 base; the comparison shows no existing Stage 2 test suite was edited.

I also examined the test assertions and build notes. The reported 71/71 Stage 3 checks and 354 regression checks are Remmy's execution results. I reviewed the source and embedded outputs, but did not independently execute those suites.

### Secondary note

The resolution-anchor interpretation in build-notes item 5, choosing the latest accepted content-modifying contribution, is a defensible conservative reading of the post-modification rule. I would add a test with two successive modifications, with assessments between them, to pin that interpretation explicitly. I am not treating this as the present blocker.

There is also a small documentation inconsistency: the build notes describe the artifact as built to Rev 3 with the Rev 4 pin, while the build record identifies Rev 4 as the authority. Please align that description when recording the correction round.

### Gate and next step

Stage 3 remains held pending B1.

Preserve this commit unchanged as the examined round.

Make the transition-validation correction as a separate, explicit round, with negative replay tests.

Return the corrected source, tests, execution output and amended notes together for examination.

No live agents. No Stage 4 progression yet. The Stage 3 design settlement and Ben's prototype commission remain in force, but this implementation has not passed its gate.

The important thing here is that the machinery must not merely record the transitions it was told happened. It must refuse to reconstruct transitions that the constitution does not permit.
