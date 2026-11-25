# Track B test rig — notes (2026-11-24, correction round 3)

Offline only: nothing here talks to a provider or a model. Built under
`ENVIRONMENT-DESIGN-REV2-2026-11-24.md` and Track B of
`ROOM-TEST-PROGRAMME-2026-11-24.md`. Correction round 1 answered
Vane's build examination (INDEX 438): an aggregate envelope, a mount
witness that proves properties, identity read from the kernel,
bounded output, exact persistence terms. Round 2 answered her
correction examination (INDEX 451): the envelope boundary defined as
the worker run, CPU accounting reconciled with an in-room reaper,
both fail-open paths closed. **This round (round 3) answers her
second correction examination (INDEX 453), which returned round 2 on
three integrity findings**: the CPU ledger had a fail-open read path
(and a silently-dropping write path); end-of-call reaper accounting
was enforcement language for what is only accounting, with the CPU
contract not stated exactly; and the storage precondition trusted
the recorded label rather than the live mount. A fourth item is
documentation only, at Ben's direction: an explicit scope statement
for the per-room serialisation (see "Scope of the serialisation").
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
| `test_rig.py` | The suite: 34 checks, including the round-1 control run, two deviant-room negative tests for the mount assessment, the warden's enforcement demonstrations, round 2's boundary, accounting, and fail-closed tests, and round 3's ledger fail-closed negatives, the budget-crossing overshoot test, and the replaced-mount negative. |
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
    [--ro-bind <tree>/work/sources /room/work/sources]   (utilise-only
        stock, where the room is stocked with briefcase sources —
        see "Utilise-only stock" at the end of these notes)
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
     rate limit and **not a hard execution ceiling** — the exact
     contract is stated under "CPU accounting (round 2, point 2;
     round 3, point 2)" below. In flight, the warden trips when the
     census-observed run total crosses it.
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

### The ledger is authority: it fails closed (round 3, point 1)

Round 2 put the run's CPU accounting in the state file's ledger —
and left two fail-open paths in it: `_ledger_consumed()` defaulted
to 0.0 when the state could not be read or parsed (corruption
became a fresh full allowance), and `_record_execution()` silently
returned when it could not read the state (an execution could
complete with its charge never recorded). Round 3 closes both:

- **Read path.** `_ledger_consumed()` raises `LedgerError` on an
  unreadable, malformed, or missing state/ledger — a missing
  `cpu_ledger`, a non-object state, or a malformed
  `consumed_seconds` all refuse execution with the failed
  precondition `cpu-ledger`. It never defaults.
- **Write path.** A failed ledger update — the state unreadable,
  the update unbuildable, or the write itself failing — is
  preserved explicitly in a **ledger-failure record**:
  `<base>/<name>.ledger-failure.json`, a sibling of the state file
  chosen so the record survives the state file itself being the
  thing that failed. Each record names the operation, the failure,
  and (for a completed execution) the charge that could not be
  recorded. The room is also poisoned in-process.
- **Blocking.** `Room.run()` refuses every execution while a
  ledger failure stands — the in-process poison flag, or a failure
  record on disk (including one left by an earlier process). The
  refusal itself is appended to the failure record, not routed
  through the untrusted state. Clearing the block is an operator
  act: reconcile the record, then remove it.

Negative tests prove both paths: a state file corrupted after
creation refuses the next execution (its marker is never written)
with a `ledger-read` failure on record; and with the state-write
seam forced to fail, a real execution completes, its unrecorded
charge (0.35 s in the suite runs) is preserved in the failure
record as a `ledger-update-write` entry, and the next execution is
refused.

### Scope of the serialisation (round 3, point 4 — Ben's direction)

