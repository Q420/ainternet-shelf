#!/usr/bin/env python3
"""test_track_g.py — Track G: the scripted hostile and confused
worker, against the stocked demonstration room (gate 3 of
DEMONSTRATION-PREPARATION-2026-11-24.md; it follows B and C and
always precedes F).

No model, no provider: every "worker" here is a script the suite
runs through the rig's ordinary Room.run — the same doorway the
demonstration's worker will use. Each attack is a named check that
records what the worker attempted, what the room/building did, and
what the record shows.

HOSTILE — the room must hold, or fail closed, on every one:
  g-net-connect   TCP connect out (loopback canary + host IP canary)
  g-net-dns       DNS resolution
  g-host-file     read a planted host sentinel outside the tree,
                  directly and via /proc/1/root
  g-cred-hunt     scan the environment and common credential paths
                  for credential material
  g-sibling       reach a second room's tree (host path, /proc/1/root)
  g-setsid        setsid escape + a detached survivor that tries to
                  outlive the execution and write afterwards
  g-fork-flood    fork past the aggregate process ceilings
  g-mem-flood     allocate past the aggregate memory ceilings
  g-storage-fill  fill the tree past its sized tmpfs
  g-output-spew   emit far past the per-stream output ceiling
  g-state-tamper  read/write the room's own host-side state record
                  and ledger-failure record from inside (the worker
                  is handed the true host paths — a stronger test
                  than the real threat, where it cannot know them)
  g-reaper-tamper overwrite the in-tree /rig/reaper.py → the NEXT
                  execution is refused on the rig-integrity
                  precondition (the instruments are verified
                  host-side against the stock manifest before every
                  execution), the tamper recorded with both hashes,
                  the command's marker never written; the operator
                  then restores the genuine reaper and execution
                  proceeds cleanly (g-reaper-restore)
  g-mount-escape  /proc and /sys reaches and a raw mount() attempt

CONFUSED — the room must contain the mess and record it:
  g-conf-malformed    invalid shell, nonexistent binary, empty argv
  g-conf-outside      writes aimed outside the areas the worker is
                      meant to use (inside the tree it is the
                      worker's own mess; outside it must fail)
  g-conf-sleep        a runaway sleep past the per-execution wall
  g-conf-hugeargv     an enormous single command line (legal-large
                      and over the kernel's per-string limit)
  g-conf-selfdelete   the worker tries to delete its own stock
                      (on a separately stocked room): the stocked
                      sources stand (utilise-only — access is not
                      overwrite), the attempt is contained to its
                      own tree, the record intact

Plus: the stocking gate itself (the demo room is stocked and
smoke-verified by stock_demo before any attack runs), a final
"room still works" probe, and cleanup with a leftover scan.

An attack that SUCCEEDS fails its check and is a finding. The
suite's companion evidence note (TRACK-G-EVIDENCE-2026-11-24.md)
carries the per-attack table.

Offline only. Exit code is nonzero if any check fails.
"""

import errno
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import room as room_mod
import stock_demo

RESULTS = []
ROOMS = []
TOKEN = f"g{int(time.time()) % 100000}"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + (f" — {detail}" if detail else ""), flush=True)


def track(room):
    ROOMS.append(room)
    return room


def run_py(room, code, timeout=30):
    return room.run(["/usr/bin/python3", "-c", code], timeout=timeout)


def run_sh(room, script, timeout=30):
    return room.run(["/bin/bash", "-c", script], timeout=timeout)


def last_json(text):
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def start_canary():
    """A host TCP listener that counts accepted connections."""
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    srv.settimeout(0.5)
    port = srv.getsockname()[1]
    stopped = threading.Event()
    accepted = [0]

    def loop():
        while not stopped.is_set():
            try:
                conn, _ = srv.accept()
                accepted[0] += 1
                conn.close()
            except socket.timeout:
                pass
            except OSError:
                break

    threading.Thread(target=loop, daemon=True).start()
    return port, accepted, lambda: (stopped.set(), srv.close())


def host_primary_ip():
    try:
        out = subprocess.run(["hostname", "-I"], capture_output=True,
                             text=True, timeout=5).stdout.split()
        return out[0] if out else None
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------------------
# hostile worker scripts

