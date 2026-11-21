# Rev 17 Correction Plan — §3.5 Process Model, Descriptor Protocol, D-9 Chronology

**Prepared by Remmy, 2026-11-13, against Alex's Rev 16 inspection
(pb-mwflcjg1-3-lf5g).** For Alex's independent pass BEFORE incorporation,
as he offered. Rev 16 (5373a416) is preserved unchanged. On his pass, this
plan is incorporated into Rev 17 as a REWRITE of the §3.5 process sequence
in the body itself — not as another amendment layer laid over text that
says the opposite. Three processes are named at every stage: the
**SUPERVISOR** (Python, `pilot-supervisor` identity, long-lived per run),
the **LAUNCHER** (C, setuid-root, one per run), the **CHILD** (the harness,
`pilot-harness` identity after its transition).

---

## Part 1 — The corrected §3.5 process sequence

**Stage 0 — Preparation (SUPERVISOR).** The supervisor's dedicated
spawning thread — which SHALL remain alive for the launcher's entire
lifecycle (correction B) — creates the status channel (Part 2), captures
its own PID as the *expected supervisor PID*, and computes every
pre-launch issuance precondition from the record itself. Nothing about
the run is taken from the harness.

**Stage 1 — Spawn (SUPERVISOR → LAUNCHER).** The supervisor executes the
launcher with the run identifier as its sole argument (Batch 0 interface
freeze, unchanged). The launcher inherits exactly one descriptor: the
status-channel end, with close-on-exec cleared for that descriptor only;
every other descriptor is close-on-exec. The supervisor retains its own
channel end and the spawning thread.

**Stage 2 — Launch request (SUPERVISOR → LAUNCHER).** The supervisor
sends LAUNCH_REQUEST (Part 2), carrying the expected supervisor PID. The
launcher validates the run identifier (frozen pattern) and the request's
shape; any defect → ABORT behaviour: exit non-zero, spawn nothing.

**Stage 3 — Fork and child establishment (LAUNCHER → CHILD).** The
launcher creates the gate pipe (as in the present design), forks. In the
CHILD, before any privilege transition: PR_SET_PDEATHSIG = SIGKILL is
armed against the launcher (the child's parent — the relationship §0B.1
preserves), then the pinned privilege-transition sequence runs, then the
child blocks reading the gate pipe. The child's pinned two-branch rule is
unchanged: the release byte, and only the release byte, proceeds to the
exec; anything else, including EOF, `_exit()`s.

**Stage 4 — pidfd handoff (LAUNCHER → SUPERVISOR).** The launcher calls
pidfd_open on the child and sends PIDFD_HANDOFF (child PID + the pidfd as
SCM_RIGHTS ancillary data). The SUPERVISOR validates: the received
descriptor is a pidfd, and the process it denotes has the stated PID
(pidfd identity check via /proc/<pid> stat start-time comparison recorded
in the run record). On success the supervisor stores the handle and
replies HANDOFF_ACK. **No part of the launch proceeds past this stage
without the ACK.** Transfer failure, validation failure, a malformed
packet, or channel EOF here → the launch aborts: the launcher kills the
child (it is the parent; the child's PDEATHSIG covers launcher death in
any case), reaps it, and exits non-zero; the supervisor records
LAUNCH_ABORTED with the stage and reason. The gate has not been released;
no issuance exists.

**Stage 5 — Launcher settles (LAUNCHER).** After the ACK, the launcher:
drops root to the `pilot-supervisor` uid; arms its own PR_SET_PDEATHSIG
against the supervisor; reads the setting back; verifies getppid()
equals the expected supervisor PID from LAUNCH_REQUEST (correction A).
Any failure → it kills and reaps the child, sends ABORT if the channel
still lives, and exits non-zero; the supervisor records LAUNCH_ABORTED.
On success it sends GATE_READY.

**Stage 6 — Gate release (SUPERVISOR decides; LAUNCHER actuates).**
Gate-release authority is the SUPERVISOR's alone: it releases only when
every issuance precondition it computed at Stage 0 still holds, and it
sends RELEASE. Only on RELEASE does the launcher write the release byte
to the gate pipe; the child execs the harness. The launcher never
releases on its own judgement.

**Stage 7 — The run.** The LAUNCHER blocks in waitpid() on the child —
it alone holds that relationship. The SUPERVISOR independently observes
the child through the pidfd (poll for termination) and owns the record:
every committed value is computed by the supervisor from the record
file; every issuance is the supervisor's act. The harness asks for
nothing and reports nothing that is taken as fact.

**Stage 8 — Termination and closure.** The child terminates. The
launcher's waitpid() reaps it; the launcher sends STATUS (child PID +
raw wait status) and waits for STATUS_ACK before exiting 0 — launcher
exit means exactly that the status word was delivered and acknowledged
(§0B.1). The SUPERVISOR closes the terminal event only when BOTH agree:
the STATUS word (exit basis from the OS via the parent) and its own
pidfd observation of termination. Agreement → the terminal event is
written from those facts. Disagreement, or pidfd termination with no
STATUS (Stage 9), → the issuance is UNRESOLVED and the run halts pending
recovery; nothing is written as finished on a guess.

**Stage 9 — Failure branches.**
- *Launcher dies before the handoff:* channel EOF, no pidfd held → the
  launch is void. The child was never released and dies by its
  PDEATHSIG against the launcher. Supervisor records LAUNCHER_LOST
  (pre-release). No issuance.
- *Launcher dies after release:* the child receives SIGKILL by its
  PDEATHSIG. The supervisor observes actual child termination on the
  pidfd — termination is PROVEN by the handle, not inferred from EOF.
  Channel EOF without STATUS → terminal closure as CRASH with basis
  LAUNCHER_LOST and exit status recorded as UNKNOWN (never invented);
  the pidfd supplies the fact and time of termination.
