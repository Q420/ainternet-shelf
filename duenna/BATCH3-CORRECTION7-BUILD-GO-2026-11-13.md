# CORRECTION 7 — BEN'S BUILD GO (2026-11-13)

Ben's tap on the scope card (widget-86eae911, 2026-11-13
22:05 MST), in his words: "Build go: one-line alignment in
the pilot driver — the recovery-event copy of the T02
adjudication row uses the same class-derived lookup as the
main site (plan approved by Alex at 7764ae67); fresh runs
+ Correction 7 bundle for his inspection."

Plan of record: duenna/BATCH3-T02-RECOVERY-ROW-PLAN-
2026-11-13.md, TECHNICALLY APPROVED by Alex
(pb-mwg00qk0), who ruled the Correction 6 build-go did
not cover this additional code site and required this
fresh explicit go. Scope: op_t02_apply_precedence_check
only — state["t02_rows"][2] →
state["t02_rows"][state["t02_classes"].index(
"adjudicator")]. Everything else unchanged.
