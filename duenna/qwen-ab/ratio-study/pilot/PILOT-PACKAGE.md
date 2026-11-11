# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V4

Corrections per Alex's V3 re-inspection (d016d94
preserved in history): **(1)** Imports are HASH-VERIFIED
before use — resolved run_ab/run_c/tools24 must match
the pinned frozen hashes in either layout; F-IMPORT now
exercises BOTH layouts in subprocesses. (The shelf's
duenna/qwen-ab/run_ab.py was the V1-era copy; it is
updated in this round to the current frozen scorer
source — the V1 copy remains in git history — so both
layouts resolve to the identical frozen file. tools24
and run_c shelf copies already matched.) **(2)**
Derivation reads the ACTUAL adjudicated records:
extract_observations() parses QWEN-AB-RESULTS.json and
QWEN-AB-V2R-RESULTS.json, locates the T05 first-attempt
blocks and the T06 worker_vs_system record, and emits
observations carrying conditions + resolvable references
(file, sha256, record locator). **(3)** Selection is
wired to execution two ways: per-run, when a profile is
present, run_level records the profile selection
alongside the calibration level (the distinction stated
in the record); and --demonstrate-runtime runs the full
loop — profile → selection → template-resolved execution
configuration → demonstration record
(RUNTIME-DEMONSTRATION.json, stubbed worker, labelled).
**(4)** Fixtures test what they claim: F-R1R2 over the
multi-item mixed T03 pack (sections + fixture, both
extraction routes); F-PROBE asserts the capture ORDER
and the revised labels + evidence flags; F-PROFILE
covers derivation-from-records and the consistency
branches. (One fixture assertion was itself corrected
this round: it demanded >3 pack items where the frozen
T03 pack has 3 — the property is multi-item mixed
handling, and the assertion now says so.) **(5)** The
probe records worker_after labels, per-statement
evidence identification, and a mechanical adoption
measurement (adopted / already-aligned / resisted /
unclear) beside the three preserved records. **(6)**
Call accounting is total: pilot wraps run_ab.call_qwen —
which run_c invokes by attribute — so Arm C internal
calls land in the same per-run manifest with purpose,
usage, latency (F-CALLS fixture).
All fixtures pass. **No pilot runs executed. Awaiting
re-inspection.**