Stated explicitly, so the mechanism is never read as more than it
is: **the per-room lock serialises ONE worker's executions inside
its OWN room only. It is not a framework-level constraint.** Each
agent holds its own room, and agents work concurrently — nothing
in this rig serialises one room against another. This rig is the
single-worker room case: one worker, one room, its calls ordered
so the run's envelope is well-defined. A shared multi-occupancy
workspace — a crew of agents working one tree together, as the
collaboration design contemplates — is a named **open design
question**. This rig does not settle it, and the per-room lock
must not be read as settling it (in either direction: neither as
the framework's concurrency model, nor as evidence against one).

### CPU accounting (round 2, point 2; round 3, point 2)

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

**The CPU contract, stated exactly (round 3, point 2).** The
reaper's end-of-call recovery is accounting accuracy, not
enforcement at the instant of crossing: if a short-lived call
crosses the remaining budget and finishes between census polls,
the overspend is discovered only when the call ends — the
completed work cannot be undone. So, in exactly these terms (the
same sentence is carried in the module docstring, the state's
envelope record, and the ledger itself): **the CPU limit is a
cumulative accounting budget, not a hard execution ceiling —
in-flight enforcement acts on what the census observes; work that
completes between observations can exceed the budget; the excess
is charged exactly and further calls are refused.** No wording in
this rig claims a hard CPU ceiling, because this host cannot
enforce one. The suite's adversarial test demonstrates the case
itself: with a 0.9 s budget and a deliberately slow 2 s census, a
first call burns ~0.53 s and exits; a second call — twelve parallel
burners, 0.64 s of CPU in well under one census interval — runs to
completion (`burst-done`, no envelope termination; the census saw
0.01 s of it), the reaper charges its exact 0.64 s at call end for
a run total of ~1.17–1.18 s (**~0.27–0.28 s over the budget,
charged, not undone**), and a third call is refused before
execution.

### Fail-closed preconditions (round 2, points 3 and 4; round 3, points 1 and 3)

- **Storage.** If the sized tmpfs mount fails at creation, creation
  itself fails: a failed-precondition record
  (`failed: true, executable: false, failed_precondition:
  "storage-tmpfs-mount"`, with the mount error) is written to the
  room's state path, the just-created tree directory is removed, and
  `create_room()` raises `RoomCreationError`. `load_room()` raises
  on such a record. There is no code path where a room executes on
  the host filesystem without its storage ceiling. Negative test:
  creation with an impossible size parameter (the mount genuinely
  fails at the real seam) raises, records, and leaves neither a
  loadable room nor a tree.
- **Storage, verified live (round 3, point 3).** Round 2's
  execution-time check trusted the recorded label
  (`mechanism == "tmpfs-sized"`) — it established what was mounted
  at creation, not what backs the tree when execution begins.
  Creation now also records the mount's identity (mount id and
  device from the host mount table, beside the declared size), and
  the precondition is verified against the **live** mount table:
  `Room.run()` — and `load_room()`, where it gates executability —
  require a mount to exist at the tree path, of type tmpfs, with
  the recorded mount id and device, and with the declared total
  size (statvfs). A removed, replaced, or changed mount fails
  closed with the failed precondition `storage-backing`, the live
  discrepancy named. Negative test: a room is created, executes
  once cleanly, its tmpfs is then unmounted (leaving the plain
  directory), and the next execution refuses against the live
  table — the command's marker is never written — and
  `load_room()` raises.
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
- **Rig integrity (Track G closure, 2026-11-24).** The in-tree rig
  instruments — `rig/reaper.py` and `rig/preflight.py` — live in the
  worker's own tree, writable by the room uid, and every execution
  runs under the tree's reaper copy: a hostile worker could rewrite
  the reaper its *next* execution runs under (Track G finding
  `g-reaper-tamper`). Before every execution, host-side, alongside
  the storage and discovery preconditions, `Room.run()` verifies
  each instrument's current SHA-256 against the hash recorded in
  the room's stock manifest at creation. A changed, missing,
  unreadable, or unrecorded instrument refuses the execution with
  the failed precondition `rig-integrity`; the tamper is recorded
  in the room state as a rig-integrity event (file, expected hash,
  actual hash or absence) and in the refused execution's record.
  Refusal + record is the contract: nothing silently restores the
  file — an operator, or a fresh stocking, does. Negative/positive
  test (Track G): a forged reaper refuses the next execution with
  both hashes on record and the command's marker never written;
  after the operator restores the genuine reaper, execution
  proceeds cleanly.
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
- **CPU budget** (3.0 s budget, three long-lived spinners the
  census observes in flight): killed at a measured 3.03–3.13
  cumulative CPU-seconds. **Run-cumulative**
  (2.0 s budget, two ~1.23 s calls): the second call killed at a
  measured run total of ~2.04 s; a third call refused unspent.
- **Short-lived burners** (40 × 25 ms CPU, each inside one census
  interval): reaper captured 100.5% of the rusage ground truth in
  both runs; the census identity captured 97.8% and 101.1%. See
  "CPU accounting" above for exactly what is claimed.
