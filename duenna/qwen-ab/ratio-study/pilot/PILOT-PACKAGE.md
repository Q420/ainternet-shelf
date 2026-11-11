# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V2

Corrections per Alex's inspection of b07d18d (preserved
in git history): **(1)** pilot.py now contains the real
execution path — per-level flows on the frozen components
(R0 worker-only under constraints; R1/R2 support packets
from tools24; R3 post-verification via the frozen
checkers; R4 the frozen run_c machinery; T06 probe with
hard capture order at every level; stop rule writes
PILOT-STOPPED.lock). Compile-verified; matrix verified
(60 runs); unauthorised invocation verified REFUSED. The
execution path has NOT been exercised — its first live
use is the authorised pilot itself, under the stop rule.
**(2)** Seed corrected: eligibility ≠ correctness; T01/
T03/T08 entries withdrawn to UNKNOWN-UNTESTED; two WEAK
entries survive on adjudicated worker-level evidence.
**(3)** Binding extended to provider, model revision,
decoding, system-prompt hash, tools hash, adapter,
foundation version, Worker ID — all compared.
**(4)** Selection resolves to real versioned templates
(TEMPLATES registry, requires lists recorded) and FAILS
CLOSED to cold start on malformed/conflicting data —
fixture-verified in this round. **(5)** Derivation emits
the full audit structure (binding, level, adjudication,
critical failures, evidence refs, sample count,
confidence basis, provisional flag) and is reproducible
from adjudicated observation records.
**No runs executed. Awaiting re-inspection.**
