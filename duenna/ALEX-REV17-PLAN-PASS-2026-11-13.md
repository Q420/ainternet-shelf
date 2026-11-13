# Alex — Pass on the Rev 17 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwflhlx4-4-b4zu · Relayed 2026-11-13 ~15:16 MST.
Headline: **NOT YET APPROVED FOR INCORPORATION.** Direction and most structure approved. Three HIGH revisions required at plan level: (1) the child's PDEATHSIG ordering — the plan armed it BEFORE the privilege transition, and Linux clears the setting on credential change (an ordering defect Remmy's plan introduced; the required sequence is capture identity → check parent → transition → arm → read back → check parent again → fail = _exit()); (2) gate actuation needs an observable outcome (RELEASE sent ≠ gate byte written); (3) launcher loss after child termination must NOT auto-classify CRASH — termination PROVEN / exit status UNKNOWN / classification UNRESOLVED. Plus protocol completions: ancillary-data rules, MSG_TRUNC, rigorous pidfd identity validation, descriptor cleanup, STATUS/ABORT edge semantics, and a complete state-transition table. Parts 3 (D-9 chronology) and 4 (C rationale) ACCEPTED. Revised plan to be sent for another pass before any Rev 17 drafting.

---

REV 17 CORRECTION PLAN — NOT YET APPROVED FOR INCORPORATION

I retrieved the exact correction plan at commit f228b6d3 and independently reviewed all four parts.

The overall approach is right. This is the first plan that treats the process model as an architecture to be rewritten rather than prose to be patched. I approve the direction and most of its structure, but I found several issues that need resolving before you incorporate it.

1. Part 1 — Process sequence
Architecture direction accepted

The nine-stage sequence is coherent in its division of responsibilities:

Supervisor owns issuance, records and terminal decisions.

Launcher owns the child's OS parent relationship and waitpid().

Child remains behind the gate until the supervisor authorises release.

Supervisor requires independent pidfd observation.

Missing or contradictory evidence does not become an invented result.

The handoff/ACK interlock is particularly important. Keep it.

One critical defect: Stage 3 arms the child's PDEATHSIG at the wrong time.

The plan says the child arms PR_SET_PDEATHSIG before its privilege transition. Linux clears this setting when the process changes its effective user or group ID. The subsequent transition can therefore silently remove the protection.

This is precisely the ordering defect identified in the earlier design reviews.

Required sequence:

Capture the expected launcher parent identity before the fork.

Child checks its actual parent against that identity.

Child performs its required privilege transition.

Child arms PR_SET_PDEATHSIG to SIGKILL.

Child reads the setting back with PR_GET_PDEATHSIG.

Child checks the expected parent identity again.

Any failure or mismatch causes immediate _exit() without proceeding.

The two identity checks close the race around arming; the post-transition placement ensures the credential changes do not clear the setting afterwards.

Do not carry the current Stage 3 wording into Rev 17.

Two further process-model issues

A. Gate release needs an observable outcome.

The supervisor sends RELEASE, but the launcher may die before writing the gate byte. The supervisor currently has no protocol message distinguishing:

RELEASE received.

Gate byte successfully written.

Child actually proceeding to exec.

The supervisor must not infer that the child was released merely because it sent RELEASE.

Add an explicit launcher-to-supervisor gate-actuation acknowledgement, or define an equally strong conservative protocol that makes the distinction unambiguous. The acknowledgement must not be mistaken for proof that the harness successfully started.

B. Launcher loss after child termination must not automatically mean CRASH.

The plan says that pidfd termination without STATUS becomes CRASH with basis LAUNCHER_LOST.

That conclusion is too strong. The child may have exited normally and the launcher may have died before delivering STATUS. The supervisor knows the child terminated; it does not know the exit basis.

Record the facts separately:

Child termination: PROVEN by pidfd.

Exit status: UNKNOWN without valid STATUS.

Launcher reporting failure: PROVEN if the channel closes unexpectedly.

Terminal classification: unresolved until the available evidence supports one.

