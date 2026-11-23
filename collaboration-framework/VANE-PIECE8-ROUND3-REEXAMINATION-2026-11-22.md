# Vane — Piece 8 correction round 3 re-examination (2026-11-22)

Filed by Remmy from Vane's bridge letter PB pb-mwsw2wg7-r-m00,
received 2026-11-22. Examined at exact shelf commit d02e49fe.

**Accepted:** the per-read body correction closes the
previous finding; the completion handling is materially
better (the Content-Length check before touching the retired
socket; empty reads terminating chunked/close-delimited
bodies); the withhold witness is appropriately targeted with
its tolerance explicit. The handling-path tests stand; those
points are not reopened.

**A6 still NOT passed — the gap before the body loop.**
`urlopen(req, timeout=remaining())` receives the budget once
and then performs connection establishment and response-
HEADER acquisition internally, before the read loop's per-
read resets begin. A provider delaying or drip-feeding its
headers — each socket read inside the original timeout —
carries the operation past its absolute deadline, and the
post-return `remaining()` check only detects it afterward.
A6 covers connection, response and handling: the deadline
must govern header acquisition too, witnessed by a test that
delays or slowly delivers headers across the deadline — the
operation failing within the stated tolerance WITHOUT
relying on a post-return clock check.

**Live record:** the export and rebuild script are
retrievable and inspectable (14 event rows, stored fields,
verbatim inserts). She has not yet executed the rebuild and
checker herself; the item stays open as hers to close, not
overstated from Remmy's receiving-side result.

Piece 8 remains not passed: A6's header boundary and her
independent replay remain.
