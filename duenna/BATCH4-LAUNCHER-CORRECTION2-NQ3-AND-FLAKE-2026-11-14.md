# BATCH 4 LAUNCHER — CORRECTION ROUND 2: NQ3 RESULT + NQ2 FLAKE (2026-11-14)

For Alex's disposition supplement (pb-mwg83z5l).

## NQ3 — DONE, STABLE

NQ3 added exactly as specified (Stage 6: empty A;
B = zero-length record carrying a descriptor;
shutdown; consume A; classify). Result across all
runs below: PASS every time — exit 8, no STATUS, no
actuation, no execution, and the queued descriptor
verifiably not leaked: the peer held a pipe whose
write end rode in B; after the launcher exited, the
pipe read EOF, i.e. the kernel destroyed the queued
descriptor when the channel socket was torn down.
The MSG_CTRUNC assumption the peek relies on is now
evidenced on its only load-bearing case (B carries
no data bytes, so the peek's length cannot decide).

The stale MSG_EOR header text is corrected (comment
only; the source's behaviour is unchanged by it).

Report claim, as requested, split by evidence kind:
CONSUMED-message descriptor evidence — Z1, Z2, P7,
P7b, P8: descriptors delivered to the launcher in a
received message, closed by the launcher's ancillary
walk (closed-count log). PEEK-path descriptor
evidence — NQ3: a descriptor in a QUEUED message,
never delivered; detected via MSG_CTRUNC on the
non-consuming peek; destroyed by the kernel on
socket teardown (pipe-EOF verification).

## NQ2 — A REAL TIMING RACE, CHARACTERISED

Repeated full peer runs after the NQ3 addition
(launcher otherwise unchanged):

run 1: 82/83 (NQ2 Stage 6 failed)
run 2: 83/83
run 3: 82/83 (a different single failure)
run 4: 83/83
run 5: 82/83 (NQ2 ACK wait)
run 6: 81/83 (NQ2 both sites)
run 7: 82/83 (NQ2 Stage 6)
run 8: 83/83

Every failure is an NQ2 case with the same signature
(exit 8, no packets): the launcher consumed record A
and sampled poll(timeout 0) BEFORE the peer's
shutdown(SHUT_WR) became visible as RDHUP, so the
no-RDHUP branch classified −2. When the shutdown
lands first, the same case takes the ruled EOF
outcome. The race is intrinsic to a zero-timeout
sample: the record and the shutdown are two events,
and classification can fall between them. It fails
in the SAFE direction (a violating peer gets the
violation outcome; nothing executes on either
outcome), but it makes NQ2's outcome timing-
dependent, which is not a demonstration.

## Proposed amendment (for Alex's ruling)

zero_classify's poll becomes a BOUNDED RDHUP WATCH:
poll in short slices up to a named deadline
(250 ms) until RDHUP/HUP (or ERR/NVAL) appears;
classify from the state at watch end via the
existing branches (peek if RDHUP; −2 if the deadline
expired without it; −3 on poll failure). "Immediately
preceding the shutdown" thereby gains an operational
meaning: within the watch window. Z3/Z4 semantics
are unchanged — their channels never shut down; they
simply wait out the window before classifying −2.
The happy path never enters zero_classify and pays
nothing. NQ2 is then expected to be deterministic
across repeats, which the closing bundle will show
by running the suite repeatedly, not once.

No source change has been made for this amendment;
the timeout-0 form stands in the current source
(new pin from the header correction only:
see bundle addendum) pending Alex's ruling.
