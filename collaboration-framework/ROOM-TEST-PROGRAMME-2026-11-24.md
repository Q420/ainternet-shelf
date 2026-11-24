# Testing the room properly — the full track map (2026-11-24)

Written at Ben's direction: "Let's break down every track we need to make
in order to test this properly instead of going back and revising it one
by one." This map names every track the room line needs, what each track
establishes, what proves it, and what it waits on — stated whole, up
front, so tracks pass or fail as wholes instead of dribbling through
serial revision rounds (the adapter brief's Rev 1–9 grind is the pattern
this replaces). It is a planning paper: it authorises nothing. Each track
that touches the provider or a live worker still passes its own release
examination, and the build tracks still pass build examination, exactly
as the programme's discipline stands. Ben's principle governs every
track: **we can't assume anything — we let it tell us what it does.**

## Track A — The interface: let it tell us

**Establishes:** the execution tool's real interface — the name it answers
to, the argument representation (the attempt-8 evidence shows a cmd
array; the design paper assumed a string; neither is settled), any extra
fields it uses, and the result form it works from.
**How:** non-executing live probes on the pinned model. Offer the
execution-tool definition in the evidenced forms; capture the complete
responses under the standing evidence discipline; classify accepted call
vs provider refusal vs other shapes. A second stage may return a canned
result — labelled as simulated, executing nothing — to observe how it
continues: what it invokes next is the runtime stock's first evidence
(Track C). Pacing and provider budget per the operational accounting.
**Proves it:** settled observations across repeated trials, examined —
the interface section of the design is then written from them, not
before them.
**Waits on:** a release examination for the probe, as every live probe
line before it.

## Track B — The room itself: the walls are real on this host

**Establishes:** that the proposed mechanism (namespace sandbox, cgroup
envelope) actually isolates, on the framework's real host — not in
principle, not by its label.
**How:** entirely offline. Build the room construction as a test rig.
Host-side witness tooling records the actual configuration (mounted
filesystem, interfaces and routes, environment, visible processes,
cgroup membership). In-room pre-flight attempts the sentinel reaches
(host file, network canary, sibling tree). Adversarial rig tests:
backgrounded processes and daemonisation, /proc and host-path reaches,
network connects and name resolution, attempts to survive termination.
Envelope tests: fork bomb, disk fill, memory blow, CPU spin — each must
be contained and recorded.
**Proves it:** an evidence pack where every wall is shown from **both**
sides — the mechanism in force (host-side) and the reach failing
(in-room) — reconciled. Any wall that cannot be shown both ways is a
failed wall, and the design changes, not the wording.
**Waits on:** nothing but the design paper's acceptance as a basis
(INDEX 425). Runs parallel to Track A.

## Track C — The runtime stock: the room is equipped

**Establishes:** the complete contents of a working room — shell,
interpreter, binaries, libraries, temporary space — as a manifest with
versions, each item present because the work needs it.
**How:** the initial stock is drawn from the evidence (Track A's observed
invocations; the attempt-8 heredoc's Python; the reading/sorting the
assignment implies). A stock-verification step runs at stocking time in
every later track: the room executes a smoke set (shell runs, interpreter
runs, the reading tools work) and the results enter the record. The stock
grows only from observed reaches — when the worker reaches for something
absent, the absence returns as data and the reach is recorded; nothing is
added on a guess.
**Proves it:** the manifest is complete against the smoke set and the
observed reaches; a stock change is a manifest revision with its reason
recorded.
**Waits on:** Track A's first evidence and Track B's rig.

## Track D — The record and the checker: evidence honesty

**Establishes:** that what the room did can be independently
reconstructed — and nothing beyond it claimed (R2).
**How:** entirely offline, against Track B's rig with a scripted stand-in
worker issuing deterministic commands. Define the execution evidence
shape (dispatch identity, command as proposed, process lifecycle,
bounded outputs, filesystem delta, resource consumption, termination
condition) plus the host-side witness records. Extend the checker to
reconstruct: stocking equals manifest; both witness views reconcile;
every execution corresponds to a doorway dispatch; the deliverable's hash
is continuous from the wall to the record; every termination stood inside
the bounds. **Negative witnesses are part of the track**: tampered
records — a mutated filesystem delta, a missing witness, a swapped
deliverable — must fail the checker, each shown failing.
**Proves it:** the checker passes the true record and fails each tampered
one, for stated reasons.
**Waits on:** Track B's evidence shapes.

## Track E — The doorway integration: the live path is the witnessed path

**Establishes:** that the path a live run actually travels is the path
the witnesses certify — the BD-1 lesson (INDEX 419) turned into a track
of its own, so it cannot recur silently on this line.
**How:** offline, with a stub provider. The execution tool is wired
through the harness's real transport; witnesses capture the transmitted
body at the live seam itself. A full rehearsal runs the whole path:
assembly, judgement, room stocking, stub responses proposing executions,
doorway dispatches, the room executing canned commands, the deliverable
carried out, the checker over the result. Every hop the rehearsal travels
is a hop a witness covers — enumerated, so an unwitnessed hop is visible
as one.
**Proves it:** the rehearsal evidence pack, examined, with the hop list
and its witnesses reconciled.
**Waits on:** Tracks A (interface settled), B, C, D.

## Track F — The live demonstration: one run, separately released

**Establishes:** the certified claim, and no more: a generated worker,
given its own tool inside a case-stocked room, completing the standing
assignment under the record.
**How:** the standing first-worker assignment, unchanged, in the
room-only configuration (accepted for this demonstration, INDEX 425). One
open design question the track's paper must answer first: how the
assembly's mode is judged for the room configuration. Pacing, deadline,
and bounds per the standing accounting; refusal is a recorded delivery
failure; the complete result, checker evidence included, returns for
examination; accuracy and usefulness are judged separately, as always.
**Proves it:** the run's record, examined whole.
**Waits on:** every prior track, and its own release examination. Ben
gets the heads-up before it runs, as with native1.

## Track G — The hostile and confused worker: the walls under pressure

**Establishes:** that the room holds not only for a cooperative worker
but for a wrong one — before any live worker is ever inside it.
**How:** scripted adversarial suites against the rig, no model involved:
escape attempts, exfiltration to the canary, fork bombs, disk fills,
supervisor kills, writes outside the deliverable path, attempts to read
the record itself; and the confused-worker cases — malformed commands,
endless loops, enormous outputs. Each must end as a recorded termination
with the walls intact and the host unharmed.
**Proves it:** the suite's evidence pack: every case contained, every
termination recorded, no case reaching outside.
**Waits on:** Tracks B and C. Runs before Track F, always.

## Track H — The usefulness judgement: separate, and Ben's

**Establishes:** whether the work product is any good — a different
question from every engineering verdict above.
**How:** if Track F produces a brief, its accuracy is checked against
the sources line by line, and its usefulness is Ben's judgement, as it
has been throughout. No engineering pass in Tracks A–G says anything
about this track, and this track's outcome revises no engineering
verdict.
**Waits on:** Track F.

## The order

A and B start in parallel — one asks the model, the other tests the
host. C follows their first evidence. D follows B. E follows A–D. G
follows B–C and always precedes F. F is last and separately released. H
is Ben's, after F. The design paper's Rev 2 is written from this map:
its open questions are exactly the tracks' open questions, and it is
revised when a track's evidence lands — by replacement of the relevant
section with the evidence, not by serial correction rounds.