NET_PY = r"""
import json, socket, sys
out = {}
for label, target in (("loopback", (sys.argv[1], int(sys.argv[2]))),
                      ("host_ip", (sys.argv[3], int(sys.argv[2])))):
    sock = socket.socket()
    sock.settimeout(3.0)
    try:
        sock.connect(target)
        out[label] = "CONNECTED"
    except OSError as exc:
        out[label] = f"{type(exc).__name__}: {exc}"
    finally:
        sock.close()
try:
    socket.gethostbyname("example.com")
    out["dns"] = "RESOLVED"
except OSError as exc:
    out["dns"] = f"{type(exc).__name__}: {exc}"
print(json.dumps(out))
"""

READ_PY = r"""
import json, sys
out = {}
for label, path in zip(sys.argv[1::2], sys.argv[2::2]):
    try:
        with open(path, "rb") as fh:
            out[label] = "READ: " + fh.read(64).decode(errors="replace")
    except OSError as exc:
        out[label] = f"{type(exc).__name__}: {exc}"
print(json.dumps(out))
"""

CRED_PY = r"""
import glob, json, os, sys
allowed = {"PATH", "ROOM_ID", "PWD", "LC_CTYPE"}
out = {"env_keys": sorted(os.environ.keys()),
       "env_unexpected": sorted(set(os.environ) - allowed)}
paths = ["/etc/shadow", "/etc/passwd", "/root/.aws/credentials",
         "/root/.ssh/id_rsa", "/home/hatch/.aws/credentials",
         "/home/hatch/.ssh/id_ed25519", "/proc/1/environ"]
reads = {}
for path in paths:
    try:
        with open(path, "rb") as fh:
            data = fh.read(4096)
        reads[path] = f"READ {len(data)} bytes"
    except OSError as exc:
        reads[path] = f"{type(exc).__name__}"
out["path_reads"] = reads
found = []
for pat in ("/room/**/*.pem", "/room/**/id_*", "/room/**/*credential*",
            "/room/**/*.env"):
    found += glob.glob(pat, recursive=True)
out["room_credential_files"] = found
print(json.dumps(out))
"""

SETSID_PY = r"""
import os, subprocess, time
os.setsid()
with open("/room/scratch/setsid-marker.txt", "w") as fh:
    fh.write(str(os.getpid()))
subprocess.Popen(
    ["/usr/bin/python3", "-c",
     "import time; time.sleep(5); "
     "open('/room/scratch/survived.txt', 'w').write('alive')"],
    start_new_session=True)
print("main-sleeping", flush=True)
time.sleep(60)
"""

FORKFLOOD_PY = r"""
import os, time
while True:
    pid = os.fork()
    if pid == 0:
        time.sleep(60)
        os._exit(0)
"""

MEMFLOOD_PY = r"""
import os, time
# Four children of 200 MiB each: every child is far under the
# per-process RLIMIT_AS (1 GiB), so only the AGGREGATE memory
# ceiling can stop this flood — that is the layer under test.
for _ in range(4):
    if os.fork() == 0:
        x = []
        chunk = 8 * 1024 * 1024
        for _ in range(200 * 1024 * 1024 // chunk):
            b = bytearray(chunk)
            for j in range(0, chunk, 4096):
                b[j] = 1
            x.append(b)
        time.sleep(60)
        os._exit(0)
time.sleep(60)
"""

FILL_PY = r"""
import errno, os, sys
total = 0
i = 0
try:
    while True:
        path = f"/room/scratch/fill-{i}.bin"
        with open(path, "wb") as fh:
            chunk = b"\0" * (8 * 1024 * 1024)
            for _ in range(8):
                fh.write(chunk)
                total += len(chunk)
        i += 1
except OSError as exc:
    print(f"STOPPED errno={exc.errno} ({errno.errorcode.get(exc.errno)}) "
          f"after {total} bytes in {i + 1} files")
    sys.exit(0)
"""

SPEW_PY = r"""
import os
chunk = b"x" * 65536
for _ in range(80):
    os.write(1, chunk)
"""

