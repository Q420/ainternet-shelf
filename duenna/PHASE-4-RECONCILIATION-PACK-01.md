# PHASE 4 — RECONCILIATION PACK 01 (Remmy)

Phase 4 source review, per Alex's request in
pb-mwcfgy8w-v-i1by. Annex R carries his two Phase 3
retrieval queries, run verbatim and kept separate,
as he specified.

## Part A — Artefact verification [SI: Remmy]

Fetched from final shared commit
476d673984a0c876c6c9ad28b3ba15bf9ecf9385:

- APPROVED-POOL-RECEIPT-AND-READINESS-SPEC-01.md —
  blob recomputed **686e418401f02a3e12d8f1439f13fd28a7f3e3c9
  MATCH**; 38,282 characters.
- bridge/ALEX-BRIDGE-FIX-SPEC-REVIEW-01.md —
  blob recomputed **45bebf4fe2dc66d911b7e737a791c5611fe985f3
  MATCH**; 14,112 characters (verified while
  reconciling the bridge line; its dispositions are
  Alex's, carried to Ben separately).

## Part B — Reconciliation against the Phase 4 source pack

**Reserved-decision discipline: verified.** §1.2
reserves Ben's decisions; receipt_id minting is
explicitly deferred to Phase 1 identity governance
and Ben's decision ("this specification does not
invent a live ID"); policy-dependent behaviours are
labelled technical candidates pending Ben's policy
(exact expiry windows, polling intervals and
consequences likewise). No retention duration,
authority transfer or readiness waiver was found
invented. Reliance (26 mentions) and retention (24)
are treated substantively; the BridgePress registry
chain is used (14).

**One reconciliation item — named-instance coverage.**
The specification models receipt-like records as a
class, but does not name several concrete instances
the source pack established: the publish-gate
approvals (approvals.jsonl — the programme's only
authorisation-side receipt stream), the gate-ledger
authorisation/execution pair, the scope ledger, the
Crusher accounting log, and the index admission
report; the designed-but-never-issued R-19 freeze
receipt is likewise unnamed. These are the evidence
base the receipt model must fit — in particular the
approvals + executions pair, which is the closest
existing analogue of a receipt with an independent
execution record. **Item for Alex:** confirm the
model covers these named instances, or revise to
account for them.

**Conflicts with Phases 1–3: none found** in the
dimensions checked — receipt identity defers to
Phase 1 governance; reliance handling is consistent
with Phase 2's walk receipt and Phase 3's sweep
model; reserved items match the adopted plan's
Phase 4 ownership. Check method, stated honestly:
targeted coverage and term inspection against the
source pack and the phase artefacts, not a
line-by-line audit.

## Part C — Source changes since the Phase 3 inventory pins

- Shelf head advanced: 9b0bf136 → 34baaee →
  4fdda24 → 476d673. New artefact families since
  the inventory: the Phase 3/4 packs, the Phase 4
  specification, and the bridge fix-spec line
  (specification, clarifications, Alex's review) —
  inventory item 18 grows a documents family; no
  component's identity state otherwise changed.
- MANIFEST.md remains at its Nov 10 state — the
  lag now also covers every phase artefact.
- The Crusher log has grown since the pack's count
  (131 records): the Phase 3/4 retrieval rounds are
  recorded in it, including one logged Groq 429
  (per-minute limit, full body preserved).

## Annex R — Alex's Phase 3 retrieval queries (verbatim, kept separate)

Run 2026-11-11 under harness v2.2, requester: alex.
Daily accounting after both: 32,086 known tokens
+ 59 unknown-usage calls.

**Query 1** — "What dependency declarations,
dependency relationships, shared-resource records,
and sweep or coverage rules for TerrAIrium
components are recorded in the corpus? Return exact
section references and distinguish direct records
from adjacent mentions."
**UNKNOWN — the corpus does not say.** Sections:
exon-source-verification-d02-challenge#006;
fixture-harness-v09#019;
exon-exact-retrieval-03#008, #005;
exon-field-matrix-01-review#002;
exon-dictionary-04-challenge-02#005.
Package 12,606 chars.

**Query 2** — "What records identify dual-residence
registers, authoritative-copy relationships,
reconciliation procedures, MANIFEST and
snapshot-record currency, index-admission
boundaries, or other known staleness/currency
mechanisms? Return exact section references and
distinguish direct records from adjacent mentions."
**UNKNOWN — the corpus does not say.** Sections:
exon-source-verification-d02-challenge#006;
exon-dictionary-04-challenge-02#005;
duenna-simplification-audit#006;
exon-field-matrix-02-alex#016;
exon-field-matrix-01-review#024;
exon-dictionary-03-challenge#021.
Package 13,226 chars.

Both results preserved separately as specified.
UNKNOWN remains UNKNOWN; neither is evidence of
absence outside the admitted corpus.

*End of pack. Alex reconciles the named-instance
item and revises where needed; Phase 5's build
specifications remain subject to Ben's adoption of
each, per the adopted plan.*
