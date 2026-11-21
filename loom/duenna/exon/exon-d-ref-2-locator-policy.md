id: exon-d-ref-2-locator-policy
title: D-REF-2 — line coordinates, structural pointer, or both?
lane: EXON
prepared_by: Alex (recommendation), via Letters 06-07
deposited: 2026-11-16
status: waiting
options: Require both locators | Structural locator alone where it suffices
---
A reference can locate its source two ways: line coordinates (1-based,
inclusive, absolute in the pinned document) and a structural locator
(JSON Pointer). Alex favours requiring both — the line for human
eyes, the pointer for machines — even when a pointer is supplied.

The question: make line coordinates mandatory in every reference, or
allow a structural locator alone for source types where it suffices?

Record: duenna/plaincode/EXON-REFERENCE-AND-RESOLUTION-DRAFT-01.md
(Draft 02, section 5, D-REF-2).
