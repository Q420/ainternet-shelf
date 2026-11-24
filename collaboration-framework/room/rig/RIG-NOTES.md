# Track B test rig — notes (2026-11-24, correction round)

Offline only: nothing here talks to a provider or a model. Built under
`ENVIRONMENT-DESIGN-REV2-2026-11-24.md` and Track B of
`ROOM-TEST-PROGRAMME-2026-11-24.md`. This round answers Vane's build
examination (INDEX 438), which returned the round-1 rig for correction
on five findings: no aggregate envelope, a mount witness that proved
presence rather than properties, identity inferred rather than read
from the kernel, an unwitnessed execution path with unbounded output,
and imprecise persistence terms. Ben's framing governs alongside:
**the room is the temp's own office, not a cell** — walls at the
property line (network, credentials, host reach, aggregate limits),
maximum freedom inside them.

## What was built

| File | Role |
|---|---|
| `room.py` | Room construction/run/destroy (module + thin CLI). A room = a stocked tree on a sized tmpfs plus a construction recipe, with its OWN uid/gid. Each execution is a fresh namespace instance over the same tree; a supervisor mode holds one instance open for witnessing. A host-side **warden** censuses every execution's pid namespace and enforces the aggregate envelope. State host-side, outside the tree, in `<base>/<name>.room.json`, including per-execution records (lifecycle, envelope outcome, pressure events, output accounting). |
| `host_witness.py` | Independent host-side witness. Given the launcher PID, reads only `/proc`: the COMPLETE mount table (every mountinfo field), network interfaces/routes, launched environment, cgroup placement, namespaces, process tree, and the room program's **actual kernel credentials** from `/proc/<pid>/status`. Also carries `assess_mounts()`, which derives the allowed mount set from the declared recipe and flags anything it cannot derive. Never executes anything in the room, never reads room-produced files. |
| `preflight.py` | In-room pre-flight (a named stock item, copied to `/rig/preflight.py`). Unchanged from round 1 (accepted): sentinel reaches plus enumeration, JSON out; every reach must fail. |
| `test_rig.py` | The suite: 25 checks, including the round-1 control run, two deviant-room negative tests for the mount assessment, and the warden's enforcement demonstrations. |
| `RIG-NOTES.md` | This file. |

## The exact construction

```
mount -t tmpfs -o size=<storage_bytes>,uid=<room uid>,gid=<room gid>,mode=0700 tmpfs <tree>
unshare -n  bwrap --unshare-pid --unshare-ipc --unshare-uts
    --hostname room-<name> --die-with-parent
    --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64
    --ro-bind /bin /bin --ro-bind /sbin /sbin
    --bind <tree> /room --proc /proc --dev /dev
    --clearenv --setenv PATH=/usr/bin:/bin --setenv ROOM_ID=<name> [...]
    --chdir /room/work
  prlimit --as=<per-process> --cpu=<per-process> --nproc=<per-uid> --fsize=<per-file>
  setpriv --reuid <room uid> --regid <room gid> --clear-groups
          --no-new-privs --bounding-set=-all --inh-caps=-all
  <command>
```

The launcher is spawned with a scrubbed environment (`PATH` only) —
bubblewrap's pid-1 shim retains its launcher's environment in its own
address space (round-1 surprise 5), so the launcher is given nothing
to retain.

## The aggregate envelope — the centre of this round

cgroup v2 **cannot be raised on this host** (the unified hierarchy's
`cgroup.controllers` is empty; a fresh child cgroup has no
`memory.max`/`cpu.max`/`pids.max` files; the rig still attempts it at
every creation and records the reason). The envelope therefore stands
on three other layers:

