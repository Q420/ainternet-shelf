# RETRIEVAL SCOPE — structured, agent-directed retrieval (first implementation) (2026-11-23)

**Revision 2 (2026-11-23):** Vane's four corrections from her INDEX 238 examination folded in — search paging with deterministic continuation (§3); exact range semantics (§2); provenance closed by retaining the exact returned content in the authoritative record, checker-verified (§5); and the cross-iteration context-retention rule made explicit (§4). Resubmitted for her examination.

Scope for Vane's examination, under her INDEX 235 settlement and Ben's direction (INDEX 236: pull structured access forward). A first implementation of the retrieval direction — **not** the A4 build. Authorises nothing until she passes it.

## The defect this repairs

The worker chooses which files to read but not how much it retrieves: `sandbox.read` returns a whole document, the result enters the next package in full, and the package re-carries it thereafter. Attempt 6's composition request (134,844 bytes) was refused by the provider (HTTP 413) — the pattern now has a hard external limit behind it, not only a design objection.

## The new tool contract (registry v3; v1/v2 frozen for history, both copies amended together)

Three retrieval tools, added to a new `tool-registry-v3` in the framework registry and the checker's independent copy, rendered in the worker's catalogue under the A3-CAT contract (assemblies declare the new catalogue contract; historical assemblies keep their exemption):

