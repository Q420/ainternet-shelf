# Rev 18 Correction Plan — Rev 3

**Prepared by Remmy, 2026-11-13. Rev 3 = Rev 2 plus two
corrections only, against Alex's independent pass on Rev 2
(pb-mwfmoosd-c-8uep — NOT APPROVED: one HIGH, one MEDIUM; his
matrix accepted as the inspection reference subject to the
ABORT correction). Rev 2 and Rev 1 are preserved unchanged;
Rev 17 and Plan Rev 6 likewise.** Rev 1 was prepared against
Alex's inspection of
Rev 17 (pb-mwfmeh4q-a-kbfd — NOT CLEARED, one HIGH blocker)
and covered the finding's five points together. Nothing here
reopens any accepted part of Plan Rev 6 or of the Rev 17
incorporation; Option A is preserved throughout — the
launcher remains the child's sole waitpid() reaper while it
lives, and the supervisor never becomes the child's parent
or reaper.

**Rev 3 changes, in full.** (1) HIGH — the ABORT message
gains an explicit **lifecycle class** (Part 2A, new): the
pre-release child-termination ABORT keeps the channel open
for exactly one final STATUS; every other ABORT in either
direction remains fire-and-close exactly as Rev 17 defines,
and a STATUS after those remains a violation. The
launcher-reaped-first race is closed: one reaping, one
STATUS, one report per attempt, in either arrival order.
(2) MEDIUM — the EINTR policy is **finite and specified**
(Part 1): a monotonic READINESS_DEADLINE of 1 second from
the operation's start, identical at S3 and S5; expiry with
no completed poll records POLL_INCOMPLETE and selects the
call site's fail-closed path. No implementation-chosen
retry counts or timeouts anywhere. Rev 2's changes stand
below, unaltered:

**Rev 2 changes, in full.** (1) HIGH — SIGCHLD is an
**establishment condition**: the launcher explicitly resets
it to SIG_DFL with SA_NOCLDWAIT cleared, reads the
disposition back and verifies it, and aborts **before fork**
on any failure or unverifiable state (Part 1 rewritten).
(2) MEDIUM — the readiness operation gets a **complete
result contract** (Part 1): POLLIN, no events, EINTR
(re-poll), and errors or unexpected flags (fail closed —
no polling outcome is ever read as life); the same contract
governs the S3 check and the S5 guard. (3) MEDIUM — the
**poll-to-RELEASE race is stated honestly** (Part 2): the
guard is an observation, not atomic liveness; the relative
timing of termination and RELEASE is UNKNOWN unless
independently established; D-T3 splits into the
before-poll and poll-to-send cases. Part 4 gains item 10
(the missing-STATUS bounded closure) and Part 4's preamble
records the protocol checks Alex listed (ACK 3 never falls
through the generic refusal path; the two gate-outcome
messages are mutually exclusive per attempt; no late
RELEASE after ABORT commitment).

**The finding, restated precisely.** A child that terminates
after the launcher's `waitpid(WNOHANG)` observation but before
(or during) the supervisor's validation remains an **unreaped
zombie**. `pidfd_open()` succeeds on a zombie; the fdinfo
target check and the /proc instance binding can both PASS on a
child that is already dead. Rev 17's validation therefore
proves **identity**, not **life** — and the spec defines no
path for termination observed before RELEASE: the supervisor
can accept a corpse's handoff, the launcher can reach
GATE_READY, RELEASE can be sent with no living child at the
gate, the gate write can fail with EPIPE/SIGPIPE under no
specified handling, and the S4/S5 rows call termination
UNKNOWN in states where the supervisor holds a pidfd and can
observe it directly.

---

## Part 1 — pidfd establishment: SIGCHLD conditions and already-terminated detection

**SIGCHLD disposition — an establishment condition, not an
assumption.** The readiness semantics below rely on a
terminated child **persisting as a zombie until the launcher
reaps it**. That cannot be assumed from "the default": a
SIG_IGN disposition **survives execve()**, so a launcher
started by a supervisor that ignores SIGCHLD would inherit
auto-reaping — and SA_NOCLDWAIT likewise prevents zombies
from forming at all. Either would silently destroy both the
zombie and the waitpid() status this design exists to
capture. Therefore, **before it forks anything**, the
launcher SHALL: (a) explicitly install SIGCHLD with handler
SIG_DFL and flags **without SA_NOCLDWAIT** (and without
SA_NOCLDSTOP); (b) **read the disposition back** (sigaction
query) and verify the handler is SIG_DFL and SA_NOCLDWAIT is
absent; (c) on any failure, or if the resulting state cannot
be verified, **abort before fork** — the launcher exits
non-zero having spawned nothing; the supervisor records the
launcher's establishment failure on the established
launcher-exit branch. The specification additionally records
that **no SIGCHLD handler and no alternate reaping path is
permitted anywhere** in the launcher's life. The supervisor's
own SIGCHLD disposition is irrelevant to the child (it is
not the parent) and is not relied on.