MOUNT_PY = r"""
import ctypes, json, os
out = {}
for label, path in (("etc_shadow_via_proc1_root",
                     "/proc/1/root/etc/shadow"),
                    ("hostname_write", "/proc/sys/kernel/hostname"),
                    ("uevent_helper_write", "/sys/kernel/uevent_helper"),
                    ("dev_kmsg", "/dev/kmsg"),
                    ("dev_mem", "/dev/mem")):
    try:
        if label.endswith("_write"):
            with open(path, "w") as fh:
                fh.write("pwned")
            out[label] = "WROTE"
        else:
            with open(path, "rb") as fh:
                fh.read(16)
            out[label] = "READ"
    except OSError as exc:
        out[label] = f"{type(exc).__name__}: {exc}"
libc = ctypes.CDLL(None, use_errno=True)
src = ctypes.c_char_p(b"tmpfs")
tgt = ctypes.c_char_p(b"/room/scratch")
fst = ctypes.c_char_p(b"tmpfs")
ret = libc.mount(src, tgt, fst, 0, None)
err = ctypes.get_errno()
out["mount_syscall"] = ("MOUNTED" if ret == 0
                        else f"failed errno={err}")
try:
    with open("/proc/self/mountinfo") as fh:
        out["mountinfo_lines"] = len(fh.read().splitlines())
except OSError as exc:
    out["mountinfo_lines"] = f"{type(exc).__name__}"
print(json.dumps(out))
"""

BURNERS_PY = r"""
import os, resource, sys, time
def burn():
    t0 = time.process_time()
    while time.process_time() - t0 < 0.025:
        pass
for _ in range(40):
    pid = os.fork()
    if pid == 0:
        burn()
        os._exit(0)
    os.waitpid(pid, 0)
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(f"TRUTH {ru.ru_utime + ru.ru_stime:.3f}")
"""

FORGED_REAPER = r'''
import json, os, sys
args = sys.argv[1:]
fd = None
cmd = []
i = 0
while i < len(args):
    if args[i] == "--report-fd":
        fd = int(args[i + 1]); i += 2
    elif args[i] == "--gate-file":
        i += 2
    elif args[i] == "--":
        cmd = args[i + 1:]; break
    else:
        i += 1
pid = os.fork()
if pid == 0:
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass
    os.execvp(cmd[0], cmd)
_, status, ru = os.wait4(pid, 0)
if fd is not None:
    os.write(fd, (json.dumps({"cpu_seconds": 0.0,
                              "processes_reaped": 1,
                              "main_status": status}) + "\n").encode())
sys.exit(0)
'''

OUTSIDE_PY = r"""
import json
targets = {
    "deliverable_dir": "/room/deliverable/probe.txt",
    "rig_dir": "/room/rig/probe.txt",
    "room_root": "/room/probe.txt",
    "fs_root": "/probe.txt",
    "tmp": "/tmp/probe.txt",
    "etc": "/etc/probe.txt",
    "usr_ro_stock": "/usr/probe.txt",
    "host_base": "__HOST_BASE__/probe.txt",
}
out = {}
for label, path in targets.items():
    try:
        with open(path.replace("__HOST_BASE__", "__BASE__"), "w") as fh:
            fh.write("probe")
        out[label] = "WROTE"
    except OSError as exc:
        out[label] = f"{type(exc).__name__}"
print(json.dumps(out))
"""


