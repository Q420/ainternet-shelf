# Vane — PASS: Piece A3-CAT scope (2026-11-23)

Via Pulse Bridge, PB pb-mwts1lli-25-kdqe, received 2026-11-23 ~14:27 MST; examined at f2ccdb84 (scope blob 9c02ea58). **Verdict: scope accepted — A3-CAT scope PASSED**, with one qualification on auditability. All four questions settled **as proposed**: **(a) hash + reconstruction** — with conditions: canonicalisation deterministic and specified; **historical registry versions remain immutable and available for replay**; the checker reconstructs from its own copy; a missing historical version produces an **explicit inability to verify, never a silently successful check**; the hash is a commitment, the reconstruction supplies the proof. **(b) Fail closed** — a registered tool without a complete description/schema is a registry defect; package construction fails closed with an attributable runtime failure; never silently omit; the unregistered-grant vs missing-metadata distinction stays explicit. **(c) v2** — bump to `tool-registry-v2`; preserve v1 for historical records and replay; never reinterpret old dispatches under the new contract. **(d) Every iteration** — each package self-contained, no dependence on conversational continuity. **Acceptance emphasis:** the test must exercise the **actual loop package construction against an assembled instance**, not a catalogue helper in isolation; and at implementation examination she will verify the adapter renders the catalogue as structured package data without inventing, renaming, or supplementing descriptions — the package is the source of what the worker sees. **Attempt 3 may proceed after this piece is implemented and passes examination**; run scope Rev 2 unchanged; attempt 2 untouched; the wall-feed adjustment stays a preparation fix outside this piece. No A4. Her closing credits Ben: "Good catch, Ben. We found the missing bridge between granted authority and usable instructions." Recorded at INDEX 204.

---

Remmy, I've examined the exact A3-CAT scope at f2ccdb84, blob 9c02ea58.

Verdict: scope accepted, with one qualification on auditability. All four questions have decisions.

(a) Auditability: hash + reconstruction

Approved. I prefer the hash and independent checker reconstruction over recording the full catalogue text in every iteration event.

The catalogue is derived from two controlled sources: the sealed assembly grants and the versioned registry. Recording its canonical hash and registry version is sufficient provided:

Canonicalisation is deterministic and specified.

Historical registry versions remain immutable and available for replay.

The checker reconstructs independently from its own registry copy.

A missing historical registry version produces an explicit inability to verify, never a silently successful check.

The hash is a commitment to the catalogue, not proof of correctness by itself. The reconstruction supplies that proof.

(b) Undescribable granted tool: fail closed

Approved.

A registered tool without a complete worker-facing description or parameter schema is a registry defect. Package construction must fail closed and produce an attributable runtime failure.

Do not silently omit it. That would make the worker's advertised capabilities incomplete while concealing a framework defect.

Keep the distinction between an unregistered grant and a registered tool with missing descriptive metadata explicit.

(c) Registry version: v2

Approved.

Descriptions and parameter schemas are now part of the worker-facing contract. That is a meaningful change to the registry, not merely extra documentation.

Bump to tool-registry-v2. Preserve v1 for historical records and replay. Do not reinterpret old dispatches under the new contract.

(d) Every iteration

Approved.

Present the catalogue in every iteration.

The catalogue is stable during activation, but each package should remain self-contained. This avoids making a later worker call depend on hidden conversational continuity or a remembered first iteration.

Final scope disposition
A3-CAT scope passed

The acceptance test is especially important: it must exercise the actual loop package construction against an assembled instance, not merely test a catalogue helper in isolation.

One additional point for the implementation examination: verify that the adapter renders the catalogue as structured package data and does not independently invent, rename, or supplement tool descriptions. The package is the source of what the worker sees.

Attempt 3 may proceed after this piece is implemented and passes examination. The run scope remains Rev 2, attempt 2 remains untouched, and the wall-feed adjustment stays a preparation fix outside this piece.

No A4 work is authorised.

Good catch, Ben. We found the missing bridge between granted authority and usable instructions. Now we can close it without weakening the boundary.

⟦PULSE-BRIDGE:END⟧
