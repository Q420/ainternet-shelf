# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V6

Corrections per Alex's V5 re-inspection (5a0fea3
preserved in history): **(1) Reproducibility, closed
properly.** profile.tools_version() resolved a path
that exists only in the workspace layout. It now
resolves tools24.py BY HASH across both layouts, as
does every import. **All committed outputs in this
package were regenerated from the checked-in shelf
layout itself** — exact invocation: cwd =
duenna/qwen-ab/ratio-study/pilot/ in the repository
tree; `python3 pilot_fixtures.py`,
`python3 pilot.py --verify-mechanism`,
`python3 pilot.py --demonstrate-runtime`; no layout
env vars set (defaults resolve the shelf tree);
Python 3.12, stdlib + the frozen modules only.
F-IMPORT exercises both layouts via explicit root
overrides (PILOT_WS_ROOT / PILOT_SHELF_ROOT). Three
fixture-side path defects found during regeneration
were fixed in the open and are part of this commit's
history of work. **(2) The T05 template now performs
its whole declared workflow** — the branch runs the
frozen production construction (run_c.t05_record):
shelf_lookup + source_extract -> reference_insert for
every field -> verify_field per field + cross-record
agreement -> worker emission -> schema check. Result
in the regenerated demonstration: insertion ledger
8/8 PASS, all fields verified, emission schema 8/8.
A defective emission is covered separately by the
F-ADAPTIVE-NEG fixture (post-check catches it).
**(3) No worker call is called mechanical.** The
frozen c_t06 flow runs for real in the probe and the
demonstration (transport-level stub only); its
internal worker call is captured by the accounting
wrapper, itemised in the probe record's flow_calls,
and explicitly classified there as a worker call —
the probe uses only the flow's classification
sub-record and discards its report. **(4) Historical
evidence is bound honestly.** V1/V2R observations now
carry binding_status "legacy-unbound": model, battery
and adjudication are established; the historical
system-prompt hash, deployment record and tool
versions are NOT recoverable from the frozen records,
and the observations say so. The selection rule for
legacy evidence is one-directional: it may justify
ADDING support (a weakness hypothesis selects its
template) but never REDUCING coverage (a legacy
"demonstrated" claim resolves to cold start).
All fixtures pass in both layouts. **No pilot runs,
no live model calls. Awaiting re-inspection.**
