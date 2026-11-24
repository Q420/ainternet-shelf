# Track B test rig — notes (2026-11-24)

Offline only: nothing here talks to a provider or a model. Built under
`ENVIRONMENT-DESIGN-2026-11-24.md` §§3–5 and Track B of
`ROOM-TEST-PROGRAMME-2026-11-24.md`, with Vane's refinements applied:
the host-side witness is independent of the room (refinement 2), and
this rig stays in Track B's lane — mechanism and walls, not hostile-use
suites (that is Track G; refinement 3).

## What was built

| File | Role |
|---|---|
| `room.py` | Room construction/run/destroy (module + thin CLI). A room = a stocked tree plus a construction recipe; each execution is a fresh namespace instance over the same tree; a supervisor mode holds one instance open for witnessing. State is kept host-side, outside the tree, in `<base>/<name>.room.json`. |
| `host_witness.py` | Independent host-side witness. Given the launcher PID, reads only `/proc`: mount table, network interfaces/routes, launched environment, cgroup placement and limits, namespaces, process tree. Never executes anything in the room and never reads room-produced files. |
| `preflight.py` | In-room pre-flight (a named stock item, copied to `/rig/preflight.py`). Attempts the sentinel reaches — host sentinel file, sibling-tree sentinel, canary TCP connects (loopback + host primary IP), DNS resolution, `/proc/1/environ` exposure — and enumerates its own environment, visible processes, top-level filesystem, interfaces. JSON out; every reach must fail. |
| `test_rig.py` | The suite: 12 checks, including a control run proving the pre-flight detects reaches when unconfined. |
| `RIG-NOTES.md` | This file. |

Python rather than a shell script for `room.py` because the rig needs
structured state, hashing, `/proc` tree-walking and JSON records, and
because the suite imports the constructor directly instead of shelling
out to it.

## The exact construction

```
unshare -n  bwrap --unshare-pid --unshare-ipc --unshare-uts
    --hostname room-<name> --die-with-parent
    --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64
    --ro-bind /bin /bin --ro-bind /sbin /sbin
    --bind <tree> /room --proc /proc --dev /dev
    --clearenv --setenv PATH=/usr/bin:/bin --setenv ROOM_ID=<name> [...]
    --chdir /room/work
  prlimit --as=<mem> --cpu=<s> --nproc=<n> --fsize=<bytes>
  setpriv --reuid 65534 --regid 65534 --clear-groups --no-new-privs
          --bounding-set=-all --inh-caps=-all
  <command>
```

The launcher itself is spawned with a scrubbed environment
(`PATH` only) — see surprise 5 for why. Room trees are owned by uid
65534 so the dropped-identity program can work in them. The deliverable
subpath is `<tree>/deliverable`, visible in-room at
`/room/deliverable` and on the host tree after the call.

## Suite result

`python3 test_rig.py` — **12 passed, 0 failed**, twice consecutively
(control, stocking, supervisor, mounts, network, environment,
namespaces, envelope-recorded, preflight, persistence, containment,
cleanup). Exit code 0. No processes, cgroups, or test trees are left
behind.

## Host behaviour that surprised us

1. **This environment is a systemd-nspawn container whose `/proc` has
   locked submounts.** Mounting a fresh `/proc` inside a *new user
   namespace* fails with EPERM (the kernel's "mount too revealing"
   check), so the design's preferred recipe — `--unshare-user` with a
   mapped root — cannot raise the `/proc` wall on this host. The room
   therefore creates **no user namespace** (the witness confirms
   `user` is the one namespace that does not differ). The identity wall
   is enforced instead by `setpriv`: uid/gid 65534, no-new-privs, and a
   zeroed capability bounding set (verified `CapBnd: 0` in-room).
   Adaptation, not a dropped wall — but on a host where userns `/proc`
   mounting works, the userns recipe should be preferred.
2. **`bwrap --unshare-net` fails here** ("loopback: Failed
   RTM_NEWADDR: No child processes"). The network namespace is created
   by an `unshare -n` wrapper instead. Consequence, witnessed: the
   room's loopback interface exists but is **down**, with no addresses
   and no routes — connects fail with ENETUNREACH.
3. **`bwrap --cap-drop ALL` breaks bwrap itself**: its setup child
   drops capabilities before chdir and then cannot enter the room tree
   (EACCES). Capability dropping was moved to `setpriv`
   (`--bounding-set=-all --inh-caps=-all`), applied after the uid drop.
4. **The cgroup v2 envelope cannot be raised on this host.** The
   visible unified hierarchy's `cgroup.controllers` is **empty**; a
   fresh child cgroup contains no `memory.max`, `cpu.max`, or
   `pids.max` files at all. `systemd-run --scope -p MemoryMax=...` is
   accepted by systemd but the resulting limit is not visible anywhere
   in this hierarchy either (the scoped process still reports cgroup
   path `/`). The rig attempts cgroup creation on every room, detects
   the absence, removes the empty cgroup, and records the reason in the
   room state. **Fallback in force: `prlimit` rlimits**
   (RLIMIT_AS / RLIMIT_CPU / RLIMIT_NPROC / RLIMIT_FSIZE), which are
   per-process and inherited — **not** an aggregate over the room's
   process tree. The containment check proves a memory hog dies against
   its per-process limit while the host and a second room keep working;
   it does not prove aggregate containment, and the rig does not claim
   it. (RLIMIT_NPROC partially compensates: it counts all processes of
   the room uid system-wide.)
5. **bubblewrap's pid-1 shim retains the launcher's environment in its
   address space** (11,491 bytes observed, including host service
   variables) — it forks but never execs with the scrubbed env. The
   shim is root-owned and the room program cannot read it (pre-flight's
   `/proc/1/environ` exposure attempt confirms no declared-outside keys
   are reachable), and the witness records the shim's environment
   openly rather than hiding it. The rig additionally spawns the
   launcher with a scrubbed environment so the shim has nothing worth
   retaining.
6. **After `setpriv`'s uid drop the room program is non-dumpable**, so
   even host root cannot read its `/proc/<pid>/environ`. The launched
   environment is therefore witnessed from the other side of the wall:
   the host witness parses the `--setenv` pairs out of the launcher's
   cmdline (host-side construction evidence) and the suite requires
   them to equal the declared manifest exactly, while the in-room
   pre-flight corroborates what actually arrived. Two-sided, as the
   design requires — neither side alone is treated as proof.
7. Small honest additions to the in-room environment: `PWD` (set by
   bwrap on chdir) and `LC_CTYPE` (Python's PEP 538 locale coercion,
   visible only in a Python process's own view). Both are named in the
   suite's allowed set rather than silently tolerated.

## What could NOT be established

- **Aggregate cgroup envelope** (memory/CPU/pids over the whole room
  tree): impossible on this host today — see surprise 4. Needs a
  hierarchy with delegated controllers.
- **Filesystem size ceiling for the room tree** (design §5): not
  enforced. The tree lives on the host filesystem; RLIMIT_FSIZE bounds
  individual file size only. A sized tmpfs or project quota would be
  needed.
- **User-namespace isolation**: not available with a working `/proc`
  on this host — see surprise 1. Identity separation rests on the uid
  drop plus the zeroed capability bounding set.
- **Concurrent executions in one room**: the rig runs one execution at
  a time per tree and takes no lock; a supervisor instance and one-shot
  calls share the tree's filesystem but nothing serialises writers.
- Everything about the worker, the model, and the interface is other
  tracks' territory (A, C, D, E, G) and is untouched here, by design.
