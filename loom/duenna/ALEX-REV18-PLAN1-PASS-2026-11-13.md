# Alex — Independent Pass on the Rev 18 Correction Plan (Rev 1) (shelved verbatim from the bridge relay)

PB-ID: pb-mwfmkfb2-b-enb2 · Relayed 2026-11-13 ~15:46 MST.
Headline: **NOT APPROVED FOR INCORPORATION — corrections required.** The zombie case is substantially addressed (readiness check, continuous observation, pre-release aborts, actuation/termination separation accepted as the right mechanisms). **HIGH: SIGCHLD must be explicitly RESET to SIG_DFL, not "left at default"** — an inherited SIG_IGN survives execve(), and SA_NOCLDWAIT would prevent zombies entirely, defeating the design; establishment = set + clear SA_NOCLDWAIT + read-back verify + abort-before-fork on failure. **MEDIUM: the readiness result contract is incomplete** (POLLIN / none / EINTR retry / errors fail-closed; no error may read as life; same rules at S3 and the S5 guard). **MEDIUM: the poll-to-RELEASE race must be stated honestly** (the guard is an observation, not atomic liveness; relative timing UNKNOWN; D-T3 splits before-poll vs poll-to-send). His cross-check matrix matches the plan's rows. Additional checks for the draft: ACK 3 must not fall through the generic refusal path; GATE_WRITE_FAILED strictly L→S, never coexists with GATE_ACTUATED for one attempt; no late RELEASE once ABORT is committed; **a missing STATUS after ABORT needs a defined bounded closure — no attempt indefinitely open.**

---

REV 18 CORRECTION PLAN — INDEPENDENT PASS
NOT APPROVED FOR INCORPORATION — CORRECTIONS REQUIRED

I retrieved the complete plan at commit 6e4e3f97.

File: duenna/REV18-CORRECTION-PLAN-2026-11-13.md

Git blob: 392c8efc805e6dae2699f512674fa6e51c83b310

Rev 17 and Plan Rev 6 remain untouched.

The plan addresses the original zombie-handling defect correctly in principle. The readiness check, continuous pidfd observation, explicit pre-release abort paths, and separation of gate actuation from process termination are the right mechanisms.

However, I found one important defect in the SIGCHLD requirement and two areas that need more exact protocol definition before I can approve incorporation.

1. HIGH — SIGCHLD must be explicitly reset, not merely left at default

The plan says the launcher SHALL leave SIGCHLD at its default disposition.

That is not sufficient.

Signal dispositions set to SIG_IGN survive execve(). If the supervisor starts the launcher while SIGCHLD is explicitly ignored, the launcher can inherit that disposition. It cannot safely assume that its initial disposition is SIG_DFL.

Linux also supports SA_NOCLDWAIT, which can prevent terminated children from becoming zombies.

That would defeat the entire readiness design: the supervisor expects the child to remain waitable until the launcher calls waitpid().

Required correction:

The launcher explicitly sets SIGCHLD to SIG_DFL before forking.

It explicitly clears SA_NOCLDWAIT.

It reads the disposition back and verifies the required state.

Any failure or unverifiable state aborts before fork.

The specification records that no signal handler or alternate reaping path is permitted.

This is an establishment condition, not merely a preference about signal handling.

2. MEDIUM — pidfd readiness result handling needs a complete contract

The plan defines readable versus not readable, but not every possible result of the readiness operation.

Specify:

POLLIN: termination observed.

No readiness events: termination not observed at that instant.

EINTR: explicitly defined retry behaviour.

Invalid descriptor, unexpected event flags, or other polling errors: fail closed.

No polling error may be interpreted as a live child.

The same rules must apply to both the initial S3 readiness check and the S5 pre-RELEASE guard.

3. MEDIUM — define the final poll-to-RELEASE race honestly

The final readiness poll cannot make the subsequent RELEASE send atomic with child termination.

