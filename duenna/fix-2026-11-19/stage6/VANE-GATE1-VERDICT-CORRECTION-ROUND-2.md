# Duenna Stage 6 — Gate 1 Verdict, Correction Round 2

Date: 2026-11-20  
Package examined: `duenna/fix-2026-11-19/stage6/`  
Package commit: `6fb8b9e23aa3002971998f3b9dd054f0405cb921`  
Prior return: `VANE-GATE1-VERDICT-CORRECTION-ROUND-1.md`, commit `b9916f4f6244861a0f91a4fe45ad07e7f12bdb60`.

## Verdict

**PASS — Stage 6 clears Gate 1 within the submitted harness and declared threat model.**

The two blocking K10 defects from correction round 1 are corrected in source, with targeted sabotage tests and healthy controls. The correction is appropriately narrow and preserves the previously examined K10, K12, G6 and historical-reproduction work.

## Correction 1 — authority capability cannot be self-issued

Accepted.

- `AttributionAuthority` construction now requires the module-private issuance token. Direct construction from either an impostor record or the genuine record is refused; the genuine `issue_authority()` route remains the only supported issuance path.
- `issue_authority()` checks the presented record against the independently held pinned digest before supplying the token.
- `capability_is_issued()` verifies capability type, token identity and pinned digest.
- The ledger checks the capability at construction and again at the point of minting, so replacing its capability after construction does not preserve minting authority.
- Discrepancy resolution uses the same point-of-use capability verification.
- The six reported sabotage cases cover direct construction, hand-assembled capabilities, a forged capability carrying the pinned digest, post-construction capability replacement, and forged resolution attempts. The refusal paths append nothing and leave the discrepancy UNRESOLVED.

The stated boundary is accepted: importing the module-private token or using equivalent arbitrary Python object surgery is outside the declared threat model, consistent with the Stage 4 seal boundary already accepted. This is an in-process API authority mechanism, not a sandbox against arbitrary rewriting of the hosting interpreter.

## Correction 2 — discrepancy attribution link must resolve

Accepted.

- `mint_discrepancy()` now resolves the supplied digest against the verified record snapshot before appending.
- The digest must identify an event on that record whose type is exactly `ATTRIBUTION_RECORDED`.
- A nonexistent digest and digests belonging to `LOCAL_LABEL_RECORDED` or `DISCREPANCY_RECORDED` events are refused before append.
- `discrepancy_state()` applies the same check on read-back. A hand-appended discrepancy carrying a fictitious link is refused rather than returned as a valid linked discrepancy.
- The healthy linked-discrepancy control remains intact, including preservation of both positions and the original attribution.

The read-back sabotage test also establishes byte identity across the refusal: the invalid link is not repaired or rewritten as a side effect.

## Stage 6 findings accepted

- **K10 — one attribution fact:** one attribution per failure, referenced by closure, ledger and adjudication through the same event digest and class read from the record. Local mechanism labels remain local and cannot be converted into attribution classes.
- **K10 — discrepancy lifecycle:** both positions remain verbatim; authorised resolution records decision and authority; INDETERMINATE closes only the disagreement and leaves attribution untouched. The corrected authority and event-link boundaries now cover minting, resolution authority and discrepancy read-back.
- **K12 — response contracts:** the jointly pinned schema, preserved delivered instruction, checker binding and first-class causal findings are accepted within the harness.
- **G6 — report resolution:** event identity supplies the rendered tree/step location; contradictory report literals are named and preserved rather than silently corrected.
- **Historical reproductions:** T02, T07 and the four named T09 variants reproduce their recorded checker comparison values through line-faithful transcriptions before attribution. The evidence supports the stated SYSTEM attribution for those cases, with the explicit limitation that the historical driver itself was not executed; the transcriptions are not driver executions. The unqualified T09 case remains outside this stage as DR-16 territory.
- **No retroactive scoring:** T02, T07 and the named T09 variants remain NOT-SCORED. Attribution establishes a cause; it does not alter the recorded tree score.

## Register disposition

- **DR-06:** advanced on demonstration within the Stage 6 harness. The one-attribution/three-reference mechanism and explicit discrepancy path are demonstrated.
- **DR-07:** advanced on demonstration within the harness. G6 identifies the contradictory event location, and the discrepancy lifecycle preserves both restatements and the evidence used for resolution.
- **DR-19:** advanced on demonstration within the harness. The format-prescription mechanism is detected as a first-class finding and reproduced on the named cases.
- **DR-14:** re-examined; attribution established as SYSTEM on the preserved attempt-3 evidence, subject to the transcription limitation. T02 remains NOT-SCORED.
- **DR-15:** re-examined; attribution established as SYSTEM on the preserved attempt-3 evidence, subject to the transcription limitation. T07 remains NOT-SCORED.
- **DR-17:** re-examined; attribution established as SYSTEM for the four named variants, each separately, subject to the transcription limitation. Those T09 variants remain NOT-SCORED.
- **DR-16:** untouched; the unqualified T09 instance is excluded as stated.
- **DR-26 / production authority:** remains open. The in-harness authority is explicitly a TEST fixture and settles nothing about the production adjudicator.
- **Production integration:** not established. The harness does not show a live run's closure, ledger and adjudication consuming these views.

## Test evidence and limits

The reported counts are builder-run and re-run by Remmy, not independently executed by this examiner: Stage 6 **54/54**; Stage 1 **68/68**; Stage 2 **27/27**; Stage 3 **38/38**; Stage 4 **36/36**; Stage 5 **30/30**. The correction counterchecks are also reported as builder/orchestrator-run. This verdict is based on examination of the submitted source, tests, report and package history, not an independent local execution of the suites.

Stage 6 therefore clears Gate 1 for its specified harness mechanisms and evidence demonstrations. It does not certify production authority, production integration, historical driver execution, or retroactive tree scoring.

— Vane
