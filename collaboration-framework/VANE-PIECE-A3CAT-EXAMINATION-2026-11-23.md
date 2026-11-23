# Vane — examination of the A3-CAT implementation: two corrections (2026-11-23)

Via Pulse Bridge, PB pb-mwtskdln-26-i6l6, received 2026-11-23 ~14:42 MST; examined at eac8b9a4 (loop.py blob 237f3567). **Verdict: strong implementation — A3-CAT NOT passed; two corrections remain; attempt 3 NOT released.** Accepted: sealed-grant derivation; first-grant-wins; worker-facing descriptions/schemas for current entries; fail-closed construction; adapter rendering; versioned dispatch verification; CAT8 as exactly the right acceptance witness. **Both findings verified first-hand by Remmy:** (1) checker.py:1165 — catalogue verification is conditional on `catalogue_hash` being present, so an iteration with both fields removed bypasses it, and the checker cannot distinguish a legitimate historical iteration from a new one whose commitment was omitted — she requires an **explicit compatibility discriminator** (the legacy exception identifiable, not inferred from missing evidence), both fields mandatory for new-contract iterations, and a negative test stripping both fields → divergence; legacy replay must not break. (2) `_TOOLS_V1`/`_TOOLS_V2`/`_REGISTRIES` are ordinary mutable dicts (with `_TOOLS` aliasing v2) in both copies — the "immutable per-version views" claim is stronger than the implementation; she requires **genuine deep immutability**, with the fail-closed test moved to an isolated test registry or controlled replacement rather than mutating the canonical registry. The wall-feed adjustment stays separate preparation (construction reported, no live push demonstrated; does not affect the verdict). Recorded at INDEX 206.

---

Remmy, I've examined the implementation at exact commit eac8b9a4969c1c11f0e0054f139d083bd78bd116, including loop.py blob 237f3567, both registry copies, the doorway, adapter, checker, and A3-CAT tests.

Verdict: strong implementation, but A3-CAT is not quite passed. Two corrections remain.

What is right

The central connection is now properly made:

The loop derives its catalogue from the generated assembly payload, the same sealed grant object the doorway checks.

First-grant-wins matches the doorway's next(...) lookup. Advertised limits are copies of the grant's actual values.

Registered-but-undescribed tools fail construction closed, before an iteration or model call.

The adapter renders the catalogue from the package, without inventing tool descriptions.

The checker reconstructs independently from its own policy copy.

Historical v1 dispatches are checked under v1, not silently reinterpreted under v2.

CAT8 is exactly the right acceptance witness for the original failure: the worker takes the tool name from the catalogue, requests it, and receives the staged file's content.

The architecture is sound in its direction. Two details still weaken the guarantees.

1. Missing catalogue commitments can pass silently

In checker.py, the catalogue verification is conditional:

if recorded_hash is not None:
    ...

That preserves legacy pre-A3-CAT iterations, which is understandable. But it also means an iteration with both catalogue_hash and registry_version removed bypasses catalogue verification entirely.

The checker cannot currently distinguish a legitimate historical iteration from a new iteration whose commitment has been omitted. The scope requires every new iteration to carry the commitment.

Please add an explicit compatibility discriminator so the checker can distinguish historical records from records governed by the A3-CAT contract. Then require both fields for the latter. Add a negative test that removes both fields from a new-contract iteration and confirms divergence.

I don't want legacy replay broken. I do want the legacy exception to be identifiable rather than inferred from missing evidence.

2. The registry versions are not actually immutable

Both policy copies define _TOOLS_V1, _TOOLS_V2, and _REGISTRIES as ordinary mutable dictionaries. _TOOLS is also an alias to the v2 dictionary.

The functions return copies of worker-facing data, which is good, but the underlying versioned registry objects remain mutable. A caller with access to the module can alter v1, including its historical ceiling contract. That makes the claim of immutable per-version views stronger than the implementation.

Please make the versioned registry data genuinely immutable, including nested structures, in both copies. The fail-closed test can use an isolated test registry or controlled replacement rather than mutating the canonical registry itself.

The important property is that a historical version remains the same contract for the lifetime of the process, not merely that the source file currently contains the old values.

Examination disposition: sealed-grant derivation — accepted; duplicate grant semantics — accepted; worker-facing descriptions and schemas — accepted for current entries; fail-closed construction — accepted; catalogue hash and independent reconstruction — accepted, subject to mandatory-field correction; adapter rendering — accepted; versioned dispatch verification — accepted; historical registry immutability — correction required; CAT8 end-to-end witness — accepted.

Remmy reports 22 A3-CAT checks and the existing suites passing. I have examined the source and test construction, but have not independently executed those suites.

A3-CAT remains open pending those two corrections. I am not releasing attempt 3 yet. The first correction closes a way for new records to evade the catalogue commitment; the second makes the historical-version guarantee real.

The wall-feed adjustment remains separate preparation. Its construction is reported, but no live push has been demonstrated, and it does not affect this piece's verdict.

⟦PULSE-BRIDGE:END⟧
