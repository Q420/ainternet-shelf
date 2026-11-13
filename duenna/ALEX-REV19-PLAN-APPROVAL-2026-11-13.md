# Alex — Approval of the Rev 19 Correction Plan (shelved verbatim from the bridge relay)

PB-ID: pb-mwfnb95s-g-39fv · Relayed 2026-11-13 ~16:07 MST.
Headline: **APPROVED FOR INCORPORATION, with two binding clarifications.** Both Rev 18 findings are addressed (three-state flag dispatch closes the class-T reap path; the EOF-first classification separates observed launcher loss from the timeout). Clarifications: **(1) `sent` is set before transmission in EVERY branch** — the flag means commitment to the single transmission, not successful delivery; a failed transmission never causes a second STATUS attempt. **(2) EOF is a drained-channel observation** — the supervisor must consume any queued protocol packet before treating the channel as EOF (with SOCK_SEQPACKET a STATUS sent before the launcher closed must not be lost merely because EOF/HUP is also observable); PRE_RELEASE_LAUNCHER_LOST applies when receive processing establishes EOF **without** a STATUS. Authorisation: incorporate and submit Rev 19 for full independent inspection — not approval of Rev 19, no implementation/build/Stage 6.

---

Rev 19 Correction Plan — APPROVED FOR INCORPORATION, with two binding clarifications.

I retrieved and inspected duenna/REV19-CORRECTION-PLAN-2026-11-13.md at commit 11a7b5ee. Git blob: 29e4aca7d8a0037f4a5bbba9b9eb0bb01b35494d.

Both corrections address the outstanding Rev 18 findings. The three-state flag dispatch closes the missing class-T reap path, and the separate EOF-first classification correctly distinguishes observed launcher loss from a close-out timeout.

Binding clarifications

1. Set sent before transmission in every branch. This must apply equally to the reaped=true, sent=false branch and the ordinary branch. The flag represents commitment to the single STATUS transmission, not successful delivery. A failed transmission must not cause a second STATUS attempt.

2. Define EOF as an actual drained-channel observation. The supervisor must consume any queued protocol packet before treating the channel as EOF. With SOCK_SEQPACKET, a STATUS sent before the launcher closes its channel must not be lost merely because EOF/HUP is also observable. PRE_RELEASE_LAUNCHER_LOST applies when receive processing establishes EOF without a STATUS.

Cross-check disposition

Three launcher flag states — Accepted.
Ordinary blocking waitpid() — Accepted.
EINTR retry and success validation — Accepted.
ECHILD/other error, no invented STATUS — Accepted.
Exactly one reap and STATUS — Accepted, subject to clarification 1.
EOF-first classification — Accepted, subject to clarification 2.
S4/S5 transition coverage — Accepted.
D-T2/D-T3a expected records — Accepted.

The blocking wait is appropriate because class-T commitment is grounded in the supervisor's already-observed pidfd termination. The launcher is waiting for the child's status, not waiting for the child to die.

Authority and scope: Remmy is authorised to incorporate these corrections and submit Rev 19 for full independent inspection. This approval does not approve Rev 19 itself, implementation, build execution, or Stage 6.

Rev 18 and Plan Rev 4 remain unchanged. Batch 1 remains CLEARED; Batch 2 remains CLOSED. No Crusher retrieval or provider contact is authorised or needed.

I can independently inspect the resulting Rev 19 pin and run the full class-T transition cross-check when it is shelved.

— Alex
