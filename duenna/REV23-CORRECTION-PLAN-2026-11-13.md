# REV 23 CORRECTION PLAN — 2026-11-13

Drafted by Remmy, for Alex's inspection. Answers his Rev 23 inspection
(pb-mwfqwllh-7-5gvm; NOT CLEARED: 3 HIGH, 2 MEDIUM) finding by finding:
the exact clause, the proposed resolution, the affected structural
requirements and schemas, the explicit acceptance tests, and the
evidence preserved. On his approval, Rev 24 is drafted from the
Rev 23 pin (8ce7b505) incorporating exactly what is listed here;
no correction code is written before Rev 24 clears. Rev 23, Rev 22,
the original Batch 3 bundle (f11d5375) and all earlier artefacts
remain immutable.

---

## Item 1 (HIGH) — two acceptance paths, one dispatch contract (§3.3)

**Clause.** §3.3's opening bullet: "`reference_insert` inserts
**only** results with `verification == "EXTRACTED"`…" — unamended
by the carried-field subsection, which says the same operation
accepts a second class. Both cannot govern.

**Resolution.** The opening bullet is rewritten as an explicit
two-path dispatch, and every later §3.3 reference to the acceptance
set is aligned to it:

- The insert tool takes exactly two presentation forms, and the
  form selects the path — there is no third form and no path
  shares the other's rules.
- **EXTRACTED path** — presentation: an `operation_id`. Rules:
  Batch 2's, word for word (acceptance conditions, registry,
  recomputation, exactly-once operation consumption, refusals).
  The carried amendment changes nothing on this path.
- **CARRIED path** — presentation: a citation
  `{event_id, payload_sha256}` and no value. Rules: §3.3's carried
  subsection (record-based acceptance, citation consumption,
  carried refusals).
- A presentation matching neither form refuses under the standard
  shape (reason `PRESENTATION_FORM`), and a presentation in one
  form is never evaluated under the other path's rules.

**Affected.** §3.3 opening bullet (rewritten); the carried
subsection's first paragraph (aligned wording: the carried class
is accepted "under the CARRIED path of the dispatch", not "by the
operation" generally); the identifiers bullet (unchanged in
substance — operation ids remain extraction-path only).

**Tests (named in Rev 24 §4, Batch 3 correction paragraph).**
(1) A carried citation presented where an operation_id is
expected, and vice versa — both refuse, neither path's rules
invoked (asserted by refusal reason and by absence of any
registry/citation consumption). (2) The Batch 2 refusal battery
re-runs unchanged on the EXTRACTED path (named regression, Item 5).

**Evidence preserved.** The corrected suite's transcript lines for
both cross-form refusals; the regression battery's transcript.

---

## Item 2 (HIGH) — SE-2 and SE-5 amended by identity class (§3.3)

**Clauses.** SE-2: "the insert interface's only handle is the
operation_id…". SE-5: "a consumed operation cannot be used
again" — neither covers the citation handle or citation reuse.

**Resolution.** Both requirements are amended in place, extraction
protections verbatim within their class:

- **SE-2 (amended):** the insert interface has exactly two
  handles — an operation_id on the EXTRACTED path, a citation
  {event_id, payload_sha256} on the CARRIED path. No value is
  ever a handle on either path; no third handle exists.
- **SE-5 (amended):** exactly-once consumption holds per identity
  class — a consumed extraction operation cannot be used again
  (unchanged), and a consumed citation cannot be used again; the
  two consumption sets are distinct and neither consumption
  touches the other. Replay verifies both: a record whose ledger
  shows two entries consuming one operation, or two entries
  consuming one citation, is a divergence.

**Affected.** §3.3 structural-requirements block (SE-2, SE-5
rewritten as above; SE-1, SE-3, SE-4, SE-6 unchanged); §3.7's
carried replay paragraph (gains the two-entries-one-citation
divergence clause, mirroring the operation rule).

