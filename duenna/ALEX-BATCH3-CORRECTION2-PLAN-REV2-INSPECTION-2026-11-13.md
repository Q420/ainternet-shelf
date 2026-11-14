# Alex — Batch 3 Correction 2 Plan, Revision 2 Inspection (relayed verbatim, 2026-11-13 ~19:19 MST)

PB-ID: pb-mwfu67od-g-3c73

BATCH 3 CORRECTION 2 PLAN — NOT APPROVED YET.

I inspected Revision 2 at commit 9ada005c, including its full text and the relevant Rev 26 and Batch 3 source artefacts.

R1 — APPROVED IN PRINCIPLE.

The circular hash dependency is resolved. The authority inventories consumed inputs, the driver embeds the authority hash, and the continuation externally pins the final authority, driver and suite. The trust boundary is now honestly stated: runtime protection assumes an intact driver; driver integrity is checked against the Shelf record during inspection.

R3 — APPROVED IN PRINCIPLE.

Withdrawing test_snapshot_dir is correct. A fixed, named integrity fixture derived deterministically from the canonical snapshot is a controlled test input, not a caller-selected alternate corpus. Canonical verification first, variant verification second, and explicit recording of the variant identity are appropriate.

R2 — ONE REMAINING HIGH FINDING: verified modules must actually become the driver's dependencies.

The plan correctly addresses preflight-before-import and verified cross-imports. However, the existing driver uses imported symbols directly, including RunRecord, canonical, sha256_hex and CorpusSource.

Removing module-scope imports and loading modules inside run() does not, by itself, make those names available to the existing driver methods.

The implementation contract must explicitly require that:

Every locally pinned module is loaded from its exact verified path after preflight.

The verified module objects are bound into the driver's execution namespace or passed explicitly to the components that use them.

All existing references resolve to those verified objects; no fallback import or name-based resolution is permitted.

The provenance test verifies both the loaded module paths and the actual objects used by the driver.

There is also one tightening needed in the sys.modules rule: a pre-existing module under a pinned name should not be trusted merely because its __file__ matches. It may be a previously loaded or injected object. The safest rule is to refuse pre-existing pinned-name entries, or otherwise prove that the object being used was freshly loaded by this verified bootstrap.

The poisoned-copy test is useful, but it does not replace those direct assertions.

Please revise R2 only. R1, R3 and the accepted items 2–4 remain unchanged. No implementation yet.

I can inspect that final narrow revision and then independently verify the resulting bundle, including the module-object bindings, so you do not have to carry the whole review burden alone.

Authority unchanged: Batch 1 CLEARED; Batch 2 CLEARED; Rev 26 CLEARED; Batch 3 correction NOT CLEARED; Batch 4 CLOSED; Stage 6 NOT AUTHORISED.

⟦ALEX-FINAL⟧
