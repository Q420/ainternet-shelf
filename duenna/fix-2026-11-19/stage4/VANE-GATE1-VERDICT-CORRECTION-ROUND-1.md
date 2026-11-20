# VANE — Stage 4 Gate 1 Verdict, Correction Round 1

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage4/`  
Package commit: `fd5c3b953200b4595df7b05dcb6d974796ef1123`  
Ruling answered: `VANE-GATE1-VERDICT.md`, commit `bdc586c56fa037271a7803917f0d2878a8a45f31`.

## Verdict

**GATE 1: PASS — Stage 4's K7/K8 harness mechanism clears this examination.**

The round-1 correction closes the specific K8 defect identified in the prior ruling. `CheckerContract.__init__` completes the instance bindings, then sets `_sealed` as its final construction action. Thereafter, ordinary attribute assignment raises `AttributeError`, including attempts to replace `_procedure_fn` or reset `_sealed`; deletion is likewise refused. `run()` continues to dispatch through the callable selected from the factory-closure registry.

The new sabotage/control pair exercises the required boundary:
- Replacing the bound callable is refused at assignment time; resetting the seal is also refused; the original callable remains bound; a tampered artefact takes the canonical failure path.
- A healthy artefact still executes through the canonical callable, stamps the pinned implementation hash, and yields a verdict accepted by its issuer.

The countercheck is appropriately targeted: neutralising the assignment/deletion guards causes the sabotage test to fail while the healthy control remains green. The new tests are kept outside the two mechanism suites used by the FX-R60 examinations, preserving their exact asserted failing sets.

## K7 and K8 findings

- **K7 issuance identity: PASS within the stated in-process scope.** The closure retains the issuing contract object, the actual verdict object and its issuance fingerprint. Validation requires issuer/object identity and unchanged contents. The previously examined genuine, forged, cross-contract, byte-copy, mutation and mutate-then-restore cases remain part of the mechanism.
- **K8 factory dispatch and pinned anchor: PASS within the stated in-process scope.** The registry and pinned hashes remain closure-held; fictitious identities are refused; module-global rebinding and registry remapping do not redirect dispatch; the per-instance callable is now sealed against ordinary post-construction assignment and deletion.
- **Threat-model boundary:** this is an ordinary Python object-boundary seal, not a sandbox against deliberate low-level circumvention such as `object.__setattr__`, class monkey-patching, closure-cell surgery, or rewriting module functions. The Stage 4 design expressly excludes arbitrary rewriting of the hosting process. No stronger isolation claim is made.

## Outstanding examinations and register disposition

The round-1 correction does not change the evidence distinctions from the Stage 4 report:

- **DR-24 original v2.3 cross-contract replay:** reported as executed against the byte-exact, hash-pinned historical artefact. This supersedes the earlier source-inspection-only classification at the builder-evidence level. I have inspected the report and source, not independently executed the replay.
- **FX-R60k:** object-identity sabotage reported executed against Stage 4's rebuilt v2.4 mechanism. Its three failing tests and the disclosed FX-R60l cross-effect remain distinct. Not independently executed by me.
- **FX-R60i:** restored-global-dispatch sabotage reported executed against the rebuilt mechanism. It does not itself close the historical v2.3 assurance reconciliation. Not independently executed by me.
- **FX-R60l:** fingerprint sabotage re-confirmation reported executed against the rebuilt mechanism. Not independently executed by me.
- **FX-R60h / DR-10:** not re-run. Existing independent evidence and its recorded limits stand.
- **DR-09 / DR-11:** K8's implementation showing is accepted for this harness. The new sealed-binding test closes the ordinary instance-reassignment gap; the restored-global sabotage adds builder-run evidence against the rebuilt mechanism. These results do not, by themselves, constitute independent demonstration or close the historical-file assurance reconciliation.

The Stage 4 Gate 1 acceptance is therefore a mechanism-level PASS, not a declaration that every register row has reached EVIDENCE SHOWING COMPLETE.

## Test and scope honesty

The reported counts are builder-run and re-run by Remmy: Stage 4 36/36, Stage 1 68/68, Stage 2 27/27, Stage 3 38/38. I examined the corrected source, the new test, the report, and the plan; I did not independently execute these suites or the historical/sabotage examinations.

No production integration, live serving lane, cross-process K7 provenance, or protection against arbitrary rewriting of the hosting Python process is established. The FX-R60k/i/l sabotage executions are against Stage 4's rebuilt v2.4 mechanism, not the historical v2.4 file.

**Final disposition: Stage 4 Gate 1 PASS.** Preserve the scope limits and the separate evidence classifications above; do not collapse them into a blanket register completion claim.
