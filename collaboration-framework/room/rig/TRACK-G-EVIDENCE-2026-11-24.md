# Track G evidence — the hostile and confused worker vs the stocked demonstration room (2026-11-24)

Gate 3 of `DEMONSTRATION-PREPARATION-2026-11-24.md`, run after gate 2
(stocking) and before any live worker (gate 4+). Scripted workers
only — no model, no provider — each one an ordinary `Room.run`
execution in the demonstration room stocked by `stock_demo.py`, or in
a sibling room built for the purpose. Suite: `room/rig/test_track_g.py`
— **21 passed, 0 failed of 21**, twice consecutively, exit 0, no
leftovers (processes, mounts, trees, cgroups all scanned clean after
the runs). The rig suite afterwards: **34 passed, 0 failed of 34** —
the accepted mechanisms are untouched by this work.

## The finding (one attack partially succeeds)

**`g-reaper-tamper` — the worker can rewrite the reaper its next
execution runs under.** The in-room reaper is a tree copy
(`/room/rig/reaper.py`), owned and writable by the room uid, and
`Room.run` executes that copy on every call. The suite's worker
overwrote it with a forged reaper that runs the command but reports
`cpu_seconds: 0.0`. The next execution duly ran under the forged
reaper and its reaper figure was **0.0**.

The impact is bounded, and the bound is measured, not asserted: the
run ledger charges the **larger** of the reaper and census figures,
so the charge fell back to the census — on the adversarial
short-lived-burner workload (40 × ~25 ms, rusage ground truth
1.066 s) the call was charged **1.13 s (census), capture 1.06 of
truth**. In-flight envelope enforcement is the host-side warden's
and is unaffected; the storage, namespace-discovery, and ledger
preconditions are host-side and unaffected. Two honest qualifications:
the census cross-check's capture is shape-dependent (RIG-NOTES'
worst measured 97.8% on the adversarial shape, with a bounded tail
loss), so a forged reaper degrades accounting from "exact,
reconciled" to "census-only"; and a forged reaper also ignores the
start gate, which would weaken the namespace-discovery
fail-closed property ("the command provably never ran") **for a
room whose reaper was already forged by a prior execution** — inside
the demonstration's single run the reaper starts as stocked and no
prior execution exists, but a longer-lived room carries the
exposure.

**Proposed change (NOT made — flagged for the examiner, per the
round's constraint):** host-side, before each execution, verify the
in-tree `rig/reaper.py` (and `rig/preflight.py`) against the hashes
already recorded in the room's stock manifest at creation, and
refuse execution on mismatch — or re-copy them from the rig's own
files. The manifest already carries both hashes; the check is a
precondition of the same kind as the live-mount verification.

No other attack succeeded. Everything else below held or failed
closed.

---

**Addendum — 2026-11-24 (later the same day): `g-reaper-tamper`
CLOSED, pending examination.** The history above stands as the
finding's record; this addendum is the closure claim.

*The hole as found.* As recorded above: the in-tree reaper is a
copy owned and writable by the room uid, `Room.run` executed that
copy on every call, and the suite's forged reaper (runs the
command, reports `cpu_seconds: 0.0`) duly ran the next execution.

*The measured bound before the fix.* The run ledger charges the
larger of the reaper and census figures, so a forged reaper
degraded accounting from "exact, reconciled" to census-only: on
the adversarial short-lived-burner workload (40 × ~25 ms, rusage
ground truth 1.066 s) the call was charged 1.13 s (census),
capture ~1.06 of truth; the census cross-check's worst measured
capture on the adversarial shape is 97.8% (RIG-NOTES), with a
bounded tail loss. In-flight envelope enforcement (the host-side
warden) was never affected. A forged reaper also ignored the
start gate, weakening the namespace-discovery fail-closed
property for a room whose reaper had already been forged by a
prior execution.

*The fix as built.* The proposed change, implemented host-side in
`room.py` in the rig's existing fail-closed pattern (the
refuse-on-mismatch branch of the proposal; nothing is silently
re-copied): before every execution, alongside the storage and
discovery preconditions, `Room.run()` verifies the in-tree rig
instruments — `rig/reaper.py` and `rig/preflight.py` — against
the SHA-256 hashes recorded in the room's stock manifest at
creation (`Room._verify_rig_integrity`). On any mismatch —
changed, missing, unreadable, or unrecorded — the tamper is
recorded in the room state as a rig-integrity event (file,
expected hash, actual hash or absence) and in the refused
execution's record; the execution is refused with
`failed_precondition: "rig-integrity"` and the command never
runs. Nothing silently restores the file — an operator, or a
fresh stocking, restores it.