**Tests.** (1) Citation reuse: a second carried insertion citing
an already-consumed event refuses `CITATION_CONSUMED`, emits no
ledger entry. (2) Cross-class independence: consuming an
extraction operation does not consume any citation and vice versa
(asserted via the registry state in both orders).

**Evidence preserved.** Transcript lines for both tests; the
registry-state assertions in the correction report.

---

## Item 3 (HIGH) — the carried LEDGER_ENTRY, field by field (§3.3, Harness §2.3)

**Gap.** Rev 23 says a carried entry "uses the established
schema" and adds `carried_from`, but never populates the schema's
existing fields for the carried case.

**Resolution.** Rev 24 §3.3 defines the complete carried
`LEDGER_ENTRY` payload against Harness §2.3's
{field, value, process_step, source_ref, source_hash, operation,
verification, verification_method} + the pilot provenance
additions:

| field | carried population |
|---|---|
| field | the record field's name (as extraction) |
| value | the value taken from the cited event's payload (never presented) |
| process_step | the **producing step** — the step whose verified output the value is (the analogue of the extraction entries' producing extract step) |
| source_ref | **null** — no source document exists; the record event is the source, identified in `carried_from` |
| source_hash | the cited payload's sha256 (`payload_sha256`) — the hash of the artefact the value was taken from |
| operation | `"reference_insert"` |
| verification | `"CARRIED"` |
| verification_method | `"carried: <producing step id>"` |
| rule_id (provenance addition) | **omitted** — no extraction rule produced the value |
| operation_id (provenance addition) | **omitted** |
| carried_from (provenance addition) | **present, required**: {event_id, payload_sha256, producing_step, check_event_id} |

**Exclusivity rule (stated in Rev 24):** a ledger entry carries
exactly one provenance form — an EXTRACTED entry carries
`operation_id` (and `rule_id`) and never `carried_from`; a CARRIED
entry carries `carried_from` and never `operation_id` or
`rule_id`. `materialise_ledger` emits entries under exactly this
schema, and §3.7 replay validates each entry against the same
field rules (an entry violating them is a divergence).

**Affected.** §3.3 carried subsection (the ledger-entry bullet
replaced by this table + rule); §3.4/§2.3-adjacent schema
references (none rewritten — the base schema stands; the pilot
additions block gains the exclusivity sentence); §3.7 replay
paragraph (schema-validation clause added).

**Tests.** (1) Schema assertion over every ledger entry of every
suite record: field presence per the table, null/omitted exactly
as specified, exclusivity holds. (2) Materialisation equality:
`ledger.json` bytes equal the canonical serialisation of the
record's LEDGER_ENTRY payloads under this schema (the existing
C3-A5 check, now run against the completed schema).

**Evidence preserved.** The schema-assertion transcript; every
run's `ledger.json` in the correction bundle (Item 5).

---

## Item 4 (MEDIUM) — the evidence comparison, exactly (§3.3)

**Clause.** "the cited list equals, as a set and in order, the
`source_ref`s of the construction's extraction results" — a set
has no order, and deduplication would erase legitimate repeats.

**Resolution.** The comparison is defined as an **ordered
sequence equality**, duplicates preserved: the expected list is
constructed by walking the tree's construction extraction events
(their `TOOL_RETURNED` payloads) **in record order** and taking
each result's `source_ref` in that order — one entry per
extraction operation, so a section supporting two extracted
fields contributes its reference **twice**. The comparison is:
same length, and elementwise equality at every position. No set
semantics, no deduplication, no sorting, anywhere in the rule.
§3.7's re-derivation uses the identical construction.

**Affected.** §3.3 carried subsection, acceptance condition (5)
(rewritten); §3.7 carried paragraph (aligned wording).

**Tests.** (1) Positive: a construction whose two fields extract
from the same section — the evidence list carries the reference
twice and inserts successfully (this case exists in the T05/T08
data: fixtures fields share sections — the test names the actual
pair from the run). (2) Negative: an evidence list with one of
the duplicates removed refuses `EVIDENCE_SET_MISMATCH`
(length mismatch); an evidence list with the two positions
swapped refuses (order mismatch) — where the record's data
provides two distinct references in sequence.

