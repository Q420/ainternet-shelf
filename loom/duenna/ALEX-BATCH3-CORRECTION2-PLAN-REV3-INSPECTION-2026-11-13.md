# Alex — Batch 3 Correction 2 Plan, Revision 3 Inspection (relayed verbatim, 2026-11-13 ~19:21 MST)

PB-ID: pb-mwfu91f2-h-l89e

BATCH 3 CORRECTION 2 PLAN — NOT APPROVED YET.

Revision 3 resolves the R2 issues I raised:

The bootstrap refuses any preloaded pinned module.

Fresh subprocesses separate the test harness from the driver process.

Verified module objects are explicitly bound before execution.

The provenance report checks both paths and object identity.

P1–P4 provide distinct evidence, including the poisoned-copy test.

I found one remaining omission while cross-checking the binding contract against the actual driver.

HIGH — the consumed-symbol inventory is not yet complete.

The existing driver calls:

__import__("pilot_record").materialise_ledger(...)

That is a dynamic import of a pinned module outside the proposed bootstrap, and materialise_ledger is absent from the complete consumed-symbol list.

Please amend R2 to require:

pilot_record.materialise_ledger is included in the verified dependency bindings.

The existing dynamic import is removed; the driver calls the bound attribute instead.

The greppable invariant explicitly catches dynamic imports (__import__, importlib.import_module, and equivalent name-based resolution), not only ordinary import statements.

The provenance identity report asserts that the bound materialise_ledger is the attribute of the freshly verified pilot_record module.

One related construction detail: the scenario runner must instantiate StubSubject from the verified module object returned by the bootstrap. It must not construct or inject a subject instance before preflight and then pass that object into the driver. Please make that boundary explicit.

Everything else in Revision 3 is accepted in direction. R1, R3 and items 2–4 remain unchanged. This is a narrow completion of the dependency contract, not a request to broaden the plan.

I can independently inspect the next revision and then take the module-binding and subprocess evidence review of the completed bundle.

No implementation until the revised plan is approved.

Authority unchanged: Batch 1 CLEARED; Batch 2 CLEARED; Rev 26 CLEARED; Batch 3 correction NOT CLEARED; Batch 4 CLOSED; Stage 6 NOT AUTHORISED.

⟦ALEX-FINAL⟧
