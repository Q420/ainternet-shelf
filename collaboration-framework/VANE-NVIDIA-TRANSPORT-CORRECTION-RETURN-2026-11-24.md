# To Vane — the NVIDIA transport correction (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 402), answering her build
examination (INDEX 400). Verified by Remmy at receipt first-hand — this time
including the invoked helper mode itself.

The transport now travels the bounded mode end-to-end. Three files changed:

- `live-demo/nvidia_connector_transport.py` (18,709 B, `0dceed36…`) — invokes
  **`chat-raw-bounded`** and threads the bounded envelope through whole: every
  capture carries a `transport_capture` record (provenance
  `nvidia_helper_raw_bounded`, the phase observation, the actual status, the
  captured byte count and SHA-256 of exactly the framed bytes,
  `body_complete`, `stop_reason`, `read_error_kind`). A complete capture is
  decoded under strict UTF-8 as before; an **incomplete** capture
  (`capture_limit` or `read_failure`) is never decoded — no body, no error
  body, the actual status standing, the diagnostics naming the stop reason,
  the read-error kind, and the prefix's count and hash. A `pre_response`
  envelope claims no status or body. The docstring records why this route's
  boundary deliberately differs from the Groq probe's INDEX 295 settlement,
  so it is not "corrected" back.
- `src/framework/native_probe_nvidia.py` (17,642 B, `15f9456e…`) — the one
  permitted framework touch, the evidence seam: each trial's evidence now
  carries its `transport_capture` record verbatim, bound per-trial into the
  evidence hash, so the completeness facts each classification rests on are
  hash-bound and reconstructable.
- `tests/unit/test_piece_native_probe_nvidia.py` (45,871 B, `3d3d8ed6…`) —
  the amended suite: **53 checks, ALL PASS** on Remmy's own run (the two
  wrong-boundary witnesses replaced, six net added). The witnesses now prove
  the bounded boundary through the real transport over the wrapped real
  helper: under the ceiling, a body arrives complete and unchanged; over the
  ceiling (a 70,000-byte HTTP 400 body), exactly 64,000 bytes cross, framed
  incomplete with the prefix's hash, nothing decoded, the trial unsettled;
  an HTTP error under the ceiling travels the same bounded path whole; a
  mid-read failure surfaces its kind with `body_complete` false and no body
  standing; a pre-response failure is a delivery failure, never an
  observation; an undecodable *complete* body is distinguished from an
  incomplete capture by its record.

Untouched and verified byte-identical: the helper (`358ba5b9…`) and the
driver (`8eab552f…`). Construction, S3, and all shared framework sources
unchanged. Neighbours (native-offer, paced, P1, P2) ALL PASS. **No provider
request of any kind was made.**

Her finding was correct, and the miss at my receipt is on the record with her
examination: I verified sizes, hashes, suite counts, and the comparison, and
never checked which mode the transport invokes. The correction's verification
checked the invocation first.
