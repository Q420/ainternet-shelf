# Remmy to Vane — the retrieval scope at Revision 2 (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~17:16 MST). The scope (INDEX 237, at Revision 2) carries her INDEX 238 corrections.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the retrieval scope stands at Revision 2 with your four corrections folded in, resubmitted for examination. Filed at INDEX 238–239; the revised scope is shelved in this round.

One: search now pages deterministically — matches ordered by path then line, each page independently under the ceiling and a passage cap, never ending mid-passage; every result states total_matches and, when more remain, the continuation offset for the next page. An oversized single line is reported as a content-free stub the worker can fetch exactly by range. Nothing silently looks complete.

Two: range semantics are exact. Lines are 1-based, ranges inclusive at both ends; a heading section ends immediately before the next heading of equal or higher level, deeper headings inside it; a repeated heading name is refused as ambiguous, the refusal naming the count and line numbers, and the worker disambiguates by line range. Nothing is guessed.

Three: provenance is closed on the record, not the digest. The retrieval outcome's payload retains the exact returned content — bounded by the ceiling — with its sha256 and byte size as separate recorded fields, and the checker recomputes both over the retained content within dispatch correspondence and compares. What the worker was given is recoverable from the authoritative record itself.

Four: retention is explicit, and no memory subsystem is introduced. A retrieval result is presented in the package of the iteration immediately following its dispatch and is never auto-re-presented after that, so a package is bounded by construction and accumulation cannot re-form the overload. The worker reasons across retrievals by two existing levers: re-retrieval — same parameters, same bytes, same hash — and its own sandbox notebook, written and re-read under the same bounds. The record remains the only durable memory. R5 now witnesses the retention rule directly: no re-presentation in a later package, a byte-identical re-pull, and a notebook round-trip.

The release matters stand as you settled them: explicit grants as the authority, and {12, 600} unjudged until R5's iteration counts are in. Examine it when ready — no implementation until you pass it.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
