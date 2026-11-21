#!/bin/bash
# ACCEPTANCE PROBE — Nemotron pilot candidate environment: Ben's laptop, Ubuntu (WSL2).
# Shape: environment-investigation.md Part 2 (Phases 0-1) + Alex's acceptance table
# (pb-mwelvcj4). Runs as root inside the distro (via wsl -u root). Every line of
# output is preserved to the log Ben watches and to this session's stdout.
LOG=/home/ben/acceptance-probe.log
exec > >(tee -a "$LOG") 2>&1
chmod 644 "$LOG" 2>/dev/null; chown ben:ben "$LOG" 2>/dev/null

say() { echo; echo "=== $* ==="; }
verdict() { echo "[$1] $2"; }

say "ACCEPTANCE PROBE — laptop Ubuntu room"
echo "date: $(date -Is)"
echo "hostname: $(hostname)"
echo "kernel: $(uname -a)"
grep PRETTY_NAME /etc/os-release

say "0.1 virtualisation type (plan: kvm/none PASS; container types FAIL)"
VIRT=$(systemd-detect-virt 2>/dev/null || echo "detect-virt-unavailable")
echo "systemd-detect-virt: $VIRT"
echo "note: recorded verbatim; classification against Alex's intent is his adjudication."

say "0.2 uid_map (plan: identity map PASS; offset map FAIL)"
echo "as root: $(cat /proc/self/uid_map | tr '\n' ' ')"
echo "as ben:  $(runuser -u ben -- cat /proc/self/uid_map | tr '\n' ' ')"

say "0.3 NoNewPrivs ancestry (plan: 0 everywhere in the chain)"
echo "PID 1 ($(cat /proc/1/comm)): $(grep NoNewPrivs /proc/1/status)"
PID=$$
while [ "$PID" != "0" ] && [ "$PID" != "1" ]; do
  echo "pid $PID ($(cat /proc/$PID/comm 2>/dev/null)): $(grep NoNewPrivs /proc/$PID/status 2>/dev/null)"
  PID=$(awk '{print $4}' /proc/$PID/stat 2>/dev/null)
done

say "0.4 launcher filesystem flags (plan: no nosuid/noexec on the launcher fs)"
findmnt -no TARGET,OPTIONS / 
findmnt -no TARGET,OPTIONS /usr/local/lib 2>/dev/null || echo "( /usr/local/lib is on the / mount )"

say "1.1 create the two identities (plan: distinct uid/gid, separate groups, harness NOT in supervisor group)"
groupadd -r pilot-supervisor 2>&1 || echo "(group pilot-supervisor may already exist)"
groupadd -r pilot-harness 2>&1 || echo "(group pilot-harness may already exist)"
useradd -r -M -g pilot-supervisor -s /usr/sbin/nologin pilot-supervisor 2>&1 || echo "(user pilot-supervisor may already exist)"
useradd -r -M -g pilot-harness -s /usr/sbin/nologin pilot-harness 2>&1 || echo "(user pilot-harness may already exist)"
echo "read-back: $(id pilot-supervisor)"
echo "read-back: $(id pilot-harness)"
getent passwd pilot-supervisor pilot-harness
getent group pilot-supervisor pilot-harness

say "1.2 custody tree — chown must stick and read back (incumbent FAILED here)"
ROOT=/srv/nemotron-pilot-probe
mkdir -p $ROOT/commitments $ROOT/runs
chown pilot-supervisor:pilot-supervisor $ROOT/commitments
chmod 0700 $ROOT/commitments
chown pilot-harness:pilot-harness $ROOT/runs
chmod 0755 $ROOT/runs
stat -c '%U:%G %a %n' $ROOT $ROOT/commitments $ROOT/runs
ls -ld / /srv $ROOT

