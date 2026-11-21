# CRUSHER HARNESS v2 — FIX TEST EVIDENCE 01 (2026-11-11)

**Scope:** Alex's clearance pb-mwc4i085-9-bsdn, implementing
CRUSHER-INFORMATION-AUDIT-01's findings. **No live Groq calls
were made as acceptance tests** — all tests inject fake
transports, per the clearance.

## The change

- `crusher.py` v1 sha256 8a0bebbc63c844f6660cbd740363862e288961b9299b1d4e0835e9f29c11727e
  → v2 sha256 10b7664f7864432ffe91571fc0ed91e8eb683055edafac5463f236269fee5657 (v1 preserved at crusher_v1_archived.py).
- `test_crusher.py` sha256 291e3300f1f83525a065efd8d05d45fa1b20d8536bd7be02b799d8748dcb585f (14 checks).
- The FENCE text is **byte-identical** to v1 (verified
  programmatically). `interim_ask.py` and `groq_batched.py`
  still import cleanly against v2.
- Transport is now called directly by the harness (same
  registered custom.groq connection + credential surrogate +
  client-signature header as the connector helper), because
  the helper's subprocess route structurally cannot return
  the HTTP error body. The connector helper itself is
  untouched.

## What v2 does (mapped to the clearance)

1. HTTP error body read in full and preserved — printed in
   the raised error and stored in the failure record.
2. Full returned usage block logged on every success.
3. Package ceiling 14,000 chars enforced before submission
   by deterministic per-section budget trimming (2800 →
   ×0.7 steps → 400 floor); section identity never removed;
   truncation labelled "shown X of Y chars".
4. Failed calls write durable records: outcome, attempts,
   http_status, retry-after, error_body.
5. BM25 scores recorded beside the section ids.
6. Daily token total: `crusher.py --usage [date]` — provider
   accounting day (UTC; Groq resets 00:00 UTC), known usage
   summed from provider usage blocks, unknown usage counted
   separately (pre-fix history, failures, not-sent).
7. HTTP 429 (and other 4xx): single attempt, record, stop.
   Bounded retry retained only for 5xx / transport errors.

## Acceptance test results (verbatim run, 2026-11-11)

```
PASS  T1a 429 body preserved verbatim in the raised error
PASS  T1b 429 not retried (exactly one submission) — submissions=1
PASS  T1c failed call leaves a durable record
PASS  T1d failure record carries attempts + status + body + retry-after
PASS  T2a success records the full usage block
PASS  T2b retrieval scores survive into the record
PASS  T2c package size recorded and within the cap — package_chars=11471
PASS  T3a daily total reconciles with usage records
PASS  T3b unknown usage counted separately — unknown=1
PASS  T3c accounting date + ceiling identified
PASS  T4a oversize package trimmed to the cap before submission — submitted=10473 cap=14000
PASS  T4b all section identities preserved under trimming
PASS  T4c resulting package size recorded
PASS  T5 5xx retried once then answered (attempts=2)

14 passed, 0 failed
```

## Real-data check (offline read of the production log)

```
Crusher usage — provider accounting day 2026-11-11 (UTC, resets 00:00 UTC)
  known:   0 tokens across 0 answered calls
  unknown: 58 calls without provider usage (pre-fix history, failures, not-sent)
  ceiling: 200000 tokens/day (published free plan)
```

Today's 0-known figure is correct, not a defect: every Qwen
call made under v1 discarded its usage, and today's failures
and interim-carried answers carry none — the accounting
honestly labels all of it unknown rather than reconstructing
numbers that were never recorded.