- *Supervisor dies:* the launcher's PDEATHSIG fires; the launcher
  exits; the child's PDEATHSIG fires in cascade; the child dies. No
  terminal event is written by anyone. At its next start the supervisor
  records SUPERVISOR_LOST against the still-open issuance, which remains
  UNRESOLVED until examined.
- *Malformed or out-of-order protocol traffic at any stage:*
  pre-release → abort as Stage 4; post-release → PROTOCOL_VIOLATION
  recorded, run halts, issuance UNRESOLVED.

**Supersession in the body.** Rev 17 rewrites §3.5 points 2–3 (spawn,
privilege transition, gate, supervision, issuance) to this sequence and
conforms every reference to the old fused parent-supervisor (including
"the parent runs as the run's supervisor", self-issuance by the parent,
and the ordering invariant, restated as: the supervisor's observation
handles — pidfd held, channel live, record open — are fully established
before the harness begins work). §0B.1 remains the governing summary and
is conformed in wording only where this plan is more precise.

## Part 2 — The descriptor protocol (operative definition)

**Channel.** One Unix socketpair, type SOCK_SEQPACKET, created by the
SUPERVISOR before the spawn. End S: supervisor's, close-on-exec set.
End L: launcher's, inherited across the launcher's exec with
close-on-exec cleared for this descriptor only; the supervisor sets
close-on-exec on every other descriptor it holds before spawning. The
gate pipe is separate, created by the LAUNCHER pre-fork as in the
present design; it is not part of this protocol.

**Framing.** SEQPACKET preserves packet boundaries: one packet is one
message, received whole or not at all — a partial message cannot be
observed on this channel, and a receive returning EMSGSIZE is a
malformed message. Every message is: 1 byte type, 2 bytes payload
length (big-endian, MUST equal the packet's payload size), then the
payload. Unknown type, length mismatch, or a message out of the stage
order defined in Part 1 is malformed.

**Message catalogue.**
- `0x01 LAUNCH_REQUEST` (S→L): expected_supervisor_pid (u32 BE).
- `0x02 PIDFD_HANDOFF` (L→S): child_pid (u32 BE) + exactly one pidfd
  attached as SCM_RIGHTS. A handoff with no descriptor, or more than
  one, is malformed.
- `0x03 HANDOFF_ACK` (S→L): result (u8: 0 = accepted; non-zero =
  rejected, launch aborts).
- `0x04 GATE_READY` (L→S): empty payload.
- `0x05 RELEASE` (S→L): empty payload. Sent once, only by the
  supervisor, only after HANDOFF_ACK.
- `0x06 STATUS` (L→S): child_pid (u32 BE), wait_status (u32 BE, the raw
  status word from waitpid()).
- `0x07 STATUS_ACK` (S→L): empty payload. The launcher exits 0 only
  after sending STATUS and receiving STATUS_ACK.
- `0x08 ABORT` (either direction): stage (u8), reason (u8). Sent when
  the channel still lives; the sender then closes its end and exits /
  records per Part 1.

**EOF semantics.** EOF on the supervisor's end before STATUS means the
launcher is gone (branch per Stage 9, keyed on whether the pidfd is
held and whether RELEASE was sent). EOF on the launcher's end means the
supervisor is gone; the launcher's PDEATHSIG makes this unreachable in
the defined model, and if observed the launcher kills and reaps the
child and exits non-zero.

**Supervisor-side child observation.** The pidfd is polled for
termination (POLLIN). Termination observed on the pidfd with a STATUS
already received closes per Stage 8; termination observed without
STATUS closes only the factual record of termination (Stage 9), never
an invented exit status.

## Part 3 — D-9 source-pinning chronology (body corrections)

The sequence is fixed as: **Batch 0 freezes behaviour and interface →
launcher source is written against that interface → source is pinned by
sha256 by dated addition and inspected → the D-9 disposition is recorded
→ only then may Batch 4 begin.** The Batch 4 checkpoint records the
BUILT BINARY and its evidence; it is not a source-pinning event.

Two body texts are corrected in Rev 17 to say exactly this: §3.5 point 2
(the phrase "pinned by sha256 in the re-freeze amendment (by dated
addition at the Batch 4 checkpoint, when it is built)" is replaced by
the sequence above) and §4's Batch 4 paragraph ("its source is pinned
by dated addition at this checkpoint" is replaced by: the source was
pinned and inspected before this batch began, per §0B.3; this checkpoint
records the built binary's sha256 and the SE-7 evidence).

## Part 4 — C-rationale evidence qualification

§0B.2(3) is reworded in Rev 17: the toolchain sentence becomes a pin
requirement, not a custody claim — "the compiler, linker mode and
dependency set actually used are recorded in the Batch 4 evidence and
are inspectable" — and the comparison with other compiled languages is
labelled a recorded preference with its reasons. §0B.2(2)'s "no runtime
services" is tied to demonstration: the property is established from
the built binary at SE-7 (dynamic section absent, or every dynamic
dependency pinned by hash), never asserted from the language choice.

---

**Asked of Alex:** his independent pass on (1) the Part 1 sequence —
stage ownership, the handoff/ACK interlock, the failure branches;
(2) the Part 2 protocol — framing, catalogue, EOF semantics;
(3) Parts 3–4 as drafted corrections. On his pass, Rev 17 incorporates
this plan as a body rewrite of §3.5 plus the conformed passages, and is
shelved for his full inspection.

— Remmy, 2026-11-13
