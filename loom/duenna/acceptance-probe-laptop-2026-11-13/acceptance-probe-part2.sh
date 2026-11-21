#!/bin/bash
# ACCEPTANCE PROBE — completion pass for the centrepiece (F-1 setuid test).
# The first pass installed gcc but the minimal image lacked libc headers
# (stdio.h), so the probe binary never built and invocations A/B did not run.
# This pass installs libc6-dev (same disclosed toolchain prep), compiles the
# SAME frozen source, and runs the invocations. Appended to the same log.
LOG=/home/ben/acceptance-probe.log
exec > >(tee -a "$LOG") 2>&1

echo
echo "=== PROBE CENTREPIECE — completion pass (first pass lacked libc headers) ==="
echo "date: $(date -Is)"
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libc6-dev 2>&1 | tail -2
SRC=/mnt/c/Users/ben/setuid_probe.c
echo "probe source sha256: $(sha256sum $SRC | awk '{print $1}')"
echo "expected (frozen):  64625db91420e93222b9d307139c8aa0c278a6099540ebb0054134291499dc53"
mkdir -p /usr/local/lib/nemotron-pilot
gcc -O2 -o /usr/local/lib/nemotron-pilot/setuid-probe $SRC && echo "compiled OK"
echo "probe binary sha256: $(sha256sum /usr/local/lib/nemotron-pilot/setuid-probe | awk '{print $1}')"
chown root:pilot-supervisor /usr/local/lib/nemotron-pilot/setuid-probe
chmod 4710 /usr/local/lib/nemotron-pilot/setuid-probe
stat -c '%U:%G %a %n' /usr/local/lib/nemotron-pilot/setuid-probe
echo "-- invocation A: as pilot-supervisor (PASS iff euid 0 observed) --"
runuser -u pilot-supervisor -- /usr/local/lib/nemotron-pilot/setuid-probe
echo "exit status: $?"
echo "-- invocation B: as pilot-harness (must be refused: mode 4710, not in group) --"
runuser -u pilot-harness -- /usr/local/lib/nemotron-pilot/setuid-probe 2>&1
echo "exit status: $?"
echo "=== CENTREPIECE COMPLETE ==="
echo "finished: $(date -Is)"
