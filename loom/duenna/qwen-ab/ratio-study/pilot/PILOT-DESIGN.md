# FEASIBILITY PILOT — DESIGN (construction package)

Built under Alex's authorisation (framing accepted,
2026-11-10). **Construction only — the 60 runs are NOT
authorised.** The driver refuses to execute without a
PILOT-AUTHORISATION.json issued after inspection, bound
to foundation c3b917fe… and framing commit 56fdaa6.

## Scope
Five levels (R0–R4 per OPERATION-MAPS-V2) × 12 entries
(T01–T08 + T09 ×4) = 60 executions, frozen packs,
feasibility + provisional calibration evidence only.
No saturation, superiority, or generalisation claims.
Stop rule in force throughout.

## How each level executes (driver: pilot.py)
R0: governed worker-only (reciprocal constraints in the
system prompt; independent J scorers). R1: + mechanical
pre-steps (location, integrity, parsing, role
classification, draft diagnosis) computed by the frozen
tools and supplied as a support packet. R2: + mechanical
extractions in the packet — the worker performs FROM
structured intermediates (class A). R3: R2 + mechanical
post-verification / classification. R4: the frozen Arm C
machinery (run_c) unchanged, capped per task where the
maps hold steps model-owned. The T06 adoption probe runs
at EVERY level with the hard capture order: unaided
worker labels first, independent mechanical
classification second, revised answer + evidence
explanation third — three records, never merged.

## Alex's five requirements, as specified here

**1. Profile derivation.** Per (task class, operation
class): DEMONSTRATED = observed with the worker correct
in every observation and no critical failure; WEAK = any
worker failure or critical failure; UNKNOWN-UNTESTED =
no observation (a first-class status, never inferred).
Derivation runs over adjudicated results only, is
mechanical (profile.py derive_entries), and at pilot
scale every derived entry is marked PROVISIONAL.

**2. Confidence.** A ladder: NONE / LOW / MEDIUM / HIGH.
LOW = pilot-scale adjudicated evidence (n=1 per cell) —
**the ceiling for anything this pilot produces; a single
result is never strong confidence.** MEDIUM requires ≥3
independent matched-variant observations, consistent,
adjudicated. HIGH requires replication across batteries,
adjudicated. Sample size, consistency, and adjudication
are the three inputs; missing any caps the rung.

**3. Selection.** profile.py select(): for each required
operation of a job — demonstrated → the map's allocation
for that operation; weak → the constraint template for
that weakness class (mechanical coverage raised one step
where the map allows); unknown or missing → cold start.
Every selection is recorded with its basis, per job, so
any allocation can be audited after the fact.

**4. Version binding.** The profile header records the
exact model string and the runtime configuration
(temperature, foundation hash). check_binding() refuses
a silent match: a changed model version or deployment
opens a new profile version; prior evidence is marked as
pertaining to the prior version, never inherited.

**5. Cold start.** No profile (or no entry) → the
conservative default: highest mechanical coverage the
map allows per operation, the full reciprocal constraint
set, adoption probes on all judgment classes, independent
scoring on every output. Unknown is treated as untrusted,
never as capable; evidence accrues from there.

## Mechanism verification (part of the pilot)
Beyond calibration: the pilot must show a profile can be
written from its evidence in this schema, that selection-
from-profile reproduces intended allocations (checked
against the seed profile + worked example in this
package), and that records are complete enough to
adjudicate entries from.