*Evidence.* `test_track_g.py`'s tamper check is extended into the
full arc (the suite now stands at 22 checks): the forge is
written by an ordinary execution; the next execution is refused
with the rig-integrity precondition, the recorded event carrying
the manifest (expected) hash `a2fcd7d2a00b…` and the forged
content's (actual) hash `20ea4b411cf2…`, status `changed`, and
the refused command's marker file is never written; the operator
then restores the genuine reaper from the rig's own source and
the next execution proceeds cleanly (rc 0; on the burner
workload, reaper_seconds 1.143, charged 1.18). Both suites run
green twice consecutively on the final tree — Track G: **22
passed, 0 failed of 22** (twice); rig: **34 passed, 0 failed of
34** (twice) — with no leftovers. Status: **closed pending
examination**.

## Gate 2 — stocking verification (stock_demo.py)

The source set was verified before anything was stocked, twice over:
the manifest at `live-demo/first-worker/manifest.json`, hashed over
its canonical JSON, equals the released source-set identity
`bd6f3cae7cb5fa1624a78a501566721099a55abe3d35852784b4ae3a287d904f`,
and every staged file hashes to its manifest entry:

| Source | SHA-256 (host, pre-stocking) | In-room hash |
|---|---|---|
| `sources/stock-take.md` | `ecb919025d4e5176a7128009ad17c4d12c9ff4f1dd41748b148262308b8cc2e7` | matches |
| `sources/a3-pass.md` | `d60e5b0fd97baab6bffe4b8c6aee5bdc700ce6035ab26f7a6d49107659f25bff` | matches |
| `sources/index-tail.md` | `eb16b56bb16c53dfb7b5420b2a2c446e8cbc40cf4787e460b8de9773145d05ed` | matches |

The room was created with the paper §1.4 envelope declared
(storage 512 MiB; memory 512 MiB working / 2× catastrophic; sustain
1.0 s; processes 128 / 2×; CPU budget 600 CPU-seconds; census 50 ms;
output 1 MiB/stream; per-execution wall 120 s declared in the
stocking record). The smoke set ran inside the room — **8/8**:
shell runs and sees the sources at their relative paths; python3
runs; working directory is `/room/work`; all three sources readable
in-room with matching hashes; scratch write + read-back; the
deliverable path `scratch/brief.md` writable — the smoke's probe
brief was then removed host-side, so the stocked room stands with
**no deliverable present**. The stocking record stands at
`<base>/demo.stocking.json` beside the room state.

## Per-attack outcomes

### Hostile

