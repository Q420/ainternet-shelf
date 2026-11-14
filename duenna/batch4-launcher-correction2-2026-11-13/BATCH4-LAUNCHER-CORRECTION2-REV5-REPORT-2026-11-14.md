# BATCH 4 LAUNCHER — CORRECTION ROUND 2, REVISION 5 REPORT (2026-11-14)

The bounded RDHUP watch, implemented under plan
Revision 5 (approved by Alex, pb-mwg8cva7).

## What changed

zero_classify() only. The single poll(timeout 0)
is replaced by a bounded watch: one absolute
CLOCK_MONOTONIC deadline 250 ms from entry; poll
slices of at most 10 ms, each bounded by the
remaining time recomputed from that deadline
(EINTR continues the loop against the SAME
deadline — interruptions never extend it); POLLIN
alone never ends the watch; POLLERR/POLLNVAL
without RDHUP/HUP → −3 immediately; non-EINTR
poll failure → −3; RDHUP/HUP → the existing peek
classification; deadline expiry → −2. Fix B, the
ancillary walk, the cleanup contract and the
happy path are untouched.

## Pins and diffs (all in this bundle)

- e7bc6e65… — the Rev 4 source (bundle of
  43788d33, preserved).
- 6e5fca561d99bb4118ee59c14148b4b4588a5a858b0f15
  ce7d5b2d0b105d1aae — header-corrected only.
  header-diff.txt is its diff against e7bc6e65…:
  comment text only, verifiable line by line. (The
  intermediate file was reconstructed for this
  bundle and its sha256 re-verified against the
  pin recorded in plan Rev 5 before the diff was
  taken.)
- e31db79d09bb3270fa0617bf4c8c8d5c04d9e2ccedddb
  70f75e79aa67579c3a4 — the watch source (current
  pin). watch-diff.txt is its diff against the
  header-corrected pin: the zero_classify watch
  and nothing else.
- test_launcher.py sha256 d73cd5a6… (W1–W4 added).

## Results

Unit: 33/33 PASS (build-transcript.log).
Peer: 87/87 PASS in each of five consecutive full
runs (peer-five-runs.log, every run's lines shown
individually), and five further identical 87/87
runs immediately before those. NQ2 — the case
that raced under the zero-timeout sample — now
passes deterministically at both sites in all ten
runs. W1/W2 (shutdown at 100 ms, inside the
window) take the EOF outcomes; W3/W4 (shutdown at
400 ms, past the deadline) correctly take the
violation outcome, exit 8 — the window defines
"immediately preceding", it does not absorb every
delay. Z3/Z4 unchanged in outcome (they wait out
the window). NQ3 regression included in every run.

## Declared build iterations

The W2/W4 cases initially failed "setup" in five
runs: the new test code called a request helper
that does not exist under that name in this suite
(the Peer's methods are request() / handoff()),
and one repeat batch ran against a stale room
copy of the suite before the staging copy step.
Both were suite-side; the launcher source was
never touched for them, and the failing signature
was traced through the launcher's request-stage
exit code before the fix. The final form uses the
Peer's own request()/handoff() pair.
