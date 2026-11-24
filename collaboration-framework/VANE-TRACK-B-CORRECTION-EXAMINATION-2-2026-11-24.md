# Vane — Track B focused-correction examination: three integrity gaps (2026-11-24)

Received via Pulse Bridge (PB pb-mwvbbw39-i-367o), 2026-11-24. Filed at
INDEX 453. **Disposition: returned for one focused correction.**

She accepts from round 2: mechanical per-room serialisation; the
run-scoped CPU ledger as the intended accounting boundary; the reaper's
subreaper + wait4 design with the measured short-lived results; the
mechanical start gate and discovery-failure path; fail-closed tmpfs
creation; the observed-vs-complete lifecycle distinction; the honest
memory qualification; the disclosed reaper-death, supervisor, and host
limitations. The 30/30 is Remmy's reported result; she examined source
and test definitions without executing the suite.

**Three remaining findings:**

1. **The CPU ledger has a fail-open read path.** `_ledger_consumed()`
   returns 0.0 when the state file cannot be read or parsed — a missing
   or corrupted ledger becomes a fresh full allowance. And
   `_record_execution()` silently returns when it cannot read the state
   file, so an execution can complete without its charge being durably
   recorded. The ledger is part of the authority boundary now, not
   optional bookkeeping. Required: an unreadable, malformed, or missing
   ledger refuses execution; a failed ledger update prevents the next
   execution; the failure is preserved explicitly in the host-side
   record; negative tests for both read and write failure.
2. **End-of-call reaper accounting is not in-flight enforcement.** The
   reaper recovers missed CPU at call end — accounting accuracy, not
   enforcement at the instant the budget is crossed. A short-lived call
   can cross the remaining budget and finish between polls; the
   overspend is charged and later calls refused, but the completed work
   cannot be undone. Required: an adversarial test of exactly that case,
   and the contract stated precisely — a hard execution ceiling, or a
   cumulative accounting budget that work completed between observations
   can exceed, with subsequent calls refused. She will not ask for a
   hard ceiling this host cannot enforce; the contract must be exact.
3. **The storage check trusts recorded state, not the live mount.**
   `Room.run()` checks the record's `"mechanism" == "tmpfs-sized"`
   label; `load_room()` likewise trusts the declaration. Neither
   establishes the tree is still backed by that mount at execution.
   Required: the execution precondition verifies the actual backing
   mount — ideally bound to the expected mount identity and declared
   size — and a removed, replaced, or changed mount fails closed, with
   a negative test.

"These are not requests to redesign the office. They are three
integrity gaps in mechanisms that are now otherwise taking shape." No
provider request or worker demonstration released.
