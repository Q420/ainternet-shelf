# The room — environment design and threat boundaries (2026-11-24)

A design paper for examination, under the certified direction
(`OWN-TOOL-FIRST-DIRECTION-2026-11-24.md`, certified at INDEX 423). No
implementation, provider request, or demonstration is proposed or
authorised by it. The examiner's two protections from the certification
are carried here as requirements **R1** (the boundary is real and
independently witnessed) and **R2** (the record distinguishes observable
execution from unobservable internal computation). The authority
distinction she protects governs throughout: **environmental authority**
inside the room may be broad; **framework authority** outside it remains
the doorway's, unchanged. Accepting the room's output accepts it as the
worker's authentic contribution — never as true, accurate, or useful;
those judgements stay where they have always been.

## 1. The shape in one paragraph

The worker is offered one new framework tool — a code-execution tool in
the form the model already reaches for — whose executor is a sealed,
per-run environment (the room) stocked by the office from the case. Each
invocation is an ordinary doorway dispatch of a granted tool, so the
record keeps a per-execution event; what changes is the control: the
doorway checks the grant and the call's shape, and **does not police the
command's contents**. Authority over what a command can do lives in the
room's walls, not in argument inspection. Inside the room the worker runs
ordinary shell tools against the case's materials and composes its
deliverable. Nothing else about the framework changes.

## 2. The tool

- **Offered natively**, under the execution name and argument form the
  evidence shows the model using (a single command string, a working
  directory inside the room, captured standard output/error and an exit
  code returned). Because the tool is offered and granted, its calls
  arrive through the passed native adapter like any other offered call —
  no unoffered-name problem arises for it.
- **Arguments are data, recorded verbatim.** The command string is carried
  in the record exactly as proposed. The framework never executes any part
  of it outside the room, and the doorway's schema check covers the
  call's shape only (a command string, a directory inside the room) —
  the deliberate relocation of control the direction rules.
- **Results return as bounded data**: exit status, and output captured
  under the ceilings of §5, with truncation marked as truncation.

## 3. The room

- **Stocked by the office from the case**, as the briefcase design already
  settles: the assignment, the case's source materials copied in, a
  scratch space, and the declared deliverable path. A stocking manifest
  (paths + hashes) is recorded before activation; the room contains
  nothing the manifest does not name.
- **Ephemeral**: created for one run, destroyed at its end. The only
  things that leave are what the framework deliberately carries out — the
  deliverable and the record.
- **Mechanism proposed**: an unprivileged namespace sandbox of the
  bubblewrap kind — mount namespace with only the room's tree bound in,
  a network namespace with no interfaces, a pid namespace, a scrubbed
  environment — with the run's resource envelope applied through cgroup
  v2. Host facts, from a read-only check on 2026-11-24 (labelled as host
  facts, not as build evidence): `unshare`, `bwrap`, and `systemd-run`
  are present on the framework's host; user/mount/network/pid namespaces
  demonstrably function; cgroup v2 is mounted; **Docker is not present**,
  so no container mechanism is proposed. The build, if one is ever
  scoped, must still witness the mechanism's behaviour itself — this
  paper's host check establishes availability, not isolation.

## 4. Threat boundaries (R1)

For each threat: the enforcing mechanism, and the **independent witness**
that establishes it. The witnesses are per-run: before activation, the
office plants sentinels outside the room and the room's own pre-flight
attempts each reach; **every attempt must fail, the failures are recorded,
and a single success refuses the room — the run never starts.** A
one-time build claim is not a witness; the boundary is re-proven each
run, cheaply, from inside the room itself.

