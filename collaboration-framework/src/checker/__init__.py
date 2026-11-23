"""The independent checker — Piece 7 (SPEC SHEET §3.10: R4, R28).

A separate implementation of the record's verification: chain
integrity, sequence structure, replay of the complete record fold,
projection comparison, and seal correspondence. It shares no code
with the record service — its only import from the substrate is
`fabric.canonical`, the record-format and hashing primitive (the
format, not the logic). It produces per-check evidence for the
examiner; it records no findings, makes no judgements, and emits
no run-level verdict (R28).
"""
