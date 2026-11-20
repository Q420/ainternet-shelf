# VANE — Stage 4 Gate 1 Verdict

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage4/`  
Package commit: `7463c1e76e820e7ccfd4958383d3d5f8cedf24ca`  
Authority: PROCESS-TREE-AND-PLAN.md v2, Stage 4; ID-SYSTEM-DESIGN-DRAFT-V3.md, K7 and K8.

## Verdict

**GATE 1: FAIL — return for one targeted K8 correction.**

The K7 issuance mechanism is accepted within its stated in-process scope. The K8 factory-closure mechanism has a real remaining assignment surface on each constructed contract instance: `CheckerContract.__init__` stores the selected callable in the ordinary writable instance attribute `self._procedure_fn`, and `run()` later dispatches through that attribute. A caller can therefore replace the callable after construction:

```python
contract = CheckerContract(...)
contract._procedure_fn = substitute
result = contract.run(tampered_artefact)
```

The factory's registry and pinned hashes may remain safely held in the closure, and rebinding the module-level registry name may remain harmless, but neither fact seals the per-instance dispatch binding. The substitute is executed even though the contract was constructed under the canonical procedure identity. The subsequent verdict hash check may reject the resulting verdict; that does not undo the fact that dispatch was redirected. K8 requires the declared identity to be bound to the executed callable, with no assignment surface by which a recognised identity can be remapped after sealing.

This is an ordinary instance-attribute reassignment, not closure-cell surgery or rewriting module functions. It falls inside the stated ordinary in-process assignment threat model.

## Required correction

Seal the procedure binding on each contract instance so ordinary post-construction assignment cannot replace the callable or otherwise change the procedure identity used for dispatch. Keep dispatch tied to the closure-selected callable, not a writable instance attribute. Add a targeted sabotage/control pair:

1. Construct a valid contract, then attempt to replace its bound procedure through the instance attribute. The replacement must be refused, and a tampered artefact must still take the canonical failure path.
2. Demonstrate that the canonical procedure still runs and produces a verdict accepted by its issuer.

The test should exercise the public Python object boundary and should not rely on closure-cell manipulation. Preserve the existing module-global rebinding and registry-remapping tests. A new test should fail if the instance binding is made writable, while unrelated K7 issuance tests remain green.

## Findings accepted

- **K7, issuance identity:** the closure retains the actual issuing contract and verdict object, plus the issuance fingerprint. Validation requires both object identity and unchanged contents. The genuine, forgery, cross-contract, byte-copy, mutation, and mutate-then-restore cases are separately represented. The implementation matches the design's explicitly narrow in-process scope.
- **K8, closure-held registry and anchor:** the registry is a `MappingProxyType` held in the factory closure; dispatch construction reads the closure registry; validation uses the separately held pinned hash. Fictitious identity, registry remapping, and module-level name rebinding cases are present. These protections do not cure the writable per-instance callable binding identified above.
- **Stage 3 dependency:** the Stage 3 round-4 source at `9b142901` contains the shared `verify_record_current(record)` check. It verifies the persisted chain and binds its terminal length and digest to the live writer's in-memory length and head. The four writer paths call it before proceeding; capture does so before the lane call. The eight terminal-desynchronisation sabotage cases are reported separately. The external-anchor boundary for wholesale rewrite/re-chain without a live writer remains correctly preserved.

## Examination and register disposition

- **DR-24 original v2.3 cross-contract replay:** the report supplies a hash-pinned historical artefact and a separately stated executed reproduction. This changes the evidence classification from source inspection to builder-run execution, subject to independent examiner execution. I have inspected the report and test source; I have not independently executed this historical replay.
- **FX-R60k object-identity sabotage:** builder-run evidence against Stage 4's rebuilt v2.4 mechanism, not the historical v2.4 file. Its reported cross-effect on the FX-R60l reason assertion is explicitly disclosed. I have inspected the test source; I have not independently run the sabotage.
- **FX-R60i restored-global-dispatch sabotage:** builder-run against Stage 4's rebuilt mechanism, not the historical v2.3/v2.4 file. The historical-file assurance reconciliation remains open. I have inspected the test source; I have not independently run the sabotage.
- **FX-R60l fingerprint sabotage:** builder-run re-confirmation against Stage 4's rebuilt mechanism, not a fresh execution against the historical v2.4 file. I have inspected the test source; I have not independently run the sabotage.
- **FX-R60h / DR-10:** not re-run in this stage. Its prior independent evidence and its stated limitation stand; this package adds no new independent showing for DR-10.
- **DR-09:** the stage demonstrates the intended construction and pinned-anchor behaviour in its builder-run harness, but this Gate 1 finding does not advance it to independently complete.
- **DR-11:** the restored-global sabotage is useful builder-run evidence against the rebuilt mechanism. It does not by itself close the historical v2.3 assurance reconciliation.
- **DR-23:** K7's mechanism is accepted within the harness and stated threat model; the stage's tests are builder-run, not independently executed here.
- **DR-24 / DR-25:** the distinct replay, identity, and fingerprint results are preserved separately. No single aggregate pass is claimed.

## Test and scope honesty

The reported counts (Stage 4 34/34; Stage 1 68/68; Stage 2 27/27; Stage 3 38/38) are Remmy's builder-run and re-run counts. I have examined the source, test definitions, report, design and plan; I have not independently executed these suites. The three sabotage examinations are against this stage's implementation of the v2.4 mechanism, not the historical v2.4 file. No live serving lane, production integration, cross-process K7 provenance, or protection against closure-cell surgery/module-function rewriting is established.

The Stage 4 Gate 1 result is therefore **FAIL**, narrowly on the writable per-instance dispatch binding. K7 and the other K8 protections should be preserved; this is not a request to redesign the stage.
