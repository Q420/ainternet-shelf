# BATCH 4 LAUNCHER — CORRECTION ROUND 2, PLAN REVISION 6 (2026-11-14)

Narrow correction of the Rev 5 watch, against
Alex's review pb-mwg8si2j. Both findings verified
against the source before drafting: the
RDHUP/HUP break path performs no deadline
re-check, and the remaining-time expression
truncates to whole milliseconds. No source
changes until this revision is approved.

## 1. Deadline enforcement on observation

After the watch loop breaks on RDHUP/HUP,
zero_classify recomputes the remaining time
against the SAME absolute deadline before the
peek classification: if the deadline has passed,
the observation is late and the classification
is −2 (the shutdown was not observed within the
accepted window). The peek runs only when the
observation is inside the window. POLLERR/
POLLNVAL handling is unchanged (−3 is a failure
classification, not an acceptance, and is not
gated on the deadline).

Deterministic test — scheduler-delay simulation:
a test-builds-only hook, PILOT_HOOK_ZERO_DELAY_MS,
sleeps inside zero_classify immediately after the
watch loop wakes with RDHUP/HUP and before the
deadline re-check, simulating a descheduled
launcher. Cases at the Stage 6 site:
- L1: peer sends empty A and shuts down
  immediately; hook delay 300 ms. Expect exit 8,
  no STATUS, no actuation — the observation is
  processed after expiry and must be rejected
  even though the shutdown itself was timely.
- L2 (control): same, hook delay 50 ms. Expect
  the EOF outcome (STATUS, exit 0) — the
  observation lands inside the window.

## 2. Sub-millisecond remaining time

The remaining-time computation moves to
nanoseconds: a helper deadline_remaining_ns(dl,
now) returning the signed difference. Expiry is
decided on the nanosecond value (≤ 0 expired;
any positive remainder, however small, is live).
The poll slice is ceil(remaining_ns / 1e6)
milliseconds, capped at 10 ms, so a sub-ms
remainder still parks in poll until the deadline
rather than spinning or expiring early; after
every wake the loop re-derives the remainder
from the absolute deadline.

Unit evidence: the helper is exercised directly
in the unit suite — remainder +400 µs → live;
remainder 0 → expired; remainder −1 ns →
expired; remainder +250 ms − 1 ns → live. (The
helper is compiled into the unit build from the
same source; zero_classify calls it, no parallel
implementation.)

## 3. Documentation

The comment block above zero_classify() is
rewritten to describe the implemented algorithm
(ancillary walk, bounded watch with absolute
deadline and post-wake re-check, peek) — the
zero-timeout description is removed.

## 4. Regression + stability

NQ1, NQ2, NQ3, Z1–Z5, A1–A5, W1–W4 and all
earlier cases retained; L1/L2 added. The closing
bundle again runs the full peer suite five
consecutive times with individual results.
Expected per-run total: 89 checks.

Scope: zero_classify() and its comment, the unit
suite's new helper cases, the peer suite's L1/L2
(and the test-build hook). Pin e31db79d… and all
historical bundles preserved; the new pin and
its diff ride in the closing bundle.