1. **The warden (aggregate memory / process count / CPU).** During
   every execution, a host-side warden censuses the room's pid
   namespace from `/proc` every **50 ms** (declared: `warden_poll_s`)
   and sums RSS and cumulative CPU time over ALL member processes and
   counts them. Membership is by namespace containment — every process
   in a pid namespace descends from its init, so the init's descendant
   set is the member set (see surprise 8 for why inode matching is not
   available on this host). Declared parameters of the case envelope:
   - **Working ceiling** (defaults: 512 MiB aggregate RSS; 128
     processes): trips only on **sustained** excess — continuously
     over the ceiling for the declared **sustain window**
     (default 1.0 s). Legitimate spikes that settle inside the window
     survive.
   - **Catastrophic ceiling** (default: 2× the working ceiling):
     trips at the first census that sees it. A genuine flood is
     capped fast, without waiting out the window.
   - **CPU budget** (default: 600 cumulative CPU-seconds): summed
     across every process the namespace ever holds, so it is
     spike-immune by construction; trips the moment it is spent.
     This is a total-work budget, **not** a CPU rate limit.
   - **Pressure events:** any excursion over the working ceiling —
     including ones that recover — is recorded in the room state with
     its peak and duration. An undersized office shows up as evidence,
     not as a killed run.
   On a trip the warden SIGKILLs **every member of the namespace**
   (by census, so a setsid-detached process dies too) and records an
   envelope termination with the measured values in the room state.
2. **Storage: a sized tmpfs backs the tree** (declared:
   `storage_bytes`, default 512 MiB). Evaluated in order: (i) a
   fixed-size backing image via loop mount — **impossible on this
   host: there are no `/dev/loop*` devices at all** (`losetup:
   cannot find an unused loop device`); (ii) a sized tmpfs —
   **in force**. The kernel enforces it: the suite's fill attempt
   wrote 15,728,640 bytes into a 16 MiB tree and stopped with
   ENOSPC (errno 28); the file on the host tree is 16,764,928 bytes
   and `statvfs` reports the filesystem total as exactly 16,777,216.
3. **Per-process rlimits** (`prlimit`: RLIMIT_AS, RLIMIT_CPU,
   RLIMIT_NPROC per room uid, RLIMIT_FSIZE per file) — retained as a
   second layer and labelled per-process everywhere they are
   recorded. They are **not** the envelope, and nothing in this rig
   presents them as one.

### Demonstrated granularity (measurement, not a guaranteed bound)

The warden is userspace polling, so a breach is seen at the first
census after it forms — plus the sustain window for working-ceiling
kills. Measured on this host at 50 ms polling, across the passing
suite runs:

- **Fastest allocation vs the 384 MiB catastrophic ceiling:**
  measured peak aggregate RSS at the kill 385–404 MiB —
  **overshoot 1–20 MiB** (the allocator touches ~0.4–1.6 GiB/s).
- **Fastest forking vs the catastrophic count ceiling of 72:**
  measured peak count 159–265 — **overshoot 87–193 processes**
  (this host forks ~2,000–4,000 times/s; each census interval
  admits that many). A tighter poll interval shrinks this linearly;
  it does not eliminate it. A kernel mechanism (cgroup pids) would;
  none is available here.
- **Sustained memory kill** (two 120 MiB allocators, 192 MiB
  working ceiling, 0.5 s window): killed at a measured aggregate
  of 277 MiB after 0.51 s of continuous excess.
- **Legitimate spike** (256 MiB against the 192 MiB working
  ceiling): peaked at ~281 MiB for 0.36–0.56 s, released, exited 0;
  pressure event recorded with peak and duration.
- **CPU budget** (3.0 s budget, three spinners): killed at a
  measured 3.03–3.13 cumulative CPU-seconds.

## The mount witness (finding 2)

`host_witness.mount_table()` now parses **every** mountinfo field:
mount id, parent id, major:minor, root, mount point, options,
optional (propagation) fields, fstype, source, super options.
`assess_mounts()` derives the allowed set from the room's declared
recipe (`room.standard_recipe()`, recorded in the room state) and
asserts, for the witnessed instance:

