# BATCH 3 CORRECTION — ROUND 5 PLAN: divergence-evidence traceability (2026-11-13)

**Scope.** One item only, per Alex's report review
(pb-mwfw6p8k): the machine-readable divergence evidence
(divergence-t02.json) gains source identity. The divergence
report, the round-4 bundle (ce0052d1) and all pins are
preserved unchanged. No driver, authority, tools or record
change. No implementation until this plan is inspected.

## The correction

Each divergence entry gains four fields, captured at the
point the divergence is detected, from the record under
recomputation — never reconstructed afterwards:
- **run_id** — the record's own run identifier (its
  RUN_STARTED run id; the same id embedded in its event
  ids).
- **record_path** — the record's identity within the
  evidence set: its run-directory name and file
  (e.g. runs/001-run-record.jsonl in the bundle).
- **event_id** and **seq** — of the STEP_TRIGGERED event
  whose T02-STEP-03 invocation produced the divergent
  artefact (the event the recomputation was processing).

**capture_id:** the pilot records carry no capture_id field
(verified: RUN_STARTED payload keys are budgets,
configuration_hashes, pins, scratch, snapshot,
subject_configuration; event ids are
`<run_id>:<seq>`). There is nothing to include; the plan
states this rather than inventing a field — run_id + seq +
event_id already identify the event uniquely, since
event_id is derived from exactly those.

## Corresponding assertions (each its own transcript line)

- Every divergence entry's (event_id, seq) resolves in its
  own record to the STEP_TRIGGERED event for T02-STEP-03
  with the entry's attempt number.
- The seven entries' identities are pairwise distinct.
- The (p-T02) failing lines are unchanged — seven, by
  design; everything else stays green.

## One reconciliation note for Alex

His crosswalk gives the MAIN triggers at seq 23 and 30; on
the round-4 bundle's records the same (run, attempt)
triggers sit at seq 22 and 29 (event ids
`B3CORR2-20261114-001:22` / `:29`) — his (run, attempt)
mapping agrees with the bundle's exactly; the seq figures
differ by one, presumably his copies' numbering. The
revised evidence carries the bundle records' own seq and
event_id values, so his verification can settle which
numbering his copies carry. Flagged here, not smoothed.

## Mechanics

Suite only (the divergence-capture site and the dump);
CONTINUATION-BATCH3-CORRECTION-5; fresh runs; new bundle
duenna/batch3-correction5-2026-11-13/ carrying the revised
divergence-t02.json (the round-4 JSON remains in its own
bundle as history). Expected suite shape: 107 + the new
identity lines PASS, the same seven (p-T02) lines FAIL,
exit 1. Build authority: the same-checkpoint reporting
authority Alex has applied to rounds 3–4, unless he directs
otherwise.
