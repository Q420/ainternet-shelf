#!/bin/bash
set -u
B=/srv/nemotron-pilot/batch4
cd $B/test-src
echo "== source pins (room test-src) =="
sha256sum launcher.c unit_test.c test_launcher.py test_harness.c
echo "== production compile (committed zero-placeholder header, no test defines) =="
gcc -std=c11 -O2 -Wall -Wextra -Werror -c launcher.c -o /tmp/launcher-prod-c0.o
echo "prod compile rc=$?"
echo "== hook strings in production object (must be none) =="
if strings /tmp/launcher-prod-c0.o | grep -E "PILOT_HOOK|closed-fds|STALL|FAIL_FIONREAD|FAIL_PEEK|FAIL_RECVMSG"; then
  echo "HOOK STRINGS PRESENT"
else
  echo "none"
fi
echo "== hook identifiers in test object (control: must be present) =="
strings $B/test/launcher-test | grep -E "PILOT_HOOK_FAIL_FIONREAD|PILOT_HOOK_STALL_RECV_MS" | sort -u
echo "== removed-mechanism tokens in source (must be none) =="
if grep -n "zero_classify\|250 ms\|250L\|CLOCK_MONOTONIC\|PILOT_HOOK_ZERO_DELAY" launcher.c; then
  echo "REMOVED TOKENS PRESENT"
else
  echo "none"
fi
echo "== classification not produced inside receipt layer =="
awk '/^static int chan_recv/,/^}/' launcher.c | grep -n "classify\|CLS_" || echo "chan_recv body: no classify/CLS_ references"
echo "== test-hook guards =="
grep -n "PILOT_TEST_HOOKS" launcher.c | head -20
