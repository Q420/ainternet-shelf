#!/usr/bin/env python3
"""test_rig.py — Track B rig suite: build a room, witness it from the
host side, run the in-room pre-flight, and assert the walls.

Checks (each prints PASS/FAIL):
  control      pre-flight detects reaches when run UNCONFINED on the
               host (a rig that cannot detect a reach proves nothing)
  stocking     the room tree matches its recorded stocking manifest
  supervisor   a long-lived room instance starts and its init is found
  mounts       host witness: only the room tree + declared stock binds
               are mounted; no other host path is exposed
  network      host witness: no interfaces but (down) loopback, no routes
  environment  host witness: the room init's launched environment is
               exactly the declared set — nothing inherited, no secrets
  namespaces   host witness: mount/net/pid namespaces differ from host's
  envelope     the resource envelope in force is recorded and consistent
               between the room state and the host witness
  preflight    in-room: every sentinel reach fails; observations match
               the declared environment, process and filesystem shape
  persistence  a file written by one in-room call is read by a second;
               a deliverable written in-room is present on the host tree
  containment  a memory hog in a small room dies against its limit while
               the host and another room keep working
  cleanup      after destroy, no room process survives and (with
               --remove-tree) the tree is gone

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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import room as room_mod
import host_witness

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}"
          + (f" — {detail}" if detail else ""))


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


def main():
    base = Path(tempfile.mkdtemp(prefix="room-rig-test-", dir="/tmp"))
    canary_port, stop_canary = start_canary()
    host_ip = host_primary_ip()
    room1 = room2 = None
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
        room1 = room_mod.create_room(base, "alpha", stock=stock)
        tree_file = room1.tree / "work" / "case" / "source.txt"
        expect = hashlib.sha256(stock["case/source.txt"]).hexdigest()
        check("stocking: tree matches recorded manifest",
              tree_file.exists()
              and room1.stock_manifest.get("case/source.txt") == expect
              and room1.state_path.exists(),
              f"tree={room1.tree}")

        # --- supervisor + host witness ---------------------------------
        info = room1.start_supervisor()
        check("supervisor: room instance starts, init found",
              info.get("room_init_pid") is not None,
              f"launcher={info.get('launcher_pid')} "
              f"init={info.get('room_init_pid')}")
        wit = host_witness.witness(info["launcher_pid"])

        points = {m["mount_point"] for m in wit["mounts"]}
        # bubblewrap's minimal /dev is a set of individual device-node
        # mounts under /dev — those are declared stock, not leaks
        allowed_points = {"/", "/proc", "/dev", "/room"} \
            | set(room_mod.STOCK_BINDS)
        unexpected = [p for p in points
                      if p not in allowed_points
                      and not p.startswith("/dev/")]
        leaked = [m for m in wit["mounts"]
                  if m["root"] and str(base) in m["root"]
                  and not (m["mount_point"] == "/room"
                           and m["root"] == str(room1.tree))]
        check("mounts: only room tree + stock binds, no host paths",
              "/room" in points
              and set(room_mod.STOCK_BINDS) <= points
              and not unexpected
              and not leaked,
              f"points={sorted(points)} unexpected={unexpected} "
              f"leaked={leaked}")

        net = wit["network"]
        check("network: no interfaces but loopback, no routes",
              net["interfaces"] == ["lo"] and net["routes"] == [],
              f"interfaces={net['interfaces']} routes={net['routes']}")

        # The room program is non-dumpable after its privilege drop, so
        # its /proc environ is closed even to the host (see witness
        # note). The environment wall is therefore proven from the
        # witnessed construction: the launcher cmdline's --setenv pairs
        # must equal the declared manifest exactly — and if the program
        # env IS readable, it must match too. The in-room pre-flight
        # corroborates arrival from inside (checked below).
        declared = wit["declared_environment_from_cmdline"]
        prog_env = wit["environment_of_room_program"]
        env_ok = declared == room1.env_manifest and (
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

        env_mech = room1.envelope["mechanism"]
        if env_mech == "cgroup-v2":
            lim = wit["cgroup"]["limits"]
            env_ok = lim.get("memory.max") == str(room1.limits["mem_bytes"])
            env_detail = f"cgroup limits witnessed: {lim}"
        else:
            env_ok = (bool(wit["cgroup"].get("entries"))
                      and bool(room1.envelope.get(
                          "cgroup_unavailable_reason")))
            env_detail = ("cgroup envelope unavailable on this host; "
                          "rlimit fallback recorded: "
                          + room1.envelope["cgroup_unavailable_reason"][:80]
                          + "...")
        check("envelope: mechanism recorded and consistent with witness",
              env_ok, env_detail)

        # --- in-room pre-flight -----------------------------------------
        res = room1.run(["/usr/bin/python3", "/room/rig/preflight.py"]
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

        # --- persistence -------------------------------------------------
        w = room1.run(["/bin/sh", "-c",
                       "echo rig-persist > /room/work/persist.txt && "
                       "echo brief-body > /room/deliverable/brief.md"],
                      timeout=30)
        r = room1.run(["/bin/sh", "-c", "cat /room/work/persist.txt"],
                      timeout=30)
        deliverable = room1.tree / "deliverable" / "brief.md"
        check("persistence: writes survive across calls; deliverable "
              "lands on the host tree",
              w["rc"] == 0 and r["stdout"].strip() == "rig-persist"
              and deliverable.exists()
              and deliverable.read_text().strip() == "brief-body",
              f"readback={r['stdout'].strip()!r}")

        # --- envelope containment ---------------------------------------
        room2 = room_mod.create_room(
            base, "tiny", limits={"mem_bytes": 256 << 20})
        hog = ("x = []\n"
               "try:\n"
               "    while True:\n"
               "        x.append(bytearray(16 * 1024 * 1024))\n"
               "except MemoryError:\n"
               "    print('contained: MemoryError')\n")
        h = room2.run(["/usr/bin/python3", "-c", hog], timeout=60)
        after = room1.run(["/bin/sh", "-c", "echo still-ok"], timeout=30)
        contained = (h["rc"] != 0 or "contained" in h["stdout"]) \
            and after["stdout"].strip() == "still-ok"
        check("containment: memory hog dies at its limit; host and "
              "other room unaffected",
              contained,
              f"hog rc={h['rc']} out={h['stdout'].strip()[:60]!r} "
              f"err={h['stderr'].strip()[-60:]!r}")

        # --- cleanup ------------------------------------------------------
        sup = room2.start_supervisor(
            inner_argv=("/bin/sh", "-c", "sleep 300 & exec sleep 300"))
        tree_pids = host_witness.tree_of(sup["launcher_pid"])
        rep_destroy = room2.destroy(remove_tree=True)
        gone = all(not room_mod.pid_alive(p) for p in tree_pids)
        check("cleanup: destroy kills the whole tree; tree removed",
              rep_destroy["survivors"] == [] and gone
              and rep_destroy["tree_removed"]
              and not room2.tree.exists(),
              f"tree pids={tree_pids} survivors={rep_destroy['survivors']}")
    finally:
        stop_canary()
        for rm in (room1, room2):
            if rm is not None:
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
