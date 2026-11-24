# Vane — Track B rig build examination: RETURNED FOR CORRECTION (2026-11-24)

Received via Pulse Bridge (PB pb-mwv9ay89-9-d1qd), 2026-11-24. Filed at
INDEX 438. She examined all five committed rig files; she inspected the
source but did **not** independently execute the suite.

**Ruling: Track B is returned for correction. The rig is not passed as
evidence that the room is sealed, and this implementation is not to be
used for a worker demonstration yet.** The 12/12 suite is useful evidence
the rig behaves as tested; the gaps are in the witnesses and containment
guarantees themselves.

## The five findings

1. **The resource envelope is not adequate.** The cgroup limitation is
   correctly identified, but the rlimit fallback provides no aggregate
   room limit: RLIMIT_AS is per-process address space, RLIMIT_CPU is
   per-process, RLIMIT_NPROC binds the real UID rather than this room's
   tree, RLIMIT_FSIZE bounds individual files rather than total storage.
   Multiple processes can each consume their own allowance, and a worker
   could fill the host filesystem through its writable tree. **The room
   currently has no demonstrated aggregate memory, CPU, process-tree, or
   storage envelope.** Not acceptable for a first live demonstration —
   demonstration scale is fine, unenforceable is not.
2. **The mount witness must establish more than mount presence.** The
   suite does not establish that stock mounts are actually read-only, nor
   the mount-option and propagation properties behind that claim. The
   host-path leakage check searches the mount's root field, which is not
   generally the host source pathname — it cannot establish the absence
   of unintended host bind mounts. Required: source and destination
   identity, read-only vs writable status, propagation, **every** exposed
   mount including unexpected ones, and whether any host path is
   reachable beyond the declared stock — the allowed set derived from the
   declared construction, not accepted because expected points appear.
3. **The identity boundary is a documented adaptation, not equivalent
   isolation.** UID/GID drop, cleared groups, no-new-privs, and the
   zeroed capability bounding set are useful controls; they do not equal
   the intended user-namespace arrangement. The witness must capture the
   process's **actual** credentials and security state (UID/GID,
   supplementary groups, capability sets, NoNewPrivs, seccomp state) —
   what the process actually has, not inferred from the launch command —
   and the host must establish the room identity cannot interfere with
   unrelated host processes or another room.
4. **The execution path is not yet fully witnessed.** The witness's
   process-tree snapshot is not a continuous execution record; one-shot
   calls are separate namespace launches and a supervisor snapshot cannot
   establish that nothing escaped or survived between observations.
   Process creation, descendants, termination, timeout handling, and
   survivors must be accounted for across the actual execution path.
   **Practical defect: `Room.run` collects stdout/stderr with no output
   ceiling** — a worker can generate enormous output before the timeout.
   Bounded output capture is required, not merely a time limit.
5. **Persistence needs a precise definition.** The implementation
   preserves the filesystem between calls; each execution gets a fresh
   PID namespace and fresh processes. **Filesystem state persists;
   process and interpreter state do not.** The design must state the two
   properties distinctly and not silently claim one while implementing
   the other — whether the model's working pattern needs a persistent
   process/session or is satisfied by filesystem persistence is to be
   settled explicitly.

## What she accepts from the submission

The rig is offline and contacts no model or provider; construction and
destruction are separated from model interaction; the case tree persists
across calls; the host witness does not trust room-produced files; the
unconfined control shows the pre-flight detects at least the tested
reaches; the cgroup, user-namespace, and filesystem limitations are
reported honestly. "These are meaningful foundations. They are not yet a
passing boundary demonstration."

## Return direction

One coherent correction, not extra assertions making the implementation
look stronger than it is: establish a host environment capable of
enforcing aggregate resource limits, or select another mechanism that
genuinely provides them; strengthen the mount and identity witnesses to
establish actual kernel state; bound output and filesystem consumption;
establish process-tree containment and termination across real execution
calls; state precisely which forms of persistence the room supports.
Track G stays separate — B establishes the mechanism, G attacks it.

**Her distinction, recorded verbatim in substance:** "I am not asking you
to make this particular host's limitations disappear through configuration
or optimistic interpretation. If the host cannot provide the required
boundary, report that and propose the appropriate host or mechanism."

**No provider request or worker demonstration is released by this
examination.**
