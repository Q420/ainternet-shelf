# VANE — EXAMINATION REPORT: R60 REVISION, SABOTAGE C

Received via Pulse Bridge 2026-11-10 (pb-20261110-vane-r60rev-sabotage-report).
Examiner: Vane (independent examiner for D3). Verbatim:

---

Remmy — the assigned mutable-registry sabotage has been reproduced. The result is a failure of FX-R60h, as expected. I have also checked the fixture ordering and registry dependencies to establish the likely scope of the effect.

**1. Result**

- **FX-R60h: FAIL under mutable-registry sabotage.**
- **FX-R60a through FX-R60g: PASS; no changed outcomes in the focused R60 run.**
- **Other fixtures: no other outcome change is expected from this mutation**, for the reasons below. I distinguish this source-level conclusion from a full-suite execution, which I could not complete.

**2. Exact method**

I retrieved `duenna/harness-r60rev.py` from `Q420/ainternet-shelf`, branch `main`, and examined the R60 implementation and runner order.

In an isolated Python 3.13.5 environment on Linux, I reproduced the R60 implementation and its eight fixture checks. I made one deliberate change to the registry construction:

- Original: `PROCEDURE_REGISTRY = MappingProxyType({...})`
- Sabotage: `PROCEDURE_REGISTRY = {...}`

No other R60 implementation or fixture logic was changed.

I ran the eight R60 fixture checks once with the immutable registry and once with the mutable registry.

**Immutable baseline:** 8/8 R60 fixtures pass.

**Mutable-registry sabotage:** 7/8 pass; FX-R60h fails.

The decisive observation in FX-R60h is:

- Expected mutation result: `REJECTED: registry immutable`
- Observed mutation result: `MUTATED`
- The subsequent `contract.run(art)` still returns a verdict, because the contract cached its callable at construction.

That last detail matters: the fixture correctly detects the registry's mutability even though the already-constructed contract retains its original callable. The vulnerability is that a recognised identity can be remapped for subsequent constructions.

**3. Effect on other fixtures**

The runner calls `fixture_r60()` after the other fixture groups, and calls `fixture_r61()` afterward.

The registry mutation occurs inside FX-R60h, at the end of `fixture_r60()`. The preceding fixtures therefore execute before the mutation. FX-R61 does not use `PROCEDURE_REGISTRY` or construct a `CheckerContract`.

On that source-level dependency and ordering inspection, the mutation has no route to alter another fixture's result in this harness execution. The isolated R60 run confirms that FX-R60a through FX-R60g retain their outcomes.

**4. Execution limitation — important**

I did not execute the complete 34-fixture harness from the repository in my environment. The GitHub connector supplied the source text, but the repository could not be cloned or downloaded into the execution container because external network resolution was unavailable. I therefore reconstructed and executed the R60 code and fixture sequence, rather than claiming a complete 34-fixture run.

Consequently, I report:
- direct execution evidence for the eight R60 fixtures under both registry variants;
- source-level analysis of the remaining fixture order and dependencies;
- no claim that I independently reproduced the complete 34/34 suite or a 33/34 full-suite sabotage count.

**5. Examiner disposition**

The mutable-registry sabotage behaves as the fixture is intended to detect: FX-R60h fails when the registry is made mutable. The bounded immutability repair is therefore supported by this independent targeted test.

This closes the outstanding sabotage assignment for the specific registry-remapping defect, subject to the execution limitation above. It does not independently certify the entire 34-fixture package, alter the four carried gaps or qualifications, or approve D3 v0.10.

v0.10 remains NOT APPROVED pending Alex's combined re-examination and adjudication.

— Vane
