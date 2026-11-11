# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V5

Corrections per Alex's V4 re-inspection (2f8234c
preserved in history): **(1) Reproducibility failure
closed at its root.** The committed F-PROBE output and
its fixture disagreed because the fixture stored a LIVE
list reference — later fixture calls kept appending to
the recorded order after the assertion had passed. The
fixture now snapshots its records, isolates its stubs
per fixture, and FIXTURES-OUTPUT.json is regenerated
from the exact committed source: the recorded probe
order is ["unaided", "revision"], and the assertions
and the output agree. **(2) Adaptive runtime now
EXECUTES.** run_adaptive_demo() passes the selected
configuration into an execution loop (stubbed worker,
labelled): the classification template runs the actual
probe sequence; the extraction template builds the real
packet, calls the worker with it, and runs the real
schema post-check; the cold-start configuration runs
with maximum packet + gate scoring. Calibration
(run_level's fixed matrix) and adaptive runtime remain
distinct mechanisms, both present. **(3) Evidence
identification is statement-specific**: a statement
counts only via a verbatim pack quote (>=16 chars,
substring-verified against the pack) or a grounded
absence (absence asserted AND the statement's artefact
term verifiably absent via pack_search). Generic words
never suffice; routes are recorded per statement; the
result stays labelled a mechanical measurement.
**Further point answered**: run_level's profile
selection now uses the task's actual operation class
(OP_CLASSES map) — no generic pilot-run class.
All fixtures pass against the regenerated output.
**No pilot runs, no live model calls. Awaiting
re-inspection.**
