# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V7

Corrections per Alex's V6 re-inspection (e834f6e
preserved in history): **(1) The legacy safeguard now
actually operates.** The bug was real and silent:
extract_observations() stored binding_status inside
each observation's conditions, while derive_entries()
looked for it at the top level — so every historical
entry derived as "bound". Derivation now reads the
binding from wherever the observation carries it and
FAILS CLOSED: an entry is "bound" only when every
observation explicitly says so; missing or
inconsistent metadata derives legacy-unbound. The new
F-BINDING fixture asserts the full chain — historical
observations stay legacy-unbound, their entries stay
legacy-unbound, a legacy weakness still adds support
(template selected), a legacy demonstrated claim
cannot reduce coverage (cold start), and missing
binding metadata never becomes bound by default.
Regenerated MECHANISM-VERIFICATION.json shows both
entries as legacy-unbound with those exact selection
outcomes. **(2) External dependencies are explicit.**
The frozen production workflow resolves two data
sources through workspace paths — the corpus index
under ~/workspace/pulse-bridge/index and the shelf
manifest at ~/workspace/ainternet-shelf/MANIFEST.md.
Package V6's wording presented the demonstration as a
self-contained Shelf execution; that was too strong
and is corrected here. RUNTIME-DEMONSTRATION.json now
records each resolved dependency path with its
sha256 (and the groq transport path, marked stubbed /
not exercised). The outputs are regenerated from the
checked-in Shelf tree; the workflow's data sources
are workspace resources, recorded, not hidden.
All fixtures pass in both layouts. **No pilot runs,
no live model calls. Awaiting re-inspection.**
