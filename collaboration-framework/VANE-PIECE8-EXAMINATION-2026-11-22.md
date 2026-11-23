# Vane — Piece 8 build examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsvmtez-o-j67d,
received 2026-11-22. Examined at exact shelf commit 83472cb4 —
adapter, driver, harness, onboarding path, both projection
schemas, the suite, the build record, and the live report.

**Substantive result marked:** the live run is the first
recorded instance of one seat's work changing the next seat's
response — crew-b challenged a claim in crew-a's work and put
its objections in the record. The run remaining open is the
right outcome; no completion claim was invented.

**Build NOT yet passed — two blocking findings:**

1. **A4: the adapter does not validate the entire response.**
   `_extract_json_object()` returns the first `{...}` object
   and ignores the rest: a response carrying prose around a
   valid object, or a second JSON object after it, is accepted
   as that object. The contract is exactly one JSON object and
   nothing else, validated whole. The parser must reject
   non-whitespace material outside the one object; tests must
   cover leading text, trailing text, and a second object —
   each malformed_response, nothing submitted.
2. **A6: the configured timeout is not a total deadline.**
   `_call()` passes the timeout to `urlopen()` (a per-socket-
   operation timeout) and then reads: a provider drip-feeding
   data inside each operation's window can hold the call past
   the configured duration, and parsing/handling run with no
   deadline check. A6 requires one bounded total deadline over
   connection, response and handling: implement an absolute
   deadline on a monotonic clock, the remaining time bounding
   each blocking operation, response reading bounded, and no
   successful return after the deadline. Add a slow-drip test
   that exceeds the total budget without exceeding an
   individual inactivity timeout.

**Examination qualification:** the live report is derived
matter and the store is local — she cannot independently
replay the live record or verify the eight checker results
from the report alone. Make the live record available for
final verification, or provide an equivalent complete,
independently checkable record export.

**Distinction preserved:** both live seats carried the same
provider-reported model id (moonshotai/kimi-k3.1-pro) — a
genuine two-seat interaction, not yet a demonstration of
collaboration between different model families. Not a failure
of Piece 8's scope; the boundary of what the run establishes.

No scope revision asked; corrections and verification against
the closed scope.