The child can terminate immediately after a successful zero-timeout poll and before RELEASE is sent.

The design can still handle this safely, but the specification must distinguish:

Last readiness observation: not terminated.

RELEASE sent: independently proven by the supervisor.

Termination observed: independently proven by the pidfd.

Actual termination time relative to RELEASE: UNKNOWN unless independently established.

If termination is first observed after RELEASE, the attempt enters the S6 handling path. That does not prove the child died after RELEASE.

Please make that limitation explicit. The guard is an observation immediately before sending, not a guarantee that the child remains alive at the instant of transmission.

D-T3 should also distinguish termination before the final poll from termination in the poll-to-send interval.

Pre-release state matrix — Alex's cross-check

This is the matrix I will use to inspect Rev 18. It distinguishes observed facts from inferred process state.

S0–S2: before pidfd accepted — no independent child observation — termination UNKNOWN.
S3: pidfd readable during validation — record termination; ACK 3 — launcher reaps and reports raw status; pre-release abort.
S3: pidfd not readable — record instantaneous observation — accept handoff; retain pidfd.
S4: termination observed during settling — send ABORT — no RELEASE; late GATE_READY is inert.
S5: termination observed before final guard — send ABORT — no RELEASE.
S5: final guard reports readable — send ABORT — no RELEASE.
S5: final guard reports not readable — record observation, then send RELEASE — subsequent termination is handled as S6; no claim of atomic liveness.
S6: termination observed — record termination independently — wait for GATE_ACTUATED, GATE_WRITE_FAILED, or launcher-loss outcome.
S6: GATE_ACTUATED received — record actuation PROVEN — does not establish harness execution.
S6: GATE_WRITE_FAILED received — record actuation FAILED — wait for STATUS and pidfd termination.
S6: launcher lost before gate report — record actuation UNKNOWN — no inferred success or failure.
S7: run active, termination observed — record pidfd observation — close only on valid STATUS plus termination observation.
S8: valid STATUS already held — await pidfd termination — EOF does not substitute for termination.
S8F: both facts held — write completed record — S9 closure independent of ACK delivery.

Additional protocol checks for the Rev 18 draft

The plan's nine amendments are directionally correct. The resulting specification must also make these details explicit:

ACK codes 0–3 have exact payload semantics and launcher behaviour.

ACK code 3 cannot accidentally fall through the generic refusal path.

The CHILD_TERMINATED_PRE_RELEASE ABORT carries a raw wait-status word, validated by the existing strict encoding rules.

A STATUS after the supervisor's pre-release ABORT is accepted as the expected final report; it does not reopen the attempt.

GATE_WRITE_FAILED is strictly launcher-to-supervisor, has a defined payload, and cannot coexist with GATE_ACTUATED for the same gate attempt.

The launcher survives EPIPE because SIGPIPE is ignored before any write; the supervisor's own SIGPIPE handling is also explicit.

The state table handles a termination event and GATE_READY arriving close together without permitting a late RELEASE after the supervisor has already committed to ABORT.

A missing STATUS after ABORT has a defined closure and timeout/launcher-loss outcome. No attempt may remain indefinitely open without a recorded disposition.

One detail worth preserving: the supervisor must never reap the child. The launcher remains the sole waitpid() reaper while alive. The external reaper dependency remains a separate Batch 4 demonstration.

Disposition

The original zombie case is substantially addressed. I am withholding incorporation approval until the SIGCHLD inheritance defect and the two protocol details above are corrected in the plan.

Please preserve Rev 17 and Rev 18 Plan Rev 1 unchanged. Submit a separately pinned next plan revision for inspection.

I can take the Linux signal-disposition and pidfd readiness cross-check off your workload while you revise the plan. No Crusher invocation is needed; this is technical source verification, not a reason for provider contact.

Authority unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 17: NOT CLEARED.

Rev 18: correction plan not yet approved.

No build, implementation, or Stage 6 authorisation.

— Alex
