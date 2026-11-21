# Correction Round Step 2 — FR-B Restoration: design and evidence map

Prepared by Remmy, 2026-11-16, under Alex's correction-round
order (ALEX-DUENNA-RESUME-RULING-2026-11-15): pack
reconciliation (accepted), FR-B restoration (this step),
Claude evidence repairs (next). RB-50 Item 4 stands
REJECTED pending this restoration.

## First-hand finding

The scripted entry, key T09/FR-B|T09-STEP-03|1:

- Original G4 stack: {"kind": "malformed",
  "raw_output": "DECISION: CLOSE?? receipt###unparseable"}
- Correction stack: {"kind": "output", raw text identical}

The correction changed one field — the kind — which routed
the malformed statement past the adapter's malformed
classification and into the tree. Alex's acceptance line:
the malformed output must not be transformed into an
ordinary output before reaching the adapter.

## Restoration

A fresh stack copied from the correction stack
(correction/restoration-stack, local working tree). The
single FR-B field is set back to "malformed"; the raw
output is byte-identical; the restored entry equals the
original G4 entry exactly. Diff against the correction
script: that one call, that one field. Restored
stub_script.json sha256
ee94e02d496d1defe7b1a287f1a838221f9fdcf8e352b365a04a2cd6ba37a5a6.
The correction stack is untouched; G4CORR-20261115-001's
13/13 remains the historical record, not a substitute.

Run: g4corr_harness over the full 13-instance battery,
scripted stub subject, scratch room staging as the
correction run was staged. No live model call.

## Evidence map against (a)-(e)

(a) Adapter receives the original malformed output —
    the ADAPTER-CAPTURE-02 record for the FR-B STEP-03
    call, showing the malformed entry as delivered.
(b) Malformed path exercised — the run record's
    ADAPTER_FAILURE on that call.
(c) Specified failure and handling result — the FR-B
    closure and failure record the run produces.
(d) Tree applies decision_stands correctly — OPEN
    QUESTION, below.
(e) Original attempt history preserved — the run's
    captures and event record, with the G4 and correction
    records untouched at their pins.

## The question for Alex

With kind "malformed", the adapter classifies at the
transport boundary (ADAPTER_FAILURE, tree
INVALIDATED-INFRASTRUCTURE) and decision_stands never
engages inside the FR-B instance. Two readings:

R1: (d) is satisfied at the T09 family level in the same
run — base T09's STEP-03 applies the tree's completion
rule and FR-B's rejection stands on the worksheet —
while (a)-(c) are satisfied inside FR-B itself.

R2: (d) requires decision_stands inside the FR-B
instance, which the restored kind makes structurally
impossible — in which case the specified handling result
at (c) needs restating before the run.

Remmy's ask: rule which reading inspects as correct, or
state the correct one. On the ruling, the run proceeds.
