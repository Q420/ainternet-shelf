# The room — environment design, Rev 2 (2026-11-24)

Derived from the accepted test programme (`ROOM-TEST-PROGRAMME-2026-11-24.md`,
accepted as the programme basis at INDEX 427) and carrying the examiner's
five findings on Rev 1 (INDEX 425) and her six refinements on the programme
map (INDEX 427). Rev 1 (`ENVIRONMENT-DESIGN-2026-11-24.md`) is preserved
unedited; this revision supersedes it as the operative design. Where Rev 1
settled a question the evidence has since reopened, this revision says so
and names the track that settles it. No implementation, provider request,
or demonstration is authorised by this paper.

**The principle, kept visible (the examiner's words):** *The room is not
supposed to make the worker behave. It is supposed to make the worker's
natural way of working safe.* Guidance belongs in the assignment,
materials, and skills. Control belongs at the boundary. Inside the room,
the worker has room to think and act through its own tools — Ben's
distinction: **guidance, not control.**

The authority distinction governs throughout: **environmental authority**
inside the room may be broad; **framework authority** outside it remains
the doorway's, unchanged. Accepting the room's output accepts it as the
worker's authentic contribution — never as true, accurate, or useful.

## 1. The shape (unchanged from Rev 1, restated)

One new offered tool — code execution — whose executor is a sealed,
per-run room stocked by the office from the case. Each invocation is an
ordinary doorway dispatch of a granted tool; the doorway checks the grant
and the call's shape and **does not police the command's contents**.
Authority over what a command can do lives in the room's walls. The room
**persists across successive calls within a run** (Rev 1 correction,
finding 4): one workspace per run, filesystem continuity between calls,
explicit process-tree cleanup at the run's end — a real workspace, not a
succession of disposable command boxes. In the first demonstration's
configuration the framework's retrieval tools are not offered
(room-only — that demonstration's selected configuration, **not** a
permanent prohibition on mixed configurations).

## 2. The interface — Track A's question, held open

Rev 1 proposed a single command-string argument. **That was an
assumption, and it is withdrawn.** The attempt-8 evidence shows a cmd
array (a shell invocation with a Python heredoc); the two forms are not
interchangeable, and Ben's principle governs: *we can't assume anything —
we have to let it tell us what it does.* The interface — the tool's name,
its argument representation, any further fields, and **the result form it
consumes** — is settled by Track A's non-executing probe, whose proposal
predeclares its trials, pacing, classifications, and decision criteria
before any provider request (programme refinement 1). Until Track A's
evidence lands and is examined, this section states the question and the
leading candidate (the evidenced cmd-array form), and nothing more. The
design's other sections are written to be independent of the interface's
eventual form.

## 3. The room and its stock — Tracks B and C

- **Stocked by the office from the case**, under a stocking manifest that
  accounts for **the complete contents of the room**: the assignment, the
  case's materials, the scratch space, the declared deliverable path —
  **and the complete executable environment** (shell, interpreter,
  binaries, libraries, temporary space, and the runtime dependencies the
  interface requires; finding 2). Nothing is in the room that the
  manifest does not name, the case materials and the runtime stock alike.
- **The stock grows only from observed reaches** (programme refinement
  4): Track A's observed invocations give the first evidence; in later
  work, a worker's failed reach is recorded as evidence of a missing
  capability — **not automatic authority to add it**. A proposed addition
  is examined against the room's purpose and boundary before the manifest
  changes.
- **Ephemeral across runs, persistent within one** (§1). The only things
  that leave a room are what the framework deliberately carries out: the
  deliverable and the record.
- **Mechanism** (Track B's to prove, not this paper's to assert): an
  unprivileged namespace sandbox of the bubblewrap kind — mount, network,
  and pid namespaces, a scrubbed environment — with a cgroup v2 resource
  envelope. Host availability facts stand as recorded in Rev 1
  (namespaces functional; Docker absent); availability is not isolation
  evidence.

## 4. Threat boundaries and witnessing — Track B (establishes), Track G (attacks)

The threat table of Rev 1 §4 stands (host filesystem, network egress,
credential reach, cross-case reach, host process interference, resource
exhaustion, persistence beyond the run, output smuggling), with the
witnessing model strengthened per finding 3 and programme refinement 2:

- **In-room pre-flight** (the boundary tested from inside): sentinel
  reaches — host file, network canary, sibling tree — plus enumeration of
  the room's own environment, visible processes, and filesystem, checked
  against the stocking manifest. Any successful reach refuses the room;
  the run never starts.
- **Host-side witness** (the mechanism established from outside):
  **independent of the room's own assertions — the room cannot certify
  its own isolation.** The witness records the actual configuration from
  the host: the mounted filesystem, the network interfaces and routes,
  the environment and credentials present, the visible process set, the
  cgroup containing the execution and its descendants, and whether any
  process can survive termination or escape the envelope.
- **The checker reconciles both views** (Track D). A wall that cannot be
  shown from both sides is a **failed wall** — the design changes, not
  the wording.
- **Track B establishes the boundary; Track G tries to break it**
  (programme refinement 3). B proves the mechanism prevents the specified
  reaches on this host; G tests resilience under hostile and confused use
  — mistakes, unusual command patterns, excessive activity, unexpected
  process behaviour. Neither substitutes for the other, and G always
  precedes any live demonstration.

## 5. Bounds inside the room

As Rev 1 §5: per-execution wall-clock, per-run execution budget inside
the activation's deadline, captured-output ceilings with truncation
marked, filesystem size ceiling, process-count ceiling, memory and CPU
in the cgroup envelope. A bound's exhaustion is a recorded termination
condition. Bounds are the office's, recorded at stocking — not the
worker's to see or set.

## 6. The record and the checker — Track D

As Rev 1 §6, under R2: the record captures the **observable execution
boundary** — stocking manifest, both witness views, per-execution
dispatch identity and command as proposed, process lifecycle, bounded
outputs, filesystem delta, resource consumption, termination condition,
the deliverable's hash taken at the wall — and **never claims the
worker's internal computation**. The checker reconstructs independently:
stocking equals manifest; the witness views reconcile; every execution
corresponds to a doorway dispatch; the deliverable's hash is continuous;
every termination stood inside the bounds. **Negative witnesses are part
of the track**: tampered records — mutated delta, missing witness,
swapped deliverable — must fail the checker, each shown failing; a
checker that also accepts tampered records has established nothing.

## 7. Integration — Track E

The execution tool is wired through the harness's **real** transport, and
the witnesses sit on that live seam — the BD-1 lesson (INDEX 419) as a
standing requirement: an internally correct commitment does not establish
what went over the wire. A full offline rehearsal (stub provider) walks
every hop — assembly, judgement, stocking, proposed executions,
dispatches, room execution, deliverable carriage, checker — with every
hop enumerated beside its witness, so an unwitnessed hop is visible as
one.

## 8. The demonstration — Track F, and the judgement — Track H

The standing assignment, unchanged, room-only, one run, separately
released; its paper must first answer how the assembly's mode is judged
for the room configuration. The claim fence of the certified direction
applies unchanged. Track H stands apart: accuracy checked against the
actual sources; usefulness is Ben's judgement; no engineering result in
Tracks A–G substitutes for it, and its outcome revises no engineering
verdict.

## 9. What this revision leaves open, deliberately

The interface (Track A); the mechanism's proven form (Track B); the
stock's final contents (Track C, from observed reaches); the evidence
shape's details (Track D, against the real rig). Each closes when its
track's evidence lands and is examined — by replacement of the relevant
section with the evidence, per the programme map, not by serial
correction rounds.
