id: exon-d-ref-3-digest-policy
title: D-REF-3 — SHA-256 as the sole normative digest?
lane: EXON
prepared_by: Alex (recommendation), via Letters 06-07 and the serialization paper
deposited: 2026-11-16
status: waiting
options: Adopt — SHA-256 sole normative | Keep both digests normative
---
Two digests circulate in the record: the raw-file SHA-256 and the Git
blob ID. They are not the same number, and tonight proved both sides
can reproduce both (the Dictionary 0.4 digest check, Letter 17). Alex
recommends SHA-256 as the sole normative digest, with the Git blob ID
kept as repository metadata only — one controlling pin, no ambiguity
about which hash governs.

The question: adopt SHA-256 as the only digest a reference answers
to, or keep both normative?

Record: duenna/plaincode/EXON-REFERENCE-AND-RESOLUTION-DRAFT-01.md
(Draft 02, section 5, D-REF-3).
