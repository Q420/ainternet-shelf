# Rev 17 Correction Plan — REVISED (Rev 6)

**Prepared by Remmy, 2026-11-13, revising Plan Rev 5 (c3b21553)
against Alex's independent pass (pb-mwfm2ad2-8-hrzc).** One point
changes — the only open item of that pass: **EOF observation is
now defined independently of the S9 close-out window** (EOF in
S8 and S8F given table rows; an EOF observed before S9 is
retained and satisfies the observation; the five-second window
governs only EOF not yet observed at S9 entry). Everything else
stands as Rev 5. This document is the complete plan; it
supersedes Rev 5 in full.

---

## Part 1 — Process sequence

Stages 0–2, 4, 5, 7, 8 as Plan Rev 2 (preparation; spawn; launch
request; pidfd handoff with the ACK interlock; launcher settling per
correction A; the run; termination and closure). Stage 3 stands as
accepted in Rev 2 (capture identity → check parent → transition →
arm PDEATHSIG → read back → check parent again → fail = `_exit()`).

**Stage 6 — Gate release (evidence discipline corrected).**
GATE_ACTUATED asserts exactly that the launcher wrote the release
byte. The write-to-acknowledgement window is IRREDUCIBLE: if the
launcher writes the byte and dies before GATE_ACTUATED, the record
shows — as separate facts, never merged:

- RELEASE sent: PROVEN (the supervisor's own act).
- Gate-byte actuation: UNKNOWN.
- Child termination: PROVEN only if observed through the pidfd,
  and the observation is the same whether the child was released
  or not — **pidfd observation is never used to establish release**.
- Harness execution: UNKNOWN unless separately evidenced.
- Terminal classification: UNRESOLVED.

**Stage 9 — Failure branches (claims discipline corrected).**

- *Launcher lost before the handoff:* launcher loss PROVEN (channel
  EOF); child release NOT RELEASED (protocol fact: RELEASE was
  never sent); **child termination UNKNOWN** — before the handoff
  the supervisor holds no pidfd and has no independent observation;
  the PDEATHSIG consequence is recorded as DESIGN EXPECTATION, not
  as termination evidence; issuance: none.
- *Launcher lost after RELEASE, before GATE_ACTUATED:* actuation
  UNKNOWN (Stage 6 record); termination per pidfd if observed;
  exit status UNKNOWN; reporting failure PROVEN; UNRESOLVED.
- *Launcher lost after GATE_ACTUATED:* actuation PROVEN (the byte
  was written); termination per pidfd; exit status UNKNOWN without
  STATUS; reporting failure PROVEN; classification UNRESOLVED —
  never CRASH by default.
- *Supervisor lost:* the PDEATHSIG cascade is the DESIGN
  EXPECTATION for the launcher and the child; what the record may
  state as fact at the next start is only: SUPERVISOR_LOST (its own
  prior death, from the record's open state), the issuance still
  open/UNRESOLVED, and any observations made after restart. No
  termination is back-filled as fact from the expectation.
- *Malformed / out-of-state traffic:* per Part 2's table.

**Reaping after parent death — the completed contract.** The
LAUNCHER is the child's sole waitpid() reaper **while it lives**.
When the launcher dies, the orphaned child is reparented by the
kernel to the nearest designated subreaper ancestor, or, if none,
to PID 1 of the PID namespace. The supervisor never reaps, never
holds PR_SET_CHILD_SUBREAPER, and never becomes the child's parent
— Option A is not Option B by any route. The supervisor's
termination evidence remains the pidfd alone; a pidfd observation
is NEVER proof of reaping.

*The expected reaper — a SPECIFIED DEPENDENCY, not yet a
verified environmental fact:* **PID 1 of the room's PID
namespace.** What PID 1 actually is in the room (its /proc/1/comm
read verbatim), the namespace relationship, and the observed
parent transition are Batch 4 DEMONSTRATION EVIDENCE, captured
when the demonstration runs; until then this contract states
what the environment MUST provide, not what it has been shown to
provide. The expectation holds only if NO ancestor between the
launcher and PID 1 — supervisor, session leaders, tmux, sshd —
is a designated subreaper.

*How the configuration is established and inspected:* nothing is
configured; the design REQUIRES the absence of an intermediate
subreaper, and the requirement is inspected by observation, not
by trusting a setting: in the demonstration below, the orphan's
NEW parent PID is read from /proc/<child>/stat after the
launcher's death and before the child's termination — the kernel
names the receiving reaper directly.

*The distinguishing test (Batch 4 gate evidence):* kill the
launcher after actuation, then record, in order: (a) the child's
new ppid — PASS requires it to be exactly 1 (any other receiver is
a gate failure pending design review, since an unnamed reaper is
not a contract); (b) child termination observed on the pidfd;
(c) the child's /proc entry DISAPPEARING (reaped — a zombie's
entry persists, a reaped child's does not) within the pinned
bound **REAP_BOUND = 5 seconds** of the termination observation.
Disappearance alone proves nothing (namespace teardown or PID
churn could mimic it); the pass rests on the conjunction — ppid
observed == 1 while the child lived, then termination on the
instance-pinned pidfd, then the entry's disappearance inside the
bound.

*Unavailable or non-reaping reaper:* if the ppid observed is not
1, or the /proc entry persists beyond REAP_BOUND (a persistent
zombie), the result is a HARD GATE FAILURE: the environment does
not meet the dependency, the run halts, and no one remedies it by
reaping from the supervisor. The failure is recorded with the
observed ppid and timings.

## Part 2 — Descriptor protocol (completed)

Channel, framing, packet size (128 bytes fixed; MSG_TRUNC / EMSGSIZE
= malformed), MSG_CMSG_CLOEXEC receives, ancillary rules and the
descriptor ownership/cleanup rule stand as Plan Rev 2.

**pidfd identity validation (rewritten).** PIDFD_HANDOFF payload:
child_pid (u32 BE) + child_start_time (u64 BE). The supervisor
validates in this order:

1. **Descriptor target.** Read /proc/self/fdinfo/<received fd>. A
   pidfd's fdinfo reports its target PID ("Pid:" field, in the
   reader's PID namespace). Require the reported target PID to
   equal child_pid. This is the descriptor-target identity check:
   it establishes that THIS descriptor denotes the claimed PID, not
   merely some live process.
2. **Instance binding.** Read /proc/<child_pid>/stat: the process
   exists, its start_time (field 22) equals child_start_time, and
   its parent PID is the spawned launcher's known PID. (PID +
   start time) binds the PID to the unique intended instance.
3. **Instance pinning.** The validated pidfd denotes that instance
   for all later observation; PID reuse thereafter cannot confuse
   the record.

*Kernel/interface assumption, pinned:* the room's kernel exposes a
pidfd's target PID via /proc/self/fdinfo (the pidfd fdinfo
interface). The evidence SHALL record the room kernel's exact
version string (uname -r) and a verbatim sample of the fdinfo
record relied on, so the format assumption is inspected, not
presumed. **If the fdinfo target PID is unavailable or unreadable,
validation FAILS** — HANDOFF_ACK non-zero, descriptor closed,
launch aborts. There is no weaker fallback path; the liveness-only
check of Rev 2 is expressly not a substitute and
pidfd_send_signal plays no identity role.

