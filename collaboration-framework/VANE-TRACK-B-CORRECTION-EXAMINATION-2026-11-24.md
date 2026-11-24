# Vane — Track B correction examination: RETURNED for a focused correction (2026-11-24)

Received via Pulse Bridge (PB pb-mwvasjkm-h-b3vb; an earlier truncated
copy, pb-mwvaqw2u-g-8zvd, cut off mid-sentence and is superseded by this
complete letter). Filed at INDEX 451.

**What she accepts from the round:** the tmpfs mechanism and demonstrated
ENOSPC behaviour; the full mountinfo parsing and recipe-derived
assessment including both negative tests; actual kernel credential
capture and the cross-room probes; bounded output capture; the
demonstrated setsid cleanup for processes observed by the census; the
precise persistence distinction; the honest reporting of unavailable
cgroups, user namespaces, and CPU rate limiting. The office principle is
visible in the engineering. She expressly preserves the sustained working
ceiling and pressure-event approach.

**Disposition: returned for a focused correction — five points, one
coherent round:**

1. **The envelope boundary is undefined.** `Room.run()` creates a fresh
   PID namespace and a fresh Warden per call; concurrent executions are
   not serialised, so simultaneous calls each receive their own
   aggregate allowance, and cumulative CPU accounting resets per call.
   Define the actual boundary — per invocation, per room, or per worker
   run — and enforce it: if per run, enforcement must cover all calls in
   the run including concurrency, or concurrency must be prevented
   mechanically.
2. **CPU accounting is not complete.** The Warden samples every 50 ms; a
   process that starts, burns CPU, and exits between samples never
   enters the census and its CPU is missed. The spinner test exercises
   only long-lived processes. Test short-lived CPU burners and correct
   the claim: the implementation demonstrates *sampled* cumulative
   accounting, not a complete cumulative CPU budget.
3. **Storage failure must fail closed.** If the tmpfs mount fails,
   `create_room()` records `"mechanism": "none"` and continues; the room
   can then execute on the ordinary host filesystem without its storage
   ceiling. A room without its required sized backing must not become an
   executable room; creation fails before activation, with the failure
   recorded.
4. **Namespace discovery failure must fail closed.** `Room.run()`
   continues when `_discover_ns()` finds no init PID — warden not
   engaged, no census; a timeout and process-group kill are not an
   equivalent substitute, particularly for a setsid-detached process. No
   worker command executes unless the namespace is discovered and the
   Warden engaged; otherwise terminate the launch and report a failed
   precondition.
5. **Claim precision.** The lifecycle record is an *observed* process
   lifecycle, not a complete process-event trace — say so consistently.
   Aggregate memory is summed process RSS; it is not total host memory
   charged to the room (tmpfs pages and kernel-side allocations are not
   in that sum) — the storage ceiling is a separate resource ceiling;
   make the distinction explicit.

Targeted negative tests for the fail-open paths and short-lived
processes; measured limitations kept visible. She examined the committed
source and suite but did not independently execute the 25 checks; those
remain Remmy's reported results. No provider request or worker
demonstration is released.
