# Track B test rig — notes (2026-11-24, correction round 2)

Offline only: nothing here talks to a provider or a model. Built under
`ENVIRONMENT-DESIGN-REV2-2026-11-24.md` and Track B of
`ROOM-TEST-PROGRAMME-2026-11-24.md`. Correction round 1 answered
Vane's build examination (INDEX 438): an aggregate envelope, a mount
witness that proves properties, identity read from the kernel,
bounded output, exact persistence terms. **This round (round 2)
answers her correction examination (INDEX 451), which returned the
round-1 correction on five points**: the envelope boundary was
undefined (per-call wardens, no serialisation, CPU resetting per
call); CPU accounting missed short-lived processes; a failed storage
mount left an executable room on the host filesystem; a failed
namespace discovery left an execution running unwardened; and two
claims (lifecycle, memory) were phrased broader than the mechanism.
Each point is answered below, in place. Ben's framing governs
alongside: **the room is the temp's own office, not a cell** — walls
at the property line (network, credentials, host reach, aggregate
limits), maximum freedom inside them.

## What was built

| File | Role |
|---|---|
| `room.py` | Room construction/run/destroy (module + thin CLI). A room = a stocked tree on a sized tmpfs plus a construction recipe, with its OWN uid/gid. Each execution is a fresh namespace instance over the same tree, serialised against the room's other executions by a lock, and run under the in-room reaper; a supervisor mode holds one instance open for witnessing. A host-side **warden** censuses every execution's pid namespace and enforces the aggregate envelope. State host-side, outside the tree, in `<base>/<name>.room.json`, including per-execution records (observed lifecycle, envelope outcome, pressure events, output and CPU accounting) and the run's CPU ledger. |
| `reaper.py` | The in-room execution parent (a named stock item, copied to `/rig/reaper.py`). A child subreaper that wait4()s every process of the execution and reports the exact collected rusage to the host over an inherited fd the command never sees; it also holds a mechanical start gate — the command is not forked until the host side opens the gate, after namespace discovery. |
| `host_witness.py` | Independent host-side witness. Given the launcher PID, reads only `/proc`: the COMPLETE mount table (every mountinfo field), network interfaces/routes, launched environment, cgroup placement, namespaces, process tree, and the room program's **actual kernel credentials** from `/proc/<pid>/status`. Also carries `assess_mounts()`, which derives the allowed mount set from the declared recipe and flags anything it cannot derive. Never executes anything in the room, never reads room-produced files. |
| `preflight.py` | In-room pre-flight (a named stock item, copied to `/rig/preflight.py`). Unchanged from round 1 (accepted): sentinel reaches plus enumeration, JSON out; every reach must fail. |
| `test_rig.py` | The suite: 30 checks, including the round-1 control run, two deviant-room negative tests for the mount assessment, the warden's enforcement demonstrations, and round 2's boundary, accounting, and fail-closed tests. |
| `RIG-NOTES.md` | This file. |

## The exact construction

```
mount -t tmpfs -o size=<storage_bytes>,uid=<room uid>,gid=<room gid>,mode=0700 tmpfs <tree>
    (if this mount fails, creation fails closed — see "Fail-closed
     preconditions" below; no executable room is produced)
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
  python3 /room/rig/reaper.py --report-fd <inherited fd>
          --gate-file /room/rig/.start-gate-<per-call token> --
    <command>          (forked by the reaper only when the host side
                        opens the gate, after namespace discovery)
```

The launcher is spawned with a scrubbed environment (`PATH` only) —
bubblewrap's pid-1 shim retains its launcher's environment in its own
address space (round-1 surprise 5), so the launcher is given nothing
to retain. The supervisor instance uses the same chain minus the
reaper: it is witnessed, not executed-and-accounted.

## The aggregate envelope — the centre of this round

cgroup v2 **cannot be raised on this host** (the unified hierarchy's
`cgroup.controllers` is empty; a fresh child cgroup has no
`memory.max`/`cpu.max`/`pids.max` files; the rig still attempts it at
every creation and records the reason). The envelope therefore stands
on three other layers:

1. **The warden (aggregate memory / process count / CPU).** During
   every execution, a host-side warden censuses the room's pid
   namespace from `/proc` every **50 ms** (declared: `warden_poll_s`)
   and sums RSS over the member processes it observes and counts
   them. Membership is by namespace containment — every process
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
   - **CPU budget** (default: 600 cumulative CPU-seconds): a total-
     work budget over the whole run (next section), **not** a CPU
     rate limit; cumulative, so spike-immune; trips the moment the
     run total crosses it.
   - **Pressure events:** any excursion over the working ceiling —
     including ones that recover — is recorded in the room state with
     its peak and duration. An undersized office shows up as evidence,
     not as a killed run.
   On a trip the warden SIGKILLs **every member of the namespace**
   (by census, so a setsid-detached process dies too) and records an
   envelope termination with the measured values in the room state.

   **What the memory ceiling is a ceiling on** (round 2, point 5):
   the summed RSS of the processes the census observes. It is **not**
   total host memory charged to the room — the tmpfs pages the room
   writes are bounded separately by the storage ceiling, and other
   kernel-side allocations are not inside the RSS sum. The state's
   envelope record says so in the same words.

### The envelope boundary is the worker run (round 2, point 1)

Round 1's warden was per execution, and the notes conceded concurrent
executions were unserialised: two simultaneous calls each received a
full aggregate allowance, and the CPU budget reset every call. The
boundary is now defined — **the worker run**, matching the
framework's other per-run bounds — and enforced two ways:

- **Serialisation, mechanically.** `Room.run()` holds a per-room
  execution lock (an `flock` on `<base>/<name>.exec.lock`) for the
  whole call. At any instant, one execution is the room's whole load,
  so the instantaneous ceilings (memory, process count) ARE per-room
  enforcement, not per-call approximations of it. The suite proves
  it: two concurrent calls on one room produce strictly
  non-interleaved begin/end markers in a shared order file.
- **A run-scoped CPU ledger.** The room state carries `cpu_ledger`:
  the budget, the consumed total, and every call's contribution
  (charged, census, and reaper figures, plus refusals). Each call's
  warden is seeded with the run's prior consumption and trips when
  the RUN total crosses the budget; a call that starts with the
  budget already spent is **refused before execution**, with the
  refusal recorded in both the executions list and the ledger. The
  suite proves it: with a 2.0 s budget, a first call burns ~1.23 s
  and exits cleanly, a second identical call is killed at a measured
  run total of ~2.04 s, and a third call is refused — its marker file
  is never written — with the ledger showing all three calls and a
  consumed total of ~2.04 s.

