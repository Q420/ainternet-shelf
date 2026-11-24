# RETRIEVAL SCOPE — structured, agent-directed retrieval (first implementation) (2026-11-23)

Scope for Vane's examination, under her INDEX 235 settlement and Ben's direction (INDEX 236: pull structured access forward). A first implementation of the retrieval direction — **not** the A4 build. Authorises nothing until she passes it.

## The defect this repairs

The worker chooses which files to read but not how much it retrieves: `sandbox.read` returns a whole document, the result enters the next package in full, and the package re-carries it thereafter. Attempt 6's composition request (134,844 bytes) was refused by the provider (HTTP 413) — the pattern now has a hard external limit behind it, not only a design objection.

## The new tool contract (registry v3; v1/v2 frozen for history, both copies amended together)

Three retrieval tools, added to a new `tool-registry-v3` in the framework registry and the checker's independent copy, rendered in the worker's catalogue under the A3-CAT contract (assemblies declare the new catalogue contract; historical assemblies keep their exemption):

1. **`sandbox.list`** — discovery without contents. For a permitted path: the file's name, size, and **structure map** (for markdown/text: its headings with line numbers; for other text: line count). Returns no body text.
2. **`sandbox.read_range`** — a bounded slice: a permitted path plus a line range (or a heading's section, by heading text). The executor enforces a **hard result ceiling** (proposed: 12,000 bytes per result); a range whose content exceeds the ceiling is **refused with a recorded reason naming the bound**, and the worker narrows — a refusal is information, never a silent truncation.
3. **`sandbox.search`** — search within permitted material: a query string plus an optional path; returns matching passages (the matching line ± a bounded context, proposed ≤ 40 lines total per result set, each passage labelled with its file and line numbers), subject to the same per-result ceiling.

**`sandbox.read` is unchanged for files within the ceiling**; a read whose content exceeds the ceiling is refused on the same terms as an oversized range, naming the bound — whole-document injection of large material becomes impossible through any door, not just discouraged.

## Boundary enforcement (the manifest is the wall, for every operation)

Every retrieval operation — list, range, search, read — resolves its path against the sealed assembly's grants and the case's evidence boundary exactly as dispatch does today (the run's grants narrow reads to `sources/` and the manifest's three files). Search results and metadata obey the same boundary: a listing shows only permitted material; a search over a non-permitted path is refused; no sizes, headings or existence signals leak from outside the boundary. A request outside the boundary is a doorway refusal, recorded as today.

## How results enter the package

A retrieval result enters the next package as exactly what was returned — the bounded piece, with its provenance label (file, range/section, query). Nothing is auto-injected: the package carries the assignment, the catalogue, and the results the worker actually pulled, in the order it pulled them. Successive requests are the worker's: what it retrieves next is decided from what it has already seen, inside the existing loop and its step ceiling.

## Provenance and record evidence

Retrievals are tool acts under the existing A2 machinery — request (with its parameters), dispatch intent, start, outcome — so the record already carries them. The scope adds one requirement: each retrieval outcome's recorded payload includes the operation's parameters and the returned content's **sha256 and byte size**, so an examiner can reconstruct exactly what evidence the worker held at each step, and the worker's brief can be checked against it. The checker gains the v3 registry entries and no new check kinds; dispatch correspondence covers retrieval acts as it covers reads today.

## Witnesses (deterministic; stub model where a worker is needed)

- **R1 Discovery without contents:** `sandbox.list` over the three run sources returns structure maps whose total size is a small fraction of the corpus, and contains no body text beyond headings.
- **R2 Selective retrieval:** a scripted worker retrieves one named section of the index tail (e.g. a single INDEX entry) and the returned bytes match that section exactly — the rest of the file never crosses.
- **R3 The bound holds:** an oversized range request and an oversized whole-file read are each refused with the bound named; nothing partial is returned.
- **R4 Search within the wall:** a search returns labelled passages from permitted material; a search aimed outside `sources/` (and a list of a non-permitted path) are refused, and no metadata about the outside is returned.
- **R5 Successive, agent-directed retrieval:** a scripted worker performs list → search → read_range in sequence, each request informed by the previous result, all recorded as dispatches with parameters, result hashes and sizes.
- **R6 The whole-collection proof:** across R5's run, the sum of returned content is strictly less than the corpus size, and no single result exceeds the ceiling — the worker demonstrably worked without swallowing the library.
- **R7 Checker correspondence:** the record of R5 replays clean under the independent checker with the v3 registry in both copies.

## Run integration (settled with the run release, not silently)

Attempt 7, when released, keeps the original assignment, the same three sources and manifest, and the Groq route with the pinned model. Two run-scope questions are named for that release, not decided here: (a) the grants gain the three retrieval tools (a case/assembly change under the existing grant machinery); (b) the **step ceiling** — successive retrieval spends steps differently than two big reads; whether {12, 600} still fits is Vane's call at the release, with the witness runs' step counts as evidence.

## Out of scope

The rest of A4 (skills loading, publication, environment beyond the sandbox); any change to the assignment, sources or manifest; streaming; package slimming as a substitute (the package's own weight may be examined separately — it is not this piece); any change to the loop's accounting, the deadline, or the checker beyond the registry addition.
