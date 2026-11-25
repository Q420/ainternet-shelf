#!/usr/bin/env python3
"""stock_demo.py — Track C stocking for the live demonstration.

Builds the demonstration room exactly as DEMONSTRATION-PREPARATION-
2026-11-24.md §1 specifies, and proves it with the paper's stock-
verification smoke set before any worker is admitted:

  * the case materials are the first-worker assignment's released
    source set — verified twice over before anything is stocked:
    the source manifest's canonical-JSON hash must equal the
    released source-set identity (EXPECTED_MANIFEST_HASH, the
    identity the probed1 run staged and sealed), and every staged
    file must hash to its manifest entry. A file or hash that
    cannot be verified stops the stocking; nothing is improvised.
  * the room is created with the paper §1.4 envelope declared
    (DEMO_LIMITS below), the three sources at their in-room paths
    under work/sources/, the rig's standard runtime stock, and the
    deliverable destination at scratch/brief.md.
  * the smoke set then runs INSIDE the room: the shell runs;
    python3 runs; each source is read at its in-room path and its
    in-room SHA-256 matches the manifest; a file is written to and
    read back from scratch/; the deliverable path is written (the
    probe is removed host-side afterwards, so the run starts with
    no deliverable present). ANY smoke failure refuses the room:
    it is destroyed, a stocking-failure record is written, and no
    executable demo room is left standing.

  * completability is verified before the room is created (the
    freedom-first setup pass, 2026-11-24): every required source
    must be carriable under the working-set content budget —
    whole, since ranges partition a file and its whole content
    through ranges weighs the same — and the per-source facts
    (size, lines, how it can be obtained) are written into the
    stocking record. A source that could not be carried refuses
    the stocking here, at setup.

The stocking record (<base>/<name>.stocking.json, host-side beside
the room state) carries the manifest identity, the per-source
hashes as verified host-side and in-room, the declared envelope,
the completability facts, and every smoke result — the record the
demonstration's checker reconstructs the stocking from (the
paper's hop 2).

Nothing here talks to a provider or a model. Offline only.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import room as room_mod

RIG_DIR = Path(__file__).resolve().parent
FRAMEWORK_DIR = RIG_DIR.parent.parent
DEFAULT_MANIFEST_PATH = (FRAMEWORK_DIR / "live-demo" / "first-worker"
                         / "manifest.json")
DEFAULT_SOURCES_DIR = (FRAMEWORK_DIR / "live-demo" / "first-worker"
                       / "sandbox")

# The first-worker assignment's source-set identity: the manifest
# hash the probed1 run staged and sealed (the harness's
# EXPECTED_MANIFEST_HASH). A staged manifest hashing to anything
# else is not the released source set, however consistent it is
# internally.
EXPECTED_MANIFEST_HASH = (
    "bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784"
    "b4ae3a287d904f")

# The paper §1.4 envelope, declared at stocking. Every value is the
# rig's default, spelled out here because the paper declares them
# for THIS run; the per-execution wall-clock is a Room.run timeout,
# not a limits key, and is declared alongside.
DEMO_LIMITS = {
    "storage_bytes": 512 << 20,                    # sized tmpfs
    "aggregate_mem_bytes": 512 << 20,              # working ceiling
    "aggregate_mem_catastrophic_multiple": 2.0,
    "sustain_seconds": 1.0,
    "aggregate_pids_max": 128,                     # working ceiling
    "aggregate_pids_catastrophic_multiple": 2.0,
    "aggregate_cpu_seconds": 600.0,                # run-cumulative
    "warden_poll_s": 0.05,
    "output_bytes": 1 << 20,                       # per stream
}
PER_EXECUTION_WALL_S = 120

DELIVERABLE_IN_ROOM = "/room/scratch/brief.md"


class StockingError(Exception):
    """The demonstration room could not be stocked and verified to
    the paper §1 specification. Raised before any worker exists;
    the refusal is recorded host-side."""


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    return _sha256_bytes(Path(path).read_bytes())


def manifest_hash_of(manifest):
    """The manifest's identity: SHA-256 over its canonical JSON —
    the harness's own computation (json.dumps with sort_keys and
    compact separators)."""
    canonical = json.dumps(manifest, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(canonical)


def verify_source_set(manifest_path=DEFAULT_MANIFEST_PATH,
                      sources_dir=DEFAULT_SOURCES_DIR):
    """Verify the released source set before anything is stocked.

    Returns (manifest, manifest_hash, stock) where stock maps each
    in-room path (relative to work/) to the file's bytes. Raises
    StockingError — naming exactly what could not be verified — if
    the manifest is unreadable, its canonical hash is not the
    released identity, an entry's file is missing, or a file's hash
    differs from its manifest entry."""
    manifest_path = Path(manifest_path)
    sources_dir = Path(sources_dir)
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as exc:
        raise StockingError(
            f"the source manifest at {manifest_path} could not be "
            f"read: {exc}")
    if not isinstance(manifest, dict) \
            or not isinstance(manifest.get("sources"), list) \
            or not manifest["sources"]:
        raise StockingError(
            f"the source manifest at {manifest_path} carries no "
            "sources list")
    mhash = manifest_hash_of(manifest)
    if mhash != EXPECTED_MANIFEST_HASH:
        raise StockingError(
            f"the source manifest hashes to {mhash}, not the "
            f"released source-set identity "
            f"{EXPECTED_MANIFEST_HASH}; the staged source set is "
            "not the released one and will not be stocked")
    stock = {}
    for entry in manifest["sources"]:
        rel = entry.get("path")
        want = entry.get("sha256")
        if not rel or not want:
            raise StockingError(
                f"a manifest entry is malformed: {entry!r}")
        staged = sources_dir / rel
        if not staged.exists():
            raise StockingError(
                f"the manifest's {rel} is missing from "
                f"{sources_dir}")
        data = staged.read_bytes()
        got = _sha256_bytes(data)
        if got != want:
            raise StockingError(
                f"{rel} hashes to {got}, not its manifest entry "
                f"{want}; the file will not be stocked")
        stock[rel] = data
    return manifest, mhash, stock


# -- completability --------------------------------------------------------
# The freedom-first setup pass (2026-11-24): before a room
# is stocked, the setup verifies the assignment is
# COMPLETABLE in the room as configured — every required
# source obtainable and carriable under the working-set
# configuration. Run 4's lesson: index-tail (40,953 bytes)
# could not be pulled whole at all under the inherited
# per-result ceiling, and no gate had ever asked whether
# the task could be finished as configured; the worker
# discovered it at his step 11 instead. The check belongs
# here, at setup, where a failure costs nothing.

def _working_set_budget():
    """The working-set content budget the carriage facts
    are checked against: the framework's own constant when
    the framework package is importable (the demo driver
    and the rehearsals run with src/ on the path), else
    the standing literal — the same number, named here so
    this module still runs standalone from the rig dir."""
    try:
        from framework import tool_policy
        return tool_policy.WORKING_SET_CONTENT_BUDGET
    except Exception:
        return 64000


def _line_count(data):
    """Lines in data, counted as the retrieval performers
    split them: each line is the bytes up to and including
    its newline; a final line may lack one."""
    count = 0
    start = 0
    while start < len(data):
        nl = data.find(b"\n", start)
        start = len(data) if nl == -1 else nl + 1
        count += 1
    return count


def check_completability(stock, budget_bytes):
    """The per-source carriage facts for a stock (a mapping
    of in-room path to bytes, as verify_source_set
    returns), and the refusal the setup owes when the
    assignment cannot be completed as configured. Returns
    the facts block for the stocking record; raises
    StockingError naming the source, its size and the
    budget when a required source could not be carried.

    A source is carriable whole when its size stands
    within the working-set content budget. Ranges cannot
    rescue a source that is not: ranges partition the
    file, so the file's whole content through ranges
    weighs exactly the file's size, and the working set's
    first-fit derivation would leave the later ranges
    standing not-carried — the worker could never hold the
    source. (The in-room exec door bypasses the working
    set, but a source the package can never present whole
    is not a source the assignment may silently depend on:
    the setup refuses, and the office re-stocks or
    re-scopes — at setup, not at the worker's step 11.)
    The accumulated figure — all stocked sources carried
    together — is recorded as a fact, not a refusal
    ground: the worker may hold the sources one or two at
    a time and reach the rest through the room."""
    facts = []
    accumulated = 0
    for rel in sorted(stock):
        data = stock[rel]
        size = len(data)
        accumulated += size
        facts.append({
            "path": rel,
            "bytes": size,
            "lines": _line_count(data),
            "obtainable_via": [
                "sandbox.read (whole pull)",
                "sandbox.read_range (line ranges)",
                "container.exec (cat, inside the room)"],
            "carriable_whole": size <= budget_bytes,
        })
    for fact in facts:
        if not fact["carriable_whole"]:
            raise StockingError(
                f"required source {fact['path']} stands at "
                f"{fact['bytes']} bytes, over the working-set "
                f"content budget of {budget_bytes} bytes: it "
                "could not be carried whole, and ranges "
                "partition the file, so its whole content "
                "through ranges weighs the same — the "
                "assignment is not completable as stocked; "
                "re-stock or re-scope at setup")
    return {
        "budget_bytes": budget_bytes,
        "sources": facts,
        "accumulated_bytes": accumulated,
        "accumulated_carriable": accumulated <= budget_bytes,
        "ok": True,
    }


# -- the smoke set ---------------------------------------------------------
# One python execution performs the in-room acts and reports them as
# a JSON line; a separate shell execution proves the shell itself.
# The worker's working directory is /room/work, so the sources are
# read at the same relative paths the assignment names.

SMOKE_PY = r"""
import hashlib, json, os, sys
out = {"cwd": os.getcwd()}
ok = True
hashes = {}
for rel in sys.argv[1:4]:
    try:
        with open(rel, "rb") as fh:
            hashes[rel] = hashlib.sha256(fh.read()).hexdigest()
    except OSError as exc:
        hashes[rel] = f"ERROR {type(exc).__name__}: {exc}"
        ok = False
out["source_hashes"] = hashes
token = sys.argv[4]
try:
    probe = "/room/scratch/.smoke-write-probe"
    with open(probe, "w") as fh:
        fh.write(token)
    with open(probe) as fh:
        back = fh.read()
    os.unlink(probe)
    out["scratch_write_readback"] = (back == token)
    ok = ok and (back == token)
except OSError as exc:
    out["scratch_write_readback"] = f"ERROR {type(exc).__name__}: {exc}"
    ok = False
try:
    with open(sys.argv[5], "w") as fh:
        fh.write("stocking smoke probe - not the deliverable\n")
    out["deliverable_writable"] = os.path.exists(sys.argv[5])
    ok = ok and out["deliverable_writable"]
except OSError as exc:
    out["deliverable_writable"] = f"ERROR {type(exc).__name__}: {exc}"
    ok = False
print(json.dumps(out))
sys.exit(0 if ok else 3)
"""


def _last_json_line(text):
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def run_smoke(room, manifest):
    """The paper §1.2 smoke set, run inside the room. Returns a
    list of {check, ok, detail} — every entry must be ok for the
    room to stand."""
    results = []

    def record(check_name, ok, detail):
        results.append({"check": check_name, "ok": bool(ok),
                        "detail": detail})
        return ok

    shell = room.run(
        ["/bin/bash", "-c",
         "echo shell-ok && test -r sources/stock-take.md "
         "&& echo source-visible"],
        timeout=PER_EXECUTION_WALL_S)
    record("shell runs and sees the sources at their relative paths",
           shell["rc"] == 0 and "shell-ok" in shell["stdout"]
           and "source-visible" in shell["stdout"],
           f"rc={shell['rc']} stdout={shell['stdout'][:80]!r}")

    token = f"smoke-{time.time():.3f}"
    rels = [e["path"] for e in manifest["sources"]]
    py = room.run(
        ["/usr/bin/python3", "-c", SMOKE_PY] + rels
        + [token, DELIVERABLE_IN_ROOM],
        timeout=PER_EXECUTION_WALL_S)
    rep = _last_json_line(py["stdout"])
    if rep is None:
        record("python3 runs the smoke program", False,
               f"no JSON report; rc={py['rc']} "
               f"stdout={py['stdout'][:120]!r} "
               f"stderr={py['stderr'][:120]!r}")
        return results
    record("python3 runs the smoke program", py["rc"] in (0, 3),
           f"rc={py['rc']}")
    record("working directory is /room/work",
           rep.get("cwd") == "/room/work", f"cwd={rep.get('cwd')}")
    want = {e["path"]: e["sha256"] for e in manifest["sources"]}
    got = rep.get("source_hashes") or {}
    for rel in rels:
        record(f"source readable in-room, hash matches: {rel}",
               got.get(rel) == want[rel],
               f"in-room sha256={got.get(rel)}")
    record("scratch write and read back",
           rep.get("scratch_write_readback") is True,
           f"{rep.get('scratch_write_readback')}")
    record("deliverable path writable (scratch/brief.md)",
           rep.get("deliverable_writable") is True,
           f"{rep.get('deliverable_writable')}")
    return results


def stock_demo_room(base, name="demo", manifest_path=None,
                    sources_dir=None):
    """Stock and verify the demonstration room under <base>.

    Returns the stocking record (also written to
    <base>/<name>.stocking.json). On any failure the room is
    refused — destroyed if created — a stocking-failure record is
    written to <base>/<name>.stocking-failure.json, and
    StockingError is raised. No executable demo room is left
    standing on a failed stocking."""
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(manifest_path) if manifest_path \
        else DEFAULT_MANIFEST_PATH
    sources_dir = Path(sources_dir) if sources_dir \
        else DEFAULT_SOURCES_DIR
    failure_path = base / f"{name}.stocking-failure.json"

    def refuse(reason, room=None):
        if room is not None:
            try:
                room.destroy(remove_tree=True)
            except Exception:
                pass
        failure_path.write_text(json.dumps({
            "room": name, "stocked": False, "reason": reason,
            "at": time.time()}, indent=2))
        raise StockingError(reason)

    try:
        manifest, mhash, stock = verify_source_set(manifest_path,
                                                   sources_dir)
    except StockingError as exc:
        refuse(f"source-set verification failed: {exc}")

    # Completability (the freedom-first setup pass): the
    # assignment must be completable in the room as
    # configured — every required source carriable under
    # the working-set budget — verified here, before the
    # room is created, so a failure costs a setup refusal
    # and never the worker's steps.
    try:
        completability = check_completability(
            stock, _working_set_budget())
    except StockingError as exc:
        refuse(f"completability verification failed: {exc}")

    try:
        room = room_mod.create_room(base, name, stock=stock,
                                    limits=dict(DEMO_LIMITS))
    except room_mod.RoomCreationError as exc:
        refuse(f"room creation failed closed: {exc}")

    smoke = run_smoke(room, manifest)
    failed = [r for r in smoke if not r["ok"]]
    if failed:
        refuse("the stock-verification smoke set failed: "
               + "; ".join(f"{r['check']} ({r['detail']})"
                           for r in failed), room=room)

    # The smoke's deliverable probe must not stand as a deliverable:
    # the run starts with scratch/brief.md absent. Removed host-side
    # from the tree; the removal is part of the stocking record.
    probe = room.tree / "scratch" / "brief.md"
    probe_removed = False
    if probe.exists():
        probe.unlink()
        probe_removed = not probe.exists()

    state = json.loads(room.state_path.read_text())
    record = {
        "room": name,
        "stocked": True,
        "at": time.time(),
        "tree": str(room.tree),
        "room_uid": room.room_uid,
        "source_manifest": {
            "path": str(manifest_path),
            "manifest_sha256": mhash,
            "identity": ("the first-worker assignment's released "
                         "source set (probed1 identity)"),
            "sources": [{
                "path": e["path"],
                "sha256": e["sha256"],
                "provenance": e.get("provenance"),
                "in_room_path": f"/room/work/{e['path']}",
                "host_tree_sha256_after_stocking": _sha256_file(
                    room.tree / "work" / e["path"]),
            } for e in manifest["sources"]],
        },
        "runtime_stock": {
            "recipe": room_mod.standard_recipe(),
            "stock_binds_ro": room_mod.STOCK_BINDS,
            "rig_stock_items": ["rig/preflight.py", "rig/reaper.py"],
            "environment": room.env_manifest,
        },
        "deliverable": {
            "in_room_path": DELIVERABLE_IN_ROOM,
            "host_path": str(room.tree / "scratch" / "brief.md"),
            "smoke_probe_removed": probe_removed,
            "present_at_stocking_end": probe.exists(),
        },
        "envelope_declared": {
            "limits": dict(DEMO_LIMITS),
            "per_execution_wall_s": PER_EXECUTION_WALL_S,
            "cpu_contract": room_mod.CPU_CONTRACT,
        },
        "completability": completability,
        "smoke": smoke,
        "room_state_executions_at_stocking": len(
            state.get("executions", [])),
    }
    (base / f"{name}.stocking.json").write_text(
        json.dumps(record, indent=2))
    return record


def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="Track C demonstration stocking")
    sub = ap.add_subparsers(dest="op", required=True)
    v = sub.add_parser("verify-sources")
    v.add_argument("--manifest", default=None)
    v.add_argument("--sources-dir", default=None)
    s = sub.add_parser("stock")
    s.add_argument("--base", required=True)
    s.add_argument("--name", default="demo")
    d = sub.add_parser("destroy")
    d.add_argument("--base", required=True)
    d.add_argument("--name", default="demo")
    args = ap.parse_args()

    if args.op == "verify-sources":
        try:
            manifest, mhash, _ = verify_source_set(
                args.manifest or DEFAULT_MANIFEST_PATH,
                args.sources_dir or DEFAULT_SOURCES_DIR)
        except StockingError as exc:
            print(json.dumps({"verified": False, "error": str(exc)},
                             indent=2))
            sys.exit(3)
        print(json.dumps({
            "verified": True, "manifest_sha256": mhash,
            "sources": [{"path": e["path"], "sha256": e["sha256"]}
                        for e in manifest["sources"]]}, indent=2))
    elif args.op == "stock":
        try:
            record = stock_demo_room(args.base, args.name)
        except StockingError as exc:
            print(json.dumps({"stocked": False, "error": str(exc)},
                             indent=2))
            sys.exit(3)
        print(json.dumps({"stocked": True, "room": record["room"],
                          "manifest_sha256":
                              record["source_manifest"]
                                    ["manifest_sha256"],
                          "smoke": record["smoke"]}, indent=2))
    elif args.op == "destroy":
        room = room_mod.load_room(args.base, args.name)
        print(json.dumps(room.destroy(remove_tree=True), indent=2))


if __name__ == "__main__":
    main()