- every exposed mount is derivable from the recipe — anything else
  is flagged **by name** in `unexpected` (the minimal `/dev`'s device
  nodes are derivable: each must be a bind of the matching node of
  the host's `/dev`, or the devpts mount);
- every declared mount is present;
- **source identity**: a stock bind's (major:minor, root) must equal
  the host path's own identity — the *resolved* path within the host
  mount containing it (this host's `/usr` is a directory of the
  overlay root, and `/lib`, `/bin` &c. are usr-merge symlinks into
  it, so identity is computed from the containing mount, not from a
  mount point of the same name);
- **read-only status**: a stock bind declared `ro` must carry `ro`
  in its kernel-recorded options;
- **propagation**: no `shared:`/`master:` optional field may appear
  on any mount (the declared propagation is private);
- **the room bind's root is exactly the declared tree**: device
  equality with the host mount backing the tree, and the bind root
  equal to the tree's location within that filesystem; the tree
  mount must be writable inside the room.

Negative tests prove the assessment bites: a room built with an
undeclared bind of the suite's base directory is flagged
(`/extra`, plus the submounts it drags in), and a room built with
its stock binds writable is flagged on every stock point.

## Identity (finding 3)

Each room gets **its own uid/gid**, allocated per room (floor
45000), recorded in its state; the tree is owned by that uid, mode
0700. The witness reads the room program's **actual** kernel state
from `/proc/<pid>/status` — Uid/Gid in all four positions, Groups,
CapInh/CapPrm/CapEff/CapBnd/CapAmb, NoNewPrivs, Seccomp — and the
suite asserts the values: all four uid/gid positions equal the
room's uid, groups empty, **all capability sets zero**, NoNewPrivs
1. Seccomp reads 2 (filter mode) with 4 filters — that is the
**host container's own inherited profile**, identical to the test
process's own; the room applies no seccomp filter of its own, and
the record says so rather than claiming one.

Cross-room, demonstrated: two concurrent rooms hold distinct uids;
probes run *as* room A's uid on the host cannot read room B's tree
file (EACCES at the 0700, B-owned tree) and cannot signal room B's
program (EPERM), while room B's own uid reads its file fine.

The round-1 adaptation stands, unchanged and still labelled an
adaptation: **no user namespace** is available with a working
`/proc` on this host (locked submounts, EPERM — "mount too
revealing"), so identity separation rests on the per-room uid drop
plus the zeroed capability bounding set, not on userns equivalence.

## Execution lifecycle and output (finding 4)

`Room.run` now records the **lifecycle of the actual call**: the
warden's census logs every process birth (host pid, namespace pid,
ppid, session, comm, cmdline where readable) and death (with its
cause: exited / timeout / envelope-termination) into the execution
record in the room state. Timeout and envelope kills sweep the
**whole namespace by census** — the suite's lifecycle check runs a
`setsid`-detached sleeper (its birth record shows session == its own
pid, i.e. it really did escape its process group) and finds it born,
recorded, and dead after the timeout sweep, with no survivors.
Output is captured by streaming readers with a **hard per-stream
ceiling** (declared: `output_bytes`, default 1 MiB): bytes beyond
the ceiling are counted and discarded, `truncated` is flagged, and
the total byte count is recorded (suite: a 5,000,000-byte spew is
counted in full, retained to exactly 1 MiB, flagged).

## Persistence terms (finding 5), stated exactly

Recorded in every room's state and evidenced by the suite:

- **Filesystem state persists across calls within a run** — one
  tree per room, bind-mounted into every execution. (Write in
  call 1, read back in call 2; a deliverable written in-room is
  present on the host tree.)
- **Process state does not persist** — every execution is a fresh
  process tree in a fresh pid namespace; no process survives the
  end of its own call. (A background sleeper launched in call 1 is
  gone before call 2; it dies with its namespace.)
- **Interpreter state does not persist** — no interpreter or shell
  session is held between calls; an environment marker set inside
  call 1's process is absent in call 2. Only files carry state
  between calls.

Whether the worker's working pattern wants a persistent session on
top of filesystem persistence is the design question Vane named;
this rig does not implement session persistence and does not claim
it.

## Suite result

`python3 test_rig.py` — **25 passed, 0 failed**, twice consecutively
(control, stocking, supervisor, mounts, mounts-extra, mounts-rw,
network, environment, namespaces, identity, cross-room,
envelope-record, preflight, persistence, persist-terms, ward-mem,
ward-spike, ward-fastspike, ward-pids, ward-forkfast, ward-cpu,
storage, output, lifecycle, cleanup). Exit code 0. Verified after
the runs: no leftover processes, mounts, cgroups, or test trees.

## Host behaviour that surprised us (round 2 additions)

8. **`/proc/<pid>/ns/pid` is ptrace-gated for the room's own
   processes.** Reading the namespace link of the room program —
   non-dumpable, owned by the room uid — fails with EACCES even for
   the host's root in this container, while the same processes'
   `status`/`stat` (NSpid, VmRSS, CPU times) read fine, and the
   root-owned bwrap shim's link reads fine. A census that matched
   namespace inodes across `/proc` would therefore count only the
   shim. The warden instead censuses by **namespace containment**
   (the init's descendant set — provably the member set while the
   init lives; a dead init means the kernel has already killed
   every member), and the init's inode, read once from the shim,
   is recorded in the execution record.
9. **usr-merge shapes bind identity.** `/lib`, `/lib64`, `/bin`,
   `/sbin` are symlinks into `/usr`; a bind of `/lib` records root
   `.../usr/lib` in mountinfo. Source-identity checks must resolve
   the host path first — a lexical comparison flags every stock
   bind on this host.
10. **The host's stock paths are not mount points.** `/usr` &c.
    are plain directories of the overlay root (device 0:42, root
    `/var/lib/hatch-runtime/rootfs-base`); their bind identity is
    computed within that containing mount. Relatedly, `/tmp`
    carries **stacked tmpfs mounts** (two entries, same point);
    the containing-mount lookup takes the last entry, the one on
    top — which is the one binds actually resolve through.

Round-1 surprises 1–7 stand as recorded in git history (nspawn
`/proc` locks and the userns adaptation; `unshare -n` wrapper for
the network namespace; `bwrap --cap-drop` breaking bwrap; the
cgroup absence — now answered by the warden + tmpfs layers above
rather than by rlimits alone; the pid-1 shim's retained
environment and the scrubbed launcher; the non-dumpable program
and the two-sided environment proof; `PWD`/`LC_CTYPE` as named
in-room additions).

## What could NOT be established

- **A kernel-enforced aggregate envelope.** The warden is
  userspace polling: its granularity is measured above and is
  real but coarse under very fast consumption (worst measured:
  ~193 processes past the catastrophic count ceiling inside one
  50 ms interval). On a host with delegated cgroup v2 controllers
  the same ceilings should be enforced by the kernel; this host
  offers no such delegation, and no configuration of this rig
  changes that.
- **User-namespace isolation**: unavailable with a working
  `/proc` on this host (round-1 surprise 1). Identity separation
  rests on the per-room uid drop plus the zeroed capability
  bounding set — a documented adaptation, not equivalence.
- **CPU *rate* limiting**: the envelope budgets cumulative
  CPU-seconds; nothing here throttles instantaneous CPU share.
- **Lifecycle completeness inside one poll interval**: a process
  born and dead entirely between two censuses (50 ms) leaves no
  lifecycle record. Births and deaths are recorded at census
  granularity, and the notes say so rather than claiming a
  continuous record.
- **Concurrent executions in one room**: the rig runs one
  execution at a time per tree and takes no lock; a supervisor
  instance and one-shot calls share the tree's filesystem but
  nothing serialises writers, and the warden supervises one-shot
  executions (the supervisor instance is witnessed, not
  warden-policed).
- Everything about the worker, the model, and the interface is
  other tracks' territory (A, C, D, E, G) and is untouched here,
  by design. Track G — attacking these mechanisms — remains a
  separate track that follows B.
