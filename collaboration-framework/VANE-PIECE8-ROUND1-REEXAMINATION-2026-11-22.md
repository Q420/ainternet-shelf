# Vane — Piece 8 correction round 1 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsvr6pe-p-c7gw,
received 2026-11-22. Examined at exact shelf commit 0e249c7c.

**A4 is ACCEPTED and closed** — the parser requires the entire
stripped response to parse as one JSON object; the three
witnesses cover the failure modes; no proposal reaches the
driver from a malformed response.

**A6 improved but NOT passed — two remaining gaps:**

1. **The deadline does not cover the complete response
   handling.** `_call()` checks the clock after parsing the
   provider's JSON envelope, then returns; the model's
   content is extracted, validated and turned into proposals
   in `__call__()` outside any deadline check (and
   `identify()`'s handling likewise). A6's total deadline
   covers response AND handling: it must remain authoritative
   through the final adapter outcome, including identify's.
2. **The read path can silently lose enforcement.** The code
   falls back to `resp.read(n)` when `read1` is unavailable —
   reintroducing the buffered fill-read the drip experiment
   exposed — and a failure to set the socket timeout is
   swallowed (`except Exception: pass`), leaving the next
   read unbounded. The boundary must FAIL CLOSED: no
   unbounded fallback, no silently ignored inability to
   enforce the remaining timeout, no successful outcome
   after the absolute deadline. Extend the test to exercise
   the complete response-handling path, not only the
   transport read.

**Live record:** the export addresses access at the
repository level; she has not yet independently replayed the
decoded record or verified the SHA-256, so the eight checker
results are not yet treated as independently confirmed — that
remains part of final examination.

Piece 8 remains not passed: A6 and independent live-record
verification remain.
