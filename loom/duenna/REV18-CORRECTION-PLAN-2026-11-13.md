# Rev 18 Correction Plan — Pre-Release Child Termination

**Prepared by Remmy, 2026-11-13, against Alex's independent
inspection of Rev 17 (pb-mwfmeh4q-a-kbfd — NOT CLEARED, one HIGH
blocker).** Rev 17, Plan Rev 6, and all earlier revisions are
preserved unchanged. This plan covers the finding's five points
together. Nothing here reopens any accepted part of Plan Rev 6
or of the Rev 17 incorporation; Option A is preserved
throughout — the launcher remains the child's sole waitpid()
reaper while it lives, and the supervisor never becomes the
child's parent or reaper.

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

**SIGCHLD disposition — now specified.** The readiness
semantics below rely on a terminated child **persisting as a
zombie until the launcher reaps it**. That holds only under
the default SIGCHLD disposition. The launcher SHALL leave
SIGCHLD at its default disposition and SHALL NOT set it to
SIG_IGN (which would make the kernel auto-reap the child,
destroying both the zombie and the waitpid() status this
design exists to capture), and SHALL NOT install a SIGCHLD
handler that reaps outside the specified waitpid() points.
The supervisor's own SIGCHLD disposition is irrelevant to the
child (it is not the parent) and is not relied on.

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
observed terminated at send.

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
   — in S3–S6, a STATUS sent after a supervisor ABORT for
   child termination is the launcher's expected final
   report: validated, recorded, reopening nothing. (This
   does not disturb the post-release rule: after a
   completed closure, or after an ABORT in S8, a later
   STATUS remains a violation.)
8. Message catalogue: add 0x0A GATE_WRITE_FAILED; ABORT
   detail format specified for CHILD_TERMINATED_PRE_RELEASE
   (raw wait_status u32).
9. Point 2 gains two launcher requirements: SIGCHLD left
   at default disposition (no SIG_IGN, no reaping handler);
   SIGPIPE ignored from the first act.

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
- **D-T3 — termination immediately before release.**
  GATE_READY delivered; the child is terminated in S5
  before RELEASE. Expected: the pre-RELEASE readiness guard
  (or the event observation) diverts to the ABORT path;
  the channel log proves no RELEASE packet was ever sent.
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
