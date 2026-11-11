# V2 BATTERY — VOIDED (Ben's ruling, 2026-11-10)

The first V2 battery attempt is NULL. Sequence: the battery
stopped itself at T01 Arm C on a technical failure
(tools23.locate built search records without the embed_text
field bm25_search requires). The implementer patched the
locate step at driver level (run_c.py), preserved the failure
under incidents, and relaunched with skip-saved resume —
carrying on instead of stopping for adjudication. Claude's
review (branch review/arm-c-process-trees, e9c5adf) named the
open question: whether a driver fix counts as a criteria
change is the adjudicator's decision. Ben ruled: the test is
null.

Preserved here as a record, not results: the full run file
(29 of 36 runs + 1 incident) and both battery logs. The
clean rerun requires: the locate defect fixed inside a new
tools revision, reviewed before the run; the full execution
stack (tools, driver, runner, trees) frozen and hashed
before the first run; a from-zero battery with no mid-run
changes of any kind.
