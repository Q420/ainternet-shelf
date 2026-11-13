# B1-6 — Architecture Decision (BEN'S RULING, 2026-11-13)

**Ruled by Ben, 2026-11-13 ~15:07 MST**, by his tap on the scope card
presented the same hour: "Adopt Option A with Alex's four corrections —
open Rev 16 drafting." This document is the decision of record. It adopts
the architecture recommended in duenna/B16-DESIGN-PROPOSAL-2026-11-13.md
(f0a79243) as independently reviewed by Alex
(ALEX-B16-D18-D9-INDEPENDENT-REVIEW-2026-11-13, pb-mwfl2iic-2-gfzx).
Alex's review was a recommendation; this ruling is Ben's.

## The ruled process model (Option A, as corrected)

1. **The launcher is the harness child's operating-system parent for the
   child's whole life, and its reaper.** It spawns and establishes the
   child, holds the waitpid() relationship, performs the child's
   privilege-transition sequence under its control, and reports the
   child's exit status (PID + exit status/signal) to the supervisor over
   the status channel. The child's PR_SET_PDEATHSIG protection points at
   the launcher, as §3.5's existing design requires.
2. **The supervisor owns the record.** Records, issuance, commitments and
   terminal-event decisions belong to the supervisor (Python,
   pilot-supervisor identity), acting on facts the launcher reports and
   on the child-lifecycle handle at (C). The supervisor never waitpids a
   process that is not its child and never treats the launcher's report
   alone as proof beyond what the protocol establishes.
3. **Launcher exit means exactly one thing:** the status word has been
   delivered and acknowledged, and the launcher's work is complete. Any
   other launcher disappearance is LAUNCHER_LOST.
4. **Option B (subreaper adoption by the supervisor) is REJECTED** — a
   child that has armed PR_SET_PDEATHSIG/SIGKILL against the launcher
   dies when the launcher dies and never re-arms; deferring the arming
   reintroduces the race. It is not a fallback.

## The four corrections (Alex's A–D, adopted as part of the ruling)

- **A — Launcher↔supervisor parent-death race.** The supervisor captures
  its own expected PID before launching; that identity reaches the
  launcher inside the fixed, validated launch request. The launcher
  drops privilege, then arms its own PR_SET_PDEATHSIG against the
  supervisor, reads the setting back, and verifies its parent is still
  the expected supervisor. Any mismatch or failed read-back aborts the
  launch. A bare getppid() check does not satisfy this correction.
- **B — Spawning-thread lifetime.** Parent-death is thread-based. The
  supervisor guarantees the thread that spawned the launcher remains
  alive for the launcher's entire lifecycle (or the design states its
  explicit equivalent, reviewed as such).
- **C — Launcher loss is not proof of child death.** A child pidfd is
  transferred to the supervisor before the launch gate is released; no
  gate release without it. Supervisor-side child termination is observed
  through that handle. No terminal closure merely on status-channel EOF;
  no successful issuance after launcher loss; if child termination
  cannot be established, the issuance remains UNRESOLVED and the run
  halts pending recovery. Transfer failure, or launcher death before
  transfer, is a defined abort, not an improvisation point.
- **D — Status-channel contract.** The descriptor protocol is specified
  precisely in the specification: request framing, status framing,
  descriptor ownership, close-on-exec behaviour, EOF semantics,
  malformed/partial message handling, and acknowledgement of the
  pre-release handoff. A valid child exit report must be distinguishable
  from a truncated message and from unexpected launcher death.

## Consequences

- Rev 16 drafting is OPEN on this ruling: §0.5 B1-6 and §3.5 are aligned
  to this model, with failure demonstrations (kill-the-launcher and
  kill-the-supervisor drills, pidfd/no-closure-on-EOF behaviour) carried
  as gate evidence requirements.
- Nothing in this ruling authorises a build, a model call, or a publish
  beyond the Rev 16 drafting and its inspection round. Batch 2 remains
  CLOSED until an inspected, cleared revision meets Ben's re-issued go.
- Alex reviews this decision and the resulting process model before the
  amendment is treated as settled (his offer, accepted).

— Recorded by Remmy from Ben's tap, 2026-11-13.
