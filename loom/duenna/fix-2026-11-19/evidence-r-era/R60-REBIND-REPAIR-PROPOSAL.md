# R60 — REBIND REPAIR PROPOSAL (for Alex's review; NOT implementation)

Proposer: Remmy (implementer), 2026-11-10. Raised under Alex's
combined adjudication of the R60 revision (Correction B OPEN;
module-level rebinding inside the threat model; the precise
implementation is Remmy's to propose). **Nothing in this
document is authorised by its existence.** If approved, the
implementation follows in fixtures-r60rev/ as harness v2.3.

## The defect, restated

`CheckerContract.__init__` reads the module global
`PROCEDURE_REGISTRY` at construction time. Any importer can
rebind that module attribute before construction
(`harness.PROCEDURE_REGISTRY = {name: substitute}`), after which
construction dispatches to the substitute. `validate_verdict`
compares the verdict against the same contract's bound callable,
so contract and validation agree with the compromised source:
there is no independent trust anchor.

## Proposed mechanism — two parts, both needed

**1. Dispatch from a captured reference, not the module global.**
The one true registry (a MappingProxyType over its single
entry) is created inside a factory scope and held in a closure.
`CheckerContract` is produced by that factory; construction
dispatches through the closure cell. The module-level name
`PROCEDURE_REGISTRY` may remain as a read-only display copy, but
nothing in the dispatch path reads it — rebinding it changes
nothing. (In Python terms: attribute assignment on the module
cannot reach a closure variable.)

**2. Validation against a pinned anchor, not the contract.**
At the same definition point, the canonical procedure's source
hash is computed once and pinned inside the protected scope.
`validate_verdict` accepts a verdict only if its
implementation_hash EQUALS the pinned hash for the claimed
identity. If a substitute ran — however it got dispatched — its
source hash differs and validation rejects the verdict. Trust no
longer comes from the contract agreeing with itself; it comes
from comparison against an anchor fixed before any contract
exists.

## New fixture — FX-R60i

Rebinding sabotage, end-to-end:
- Rebind `harness.PROCEDURE_REGISTRY` to a substitute registry
  whose callable returns the expected digest unconditionally.
- Construct a contract under the recognised identity.
- Run a TAMPERED artefact.
- Expected: the verdict is the failure path (the true procedure
  ran), and any "preserved" verdict under that identity fails
  validation against the pinned anchor.
- Sabotage-of-the-fixture: restoring the old dispatch (module
  global read + self-referential validation) must make FX-R60i
  FAIL while the rest of the suite stays green.

## Suite and evidence on implementation

- Complete suite re-run: 34 existing fixtures + FX-R60i = 35,
  all PASS expected; all 31 original identities preserved;
  FX-R60f/g/h unchanged in behaviour.
- Sabotage evidence: (a) mutable-dict variant still fails
  FX-R60h alone; (b) rebind variant passes the suite ONLY in the
  sense that FX-R60i detects it — i.e. under the rebind, no
  accepted false verdict is producible; (c) removing the pinned
  anchor (self-referential validation restored) fails FX-R60i.
- Change record + updated hashes returned for independent
  examination, as before.

## Threat-model boundary, stated plainly

This repair covers rebinding and substitution through ordinary
module-level attribute assignment — the demonstrated bypass.
It does NOT claim resistance to an actor who rewrites the
module's own functions or reaches into closure cells directly
(`__closure__` surgery, monkeypatching `validate_verdict`
itself): Alex's adjudication already excludes unrestricted
internal access from the claim. The proposal also changes the
harness's structure (a factory), which the examiners should
weigh: it is the smallest structural change that gives dispatch
a captured reference; a class-level private registry was
considered and rejected because class attributes are equally
rebindable through the class object.

## Preserved, untouched

Correction A (closed PASS); R47/R65; the four gaps; UX-1…5;
`pinned=True` qualification; specification text; v0.8 immutable;
v0.10 NOT APPROVED until the gate completes.