- **Budget-crossing burst** (round 3; 0.9 s budget, 2 s census):
  a 0.64 s parallel burst completed between polls (census saw
  0.01 s of it), was charged exactly by the reaper at call end,
  and left the run ~0.27–0.28 s over budget with the next call
  refused — the accounting-budget contract, demonstrated. See
  "CPU accounting".

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

`python3 test_rig.py` — **34 passed, 0 failed**, twice consecutively
(control, stocking, supervisor, mounts, mounts-extra, mounts-rw,
network, environment, namespaces, identity, cross-room,
envelope-record, preflight, persistence, persist-terms, ward-mem,
ward-spike, ward-fastspike, ward-pids, ward-forkfast, ward-cpu,
serialise, cpu-run, cpu-shortlived, cpu-overshoot, ledger-read-fail,
ledger-write-fail, storage-fail, ns-fail, mount-replaced, storage,
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
- **A hard CPU execution ceiling**: not established, and not
  claimed. The CPU limit is a cumulative accounting budget (see
  "CPU accounting" for the contract in its exact terms): work
  that completes between census observations can exceed the
  budget before the excess is charged at call end. A hard ceiling
  would need a kernel mechanism (cgroup cpu.max) this host does
  not delegate.
- **A ledger failure whose record cannot be written either**: if
  the state write fails AND the ledger-failure file cannot be
  written (the base directory itself unwritable), the failure is
  preserved only in the failing process's poison flag — that
  process refuses all later executions, but a fresh process would
  read the stale state and not know. Both writes failing means
  the room's host-side record directory is broken wholesale,
  which creation and every other record operation would also
  fail against; the residual is stated, not hidden.
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

## Utilise-only stock — the sources bind (2026-11-24, after correction round 3)

Ben's ruling (2026-11-24 18:56 MST): "access doesnt mean
overwrite. it means utlilize" — the briefcase's stock is
utilise-only for the worker. The doorway side already conformed
(no write grant touches `sources/`); the room did not: the tree
was bound read-write whole (`--bind <tree> /room`) and creation
chowned every stocked file to the room uid, so a worker's exec
could overwrite `work/sources/*` and the change persisted (the
combined rehearsal's witness demonstrated it: sources/
stock-take.md sha256 ecb91902… → b2d545a8…).

**The mechanism.** Where a room is stocked with briefcase
sources (any stock path under `sources/`), creation declares
one more mount in the room's recipe — mount point
`/room/work/sources`, kind `sources-ro-bind`, access `ro` —
and `Room.bwrap_cmd` builds it in every execution: after the
main tree bind, the sources subtree is bound read-only over
itself (`--ro-bind <tree>/work/sources /room/work/sources`).
The host witness verifies the mount from the kernel record
like every other: presence, source identity (device + root of
the tree's `work/sources` within the mount backing the tree),
and `ro` in its options.

**The property, stated precisely.** Inside every execution of
such a room, the stocked sources subtree is read-only at the
room wall: create, modify and delete under `/room/work/sources/`
fail at the kernel (`EROFS` — "Read-only file system"); the
sources directory itself is a mount point and can neither be
removed nor renamed from inside (`EBUSY`); a remount to
read-write would need CAP_SYS_ADMIN, which the construction's
zeroed capability bounding set withholds. Reads are unaffected.
Everything outside the subtree — `/room/scratch` above all,
and any other stock the room carries — keeps exactly the
access it had: the worker's own space stays writable. The
stocking smoke set is unchanged and passes (it reads the
sources and writes its probe in scratch). The combined
rehearsal's utilise-only witness now passes: the scripted
overwrite attempt is dispatched, executes, fails against the
read-only mount (its stderr names it), and the source's
SHA-256 stands unchanged. Track G's `g-conf-selfdelete` case
was updated to the property it now meets: the delete attempt
fails against the stock and is contained, the sources read
back whole, the record intact — the count of checks is
unchanged.

**What this does not cover.** The protection attaches to the
`sources/` subtree — the briefcase's stock as the framework
stocks it. Stock placed anywhere else under `work/` (no
current stocking does this; the demonstration stocks only
`sources/`) remains writable by the worker, as does everything
in `scratch/` by design. The bind is per-execution namespace
construction, re-applied at every call; it does not change the
tree on the host, where the office's own acts remain the
office's. A worker can still fill his storage ceiling or wreck
his own scratch — his space, his mess; the stock is what he
may no longer touch.
