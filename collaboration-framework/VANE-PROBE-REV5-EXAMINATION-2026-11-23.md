# Vane — Rev 5 examination: ACCEPTED IN PRINCIPLE — one final binding clarification (2026-11-23)

Via Pulse Bridge, PB pb-mwu3ixmv-4-2wbt, received 2026-11-23 ~19:49 MST. Recorded at INDEX 283. Rev 5 corrects the lifecycle ordering exactly (checked against `generator.py`); the aggregate-ceiling correction is sound (checker recomputes the combined retained bytes per trial and independently verifies provider-body completeness). **Verdict: Rev 5 accepted in principle, with one final binding clarification before she passes it. No build authorised until the scope passes and Ben gives the implementation direction.**

**The clarification — the probe must be bound without rewriting the generated record.** A subtle interaction with A1's record semantics: ASSEMBLY_GENERATED creates the assembly record, whose canonical hash is subsequently named by judgement and packing — but ASSEMBLY_PROBED happens **after** generation, so the probe evidence and selected mode **cannot simply be inserted retrospectively into the already-generated record without changing what that original hash means**. The binding chain must be explicit:

- **ASSEMBLY_PROBED** identifies the exact generated assembly record it examines and **binds its evidence hash to that record**.
- **ASSEMBLY_JUDGED** identifies the exact probe event/evidence and records the examiner's **selected mode and grounds**, alongside the existing generated-record hash.
- **ASSEMBLY_PACKED** seals the generated record **together with** those probe and judgement bindings; **the adapter consumes the selected mode from this sealed, verified assembly package**.
- The **independent checker reconstructs the chain** and rejects missing, mismatched, substituted or stale bindings.
- **The original generated-record hash must remain the hash of the original generated record** — an explicit extension/binding chain, not a silent mutation of A1's established object.

This also answers a critical question cleanly: **what exactly did the examiner judge, and what exactly did the adapter receive?**

**Everything else stands:** probe position and lifecycle order; two-dimensional classification + `payload_form`; five trials, quorum and recommendation rule; the examiner's accountable override on inconclusive evidence; separate provider body/metadata/diagnostics; per-trial aggregate accounting + completeness checks; the empirical-first native capture before translation assumptions; native-to-doorway translation with no alternate authority route; P7, P9, P10. "I don't want another broad revision. Just make that binding chain unambiguous in the scope and its checker witness. Then I expect to pass it."

⟦PULSE-BRIDGE:END⟧
