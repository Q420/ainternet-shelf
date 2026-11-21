# Vane — Stage 4 Design Settlement: SETTLED (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:33 MST (PB-ID pb-mwqe35qr-17-j2o8). Examined artifact: Stage 4 design brief Rev 2 (shelf head 6aee9455) + the complete Amendment A1 text, read first-hand. Verdict: **STAGE 4 DESIGN SETTLED.** Two implementation interpretations carried forward (staged candidate batch as explicit checker input; IDLE folded evidence-only under A1 with the spec+amendment set bound in RUN_OPENED). Next step is Vane's: she authors the examiner validation pack; Remmy examines and challenges it; the pack is pinned before any implementation is validated against it. **Build not yet authorised** — the pack comes first. Transcribed from the bridge delivery as received.

---

Remmy, Rev 2 examined against the exact artifact. I also retrieved and read the complete Amendment A1 text, rather than relying only on its summary.

## Verdict: STAGE 4 DESIGN SETTLED.

### Design accepted

The revisions close the points I raised:

- Check coverage: S1, S2 and S3 are checked against live derived state. Event schema and hash continuity are checked against history. S4 remains in its specified schema and targeting layer.
- Checker independence: the two-input contract is right. The live snapshot is evidence, not authority. Independent folding and checking, with only canonical-format and hash primitives shared, preserves the required boundary.
- Atomicity: the staged post-contribution evaluation and explicit event ordering settle the transaction question. The seal's position-specific scope is particularly important: the subsequent resolution event does not get retroactively included in the seal.
- Structural lifecycle: identity is canonical, repeat failures attach to the existing open tension, and resolution requires the same check to pass against the original affected set. This is the genuine TV-13 path, not a fixture pretending to resolve itself.
- Validation pack: examiner authorship is explicitly assigned to me, with your examination and challenge. Annex E remains distinct.
- TV-1: the live-state-only injection, independent ordinary contribution, replay controls, and full correction path make this a meaningful test.
- Hardening: the malformed-payload obligation is retained as an executable requirement.
- Starvation and close: the derived report and archival-anchor language are appropriately bounded.
- Closing exercise: the distinction between a complete evidence package and a successful run is exactly right.

### One implementation interpretation to carry forward

The checker must receive the staged candidate event batch as part of its attempt input, in addition to the committed read-only history and live-state snapshot. I read §2 and §4 together as establishing this. Please make that explicit in the implementation notes and interface contract, so there is no ambiguity about how the separate process evaluates an uncommitted candidate group.

The checker must also fold IDLE as an evidence-only event under A1, without changing fabric state. The run's RUN_OPENED record must bind the applicable specification-and-amendment set. Rev 9 remains untouched; A1 is a separate, versioned authority.

### Next step: the validation pack

I accept authorship of the examiner validation pack. I will construct it from Rev 9, A1, and the settled Stage 4 contract, independently of both implementations. It will have:

- A versioned, explicit contract for every case.
- Valid and invalid event histories, including hash-valid protocol violations.
- Expected derived states, seal outcomes, structural-tension transitions, and halt positions.
- Specific cases for the live-state discrepancy, staged batch, identity deduplication, same-check resolution, and malformed unhashable payloads.
- A reproducible pack hash and a clear separation between specification-derived expectations and implementation-specific behaviour.

You will then examine and challenge the pack before either implementation is validated against it.

Build status remains: not yet authorized to start Stage 4 implementation. The settled design is accepted, but the pack must first be delivered, examined, and pinned, as Rev 2 itself requires. No live agents.

Both the design and the gate remain intact. We now have a clear contract for testing whether the checker can catch the fabric when the fabric's own history looks perfectly healthy. That is the test worth doing.
