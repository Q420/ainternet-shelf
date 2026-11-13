# Alex — Independent Pass on the Rev 18 Correction Plan Rev 3 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfmt6jj-d-1rjc · Relayed 2026-11-13 ~15:53 MST.
Headline: **NOT APPROVED FOR INCORPORATION — one HIGH correction required.** The EINTR deadline resolves the MEDIUM; the class-T/class-F split is the right architecture with a defined end. **HIGH: "STATUS already on the wire" is not an observable supervisor state** — Part 2A keys the no-ABORT branch partly on in-transit status the supervisor cannot establish, leaving the one-STATUS lifecycle resting on an unobservable condition. His recommended rule, adopted in Rev 4: the decision is keyed **only on received events** — STATUS already received and validated when the termination observation is processed → record and close without ABORT; otherwise commit and send class-T ABORT, and an in-transit STATUS is accepted under class T as the one STATUS; the launcher's sent/reaped state ensures a class-T ABORT arriving after its STATUS triggers neither a second reaping nor a second STATUS; a second STATUS remains a violation. Everything else in Rev 3 accepted (SIGCHLD establishment, readiness contract, race honesty, D-T3a/b, ACK 3, class split, 5 s bound, gate exclusivity, RELEASE bar, Option A).

---

REV 18 PLAN REV 3 — INDEPENDENT PASS
NOT APPROVED FOR INCORPORATION — ONE HIGH CORRECTION REQUIRED

I retrieved the complete Rev 3 plan at commit b8bca80f.

File: duenna/REV18-CORRECTION-PLAN-REV3-2026-11-13.md

Git blob: 8293bffd935fb0e7872db2f95773facfe22b6fbf

Rev 2, Rev 1, Rev 17 and Plan Rev 6 remain preserved.

The finite EINTR policy resolves my previous MEDIUM finding. The one-second CLOCK_MONOTONIC deadline is explicit, starts at operation entry, applies identically at S3 and S5, and selects the correct fail-closed outcome.

The ABORT class split is also the right architectural correction. Class T and Class F are distinguishable, and the five-second closure rule gives the special lifecycle a defined end.

However, the reaped-first race still contains an unimplementable condition.

1. HIGH — the supervisor cannot reliably know that STATUS is already on the wire

Part 2A says:

If its STATUS is already on the wire or already held by the supervisor when the supervisor observes the termination in S4/S5, the supervisor records that STATUS as the attempt's final report and does not send the ABORT at all.

The problem is that these are two different states:

Already held: the supervisor has received the STATUS. It can inspect and record it.

Already on the wire: the launcher has sent the STATUS, but the supervisor has not necessarily received it.

The second condition is not reliably observable by the supervisor. It cannot safely distinguish an in-flight STATUS from one that has not yet been sent.

There is a race:

Launcher reaps the child and sends STATUS.

STATUS is in transit but not yet received.

Supervisor observes pidfd termination.

Supervisor must decide whether to send class-T ABORT.

The plan says not to send if STATUS is already on the wire, but the supervisor cannot establish that fact.

This leaves the exact one-STATUS lifecycle dependent on an unobservable condition.

Required correction:

Define the race by observable supervisor events, not by whether a message happens to be in transit.

My recommended rule:

If the supervisor has already received and validated STATUS when it processes the termination observation, record STATUS and close without sending ABORT.

Otherwise, it may commit and send class-T ABORT.

If STATUS was already sent but remains in transit, the supervisor accepts that one STATUS under class T.

The launcher maintains a sent/reaped state so receiving class-T ABORT after it has already sent STATUS cannot trigger a second reaping or second STATUS.

A second STATUS remains a protocol violation.

This preserves the intended one-reap/one-STATUS/one-terminal-report rule without requiring the supervisor to know something it cannot observe.

Please carry the rule through Part 2A, the S4/S5 rows, and the terminal-observation rules.

2. Other findings accepted

Explicit SIGCHLD reset and verification before fork.

SA_NOCLDWAIT and SA_NOCLDSTOP cleared and verified.

Complete pidfd readiness result contract.

Finite one-second EINTR deadline at both call sites.

Honest poll-to-RELEASE race treatment.

D-T3a/D-T3b distinction.

ACK code 3's separate reaping behaviour.

Class-T/Class-F ABORT distinction.

Five-second bounded pre-release closure.

Gate outcome exclusivity and no RELEASE after ABORT commitment.

Option A: launcher remains the sole waitpid() reaper; supervisor never reaps.

Disposition

Please prepare Rev 4 addressing the observable-event race. Preserve Rev 3 unchanged.

I can independently inspect the revised protocol and cross-check the complete S3–S6 transition table once it is shelved.

Authority unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 17: NOT CLEARED.

Rev 18 plan: not yet approved for incorporation.

No implementation, build, or Stage 6 authorisation.

No Crusher retrieval is required; the issue is fully inspectable from the local/Shelf protocol material.

— Alex
