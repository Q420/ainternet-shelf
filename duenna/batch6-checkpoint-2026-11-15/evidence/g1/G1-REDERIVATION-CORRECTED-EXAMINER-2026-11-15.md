# G1 RE-DERIVATION UNDER THE CORRECTED EXAMINER (2026-11-15)

Raised by Claude's Batch 6 inspection, item 2: G1's
original 19/19 battery and 13/13 re-derivation were produced
under the pre-fix examiner (36bf23e1…). Re-run 2026-11-15
with the corrected examiner (564925230a70c56d…) as the
imported module: test_g1.py 13/13 re-derivation checks
pass, unchanged verdicts. The Step 4 fix (operation-
identity refusal pairing) does not alter any G1 result —
G1's record carries genuine INSERT_REFUSED events and they
pair correctly under both pairing rules; the defect bit
only where a refusal's return ordering differed, which
the G4 record was the first to exhibit.
