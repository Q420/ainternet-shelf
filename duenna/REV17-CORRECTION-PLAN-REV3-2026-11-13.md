# Rev 17 Correction Plan — REVISED (Rev 3)

**Prepared by Remmy, 2026-11-13, revising Plan Rev 2 (11759ff2)
against Alex's independent pass (pb-mwflnguw-5-2x5o).** Stage 3 and
Parts 3–4 stand as ACCEPTED and are carried unchanged. This revision
corrects: the gate-actuation evidence claim (§2 of the pass), the
pre-handoff termination claim (§3), pidfd descriptor-target identity
(§4, HIGH), post-parent-death reaping (§5, HIGH), the state table
(§6), and wait_status validation + terminal-observation rules (§7).
This document is the complete plan; it supersedes Rev 2 in full.

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

**Reaping after parent death (new, resolving the pass's §5).** The
LAUNCHER is the child's sole waitpid() reaper **while it lives**.
When the launcher dies, the child — orphaned — is reparented by the
kernel to the reaper of last resort in its PID namespace (the
namespace's init, or a configured subreaper above the launcher that
is NOT the supervisor). That external reaper performs the waitpid();
the supervisor never reaps, never holds PR_SET_CHILD_SUBREAPER, and
never becomes the child's parent — Option A is not Option B by any
route. The supervisor's termination evidence remains the pidfd
alone. This is a stated ENVIRONMENT DEPENDENCY: the Batch 4 gate
evidence SHALL demonstrate it in the room — kill the launcher after
actuation, observe (a) child termination on the pidfd, and (b) the
child's /proc entry disappearing within a bounded interval
evidencing external reaping. If (b) does not occur, the environment
fails the requirement and the run halts; a persistent zombie is a
gate failure, never something the supervisor "fixes" by reaping.

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
interface). Batch 0/4 evidence SHALL demonstrate checks 1–2 on the
room's actual kernel against a live handoff. **If the fdinfo
target PID is unavailable or unreadable, validation FAILS** —
HANDOFF_ACK non-zero, descriptor closed, launch aborts. There is no
weaker fallback path; the liveness-only check of Rev 2 is expressly
not a substitute and pidfd_send_signal plays no identity role.

**wait_status validation (new).** A STATUS packet is a valid
terminal report only if ALL hold: framing valid; child_pid equals
the handoff's child_pid; the raw wait_status decodes under the
Linux waitpid encoding as WIFEXITED (exit code = (status >> 8) &
0xFF, recorded raw and decoded) or WIFSIGNALED (signal = status &
0x7F, core-dump bit recorded). Any other decode — including
WIFSTOPPED / WIFCONTINUED states, which the launcher cannot
honestly produce (it waits without WUNTRACED/WCONTINUED) — makes
the STATUS invalid: facts recorded separately, classification
UNRESOLVED, run halts. The raw status word is recorded verbatim in
every case.

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
(GATE_ACTUATED received) · S8 STATUS_RECEIVED (valid STATUS held) ·
S9 CLOSED (STATUS_ACK sent AND pidfd termination observed;
supervisor's record complete) · SX TERMINAL_RECORDED (aborted /
lost / violation; the supervisor's record states the facts and the
classification per Part 1).

| State | Event (sender→receiver) | Validation | Next | Descriptor result | On failure |
|---|---|---|---|---|---|
| S0 | LAUNCH_REQUEST (S→L) | framing; run-id already argv-validated | S1 | none carried | malformed/EOF → SX: spawn attempt void (the launcher exits; NOTHING was forked) |
| S1 | fork occurs (L internal); PIDFD_HANDOFF (L→S) | — | S2→S3 on receipt | pidfd in flight | launcher internal failure → EOF → SX (Stage 9 pre-handoff facts) |
| S3 | supervisor validates handoff | fdinfo target == child_pid; /proc instance binding; exactly 1 descriptor | S4 on ACK 0 | pidfd ADOPTED into the run's held state | validation fail → ACK non-zero, fd closed → SX (child killed+reaped by launcher per Stage 4 abort) |
| S4 | GATE_READY (L→S) | in-state; empty payload | S5 | — | EOF → SX LAUNCHER_LOST (child unreleased; termination UNKNOWN) |
| S5 | RELEASE (S→L) | supervisor's own Stage 0 preconditions | S6 | — | EOF before RELEASE → SX LAUNCHER_LOST (unreleased) |
| S6 | GATE_ACTUATED (L→S) | in-state; empty payload | S7 | — | EOF first → SX-recorded: actuation UNKNOWN branch (Part 1 Stage 6/9) |
| S7 | STATUS (L→S) | framing; child_pid match; wait_status decode (above) | S8 | — | EOF without STATUS → facts separated, UNRESOLVED (SX); invalid STATUS → violation, UNRESOLVED (SX) |
| S8 | pidfd termination observed (S, kernel) | instance already pinned | S9 when STATUS_ACK also sent | pidfd retained until S9, then closed as the record closes | termination never observed → no closure; run remains open (not a silent state — G-record shows it) |
| S8 | STATUS_ACK (S→L) | — | (S9 with the row above, either order) | — | EOF from L after ACK → LAUNCHER_EXIT_OBSERVED recorded; EOF absent within close-out → LAUNCHER_EXIT_UNOBSERVED recorded; neither reopens closure, which rests on STATUS + pidfd |
| S7–S8 | pidfd termination observed before STATUS | instance pinned | stays; fact recorded | — | STATUS later validated normally (rules above) |
| any ≤ S8 | ABORT (L→S) | framing | SX | any attached fds closed unexamined | post-RELEASE ABORT: record ABORT_RECEIVED + facts; classification UNRESOLVED unless STATUS/pidfd facts already suffice; child governed by PDEATHSIG, observed by pidfd if held |
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

**Asked of Alex:** his independent pass on this Rev 3 — in
particular the fdinfo descriptor-target check with its fail-closed
rule, the external-reaping dependency and its gate demonstration,
the corrected evidence claims, and the state table as a contract.
On his approval, Rev 17 is drafted as the single §3.5 body rewrite
and shelved for full inspection.

— Remmy, 2026-11-13
