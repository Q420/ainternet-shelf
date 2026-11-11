# BRIDGE FIX — TRACEABILITY MATRIX 01

Companion to BRIDGE-FIX-SPEC-02.md. Each row: the
requirement, where it came from, where it lives in
the consolidated specification, and how it is
accepted. Sources: BEN-1/BEN-2 = Ben's bridge notes
rounds 1 and 2 (2026-11-11); REC = the standing
record (path audit, prior rulings, defect reports);
ALEX-1/ALEX-2 = Alex's reviews (pb-mwcf39wn-u-ioqt;
ALEX-BRIDGE-FIX-CLARIFICATIONS-REVIEW-01).

| Req | Source | Spec § | Acceptance |
|---|---|---|---|
| Centre-screen transfer animation, direction by travel | BEN-1 | §1 | Live walk, both directions; failure shows FAILED |
| Seat-popup parity, both seats identical | BEN-2 | §2 | Side-by-side panel comparison on both seats |
| Send/receive notifications at the true event | BEN-2 | §2 | Timed against TRANSIT→DELIVERED and verified delivery |
| Completed-receipts list removed from popup bottom | BEN-2 | §2 | Popup inspection |
| Force send for a stuck message, clears the queue item | BEN-1 | §3 | Stuck-item drill; journal checked first; act logged |
| Force-send override boundary enumerated | ALEX-1, ALEX-2 | §3 + §13.2 | Never-bypass list tested item by item |
| Pause/disconnect purges queue and cache | BEN-1 | §7 | Queue letter → pause → resume: nothing sends; purge set empty |
| Journal survival across pause — open decision, both branches | BEN-1 + ALEX-2 | §7 + §13.1 | Branch implemented as ruled |
| 20-message ID-only review journal against duplicates | BEN-1 | §5 | Replay a delivered ID: dropped, drop logged |
| Journal dispositions distinct; persistence; eviction at 21st | ALEX-1 | §5 | Restart drill; eviction log inspection |
| Journal sole duplicate authority; registry demoted; migration | ALEX-2 (F-10) | §5 | First-run import verified; registry makes no claim |
| Falsely-thinks-typing / vanished button blocks sends | BEN-1 | §4 | Regression fixtures (3) + Ben's live flow |
| UNKNOWN button = non-veto hold, supersedes generic quorum for that condition | ALEX-2 (F-5) | §4 + §13.3 | Verdict table test: button UNKNOWN + 2 positives = HOLD |
| Resend defect: history re-delivered; divergent truncation | REC (P-01/P-02) | §11 | Seat-tab reload: zero re-deliveries |
| Completeness contract: length, blocks, sha256 trailer | ALEX-1, ALEX-2 (F-6) | §6 + §13.4 | Truncated payload refused whole; later complete copy delivers |
| Incomplete copy does not poison its ID | ALEX-2 | §6 | Incomplete then complete, same ID: second delivers |
| Composer auto-paste defect | REC (Ben 2026-11-10) | §10 | Ben types unaided; box holds only his text |
| Outbound buffering: append into one, release after reply | REC (Ben's ruling 2026-11-11) | §8 | Two letters in one open pair arrive as one, in order |
| Aggregate keeps constituent PB-IDs; partial delivery; overflow; recovery | ALEX-1, ALEX-2 (F-8) | §8 | Per-constituent journal + ack inspection |
| F-3/F-8 lifecycle conflict resolved by event class | ALEX-1 | §7 | Pause drill vs crash drill give the two specified outcomes |
| In-flight purge: dispatched send cannot be erased | ALEX-2 | §7 | DISPATCHED-UNCONFIRMED → DELIVERED-LATE path; never resent |
| 45s defer visible; ceiling returns letter visibly | REC + BEN-1 sweep | §9 | DEFER-WAIT panel state; QUEUE-HEAD resumption |
| "Head of queue" mapped to the one-active-pair machine | ALEX-2 (F-9) | §9 | Pair-machine state trace |
| Restart recovery re-verifies pair state (R9 flake class) | REC (TEST-REPORT-v0.18.0) | §7, §9 | Restart drill: unverifiable state holds |
| Bounded windows stated honestly (journal 20; registry history) | REC | §12 | Panel/log wording inspection |
| Gemini sidebar hook — DEFERRED by Ben ("leave out Gemini for now") | BEN-1, withdrawn BEN-2 round | — | Not in this specification |

*End of matrix. The consolidated specification and
this matrix are the pair Alex re-reviews.*
