id: exon-serialization-five
title: The serialization five — Alex's package
lane: EXON
prepared_by: Alex (decision paper), via Letter 11
deposited: 2026-11-16
status: waiting
options: Adopt the package | Decide question by question
---
Five questions decide how EXON is written down as bytes. Alex's
decision paper recommends one package: JSON as the authoritative
representation; RFC 8785 (JCS) as the canonical serialization;
SHA-256 as the initial digest; an explicit sha256: algorithm
identifier; and canonical bytes authoritative, with pretty-printed
JSON as a human view only. The skeleton drafts were written
serialization-agnostic, so nothing built so far leans on the answer.

The question: adopt the package whole, or take the five questions
one at a time?

Record: duenna/plaincode/EXON-SERIALIZATION-DECISION-PAPER-01.md
(section 8 poses the five questions).