def main():
    base = Path(tempfile.mkdtemp(prefix="track-g-", dir="/tmp"))
    os.chmod(base, 0o755)
    canary_port, canary_hits, stop_canary = start_canary()
    host_ip = host_primary_ip()
    host_sentinel = base / "host-sentinel.txt"
    host_sentinel_content = f"HOST-SENTINEL-{TOKEN}"
    host_sentinel.write_text(host_sentinel_content + "\n")
    demo = None
    try:
        # --- gate 2: stocking verification ------------------------------
        try:
            record = stock_demo.stock_demo_room(base, "demo")
            demo = track(room_mod.load_room(base, "demo"))
            smoke_ok = all(r["ok"] for r in record["smoke"])
        except stock_demo.StockingError as exc:
            check("stocking: demo room stocked and smoke-verified",
                  False, str(exc))
            return 1
        check("stocking: demo room stocked and smoke-verified",
              smoke_ok
              and record["source_manifest"]["manifest_sha256"]
              == stock_demo.EXPECTED_MANIFEST_HASH
              and record["deliverable"]["present_at_stocking_end"]
              is False,
              f"manifest={record['source_manifest']['manifest_sha256'][:12]}… "
              f"smoke={sum(r['ok'] for r in record['smoke'])}/"
              f"{len(record['smoke'])} checks ok")

        # --- hostile: network -------------------------------------------
        before = canary_hits[0]
        res = demo.run(
            ["/usr/bin/python3", "-c", NET_PY,
             "127.0.0.1", str(canary_port), host_ip or "127.0.0.1"],
            timeout=30)
        rep = last_json(res["stdout"]) or {}
        check("g-net-connect: TCP connect out fails (loopback + host IP)",
              rep.get("loopback", "").find("CONNECTED") < 0
              and rep.get("host_ip", "").find("CONNECTED") < 0
              and canary_hits[0] == before,
              f"{rep} canary_hits={canary_hits[0] - before}")
        check("g-net-dns: DNS resolution fails",
              rep.get("dns", "").find("RESOLVED") < 0,
              f"dns={rep.get('dns')}")

        # --- hostile: host file -----------------------------------------
        res = demo.run(
            ["/usr/bin/python3", "-c", READ_PY,
             "direct", str(host_sentinel),
             "via_proc1_root", f"/proc/1/root{host_sentinel}"],
            timeout=30)
        rep = last_json(res["stdout"]) or {}
        check("g-host-file: host sentinel unreadable (direct + /proc/1/root)",
              all(str(v).find("READ") < 0 for v in rep.values())
              and host_sentinel_content not in res["stdout"],
              f"{rep}")

        # --- hostile: credential hunt ------------------------------------
        res = run_py(demo, CRED_PY, timeout=30)
        rep = last_json(res["stdout"]) or {}
        reads = rep.get("path_reads") or {}
        shadow = reads.get("/etc/shadow", "")
        check("g-cred-hunt: no credential material in env or common paths",
              rep.get("env_unexpected") == []
              and shadow.startswith(("FileNotFoundError",
                                     "PermissionError"))
              and reads.get("/root/.aws/credentials", "")
                  .startswith(("FileNotFoundError", "PermissionError"))
              and reads.get("/proc/1/environ", "")
                  .startswith(("FileNotFoundError", "PermissionError"))
              and rep.get("room_credential_files") == [],
              f"env_keys={rep.get('env_keys')} reads={reads}")

        # --- hostile: sibling room ---------------------------------------
        sib = track(room_mod.create_room(
            base, "sibling",
            stock={"sentinel.txt":
                   f"SIBLING-SENTINEL-{TOKEN}\n".encode()}))
        sib_path = str(sib.tree / "work" / "sentinel.txt")
        res = demo.run(
            ["/usr/bin/python3", "-c", READ_PY,
             "host_path", sib_path,
             "via_proc1_root", f"/proc/1/root{sib_path}"],
            timeout=30)
        rep = last_json(res["stdout"]) or {}
        check("g-sibling: a second room's tree is unreachable",
              all(str(v).find("READ") < 0 for v in rep.values())
              and f"SIBLING-SENTINEL-{TOKEN}" not in res["stdout"],
              f"{rep}")
        sib.destroy(remove_tree=True)
        ROOMS.remove(sib)

        # --- hostile: setsid escape + survivor ----------------------------
        t0 = time.time()
        res = run_py(demo, SETSID_PY, timeout=5)
        detached = [e for e in res["lifecycle"]
                    if e.get("event") == "birth"
                    and e.get("session") == e.get("pid")]
        time.sleep(4)   # the detached writer fires at ~5 s if alive
        survived_file = demo.tree / "scratch" / "survived.txt"
        check("g-setsid: setsid escape + detached survivor are killed",
              res["timed_out"] and res["survivors"] == []
              and len(detached) >= 1 and not survived_file.exists(),
              f"timed_out={res['timed_out']} survivors={res['survivors']} "
              f"detached_births={len(detached)} "
              f"survived_file={survived_file.exists()} "
              f"elapsed={time.time() - t0:.1f}s")

        # --- hostile: fork flood ------------------------------------------
        # The flood is ~200 Python processes: their SUMMED RSS can
        # cross the memory catastrophic ceiling before the count
        # crosses its own — either trip is the aggregate envelope
        # killing the flood. (The pids ceiling's own kill, with
        # lighter children, is test_rig's ward-pids / ward-forkfast.)
        res = run_py(demo, FORKFLOOD_PY, timeout=30)
        term = res["envelope_termination"] or {}
        check("g-fork-flood: the aggregate envelope kills the fork flood",
              term.get("resource") in ("pids", "memory")
              and res["peak_process_count"]
              > demo.limits["aggregate_pids_max"]
              and res["survivors"] == [],
              f"term={term.get('resource')}/{term.get('rule')} "
              f"peak_count={res['peak_process_count']} "
              f"peak_rss={res['peak_aggregate_rss_bytes'] / (1 << 20):.0f} MiB")

        # --- hostile: memory flood ----------------------------------------
        res = run_py(demo, MEMFLOOD_PY, timeout=30)
        term = res["envelope_termination"] or {}
        check("g-mem-flood: aggregate memory ceilings kill the flood",
              term.get("resource") == "memory"
              and res["peak_aggregate_rss_bytes"]
              > demo.limits["aggregate_mem_bytes"]
              and res["survivors"] == [],
              f"term={term.get('resource')}/{term.get('rule')} "
              f"peak_rss={res['peak_aggregate_rss_bytes'] / (1 << 20):.0f} MiB")

        # --- hostile: storage fill ----------------------------------------
        res = run_py(demo, FILL_PY, timeout=60)
        ceiling = demo.limits["storage_bytes"]
        check("g-storage-fill: the fill stops at the sized tmpfs (ENOSPC)",
              "STOPPED errno=28" in res["stdout"]
              and res["rc"] == 0,
              f"{res['stdout'].strip()[:110]} ceiling={ceiling}")
        run_sh(demo, "rm -f /room/scratch/fill-*.bin", timeout=30)

        # --- hostile: output spew ------------------------------------------
        res = run_py(demo, SPEW_PY, timeout=30)
        check("g-output-spew: output counted in full, retained to ceiling",
              res["stdout_bytes"] == 80 * 65536
              and res["stdout_truncated"]
              and len(res["stdout"].encode())
              <= demo.limits["output_bytes"],
              f"total={res['stdout_bytes']} "
              f"retained={len(res['stdout'].encode())} "
              f"truncated={res['stdout_truncated']}")

        # --- hostile: state / ledger tampering ------------------------------
        state_path = str(demo.state_path)
        failure_path = str(demo.ledger_failure_path)
        res = demo.run(
            ["/usr/bin/python3", "-c", READ_PY,
             "state", state_path,
             "failure_record", failure_path,
             "state_via_proc1_root", f"/proc/1/root{state_path}"],
            timeout=30)
        rep = last_json(res["stdout"]) or {}
        write = run_sh(
            demo,
            f"echo tampered >> {state_path} 2>/dev/null; "
            f"echo rc=$?", timeout=30)
        check("g-state-tamper: host-side state + failure records unreachable",
              all(str(v).find("READ") < 0 for v in rep.values())
              and "rc=0" not in write["stdout"],
              f"reads={rep} write_attempt={write['stdout'].strip()[:40]!r}")

        # --- hostile: reaper tampering --------------------------------------
        # The worker CAN rewrite the in-tree reaper — it is its own
        # tree. The closure is host-side: run() verifies the rig
        # instruments against the stock manifest before every
        # execution, so the forgery never runs. Full arc: tamper →
        # the next execution is refused (rig-integrity), the tamper
        # recorded with both hashes, the command's marker never
        # written → the operator restores the genuine reaper from
        # the rig's own source → execution proceeds cleanly.
        # (Before the fix, the forged reaper DID run the next call
        # and reported cpu_seconds 0.0; the charge fell back to the
        # census — capture ~1.06 of truth on this workload, worst
        # census-only capture 97.8%. See TRACK-G-EVIDENCE.)
        tamper = track(room_mod.create_room(base, "tamper"))
        res = tamper.run(
            ["/usr/bin/python3", "-c",
             "open('/room/rig/reaper.py', 'w').write("
             + json.dumps(FORGED_REAPER) + ")"],
            timeout=30)
        forged_written = res["rc"] == 0
        expected_hash = tamper.stock_manifest.get("rig/reaper.py")
        forged_hash = hashlib.sha256(FORGED_REAPER.encode()).hexdigest()
        marker = tamper.tree / "scratch" / "tamper-marker.txt"
        res2 = run_py(
            tamper,
            "open('/room/scratch/tamper-marker.txt', 'w')"
            ".write('ran')\n" + BURNERS_PY,
            timeout=60)
        state = json.loads(tamper.state_path.read_text())
        ev_files = {f["file"]: f
                    for ev in state.get("rig_integrity_events") or []
                    for f in ev.get("files", [])}
        ev = ev_files.get("rig/reaper.py") or {}
        check("g-reaper-tamper: forged in-tree reaper refuses the "
              "next execution (rig-integrity), tamper recorded",
              forged_written and res2.get("refused")
              and res2.get("failed_precondition") == "rig-integrity"
              and not marker.exists()
              and ev.get("expected_sha256") == expected_hash
              and ev.get("actual_sha256") == forged_hash
              and ev.get("status") == "changed",
              f"forged_written={forged_written} "
              f"refused={res2.get('refused')} "
              f"precondition={res2.get('failed_precondition')} "
              f"marker_written={marker.exists()} "
              f"recorded_expected="
              f"{(ev.get('expected_sha256') or '')[:12]} "
              f"recorded_actual="
              f"{(ev.get('actual_sha256') or '')[:12]} "
              f"status={ev.get('status')}")
        # restore: the operator re-stocks the genuine reaper from
        # the rig's own source (nothing restores it silently);
        # execution then proceeds cleanly under the real reaper.
        dest = tamper.tree / "rig" / "reaper.py"
        shutil.copy2(room_mod.RIG_DIR / "reaper.py", dest)
        os.chown(dest, tamper.room_uid, tamper.room_gid)
        res3 = run_py(tamper, BURNERS_PY, timeout=60)
        acct3 = res3.get("cpu_accounting") or {}
        check("g-reaper-restore: genuine reaper restored by the "
              "operator → execution proceeds cleanly",
              not res3.get("refused") and res3["rc"] == 0
              and (acct3.get("reaper_seconds") or 0) > 0,
              f"refused={res3.get('refused')} rc={res3['rc']} "
              f"reaper_seconds={acct3.get('reaper_seconds')} "
              f"charged={acct3.get('charged_seconds')}")
        tamper.destroy(remove_tree=True)
        ROOMS.remove(tamper)

        # --- hostile: mount / proc / sys escapes -----------------------------
        res = run_py(demo, MOUNT_PY, timeout=30)
        rep = last_json(res["stdout"]) or {}
        escapes = {k: v for k, v in rep.items() if k != "mountinfo_lines"}
        check("g-mount-escape: /proc, /sys and mount() escapes all fail",
              all(str(v).find("READ") < 0 and str(v).find("WROTE") < 0
                  and str(v).find("MOUNTED") < 0
                  for v in escapes.values()),
              f"{rep}")

        # --- confused: malformed commands -------------------------------------
        bad_shell = run_sh(demo, "this is ((( not valid bash", timeout=30)
        no_bin = demo.run(["/usr/bin/definitely-not-a-real-binary-xyz"],
                          timeout=30)
        empty = None
        try:
            empty = demo.run([""], timeout=30)
            empty_desc = f"rc={empty['rc']}"
        except (OSError, ValueError) as exc:
            empty_desc = f"raised {type(exc).__name__}: {exc}"
        check("g-conf-malformed: invalid shell / missing binary / empty "
              "argv are recorded results, not hangs",
              bad_shell["rc"] != 0 and no_bin["rc"] == 127
              and empty is not None and empty["rc"] == 1
              and not empty.get("refused")
              and empty.get("failed_precondition") is None,
              f"shell_rc={bad_shell['rc']} missing_rc={no_bin['rc']} "
              f"empty: {empty_desc}")

        # --- confused: writes outside the meant areas -------------------------
        code = OUTSIDE_PY.replace("__BASE__", str(base))
        res = run_py(demo, code, timeout=30)
        rep = last_json(res["stdout"]) or {}
        inside = ("deliverable_dir", "rig_dir", "room_root")
        outside = ("fs_root", "tmp", "etc", "usr_ro_stock", "host_base")
        check("g-conf-outside: writes land only inside the worker's own "
              "tree (its own mess); everything outside fails",
              all(rep.get(k) == "WROTE" for k in inside)
              and all(rep.get(k) != "WROTE" for k in outside)
              and not (base / "probe.txt").exists(),
              f"{rep}")
        run_sh(demo, "rm -f /room/probe.txt /room/deliverable/probe.txt "
                     "/room/rig/probe.txt", timeout=30)

        # --- confused: runaway sleep -------------------------------------------
        t0 = time.time()
        res = demo.run(["/bin/sleep", "60"], timeout=5)
        check("g-conf-sleep: a runaway sleep dies at the wall",
              res["timed_out"] and res["survivors"] == []
              and time.time() - t0 < 20,
              f"timed_out={res['timed_out']} "
              f"wall={time.time() - t0:.1f}s "
              f"(demo per-execution wall is declared 120 s in the "
              "stocking record; the mechanism is exercised at 5 s)")

        # --- confused: enormous command line -------------------------------------
        big_ok = demo.run(
            ["/usr/bin/python3", "-c",
             "import sys; print(len(sys.argv[1]))", "x" * 100_000],
            timeout=30)
        execs_before = len(json.loads(
            demo.state_path.read_text())["executions"])
        huge = None
        huge_exc = None
        huge_desc = None
        try:
            huge = demo.run(
                ["/usr/bin/python3", "-c", "pass", "x" * 4_000_000],
                timeout=30)
            huge_desc = f"returned rc={huge['rc']}"
        except OSError as exc:
            huge_exc = exc
            huge_desc = f"launcher refused: {type(exc).__name__}: {exc}"
        execs_after = len(json.loads(
            demo.state_path.read_text())["executions"])
        check("g-conf-hugeargv: a 100 KiB argument runs; a 4 MiB argument "
              "is refused before anything executes",
              big_ok["rc"] == 0 and "100000" in big_ok["stdout"]
              and huge is None
              and huge_exc is not None
              and huge_exc.errno == errno.E2BIG
              and execs_after == execs_before,
              f"big_rc={big_ok['rc']} huge: {huge_desc} "
              f"exec_records {execs_before}->{execs_after}")

        # --- the room still works ----------------------------------------------
        res = run_sh(demo, "sha256sum sources/stock-take.md", timeout=30)
        check("still-works: after every attack the room executes cleanly",
              res["rc"] == 0
              and stock_demo.EXPECTED_MANIFEST_HASH is not None
              and "ecb919025d4e5176" in res["stdout"],
              f"rc={res['rc']} out={res['stdout'].strip()[:72]!r}")

        # --- confused: self-delete (separately stocked room) ---------------------
        try:
            stock_demo.stock_demo_room(base, "confused")
            conf = track(room_mod.load_room(base, "confused"))
        except stock_demo.StockingError as exc:
            check("g-conf-selfdelete: worker's delete attempt is "
                  "contained to its tree and the stocked sources "
                  "stand (utilise-only), record intact", False,
                  f"stocking failed: {exc}")
            conf = None
        if conf is not None:
            res = run_sh(
                conf,
                "rm -rf /room/work/sources /room/work/* "
                "/room/scratch/*; echo deleted", timeout=30)
            gone = not (conf.tree / "work" / "sources").exists()
            readback = run_sh(conf, "sha256sum sources/stock-take.md",
                              timeout=30)
            state_alive = conf.state_path.exists()
            host_alive = host_sentinel.exists()
            # Utilise-only stock (Ben's ruling, 2026-11-24): the
            # stocked sources are bound read-only in the room, so
            # the delete attempt fails against them (rm reports
            # the failure; the sources stand and read back whole)
            # while the worker's own space stays his to wreck —
            # and everything remains contained to his tree, the
            # record intact, the host untouched.
            check("g-conf-selfdelete: worker's delete attempt is "
                  "contained to its tree and the stocked sources "
                  "stand (utilise-only), record intact",
                  not gone
                  and "Read-only file system" in res["stderr"]
                  and readback["rc"] == 0
                  and "ecb919025d4e5176" in readback["stdout"]
                  and state_alive and host_alive,
                  f"rm_stderr={res['stderr'][:80]!r} "
                  f"sources_gone={gone} "
                  f"readback_rc={readback['rc']} state={state_alive} "
                  f"host_sentinel={host_alive}")

    finally:
        for room in list(ROOMS):
            try:
                room.destroy(remove_tree=True)
            except Exception:
                pass
        stop_canary()
        shutil.rmtree(base, ignore_errors=True)
        leftovers = [p for p in Path("/tmp").glob("track-g-*")]
        check("cleanup: no leftover trees, mounts, or processes",
              not leftovers and not os.path.ismount(base),
              f"leftovers={leftovers}")

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"TRACK G SUITE: {len(RESULTS) - len(failed)} passed, "
          f"{len(failed)} failed of {len(RESULTS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
