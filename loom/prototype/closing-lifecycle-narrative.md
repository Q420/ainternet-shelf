# Closing lifecycle — closing-lifecycle

One Stage 4-bound run, driven mechanically through the real socket service. Every line below is generated from the exported event history; the seq is the citation.

- seq 1 · RUN_OPENED — The run opened, bound to Rev 9 + Amendment A1 and the pinned examiner pack; the genesis state (six regions, four dependencies, the constitution) is carried inside this event.
- seq 2 · BOUNDARY_PROBE — Boundary probe attestation: before this run opened, the pre-run boundary probe ran against a disposable twin of this runtime (same layout, owners, permissions and service build) from the agent OS context. The twin's store and ground-truth files denied every direct and alternate-path read; forged-token and issuance attempts on the data socket were refused; legitimate operations through the harness succeeded. This event attests to that twin probe — the experimental store itself was not probed, and no probe reads are in this history.
- seq 3 · DISCOVERY — Agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa opened Interactions (version 1) by reading the fabric directly.
- seq 4 · DISCOVERY — Agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa opened Continuity (version 1) by reading the fabric directly.
- seq 5 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened Components (version 1) by reading the fabric directly.
- seq 6 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened State (version 1) by reading the fabric directly.
- seq 7 · DISCOVERY — Agent cccccccc-cccc-4ccc-8ccc-cccccccccccc opened Presentation (version 1) by reading the fabric directly.
- seq 8 · CONTRIBUTION_ACCEPTED — A contribution by agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa was accepted and committed, changing Interactions.
- seq 9 · FACET_STATUS — The facet Interactions is now unexamined (it was open), on the evidence the record holds.
- seq 10 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 11 · CONTRIBUTION_ACCEPTED — A contribution by agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb was accepted and committed, changing State.
- seq 12 · FACET_STATUS — The facet State is now unexamined (it was open), on the evidence the record holds.
- seq 13 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 14 · CONTRIBUTION_REJECTED — A contribution was rejected as structural: it violated invariant S3.
- seq 15 · EXAMINATION_RECORDED — An examination of Interactions, Continuity was recorded and raised a new semantic tension.
- seq 16 · TENSION_RAISED — A semantic tension was raised over Interactions, Continuity by an examination report.
- seq 17 · ASSESSMENT_RECORDED — An assessment of a tension was recorded, position addressed.
- seq 18 · TENSION_STATUS — The tension over Interactions, Continuity was examined: its first assessment is on record.
- seq 19 · ASSESSMENT_RECORDED — An assessment of a tension was recorded, position clarifies.
- seq 20 · COMPLETION_CLAIMED — A completion claim was recorded; whether it counts is a matter of the evidence binding, computed from the record.
- seq 21 · FACET_STATUS — The facet State is now claimed (it was unexamined), on the evidence the record holds.
- seq 22 · ASSESSMENT_RECORDED — An assessment of a facet was recorded, position examined.
- seq 23 · FACET_STATUS — The facet State is now complete (it was claimed), on the evidence the record holds.
- seq 24 · COMPLETION_CLAIMED — A completion claim was recorded; whether it counts is a matter of the evidence binding, computed from the record.
- seq 25 · FACET_STATUS — The facet Interactions is now claimed (it was unexamined), on the evidence the record holds.
- seq 26 · IDLE — Agent cccccccc-cccc-4ccc-8ccc-cccccccccccc chose to idle: it took no action this turn.
- seq 27 · CONTRIBUTION_ACCEPTED — A contribution by agent aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa was accepted and committed, changing Continuity.
- seq 28 · FACET_STATUS — The facet Continuity is now unexamined (it was open), on the evidence the record holds.
- seq 29 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and failed: structural check(s) S1 did not pass on the current state. No seal was issued.
- seq 30 · TENSION_RAISED — A structural tension was raised by the checker (S1): the records it names are inconsistent in the current state.
- seq 31 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened Components (version 1) by reading the fabric directly.
- seq 32 · DISCOVERY — Agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb opened State (version 2) by reading the fabric directly.
- seq 33 · CONTRIBUTION_ACCEPTED — A contribution by agent bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb was accepted and committed, changing Components, State.
- seq 34 · FACET_STATUS — The facet Components is now unexamined (it was open), on the evidence the record holds.
- seq 35 · FACET_STATUS — The facet State is now unexamined (it was complete), on the evidence the record holds.
- seq 36 · SEAL_ATTEMPTED — A weave seal was attempted after the accepted commit and passed: every structural check succeeded on the current state, and a seal stands at this position. The seal certifies structure only; it grants no semantic clearance.
- seq 37 · TENSION_STATUS — A structural tension was resolved: the S1 check, re-run against the tension's original affected records by the passing seal attempt at sequence 36, found the inconsistency gone.
- seq 38 · RUN_CLOSED — The run was closed. Its final state hash and chain head stand in this record; what an external anchor does and does not establish for them is stated in the Stage 4 build notes (B7), not claimed here.

Final facet accounting (derived): Components = unexamined, Interactions = claimed, State = unexamined, Continuity = unexamined, Presentation = unexamined, Operations = unexamined.

Anchor: content-addressed archival anchor — produced by the closing exercise script from the service's own exported history; an archival record of the run's tail, NOT an independently trusted attestation.
History SHA-256 (canonical events): 4e2aa66d020b75f75b9b3e8a4209a00c1d7770b3635cfb9cb3934c0df00123bf.
