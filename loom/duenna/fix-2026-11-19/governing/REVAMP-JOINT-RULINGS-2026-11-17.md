# REVAMP — OWNER RULINGS ON THE SEVEN OPEN JOINTS

Owner: Ben. Main chat, 2026-11-17 01:37 MST, ruling on the decision
sheet presented 2026-11-16 21:24 MST. These rulings govern the
framework revamp paper. They authorise no build by themselves.

## 1. Pins / minting — RULED
Each document's ID is made from the document itself: the SHA-256 of
its content. The ID is the pin — one string does both jobs, and it
changes the moment a single character changes, so it can never point
at the wrong version. Human names are labels, not references.
"The same document, new edition" is a chain of IDs linked by
supersession records, not a shared ID. Locators (line coordinates +
structural pointer) still ride with the reference. Consistent with
D-REF-3 (SHA-256 the sole normative digest). Building a minter
remains a separate build decision.

## 2. Dictionary revision — RULED
The next Dictionary revision carries the ruled words in: SUCCESS,
DESTINATION, YES, PREVAIL, plus the adopted category and collision
splits. The six foundational proposals (SEAT, GATE, CHECK, FLAG,
COMMITMENT, ARTEFACT) remain unadmitted. Dictionary 0.5 stands
unchanged until the revision is admitted.

## 3. Write-target packing — RULED
The orchestrator decides. What a Briefcase must contain for its task
is the orchestrator's decision, made per task — not a fixed
mechanical criterion. The Distiller packs to the orchestrator's
decision; the Warehouse Worker inspects against the source.

## 4. Distillation gate — RULED
A direct factual comparison to the source. A distilled shipment
passes its gate by being compared, factually and directly, against
the source it was distilled from.

## 5. Three-shelf taxonomy vs Comparator terminus — RULED
The owner's model (main chat, 2026-11-17 01:40 MST, his words):
"Things from the library are validated. They trickle down to the
shelf. Then once they're in the shelf they're absolutely double
checked and considered fact and then from there they trickle down
to Exxon."

The structure is a cascade, not rival shelves:
- LIBRARY (the AInternet, the whole collection): things are
  VALIDATED before moving down.
- SHELF: validated things trickle down onto the shelf; once on the
  shelf they are absolutely double-checked and CONSIDERED FACT.
  The shelf is the fact layer.
- EXON: fact trickles down from the shelf into EXON — the distilled,
  addressed, operational form of the shelf's fact. EXON's authority
  is inherited from the shelf; its failure mode is fidelity
  (mis-distilling fact), never sourcing.
The Comparator terminus holds unchanged: EXON is the reference side
because it is fact in working form; beneath it sits only the same
fact undistilled, so no further checking layer exists above it.

## 6. Custody venue — RULED
Ben's laptop. Custody-grade governed runs run in the laptop room,
where the supervisor chain works. The VM is disproved for that class
of run (NoNewPrivs=1, measured 2026-11-16). The supervisor-less smoke
remains a one-call exception, not a precedent.

## 7. Warehouse Worker receipt re-performance — DISCUSSED, AWAITING RULING
Referred to Claude; his discussion is filed at
record/CLAUDE-WW-RECEIPT-REPERFORMANCE-DISCUSSION-2026-11-17.md.
His line: make the receipt mechanical (enumerations and hashes, not
conclusions); the Comparator re-performs the mechanical comparison
from source and shipment directly and emits the diff record; a
second independent implementation checks the Comparator's tooling;
judgment claims are never re-checked by a checker — they are
declined in the receipt or escalated to the owner. Deterministic
checks run on every shipment; judgment claims are sampled (seeded
from the pin, chosen by the Comparator) or escalated on dispute.
Three questions were put to the owner. The owner delegated them
(main chat, 2026-11-17 01:52 MST: "I need you to make those
decisions. I know you will pick the most efficient options").
Decided by Remmy under that delegation, on the efficiency criterion,
correctable by the owner at any time:

(a) THE LINE. A respect is MECHANICAL if a fixed procedure can
decide it from the artefacts and the manifest alone, without reading
meaning: hash and byte equality; presence/absence against the
enumeration; counts; addresses resolving to their pinned targets
(EXON SUCCESS, resolution only); form and schema conformance; pin
correctness. A respect is JUDGMENT if deciding it requires
understanding content: semantic equivalence of distilled text,
fairness of a summary, adequacy of selection. Judgment respects are
declined in the receipt and routed to the owner; no checker
re-performs them.

(b) SAMPLING. Judgment claims are sampled at 1 in 5 shipments
(20%), the sample seeded from the shipment's pin and selected by
the Comparator, and presented to the owner — the owner judges; the
sample creates no checker verdict. Two triggers escalate a
shipment's judgment claims in full, sample or not: any mechanical
unmatched item in that shipment, and any dispute.

(c) THE GATE CONDITION. "Matched" is defined once, by rule: an item
is matched when its bytes are hash-equal at its pinned address. A
shipment passes the distillation gate automatically when the
Comparator's re-performance returns zero unmatched items and the
not-compared set contains nothing the comparison procedure required
comparing (undeclared gaps are UNKNOWN and the gate is not
satisfied). The Comparator still emits only the diff; the gate is
the fixed owner-defined function of the diff, applied as an
enforcement edge. No per-shipment owner ruling.

Joint 7 is RULED. All seven joints are now settled.
