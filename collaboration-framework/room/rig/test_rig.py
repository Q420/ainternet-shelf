#!/usr/bin/env python3
"""test_rig.py — Track B rig suite, correction round 2: build rooms,
witness them from the host side, run the in-room pre-flight, and assert
the walls — including the aggregate envelope Vane's examination
required (INDEX 438): a host-side warden over the pid namespace with a
two-threshold (sustained working / immediate catastrophic) rule, a
cumulative CPU budget, pressure-event recording, a sized-tmpfs storage
ceiling, per-room identities witnessed from actual kernel state,
recipe-derived mount assessment with deviant-room negative tests,
bounded output capture, and observed process-lifecycle accounting
(census-sampled — never a complete trace).

Correction round 2 (Vane's five points, INDEX 451) adds: the envelope
boundary DEFINED as the worker run — executions serialised by a
per-room lock, the CPU budget cumulative across the run's calls in a
state ledger; CPU accounting reconciled with an in-room reaper's exact
rusage and measured against short-lived CPU burners; and both
fail-open paths (storage mount failure, namespace discovery failure)
closed and negative-tested.

Checks (each prints PASS/FAIL):
  control        pre-flight detects reaches when run UNCONFINED
  stocking       the room tree matches its recorded stocking manifest
  supervisor     a long-lived room instance starts and its init is found
  mounts         full mountinfo; the recipe-derived assessment passes
                 for a properly built room (source identity, ro status,
                 propagation, every exposed mount accounted for)
  mounts-extra   NEGATIVE: a room with an undeclared bind is flagged
  mounts-rw      NEGATIVE: a room with a writable stock bind is flagged
  network        host witness: no interfaces but (down) loopback, no routes
  environment    host witness: launched env equals the declared manifest
  namespaces     host witness: mount/net/pid namespaces differ from host's
  identity       witness: the program's ACTUAL kernel credentials —
                 per-room uid/gid in all four positions, no groups, all
                 capability sets zero, NoNewPrivs set, seccomp state
                 captured (the host container's inherited profile)
  cross-room     two rooms, distinct uids: neither identity can read
                 the other's tree or signal the other's processes
  envelope-rec   the envelope in force (warden + tmpfs + rlimits, and
                 cgroup's unavailability) is recorded and consistent
                 between the room state and the host witness
  preflight      in-room: every sentinel reach fails; observations match
  persistence    writes survive across calls; deliverable lands on host
  persist-terms  the stated terms are the true ones: filesystem state
                 persists across calls; process/environment state does
                 not (a background process from call 1 is gone, an env
                 marker set in call 1 is absent in call 2)
  ward-mem       AGGREGATE memory: two processes, each under the
                 per-process limit, together over the working ceiling
                 for the sustain window — both die, termination recorded
  ward-spike     a legitimate spike over the working ceiling that
                 settles inside the sustain window SURVIVES, and the
                 excursion is recorded as a pressure event
  ward-fastspike fastest-possible allocation dies at the catastrophic
                 ceiling; the measured overshoot is printed (the
                 warden's demonstrated granularity, also in RIG-NOTES)
  ward-pids      AGGREGATE process count over the working ceiling for
                 the sustain window — killed, termination recorded
  ward-forkfast  fastest-possible forking dies at the catastrophic
                 process ceiling; measured overshoot printed
  ward-cpu       AGGREGATE cumulative CPU-seconds budget: parallel
                 spinners die when the budget is spent
  serialise      BOUNDARY: two concurrent run() calls on one room
                 never overlap inside the room (per-room lock)
  cpu-run        BOUNDARY: the CPU budget is cumulative across the
                 run's calls — call 2 dies at the RUN budget, call 3
                 is refused before execution, the ledger shows all
  cpu-shortlived ADVERSARIAL: 40 CPU burners each living ~25 ms of
                 CPU time (inside one census interval), reaped by
                 their parent — the charged accounting (reaper +
                 census) is measured against the workload's own
                 rusage ground truth
  storage-fail   NEGATIVE: a failed tmpfs mount fails creation
                 closed — RoomCreationError, a failed-precondition
                 record, no loadable/executable room, no tree
  ns-fail        NEGATIVE: namespace discovery failure fails the
                 execution closed — refused result, the gated command
                 provably never ran (no marker), nothing survives
  storage        the tree's sized tmpfs is a hard aggregate ceiling:
                 a fill attempt stops at it with ENOSPC
  output         stdout capture is bounded: 5 MB spew is counted in
                 full, truncated at the ceiling, and flagged
  lifecycle      OBSERVED lifecycle: a setsid-detached child is seen
                 born, recorded, and dead after the timeout sweep —
                 no namespace survivors
  cleanup        destroy kills the supervisor tree including a
                 setsid-detached process; tree removed; tmpfs unmounted

Offline only. Exit code is nonzero if any check fails.
"""

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
import host_witness

