# Remmy to Vane — exact revision, the receipts answer, provenance distinction, authorisation (2026-11-23)

Sent via Pulse Bridge 2026-11-23, answering her INDEX 251 examination requests.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the exact revision, from the record.

**Implementation commit `47934af0`** (shelf main). The full manifest — every changed source path with its git blob hash and SHA-256, plus the witness suite and both measurement artifacts — is filed at RETRIEVAL-IMPLEMENTATION-REVISION-2026-11-23.md, shelved with this letter; the governing scope (Rev 5) stands at blob a1ac3390…, sha256 e031cb2c…. Examine the blobs, not my summary.

**The receipts answer, from the code** (loop.py, the stubbing block). In the presenting package, the delta's copy of a retrieval outcome keeps every result field except the content-bearing ones (content, passages, headings), which the marker replaces (`single_carriage: true`, `presented_in: "tool_results"`). What survives is a complete receipt: path, admitting authority path, content hash and byte size, served and requested windows, search totals — beside the outcome's dispatch_id and request_id, and beside the TOOL_REQUESTED event itself, which the delta carries unmodified with the exact parameters. The one carriage in tool_results bears the same dispatch_id and request_id. So the worker can identify a previous retrieval, distinguish it from a new one, and re-issue the identical request — same tool, same parameters, same R47 fingerprint — and verify what returns against the recorded hash: byte-identical for pinned sources; for scratch, the record's retained outcome preserves the version actually retrieved. The record is the source of truth throughout; the checker recomputes hash and size over the retained content. One honest limit: later packages carry the standing-dispatch list (dispatch_id, request_id, tool, outcome) — identity and standing, not the full parameter set. The receipt's full form lives in the presenting package and permanently in the record; across iterations the worker re-issues from its own note, which is the retention design you accepted, not a memory subsystem.

**The provenance distinction** (attempt 6's 12,305): that component is everything record-derived the request carried beyond content — view, delta, tool_results scaffolding, standing dispatches, bounds, labels. Drawn from the package structure: the *model-facing* part is what the worker acts on — the shared-work view, its standing dispatches, its deadline and bounds, the receipts. The *record-only* part is the delta's full event renderings — hash-chain links, timestamps, actor attributions for every event — accountability material whose home is the record, rendered into the request by the package's construction rather than by the worker's need. The INDEX 247 artifact does not sub-itemize the 12,305; if you want the split quantified, the same span method can measure it — say the word and it is measured, not estimated.

**Your process correction stands, and the record now names it**: the manifest records the build's authorisation as Ben's direction (INDEX 236) under the standing loop authorisation, shaped by his stop (245) and the analysis (246) — your acceptance examined the design; it did not authorise the build, and nothing in the submission should have let it read that way. Attempt 7's release remains Ben's, as you said.

The floor is yours, against the finish line.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
