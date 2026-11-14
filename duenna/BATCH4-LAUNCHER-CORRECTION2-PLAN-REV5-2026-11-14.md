# BATCH 4 LAUNCHER — CORRECTION ROUND 2, PLAN REVISION 5 (2026-11-14)

The bounded RDHUP watch, drafted against Alex's
ruling pb-mwg89t9e. Revisions 1–4 and the Treatment
A classification stand unchanged except as below.
No source changes until this revision is approved.

## 1. The watch mechanism (zero_classify only)

On entry, zero_classify computes an ABSOLUTE
deadline: clock_gettime(CLOCK_MONOTONIC) + 250 ms,
stored once. It then loops:

- remaining = deadline − now (monotonic). If
  remaining ≤ 0, the watch has expired.
- poll(channel, POLLIN | POLLRDHUP,
  min(remaining, 10 ms slice)).
- poll returns −1 with EINTR: recompute remaining
  from the SAME deadline and continue. An
  interruption never extends the deadline.
- poll returns −1 otherwise: −3 (receive-error
  class; existing cleanup, no STATUS), immediately.
- revents carries POLLERR or POLLNVAL without
  POLLRDHUP/POLLHUP: −3, immediately (as today).
- revents carries POLLRDHUP or POLLHUP: leave the
  loop and run the EXISTING peek classification
  (peek length > 0 or MSG_CTRUNC → −2; peek zero
  clean → −1; peek failure → −3).
- Deadline expires with no RDHUP/HUP observed:
  −2 (the record was consumed on a channel whose
  peer did not shut down within the window —
  the existing no-RDHUP outcome, Z3/Z4 semantics
  preserved).

Only zero_classify changes. Every other receive
path, the classification table, Fix B, and the
cleanup contract are untouched. The happy path
never enters zero_classify.

The 250 ms window DEFINES "immediately preceding
shutdown" for this implementation (Alex's
distinction): a shutdown arriving after the
deadline correctly takes the violation outcome;
the window is not a claim that every scheduling
delay is absorbed.

## 2. Timing tests (peer suite; deterministic)

The peer synchronises on protocol state, not on
sleeps alone: at Stage 6 the peer acts only after
GATE_READY (the launcher is in the Stage 6 wait);
at the ACK wait it acts only after the pidfd
handoff. Delays are then measured against the
250 ms deadline with wide margins.

- W1 (Stage 6, inside window): send empty A; wait
  100 ms; shutdown. Expect the EOF outcome
  (STATUS with the child's word, exit 0).
- W2 (ACK wait, inside window): send empty A;
  wait 100 ms; shutdown. Expect exit 6, no STATUS.
- W3 (Stage 6, past deadline): send empty A; wait
  400 ms; shutdown. Expect exit 8, no STATUS —
  the shutdown arrived after the accepted window
  and correctly takes the violation outcome.
- W4 (ACK wait, past deadline): same shape.
  Expect exit 8, no STATUS.
- NQ2 retained as filed (immediate shutdown, both
  sites). Z3/Z4 retained (no shutdown ever; they
  now wait out the window before classifying −2).

## 3. Stability evidence

The closing bundle's peer transcript runs the FULL
suite five consecutive times and prints every run's
own total plus its NQ2/W lines individually — no
aggregate-only reporting. The expected result is
five identical full passes.

## 4. Pins carried into the next source bundle

Per Alex's note on the NQ3 filing: the bundle will
carry the header-corrected source (launcher.c
sha256 6e5fca561d99bb4118ee59c14148b4b4588a5a858b0f
15ce7d5b2d0b105d1aae — pin e7bc6e65… plus the
comment-only header correction) AND its diff
against pin e7bc6e65…, so the comment-only claim
is directly verifiable, alongside the watch
implementation's new pin and diff.
