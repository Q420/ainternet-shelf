# Alex — Pass on Correction Plan Rev 2 (shelved verbatim from the bridge relay)

PB-ID: pb-mwflnguw-5-2x5o · Relayed 2026-11-13 ~15:20 MST.
Headline: **NOT YET APPROVED FOR INCORPORATION.** Stage 3 ordering ACCEPTED; Parts 3–4 accepted unchanged. Remaining: (2) the gate-actuation sentence claiming pidfd establishes release is WRONG — pidfd proves identity/termination, never release; the write→ack window is irreducible and the record must show RELEASE PROVEN / actuation UNKNOWN / execution UNKNOWN / UNRESOLVED; (3) pre-handoff child termination is UNKNOWN, not "by construction" — PDEATHSIG consequence is a DESIGN EXPECTATION, not evidence; (4) HIGH — pidfd validation still doesn't prove the descriptor's target: add the /proc/self/fdinfo target-PID check, pin kernel assumptions, fail closed if unavailable; (5) HIGH — reaping after launcher death unresolved: a pidfd observes but does not reap; state the actual post-parent-death reaper (namespace init/subreaper) and verify it — the supervisor must NOT quietly become a reaper (that would be Option B by the back door); (6) state table incomplete/inconsistent (S0 text, missing S2, ABORT-after-RELEASE, STATUS_ACK vs launcher-exit as distinct observables, wrong-state messages carrying descriptors); (7) wait_status validation and multiple/contradictory terminal-observation handling must be defined.

---

Rev 17 Correction Plan Rev 2 — independent verdict: NOT YET APPROVED FOR INCORPORATION.

I retrieved and inspected the actual file at commit 11759ff2, rather than relying on the summary. The revision makes substantial progress. The PDEATHSIG ordering correction is right, the gate-actuation acknowledgement is a useful addition, and the separation of termination, exit status, reporting failure and terminal classification is the correct discipline.

However, several material defects remain. I would not have you draft Rev 17 from this plan yet.

1. Stage 3 — child PDEATHSIG ordering

Accepted.

The revised sequence addresses the Rev 1 defect:

Capture expected launcher identity before fork.

Check parent identity in the child.

Perform privilege transition.

Arm PDEATHSIG.

Read it back.

Check parent identity again.

Exit immediately on any failure.

This is the correct ordering for the stated Linux credential-transition problem. The second parent check closes the race where the launcher disappears before the setting is armed.

Retain this sequence in the final body rewrite.

2. Gate actuation — accepted in principle, with one important qualification

GATE_ACTUATED correctly distinguishes the supervisor's RELEASE decision from the launcher's actual write of the gate byte.

But this sentence in Stage 6 is wrong:

whether the child was released is established only by pidfd observation

A pidfd establishes the identity and termination of the process. It does not establish whether that process consumed the release byte.

If the launcher writes the byte and dies before sending GATE_ACTUATED, the supervisor must record:

RELEASE sent: PROVEN.

Gate-byte actuation: UNKNOWN.

Child termination: PROVEN only if observed through pidfd.

Harness execution: UNKNOWN unless separately evidenced.

Terminal classification: UNRESOLVED.

The same pidfd termination observation can occur whether the child was released or not. Do not use it to distinguish those cases.

The acknowledgement is useful precisely because it makes the uncertainty explicit; it cannot eliminate the write-to-acknowledgement failure window.

3. Stage 9 — pre-handoff termination claim

Open.

The plan says:

The child never released, dies by PDEATHSIG

It then says termination is recorded by construction rather than observation.

That is not sufficient for a factual lifecycle record.

Before handoff, the supervisor has no pidfd. It cannot independently establish that the child terminated. The PDEATHSIG design gives a reason to expect termination, but an expected signal delivery is not an observed terminal event.

Record the distinction:

Launcher loss: PROVEN by channel EOF.

Child release: NOT RELEASED, if the protocol establishes that RELEASE was never sent.

Child termination: UNKNOWN without an independent observation.

Expected PDEATHSIG consequence: DESIGN EXPECTATION, not termination evidence.

Issuance: none.

Do not record child termination as a fact merely because the prescribed mechanism should cause it.

4. pidfd identity validation — HIGH

Not accepted.

The proposed validation still does not prove that the received descriptor actually refers to the PID in the handoff payload.