The supervisor instance stands outside this boundary: it is a
witnessing harness held open across calls, not a worker execution,
and it remains witnessed-but-not-policed (see "What could NOT be
established").

### CPU accounting (round 2, point 2)

Round 1's warden accumulated CPU from per-process sampled deltas: a
process that started, burned, and exited between two censuses never
entered the census and its CPU was simply missed — the claim
"cumulative budget" was broader than the mechanism. Two mechanisms
now close the hole, and the claim is restated to match them:

- **In flight — the census identity.** For every observed process
  the census sums its own CPU time **plus its reaped-children CPU
  times** (`/proc/<pid>/stat` fields 14–17). When a process is
  reaped, its times move into its parent's reaped-children fields at
  exactly the moment it leaves `/proc`, so summed over the tree the
  figure is the tree's true total at that instant — short-lived
  processes their parents reaped are counted through the parent,
  without the sampler ever seeing them alive. The warden keeps the
  maximum level seen (a single non-atomic `/proc` sweep can
  transiently under-read; it cannot over-read beyond scan races).
- **At call end — the reaper's exact total.** The executed command
  runs under the in-room **reaper** (`reaper.py`): a child subreaper
  that `wait4()`s every process of the execution. A reaped process's
  rusage carries its own CPU plus every descendant it reaped in
  turn, and orphans reparent to the reaper, so its collected sum is
  the execution's exact total for every process that terminated
  while it lived. When the main command exits, the reaper SIGKILLs
  and reaps whatever remains, so stragglers are accounted too. It
  reports one JSON line over an inherited pipe fd that the command
  never sees (the reaper closes it in the child before exec; the
  fd survives the unshare/bwrap/prlimit/setpriv chain — verified
  empirically on this host). If the reaper itself is killed (warden
  sweep, timeout), its report dies with it and the call falls back
  to the census level. **The ledger is charged the larger of the
  two figures** — each method can miss what the other catches, and
  never less than either measured.

**Measured capture** (the suite's adversarial check): a workload
whose parent forks **40 burners, each burning 25 ms of CPU** —
inside one 50 ms census interval — and reaps each in turn, printing
its own rusage-derived ground truth (self + reaped children). Across
the two passing suite runs: ground truth 1.084 s and 1.108 s;
**reaper captured 100.5% both runs; census captured 97.8% and
101.1%** (the census figure includes the rig's own in-namespace
processes — the shim and the reaper — which the workload's ground
truth does not; the reaper's figure counts only the workload tree).
The claim the record makes is exactly this: *sampled in-flight
accounting by the census identity, reconciled per call against the
reaper's exact collected rusage* — with these measured fractions on
this adversarial shape, not a blanket "complete".

### Fail-closed preconditions (round 2, points 3 and 4)

- **Storage.** If the sized tmpfs mount fails at creation, creation
  itself fails: a failed-precondition record
  (`failed: true, executable: false, failed_precondition:
  "storage-tmpfs-mount"`, with the mount error) is written to the
  room's state path, the just-created tree directory is removed, and
  `create_room()` raises `RoomCreationError`. `load_room()` raises
  on such a record, and `Room.run()` independently refuses any room
  whose recorded storage is not `tmpfs-sized`. There is no code path
  where a room executes on the host filesystem without its storage
  ceiling. Negative test: creation with an impossible size parameter
  (the mount genuinely fails at the real seam) raises, records, and
  leaves neither a loadable room nor a tree.
- **Namespace discovery.** An execution's command starts only when
  the host side opens the reaper's **start gate** — a file in the
  room tree whose name carries a per-call random token — and the
  gate is opened only after the namespace init has been discovered
  and the warden constructed. If discovery fails, the launch is
  terminated (whole launcher tree killed) with the gate still
  closed: the command **provably never ran**, a property of the
  mechanism, not of winning a kill race. The result records the
  failed precondition (`namespace-discovery`). Negative test: with
  the discovery seam simulated as failed against a live launch, the
  command's marker file does not exist, the gate file was never
  created, and nothing from the launch survives.
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
  measured peak aggregate RSS at the kill 386–461 MiB across the
  passing runs of both rounds — **overshoot 1.7–76.6 MiB** (the
  allocator touches ~0.4–1.6 GiB/s; the spread is host load, and
  it is reported as a spread, not a best case).
- **Fastest forking vs the catastrophic count ceiling of 72:**
  measured peak count 156–265 — **overshoot 84–193 processes**
  (this host forks ~2,000–4,000 times/s; each census interval
  admits that many). A tighter poll interval shrinks this linearly;
  it does not eliminate it. A kernel mechanism (cgroup pids) would;
  none is available here.
- **Sustained memory kill** (two 120 MiB allocators, 192 MiB
  working ceiling, 0.5 s window): killed at a measured aggregate
  of ~276 MiB after 0.51 s of continuous excess.
- **Legitimate spike** (256 MiB against the 192 MiB working
  ceiling): peaked at ~280–293 MiB for 0.36–0.56 s, released,
  exited 0; pressure event recorded with peak and duration.
- **CPU budget** (3.0 s budget, three spinners): killed at a
  measured 3.03–3.13 cumulative CPU-seconds. **Run-cumulative**
  (2.0 s budget, two ~1.23 s calls): the second call killed at a
  measured run total of ~2.04 s; a third call refused unspent.
- **Short-lived burners** (40 × 25 ms CPU, each inside one census
  interval): reaper captured 100.5% of the rusage ground truth in
  both runs; the census identity captured 97.8% and 101.1%. See
  "CPU accounting" above for exactly what is claimed.

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

## Observed execution lifecycle and output (finding 4; round 2, point 5)

`Room.run` records the **observed lifecycle of the actual call**:
the warden's census logs the process births it sees (host pid,
namespace pid, ppid, session, comm, cmdline where readable) and the
deaths it sees (with cause: exited / timeout /
envelope-termination) into the execution record in the room state,
which labels the record `observed (census-sampled)`. It is **not** a
complete process-event trace: a process born and dead entirely
between two censuses leaves no lifecycle record (its CPU is still
accounted — see "CPU accounting"). Timeout and envelope kills sweep
the **whole namespace by census** — the suite's lifecycle check runs
a `setsid`-detached sleeper (its birth record shows session == its
own pid, i.e. it really did escape its process group) and finds it
observed born, recorded, and dead after the timeout sweep, with no
survivors. Output is captured by streaming readers with a **hard
per-stream ceiling** (declared: `output_bytes`, default 1 MiB):
bytes beyond the ceiling are counted and discarded, `truncated` is
flagged, and the total byte count is recorded (suite: a 5,000,000-byte
spew is counted in full, retained to exactly 1 MiB, flagged).

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

`python3 test_rig.py` — **30 passed, 0 failed**, twice consecutively
(control, stocking, supervisor, mounts, mounts-extra, mounts-rw,
network, environment, namespaces, identity, cross-room,
envelope-record, preflight, persistence, persist-terms, ward-mem,
ward-spike, ward-fastspike, ward-pids, ward-forkfast, ward-cpu,
serialise, cpu-run, cpu-shortlived, storage-fail, ns-fail, storage,
output, lifecycle, cleanup). Exit code 0. Verified after the runs:
no leftover processes, mounts, cgroups, or test trees.

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
11. **CPU time is never destroyed by reaping — it moves**
    (verified empirically, round 2; the accounting rests on it).
    The rusage `wait4()` returns for a process includes that
    process's own times **plus** the times of every descendant it
    reaped in turn; likewise `/proc/<pid>/stat` fields 16/17
    (cutime/cstime) accumulate exactly the reaped subtrees. So a
    subreaper that reaps the whole execution collects its exact
    total, and a census summing own + reaped-children times over
    the live tree reads the tree's true total at that instant —
    two independent routes to the same figure, which is what lets
    the rig reconcile them. Relatedly, an extra inherited fd
    survives the whole unshare → bwrap → prlimit → setpriv chain
    unrenumbered (verified), which is the reaper's report channel.

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
  granularity — the record is labelled *observed* everywhere —
  and the notes say so rather than claiming a continuous record.
  (Its CPU is a different matter: accounted via its parent's
  reaped-children times or the reaper, per "CPU accounting".)
- **CPU accounting's residual gap**: if the reaper itself is
  killed (a warden sweep or timeout SIGKILLs the whole namespace),
  that call is charged the census figure, and the census can lose
  a tail that vanishes entirely between two polls — a branch that
  is born, burns, is reaped upward, and whose last surviving
  ancestor is itself reaped onward inside one 50 ms interval.
  The loss is bounded by one interval of the tree's burn rate;
  on the suite's adversarial shape the census's worst measured
  capture was 97.8% of ground truth. The reaper's report channel
  (an inherited fd) is protected on this host by the reaper's
  non-dumpability after the uid drop — the same property that
  closes room processes' `/proc` entries to the host's root
  (surprise 8) — which the rig observes but does not itself
  enforce; a worker determined to forge its own CPU ledger is
  Track G's problem, and the census cross-check bounds any lie
  to the gap between the two figures.
- **The supervisor instance stands outside the envelope
  boundary**: executions are now serialised mechanically (the
  per-room lock) and the CPU budget is run-cumulative, but the
  long-lived supervisor instance — a witnessing harness, not a
  worker execution — still shares the tree's filesystem without
  taking the lock and is witnessed, not warden-policed. The lock
  itself is a rig-level `flock`: it serialises the rig's own
  executions; it is not, and is not claimed to be, a defence
  against another host-side actor.
- Everything about the worker, the model, and the interface is
  other tracks' territory (A, C, D, E, G) and is untouched here,
  by design. Track G — attacking these mechanisms — remains a
  separate track that follows B.
