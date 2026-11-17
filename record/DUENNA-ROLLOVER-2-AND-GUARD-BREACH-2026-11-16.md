# DUENNA CONVERSATION ROLLOVER 2 + GUARD BREACH NOTE (2026-11-16)

The Duenna conversation 6afb8904 reached its context limit
(CONTEXT_FULL at doorbell event seq 702) during the Spec 01
Rev 02 exchange. Rollover executed 2026-11-16 ~17:47 MST:

- Pre-send guard consumed for 6afb8904 @ seq 702.
- New conversation created from the banner's New chat control:
  https://chatgpt.com/c/6afba3d2-972c-83e8-8a8b-f50cb62d6eca —
  the Duenna loop's current home.
- Triggers re-armed there (duenna-stage6-reply REPLY_SETTLED,
  duenna-stage6 CONTEXT_FULL); the 6afb8904 arms retired.
  Guard CLEAR on the new conversation.
- First letter sent: rollover reconciliation from the shelf
  record, carrying the Rev 02 ruling request (Spec 01 Rev 02
  @ 334fe557). Awaiting Alex's ruling; on approval the smoke
  fires exactly once under Spec 01.

## Breach note — unauthorized tool execution (recorded plainly)

The Rev 02 letter was ALSO sent into 6afb8904 after the
pre-send guard had returned BLOCKED (exit 3). Cause: Remmy's
shell command chained the send through an `echo` — the `&&`
bound to the echo's exit status, not the guard's — so the
BLOCKED verdict did not stop the send. The letter landed in
the context-full conversation; no reply was recorded there
(verified first-hand after rollover), and the same ask was
re-issued in the new conversation as its first letter, with
the duplication stated on its face. Corrective rule, adopted:
the guard check and any send it gates run in SEPARATE commands,
never chained through an intermediary. The guard itself worked
exactly as designed; the failure was in the operator's command
construction.