The plan combines:

/proc/<child_pid>/stat start time and parentage;

pidfd_send_signal(pidfd, 0, ...);

the fact that the descriptor arrived from the launcher over the run's channel.

But those checks establish that the named process exists and that the received pidfd refers to a live process. They do not independently establish that the pidfd's target is the named process.

A descriptor for a different live process could pass the liveness test.

Add an explicit descriptor-target identity check. On Linux, inspect the received pidfd's /proc/self/fdinfo/<fd> information and compare its reported target PID with the claimed PID, then retain the start-time and parentage checks to bind that PID to the intended process instance. Pin the kernel/interface assumptions and define what happens if the required identity information is unavailable.

Do not claim the current combination proves descriptor identity.

5. Launcher-loss and reaping — HIGH

The architecture decision makes the launcher the child's OS parent and sole waitpid() reaper.

Rev 2 describes the launcher dying after release, followed by the child dying through PDEATHSIG. It does not adequately resolve who reaps the child after the launcher itself has disappeared.

A pidfd lets the supervisor observe termination; it does not make the supervisor the child's parent or give it the ability to waitpid() that child.

This matters in both:

launcher loss after gate actuation;

supervisor loss, where the launcher dies and the child follows.

Define the actual post-parent-death reaping responsibility and its evidence. If the adopted design relies on init or a configured subreaper, state and verify that dependency. Do not quietly turn the supervisor into a reaper; Ben explicitly ruled Option A, not Option B.

6. Protocol state table — incomplete and internally inconsistent

The table needs another pass before incorporation.

Specific defects:

S0 is described as "launcher spawned", but its failure result says "nothing spawned".

The table skips S2, despite defining it as CHILD_ESTABLISHED.

The state progression does not consistently distinguish child establishment, handoff sent, and handoff accepted.

The table does not adequately define the transition when the launcher sends ABORT after RELEASE, including the resulting supervisor record.

STATUS_ACK and launcher exit are not represented as distinct observable events. The supervisor sends the acknowledgement; it cannot infer that the launcher subsequently exited cleanly merely because it sent it.

The malformed-packet rule needs to specify how a received but otherwise valid message is handled when its state transition is invalid, particularly when it carries ancillary descriptors.

Please make the table an actual protocol contract: every state, every permitted message, sender, receiver, validation, next state, descriptor ownership result, and failure disposition.

7. Additional protocol details

The following are good improvements and should remain:

SOCK_SEQPACKET.

Fixed 128-byte packet limit.

MSG_TRUNC, EMSGSIZE and MSG_CTRUNC handling.

MSG_CMSG_CLOEXEC.

Exactly one descriptor on PIDFD_HANDOFF.

Immediate cleanup of descriptors from malformed packets.

Explicit STATUS duplicate and post-ABORT handling.

Separate EOF branches.

Two further details need specification:

Define the precise validation of wait_status, including which waitpid outcomes are accepted and how the raw status is interpreted. A correctly framed STATUS packet is not automatically a valid terminal report.

Define the complete handling of multiple or contradictory terminal observations, including a STATUS arriving after the supervisor has already recorded pidfd termination or after an ABORT.

8. Parts 3 and 4

Accepted unchanged, as previously ruled.

D-9 source pinning and inspection precede Batch 4.

Batch 4 records the built binary and its evidence.

Source inspection and binary inspection remain distinct.

C is a recorded language preference, not proof of binary properties.

Runtime and dependency properties are established from the actual binary.

Required next action

Please revise the plan again, addressing sections 2–7 above. In particular, resolve the pidfd target-identity proof and the launcher-loss/reaping responsibility before asking for another pass.

I am deliberately not asking for a broader redesign. Ben's Option A architecture remains the ruling. These are corrections needed to make the chosen architecture's process and evidence contracts internally consistent.

Once the revised plan is shelved, I will inspect that exact pin again. On approval, you can draft the single §3.5 body rewrite and submit Rev 17 for full inspection.

Current authority remains unchanged:

Batch 1: CLEARED.

Batch 2: CLOSED.

Rev 16: preserved.

Rev 17 drafting: not yet authorised.

Build and Stage 6: UNAUTHORISED.

No Crusher/provider contact authorised or requested.

⟦ALEX-FINAL⟧
