# Alex — Independent Pass on the Rev 18 Correction Plan Rev 2 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfmoosd-c-8uep · Relayed 2026-11-13 ~15:49 MST.
Headline: **NOT APPROVED FOR INCORPORATION — two corrections required.** The three Rev 1 findings are substantially resolved (SIGCHLD establishment, readiness contract, honest race limitation, matrix adopted). **HIGH: the pre-release ABORT flow contradicts Rev 17's fire-and-close ABORT contract** — the plan never redefines the channel lifecycle; required: two distinct ABORT behaviours (pre-release child-termination ABORT keeps the channel open for exactly one final STATUS; all other terminal ABORTs stay fire-and-close), reflected in the catalogue, terminal-observation rules and state table, plus the race where the launcher reaped before the ABORT arrived (exactly one STATUS, one reaping, one report — neither arrival order a violation or a duplicate). **MEDIUM: EINTR "without bound" has no measurable stopping condition** — a finite deadline/retry policy must be specified by the plan, not chosen by the implementation. His matrix accepted as the inspection reference subject to the ABORT correction; everything else in Rev 2 accepted (SIGCHLD reset verified, D-T3a/b, ACK 3 separation, gate-outcome exclusivity, ABORT-commitment RELEASE bar, 5 s missing-STATUS disposition, Option A intact).

---

REV 18 PLAN REV 2 — INDEPENDENT PASS
NOT APPROVED FOR INCORPORATION — TWO CORRECTIONS REQUIRED

I retrieved the complete Rev 2 plan at commit 710199d4.

File: duenna/REV18-CORRECTION-PLAN-REV2-2026-11-13.md

Git blob: 8dd79c4e684b90549f9104c7923b9990c1e333a3

Rev 1, Rev 17 and Plan Rev 6 remain preserved.

The three corrections from my previous inspection are substantially resolved. The readiness contract, explicit SIGCHLD establishment, and honest poll-to-RELEASE limitation are all materially improved. The adopted pre-release matrix is also a sound basis for the next inspection.

I cannot approve incorporation yet. Two protocol issues remain.

1. HIGH — pre-release ABORT and STATUS contradict the existing fire-and-close contract

Rev 17's protocol says ABORT is fire-and-close. Its terminal-observation rules also say a STATUS arriving after a supervisor-sent ABORT is a protocol violation and is ignored.

Rev 18 now requires something different:

Supervisor observes child termination in S4 or S5.

Supervisor sends ABORT.

Launcher reaps the child.

Launcher sends STATUS as its expected final report.

Supervisor validates and records that STATUS.

That is a legitimate design change, but it is not just a new terminal-observation exception. The underlying channel lifecycle must change too.

The plan does not explicitly say whether the supervisor's pre-release ABORT keeps the channel open, whether the launcher is permitted to send STATUS after receiving it, or how the existing fire-and-close behaviour is superseded.

Required correction:

Define two distinct ABORT behaviours:

Pre-release child-termination ABORT: channel remains open for the launcher's one permitted final STATUS; supervisor validates and records it; then the channel closes under the specified completion or bounded-failure rule.

All other terminal ABORTs: retain the existing fire-and-close semantics unless another explicitly defined exception applies.

Also define the race where the launcher has already received waitpid() before the ABORT arrives. There must be exactly one STATUS, one reaping operation, and one terminal report. Neither arrival order may create a duplicate or turn the expected STATUS into a violation.

This needs to be reflected in the message catalogue, terminal-observation rules, and state table—not only in the prose amendment.

2. MEDIUM — repeated EINTR has no measurable stopping condition

The plan says EINTR causes re-polling, and repeated interruption without bound fails closed as POLL_INCOMPLETE.

That describes the desired outcome but not how the implementation determines that interruption has become unbounded.

Required correction:

Specify a finite operational limit, such as a monotonic-clock deadline or a bounded retry policy. State:

What starts the deadline.

Whether the same deadline applies at S3 and S5.

What happens when the deadline expires.

Which observation is recorded.

How the S3 refusal and S5 no-RELEASE/ABORT paths are selected.

Do not let an implementation choose its own retry count or timeout.

Matrix cross-check

The plan's pre-release matrix matches the intended state progression in the main cases: termination before handoff correctly detected and refused; termination during settling — correct ABORT/no-RELEASE path; termination before final poll — correct no-RELEASE path; termination after final poll but before send — correctly records timing as UNKNOWN; termination after RELEASE — correctly enters S6 without inferring ordering; gate write returns one byte — actuation PROVEN; gate write fails — actuation FAILED, never reported as actuation; launcher lost at gate write — actuation UNKNOWN; STATUS and pidfd facts — closure requires both; missing STATUS after pre-release ABORT — bounded disposition specified. The matrix is therefore accepted as the inspection reference, subject to the ABORT-channel correction above.

Other findings accepted

SIGCHLD is explicitly reset and verified before fork.

SA_NOCLDWAIT and SA_NOCLDSTOP are cleared and read back.

No alternate SIGCHLD handler or reaping path is permitted.

S3 and S5 share one readiness-operation contract.

Poll errors and unexpected readiness flags fail closed.

A clean poll is not represented as proof of life at RELEASE.

D-T3a and D-T3b distinguish the two termination windows.

ACK code 3 is distinct from the generic refusal path.

Gate outcome messages are mutually exclusive, with contradictory arrivals recorded as violations.

RELEASE is barred after the supervisor commits to ABORT.

The five-second pre-release closure bound gives missing STATUS a defined disposition.

Option A and the launcher-only waitpid() responsibility remain intact.

Disposition

Please prepare Rev 3 addressing the ABORT lifecycle and finite EINTR policy. Preserve Rev 2 unchanged.

I can independently cross-check the revised state table against the original protocol and the accepted matrix once it is shelved.

Authority remains unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 17: NOT CLEARED.

Rev 18 plan: not yet approved for incorporation.

No implementation, build, or Stage 6 authorisation.

— Alex
