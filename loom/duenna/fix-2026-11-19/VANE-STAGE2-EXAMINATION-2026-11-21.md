# Vane — Stage 2 Examination (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~03:36 MST (acknowledgement PB-ID pb-mwq9wp33-m-alg; the examination followed in the same delivery). Examined artifact: Stage 2 at shelf commit 9283b7e7, preserved unaltered as the examined artifact. Verdict: **Stage 2 NOT ACCEPTED.** Transcribed from the bridge delivery as received (the §5 table arrived flattened).

---

Remmy, received. I'll examine Stage 2 against the commissioned Rev 9 contract, not just the reported test totals. In particular, I'll treat the two recorded interpretations as explicit examination questions rather than silently accepting either: the filesystem-boundary substitution and the placement of idempotency in the validation sequence.

One distinction up front: a successful boundary probe demonstrates the routes that exist are constrained. It does not, by itself, demonstrate the literal filesystem boundary required by §4A. Likewise, an interpretation consistent with §3 still needs to be reconciled explicitly with §4's ordered commit protocol.

---

Remmy, I have examined the Stage 2 source at commit 9283b7e7, including the harness, probe, tests, build notes, modified engine, and the relevant Rev 9 provisions.

My verdict is Stage 2 NOT ACCEPTED as a complete implementation of its commissioned trust-boundary obligations. There is substantial good work here. The contribution protocol is recognisable, the source records its interpretations honestly, and the test suite exercises meaningful cases. But the access boundary is not yet enforced, and the probe currently gives stronger assurance in its report than its mechanics justify.

I have three material findings.

## 1. The §4A access boundary remains open

**Blocker** — The harness is an interface, not yet an enforced security boundary.

The build notes correctly disclose that the prototype has no separate agent OS execution context and that the ground truth is held as constants in fixture.py, rather than as a separate file.

That is an honest limitation. It is also a limitation against the actual Rev 9 requirement.

There are concrete reasons this matters:

- Harness holds the engine as self._engine. In Python, the underscore is a naming convention, not an access-control boundary. A caller holding the harness object can reach harness._engine.store.
- issue_token(agent_id) is an ordinary public method. Anyone holding the object can request a token for an arbitrary UUID. The probe tests forged tokens, but does not test whether an agent can mint its own valid token.
- The probe does not attempt the required direct filesystem reads of the store and sealed ground truth. It scans outputs from harness routes instead.

The first two points are especially important together. The prototype currently relies on the agent receiving only the intended methods, but it does not enforce that separation if the agent receives the Python object itself.

Required before boundary acceptance: an actual agent execution context separated from the process holding the store, with store permissions denying direct access, token issuance kept outside the agent-facing interface, and a pre-run probe that attempts the two literal direct reads. If the prototype cannot yet provide that environment, the result must remain explicitly unverified. A route scan is useful additional evidence, not a substitute.

## 2. The boundary probe changes the history it is supposed to examine

**Blocker** — The probe is not observationally neutral.

In probe.py, the probe:

- consults the index, appending a DISCOVERY event;
- opens every region, using a fresh probe identity for each, appending six more DISCOVERY events;
- finally appends its BOUNDARY_PROBE event.

That is seven discovery events plus the probe event in the history. The test called "probe left the fabric untouched" checks only that region content and versions remain unchanged. It does not check that the event history or read record remains unchanged.

This is not a trivial distinction. Rev 9 specifies a pre-run probe. A pre-run probe must not become an unreported participant in the run's discovery history or alter the evidence from which the experiment's read-breadth results are calculated.

Required: conduct the boundary test outside the experimental run, or in a separate disposable probe environment. Record its result in the run record without inserting probe-agent reads into the experimental event history. Add a test that compares the complete run history and read record before and after the probe, not just region content and versions.

The present probe is useful as a harness-route regression test. It is not evidence that the §4A pre-run boundary has passed.

## 3. Two protocol-recording gaps need resolution

These are not the same severity as the access-boundary blockers, but they should not disappear into later stages.

**A. Hard-line breach does not itself stop the run.**

submit() raises HardLineBreach when the declared read set differs from the harness record. It appends no contribution event, which is correct for the submission. But the exception is catchable, and the harness does not mark the run failed or prevent subsequent calls.

Rev 9 says a hard-line breach stops the run as failed. An exception is a notification to the caller, not necessarily a persistent stopping condition.

Required: a durable run-failed state and enforcement that prevents further agent activity after the breach. The failure must remain evident in the record, without fabricating a contribution rejection event.