1. **`sandbox.list`** — discovery without contents. For a permitted path: the file's name, size, and **structure map** (for markdown/text: its headings with line numbers; for other text: line count). Returns no body text.
2. **`sandbox.read_range`** — a bounded slice: a permitted path plus a line range (or a heading's section, by heading text). The executor enforces a **hard result ceiling** (proposed: 12,000 bytes per result); a range whose content exceeds the ceiling is **refused with a recorded reason naming the bound**, and the worker narrows — a refusal is information, never a silent truncation. **Exact semantics (§2 of the corrections):** lines are numbered from 1; a line is the bytes up to and including its newline (the final line may lack one); a line range [start, end] is **inclusive at both ends**. A heading section begins at its heading line and ends immediately before the next heading of the same or higher level (equal or fewer `#`), or at end of file; deeper nested headings lie inside the section. A heading request must match **exactly one** heading: if the text matches several, the request is **refused as ambiguous**, the refusal naming the match count and their line numbers (metadata inside the boundary), and the worker disambiguates by line range. No request is ever resolved by guesswork.
3. **`sandbox.search`** — search within permitted material: a query string plus an optional path; returns matching passages (the matching line ± up to 2 context lines, each passage labelled with its file and line numbers). **Completeness and overflow (§1 of the corrections):** matches are ordered deterministically — by path, then by line number — and returned in **pages**: each page independently respects the ceiling and a passage cap (proposed ≤ 40 lines per page). A page never ends mid-passage; if the next passage would breach the ceiling, the page ends before it. Every search result states `total_matches`, how many this page returns, and — when more remain — a **continuation**: the worker repeats the query with the returned page offset to receive the next deterministic page. A result never silently looks complete. A single match whose minimal form (its matching line alone) exceeds the ceiling is reported as a **stub** — path, line number, line byte size, no content — which the worker can then fetch exactly in slices via `sandbox.read_range`.

**`sandbox.read` is unchanged for files within the ceiling**; a read whose content exceeds the ceiling is refused on the same terms as an oversized range, naming the bound — whole-document injection of large material becomes impossible through any door, not just discouraged.

## Boundary enforcement (the manifest is the wall, for every operation)

Every retrieval operation — list, range, search, read — resolves its path against the sealed assembly's grants and the case's evidence boundary exactly as dispatch does today (the run's grants narrow reads to `sources/` and the manifest's three files). Search results and metadata obey the same boundary: a listing shows only permitted material; a search over a non-permitted path is refused; no sizes, headings or existence signals leak from outside the boundary. A request outside the boundary is a doorway refusal, recorded as today.

## How results enter the package

A retrieval result enters the next package as exactly what was returned — the bounded piece, with its provenance label (file, range/section, query). Nothing is auto-injected: the package carries the assignment, the catalogue, and the results the worker actually pulled, in the order it pulled them. Successive requests are the worker's: what it retrieves next is decided from what it has already seen, inside the existing loop and its step ceiling.

## Context retention across iterations (§4 of the corrections — stated explicitly)

The loop builds each iteration's package from the record delta since its previous cursor. The rule for retrieval, made explicit: **a retrieval result is presented in the package of the iteration immediately following its dispatch, and is not automatically re-presented in later packages.** A package's size is therefore bounded by construction — the case view plus one iteration's results (each ≤ the ceiling) — and context overload cannot re-form by accumulation. The worker reasons across successive retrievals through two levers, both existing mechanisms — **no new memory subsystem is introduced**:

- **Re-retrieval.** Any earlier result can be pulled again by repeating the operation: same parameters return the same bytes under the same recorded hash. Deterministic, recorded, and cheap on a fast route; the step cost is real and is counted (it feeds the step-ceiling evidence).
- **The worker's own notebook.** The worker may write notes into its sandbox with the already-granted `sandbox.write` and read them back in bounded ranges like any other material. What it chooses to write down is its own retention decision; the notebook is a file it controls, under the same bounds.

The durable memory of the work remains the record alone; the sandbox is the worker's scratch. What the worker retains is its choice, exercised through pulls and notes — never an accumulation the framework imposes.

## Provenance and record evidence

Retrievals are tool acts under the existing A2 machinery — request (with its parameters), dispatch intent, start, outcome — so the record already carries them. **Provenance, closed (§3 of the corrections): the exact returned content is retained in the authoritative record.** The retrieval outcome's payload carries the operation, its parameters, the path, the returned content itself (bounded by the ceiling, so at most 12,000 bytes per result), and the content's **sha256 and byte size** as separate recorded fields. Reconstructibility therefore rests on the record, never on the digest alone: an examiner reads the exact bytes the worker was given from the outcome itself. **The checker verifies it**: within dispatch correspondence for v3 retrieval outcomes, the checker recomputes the sha256 and byte size over the retained content and compares them against the recorded fields — a mismatch is a correspondence failure. The checker gains the v3 registry entries and no new check kinds beyond that verification.

## Witnesses (deterministic; stub model where a worker is needed)

- **R1 Discovery without contents:** `sandbox.list` over the three run sources returns structure maps whose total size is a small fraction of the corpus, and contains no body text beyond headings.
- **R2 Selective retrieval:** a scripted worker retrieves one named section of the index tail (e.g. a single INDEX entry) and the returned bytes match that section exactly — the rest of the file never crosses.
- **R3 The bound holds:** an oversized range request and an oversized whole-file read are each refused with the bound named; nothing partial is returned.
- **R4 Search within the wall, completely:** a search returns labelled passages from permitted material; a search aimed outside `sources/` (and a list of a non-permitted path) are refused, and no metadata about the outside is returned. A query with more matches than one page returns page 1 with `total_matches` and a continuation; page 2 fetched by continuation is the deterministic next slice, and the two pages together contain no duplicates and no silent gap. An ambiguous heading request (a repeated heading name) is refused with the match count and line numbers named.
- **R5 Successive, agent-directed retrieval:** a scripted worker performs list → search → read_range in sequence, each request informed by the previous result, all recorded as dispatches with parameters, result hashes and sizes. The same run witnesses the retention rule: a result pulled in iteration 1 is **not** re-presented in iteration 3's package; re-pulling it reproduces byte-identical content under the same recorded hash; and the worker's sandbox notebook round-trips (write a note, read it back in a bounded range).
- **R6 The whole-collection proof:** across R5's run, the sum of returned content is strictly less than the corpus size, and no single result exceeds the ceiling — the worker demonstrably worked without swallowing the library.
- **R7 Checker correspondence:** the record of R5 replays clean under the independent checker with the v3 registry in both copies.

## Run integration (settled with the run release, not silently)

Attempt 7, when released, keeps the original assignment, the same three sources and manifest, and the Groq route with the pinned model. Two run-scope questions are named for that release, not decided here: (a) the grants gain the three retrieval tools (a case/assembly change under the existing grant machinery); (b) the **step ceiling** — successive retrieval spends steps differently than two big reads; whether {12, 600} still fits is Vane's call at the release, with the witness runs' step counts as evidence.

## Out of scope

The rest of A4 (skills loading, publication, environment beyond the sandbox); any change to the assignment, sources or manifest; streaming; package slimming as a substitute (the package's own weight may be examined separately — it is not this piece); any change to the loop's accounting, the deadline, or the checker beyond the registry addition.