say "1.3 custody separation — harness must be DENIED the supervisor's tree"
runuser -u pilot-supervisor -- bash -c "echo supervisor-secret > $ROOT/commitments/held.txt && chmod 0600 $ROOT/commitments/held.txt" && echo "supervisor wrote held.txt"
if runuser -u pilot-harness -- cat $ROOT/commitments/held.txt 2>/dev/null; then
  verdict FAIL "pilot-harness READ the supervisor custody file"
else
  verdict PASS "pilot-harness cannot read supervisor custody (denied)"
fi
if runuser -u pilot-harness -- touch $ROOT/commitments/intrusion 2>/dev/null; then
  verdict FAIL "pilot-harness WROTE into supervisor custody"
else
  verdict PASS "pilot-harness cannot write supervisor custody (denied)"
fi
runuser -u pilot-supervisor -- cat $ROOT/commitments/held.txt >/dev/null && verdict PASS "supervisor reads its own custody"
runuser -u pilot-harness -- touch $ROOT/runs/harness-work && verdict PASS "harness writes its own runs tree"

say "PROBE — setuid elevation, Batch 0's exact shape (the F-1 test)"
SRC=/mnt/c/Users/ben/setuid_probe.c
echo "probe source sha256: $(sha256sum $SRC | awk '{print $1}')"
echo "expected (frozen):  64625db91420e93222b9d307139c8aa0c278a6099540ebb0054134291499dc53"
if ! command -v gcc >/dev/null 2>&1; then
  echo "no compiler present — installing gcc (disclosed environment change, logged):"
  apt-get update -qq 2>&1 | tail -1
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gcc 2>&1 | tail -2
fi
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

say "CAPS — capability state observable and empty (Alex's table)"
echo "as root context:"; grep -E 'Cap(Inh|Prm|Eff|Bnd|Amb)' /proc/self/status
echo "as pilot-harness:"; runuser -u pilot-harness -- grep -E 'Cap(Inh|Prm|Eff|Bnd|Amb)' /proc/self/status
cat > /tmp/ambcheck.py << 'PYEOF'
import ctypes
libc = ctypes.CDLL("libc.so.6", use_errno=True)
PR_CAP_AMBIENT = 47; PR_CAP_AMBIENT_IS_SET = 2
vals = [libc.prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, cap, 0, 0) for cap in range(41)]
print("ambient caps set:", [i for i, v in enumerate(vals) if v > 0] or "NONE")
PYEOF
echo "ambient (as pilot-harness): $(runuser -u pilot-harness -- python3 /tmp/ambcheck.py)"
echo "ambient (as ben): $(runuser -u ben -- python3 /tmp/ambcheck.py)"

say "NET — isolation constructible; indirect paths on the record (Alex's table, G1 widened)"
echo "proxy env in distro: $(env | grep -i proxy || echo none)"
echo "default namespace routes:"; ip route 2>/dev/null || echo "(iproute2 absent)"
cat > /tmp/nsprobe.py << 'PYEOF'
import socket, subprocess, sys
subprocess.run(["ip", "link", "set", "lo", "up"])
print("namespace routes:", subprocess.run(["ip", "route"], capture_output=True, text=True).stdout.strip() or "(empty)")
for target, port, label in [("1.1.1.1", 53, "non-provider egress"), ("127.0.0.1", 9, "loopback stack")]:
    s = socket.socket(); s.settimeout(5)
    try:
        s.connect((target, port)); print(f"{label}: CONNECTED (unexpected)")
    except OSError as e:
        print(f"{label}: {type(e).__name__}: {e}")
    finally:
        s.close()
PYEOF
echo "-- inside a fresh loopback-only namespace (unshare -Urn, as ben) --"
runuser -u ben -- unshare -Urn python3 /tmp/nsprobe.py 2>&1

say "PROBE COMPLETE"
echo "finished: $(date -Is)"
echo "exhibits left in place: accounts pilot-supervisor/pilot-harness; $ROOT; /usr/local/lib/nemotron-pilot/setuid-probe; this log."
