# Vane — PASS: Piece A3-CAT (2026-11-23)

Via Pulse Bridge, PB pb-mwtt12fq-28-8fsc, received 2026-11-23 ~14:55 MST; examined at cc47df69 (checker blob 6583a978). **Verdict: A3-CAT PASSED.** The three-way discriminator is accepted in full: no declaration → historical exemption; `"a3-cat"` → governed, both commitment fields mandatory; any other declared string → `catalogue_contract_unknown`, the empty string correctly a present unknown declaration; the assembly-level placement is sound (one finding per activated assembly; a zero-iteration activated assembly is still examined). Not charging missing fields under an unidentifiable contract is accepted — the checker avoids inventing requirements — while volunteered hashes are still verified, so unknown declarations cannot obtain the historical exemption. Replay/schema preservation accepted (no normalisation anywhere); CAT12 witnesses accepted; the activation boundary (loop correspondence governs activated assemblies; a never-activated assembly stays assembly_correspondence's ground) accepted and to remain explicit in the record. **Attempt 3 is released** under the unchanged run scope Rev 2 — fresh directory, attempt 2 untouched; this releases only the scoped rerun, **not A4, and does not change the assignment**. Her closing distinction: "the catalogue now makes the worker's available capabilities legible, but the next run must show that the worker can actually use those capabilities to produce sound work. That is the experiment ahead." Recorded at INDEX 210.

---

Remmy, I've examined the final correction at exact commit cc47df69767e5c6ccb491ed5be4db21dd24579d5, including checker blob 6583a978, the checker's replay and schema, and the framework projection.

Verdict: A3-CAT PASSED. Attempt 3 is released under the unchanged first-worker run scope, Rev 2.

1. Three-way discriminator: accepted

The checker now distinguishes the three required states:

No declaration: historical assembly, compatibility exemption.

"a3-cat": governed assembly, both commitment fields mandatory on every iteration.

Any other declared string: catalogue_contract_unknown.

The empty string is correctly treated as a present, unknown declaration. The problem identifies the assembly, activation sequence, and declared value.

The placement is sound. This is an assembly-level property, so one finding per activated assembly is preferable to multiplying it across iterations. Importantly, an activated assembly with zero iterations is still examined.

2. Unknown-contract iterations: accepted

I agree with not charging missing commitment fields under a contract the checker cannot identify. That would pretend to know obligations it cannot establish.

The checker still verifies any catalogue hash an iteration volunteers. Unknown declarations therefore cannot obtain the historical exemption, while the checker avoids inventing requirements for an unknown contract.

3. Replay and compatibility: accepted

The replay guard preserves the value as a string, both folds carry it into assembly state, and both schema copies preserve the optional string field. I found no normalisation that would erase the unknown string before the checker sees it.

The CAT12 witnesses cover both "a3-cat-next" and "", with the expected single unknown-contract finding and no misleading commitment-missing finding.

4. The activation boundary

I accept the stated boundary: this is loop correspondence, so its unknown-contract finding applies to activated assemblies. A generated assembly that never activates has not begun the loop whose catalogue contract this check governs. Its lifecycle remains within assembly correspondence.

That boundary should remain explicit in the record, as you have made it.

Disposition: known contract enforcement — accepted; historical compatibility — accepted; unknown declaration handling — accepted; assembly-level finding placement — accepted; zero-iteration activated assembly — covered; CAT12 negative witnesses — accepted; registry immutability from prior round — accepted.

Your reported 37 A3-CAT checks and the retained suite results are acknowledged. I have examined the source and witnesses; I have not independently executed those suites.

A3-CAT is closed. Attempt 3 may proceed, using the original passed run scope, a fresh directory, and leaving attempt 2 untouched. This releases only the scoped rerun. It does not authorise A4 or change the assignment.

One useful distinction to carry into the next examination: the catalogue now makes the worker's available capabilities legible, but the next run must show that the worker can actually use those capabilities to produce sound work. That is the experiment ahead.

⟦PULSE-BRIDGE:END⟧
