# BATCH 2 CHECKPOINT REPORT — PILOT-TOOLS-01 and the registry

**Build:** Stage 5, Spec Rev 22 at pin afae29fb, §4 Batch 2 —
under Ben's build go of 2026-11-13 16:40 MST (shelved at
a07d9ccd). **Built by Remmy in the room** (Ben's laptop, WSL2
Ubuntu 26.04.1, /srv/nemotron-pilot/batch2/work/), run in the
watch window; transcript /home/ben/batch2.log in-room.
**Verdict: CHECKPOINT PASSED — 35/35, exit 0.** Alex's
between-batch review follows; Batch 3 does not open before it.

## What was built

**PILOT-TOOLS-01** (`pilot_tools.py`, sha256
e12ccf6b314e609c4f7ff17618a687f668be64a869a2d39845c490133157dec5):
the five tools as a new versioned artefact on the Batch 1
interfaces (CorpusSource + rules_engine semantics; no trial
runner, no live shelf) — `shelf_lookup`, `source_extract`,
`reference_insert`, `verify_field`, `receipt_worksheet` — plus
the issuance registry (§3.3, five properties) and the logging
contract in scratch-record form (Batch 3 builds the full
hash-chained writer on this event stream).

`reference_insert` implements the provenance rule whole:
EXTRACTED-only acceptance; registry presence, unconsumed,
same tree/step context; **recomputation at insert time**
(section re-fetched, sha256(text) checked against the
snapshot's recorded hash — the convention verified against a
production section before building — the rule re-applied,
value byte-equal, evidence line verbatim); exactly-once
consumption; refusals return no value and emit INSERT_REFUSED
with full claimed-vs-recomputed detail. A caller-built dict
presented as an operation_id is refused
(MALFORMED_PRESENTATION) — no caller-supplied provenance is
representable (SE-2).

## Checkpoint (§4 Batch 2) — evidence

- Four-outcome semantics at the tools layer on production
  sections and synthetics: EXTRACTED (×3 production fields,
  values equal to EXPECTED-01 ground truth), NOT FOUND
  (unknown section; undeclared field by declared design),
  AMBIGUOUS (synthetic two-match, both candidates recorded,
  no value), TYPE FAILURE (synthetic type-defeating, no
  value).
- Refusal mechanics at unit level: forged ids (the guessable
  next sequence number op-7, and op-9999) → NO_ISSUANCE;
  genuine NOT FOUND → NOT_EXTRACTED; second consumption →
  ALREADY_CONSUMED; wrong-step presentation →
  CONTEXT_MISMATCH.
- Logging contract: every invocation in the scratch records
  with its TOOL_INVOKED/TOOL_RETURNED pair (20 + 5
  invocations); exactly 1 LEDGER_ENTRY (the one genuine
  insert); every refusal carrying its INSERT_REFUSED
  governance event (6 + 2).
- Registry property 5: registry state reconstructed from the
  event records alone, matching the live registries, both
  records.
- verify_field against EXPECTED-01 and against the ledgered
  extraction; wrong value does not verify.
  receipt_worksheet reproduces the T09 decisions from the
  data alone: FR-A/FR-B/FR-C REJECT, FR-VALID CLOSE.

Scratch records: scratch-record.jsonl sha256
f3146e4315bdf20008572f39d7caf641061eecd4482da913b454f6352a51c4be;
scratch-record-2.jsonl sha256
66fe3dcb541324bb4b403d292d1e5cde502457b1791c8f4aeb9399c96e80568a.

## Gate G1 sabotage battery (§5) — run on the completed tools

S1 PASS (both forged forms refused from absence of an entry).
S2 PASS (genuine non-EXTRACTED refused). S3 PASS (first insert
succeeds; second refused; a tool that refused everything
would have failed here). S4 PASS (perturbed scratch snapshot →
SNAPSHOT_MISMATCH refusal). S5 PASS (AMBIGUOUS recorded with
all candidates, no value; its insert refused). No insertion
succeeded in S1/S2/S4/S5; no refusal returned a value or
emitted a ledger entry. The battery's record is preserved
(this run) per §4 — G1's zero-egress evidence item belongs to
the gate run on the assembled package (Batch 6) and is not
claimed here.

## Pinning

PILOT-TOOLS-01 is pinned by the dated continuation of the
re-freeze amendment (Batch 2 continuation, 2026-11-13),
placed in the room's freeze tree and shelved with this
report, before any later batch depends on it.