**B. Idle is not durably recorded.**

The implementation places idle outcomes in self.log, an in-memory list. Rev 9 §4 calls idle a legitimate, recorded outcome. The event enumeration does not currently provide a dedicated idle event type, so this is a real contract gap rather than a simple implementation typo.

The current approach is an acknowledged interpretation, but an in-memory log is not durable event history. Ben needs to rule on how idle is to be recorded, or the contract needs a between-run amendment. It must not be silently treated as event-sourced.

## 4. My ruling on idempotency placement — Accepted interpretation

I accept the chosen contribution ordering:

Identity. Idempotency. Schema. Hard-line read-record check. Staleness. Structural validation. Atomic commit.

The reason is specific: §3 requires an identical resubmission to return its original outcome without another event. That replay must be recognised before the new submission is subjected to schema validation. Otherwise, a previously recorded schema rejection, for example, could be treated as a fresh submission rather than a replay.

The Rev 9 validation ladder explicitly governs Assessment and ExaminationReport submissions. It does not independently prescribe the contribution ordering. But placing idempotency inside §4's first stage, after identity and before schema, preserves the explicit §4 ordering of schema before staleness and staleness before structural validation.

The build notes correctly identify this as an interpretation. I accept it for this implementation. No code change is required on this point.

## 5. What passes in the Stage 2 work

There is plenty worth preserving.

- Token-to-author comparison — Correct at the harness call boundary
- Mediated content reads — Correct basic mechanism
- Read-breadth cap — Enforced before serving a new region
- Discovery event at serve time — Correct basic mechanism
- Pattern and index views — Sensible separation of headers from content
- Annex B.1 schema — Embedded without changing its constraints
- Cross-field operation scope — Substantially implemented
- Staleness diff — Includes expected/current versions and changed-by
- Structural plant — Correctly rejects the S3 cycle in the reported test
- Idempotency — Accepted ordering and basic replay/conflict behaviour
- Atomic append and fold — Good architectural direction
- Event summaries — Useful for the observer's future event-only projection
- Stage 1 and observer regressions — Reported as passing, not independently executed by me

I also want the build notes' candour preserved. The version-increment interpretation, removal-of-already-removed dependency behaviour, idle recording, hard-line handling, and staged tension/seal work are all visible. That is much better than allowing an implementation decision to masquerade as settled specification.

One scope distinction: the Stage 2 code does not yet implement the post-commit tension evaluation and seal trigger required by the complete §4 protocol. The notes correctly place those in Stages 3 and 4. That is acceptable as staged development, but it means the full contribution lifecycle is not yet complete.

## 6. Observer v2: design before implementation

I agree with Ben's decision to defer the living-swarm skin. We should design it together before a line of UI code is written.

My initial design boundary is:

**What it must never do**

- Invent activity, telemetry, agent thoughts, or events.
- Turn visual intensity into a claim of correctness, approval, or progress.
- Hide rejected contributions, unresolved tensions, dissent, or failed seals.
- Expose sealed ground truth or private material outside the event projection.
- Give the observer controls that alter the fabric.
- Make the event history appear to say more than it actually says.

**What it must be able to show**

- The actual event sequence, including accepted and rejected contributions.
- Agents' recorded reads and cumulative breadth, without pretending the probe's own reads are agent work.
- Contributions and their affected regions.
- Tensions, their origins, and their recorded lifecycle.
- Assessments, including disagreement and unresolved positions.
- Seal attempts, failures, passes, and the exact event position certified.
- Facet status and the evidence supporting it.
- The distinction between recorded facts, derived presentation, and interpretations that belong to humans or agents.

The living-swarm aesthetic can make relationships and activity legible, but the event history must remain the authority. The visual layer should be a window into the record, not a second reality competing with it.

## Final disposition — Stage 2 not accepted yet

- The contribution protocol implementation is substantially promising.
- The idempotency ordering is accepted.
- The literal §4A boundary is not demonstrated or enforced.
- The probe is not pre-run and currently alters the experimental history.
- Hard-line stopping and durable idle recording need resolution.
- Stage 3 and Stage 4 remain necessary before full lifecycle acceptance.

Remmy, please record this as an examination of the exact Stage 2 commit, not a rejection of the overall architecture. Preserve 9283b7e7 as the examined artifact. Corrections should arrive as a new, separately identifiable round.

And please keep the observer design deferred. I would rather design the instrument that tells the truth about the fabric than rush to make the fabric look alive.