RESULTS = []
ROOMS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + (f" — {detail}" if detail else ""))


def mkroom(base, name, **kw):
    room = room_mod.create_room(base, name, **kw)
    ROOMS.append(room)
    return room


def start_canary():
    """A TCP listener on the host; returns (port, stop_fn)."""
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    srv.settimeout(0.5)
    port = srv.getsockname()[1]
    stopped = threading.Event()

    def loop():
        while not stopped.is_set():
            try:
                conn, _ = srv.accept()
                conn.close()
            except socket.timeout:
                pass
            except OSError:
                break

    threading.Thread(target=loop, daemon=True).start()
    return port, lambda: (stopped.set(), srv.close())


def host_primary_ip():
    try:
        out = subprocess.run(["hostname", "-I"], capture_output=True,
                             text=True, timeout=5).stdout.split()
        return out[0] if out else None
    except (OSError, subprocess.SubprocessError):
        return None


def self_seccomp():
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("Seccomp:"):
            return int(line.split()[1])
    return None


def as_uid(uid, code):
    """Run a python snippet as the given uid (host-side identity probe)."""
    return subprocess.run(
        ["setpriv", f"--reuid={uid}", f"--regid={uid}", "--clear-groups",
         sys.executable, "-c", code],
        capture_output=True, text=True, timeout=15, cwd="/")


# -- helper programs stocked into envelope-test rooms ----------------------
ALLOC = b"""
import sys, time
mb, hold = int(sys.argv[1]), float(sys.argv[2])
x = []
chunk = 8 * 1024 * 1024
for _ in range(mb * 1024 * 1024 // chunk):
    b = bytearray(chunk)
    for j in range(0, chunk, 4096):
        b[j] = 1
    x.append(b)
print(f"allocated {mb} MiB", flush=True)
time.sleep(hold)
"""
SPIKE = b"""
import sys, time
mb, hold = int(sys.argv[1]), float(sys.argv[2])
x = []
chunk = 8 * 1024 * 1024
for _ in range(mb * 1024 * 1024 // chunk):
    b = bytearray(chunk)
    for j in range(0, chunk, 4096):
        b[j] = 1
    x.append(b)
print("spiked", flush=True)
time.sleep(hold)
x.clear()
print("spike-released", flush=True)
"""
FASTALLOC = b"""
import time
x = []
chunk = 16 * 1024 * 1024
while True:
    b = bytearray(chunk)
    for j in range(0, chunk, 4096):
        b[j] = 1
    x.append(b)
"""
FORKSPAM = b"""
import os, sys, time
n = int(sys.argv[1])
for _ in range(n):
    if os.fork() == 0:
        time.sleep(60)
        os._exit(0)
print("forked", flush=True)
time.sleep(60)
"""
FORKFAST = b"""
import os, time
while True:
    if os.fork() == 0:
        time.sleep(60)
        os._exit(0)
"""
SPINNER = b"""
while True:
    pass
"""
BURN_FIXED = b"""
import sys, time
target = float(sys.argv[1])
t0 = time.process_time()
while time.process_time() - t0 < target:
    pass
print("burned", flush=True)
"""
BURNERS = b"""
import os, resource, time
N, PER = 40, 0.025
for _ in range(N):
    c = os.fork()
    if c == 0:
        t0 = time.process_time()
        while time.process_time() - t0 < PER:
            pass
        os._exit(0)
    os.waitpid(c, 0)
self_ru = resource.getrusage(resource.RUSAGE_SELF)
child_ru = resource.getrusage(resource.RUSAGE_CHILDREN)
true_total = (self_ru.ru_utime + self_ru.ru_stime
              + child_ru.ru_utime + child_ru.ru_stime)
print(f"TRUE {true_total:.3f}", flush=True)
"""
SPEW = b"""
import os, sys
n = int(sys.argv[1])
chunk = b"x" * 65536
while n > 0:
    part = chunk[:min(n, len(chunk))]
    os.write(1, part)
    n -= len(part)
"""
WRITER = b"""
import sys
path = sys.argv[1]
total = 0
chunk = b"z" * 1024 * 1024
try:
    with open(path, "wb") as fh:
        while total < 64 * 1024 * 1024:
            fh.write(chunk)
            total += len(chunk)
    print(f"WROTE {total} FULL")
except OSError as exc:
    print(f"WROTE {total} ENOSPC errno={exc.errno}")
"""


