# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V3

Corrections per Alex's inspection of 5f07030 (preserved
in history): **(1)** Imports resolve in both the
workspace layout and the shelf layout; resolved paths
are recorded in every run record (F-IMPORT fixture).
**(2)** Pack items handled as the frozen (id, text)
tuples; R1/R2 packets built by the tools' native tuple
interfaces (F-R1R2 fixture over the real T01 pack).
**(3)** The T06 probe no longer calls the absent
check_t06_labels — a pilot-local label extractor scores
probe records; the frozen gate scorers still score the
task response (F-PROBE fixture, stubbed, verifies the
three-record structure + capture order). **(4)** The
profile mechanism is exercised in the driver itself:
--verify-mechanism derives entries from the adjudicated
V1/V2R observation records, validates, binds, selects,
and writes MECHANISM-VERIFICATION.json (run this round:
binding OK, no defects, T05/T06 weak at LOW).
**(5)** Confidence consistency enforced in code: any
failure caps at LOW at any n; MEDIUM requires n>=3
consistent + adjudicated (F-PROFILE fixture).
**(6)** Measurement accounting explicit: every model
call is logged per run with its purpose (scored-task-
response / probe-unaided / probe-revision); probe
records are typed "adoption-probe (not scored)" and
kept separate from the scored response at every level
including R4.
All four fixtures pass (FIXTURES-OUTPUT.json). Driver
compile- and refusal-verified. **No pilot runs executed.
Awaiting re-inspection.**
