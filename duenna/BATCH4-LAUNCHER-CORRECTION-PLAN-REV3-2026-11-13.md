# BATCH 4 LAUNCHER — SOURCE CORRECTION PLAN, REVISION 3 (2026-11-13)

(Revision 2's text, plus the Finding 6 clarification appended at the end on Alex's request, pb-mwg18y5n.)

Revision 2 appends Alex's two clarifications
(pb-mwg16z8g) to Revision 1 (shelved at 190a5fc0,
preserved unchanged): the Finding 7 ancillary rule is
stated unambiguously throughout, and the Finding 6
matrix gains the fault-injected receive-error case.
Nothing else changes.

Answers Alex's source inspection of launcher.c at pin
ba4cb865… (shelved 0c68ae5b; verdict pb-mwg12rai:
NOT CLEARED, seven findings). The pinned source is
preserved unchanged as historical evidence; the
correction produces a NEW source pin, which returns to
Alex for inspection under the same C4-0b chronology.
No Batch 4 implementation is authorised by this plan.

Builder's note on finding 1: the draft's own smoke test
exercised only invalid identifiers (no-arg, "BAD ID") —
both correctly refused — and never a valid one, so the
offset bug passed the build check. The correction's
test matrix leads with the valid path.

## Finding 1 (HIGH) — run-ID parser offset

