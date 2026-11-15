# Review — Stage 3 stale-window fix (03102608) and waker stop-request should-fix

## Stage 3 stale-window fix — ACCEPTED (logic)
Stale now means an outstanding send: the last SEND_OBSERVED with no
REPLY_CAPTURED after it, older than the interval. An idle window with no
outstanding send is never stale. This matches the ruling. Fixtures cover
idle-judges, outstanding-holds (zero judge calls, streak untouched, alert
logged), and send-then-reply-not-stale. Full Stage 3 acceptance still waits
on the gate rebuild onto the registry's pinned gate_terms (the detector's
interim gate pinning is still in place; line ~410).

## Waker stop-request should-fix — ACCEPTED
clear_stale_stop_request() runs at supervisor start (line ~267), before the
launch transition. The stop command writes its request only when a live
supervisor is about to be signalled (line ~221). Fixtures pass (waker,
0 failures; the cleared-with-no-request case is covered).

## Open
- Stage 3 full acceptance: gate rebuild onto gate_terms.
- Stage 4 (scheduler) after Stage 3 is fully accepted.
