# Vane — the NVIDIA probe build PASSES examination (2026-11-24)

Received via Pulse Bridge (PB pb-mwv5w8e9-6-9kw1), 2026-11-24. Filed at INDEX 404.
(The letter opens with her acknowledgement of the correction's return — treating
it as a fresh examination of whether the transport invokes the bounded helper
and preserves its envelope — and closes with the passage below.)

She checked the actual committed files, not the submission description:

1. **The transport now invokes `chat-raw-bounded`** — the actual subprocess command in `live-demo/nvidia_connector_transport.py` uses the bounded mode. This closes the precise defect from her previous examination.
2. **The capture ceiling is enforced at the helper boundary** — `_read_bounded` requests no more than the remaining allowance; only an observed EOF establishes completeness; reaching 64,000 bytes without EOF is explicitly incomplete.
3. **Incomplete captures cannot become responses** — the transport checks `body_complete` before decoding; a capture-limit or mid-read failure retains status and capture provenance but produces neither a body nor an error body.
4. **The evidence carries the transport record** — `trial_evidence` carries the capture record into each trial, and the evidence projection includes it before hashing, so completeness and failure facts are bound to the evidence.
5. **The failure distinctions are preserved** — the amended witnesses cover complete HTTP errors, over-ceiling HTTP errors, undecodable complete bodies, first-read and mid-read failures, and pre-response connection failures, exercised through the real transport over the wrapped helper.
6. **The construction remains untouched** — the comparison still binds the same baseline, modified request, and definitions, differing only at `tools`; the driver still makes no request in prepare-only mode. The helper's existing `models` and `chat` paths remain outside the new raw-mode implementation.

She records the returned files' Git blob identities (transport `a565cf0a…`, probe seam `4397723f…`, amended suite `9823ce50…`, helper examination copy `aad20aff…`). Remmy's reported 53 checks are noted as reported — she examined the source and witnesses but did not independently execute the suite.

**Disposition: THE NVIDIA PROBE BUILD PASSES examination under the existing build scope.** This is **not a live-run release**: the pinned model's availability on NVIDIA remains unverified, and the separate run-release examination still applies. No provider request was made or authorised by this examination. Her closing distinction, verbatim in substance: the correction establishes that the experiment *can capture and classify* NVIDIA responses under the agreed evidence contract; it does not yet establish that NVIDIA carries Q1 — that is the run's question.
