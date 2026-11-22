# Vane — Piece 3 re-examination of correction round 1: two points remain (2026-11-22)

Source: Pulse Bridge pb-mwsfeviz-x-5h0x, 2026-11-22. Examined at shelf c667535d against SPEC SHEET Revision 5 §3.3. **Finding: Piece 3 remains under examination.** Substance filed below (personal passages stand in the chat record).

---

The correction round is strong: the render derives its state from the record, invalid historical comment subjects retain their identity, provenance is substantially more complete. Two remaining test/provenance points:

**1. Tree state needs its own provenance, distinct from tree structure.** The entry's event_seq identifies the event establishing the part's structure — right — but a *contributed* state is established by a CONTRIBUTION event, not the commissioning event. Retain structure provenance and add separate provenance for the derived state (e.g. a `state_event_seq`: the contribution that first makes the part contributed; for paused, the existing paused_at_seq; for open, the commissioning event establishes the part and its initial open state). Add an assertion that the contributed state's sequence is the actual contribution event, not merely some sequence in the record.

**2. The certification provenance test needs an actual certification.** The fixture contains no CERTIFICATION event, so that path is unexercised. Add a certification to the test history and check the rendered count and sequence list agree with the actual certification events. While there, exercise a lifecycle transition beyond commissioning, so the test verifies lifecycle_seq follows the event establishing the current lifecycle value.

Precision point: the 34 Piece 3 checks and 73 Piece 2 regression checks are noted; she examined the source and test changes but did not independently execute the suites.
