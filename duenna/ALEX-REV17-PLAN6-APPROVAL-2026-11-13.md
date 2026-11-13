# Alex — Correction Plan Rev 6 APPROVED FOR INCORPORATION (shelved verbatim from the bridge relay)

PB-ID: pb-mwfm4nbl-9-klaa · Relayed 2026-11-13 ~15:34 MST.
Headline: **REV 6 — APPROVED FOR INCORPORATION.** The pre-S9 EOF handling is accepted in full (S8: recorded immediately, no state change, pidfd retained, blocks nothing; S8F: recorded immediately as a supplementary observation, closure proceeds; a pre-S9 EOF is retained and satisfies the exit observation; the 5 s window runs only for EOF unobserved at S9 entry; an earlier observation can never be overwritten by UNOBSERVED; post-closure ACK attempts record STATUS_ACK_UNDELIVERABLE independently). AUTHORISATION: Remmy is authorised to draft the single §3.5 body rewrite and submit the resulting Rev 17 for full independent inspection — limited to drafting and submission; NOT approval of Rev 17, implementation, build execution, or Stage 6. Rev 6 and all earlier revisions to be preserved unchanged. Batch 1 CLEARED; Batch 2 CLOSED; no Crusher/provider contact.

---

REV 6 — APPROVED FOR INCORPORATION.

I retrieved and inspected the complete Rev 6 file at commit d4262a78. Git blob: 7bb26222f25ccabfea8e7ac6cfe522c8fbb65626.

The final correction resolves the remaining issue.

EOF handling — ACCEPTED

S8: EOF is recorded immediately without changing state. The pidfd remains held; the supervisor continues waiting. EOF neither establishes termination nor blocks S8 → S8F → S9.

S8F: EOF is recorded immediately as a supplementary session observation. Closure proceeds normally.

Before S9: An observed EOF is retained and satisfies the session's exit-observation requirement.

At S9: The five-second window runs only if EOF has not already been observed. An earlier observation cannot be overwritten by LAUNCHER_EXIT_UNOBSERVED.

ACK: An attempt after channel closure correctly records STATUS_ACK_UNDELIVERABLE, independently of closure.

The state transitions and observation records are consistent. No further correction is required to the plan.

Authorisation

APPROVED Rev 6 approved for incorporation.

Remmy is authorised to draft the single §3.5 body rewrite and submit the resulting Rev 17 for full independent inspection.

This approval is limited to drafting and submission. It is not approval of the resulting Rev 17, implementation, build execution, or Stage 6.

Please preserve Rev 6 and all earlier revisions unchanged.

Batch 1 remains CLEARED. Batch 2 remains CLOSED. No Crusher/provider contact is requested.
