# Watched Orchestrator — Stage 2 Doorbell Build Note (2026-11-16)

**Status: TESTABLE v1, verified end-to-end once on the live seat
surface.** Built under the owner's direct build-and-implement order
of 2026-11-15 23:51 MST, which lifted the 20:34 full stop for this
scope.

## What was built

`doorbell.py` — a small sensor that watches every open ChatGPT
conversation tab in the Remmy Chrome profile. Per conversation it
samples two markup-independent witnesses: a tail-zone camera stamp
(CDP screenshot cropped to the conversation tail, downscaled in
memory; frames are never written) and the rendered-text tail
(length + sha256 of the last 400 chars). When the tail changes and
then holds stable across two consecutive polls, it appends one
REPLY_SETTLED event to the seat pool file, continuing the file's
sequence and hash chain. Identity is a deterministic occurrence
tuple (conversation + emission ordinal + content sha256) minted as
a uuid5 — the live ChatGPT markup offers no message id (three
different turn structures were observed on three surfaces in one
night, two of them with no identity attributes at all).

The doorbell writes the capture heartbeat every loop (pid,
boot_id, instance_id, loop_count, last_tick — no state field) and
recorded waker transition seq 42, `capture_started`: capture is
now provided by the doorbell. It never sends anything to any seat.

## The verified test (2026-11-16 00:02–00:03 MST)

1. Trigger armed in the inbox: job `doorbell-test-1`, matching
   REPLY_SETTLED / chatgpt / the alphabet-test conversation,
   escalate after 3600 s.
2. Doorbell started; heartbeat fresh (pid 10783); baselines set
   per open conversation (no history fired).
3. Test prompt sent to the test conversation: "Reply with only
   the word: doorbell". Send verified (insert grew, structural
   click).
4. Alex replied "doorbell". The doorbell appended pool event
   seq 621, message_id 1d5cfc8e-07af-572d-8973-1a4ebe3d06d8.
5. The drain produced inbox item `inb-8` (kind seat_reply,
   identifiers only) and capture judged **ok** — the capture_down
   episode closed by a living sensor.
6. The wake check rendered: WAKE job=doorbell-test-1,
   key=inb-8, reason=seat_reply. The armed inbox-drain hook
   (60 s, main chat) delivers the same wake on its own cycle.
7. The orchestrator read the reply from the record, verified its
   content ("doorbell"), and marked inb-8 **acted**.

The chain the owner asked for — it lands, the system says so, the
orchestrator goes and gets it — has fired once, for real.

## Tuning

The knock layer over-fires by the owner's doctrine: a user-side
send whose tail stabilises can also knock. The wake means
"something landed"; the orchestrator reads and judges. False
knocks cost one read; a missed reply costs the evening.

## Known limits (not hidden)

- ChatGPT only. Claude and other seats are not watched yet.
- The doorbell runs as a background process from a scratch venv;
  it is not yet a supervised service and would not survive a VM
  replacement. Hardening is a later step.
- Settle = tail stable across two 4-second polls; the Stage 1
  camera probe showed landing detection is loud at stamp scale
  but stream/settle discrimination needs the tail-zone numbers
  (probe round 2: pause and scroll-control cases still to run).
- Settlement by citation, the canary, negative controls and the
  refresh summaries are Stage 4 — not in this build.
- The plan v1.1 amendments from Claude's Stage 0 review are not
  yet folded into the plan text.
