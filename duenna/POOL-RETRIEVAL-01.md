# POOL RETRIEVAL 01 — existing mechanisms, checked before designing

Requested by Alex (pb-20261111-doc-id-ledger-addendum-
response) before vocabulary or mechanics are settled.
Run by Remmy, 2026-11-11, against the admitted corpus
(1,156 sections). Crusher answers were invoked with
Alex's phrasing; Remmy's own index scan follows each
answer, labelled as hers. Absence and retrieval miss
are distinguished throughout.

## Q1 — Infrastructure Gap 2 and its original definition of atomic live-head updates
**Crusher: substantive.** Gap 2 is "Atomic live-head
update", **exon-infrastructure-gap-register#003**,
status UNKNOWN — not established by retrieved corpus.
Not established: a canonical live-head record for a
commitment chain; an atomic compare-and-set or
equivalent single-winner update; a rule for which
successor becomes operative when two authorised
successors target the same predecessor; a durable
record of rejected or competing branches. Machinery
required (quoted from #003): "One authoritative head
per commitment chain. A single atomic operation that
checks the expected predecessor and changes the head.
A deterministic conflict result when the expected
predecessor is no longer current. Preservation of
losing successors as visible, non-operative records.
A read-after-write confirmation identifying the new
live head." Corroborated at exon-field-matrix-02-
alex#017 and exon-dictionary-04#025 ("Gap 2 — atomic
live-head update (UNKNOWN)").

## Q2 — Existing master-ledger, registry, version-pointer or supersession mechanisms
**Crusher: UNKNOWN as to mechanisms**, with the
record stating so explicitly: the matrix "does not
claim that the following mechanisms exist" — task
registration/registry versioning (Gap 1), atomic
live-head (Gap 2), concurrency/conflict resolution
(Gap 3), a dedicated authority registry (Gap 5)
(exon-field-matrix-02-alex#017). General supersession
policy: "Partially evidenced; general policy UNKNOWN"
(exon-infrastructure-gap-register#005). Dictionary
fields (task_registry_ref, hash chains) are "hash-
chain design, not an existing capability claim"
(exon-dictionary-03-reconciliation#008).
**Remmy's scan:** the string "master ledger" occurs
in **zero** sections — a true absence; the term is
Ben's, new tonight. The BridgePress serial ledger is
a working instance of the pattern (serials extracted
from the artefacts; ledger generated from the shelf)
but lives outside the retrieval corpus; sections
mentioning BP serials or a serial ledger: 8.

## Q3 — Existing generation identifiers and manifest conventions that might conflict
**Crusher: UNKNOWN** — its closest sections were run
records, not conventions (a retrieval miss in form:
no convention surfaced). **Remmy's scan:** no
generation-identifier or manifest convention in the
admission/manifest documents conflicts with the
proposed grammar; none establishes a competing one.
Stated as a scan result, not proof of absence.

## Q4 — Existing concurrency or compare-and-swap requirements
**Crusher: UNKNOWN** with closest sections in the
reconciliation and flag proposal. **Remmy's scan:**
partially a retrieval miss — the corpus DOES carry
the topic: **Gap 3, Concurrency and conflict
resolution, exon-infrastructure-gap-register#004**,
status UNKNOWN; and compare-and-set appears exactly
once, inside Gap 2's machinery list (#003). No
established concurrency mechanism or compare-and-
swap requirement exists beyond those gap statements.

## Summary for the design
Nothing established elsewhere conflicts with the
ledger design. The gap register has already written
the override's requirements list; the pool paper's
job is to adopt it, not to reinvent it. Gaps 1–5 all
remain UNKNOWN as mechanisms — the ledger is a
proposal toward Gap 2's machinery, and it changes
no gap's status by being described.