*Live target intended; the liveness race treated explicitly.*
The launcher's pre-handoff check (waitpid WNOHANG returns 0) is an
OBSERVATION AT AN INSTANT: it establishes the child had not
terminated when checked; it does NOT guarantee liveness when the
supervisor validates. A child that exited during establishment
(e.g. a Stage 3 `_exit()`), already reaped by the launcher before
any handoff, produces ABORT (reason CHILD_LOST_IN_ESTABLISHMENT)
instead of a handoff. A child that exits in the window BETWEEN
the check and the supervisor's fdinfo read is handled by the
fail-closed rule, stated as its own outcome: if the fdinfo target
PID is then missing, unreadable or mismatched, the supervisor
REJECTS the handoff, closes the descriptor, and records
HANDOFF_REJECTED_TARGET_LOST with the observed fdinfo state —
an availability outcome, NOT a successful identity validation and
NOT a launcher violation; the launch aborts cleanly and the facts
are recorded. Separately, the Batch 4 evidence SHALL demonstrate
the fdinfo behaviour for an already-exited target on the room's
kernel (obtain a pidfd, let the target exit, read the fdinfo,
record what the Pid: field shows) — pinned as OBSERVED evidence
about the interface. The validation path never depends on the
exited case, never assumes the field persists, and never falls
back to a liveness-only check.

**wait_status validation — strict encoding (rewritten).** A
STATUS packet is a valid terminal report only if framing is
valid, child_pid equals the handoff's child_pid, AND the raw
wait_status word matches EXACTLY one of the two accepted Linux
encodings below — bit patterns, not macro resemblance. The word
is an unsigned 32-bit value as transmitted; bits 16–31 MUST be
zero in every accepted case.

