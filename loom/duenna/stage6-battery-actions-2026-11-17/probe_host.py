#!/usr/bin/python3
"""Online-venue custody feasibility probe (rudimentary test,
2026-11-17). Checks only: creates nothing outside a temp dir,
no accounts, no keys, no network calls.

A custody venue for the Stage 6 battery must let a setuid
launcher actually elevate (the VM fails this: NoNewPrivs=1 on
every process). This probe measures the decisive facts:
NoNewPrivs, seccomp, mount nosuid flags, a functional
setuid-elevation test (when run as root), loopback binding,
toolchain presence, and resources. Verdict:
CUSTODY_FEASIBLE / NOT_FEASIBLE / UNKNOWN_NEEDS_ROOT.
"""
import json, os, shutil, socket, subprocess, sys, tempfile

checks = {}
def rec(name, status, detail):
    checks[name] = {"status": status, "detail": detail}

status = open('/proc/self/status').read()
nn = [l for l in status.splitlines() if l.startswith('NoNewPrivs')]
sec = [l for l in status.splitlines() if l.startswith('Seccomp:')]
nnv = nn[0].split(':')[1].strip() if nn else '?'
rec('no_new_privs', 'FAIL' if nnv == '1' else 'PASS',
    f'NoNewPrivs={nnv} (1 = kernel ignores setuid = custody impossible)')
rec('seccomp', 'INFO', sec[0].split(':')[1].strip() if sec else '?')

mounts = open('/proc/mounts').read().splitlines()
def mount_of(path):
    best = None
    for m in mounts:
        parts = m.split()
        if len(parts) >= 4 and (path == parts[1] or path.startswith(parts[1].rstrip('/') + '/')):
            if best is None or len(parts[1]) > len(best[1]):
                best = parts
    return best
# The elevation test must run on a suid-capable filesystem of
# the class a room would live on (a rootfs dir), NOT on a
# nosuid scratch tmpfs like /tmp — the first WSL control run
# measured /tmp and falsely failed a known-good room.
tmp = None
for cand in (os.environ.get('VENUE_PROBE_DIR'), '/srv', '/var/tmp', '/tmp'):
    if not cand or not os.path.isdir(cand):
        continue
    probe_dir = os.path.join(cand, '.venue-probe-tmp')
    try:
        os.makedirs(probe_dir, exist_ok=True)
    except OSError:
        continue
    mnt = mount_of(probe_dir)
    if mnt and 'nosuid' not in mnt[3].split(','):
        tmp = probe_dir
        break
    shutil.rmtree(probe_dir, ignore_errors=True)
if tmp is None:
    tmp = tempfile.mkdtemp(prefix='venue-probe-')
best = mount_of(tmp)
if best:
    nosuid = 'nosuid' in best[3].split(',')
    rec('mount_setuid', 'FAIL' if nosuid else 'PASS',
        f'test dir {tmp} on {best[1]} options={best[3]}')
else:
    rec('mount_setuid', 'UNKNOWN', 'mount not found for temp dir')

# functional setuid test: helper owned by root, run as nobody;
# elevation happened iff euid becomes 0 while uid stays 65534.
if os.geteuid() == 0 and shutil.which('gcc'):
    src = os.path.join(tmp, 'h.c')
    exe = os.path.join(tmp, 'helper')
    open(src, 'w').write('#include <stdio.h>\n#include <unistd.h>\n'
                         'int main(){printf("%d %d\\n", getuid(), geteuid()); return 0;}\n')
    subprocess.run(['gcc', '-O2', '-o', exe, src], check=True,
                   capture_output=True)
    os.chown(exe, 0, 0); os.chmod(exe, 0o4711)
    out = None
    for runner in (['setpriv', '--reuid=65534', '--regid=65534',
                    '--clear-groups', exe],
                   ['runuser', '-u', 'nobody', '--', exe],
                   ['su', '-s', '/bin/sh', 'nobody', '-c', exe]):
        if shutil.which(runner[0]):
            r = subprocess.run(runner, capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                out = r.stdout.strip(); break
    if out:
        uid_s, euid_s = out.split()
        rec('setuid_elevation', 'PASS' if euid_s == '0' and uid_s == '65534' else 'FAIL',
            f'helper as nobody: uid={uid_s} euid={euid_s}')
    else:
        rec('setuid_elevation', 'UNKNOWN', 'no working nobody-runner found')
elif os.geteuid() != 0:
    rec('setuid_elevation', 'UNKNOWN_NEEDS_ROOT', 'probe not run as root')
else:
    rec('setuid_elevation', 'UNKNOWN', 'gcc missing')

try:
    s = socket.socket(); s.bind(('127.0.0.1', 0)); s.listen(1)
    port = s.getsockname()[1]
    c = socket.create_connection(('127.0.0.1', port), timeout=3)
    c.close(); s.close()
    rec('loopback_bind', 'PASS', f'bound+connected on 127.0.0.1:{port}')
except Exception as e:
    rec('loopback_bind', 'FAIL', f'{type(e).__name__}: {e}')

for tool in ('gcc', 'python3', 'useradd', 'systemctl'):
    rec(f'tool_{tool}', 'PASS' if shutil.which(tool) else 'MISSING',
        shutil.which(tool) or 'not on PATH')
du = shutil.disk_usage('/')
mem = [l for l in open('/proc/meminfo') if l.startswith('MemTotal')][0]
rec('resources', 'INFO',
    f'cpus={os.cpu_count()} disk_free_gb={du.free // 2**30} {mem.strip()}')
rec('outbound_https', 'UNKNOWN',
    'not tested (no live call in this test scope)')

hard_fail = any(v['status'] == 'FAIL' for v in checks.values())
unknown_key = checks['setuid_elevation']['status'].startswith('UNKNOWN')
verdict = ('NOT_FEASIBLE' if hard_fail else
           'UNKNOWN_NEEDS_ROOT' if unknown_key else 'CUSTODY_FEASIBLE')
print(json.dumps({'verdict': verdict, 'checks': checks}, indent=1))
shutil.rmtree(tmp, ignore_errors=True)