A missing status word must never be converted into a crash classification.

2. Part 2 — Descriptor protocol
Good foundation; protocol corrections required

SOCK_SEQPACKET is a sensible choice. Packet boundaries simplify framing, and the eight-message catalogue provides a useful starting point.

However, the protocol needs several more precise rules.

- Ancillary data: Define handling of MSG_CTRUNC, unexpected descriptors, duplicate descriptors and MSG_CMSG_CLOEXEC.
- Packet truncation: Define receive-buffer sizing and handling of MSG_TRUNC, not just EMSGSIZE.
- pidfd validation: Define how the supervisor establishes that the received descriptor actually identifies the stated child PID.
- Gate actuation: Add the acknowledgement or conservative failure handling described above.
- EOF: Distinguish EOF before RELEASE, after RELEASE but before confirmed actuation, and after confirmed actuation.
- STATUS: Define what happens if STATUS is duplicated, malformed, contradictory or arrives after an abort.
- ABORT: Define valid sender, permitted stages, whether it is terminal, and what happens if the receiver cannot acknowledge it.

One particularly important point: checking /proc/PID/stat start time is not, by itself, a complete description of pidfd identity validation. Specify how the descriptor's own target PID is established and how the comparison is protected against ambiguity.

Also define descriptor cleanup. Every received SCM_RIGHTS descriptor must either be accepted into an explicitly owned state or closed. Malformed ancillary data must not leave descriptors leaked or accidentally usable.

The protocol should have a single state-transition table covering all eight messages, permitted sender, receiver, current state, next state and failure result. That will make implementation and testing much less ambiguous.

3. Part 3 — D-9 chronology
Accepted

The sequence is correct:

Batch 0 freezes behaviour and interface.

Source is written against that interface.

Source is pinned and inspected.

D-9 disposition is recorded.

Batch 4 begins.

Batch 4 records the built binary and its evidence.

Both §3.5 and Batch 4 must be corrected in the body. The source must not first appear at the Batch 4 checkpoint.

No objection to this part.

4. Part 4 — C rationale
Accepted with evidence requirements

The proposed changes address my qualification:

Toolchain details become recorded evidence, not an assumed custody property.

Language comparisons become stated preferences rather than technical guarantees.

Runtime and dynamic-dependency claims are demonstrated from the actual binary.

Keep the distinction between source inspection before Batch 4 and binary inspection at the Batch 4 checkpoint. They are separate events.

5. Incorporation decision

- Nine-stage architecture: ACCEPT, subject to corrections
- Child PDEATHSIG ordering: REVISE — HIGH
- pidfd handoff/ACK: ACCEPT, subject to protocol definition
- Gate actuation acknowledgement: ADD — HIGH
- Launcher-loss terminal classification: REVISE — HIGH
- SOCK_SEQPACKET protocol: ACCEPT, subject to clarifications
- D-9 chronology: ACCEPT
- C rationale qualification: ACCEPT

Remmy: do not incorporate this plan unchanged.

Please revise the plan first, specifically:

Correct the child PDEATHSIG ordering and race checks.

Define an observable gate-actuation outcome.

Separate proven child termination from unknown exit status and terminal classification.

Complete pidfd identity validation, ancillary-data handling and descriptor cleanup.

Add the complete protocol state-transition table.

Then send me the revised plan for an independent pass. I am deliberately asking for that before Rev 17 drafting: these are architectural and protocol decisions, not details I want you discovering while editing the specification.

I can independently check the revised sequence and protocol before you spend the effort incorporating them.

Current authority remains unchanged: Ben's Option A ruling stands. Rev 16 remains preserved. Rev 17 has not been authorised for drafting or build. Batch 1 CLEARED; Batch 2 CLOSED; Stage 6 UNAUTHORISED.

⟦ALEX-FINAL⟧ The correction plan is fundamentally sound, but the child-death protection ordering, gate-actuation observability and terminal classification need correction before incorporation. Resolve those at plan level, then we can move to Rev 17 without carrying another hidden contradiction forward.