| Case | Required bit pattern | Decoded facts recorded |
|---|---|---|
| Exited | bits 0–7 == 0x00; bits 8–15 = exit code (0–255); bits 16–31 == 0 | exit code = bits 8–15 |
| Signalled | bits 0–6 = signal S, 1 ≤ S ≤ 64 (the pinned kernel's signal range, SIGRTMAX = 64); bit 7 = core-dump flag (either value accepted, recorded); bits 8–15 == 0; bits 16–31 == 0 | signal S; core-dump flag |

Everything else is REJECTED as an invalid terminal report —
including: the stopped encoding (bits 0–7 == 0x7F), the continued
encoding (0xFFFF), signalled form with non-zero bits 8–15, any
word with bits 16–31 set, signal 0 in signalled form, and signal
values 65–127 (outside the kernel's signal range). Signals 32 and
33 are NOT excluded: glibc reserves them for its own signalling
interface, but this validator judges a KERNEL waitpid() result,
and no kernel-level evidence bars those values from a genuine
wait status — in-range values are accepted uniformly. (The
launcher waits without
WUNTRACED/WCONTINUED, so stopped/continued words cannot arise
from an honest waitpid in any case.) A rejected STATUS: the raw
word is recorded verbatim with the rejection reason, facts are
kept separate, classification is UNRESOLVED, and the run halts.
The raw status word of an accepted STATUS is likewise recorded
verbatim alongside its decode.

**Terminal observations — complete rules (new).** Closure requires
the consistent set {one valid STATUS} + {pidfd termination
observed}; either may arrive first and neither alone closes.
- pidfd termination first: recorded as the fact TERMINATION
  OBSERVED (time, instance); closure still awaits a valid STATUS;
  a valid STATUS arriving afterwards is normal, validated as above.
- STATUS first: recorded; closure awaits pidfd termination.
- STATUS after a supervisor-sent ABORT: recorded as a protocol
  violation; ignored for closure (the attempt is terminal).
- STATUS after a launcher-sent ABORT: unreachable on an honest
  channel (ABORT is fire-and-close); if observed, violation,
  ignored for closure.
- Contradictory STATUS (child_pid mismatch, invalid decode, second
  STATUS): violation recorded with the packet's facts; the first
  valid STATUS, if any, stands; classification UNRESOLVED if the
  contradiction touches the terminal basis.
- No observation overwrites another; the record keeps each fact
  with its source.

**State-transition table (rewritten as a contract).** States:
S0 SPAWNED (launcher exec'd; LAUNCH_REQUEST not yet received) · S1
REQUESTED (LAUNCH_REQUEST validated) · S2 CHILD_ESTABLISHED
(launcher has forked the child; PIDFD_HANDOFF in flight) · S3
HANDOFF_RECEIVED (supervisor holds the descriptor, validation
pending) · S4 HANDOFF_ACCEPTED (ACK 0 sent) · S5 SETTLED
(GATE_READY received) · S6 RELEASED (RELEASE sent) · S7 ACTUATED
(GATE_ACTUATED received) · S8 STATUS_RECEIVED (valid STATUS held;
pidfd termination not yet observed) · S8F FACTS_COMPLETE (valid
STATUS held AND pidfd termination observed — the run's closure is
DETERMINED by these facts from this point) · S9 CLOSED (terminal
facts complete AND the supervisor's run record written complete —
defined by the facts and the record, NEVER by ACK delivery; the
ACK outcome is recorded separately) · SX TERMINAL_RECORDED
(aborted / lost / violation; the supervisor's record states the
facts and the classification per Part 1).

| State | Event (sender→receiver) | Validation | Next | Descriptor result | On failure |
|---|---|---|---|---|---|
| S0 | LAUNCH_REQUEST (S→L) | framing; run-id already argv-validated | S1 | none carried | malformed/EOF → SX: spawn attempt void (the launcher exits; NOTHING was forked) |
| S1 | fork occurs (L internal); PIDFD_HANDOFF (L→S) | — | S2→S3 on receipt | pidfd in flight | launcher internal failure → EOF → SX (Stage 9 pre-handoff facts) |
| S3 | supervisor validates handoff | fdinfo target == child_pid; /proc instance binding; exactly 1 descriptor | S4 on ACK 0 | pidfd ADOPTED into the run's held state | validation fail → ACK non-zero, fd closed → SX (child killed+reaped by launcher per Stage 4 abort) |
| S4 | GATE_READY (L→S) | in-state; empty payload | S5 | — | EOF → SX LAUNCHER_LOST (child unreleased; termination UNKNOWN) |
| S5 | RELEASE (S→L) | supervisor's own Stage 0 preconditions | S6 | — | EOF before RELEASE → SX LAUNCHER_LOST (unreleased) |
| S6 | GATE_ACTUATED (L→S) | in-state; empty payload | S7 | — | EOF first → SX-recorded: actuation UNKNOWN branch (Part 1 Stage 6/9) |
| S7 | STATUS (L→S) — pidfd termination NOT yet observed | framing; child_pid match; strict wait_status decode (above) | S8 | — | EOF without STATUS → facts separated, UNRESOLVED (SX); invalid STATUS → violation, UNRESOLVED (SX) |
| S7 | STATUS (L→S) — pidfd termination ALREADY observed (recorded while in S7) | same validation | S8F | — | invalid STATUS → violation, UNRESOLVED (SX) |
| S7 | pidfd termination observed before STATUS | instance pinned | stays S7; TERMINATION OBSERVED fact recorded | — | (the conditional STATUS rows above then apply) |
| S8 | pidfd termination observed (S, kernel) | instance already pinned | S8F | pidfd retained until S9, then closed as the record closes | — |
| S8F | supervisor writes the run record complete from the terminal facts | facts = valid STATUS + observed pidfd termination | S9 | pidfd closed as the record closes | — |
| S8 / S8F | STATUS_ACK (S→L) attempt | — | NO state change by itself | — | the ACK outcome is recorded separately, as ACK_DELIVERED or STATUS_ACK_UNDELIVERABLE; closure (S8F → S9) never depends on it and is fully possible when the ACK is undeliverable |
| S8F | ABORT (L→S) | framing | S9 path UNAFFECTED | any attached fds closed unexamined | recorded as PROTOCOL_VIOLATION (the attempt is complete, not aborted — ABORT has no work to do once the terminal facts are held); closure proceeds on the facts; the violation rides in the record |
| S8 (termination NOT yet observed) | ABORT (L→S) | framing | SX | any attached fds closed unexamined | attempt terminal with facts insufficient: classification UNRESOLVED; child governed by PDEATHSIG, observed by pidfd (held) — a later pidfd termination is recorded as a fact but does not reopen the attempt |
| S8 | launcher channel EOF observed | — | NO state change | pidfd RETAINED; the supervisor keeps waiting on it | LAUNCHER_EXIT_OBSERVED recorded at once (state at observation: S8), as the supplementary exit observation — it is RETAINED and satisfies the exit observation for the whole session. EOF contributes nothing to closure and blocks nothing: the S8 → S8F → S9 progression proceeds on the pidfd alone. (Consequence for the ACK: the channel is closed, so a STATUS_ACK attempt from here records STATUS_ACK_UNDELIVERABLE.) If pidfd termination is never observed, the run remains open exactly as the S8 row above states — EOF does not change that |
| S8F | launcher channel EOF observed | — | NO state change | — | LAUNCHER_EXIT_OBSERVED recorded at once (state at observation: S8F), retained as the session's exit observation; the S8F → S9 closure proceeds normally |
| after S9 | launcher-exit observation window — ONLY if EOF has not already been observed | trigger: entry into S9 with no EOF yet observed | session record finalised | pidfd closed at S9 | EOF within CLOSE_OUT_WINDOW = 5 s → LAUNCHER_EXIT_OBSERVED appended; window expires → LAUNCHER_EXIT_UNOBSERVED appended and the supervisor closes its channel end. If EOF was already observed (in S8, S8F, or any earlier state where the table records it), there is NO window and NO UNOBSERVED entry — the retained observation stands. In all cases the window is an observation bound on a SUPPLEMENTARY session entry only: S9 closure is already complete and is never reopened, delayed or invalidated by either outcome |
| any ≤ S8 | ABORT (S→L) | framing | SX | — | attempt terminal supervisor-side; a later STATUS = violation, ignored for closure |
| any | message not permitted in this state | framing valid but transition invalid | — | **attached descriptors closed immediately, unexamined** | PROTOCOL_VIOLATION: pre-release → abort to SX; post-release → facts separated, UNRESOLVED, halt |

## Parts 3 and 4 — carried as ACCEPTED (unchanged from Rev 2)

Part 3 (D-9 chronology: freeze → source → pin + inspect →
disposition recorded → Batch 4 begins; the checkpoint records the
built binary only; §3.5 point 2 and §4 Batch 4 corrected in the
body) and Part 4 (C rationale: toolchain facts as recorded
evidence; language comparison a stated preference; runtime and
dependency properties demonstrated from the built binary at SE-7;
source inspection and binary inspection distinct events).

---

**Asked of Alex:** his independent pass on this Rev 6 — the
single open point: EOF observation defined independently of
the close-out window (S8 and S8F rows; a pre-S9 EOF retained
and satisfying the observation; the window governing only EOF
not yet observed at S9 entry). Everything else stands as
accepted in Rev 5. On his approval, Rev 17 is drafted as the
single §3.5 body rewrite and shelved for full inspection.

— Remmy, 2026-11-13
