# PILOT-MANIFEST-01 — RE-FREEZE AMENDMENT (2026-11-13)
## CONTINUATION — BATCH 3 CORRECTION 7 (RECOVERY-ROW ALIGNMENT)

Supersedes the Correction 6 continuation for the DRIVER
only. Everything else stands as pinned there.

- pilot_driver.py — sha256
  f22707732f451a290f9d11dd01b1b733721e77b309de48cf94f36c20b84ad31f
  — one-line alignment under Ben's Correction 7 build go
  (widget-86eae911; go record shelved at 66a386a6) per the
  plan APPROVED by Alex (7764ae67): in
  op_t02_apply_precedence_check, the recovery event's
  adjudication_row is now located by the class-derived
  lookup state["t02_classes"].index("adjudicator"),
  replacing the positional state["t02_rows"][2]. No other
  change; no positional T02 row access remains in the
  driver.

Standing pins, restated: authority e245cabc…; tools
df1045f7…; record ed3f5c85…; suite 0732d07b… (unchanged
from Correction 6).
