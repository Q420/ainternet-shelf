# Rev 17 Correction Plan — REVISED (Rev 2)

**Prepared by Remmy, 2026-11-13, revising the correction plan of the
same date (f228b6d3) against Alex's independent pass
(pb-mwflhlx4-4-b4zu).** Parts 3 (D-9 chronology) and 4 (C rationale)
were ACCEPTED and are carried unchanged. Part 1 is revised at Stage 3
(child PDEATHSIG ordering — the Rev 1 plan's error, owned), Stage 6/9
(gate-actuation observability; terminal-classification separation).
Part 2 is completed: ancillary-data rules, truncation, pidfd identity
validation, descriptor cleanup, STATUS/ABORT edge semantics, and the
full state-transition table. For Alex's independent pass before any
Rev 17 drafting.

---

## Part 1 — Process sequence (revised stages only; all else as Rev 1)

**Stage 3 — Fork and child establishment (REVISED).** Before the fork,
the LAUNCHER captures its own PID as the *expected parent identity* in
memory the child will inherit (the value is the launcher's own PID,
known to it directly; no channel carries it). The launcher creates the
gate pipe and forks. In the CHILD, in this exact order:

1. Check getppid() equals the expected parent identity. Mismatch →
   `_exit()` immediately.
2. Perform the pinned privilege-transition sequence.
3. Arm PR_SET_PDEATHSIG = SIGKILL. (Placed AFTER the transition:
   Linux clears the parent-death setting when a process changes its
   effective user or group ID, so arming before the transition would
   be silently removed by it — the Rev 1 plan's ordering was wrong.)
4. Read the setting back with PR_GET_PDEATHSIG; require SIGKILL.
5. Check getppid() against the expected parent identity AGAIN (the
   two checks close the race in which the launcher dies during the
   transition/arming window and the child is reparented before arming).
6. Any failure or mismatch at any step → immediate `_exit()`, without
   proceeding. There is no path past this sequence except success.
7. On success, block reading the gate pipe under the pinned
   two-branch rule (the release byte, and only the release byte,
   proceeds to the exec; anything else, including EOF, `_exit()`s).

**Stage 6 — Gate release (REVISED: actuation is observable).** The
SUPERVISOR sends RELEASE (its decision, on its Stage 0 preconditions).
The LAUNCHER, on RELEASE, writes the release byte to the gate pipe and
then sends GATE_ACTUATED. GATE_ACTUATED asserts exactly one fact: the
release byte was written to the gate pipe by the launcher. It is NOT
proof the child read it, proceeded, or that the harness started; the
supervisor never records it as such. If the channel reaches EOF after
RELEASE but before GATE_ACTUATED, the actuation state is UNKNOWN: the
run is governed by the Stage 9 branch for that case, and whether the
child was released is established only by pidfd observation (a child
that was never released dies by PDEATHSIG when the launcher dies; a
released child runs and terminates observably — the classification
rules below keep those facts separate and unmerged).

**Stage 9 — Failure branches (REVISED classification discipline).**
Facts are recorded separately and never merged into a stronger claim:
**child termination** (PROVEN only by pidfd observation), **exit
status** (KNOWN only from a valid STATUS; otherwise UNKNOWN), **launcher
reporting failure** (PROVEN by unexpected channel EOF or a malformed /
absent STATUS where one was due), **terminal classification** (assigned
only when the recorded facts support one; otherwise UNRESOLVED and the
run halts pending recovery).

- *Launcher dies before the handoff:* EOF, no pidfd held → launch void;
  child never released, dies by PDEATHSIG; record LAUNCHER_LOST
  (pre-release); no issuance. (Termination here is by construction of
  the pinned child sequence, recorded as such — not as an observation.)
- *Launcher dies after RELEASE, before GATE_ACTUATED:* actuation
  UNKNOWN (above). The child's PDEATHSIG fires if it was armed, and
  the pidfd — already held — establishes whether and when the child
  terminated. Exit status UNKNOWN; reporting failure PROVEN;
  classification UNRESOLVED.
- *Launcher dies after GATE_ACTUATED:* the child was released (byte
  written) and dies by PDEATHSIG; pidfd proves termination; exit
  status UNKNOWN without STATUS; classification UNRESOLVED — **never
  CRASH by default**: a missing status word is not a crash.
- *Child terminates, STATUS valid:* closure per Stage 8 (STATUS +
  pidfd agreement).
- *Supervisor dies:* cascade as Rev 1 (launcher PDEATHSIG → launcher
  exits → child PDEATHSIG fires); SUPERVISOR_LOST recorded at next
  start against the still-open issuance; UNRESOLVED.
- *Malformed / out-of-order traffic:* pre-release → abort (Stage 4
  semantics); post-release → PROTOCOL_VIOLATION recorded, facts kept
  separate, classification UNRESOLVED, run halts.

## Part 2 — Descriptor protocol (completed)

**Channel and buffers.** As Rev 1 (SOCK_SEQPACKET socketpair, created
by the supervisor; end L inherited by the launcher with close-on-exec
cleared for that descriptor only). Maximum packet size is fixed at
**128 bytes total** (3-byte header + at most 125 bytes payload); the
receive buffer is exactly 128 bytes. A packet that would exceed the
buffer is received with MSG_TRUNC set → malformed (see below). A
receive error EMSGSIZE is likewise malformed. Either way the packet's
content is never partially processed.

**Framing.** 1 byte type, 2 bytes payload length (big-endian, MUST
equal the packet's actual payload size), then payload. Unknown type,
length mismatch, or a message not permitted in the current state
(state table below) is malformed.

**Ancillary data.** Receives use recvmsg with MSG_CMSG_CLOEXEC, so any
received descriptor arrives close-on-exec and can never leak across a
subsequent exec. Rules:
- Only PIDFD_HANDOFF may carry ancillary data, and exactly ONE
  descriptor. Any descriptor attached to any other message type, a
  handoff with zero or ≥2 descriptors, or a packet received with
  MSG_CTRUNC set, is malformed.
- On ANY malformed packet, every descriptor received with it is closed
  immediately, unexamined beyond counting; nothing from a malformed
  packet enters an owned state.
- **Descriptor cleanup (ownership rule):** every descriptor a process
  receives is, before any further processing, either (a) adopted into
  exactly one named owned state (for the supervisor: the run's held
  child pidfd, recorded in the run record), or (b) closed. There is no
  third state and no descriptor survives a state transition unowned.

**pidfd identity validation.** PIDFD_HANDOFF payload: child_pid
(u32 BE) + child_start_time (u64 BE, field 22 of /proc/<child>/stat,
read by the launcher from the child it forked). The supervisor
establishes the descriptor's target as follows:
1. The received descriptor is a pidfd; a pidfd denotes ONE specific
   process instance and is immune to PID reuse — termination observed
   on it is about that instance whatever happens to the PID space.
2. The supervisor reads /proc/<child_pid>/stat and requires: the
   process exists, its start_time equals child_start_time, and its
   parent PID is the launcher (ppid check against the spawned
   launcher's known PID). This binds the claimed PID to a unique
   process instance (PID + start time) in the correct parentage.
3. The supervisor then confirms the pidfd denotes that same instance:
   pidfd_send_signal(pidfd, 0, NULL, 0) must succeed (the descriptor
   refers to a live process) — combined with (2)'s unique-instance
   binding and the fact that the descriptor arrived over the run's own
   channel from the launcher that forked the child, the target is
   established; the residual ambiguity (a descriptor for a different
   instance carrying the same PID) is excluded because such an
   instance cannot simultaneously satisfy (2)'s start-time equality
   for the claimed PID.
On any failure: HANDOFF_ACK with non-zero result; the descriptor is
closed (cleanup rule); the launch aborts per Part 1 Stage 4.

**Message catalogue (nine messages).** 0x01 LAUNCH_REQUEST (S→L:
expected_supervisor_pid u32) · 0x02 PIDFD_HANDOFF (L→S: child_pid u32
+ child_start_time u64 + exactly one pidfd via SCM_RIGHTS) · 0x03
HANDOFF_ACK (S→L: result u8) · 0x04 GATE_READY (L→S: empty) · 0x05
RELEASE (S→L: empty) · 0x06 GATE_ACTUATED (L→S: empty) · 0x07 STATUS
(L→S: child_pid u32 + raw wait_status u32) · 0x08 STATUS_ACK (S→L:
empty; the launcher exits 0 only after STATUS + STATUS_ACK) · 0x09
ABORT (either direction: stage u8 + reason u8; fire-and-close — no
acknowledgement exists or is waited for; receiving ABORT is terminal
for the launch attempt; an ABORT arriving after RELEASE is recorded
and the run follows Part 1 Stage 9 semantics, the child's fate being
governed by PDEATHSIG and observed by pidfd).

**STATUS edge cases.** A second STATUS is out-of-state → malformed
(PROTOCOL_VIOLATION recorded; the first valid STATUS stands). A STATUS
whose child_pid contradicts the handoff's → facts recorded separately,
classification UNRESOLVED, run halts. STATUS after ABORT → the launch
is already terminal; the packet is recorded as a violation and
otherwise ignored; no closure is built on it.

**EOF semantics (three positions).** EOF before RELEASE → launcher
gone pre-release (Stage 9 branch 1 or, after handoff, LAUNCHER_LOST
with the child unreleased). EOF after RELEASE but before
GATE_ACTUATED → actuation UNKNOWN branch. EOF after GATE_ACTUATED →
post-actuation branch. EOF on the launcher's end (supervisor gone) is
unreachable in the model (the launcher's own PDEATHSIG fires first);
if observed, the launcher kills and reaps the child and exits non-zero.

**State-transition table.** States: S0 INIT (launcher spawned) · S1
REQUESTED · S2 CHILD_ESTABLISHED · S3 HANDOFF_SENT · S4
HANDOFF_ACCEPTED · S5 SETTLED (GATE_READY sent) · S6 RELEASED · S7
ACTUATED · S8 STATUS_SENT · S9 CLOSED (terminal, clean) · SX ABORTED /
LOST / VIOLATION (terminal, recorded; classification per Part 1).

| State | Message (sender→receiver) | Next state | Failure result |
|---|---|---|---|
| S0 | LAUNCH_REQUEST (S→L) | S1 | malformed/EOF → SX (abort, nothing spawned) |
| S1 | PIDFD_HANDOFF (L→S) | S3 | malformed/ancillary defect → SX (child killed+reaped by launcher; fds closed) |
| S3 | HANDOFF_ACK result 0 (S→L) | S4 | ACK non-zero or EOF → SX (Stage 4 abort) |
| S4 | GATE_READY (L→S) | S5 | EOF → SX (LAUNCHER_LOST, child unreleased) |
| S5 | RELEASE (S→L) | S6 | EOF before RELEASE → SX (LAUNCHER_LOST, unreleased) |
| S6 | GATE_ACTUATED (L→S) | S7 | EOF before GATE_ACTUATED → SX-recorded branch: actuation UNKNOWN, classification UNRESOLVED |
| S7 | STATUS (L→S) | S8 | EOF without STATUS → facts separated; classification UNRESOLVED |
| S8 | STATUS_ACK (S→L) | S9 | EOF → launcher already exited only post-ACK; supervisor-side: closure stands on STATUS+pidfd agreement (Part 1 Stage 8) |
| any pre-S9 | ABORT (either) | SX | terminal for the attempt; post-RELEASE → Stage 9 semantics |
| any | any message not listed for that state | — | malformed → PROTOCOL_VIOLATION; pre-release abort, post-release UNRESOLVED + halt |

## Parts 3 and 4 — carried as ACCEPTED

Part 3 (D-9 chronology: freeze → source → pin + inspect → disposition
→ Batch 4; checkpoint records the built binary only; both §3.5 point 2
and §4 Batch 4 corrected in the body) and Part 4 (C rationale:
toolchain facts as recorded evidence; language comparison a stated
preference; runtime/dependency claims demonstrated from the built
binary at SE-7; source inspection before Batch 4 and binary inspection
at the checkpoint kept as separate events) stand as accepted in Alex's
pass and are incorporated unchanged.

---

**Asked of Alex:** his independent pass on this revised plan — the
Stage 3 sequence, the actuation interlock, the classification
discipline, the completed protocol and its state table. On his
approval for incorporation, Rev 17 is drafted as a body rewrite of
§3.5 per this plan and shelved for his full inspection.

— Remmy, 2026-11-13
