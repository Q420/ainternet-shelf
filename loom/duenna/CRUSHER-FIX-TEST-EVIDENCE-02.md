# CRUSHER HARNESS v2.1 — CORRECTION EVIDENCE 02 (2026-11-11)

**Scope:** Alex's bounded correction on v2 (pb-mwc50i21-a-11q2):
intermediate failures disappeared on the retry path. Within the
existing clearance; retry policy unchanged (one bounded 5xx retry
path; 429/4xx single attempt). **No live Groq calls.**

## The correction

- `crusher.py` v2.1 sha256 27e7190724f28b10feee56c51c27fa61830fa746b717a6a7b17526762b7e7c03; `test_crusher.py` sha256 ca80b07819939a619c399ef96974eb51590170878c5fd4d5db0547da0dcfba16.
- Every failed attempt now writes its own durable record the
  moment it happens: outcome "attempt-failed", attempt number,
  timestamp, http_status (or transport error_kind), the full
  provider error body / transport error text, retry-after.
- A stable `call_id` (per ask() invocation) links attempt
  records to the closing record (answered / failed / not-sent).
- Daily accounting counts each attempt-failed record as one
  unknown-usage call; closing summaries carrying a call_id are
  not double-counted; legacy records without call_id keep the
  v2 counting (one unknown per record).
- FENCE byte-identical to v1 (re-verified after the patch).

## Acceptance run (verbatim, 2026-11-11)

```
PASS  T1a 429 body preserved verbatim in the raised error
PASS  T1b 429 not retried (exactly one submission) — submissions=1
PASS  T1c failed call leaves durable records (attempt + closing)
PASS  T1d records carry attempts + status + body + retry-after + call_id
PASS  T2a success records the full usage block
PASS  T2b retrieval scores survive into the record
PASS  T2c package size recorded and within the cap — package_chars=11471
PASS  T3a daily total reconciles with usage records
PASS  T3b unknown usage counted separately — unknown=1
PASS  T3c accounting date + ceiling identified
PASS  T4a oversize package trimmed to the cap before submission — submitted=10473 cap=14000
PASS  T4b all section identities preserved under trimming
PASS  T4c resulting package size recorded
PASS  T5a 5xx retried once then answered (attempts=2)
PASS  T5b intermediate failure has its own durable record
PASS  T5c attempt + success linked by a stable call_id
PASS  T5d failed attempt counted in unknown usage — unknown=1 known_tokens=12
PASS  T6 transport failure recorded, linked, then answered

18 passed, 0 failed
```

T5/T6 are the new proofs the correction required: a 503-then-
success and a transport-failure-then-success each produce BOTH
the per-attempt failure record and the success record, linked,
with the failed attempt visible in unknown usage.
