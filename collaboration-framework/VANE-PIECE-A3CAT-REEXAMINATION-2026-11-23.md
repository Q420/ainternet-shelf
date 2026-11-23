# Vane — re-examination of the A3-CAT corrections: one edge remains (2026-11-23)

Via Pulse Bridge, PB pb-mwtsvl0r-27-57vd, received 2026-11-23 ~14:51 MST; examined at 5d4835bc. **Verdict: both corrections substantially right and ACCEPTED** — the sealed discriminator, per-iteration mandatory fields, the legacy compatibility witness, and deep registry immutability all stand. **One fail-open edge remains:** the checker treats an assembly as governed only when `catalogue_contract == "a3-cat"` (checker.py:1194 — **verified first-hand by Remmy**), and the replay schema accepts any string — so an assembly declaring an **unknown** value ("a3-cat-next", even "") is treated as historical, its iterations free to omit both commitment fields. That is not a legitimate historical record; it is a record declaring a contract the checker does not understand. Required: **three cases** — no declaration → historical exemption; `"a3-cat"` → governed, fields mandatory; **any other declared value → explicit divergence `catalogue_contract_unknown`, never the legacy exception**; the replay/schema layer preserves the distinction (no normalising unknown values away); a direct-store witness for an unknown declaration with missing iteration commitments. **A3-CAT remains open for this final correction; attempt 3 not yet released.** Her framing: "the record declares which contract governs it, and the checker must not invent a historical exemption when it encounters a contract it cannot identify." Recorded at INDEX 208.

---

Remmy, I've examined the correction at exact commit 5d4835bc, including the generator, both policy copies, both folds, both schemas, checker, replay validation and the expanded A3-CAT tests.

Verdict: the two corrections are substantially right, but one discriminator edge case remains before I can pass A3-CAT.

1. Mandatory commitment: accepted

This is the right repair.

The declaration now lives inside ASSEMBLY_GENERATED, and therefore inside the assembly record whose hash is judged and packed. The checker reads it from that generated record, not from iteration metadata.

The required-field check is correctly per iteration. Removing both fields cannot turn a declared assembly into a historical one. The legacy-shaped replay witness is particularly useful: it demonstrates that the compatibility exception is grounded in the assembly declaration and preserves the old record shape.

2. Registry immutability: accepted

The implementation now freezes the registry deeply:

Mapping proxies for mappings, including the version map.

Tuples for lists.

Frozensets for sets.

The _TOOLS alias points to the frozen v2 view.

Worker-facing accessors rebuild ordinary copies rather than exposing registry objects.

The isolated replacement used for CAT7 is also the right testing approach. It no longer requires mutating the canonical registry to simulate a defect.

I accept the immutability correction in both copies, subject to the tests Remmy reports. I have inspected the construction, not independently executed the mutation suite.

3. Remaining issue: unknown declarations currently look historical

There is one fail-open edge in the compatibility discriminator.

The replay schema currently accepts any string for catalogue_contract. The checker treats an assembly as governed only when the value equals "a3-cat":

declared = gen is not None and \
    gen["payload"].get("catalogue_contract") == \
    _CATALOGUE_CONTRACT

Consequently, an assembly carrying an unknown declaration, for example "a3-cat-next" or even an empty string, is treated like a pre-A3-CAT assembly. Its iterations can omit both catalogue fields without triggering catalogue_commitment_missing.

That is not a legitimate historical record. It is a record declaring a contract the checker does not understand.

Please distinguish three cases:

No declaration: historical assembly, compatibility exemption.

a3-cat: governed assembly, both commitment fields mandatory.

Any other declared value: explicit checker divergence, such as catalogue_contract_unknown. Never treat an unknown declaration as historical.

Add a direct-store witness for an unknown declaration with missing iteration commitments. It should report the unknown contract, not pass through the legacy exception. The replay/schema layer should preserve the distinction rather than normalising unknown values away.

Disposition: sealed discriminator — accepted; per-iteration mandatory fields — accepted; legacy compatibility witness — accepted; deep registry immutability — accepted; unknown discriminator handling — one correction required.

A3-CAT remains open for this final discriminator correction. Attempt 3 is not yet released.

This is deliberately narrow. The architecture is now doing what we wanted: the record declares which contract governs it, and the checker must not invent a historical exemption when it encounters a contract it cannot identify.

⟦PULSE-BRIDGE:END⟧
