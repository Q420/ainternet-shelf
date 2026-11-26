# BUILD SCOPE + PROCESS TREE — The Amended Road (§6), 2026-11-26

**Authority:** AMENDMENT-SECTION6-ROAD-2026-11-26.md, ACCEPTED by Ben
2026-11-26 01:43 MST with the examiner's refinements
(VANE-EXAMINATION-SECTION6-AMENDMENT-2026-11-26.md). Ben's build order:
"Proceed with you and Vane's plan" (01:45 MST). **Builder: Remmy's own
hands** (Ben's standing order, 2026-11-25 23:41). This paper is the
scope and the tree; the tree goes to the examiner before the build
dispatches (Ben's major-build rule, 2026-11-25 23:36).

**The symptom:** the cycle walk cannot complete under the per-call
regime — honestly counted, its ordinary calls exceed the cap the old
accounting waved through (gptoss11, call 2: 5,735 wire tokens against
a 532 package estimate).

**The system producing it:** the road layer of the office cycle —
counting (tool_policy/adapter), admission (loop), transport pacing
(adapter/driver), and package assembly (loop/tool_policy) — built
around a per-request size restriction doing a rate limit's job.

**What will still be wrong if this build works perfectly:** the
worker's composition competence remains untested; the blind handoff,
A5 and A6 stand where they stood; TwIL-8B has no road into the room.
This build is the road only.

**Trade flag:** this build displaces the AIvory S4/S5 papers and any
further proof run until the road stands (Ben's accepted flag,
2026-11-26 01:33).

---

## The tree — six pieces, in order of operation

Foundations before what consumes them. Every piece consumes counted
tokens; counting is therefore Piece 1, and nothing above it is built
on the bytes÷4 estimator.

### Piece 1 — Counting (adapter + tool_policy)
A provider-equivalent counting function per seat: for the Groq
GPT-OSS seat, **o200k_harmony** over the rendered conversation
(messages with roles and channels, tool definitions, tool-call
structure, framing) — NOT the raw HTTP JSON body tokenized as text.
Other seats: their matched tokenizers where one exists; where none
exists, the bytes÷4 estimator, labelled an estimate wherever its
figure stands. Predicted input count recorded before dispatch;
the provider's returned `prompt_tokens` recorded after; the
discrepancy stands in the ledger as a measurement, and calibration
is conservative against observed discrepancies.
**Dependency to measure before building:** the counting library's
availability in this environment (o200k_harmony ships with OpenAI's
harmony tooling / tiktoken registry) — verified by a live import and
a count of a known string against Groq's returned usage on a past
capture, before any loop code depends on it.
**Acceptance:** on gptoss11's captured requests, predicted counts
stand within a stated tolerance of Groq's metered figures, and the
tolerance is named in the test, not implied.

### Piece 2 — The bucket (new route module; adapter transport seam)
One token bucket per route (provider account + model), shared by
every caller on that route — loop calls and any other driver call
alike. Reserve = counted input + the configured maximum output
allowance, taken **atomically** (a lock around inspect-and-reserve;
two callers cannot spend the same capacity). Rolling/provider-aligned
minute accounting, reconciled after each response against actual
usage and the provider's rate-limit headers where present. On 429:
respect Retry-After, bounded exponential backoff with jitter, no
retry storms. The 65-second pacing remains as the interim safeguard
until the bucket is proven in rehearsal; it is then retired, not
kept as a second limiter.
**Acceptance:** a rehearsal with two concurrent callers shows one
waiting, never both admitted over capacity; a scripted 429 shows
the backoff honouring Retry-After exactly once per refusal.

### Piece 3 — Spill (loop + tool_policy)
A tool result over **4,096 counted tokens** does not ride whole:
the full content stands in the room/record (it already does), and
the package carries a reference — result identity, file address,
counted size, fingerprint, completeness, and a preview of at most
**512 counted tokens**. Retrieval through the existing pull
machinery in bounded slices with explicit ranges. File-backed
blocks are presented as bounded slices directly — no second copy
is manufactured. The threshold is sealed office-level configuration
at assembly, not a constant in the transport contract.
**Acceptance:** a scripted oversized result produces a package
whose carried content is the reference + preview only, and the
worker-side slice pulls return the original bytes exactly
(hash-checked against the fingerprint).

### Piece 4 — Shedding (loop)
A running total = the counted size of the context that will
actually be assembled for the next request (re-carried material
counted again, as it is sent again). At **70%** of the model's
window (GPT-OSS: 91,750 of 131,072) the ladder runs before the
call: clear spent tool-result payloads → trim oldest completed
cycle material → summarize older material into the journal.
**80%** (104,858) is the hard admission boundary. Shedding never
deletes: spilled originals remain retrievable, cleared means
cleared from presentation, summaries are derived matter and are
named as such; evidence, journal, summary, and presentation stay
four distinct things.
**Acceptance:** a scripted long walk crosses 70% and the record
shows the ladder's rungs in order, each shed item still
retrievable by its reference, and no call admitted past 80%.

### Piece 5 — The sealed run budget (generator/office + driver report)
At stocking, the office seals the run's allocation from the route's
daily pool (Groq: 200,000 TPD, rolling). The opening declares the
allocation and its basis; the worker cannot enlarge it. Accounting
keeps four figures distinct: provider limit / office allocation /
run consumption / remaining allocation. The report expands per the
examination's list: predicted vs actual input, output, totals,
tokenizer identity, reservation, bucket availability and waits,
retries, spill events with references, shedding events, running
context size, total consumption, remaining budget. Measured facts
and estimates are never blended in one figure.
**Acceptance:** a rehearsal run that exhausts its sealed allocation
stops at the boundary with the four figures reconciling to the
token, and the opening's declared allocation matches the seal.

### Piece 6 — Contract + rehearsal rebase (tool_policy + rehearsals)
A new presentation contract (office-cycle-v9) carries the amended
road; contracts v1–v8 keep their existing behaviour and records,
and the budget-refusal machinery is retired from new contracts
while standing for the old. The working-set rehearsal is rebased
to the amended road whole — cycle-honest included, its opening no
longer refused for size — and gains scenarios for Pieces 2–5.
**Acceptance (the proof sequence, the examiner's §4, verbatim in
effect):** the rebased suite passes whole; no call refused for its
individual size; every request shows preflight counting and
retrospective reconciliation; pacing and reservation behaviour
verified; spill, reference retrieval, and bounded slicing verified;
shedding without evidence loss verified; the sealed run budget
verified. **Only then** a cold live run on the Groq GPT-OSS seat
under the amendment's §5 acceptance.

---

## Out of scope, named
The opening's shape, the cycle's file-as-work-unit design, the
delivery contract and floor, the ten sealed grants, the working-set
carriage ceiling — untouched (the amendment's §3). No other seat's
road is rebuilt in this scope; the counting fallback serves them
until their own scopes are called. No UI. No AIvory work.

— Remmy, 2026-11-26. Drafted at Ben's order for the examiner.
