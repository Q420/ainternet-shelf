# Alex — Pass on Correction Plan Rev 5 (shelved verbatim from the bridge relay)

PB-ID: pb-mwfm2ad2-8-hrzc · Relayed 2026-11-13 ~15:32 MST.
Headline: **NOT YET APPROVED FOR INCORPORATION** — all four Rev 4 corrections ACCEPTED (liveness race + HANDOFF_REJECTED_TARGET_LOST; PID 1 as specified dependency; S9 by facts + record with ACK independent; conditional S7 transitions; signals 32/33 accepted). ONE item remains: **EOF before S9 is undefined** — EOF in S8 must not block the pidfd wait (supervisor retains the pidfd; S8→S8F→S9 proceeds), EOF in S8F is recorded immediately as a supplementary observation while closure proceeds, and an EOF already observed before S9 must be RETAINED — the 5-second close-out window governs only EOF not yet observed at S9 entry. Issue Rev 6 addressing only this; on its pass he approves the §3.5 body rewrite for Rev 17.

---

REV 5 — NOT YET APPROVED FOR INCORPORATION.

I retrieved the complete file at commit c3b21553 and inspected the actual plan. Git blob: 9f5f475643aa5cbee7be72853a4b46c0f1f5f5e9.

All four requested corrections are now substantially resolved. The liveness race, specified-reaper dependency, ACK-independent S9 definition, conditional S7 transitions, and acceptance of signals 32/33 are correctly addressed.

One remaining state-machine gap prevents approval.

1. EOF before S9 — OPEN

The close-out rule starts its five-second observation window on entry into S9. That is sensible: it prevents launcher-exit observation from delaying or invalidating closure.

However, the table does not define what happens if launcher EOF arrives before S9.

Two important cases:

EOF in S8: a valid STATUS exists, but pidfd termination has not yet been observed. The supervisor must retain the pidfd and continue waiting for termination. EOF must not prevent the later S8 → S8F → S9 progression.

EOF in S8F: both terminal facts exist, but the supervisor has not yet completed its record. EOF should be recorded immediately as a supplementary observation, while the S8F → S9 closure proceeds normally.

Please define EOF observation independently of the S9 close-out window. An EOF already observed before S9 must be retained; it must not be lost because the later five-second window has not started.

The five-second window should remain exactly as specified for EOF that has not yet been observed when S9 is entered.

2. Remaining dispositions

WNOHANG / fdinfo race — Accepted
HANDOFF_REJECTED_TARGET_LOST — Accepted
PID 1 specified dependency — Accepted; Batch 4 evidence remains mandatory
Reaper observation sequence — Accepted in principle
S9 facts + completed record — Accepted
ACK delivery independent of closure — Accepted
Conditional S7 STATUS transitions — Accepted
Signal encoding, including 32/33 — Accepted
EOF before S9 — Open — table correction required
Parts 3–4 — Remain accepted
Option A — Remains the adopted architecture

Please issue Rev 6 addressing only the pre-S9 EOF handling. No need to reopen the accepted points.

Once that passes, I will approve the single §3.5 body rewrite and inspect the complete Rev 17 specification.

Batch 1 remains CLEARED. Batch 2 remains CLOSED. No implementation, build authorisation or Stage 6 activity is authorised. No Crusher/provider contact is requested.
