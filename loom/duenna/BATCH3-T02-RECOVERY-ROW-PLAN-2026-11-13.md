# T02 RECOVERY-ROW ALIGNMENT — NARROW CORRECTION PLAN (2026-11-13)

## The clarification Alex asked for

The remaining `state["t02_rows"][2]` (pilot_driver.py,
op_t02_apply_precedence_check, the recovery event's
recovery_inputs) is NOT intentionally covered by the
fixed-order invariant as a design choice. It is a second
site producing the same adjudication_row value that the
Correction 6 plan inventory missed: Revision 2 §B named
"the recovery adjudication_row" as one concept, and two
functions produce it — op_t02_apply_precedence_inputs
(the step's declared inputs on attempt > 1, corrected)
and op_t02_apply_precedence_check (the recovery event's
recovery_inputs, not corrected). The observed records are
correct only because the worksheet operation asserts the
class order before either site runs. The plan's rule —
the row is located by its position in the asserted class
sequence — should govern both sites. The miss is Remmy's
inventory gap, recorded as such.

## The correction (one line)

In op_t02_apply_precedence_check, replace
`state["t02_rows"][2]` with the same class-derived lookup
used in op_t02_apply_precedence_inputs:
`state["t02_rows"][state["t02_classes"].index("adjudicator")]`.
No other driver change. Suite unchanged (its derivations
already locate the adjudicator row by class). New driver
pin via CONTINUATION-BATCH3-CORRECTION-7; fresh runs; new
bundle duenna/batch3-correction7-2026-11-13/; expected
result 109/109 PASS exit 0 with byte-different records
only in run identity fields — the recovery payloads'
content is unchanged because the value selected is the
same row.

## Authority

Alex's review authorised no change; this plan is for his
approval. A driver change then needs Ben's fresh explicit
build-go, per the sequence Alex ruled at pb-mwfwm0jz —
unless Alex rules this alignment inside Ben's Correction
6 go, which named the plan rather than this site. Remmy's
recommendation: treat it as a fresh narrow go; it costs
Ben one tap and keeps the record clean.
