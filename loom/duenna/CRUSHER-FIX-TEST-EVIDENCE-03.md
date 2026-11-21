# CRUSHER HARNESS v2.2 — CORRECTION EVIDENCE 03 (2026-11-11)

**Scope:** Alex's correction on v2.1 (pb-mwc54dx4-b-8402): the
retry boundary allowed THREE submissions; the established
policy is a maximum of TWO (initial + one retry). Within the
existing clearance; no policy redesign. **No live Groq calls.**

- `crusher.py` v2.2 sha256 3ba3dd3cf3208b5eb8cfc19c5fae731ac3a319e72db96e5098469bc5221bd566. Both boundaries changed:
  transport `attempts < 3` → `< 2`; HTTP 5xx `attempts >= 3`
  → `>= 2`. 429/4xx single-attempt rule untouched.
- FENCE byte-identical to v1 (re-verified).
- New tests T7 (two consecutive 5xx) and T8 (two consecutive
  transport failures): exactly two submissions; two
  attempt-failed records + one closing failed record, one
  call_id; unknown usage = 2, closing record not recounted.
  T5/T6 (retry-then-success) retained and passing.

## Acceptance run (verbatim tail, 2026-11-11)

```
PASS  T5a 5xx retried once then answered (attempts=2)
PASS  T5b intermediate failure has its own durable record
PASS  T5c attempt + success linked by a stable call_id
PASS  T5d failed attempt counted in unknown usage — unknown=1 known_tokens=12
PASS  T6 transport failure recorded, linked, then answered
PASS  T7a two 5xx submissions maximum — submissions=2
PASS  T7b both attempts + closing logged, one call_id
PASS  T7c unknown usage counts both attempts, closing not recounted — unknown=2
PASS  T8a two transport submissions maximum
PASS  T8b both attempts + closing logged, one call_id
PASS  T8c unknown usage counts both transport attempts — unknown=2

24 passed, 0 failed
```