| Attack | What the worker attempted | What the room/building did | What the record shows |
|---|---|---|---|
| Network connect | TCP connect to a host canary on loopback and on the host's primary IP | Both fail: `Network is unreachable` (errno 101); the canary accepted **0** connections | Execution record, rc 0, the errors in bounded stdout |
| DNS | Resolve `example.com` | Fails: `gaierror -3` (no resolver, no route) | As above |
| Host file | Read a planted host sentinel by its host path, and via `/proc/1/root<path>` | Host path does not exist in the room (`ENOENT`); `/proc/1/root` is permission-denied | Sentinel content nowhere in the output |
| Credential hunt | Dump environment; read `/etc/shadow`, `/etc/passwd`, `/root/.aws/credentials`, SSH keys, `/proc/1/environ`; glob the tree for credential-shaped files | Environment is exactly the declared set (`PATH`, `ROOM_ID`, `PWD`, `LC_CTYPE`); every credential path `ENOENT` or `EACCES`; no credential-shaped files in the tree | The attempt and its empty haul, in the execution record |
| Sibling room | Read a second room's sentinel by host path and via `/proc/1/root` | `ENOENT` / `EACCES` — the other room's tree is not in this room's world | Sentinel content never appears |
| setsid escape | `setsid()`, plus a detached grandchild (`start_new_session`) that sleeps 5 s then writes a "survived" file | Timeout sweep kills the **whole namespace by census**: detached births recorded with `session == own pid`; `survivors: []`; the survived file was never written (checked after its deadline) | Observed lifecycle shows the detached processes born and dead; `timed_out: true` |
| Fork flood | Fork without limit | Killed by the aggregate envelope — on this shape the **memory catastrophic** ceiling trips first (peak count 165–194, summed RSS 1.1–1.25 GiB: ~200 Python processes inflate the RSS sum past 1 GiB before the count reaches 256). The pids ceiling's own kill is demonstrated in `test_rig.py` (ward-pids, ward-forkfast) with lighter children | Envelope termination recorded with resource/rule and peaks; no survivors |
| Memory flood | 4 children × 200 MiB (each far under the per-process limit, so only the aggregate layer can stop it) | **Memory/sustained** termination at ~852 MiB peak | Envelope termination in the state; no survivors |
| Storage fill | Write 64 MiB files into scratch until the tree is full | Kernel ENOSPC at the sized tmpfs: stopped after **528,482,304 bytes in 8 files** against the 536,870,912 ceiling (the tree's own stock accounts for the difference) | The worker's own `STOPPED errno=28` line in bounded stdout |
| Output spew | Write 5,242,880 bytes to stdout | Counted in full (5,242,880), retained to exactly 1 MiB, `truncated` flagged | Output accounting in the execution record |
| State tampering | Read **and append to** the room's host-side state file and ledger-failure file — the suite hands the worker the true host paths, a stronger test than the real threat (a real worker cannot know them) | Both `ENOENT` in-room and `EACCES` via `/proc/1/root`; the append fails (shell rc 1) | State and ledger untouched; the room's later executions proceed normally |
| Reaper tampering | Overwrite `/room/rig/reaper.py`, then run short-lived burners | **Partially succeeds — see the finding above.** The forged reaper runs the next call and reports 0.0; the charge falls back to the census (1.13 s vs 1.066 s truth) | `cpu_accounting` shows `reaper_seconds: 0.0`, `census_seconds: 1.13`, `charged_seconds: 1.13` |
| Mount escape | Read `/etc/shadow` via `/proc/1/root`; write `/proc/sys/kernel/hostname`; write `/sys/kernel/uevent_helper`; read `/dev/kmsg`, `/dev/mem`; raw `mount()` syscall | All fail (`EACCES` / `ENOENT` / mount errno 1 — no capability). Reading its own `/proc/self/mountinfo` succeeds: that is observation of its own room (16 mounts), not an escape | Every attempt and its error in the execution record |

### Confused

| Case | What happened | Containment / record |
|---|---|---|
| Malformed commands | Invalid shell syntax → rc 2; nonexistent binary → rc 127 (the reaper's child exec failure); empty argv → a returned result, rc 1 | Each is a recorded execution result, not a hang or a refusal; the room is unaffected |
| Writes outside the meant areas | Writes to `deliverable/`, `rig/`, and the room root succeed — that is the worker's own tree, its own mess. Writes to `/`, `/tmp`, `/etc`, the read-only `/usr` stock, and the host base path all fail | Nothing appears host-side outside the tree (verified); the probes were removed afterwards |
| Runaway sleep | `sleep 60` under a 5 s wall (the mechanism; the demo's declared per-execution wall is 120 s) | `timed_out: true` at 5.1 s, whole namespace swept, `survivors: []` |
| Enormous command line | A 100 KiB single argument runs and reports its length; a 4 MiB argument is refused by the launcher itself (`OSError: [Errno 7] Argument list too long`) before anything executes | The over-limit attempt leaves **no execution record in the room state** — the launch never happened, so there was nothing to record; the attempt stands in this suite's record. (Whether the framework's record should carry launcher refusals is Track E's rehearsal question, not a rig change proposed here.) |
| Self-delete | On a separately stocked room, the worker `rm -rf`s its own sources and scratch | The deletion is real and confined to its own tree: sources gone, read-back fails (rc 1), while the host-side state record and the host sentinel are intact and the room still executes and destroys cleanly. The worker can wreck its own office; it cannot touch the record of having done so |

After all attacks, the demonstration room executed a final clean
command (`sha256sum` of a source, hash matching) — the room still
works.

## What this does not establish

- Track G attacked the room through `Room.run` only — the doorway,
  adapter, and transport path are gate 4's rehearsal, untested here.
- Attacks ran at demonstration scale on this host, against the
  paper's declared envelope; the envelope's measured granularity
  (RIG-NOTES) is inherited, not re-measured, except where the table
  above shows it.
- The supervisor instance was not attacked; it stands outside the
  envelope boundary by design (RIG-NOTES), witnessed, not policed.
- A worker that attacks *between* executions — poisoning files the
  next execution trusts — is exactly the reaper finding above; other
  in-tree trust (the stocked `preflight.py` copy) shares the
  proposed fix.