Location: run_id_valid(), launcher.c:274–289.
Change: rewrite the parser positionally from the end:
the counter is the final 3 chars preceded by '-'; the
date is the 8 chars before that, preceded by '-'; the
battery id is everything before, length 1–64, alphabet
[A-Za-z0-9-], no leading/trailing '-'. All index
arithmetic is guarded by total-length checks before any
pointer is formed (minimum length 14 = 1+1+8+1+3);
calendar validation gains the day-per-month table with
the leap-year rule for February (a date the grammar
admits must be a real date — "impossible calendar
dates" per the finding).
Tests (unit binary, -DUNIT_TESTS exposing the
validator): valid — a canonical id, minimum battery
length (1), maximum (64), leap date 20280229; invalid —
counter 000, counter 2 or 4 digits, month 00/13, day
00/32, Feb 29 on a non-leap year, Feb 30, missing
separators, separator inside the date, trailing or
leading '-', empty string, a 2-char string (no
out-of-bounds access; run under ASan for the suite).

## Finding 2 (HIGH) — child's first act

Location: fork branch, launcher.c:538–542, and
child_main().
Change: the forked child performs NO call before the
inherited-parent identity check. child_main() receives
the gate write end as a parameter; its first statement
is the getppid() comparison; only after it passes does
the child close the gate write end and the channel
descriptor, then proceed with the drop.
Test: a test peer (small Python driver) spawns the
test-build launcher and kills it in the fork window
under the D-T hold instrumentation; the child must
exit without any harness execution marker. Plus a
source-order assertion in the test suite: the first
statement of the child path is the identity check
(grep-level, named as such — the runtime case is the
evidence).

## Finding 3 (HIGH) — descriptor closure fail-closed

Location: child_main() step (g), launcher.c:446–450.
Change: every close_range() return is checked; on any
failure the child _exit()s. After the closes, the child
VERIFIES by enumerating /proc/self/fd: every remaining
descriptor must be in {0, 1, 2, gate read end} (the
enumeration's own descriptor excluded while in use);
anything else is closed individually and re-verified;
a close failure or a persistent unexpected descriptor
means _exit() before the gate.
Tests: (a) inherited-descriptor case — the peer opens
extra descriptors (incl. a writable file) before
spawning; the executed test harness lists its own
/proc/self/fd and must show exactly 0/1/2. (b) fault
case — the test build's hook forces close_range to
fail (PILOT_TEST_HOOKS fault point); the child must
exit without executing (no harness marker).

## Finding 4 (HIGH) — ENOTSUP is not an empty capability set

Location: file_caps_empty(), launcher.c:356–357.
Change: only ENODATA establishes absence. ENOTSUP and
every other error fail the check (return −1).
Test: unit test pointing the check at a filesystem
object on a mount without xattr support if one is
available in the room (probed at test time; if none
exists, the case is covered by a hook-injected error
in the test build and the limitation is stated), plus
the standing positive cases (no-xattr file passes; a
file WITH a nonzero capability xattr, set via setcap
in the test tree, fails).

## Finding 5 (HIGH) — ABORT packet validation before dispatch

Location: the Stage 6 receive loop, launcher.c:668–670
(and the same discipline applied at the ACK-wait read).
Change: an incoming ABORT is dispatched on only after
full validation — code, flags byte zero, reason in the
assigned table, and exact length for its form (3 bytes
reason-only; the class-T supervisor ABORT is exactly
the reason-only form; a word-carrying form is never
valid supervisor→launcher). A malformed ABORT takes
the protocol-violation path (cleanup, exit, no STATUS).
Tests: peer sends — a well-formed class-T ABORT
(dispatched; one STATUS follows), a class-T reason
with a trailing word (violation; no STATUS), flags
byte nonzero (violation), an unknown reason code
(violation), a truncated packet (violation).

## Finding 6 (MEDIUM) — receive outcomes kept distinct

Location: the Stage 6 loop, launcher.c:659–666.
Change: chan_recv()'s outcomes drive distinct paths:
EOF (−1) alone takes the gate-close-and-collect path;
malformed (−2) and ancillary violation (−4, finding 7)
take the protocol-violation path (cleanup, exit, no
collection); receive error (−3) takes a failure path
(cleanup, exit, distinct exit code). Exit codes are
named per path in the source so the supervisor-side
record can distinguish them by the launcher's own exit.
Tests: peer cases — orderly close (EOF path), a
truncated packet mid-session (violation path), and a
channel closed with unread garbage (violation path);
each asserts the launcher's exit code and that no
STATUS was sent on the violation paths. PLUS the
receive-error case (added Rev 2): the test build
fault-injects recvmsg() to fail with EIO at the Stage 6
wait (PILOT_TEST_HOOKS fault point); the case asserts
the error is NOT classified as EOF, the specified
cleanup is performed (child collected via the gate-EOF
route, no harness left running), the distinct
receive-error exit code is returned, and no STATUS is
sent.

## Finding 7 (MEDIUM) — ancillary data comprehensively rejected

Location: chan_recv().
Change: the rule is stated once and holds everywhere —
THE LAUNCHER ACCEPTS NO ANCILLARY DATA ON ANY RECEIVED
MESSAGE. Any control message, regardless of level or
type, is a protocol violation (new return −4). Every
descriptor the kernel delivered with that message is
closed unexamined, including descriptors received
alongside malformed, truncated (MSG_TRUNC) or
control-truncated (MSG_CTRUNC) packets and across
multiple control messages on one packet; no descriptor
the kernel delivered is ever leaked. Earlier wording
in Revision 1 that permitted a single one-descriptor
SCM_RIGHTS message is withdrawn — it contradicted this
rule and the tests, which always treated it as a
violation.
Tests: peer sends a normal packet WITH an attached
descriptor (violation; the descriptor observed closed
peer-side by its /proc accounting); two descriptors on
one packet (violation, both closed); a packet with a
non-SCM_RIGHTS control message if constructible from
the peer (else code-inspection evidence, so labelled);
and a descriptor attached to a TRUNCATED packet
(violation path; the descriptor is verified closed —
peer-side /proc accounting shows it gone — proving
cleanup on the error paths, not only the clean
violation path).

## Supporting change

HARNESS_PATH becomes #ifndef-guarded so test builds can
retarget the exec at the test harness (an fd-listing,
marker-writing helper) without editing the source; the
production build uses the compiled default. The test
peer, the test harness, and the unit suite are test
artefacts of the correction checkpoint, shelved with
it; they are not part of the shipped source pin beyond
being named in its disposition.

## Deliverable

Corrected launcher.c (new pin), the acceptance suite
above run in the room against the test build, its
transcript, and a correction report discharging this
plan item by item — to Alex for inspection. The
original pin ba4cb865… and Alex's findings stand as
history. Nothing installs; no Batch 4 implementation.

---

## Revision 3 — Finding 6 clarification (2026-11-13)

Appended on Alex's request (pb-mwg18y5n). Revision 2's
"no collection" phrasing for the violation paths is
withdrawn as imprecise; the exact semantics are:

**One cleanup contract governs every pre-actuation
receive failure (-2 malformed, -3 receive error,
-4 ancillary violation) and, for its child handling,
the Stage 6 EOF path as well:**

1. The launcher transmits NOTHING further on that path
   — no ABORT, no STATUS — with one exception stated at
   (4). A failed or violated channel is never used to
   report its own failure.
2. If a child exists and is unreaped: while the
   launcher is still privileged, it kills the child
   directly (SIGKILL) and reaps it; once dropped, it
   closes the gate write end unreleased — the child
   observes end-of-file and exits itself — and reaps
   it. Exactly one reap; the raw word is held locally
   and never transmitted on these paths.
3. The child can NEVER reach harness execution on any
   of these paths: the gate is released only by a
   validated RELEASE processed in the Stage 6 loop;
   a receive failure means no RELEASE was processed,
   and the cleanup closes the gate unreleased. The
   PDEATHSIG backstop covers the launcher's own death
   throughout.
4. The paths differ ONLY in their observable terminal
   outcome, so launcher and supervisor agree on the
   record: EOF at the Stage 6 wait (-1) is the orderly
   exception — gate closed unreleased, child reaped,
   and the one STATUS IS sent (the collection route),
   exit 0 — because an orderly channel close is not a
   failure of the peer. On -2 the launcher exits with
   the protocol-violation code (8); on -4 the same
   code (8) — both are peer violations; on -3 the
   receive-error code (9). On all three the channel
   then shows EOF with NO STATUS ever sent, and the
   supervisor closes the attempt on those facts.
5. Post-actuation there is no receive site: after
   GATE_ACTUATED the launcher only waits and reports
   (Stage 8), so no receive outcome can arise there.
   The ACK-wait and LAUNCH_REQUEST receives take the
   same contract (pre-fork failures have no child;
   post-fork failures clean up per (2)).

The EIO acceptance case is restated under this
contract: injected recvmsg() failure at the Stage 6
wait → not EOF-classified → gate closed unreleased →
child reaped via the gate-EOF route → no STATUS → exit
code 9.
