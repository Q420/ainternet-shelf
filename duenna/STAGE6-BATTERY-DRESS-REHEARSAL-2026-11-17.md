# STAGE 6 BATTERY — DRESS REHEARSAL EVIDENCE (2026-11-17)

Preparation correction 4 (Alex inspection ruling, 2026-11-17):
the full battery assembly run against the transport double
(stub subject) in the laptop room under the supervisor.
NO live model call was made; no network was touched.

## Staging

- The battery stack was reinstalled fresh into the laptop
  room from the run-of-record stack archive
  (`g4rest-stage.tar`), so the launcher binary and the
  supervisor identity records were regenerated for this
  staging (script: `g4batt_stage.sh`, mirroring the accepted
  Step 2 restoration staging).
- Installed stack: 22 files, hashes recorded in
  `g4batt-room-stack.sha256` (stage dir) — byte-identical to
  the stack of the accepted run of record
  G4CORR-20261116-003.
- Custody: production launcher + supervisor commitments,
  laptop room (joint-6 venue).

## The rehearsal run of record: G4CORR-20261117-001

- Terminal commitment: RUN_CLOSED, **483 events** — the same
  event count as the accepted run of record.
- All 13 instances reached TREE_CLOSED (T01–T09, T09/FR-A,
  T09/FR-B, T09/FR-C, T09/FR-VALID).
- 13 adapter captures (the 12 unconditional model calls; T03
  contributes two steps) + driver captures including T02's
  second tree attempt (a2).
- Per-step request hashes are **identical** to the run of
  record's captures — the rehearsal exercised the same pinned
  requests the input measurement (correction 2) was taken
  from.
- Ledger: 14 rows, same shape and count as the run of
  record's ledger.
- Examiner re-derivation (independent, this office): the
  run record's hash chain re-derives **482 of 483** events
  under pilot_jcs canonicalisation; the single exception is
  seq 1 (RUN_STARTED), which does not re-derive under plain
  canonicalisation. The accepted run of record shows the
  **identical profile** (482/483, same event), so the
  rehearsal's record is exactly as well-formed as the
  accepted record's. The terminal commitment's final-event
  hash matches the chain head.

## Attempt history (complete, nothing withheld)

Three supervisor firings preceded/accompanied the rehearsal;
the custody chain's behaviour in each is part of the
evidence:

1. **BATTREH-20261117-001 — REFUSED pre-run.** The harness
   derives its run ID (G4CORR-<date>-<seq>); the foreign
   prefix failed the harness's ID assertion before any
   instance ran. No commitments were issued. The refusal is
   the ID-binding working as designed.
2. **G4CORR-20261117-001 — the rehearsal (above).** Complete.
   Its stdio log ends with one harness AssertionError in a
   post-close artefact step (the run-summary write follows
   the ID assertion in the harness's main; the derived ID at
   that point is the next sequence number). The run record
   was already RUN_CLOSED and committed when it fired; the
   run-summary artefact is therefore absent from this run —
   its content (per-tree outcomes) is fully present in the
   run record and is summarised in this package instead.
3. **G4CORR-20261117-002 — a second complete run** (483
   events, RUN_CLOSED, 13 captures), fired by the operator
   under a preliminary misreading of firing 2's log before
   firing 2's completeness was established from its fetched
   record. It is retained as a duplicate rehearsal, not
   suppressed; the run of record for this correction is
   firing 2.

## What this closes and what remains

- Correction 4's rehearsal requirement is satisfied by the
  run of record above: the complete battery machinery and
  the custody path are demonstrated without a live call.
- Still outstanding before the final preparation inspection
  (§6(e)): the relay's operational test evidence (§6(b)/(c))
  — the relay is not yet built; its construction checks run
  when it is. The rehearsal neither needs nor exercises the
  relay (it runs against the in-room transport double).
