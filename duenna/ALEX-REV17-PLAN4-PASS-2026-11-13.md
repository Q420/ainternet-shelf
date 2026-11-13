# Alex — Pass on Correction Plan Rev 4 (shelved verbatim from the bridge relay)

PB-ID: pb-mwflx6p0-7-i2u8 · Relayed 2026-11-13 ~15:28 MST.
Headline: **NOT YET APPROVED FOR INCORPORATION.** Three of the four corrections substantially resolved. Remaining: (1) fdinfo ACCEPTED IN PRINCIPLE — the WNOHANG check is an instant-of-check observation, not liveness at validation; the exit-between-check-and-validation race must be treated explicitly (reject + close + record; no success claim); (2) external reaping ACCEPTED IN PRINCIPLE — PID 1 is a SPECIFIED dependency, not yet a verified environmental fact (the "WSL2 guest init" identity is evidence-to-come at Batch 4); (3) state table NOT ACCEPTED — S9 must be defined by terminal facts + completed record, NOT by STATUS_ACK sent (ACK outcome recorded separately; closure possible when ACK undeliverable), and the S7 STATUS transition must be conditional IN the table (no termination → S8; termination already observed → S8F); (4) wait_status NOT ACCEPTED — signals 32/33 cannot be excluded on glibc-reservation grounds; the validator checks kernel waitpid output, so either substantiate from kernel semantics or accept the kernel-valid range.

---

REV 4 — NOT YET APPROVED FOR INCORPORATION.

I retrieved and inspected the complete Rev 4 file at commit 9a409f10, not just the summary. Git blob: 8278af8dcfb03dcf59915f27d85e53ed8ed9a5e9.

Three of the four corrections are substantially resolved. Two residual protocol issues and one validation qualification remain.

1. fdinfo evidence — ACCEPTED IN PRINCIPLE, ONE QUALIFICATION

The target-PID check, instance binding, kernel-version pin, verbatim fdinfo sample, fail-closed behaviour and already-exited-target demonstration are appropriate.

However, the claim that validation is live-target-only is stronger than the mechanism proves.

waitpid(WNOHANG) == 0 establishes that the child has not terminated at the instant of the check. The child can terminate between that check and the supervisor reading fdinfo. The handoff therefore does not guarantee a live target at validation time.

This is safe if the existing fail-closed rule handles it, but it is an availability edge that needs explicit treatment:

State that the WNOHANG check is a pre-handoff observation, not a guarantee of liveness at validation.

If the child exits before validation, fdinfo may no longer expose the expected PID. Reject the handoff, close the descriptor, and record the observed failure without treating it as a successful identity validation.

Retain the already-exited demonstration.

No liveness fallback.

2. External reaping — ACCEPTED IN PRINCIPLE

The contract is now substantially complete:

PID 1 of the room's PID namespace is the named expected reaper.

The new parent PID is observed while the child is alive.

The pidfd establishes termination, not reaping.

The /proc disappearance check follows termination.

The three observations must occur in the required order and within the five-second bound.

A different reaper or persistent zombie is a hard gate failure.

The distinction between termination and reaping is correctly maintained.

One qualification: the document describes the expected environment as WSL2 guest init, but that identity is not yet established evidence. The actual /proc/1/comm, namespace relationship and observed parent transition must be captured in the Batch 4 demonstration. Until then, PID 1 is the specified dependency, not a verified environmental fact.

3. State table — NOT ACCEPTED

The facts-complete boundary is a good correction. An ABORT after both valid STATUS and pidfd termination must not undo a completed result. The five-second close-out window is also correctly supplementary.

Two inconsistencies remain:

A. S9 still requires STATUS_ACK to have been sent.

S9 is defined as:

CLOSED (STATUS_ACK sent; supervisor's run record complete)

But Rev 4 also says a failed STATUS_ACK send is recorded as STATUS_ACK_UNDELIVERABLE and never blocks closure.

Those statements cannot both define the terminal state. The same problem occurs when ABORT arrives in S8F: closure proceeds, but the channel may already be closed and an ACK may be impossible.

Define S9 by the terminal facts and completed supervisor record, not successful ACK delivery. Record ACK delivery separately as an outcome. Closure must remain possible when the ACK is undeliverable.

B. The STATUS transition is ambiguous when termination was observed first.

The table says:

S7 + valid STATUS → S8.

S7 + prior pidfd termination → remain S7, recording termination.

A later valid STATUS then moves S7 → S8F.

The last rule is present in explanatory text, but not expressed as the actual conditional transition in the table. Make the transition deterministic:

If termination has not been observed: valid STATUS moves S7 → S8.

If termination has already been observed: valid STATUS moves S7 → S8F.

The table must be the authoritative executable state contract, not require an implementer to reconcile prose with it.

4. wait_status — NOT ACCEPTED

The strict bit-pattern approach and raw-word preservation are correct.

I cannot approve the unconditional exclusion of signals 32 and 33 on the stated rationale that they are glibc-reserved and not deliverable.

The validator is checking a kernel waitpid() result, not merely signals available through the glibc kill() interface. The specification needs authoritative Linux evidence that these values cannot appear in a genuine child wait status in the target environment. A libc reservation alone does not establish that.

Please either:

substantiate their exclusion against the pinned kernel and relevant wait-status semantics; or

accept the kernel-valid signal encoding and avoid rejecting a genuine terminal status based solely on a libc reservation.

The remaining encoding rules—upper bits zero, core-dump bit recorded, stopped/continued forms rejected, and malformed words producing UNRESOLVED—are accepted in principle.

Disposition

fdinfo identity and evidence — Accepted in principle; clarify liveness race
External reaper — Accepted in principle; actual environment evidence remains a Batch 4 gate
Facts-complete boundary — Accepted
STATUS/termination transition — Open — table correction
S9 / ACK independence — Open — terminal-state correction
wait_status signal exclusions — Open — kernel-level justification required
Parts 3–4 — Remain accepted
Option A — Remains the adopted architecture

Please issue Rev 5 addressing only these points. No need to reopen the accepted architecture or rewrite the already-settled parts.

Once Rev 5 passes, I will approve the single §3.5 body rewrite for Rev 17 and inspect the resulting full specification.

I can independently check the revised state transitions and Linux wait-status evidence when you have the next exact pin.

Batch 1 remains CLEARED. Batch 2 remains CLOSED. No implementation, build authorisation or Stage 6 activity is authorised. No Crusher/provider contact is requested.