**Evidence preserved.** Transcript lines naming the duplicate-
reference pair and both refusals.

---

## Item 5 (MEDIUM) — the acceptance tests, specified in the spec (§4 + §3.x cross-references)

**Gap.** §0I summarises; the checks themselves are not specified
where an inspector can hold the build to them.

**Resolution.** Rev 24's §4 Batch 3 paragraph gains an explicit
**Batch 3 correction acceptance list**, each entry an assertion,
not a topic:

*Pin authority* — (a) substitution: a consumed file changed AND
its caller-supplied hash changed to match → pre-flight refuses;
(b) inventory-by-name: every artefact in the authority's consumed
inventory — the five Batch 1 data files named individually —
asserted present by name in RUN_STARTED's pin block; (c)
missing-entry: the caller configuration omitting an inventory
entry refuses; (d) extra-entry: the caller configuration adding
an entry refuses.

*Carried fields* — (e) eight-entry assertion: each T05 and T08
record carries exactly eight LEDGER_ENTRY events, one per
produced field, each satisfying Item 3's schema; (f) tampered
citation: a citation whose payload_sha256 does not match the
record recomputes → `CITATION_HASH_MISMATCH`, no entry; (g)
failed producing check: a citation to an artefact whose step's
CHECK_RESULT failed → `CITATION_CHECK_FAILED`, no entry; (h)
incomplete evidence: Item 4's two negatives; (i) citation reuse:
Item 2's test; (j) regression: the Batch 2 refusal battery
(S1–S5 + the correction's artifact-comparison and rule_id cases)
re-runs unchanged against the corrected tools on the EXTRACTED
path.

*Step budgets* — (k) [TOOL]/[RULE] over-budget: STEP_FAILED class
STEP_TIMEOUT, no STEP_SATISFIED and no passing CHECK_RESULT for
the attempt, the tree takes its failure branch; (l) [MODEL]
over-budget: STEP_FAILED class ADAPTER_TIMEOUT, same record
assertions; (m) coherence invariant asserted over **every**
record the suite produces: no (tree, step, attempt) carries both
a satisfied outcome and a subsequent failure.

*Chunk-sheet fidelity* — (n) C3-A2 at its wording: schema
assertions over **every** event of every record — field presence
AND declared types (seq integer; event/run ids strings;
recorded_at_utc ISO-8601-parseable; hashes 64-hex; payload
object); (o) C3-A6 at its wording: before/after listing of the
pilot root's parent compared — the only delta is the runs' own
directories — and a scratch `commitments/` directory asserted
byte-unchanged across the suite; (p) C3-B3 at its wording: for
every [MODEL] step, the STEP_TRIGGERED manifest's artefacts
recomputed from the cited producing outputs and deep-compared to
the step's declared inputs in the trees data; (q) C3-B10 at its
wording: the stopped-run record checked element by element
against Harness §6.4 (exactly one terminal event, last; chain
verifies to it; closed trees complete per declared sequence; the
open tree's completed steps a strict prefix; no events for unrun
steps; RUN_STOPPED carries reason + position) — each element its
own named check in the transcript.

**Affected.** §4 (the acceptance list added to the Batch 3
paragraph); §0J records the incorporation; header + register
updated per the established pattern.

**Evidence preserved in the correction bundle.** The corrected
suite's full transcript with every acceptance-list entry as a
named line; all run records AND their materialised `ledger.json`
files as named artefacts; the re-freeze continuation pinning the
pin authority and the corrected artefacts; the correction
checkpoint report discharging this plan item by item and the
chunk sheet line by line.

---

## Drafting order on approval

Rev 24 is drafted from the Rev 23 pin, incorporating Items 1–5
and nothing else; the diff footprint is confined to §3.1 (no
change — Item 3 of the original plan already landed there), §3.3,
§3.4 (no change), §3.7, §4, the header, and §0J. It is submitted
for Alex's inspection; the Batch 3 correction build proceeds only
on his clearance of the Rev 24 pin.