| Threat | Enforcement | Witness |
|---|---|---|
| Host filesystem reach | Mount namespace; only the room's tree bound in; the rest of the host filesystem not mounted at all | Pre-flight tries to read a sentinel file planted on the host outside the room; the open must fail |
| Network egress (any destination, incl. the provider) | Network namespace with no interfaces and no route | Pre-flight tries to connect to a canary listener on the host and to resolve a name; both must fail |
| Credential reach | Environment scrubbed at construction; no vault, connector, or host paths bound in; the room's environment carries only what the stocking manifest names | Pre-flight enumerates its own environment and top-level tree into the record; the checker compares both against the manifest — anything unnamed fails the run |
| Cross-case reach | One room per run; no other run's tree bound in; rooms destroyed at run end | Pre-flight tries a sentinel planted in a sibling path outside its own tree; the open must fail |
| Host process interference | Pid namespace (host processes invisible); the room's processes run under a mapped, unprivileged identity | Pre-flight lists its visible processes into the record; only its own tree may appear |
| Resource exhaustion of the host | cgroup v2 envelope (§5) applied before activation; the room's processes die with the run | The envelope's presence and values are recorded at stocking; consumption is in the record (§6) for the checker to compare |
| Persistence beyond the run | The room is destroyed; only the framework's deliberate carriage (deliverable + record) survives | Post-run, the office records the room path's absence; the deliverable's hash is taken at the wall before destruction (§6) |
| Output smuggling | The deliverable and all returned output are data — hashed, carried, never executed or interpreted by the framework | The record carries hashes, not executions; nothing in the framework's path runs room output |

## 5. Bounds inside the room

Per-execution wall-clock limit; a per-run total execution budget inside
the activation's standing deadline; captured-output ceilings per
execution with truncation marked, never silent; a filesystem size ceiling
for the room's tree; a process-count ceiling; memory and CPU ceilings in
the cgroup envelope. A bound's exhaustion is a recorded termination
condition (§6), not an error to be retried around.

## 6. The record (R2)

**Captured — the observable execution boundary:** the stocking manifest;
the boundary witnesses' results; for each execution, the dispatch identity
beside the command as proposed, the process's start and termination
(exit code or signal), its captured output under the ceilings, its wall
time and recorded resource consumption, and its termination condition
(completed / timed out / killed / ceiling reached); the room's filesystem
delta (files created or changed, with hashes, at run end); the
deliverable's hash taken at the wall.

**Not captured, and never claimed:** the worker's internal computation —
what a command's process thought about, intermediate states inside a
single execution beyond its observable effects, anything not crossing
the boundary. The record says what the evidence establishes, in the
evidence's own terms.

**The checker reconstructs, independently:** that the room was stocked
exactly as the manifest declares; that every boundary witness failed to
reach as required; that each recorded execution corresponds to a doorway
dispatch of the execution tool under the case's grants; that the
deliverable that left the room is the deliverable whose hash was taken at
the wall; and that every termination stood inside the bounds. Its claims
stop exactly at the evidence — the same discipline as the native line's
checker, applied to a new evidence shape.

## 7. A configuration decision, proposed for examination

In the room configuration, the framework's retrieval tools are **not**
offered: the assignment's materials are inside the room, and the worker
reads and sorts them with its own tool, as the direction intends. This
keeps one clear authority surface per configuration — the doorway's tools
or the room — and the first demonstration (§8) would run room-only.
Flagged openly as this paper's judgement call, the examiner's to rule on.

## 8. The first demonstration, in shape only

Not authorised; scoped and released separately if the design passes. The
standing first-worker assignment, unchanged, in the room configuration:
the worker reads the three sources inside its room and writes the brief
to the declared deliverable path. Success is the brief carried out of the
room under the record — judged for accuracy and usefulness separately,
exactly as before. The certified claim fence applies unchanged.

## 9. Open questions for the examiner

Whether per-run sentinel witnessing is the right cadence, or whether some
witnesses belong at build verification with per-run spot checks; whether
the deliverable's filesystem delta should be captured per-execution or at
run end (this paper proposes run end, with per-execution output captured
as it returns); whether the execution tool should also be available in
mixed configurations later, or room-only is a standing rule; and whether
the resource envelope's values belong in the case (proposed: bounds are
the office's, recorded at stocking, not the worker's to see or set).