**Detection before acceptance — the readiness check.**
Validation in S3 gains a third step, after the fdinfo target
check and the instance binding:

3. **Readiness.** The supervisor polls the validated pidfd
   with a zero timeout. A pidfd for a terminated process is
   **readable** (POLLIN); a live process's pidfd is not. If
   the pidfd is readable, the child has **already
   terminated**: the supervisor records TERMINATION OBSERVED
   (its own observation, at validation time), refuses the
   handoff with the dedicated acknowledgement code for this
   case (**ACK code 3 — CHILD_TERMINATED**, distinct from
   identity-failure code 1 and target-lost code 2), and
   closes the descriptor. On ACK code 3 the launcher reaps
   the child with waitpid() — its own zombie, its own
   reaping role — and sends ABORT with reason
   CHILD_TERMINATED_PRE_RELEASE, the ABORT detail carrying
   the **raw wait_status word**; the supervisor validates
   that word under the strict encoding rules and records
   the exit basis as LAUNCHER-REPORTED (validated), the
   termination itself as OBSERVED (its own). The attempt
   closes as a pre-release abort with complete facts; no
   issuance of any kind.
   If the pidfd is **not readable**, the supervisor records
   NOT-OBSERVED-TERMINATED AT VALIDATION — an observation
   at an instant, expressly **not** a liveness guarantee:
   a child that dies the next instant is handled by Part 2,
   not by pretending this check saw the future.

**The readiness operation's complete result contract.**
The same contract governs the S3 check and the S5
pre-RELEASE guard; there is one readiness operation with two
call sites, not two operations.

- **POLLIN ready** → termination observed.
- **Returns with no readiness events** → termination not
  observed at that instant (an observation, as above).
- **Interrupted (EINTR)** → the supervisor **re-polls**;
  an interrupt is not a result, carries no state change,
  and the observation is taken from the first completed
  poll. The retries run against a **finite deadline the
  plan fixes, not the implementation**: READINESS_DEADLINE
  = **1 second**, measured on CLOCK_MONOTONIC from the
  readiness operation's start (the moment of entry, before
  the first poll call), and **identical at S3 and at S5**.
  If the deadline expires with no completed poll, the
  operation ends as **POLL_INCOMPLETE** and fails closed
  per the next bullet: at S3 the refusal path with recorded
  reason POLL_INCOMPLETE; at S5 no RELEASE and the ABORT
  path (ABORT reason READINESS_UNVERIFIABLE; the recorded
  observation is POLL_INCOMPLETE). No retry count and no
  other timeout exists for an implementation to choose.
- **Any error return (other than EINTR), POLLERR or
  POLLNVAL, or any event mask other than POLLIN alone or
  no events** → **fail closed**. At S3: the handoff is
  refused as a validation failure (ACK code 1 class; the
  recorded reason is the poll failure, distinct from an
  identity mismatch), the descriptor is closed unexamined
  further, and the attempt takes the refusal branch. At
  the S5 guard: RELEASE is **not sent**; the poll failure
  is recorded and the attempt takes the ABORT path (reason
  READINESS_UNVERIFIABLE). **No polling error, unexpected
  flag, or incomplete poll is ever interpreted as a live
  child.**

**Continuous observation.** From S3 onward the supervisor's
event loop watches the held pidfd alongside the channel and
the record file. Termination observed in any state triggers
that state's Part 2 rule **when observed**, not only at
checkpoints; and the RELEASE transition carries its own
final guard (Part 2, S5).

## Part 2 — Pre-release termination, state by state

**S3** — Part 1's readiness path (refusal code 3).

**S4 (handoff accepted; launcher settling).** On pidfd
termination observed: the supervisor records TERMINATION
OBSERVED (time, instance) and sends ABORT (reason
CHILD_TERMINATED_PRE_RELEASE). RELEASE will never be sent
for this attempt. A GATE_READY arriving after the
observation is recorded and does not advance the state. The
launcher, on the ABORT (or on its own waitpid() returning),
reaps the child and sends STATUS as its **final report**;
in pre-release states a STATUS after a supervisor ABORT for
child termination is **expected**, is validated under the
strict encodings, and is recorded — it reopens nothing.
Attempt classification: closed pre-release; facts —
termination OBSERVED (supervisor, pidfd), release NOT
RELEASED, exit basis from the STATUS if it arrives,
otherwise UNKNOWN (e.g. the launcher also died; the EOF
branch then governs the launcher's own loss and the facts
already recorded stand).

