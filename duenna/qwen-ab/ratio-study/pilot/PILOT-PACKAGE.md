# FEASIBILITY PILOT — CONSTRUCTION PACKAGE V8

Corrections per Alex's V7 re-inspection (02dfefc
preserved in history): **(1) Binding declarations must
agree unanimously.** _binding_status() returned the
first declaration it found, so a top-level "bound"
could override a nested "legacy-unbound". The resolver
now inspects every supplied declaration: "bound"
requires at least one declaration and unanimity;
conflict, absence, or any non-bound declaration
resolves legacy-unbound. F-BINDING gains the
conflicting-declarations case: the derived entry stays
legacy-unbound and cannot reduce coverage.
**(2) The T06 probe now retrieves the real mechanical
classification.** The frozen c_t06 returns it at
process.system_classification; the probe read the top
level and got null — so V7's demonstration showed
mechanical: null, the revision call received null, and
every adoption measurement was "unclear". The
extraction is corrected, and F-PROBE no longer fakes
c_t06: it runs the REAL frozen function with only the
transport stubbed, and asserts the classifications are
non-null for S1–S4, that the revision call receives
them, that the three records stay separate, that
adoption is calculated, and that the flow's internal
worker call is accounted. Regenerated outputs show
the mechanical record matching the ruled key (S1
SUPPORTED · S2 UNTRACEABLE · S3 UNTRACEABLE · S4
CONTRADICTED) in both the fixture and the runtime
demonstration, with adoption measured rather than
unclear. All fixtures pass in both layouts.
**No pilot runs, no live model calls. Awaiting
re-inspection.**