def main():
    base = Path(tempfile.mkdtemp(prefix="room-rig-test-", dir="/tmp"))
    os.chmod(base, 0o755)   # so per-room uids can reach their own trees
    canary_port, stop_canary = start_canary()
    host_ip = host_primary_ip()
    try:
        # --- sentinels -------------------------------------------------
        host_sentinel = base / "host-sentinel.txt"
        host_sentinel.write_text("HOST-ONLY\n")
        sibling_tree = base / "sibling-tree"
        sibling_tree.mkdir()
        sibling_sentinel = sibling_tree / "sentinel.txt"
        sibling_sentinel.write_text("SIBLING-ONLY\n")

        pf_args = ["--host-sentinel", str(host_sentinel),
                   "--sibling-sentinel", str(sibling_sentinel),
                   "--canary", f"127.0.0.1:{canary_port}"]
        if host_ip:
            pf_args += ["--canary", f"{host_ip}:{canary_port}"]
        pf_args += ["--dns-name", "example.com"]

        # --- control: pre-flight must DETECT reaches when unconfined ---
        ctl = subprocess.run(
            [sys.executable,
             str(Path(__file__).parent / "preflight.py")] + pf_args,
            capture_output=True, text=True, timeout=30)
        try:
            ctl_rep = json.loads(ctl.stdout)
            ctl_ok = (ctl_rep["room_valid"] is False
                      and ctl_rep["reaches"]["host_sentinel_read"]["reached"]
                      and ctl_rep["reaches"]["canary_connects"][0]["reached"])
            ctl_detail = "unconfined run reports reaches succeeding"
        except (ValueError, KeyError) as exc:
            ctl_ok, ctl_detail = False, f"control output unparsable: {exc}"
        check("control: pre-flight detects reaches when unconfined",
              ctl_ok, ctl_detail)

        # --- stocking ---------------------------------------------------
        stock = {"case/source.txt": b"the case source material\n"}
        alpha = mkroom(base, "alpha", stock=stock)
        tree_file = alpha.tree / "work" / "case" / "source.txt"
        expect = hashlib.sha256(stock["case/source.txt"]).hexdigest()
        check("stocking: tree matches recorded manifest",
              tree_file.exists()
              and alpha.stock_manifest.get("case/source.txt") == expect
              and alpha.state_path.exists(),
              f"tree={alpha.tree}")

        # --- supervisor + host witness ---------------------------------
        info = alpha.start_supervisor()
        check("supervisor: room instance starts, init found",
              info.get("room_init_pid") is not None,
              f"launcher={info.get('launcher_pid')} "
              f"init={info.get('room_init_pid')}")
        wit = host_witness.witness(info["launcher_pid"])

        # --- mounts: full parse + recipe-derived assessment -------------
        full_fields = all(
            {"mount_id", "parent_id", "major_minor", "root",
             "mount_point", "options", "optional_fields", "fs_type",
             "source", "super_options"} <= set(m) for m in wit["mounts"])
        assess = host_witness.assess_mounts(
            wit, room_mod.standard_recipe(), str(alpha.tree))
        check("mounts: full mountinfo; recipe-derived assessment "
              "passes for a proper room",
              full_fields and assess["ok"],
              f"unexpected={assess['unexpected']} "
              f"violations={assess['violations']}")

        # --- mounts NEGATIVE: undeclared extra bind ----------------------
        sneaky = mkroom(base, "sneaky",
                        extra_binds=[(str(base), "/extra", "ro")])
        s_info = sneaky.start_supervisor()
        s_wit = host_witness.witness(s_info["launcher_pid"])
        s_assess = host_witness.assess_mounts(
            s_wit, room_mod.standard_recipe(), str(sneaky.tree))
        check("mounts-negative: an undeclared extra bind is flagged "
              "by name",
              not s_assess["ok"] and "/extra" in s_assess["unexpected"],
              f"unexpected={s_assess['unexpected']}")
        sneaky.destroy(remove_tree=True)

        # --- mounts NEGATIVE: stock bind made writable -------------------
        loose = mkroom(base, "loose", stock_rw=True)
        l_info = loose.start_supervisor()
        l_wit = host_witness.witness(l_info["launcher_pid"])
        l_assess = host_witness.assess_mounts(
            l_wit, room_mod.standard_recipe(), str(loose.tree))
        check("mounts-negative: a writable stock bind is flagged",
              not l_assess["ok"]
              and any("/usr" in v and "read-only" in v
                      for v in l_assess["violations"]),
              f"violations={l_assess['violations']}")
        loose.destroy(remove_tree=True)

        net = wit["network"]
        check("network: no interfaces but loopback, no routes",
              net["interfaces"] == ["lo"] and net["routes"] == [],
              f"interfaces={net['interfaces']} routes={net['routes']}")

        declared = wit["declared_environment_from_cmdline"]
        prog_env = wit["environment_of_room_program"]
        env_ok = declared == alpha.env_manifest and (
            prog_env is None
            or set(prog_env) <= set(declared) | {"PWD"})
        check("environment: launched env equals the declared manifest "
              "(witnessed from the launcher cmdline)",
              env_ok,
              f"declared={declared} program_env="
              f"{'unreadable (non-dumpable)' if prog_env is None else sorted(prog_env)}")

        nd = wit["namespace_differs_from_witness"]
        check("namespaces: mount/net/pid differ from the host's",
              nd.get("mnt") and nd.get("net") and nd.get("pid"),
              f"differs={nd}")

        # --- identity: ACTUAL kernel state, per-room uid -----------------
        ident = wit["identity_of_room_program"] or {}
        zero = "0000000000000000"
        ident_ok = (
            ident.get("Uid") == [alpha.room_uid] * 4
            and ident.get("Gid") == [alpha.room_gid] * 4
            and ident.get("Groups") == []
            and ident.get("CapEff") == zero
            and ident.get("CapPrm") == zero
            and ident.get("CapBnd") == zero
            and ident.get("CapAmb") == zero
            and ident.get("NoNewPrivs") == 1
            and ident.get("Seccomp") == self_seccomp())
        check("identity: actual kernel credentials — per-room uid, no "
              "groups, zero capabilities, NoNewPrivs, seccomp captured",
              ident_ok,
              f"uid={alpha.room_uid} ident={ident}")

        # --- cross-room identity ------------------------------------------
        beta = mkroom(base, "beta",
                      stock={"case/source.txt": b"beta material\n"})
        b_info = beta.start_supervisor()
        b_wit = host_witness.witness(b_info["launcher_pid"])
        beta_prog = b_wit["room_program_pid"]
        beta_file = str(beta.tree / "work" / "case" / "source.txt")
        read_beta = f"open({beta_file!r}).read()"
        own_read = as_uid(beta.room_uid, read_beta)
        cross_read = as_uid(alpha.room_uid, read_beta)
        cross_signal = as_uid(
            alpha.room_uid,
            "import os, sys\n"
            "try:\n"
            f"    os.kill({beta_prog}, 0)\n"
            "    sys.exit(0)\n"
            "except PermissionError:\n"
            "    sys.exit(3)\n")
        tree_stat = os.stat(beta.tree)
        cross_ok = (
            alpha.room_uid != beta.room_uid
            and tree_stat.st_uid == beta.room_uid
            and (tree_stat.st_mode & 0o777) == 0o700
            and own_read.returncode == 0
            and cross_read.returncode != 0
            and cross_signal.returncode == 3)
        check("cross-room: distinct uids; room A's identity cannot "
              "read room B's tree or signal its processes",
              cross_ok,
              f"uidA={alpha.room_uid} uidB={beta.room_uid} "
              f"own_read_rc={own_read.returncode} "
              f"cross_read_rc={cross_read.returncode} "
              f"cross_signal_rc={cross_signal.returncode}")

        # --- envelope recorded ---------------------------------------------
        state = json.loads(alpha.state_path.read_text())
        env_rec = state["envelope"]
        agg = env_rec.get("aggregate", {})
        env_ok = (
            "warden" in agg.get("mechanism", "")
            and agg.get("memory", {}).get("working_ceiling_bytes")
                == alpha.limits["aggregate_mem_bytes"]
            and env_rec.get("storage", {}).get("mechanism")
                == "tmpfs-sized"
            and env_rec.get("cgroup", {}).get("available") is False
            and "controllers" in env_rec.get("cgroup", {}).get("reason", "")
            and bool(wit["cgroup"].get("entries")))
        check("envelope: warden aggregate + tmpfs storage recorded; "
              "cgroup unavailability recorded and consistent",
              env_ok,
              f"mechanism={env_rec.get('mechanism', '')[:70]}...")

        # --- in-room pre-flight -----------------------------------------
        res = alpha.run(["/usr/bin/python3", "/room/rig/preflight.py"]
                        + pf_args, timeout=30)
        try:
            rep = json.loads(res["stdout"])
            reaches = rep["reaches"]
            all_failed = (not reaches["host_sentinel_read"]["reached"]
                          and not reaches["sibling_sentinel_read"]["reached"]
                          and not reaches["dns_resolution"]["reached"]
                          and not reaches["pid1_environ_exposure"]["reached"]
                          and all(not c["reached"]
                                  for c in reaches["canary_connects"]))
            obs = rep["observations"]
            pf_ok = (rep["room_valid"] and all_failed
                     and set(obs["environment"])
                     <= {"PATH", "ROOM_ID", "PWD", "LC_CTYPE"}
                     and len(obs["visible_processes"]) <= 4
                     and set(obs["top_level_listing"])
                     <= {"bin", "dev", "lib", "lib64", "proc", "room",
                         "sbin", "usr"})
            pf_detail = (f"valid={rep['room_valid']} "
                         f"procs={len(obs['visible_processes'])} "
                         f"top={obs['top_level_listing']}")
        except (ValueError, KeyError) as exc:
            pf_ok, pf_detail = False, (f"unparsable preflight output: "
                                       f"{exc}; rc={res['rc']} "
                                       f"stderr={res['stderr'][:200]}")
        check("preflight: every sentinel reach fails inside the room",
              pf_ok, pf_detail)

        # --- persistence (round 1 form) ------------------------------------
        w = alpha.run(["/bin/sh", "-c",
                       "echo rig-persist > /room/work/persist.txt && "
                       "echo brief-body > /room/deliverable/brief.md"],
                      timeout=30)
        r = alpha.run(["/bin/sh", "-c", "cat /room/work/persist.txt"],
                      timeout=30)
        deliverable = alpha.tree / "deliverable" / "brief.md"
        check("persistence: writes survive across calls; deliverable "
              "lands on the host tree",
              w["rc"] == 0 and r["stdout"].strip() == "rig-persist"
              and deliverable.exists()
              and deliverable.read_text().strip() == "brief-body",
              f"readback={r['stdout'].strip()!r}")

        # --- persistence terms, evidenced ----------------------------------
        terms = state.get("persistence", {})
        alpha.run(["/usr/bin/python3", "-c",
                   "import os\n"
                   "os.environ['RIG_MARKER'] = 'set-in-call-1'\n"
                   "open('/room/work/envmark.txt', 'w')"
                   ".write('file-was-here')\n"],
                  timeout=30)
        bg = alpha.run(["/bin/sh", "-c", "sleep 315 & echo bg-launched"],
                       timeout=30)
        time.sleep(0.3)
        bg_gone = room_mod.room_processes(bg["room_init_pid"]) == []
        nxt = alpha.run(["/usr/bin/python3", "-c",
                         "import os\n"
                         "print('MARKER', os.environ.get('RIG_MARKER'))\n"
                         "print('FILE', open('/room/work/envmark.txt')"
                         ".read())\n"],
                        timeout=30)
        terms_ok = (
            "persists across calls" in terms.get("filesystem_state", "")
            and "does not persist" in terms.get("process_state", "")
            and "MARKER None" in nxt["stdout"]
            and "file-was-here" in nxt["stdout"]
            and bg_gone)
        check("persist-terms: filesystem persists across calls; "
              "process/environment state does not",
              terms_ok,
              f"call2={nxt['stdout'].strip()!r} bg_gone={bg_gone}")

        # --- warden: AGGREGATE memory, sustained rule ----------------------
        memrun = mkroom(
            base, "memrun",
            stock={"helpers/alloc.py": ALLOC},
            limits={"mem_bytes": 512 << 20,
                    "aggregate_mem_bytes": 192 << 20,
                    "sustain_seconds": 0.5})
        m = memrun.run(
            ["/bin/sh", "-c",
             "/usr/bin/python3 /room/work/helpers/alloc.py 120 30 & "
             "/usr/bin/python3 /room/work/helpers/alloc.py 120 30 & wait"],
            timeout=30)
        term = m["envelope_termination"] or {}
        m_state = json.loads(memrun.state_path.read_text())
        m_recorded = (m_state.get("executions") or [{}])[-1].get(
            "envelope_termination") or {}
        check("ward-mem: two processes under the per-process limit but "
              "over the aggregate ceiling are both killed (sustained)",
              term.get("resource") == "memory"
              and term.get("rule") == "sustained"
              and term.get("measured", 0) >= 192 << 20
              and m["survivors"] == []
              and m_recorded.get("resource") == "memory",
              f"term={term}")
        memrun.destroy(remove_tree=True)

        # --- warden: a legitimate spike SURVIVES ----------------------------
        spike = mkroom(
            base, "spike", stock={"helpers/spike.py": SPIKE},
            limits={"aggregate_mem_bytes": 192 << 20,
                    "sustain_seconds": 1.0})
        s = spike.run(["/usr/bin/python3",
                       "/room/work/helpers/spike.py", "256", "0.3"],
                      timeout=30)
        pressures = [p for p in s["pressure_events"]
                     if p["resource"] == "memory"]
        s_state = json.loads(spike.state_path.read_text())
        check("ward-spike: spike over the working ceiling that settles "
              "inside the sustain window survives; pressure recorded",
              s["rc"] == 0 and "spike-released" in s["stdout"]
              and s["envelope_termination"] is None
              and pressures
              and pressures[0]["peak"] >= 192 << 20
              and pressures[0]["recovered"] is True
              and bool(s_state.get("pressure_events")),
              f"rc={s['rc']} pressures={pressures}")
        spike.destroy(remove_tree=True)

        # --- warden: fastest spike dies at the catastrophic ceiling --------
        fastspike = mkroom(
            base, "fastspike", stock={"helpers/fastalloc.py": FASTALLOC},
            limits={"mem_bytes": 2 << 30,
                    "aggregate_mem_bytes": 192 << 20,
                    "sustain_seconds": 1.0})
        f = fastspike.run(["/usr/bin/python3",
                           "/room/work/helpers/fastalloc.py"], timeout=30)
        fterm = f["envelope_termination"] or {}
        cat_ceiling = 2 * (192 << 20)
        overshoot = f["peak_aggregate_rss_bytes"] - cat_ceiling
        check("ward-fastspike: fastest allocation dies at the "
              "catastrophic ceiling; overshoot measured",
              fterm.get("resource") == "memory"
              and fterm.get("rule") == "catastrophic"
              and f["peak_aggregate_rss_bytes"] >= cat_ceiling
              and f["survivors"] == [],
              f"peak={f['peak_aggregate_rss_bytes'] / 2**20:.0f} MiB vs "
              f"catastrophic {cat_ceiling / 2**20:.0f} MiB — measured "
              f"overshoot {overshoot / 2**20:.1f} MiB at 50 ms polling")
        fastspike.destroy(remove_tree=True)

        # --- warden: AGGREGATE process count, sustained rule ----------------
        pidsrun = mkroom(
            base, "pidsrun", stock={"helpers/forkspam.py": FORKSPAM},
            limits={"aggregate_pids_max": 24,
                    "aggregate_pids_catastrophic_multiple": 4,
                    "sustain_seconds": 0.5, "pids_max": 512})
        p = pidsrun.run(["/usr/bin/python3",
                         "/room/work/helpers/forkspam.py", "48"],
                        timeout=30)
        pterm = p["envelope_termination"] or {}
        check("ward-pids: process count over the working ceiling for "
              "the sustain window is killed (sustained)",
              pterm.get("resource") == "pids"
              and pterm.get("rule") == "sustained"
              and pterm.get("measured", 0) > 24
              and p["survivors"] == [],
              f"term={pterm}")
        pidsrun.destroy(remove_tree=True)

        # --- warden: fastest forking dies at the catastrophic ceiling -------
        forkfast = mkroom(
            base, "forkfast", stock={"helpers/forkfast.py": FORKFAST},
            limits={"aggregate_pids_max": 24,
                    "aggregate_pids_catastrophic_multiple": 3,
                    "aggregate_mem_bytes": 4 << 30,
                    "pids_max": 4096, "sustain_seconds": 1.0})
        ff = forkfast.run(["/usr/bin/python3",
                           "/room/work/helpers/forkfast.py"], timeout=30)
        ffterm = ff["envelope_termination"] or {}
        pid_cat = 72
        check("ward-forkfast: fastest forking dies at the catastrophic "
              "process ceiling; overshoot measured",
              ffterm.get("resource") == "pids"
              and ffterm.get("rule") == "catastrophic"
              and ff["peak_process_count"] >= pid_cat
              and ff["survivors"] == [],
              f"peak_count={ff['peak_process_count']} vs catastrophic "
              f"{pid_cat} — measured overshoot "
              f"{ff['peak_process_count'] - pid_cat} processes")
        forkfast.destroy(remove_tree=True)

        # --- warden: AGGREGATE cumulative CPU budget -------------------------
        cpurun = mkroom(
            base, "cpurun", stock={"helpers/spinner.py": SPINNER},
            limits={"aggregate_cpu_seconds": 3.0})
        t_cpu = time.time()
        c = cpurun.run(
            ["/bin/sh", "-c",
             "/usr/bin/python3 /room/work/helpers/spinner.py & "
             "/usr/bin/python3 /room/work/helpers/spinner.py & "
             "/usr/bin/python3 /room/work/helpers/spinner.py & wait"],
            timeout=30)
        cpu_wall = time.time() - t_cpu
        cterm = c["envelope_termination"] or {}
        check("ward-cpu: parallel spinners die when the cumulative "
              "CPU-seconds budget is spent",
              cterm.get("resource") == "cpu"
              and cterm.get("measured", 0) >= 3.0
              and cpu_wall < 15 and c["survivors"] == [],
              f"term={cterm} wall={cpu_wall:.1f}s")
        cpurun.destroy(remove_tree=True)

        # --- boundary: executions are serialised per room -------------------
        serial = mkroom(base, "serial")
        order_file = serial.tree / "work" / "order.txt"
        serial_results = {}

        def serial_call(tag):
            serial_results[tag] = serial.run(
                ["/bin/sh", "-c",
                 f"echo {tag}-begin >> /room/work/order.txt; "
                 "sleep 1.5; "
                 f"echo {tag}-end >> /room/work/order.txt"],
                timeout=30)

        threads = [threading.Thread(target=serial_call, args=(t,))
                   for t in ("A", "B")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        order = order_file.read_text().split()
        serialised_orders = (
            ["A-begin", "A-end", "B-begin", "B-end"],
            ["B-begin", "B-end", "A-begin", "A-end"])
        check("serialise: two concurrent run() calls never overlap "
              "inside the room (per-room execution lock)",
              order in serialised_orders
              and all(r["rc"] == 0 for r in serial_results.values()),
              f"order={order}")
        serial.destroy(remove_tree=True)

        # --- boundary: the CPU budget is cumulative across the run ----------
        runburn = mkroom(base, "runburn",
                         stock={"helpers/burn.py": BURN_FIXED},
                         limits={"aggregate_cpu_seconds": 2.0})
        rb1 = runburn.run(["/usr/bin/python3",
                           "/room/work/helpers/burn.py", "1.2"],
                          timeout=30)
        rb2 = runburn.run(["/usr/bin/python3",
                           "/room/work/helpers/burn.py", "1.2"],
                          timeout=30)
        rb3 = runburn.run(["/bin/sh", "-c",
                           "echo ran > /room/work/should-not-exist.txt"],
                          timeout=30)
        rb_term = rb2["envelope_termination"] or {}
        ledger = json.loads(runburn.state_path.read_text())["cpu_ledger"]
        check("cpu-run: budget is cumulative across the run's calls — "
              "call 2 dies at the run budget, call 3 refused, ledger "
              "shows all three",
              rb1["rc"] == 0 and not rb1["refused"]
              and rb_term.get("resource") == "cpu"
              and rb_term.get("boundary") == "per worker run"
              and rb2["survivors"] == []
              and rb3["refused"]
              and rb3["refusal_kind"] == "run-cpu-budget-spent"
              and not (runburn.tree / "work"
                       / "should-not-exist.txt").exists()
              and ledger["consumed_seconds"] >= 2.0
              and len(ledger["calls"]) == 3
              and ledger["calls"][2]["refused"],
              f"charged1={rb1['aggregate_cpu_seconds']} "
              f"term2={rb_term.get('measured')} "
              f"ledger={ledger['consumed_seconds']}s over "
              f"{len(ledger['calls'])} calls")
        runburn.destroy(remove_tree=True)

        # --- adversarial: short-lived CPU burners vs the accounting ----------
        burners = mkroom(base, "burners",
                         stock={"helpers/burners.py": BURNERS})
        bn = burners.run(["/usr/bin/python3",
                          "/room/work/helpers/burners.py"], timeout=60)
        true_lines = [l for l in bn["stdout"].splitlines()
                      if l.startswith("TRUE")]
        true_cpu = float(true_lines[0].split()[1]) if true_lines else 0.0
        acct = bn["cpu_accounting"] or {}
        check("cpu-shortlived: 40 burners of ~25 ms CPU each are "
              "accounted against rusage ground truth",
              bn["rc"] == 0 and true_cpu > 0.8
              and acct.get("reaper_seconds") is not None
              and acct["reaper_seconds"] >= 0.95 * true_cpu
              and acct["census_seconds"] >= 0.90 * true_cpu
              and acct["charged_seconds"] >= 0.95 * true_cpu,
              f"true={true_cpu:.3f}s reaper="
              f"{acct.get('reaper_seconds')} "
              f"({(acct.get('reaper_seconds') or 0) / max(true_cpu, 1e-9):.1%}) "
              f"census={acct.get('census_seconds')} "
              f"({acct.get('census_seconds', 0) / max(true_cpu, 1e-9):.1%}) "
              f"charged={acct.get('charged_seconds')}")
        burners.destroy(remove_tree=True)

        # --- NEGATIVE: storage mount failure fails creation closed ------------
        raised = None
        try:
            room_mod.create_room(base, "badstore",
                                 limits={"storage_bytes": -1})
        except room_mod.RoomCreationError as exc:
            raised = exc
        bad_rec_path = base / "badstore.room.json"
        bad_rec = (json.loads(bad_rec_path.read_text())
                   if bad_rec_path.exists() else {})
        load_raised = False
        try:
            room_mod.load_room(base, "badstore")
        except room_mod.RoomCreationError:
            load_raised = True
        check("storage-fail: a failed tmpfs mount fails creation "
              "closed — error raised, failure recorded, no executable "
              "room, no tree left",
              raised is not None
              and bad_rec.get("failed") is True
              and bad_rec.get("executable") is False
              and bad_rec.get("failed_precondition")
                  == "storage-tmpfs-mount"
              and "tmpfs" in bad_rec.get("reason", "")
              and load_raised
              and not (base / "badstore-tree").exists()
              and not os.path.ismount(base / "badstore-tree"),
              f"record={ {k: bad_rec.get(k) for k in ('failed', 'executable', 'failed_precondition')} }")

        # --- NEGATIVE: namespace discovery failure fails execution closed -----
        nsfail = mkroom(base, "nsfail")
        # simulate the discovery seam reporting failure while a real
        # launch is alive behind its closed start gate
        nsfail._discover_ns = lambda proc, deadline_s=5.0: (None, None)
        marker = nsfail.tree / "work" / "marker.txt"
        nf = nsfail.run(["/bin/sh", "-c",
                         "echo ran > /room/work/marker.txt"], timeout=30)
        gate_leftovers = list((nsfail.tree / "rig").glob(".start-gate-*"))
        check("ns-fail: discovery failure refuses the execution — "
              "the gated command never ran, nothing survives",
              nf["refused"]
              and nf["failed_precondition"] == "namespace-discovery"
              and nf["warden_engaged"] is False
              and not marker.exists()
              and nf["survivors"] == []
              and not gate_leftovers
              and not room_mod.pid_alive(nf["launcher_pid"]),
              f"reason={nf['refusal_reason'][:80]}...")
        nsfail.destroy(remove_tree=True)

        # --- storage: sized tmpfs is a hard aggregate ceiling ----------------
        stor = mkroom(base, "storage", stock={"helpers/writer.py": WRITER},
                      limits={"storage_bytes": 16 << 20})
        st = stor.run(["/usr/bin/python3",
                       "/room/work/helpers/writer.py",
                       "/room/scratch/big.bin"], timeout=60)
        big = stor.tree / "scratch" / "big.bin"
        vfs = os.statvfs(stor.tree)
        total_bytes = vfs.f_blocks * vfs.f_frsize
        check("storage: fill attempt stops at the tmpfs ceiling "
              "with ENOSPC",
              "ENOSPC" in st["stdout"]
              and big.exists() and big.stat().st_size <= 16 << 20
              and abs(total_bytes - (16 << 20)) < (1 << 20)
              and stor.storage.get("mechanism") == "tmpfs-sized",
              f"out={st['stdout'].strip()!r} file="
              f"{big.stat().st_size if big.exists() else None} "
              f"fs_total={total_bytes}")
        stor.destroy(remove_tree=True)

        # --- bounded output ---------------------------------------------------
        spew = mkroom(base, "spew", stock={"helpers/spew.py": SPEW})
        sp = spew.run(["/usr/bin/python3",
                       "/room/work/helpers/spew.py", "5000000"],
                      timeout=30)
        check("output: 5 MB spew is counted in full, retained only "
              "to the ceiling, and flagged truncated",
              sp["stdout_bytes"] == 5000000
              and sp["stdout_truncated"] is True
              and len(sp["stdout"].encode()) <= 1 << 20,
              f"total={sp['stdout_bytes']} retained="
              f"{len(sp['stdout'].encode())} "
              f"truncated={sp['stdout_truncated']}")
        spew.destroy(remove_tree=True)

        # --- lifecycle: setsid escapee is accounted and killed -----------------
        life = mkroom(base, "lifecycle")
        lf = life.run(["/bin/sh", "-c",
                       "setsid /bin/sleep 313 & exec /bin/sleep 300"],
                      timeout=3)
        births = [e for e in lf["lifecycle"] if e["event"] == "birth"]
        deaths = {e["pid"] for e in lf["lifecycle"]
                  if e["event"] == "death"}
        detached = [b for b in births
                    if b["comm"] == "sleep" and b["session"] == b["pid"]]
        check("lifecycle (observed): setsid-detached child is seen "
              "born, recorded, and dead after the timeout sweep; "
              "no survivors",
              lf["timed_out"] and detached
              and all(b["pid"] in deaths for b in detached)
              and lf["survivors"] == []
              and room_mod.room_processes(lf["room_init_pid"]) == [],
              f"detached={detached} survivors={lf['survivors']}")
        life.destroy(remove_tree=True)

        # --- cleanup: destroy kills everything, incl. setsid-detached ----------
        doomed = mkroom(base, "doomed")
        dsup = doomed.start_supervisor(
            inner_argv=("/bin/sh", "-c",
                        "setsid sleep 314 & exec sleep 314"))
        d_init = dsup["room_init_pid"]
        rep_destroy = doomed.destroy(remove_tree=True)
        check("cleanup: destroy kills the whole tree incl. detached "
              "processes; tree removed; tmpfs unmounted",
              rep_destroy["survivors"] == []
              and room_mod.room_processes(d_init) == []
              and rep_destroy["tree_removed"]
              and not doomed.tree.exists()
              and not os.path.ismount(doomed.tree),
              f"survivors={rep_destroy['survivors']}")
    finally:
        stop_canary()
        for rm in ROOMS:
            try:
                rm.destroy(remove_tree=True)
            except Exception:
                pass
        shutil.rmtree(base, ignore_errors=True)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"RIG SUITE: {passed} passed, {len(RESULTS) - passed} failed "
          f"of {len(RESULTS)}")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