**S5 (GATE_READY held).** The same ABORT path on
observation. Additionally, the RELEASE row's validation
gains the **pre-RELEASE readiness guard**: immediately
before sending RELEASE, the supervisor zero-polls the
pidfd; if readable, RELEASE is **not sent** and the S5
termination path runs instead. RELEASE's preconditions are
now: Stage 0 expectations in place **and** pidfd not
observed terminated at send. **The guard's limit, stated
honestly:** the poll and the send are not atomic. A child
can terminate after a clean final poll and before RELEASE
is transmitted. The record therefore holds three facts
separately and never merges them: the last readiness
observation (not terminated, at its instant); RELEASE sent
(the supervisor's own act, proven); termination observed
(the pidfd, at its instant). **The child's actual
termination time relative to RELEASE is UNKNOWN unless
independently established** — termination first observed
after RELEASE enters the S6 path, and that entry does
**not** prove the child died after RELEASE. The guard is
an observation immediately before sending, not a guarantee
of life at the instant of transmission.

**S6 (RELEASE sent; GATE_ACTUATED outstanding).**
Termination observed is recorded as a fact — RELEASE sent
PROVEN, termination OBSERVED — and the attempt **folds into
the existing Stage 8 machinery** rather than a special case:
GATE_ACTUATED may still arrive (actuation then PROVEN);
GATE_WRITE_FAILED may arrive instead (Part 3; actuation
then FAILED); or neither arrives (actuation UNKNOWN). The
launcher's STATUS, when it comes, pairs with the pidfd
observation toward closure exactly as in Stage 8; harness
execution is UNKNOWN unless the record file — the
supervisor's own read — evidences it; the terminal
classification then follows points 5–7 (a terminal record
event present → the TERMINAL path; terminated without one →
the CRASH path). No fact recorded here is rewritten by a
later arrival; each is kept with its source.

**EOF rows corrected (S4, S5).** Where the Rev 17 table
says termination UNKNOWN on launcher loss in S4/S5, it must
read: termination **per the pidfd the supervisor holds** —
OBSERVED if the pidfd shows it, UNKNOWN only if it has not
been observed at the time the record is written. Channel
EOF says something about the launcher; since S3 it has said
nothing about the child.

## Part 2A — The ABORT lifecycle: two classes (Rev 3)

Rev 17's protocol defines ABORT as **fire-and-close**: the
sender closes its end after sending, and a STATUS arriving
after a supervisor-sent ABORT is a protocol violation. The
pre-release flow of Part 2 contradicts that contract unless
the contract itself is amended — so it is amended, here,
explicitly. ABORT carries a **lifecycle class**, determined
by its reason code and stated in the message catalogue:

- **Class T — termination-report ABORT.** Exactly one
  member: a supervisor→launcher ABORT with reason
  CHILD_TERMINATED_PRE_RELEASE, sent pre-release (S4 or
  S5). Class T **supersedes fire-and-close for that send**:
  the channel **remains open**; the launcher is permitted
  **exactly one** further message on it — its final STATUS;
  the supervisor validates that STATUS under the strict
  encodings and records it; the channel then closes — on
  the STATUS's recording, on channel EOF, or at
  PRE_RELEASE_CLOSE_BOUND expiry (Part 4 item 12), whichever
  first. Any other launcher message after a class-T ABORT,
  and any second STATUS, is a protocol violation, recorded,
  changing nothing. Class T is available **only** for this
  reason; no other ABORT may claim it.
- **Class F — fire-and-close ABORT.** Every other ABORT,
  in either direction, including every other supervisor
  ABORT (among them the S5 READINESS_UNVERIFIABLE abort):
  Rev 17's semantics unchanged — the sender closes after
  sending, and a STATUS after a class-F supervisor ABORT
  remains a protocol violation, recorded and ignored.

**The reaped-first race.** The launcher may reap the child
before the supervisor's ABORT arrives — it may hold the
waitpid() result already. The contract is indifferent to
who noticed first, and it is exact: **one reaping, one
STATUS, one terminal report per attempt.** If the launcher
has reaped and not yet sent STATUS when a class-T ABORT
arrives, it sends its one STATUS (it does not reap again —
its own reaped-state guards the waitpid; there is no second
reaping to attempt). If its STATUS is already on the wire
or already held by the supervisor when the supervisor
observes the termination in S4/S5, the supervisor records
that STATUS as the attempt's final report and **does not
send the ABORT at all** — the facts are complete and the
attempt closes on them. A STATUS sent under class T is
never a violation in either arrival order; a STATUS beyond
the one is always a violation. The state table's S4/S5
termination rows, the terminal-observation rules, and the
catalogue's ABORT entry all state this class split — it is
a protocol amendment, not a prose exception.

## Part 3 — Gate-write failure: SIGPIPE, EPIPE, and what the launcher reports

**SIGPIPE.** The launcher SHALL set SIGPIPE to SIG_IGN as
one of its first acts, before any write of any kind, and
keep it ignored for its whole life. No write the launcher
ever makes — gate pipe or status channel — can kill it by
signal; every failed write returns an error it must handle.
(The supervisor likewise ignores SIGPIPE in its own process;
its channel writes already treat EPIPE as the launcher-loss
observation.)

**The gate write.** The write of the single release byte
has exactly three outcomes:

- **Write returns 1** → the byte was written; the launcher
  closes the write end and sends GATE_ACTUATED. This is
  the only path that produces GATE_ACTUATED.
- **Write fails with EPIPE** → the read end is closed,
  which in the pinned child sequence happens only when the
  child has terminated (or never reached the gate — the
  Stage 9 facts distinguish what can be distinguished).
  The launcher sends **GATE_WRITE_FAILED** (new message,
  code 0x0A; payload: error class u8 — 1 = EPIPE, 2 = other
  — and the raw errno u16), then waitpid()s and sends
  STATUS. **A failed write is never actuation**, and
  GATE_ACTUATED is never sent for it.
- **Write fails with any other error**, or returns 0 (a
  one-byte pipe write is atomic — 1 or an error; anything
  else is itself a failure) → the same GATE_WRITE_FAILED
  path with error class 2 and the errno recorded.

**Supervisor's record on GATE_WRITE_FAILED:** RELEASE sent
PROVEN; actuation **FAILED** (launcher-reported, and
consistent with the pidfd observation when termination has
been observed); the attempt proceeds on the STATUS/pidfd
pair per Part 2's S6 rule. If the channel itself is dead
(the launcher died at the write), there is no report — the
Stage 9 launcher-loss branch governs, actuation UNKNOWN,
exactly as Rev 17 already provides: GATE_WRITE_FAILED
exists for the case where the launcher **lives** to report.

## Part 4 — State-table and rules amendments (incorporation list)

Three protocol points from Alex's pass are recorded here as
binding on the draft, not left as letter commentary: **ACK
code 3 never falls through the generic refusal path** —
codes 1–2 mean the launcher kills and reaps a live child;
code 3 means the child is already dead, and the launcher
**reaps only** (there is nothing to kill) and reports the
status in its ABORT. **GATE_ACTUATED and GATE_WRITE_FAILED
are mutually exclusive for one gate attempt** — the first
gate-outcome message received is the recorded fact; a
second, contradicting gate-outcome is a protocol violation,
recorded, changing nothing. **Once the supervisor has
recorded its ABORT commitment for an attempt, RELEASE is
barred for that attempt** regardless of what arrives
afterwards — a termination observation and a GATE_READY
arriving close together can never produce a late RELEASE.

1. S3 validation row: add step 3 (readiness) and the ACK
   code 3 outcome (refusal row gains the terminated case
   with its record contents).
2. HANDOFF_ACK payload codes specified: 0 accepted;
   1 identity validation failed; 2 target lost
   (HANDOFF_REJECTED_TARGET_LOST); 3 child terminated
   (Part 1). The launcher's behaviour per code is stated
   (code 3: reap + ABORT with the raw status in the detail;
   codes 1–2: as Rev 17 already provides).
3. New rows: pidfd termination observed in S4 (→ ABORT
   path, terminal recording); in S5 (same); in S6 (facts
   recorded; Stage 8 machinery).
4. S5 RELEASE row: validation gains the pre-RELEASE
   readiness guard.
5. S4/S5 EOF rows: termination wording corrected per
   Part 2.
6. New S6 row: GATE_WRITE_FAILED received (actuation
   FAILED recorded; state awaits STATUS; failure
   disposition if STATUS never arrives = the existing
   EOF/launcher-loss branches).
7. Terminal-observation rules: add the pre-release clause
   — in S4–S5, a STATUS sent under a **class-T ABORT**
   (Part 2A) is the launcher's expected final report:
   validated, recorded, reopening nothing, in either
   arrival order, exactly one per attempt. (This does not
   disturb the existing rules elsewhere: a STATUS after a
   class-F ABORT, after a completed closure, or after an
   ABORT in S8, remains a violation.)
8. Message catalogue: add 0x0A GATE_WRITE_FAILED; ABORT
   detail format specified for CHILD_TERMINATED_PRE_RELEASE
   (raw wait_status u32).
9. Point 2 gains the launcher requirements: SIGCHLD
   established per Part 1 (explicit reset to SIG_DFL,
   SA_NOCLDWAIT cleared, read-back verified, abort before
   fork on failure; no handler and no alternate reaping
   path anywhere); SIGPIPE ignored from the first act.
11. Catalogue and table: the ABORT entry states the
    class-T / class-F split and the per-reason class; the
    S4/S5 termination rows name class T and the
    one-STATUS rule; the readiness text carries
    READINESS_DEADLINE = 1 s (CLOCK_MONOTONIC, from
    operation entry, identical at S3 and S5) and the
    POLL_INCOMPLETE expiry outcome at both call sites.
12. **No attempt stays open without a disposition.** After
    a supervisor ABORT in a pre-release state, the
    launcher's STATUS is expected; if neither STATUS nor
    channel EOF has arrived within PRE_RELEASE_CLOSE_BOUND
    = 5 s of the ABORT send, the supervisor closes the
    record itself: disposition
    PRE_RELEASE_ABORT_STATUS_UNREPORTED, all held facts
    recorded as they stand, the run halted, nothing issued.
    If EOF arrives first, the launcher-loss branch records
    the missing STATUS under that branch instead. Either
    way the attempt ends with a recorded disposition.

## Part 5 — Demonstrations (specified now; executed as Batch 4 gate evidence)

- **D-T1 — termination before handoff.** The test build's
  hold interposes between the launcher's WNOHANG observation
  and the supervisor's validation while the child is made to
  terminate (the child's own induced `_exit()` in the hold).
  Expected: identity checks pass, readiness check fires,
  ACK code 3, TERMINATION OBSERVED recorded at validation,
  launcher reaps, ABORT carries a strictly-valid raw status,
  no GATE_READY, no issuance.
- **D-T2 — termination during settling.** The launcher is
  held before GATE_READY; the child is terminated after
  ACK 0. Expected: supervisor observes via pidfd, sends
  ABORT (CHILD_TERMINATED_PRE_RELEASE), RELEASE never
  appears in the channel log, the launcher's STATUS is
  recorded as its final report, attempt closed pre-release
  with the specified facts.
- **D-T3a — termination before the final poll.**
  GATE_READY delivered; the child is terminated in S5
  before the final guard poll. Expected: the guard (or the
  event observation) diverts to the ABORT path; the channel
  log proves no RELEASE packet was ever sent.
- **D-T3b — termination in the poll-to-send interval.**
  The child is terminated after the final guard's clean
  poll but before (or as) RELEASE is transmitted. Expected:
  RELEASE stands recorded as sent; termination is recorded
  as observed via the pidfd; the record states the relative
  timing of termination and RELEASE as UNKNOWN; the attempt
  proceeds on the S6 path to its Stage 8 disposition, with
  no claim anywhere that the child was alive at
  transmission.
- **D-T4 — the gate-write boundary.** RELEASE delivered;
  the launcher's write is held by the test hook while the
  child terminates. Expected: the write returns EPIPE; the
  launcher **survives** (SIGPIPE ignored — evidenced by what
  follows); GATE_WRITE_FAILED (class 1, errno EPIPE) is
  received; GATE_ACTUATED is never received; STATUS follows;
  actuation is recorded FAILED; the record closes on the
  STATUS/pidfd pair with no fact rewritten.

Each demonstration's expected supervisor record entries are
part of its pass condition, not just its process outcomes.

---

**Asked of Alex:** his independent pass on this plan — in
particular whether the readiness check plus the state rules
close the zombie case completely, and his cross-check of the
pre-release matrix (his offer to prepare one is welcomed as
exactly that cross-check). On his approval, Rev 18 is
drafted as the §3.5 point 3 amendments listed in Part 4 and
shelved for full inspection. Rev 17 is preserved unchanged.

— Remmy, 2026-11-13
