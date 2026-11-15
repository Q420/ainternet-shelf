# Watchdog Stage 1 Contract — Amendment v1.3 (DRAFT)

**DRAFT — owner confirmation pending. Not frozen, not filed.**
Drafted 2026-11-15 as part of the Stage 3 correction round,
from the Stage 3 review rulings D1, D2 and D5
(CLAUDE-WATCHDOG-STAGE3-REVIEW-2026-11-15). When the owner
confirms this text, it amends the frozen contract v1.1 as
amended by v1.2. Until then, the interim detector behaviour
described in the Stage 3 resubmission note stands in for
items (a) and (b).

## (a) §3 — the job record gains `gate_terms`

§3 is amended to add one field to the job record:

- **`gate_terms`** — a list of strings: the keyword first
  gate's terms for this job. A turn whose content matches no
  term is gated out (never judged; see (b)).

Rules:

- `gate_terms` is set **before activation**, like the rest
  of the record.
- It is **pinned with the record** under §2: it is part of
  the record hash, not a set-once side field.
- It is **immutable while the job is active**. Changing the
  gate is a new job_id, exactly as for any other active
  record change.
- A job whose `gate_terms` is empty (or absent) has no
  gate: every completed seat turn is judged. That state is
  itself part of the pinned record, not a default applied
  at detection time.

This retires the detector-local gate table: once v1.3 is
confirmed, the gate's home is the registry, and the
detector's interim pin (Stage 3 resubmission note, M-S3-2)
is removed in favour of the §2 record pin.

## (b) §6 — streak reset causes

§6 is amended so that a reset of the streak count has
exactly two causes, recorded distinctly in the streak
record (`reset_cause`):

1. **`judged_no`** — a judged turn whose result is NO.
2. **`gate_reset`** — a completed seat turn that the
   keyword gate excluded before judging.

A `gate_reset`:

- requires **no judge call** (§13's "no match → judge
  never called" is unchanged);
- is **never recorded as a judged NO** — not in the streak
  record, not in any packet, not in the ops log;
- advances the streak's last-turn key to the gated turn,
  so the turn is never reprocessed.

Judge errors continue to HOLD the streak (neither count
nor reset), as before. A recorded event continues to
consume the pair (amendment A1), recorded as cause
`event_recorded`.

## (c) §11 — credentials sentence replaced

The §11 sentence about judge credentials is replaced in
full by:

> Credentials for the judge transport are obtained only
> through the connector's secure route (the registered
> credential's surrogate, attached by the connector
> framework). Environment-variable keys are not used.

No other §11 text changes: the judge still runs on the
hosted NVIDIA API per the owner's ruling, and credentials
are still never logged or written into packets, the
registry, the ledger, or logs.

---

*End of draft. Owner confirmation pending on all three
items; on confirmation this becomes the frozen v1.3
amendment and the Stage 3 interim mechanisms are reconciled
to it.*
