# BATCH 4 LAUNCHER — SOURCE CORRECTION REPORT (2026-11-13)

Built under correction plan Revision 3, APPROVED by Alex
(pb-mwg1b52y, shelved at 223478df). Original source pin
ba4cb865… preserved unchanged as history. Nothing is
installed; no privileged execution is claimed — the
acceptance evidence below is from the TEST build
(PILOT_TEST_HOOKS, harness retargeted at the test
programme), run uninstalled in the room.

## Corrected source pin

launcher.c (corrected form), 827 lines,
sha256 6430b9f4403210f4f960111b5a63be6431f973e2361e765e5ac029a19c3585c4.
Production compile check: gcc -std=c11 -O2 -Wall -Wextra
-Werror, clean (build transcript).

## Discharge, finding by finding

F1 (run-ID parser): rewritten positionally from the end
of the string; length guards before any pointer
arithmetic; real calendar validation incl. leap years.
Unit suite (ASan/UBSan), valid path FIRST: canonical id,
battery lengths 1 and 64, leap date — then 22 invalid
cases (000 counter, wrong counter widths, month 00/13,
day 00/32, Feb 29 non-leap, Feb 30, Apr 31, separator
defects, leading/trailing battery dashes, bad alphabet,
empty and 2–3 char inputs with no out-of-bounds reads).

F2 (child ordering): child_main receives the gate write
end as a parameter; its first statement is the
getppid() comparison against the pre-fork captured
value; the gate-write and channel closes happen only
after it passes. Peer P2: the launcher is killed in the
fork/handoff window 20 times — the harness never
executes and no harness process is left behind.

F3 (descriptor closure): close_range results checked;
the result verified by /proc/self/fd enumeration (only
0/1/2 + gate read may remain, two passes). P1/P3a: the
exec'd harness lists exactly fds 0 1 2, including when
the launcher itself inherited extra descriptors. P3b:
with closure forced to fail, the child exits 73 during
establishment; the supervisor peer observes it on the
pidfd and answers ACK 3; the launcher reaps and reports
ABORT/CHILD_TERMINATED_AT_HANDOFF carrying the word —
no execution.

F4 (capability inspection): only ENODATA establishes
absence; ENOTSUP/EIO/missing file all fail closed
(unit-tested, ENOTSUP/EIO via the test-hooks error
injection the plan allowed). DECLARED EXTRA, found by
the plan's own acceptance test: the draft's capability
struct did not match the kernel's vfs_cap_data layout
(no per-entry effective field exists on disk; the
effective vector lives in magic_etc, and the second
uid's inheritable word went unchecked). The function
now parses the xattr as words and inspects every
capability word; unit cases cover a crafted nonzero
permitted set, an all-zero rev2 set (empty), and an
effective-only set (fails). This is inside finding 4's
function and is declared here for Alex's ruling rather
than hidden.

F5 (ABORT validation): abort_packet_valid() — exactly
the 3-byte reason-only form, zero flags, reason in the
assigned table — runs before any dispatch. Peer: the
well-formed class-T ABORT (peer kills the child via
pidfd_send_signal, sends reason 2) produces exactly one
STATUS whose word decodes signalled/SIGKILL; the three
malformed variants (word-carrying, nonzero flags,
unknown reason) each exit 8 with no STATUS and no
execution.

F6 (receive outcomes + Rev 3 cleanup contract):
chan_recv returns −1/−2/−3/−4 distinctly; the ACK wait
and Stage 6 loop dispatch per outcome. Peer: orderly
EOF (peer half-close) → gate closed unreleased, child
reaped (word = gate-refused exit 71), the one STATUS
sent, exit 0; truncated packet → exit 8, no STATUS;
fault-injected recvmsg error at the Stage 6 wait
(PILOT_HOOK_FAIL_RECVMSG_AT) → exit 9, no STATUS, child
collected via the gate-EOF route (pidfd readable, no
execution). Named exit codes per path throughout.

F7 (ancillary data): chan_recv accepts NO control data
of any level or type; every delivered descriptor is
closed unexamined on every path (including truncated
packets and MSG_CTRUNC), with test-hooks accounting of
closed descriptors. Peer: RELEASE with an attached fd →
exit 8, no GATE_ACTUATED/STATUS, the closed-count log
grows; a 200-byte truncated packet with an attached fd
→ exit 8, descriptor closed; ancillary data on the
LAUNCH_REQUEST itself → exit 8 before any fork.

Supporting change (as planned): HARNESS_PATH is
#ifndef-guarded; the production default is unchanged.
Test-only hooks are compile-time only: descriptor-close
failure injection, recvmsg-failure injection at a named
call index, xattr-error injection, and the closed-count
log (which records counts only, in the test build's own
directory).

## Results

Unit suite: 33/33 PASS (ASan/UBSan clean).
Peer acceptance suite: 53/53 PASS.
Both transcripts are in this bundle, with the build and
run scripts that produced them (stage_build.sh,
run_all.sh).

## Declared build iterations

(i) The first peer run exposed a build-script defect —
the quote-include resolved the zero-placeholder identity
header beside the source instead of the test build's
generated header, and the launcher correctly refused
with ABORT/IDENTITY_RECHECK_FAILED; the staging now
swaps the generated header in for the test compile and
restores the committed header after. (ii) The test
harness programme originally listed its own result-file
descriptor (opened before enumerating); it now
enumerates first — the fd assertions then read exactly
0 1 2. (iii) One peer case addressed its runs with a
two-digit counter and the corrected validator rejected
them (exit 12) — the case was fixed, the validator was
not touched. (iv) The capability-layout extra under F4
above.

## Submission

For Alex's independent source inspection against the
Batch 0 interface freeze, as the C4-0b pre-gate
requires. Batch 4 implementation, installation and
privileged execution remain unauthorised until his
disposition is recorded.
