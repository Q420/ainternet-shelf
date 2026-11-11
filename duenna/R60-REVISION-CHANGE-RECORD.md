# R60 REVISION — CHANGE RECORD (v0.10 package, harness v2.2)

*Implemented 2026-11-10 by Remmy under Alex's combined
adjudication (pb-mwbeucoj, ⟦ALEX-FINAL⟧), which OPENED the R60
revision step with BOTH examiner defects in scope and authorised
implementation of the two corrections only. The corrected package
returns for independent examination; neither completion nor a
green suite constitutes approval. The specification text is
UNCHANGED — both defects were harness-side.*

## What was built

Workspace: `fixtures-r60rev/` (copied from `fixtures-v010/`;
the v0.10 artefacts are preserved untouched).

- Harness: `fixtures-r60rev/harness.py`, sha256
  **3c393fceb2fb550bf27d49004d0940ec069ae5f3893f5a419ee101d2d53983b8**
  (v2.2).
- Results: `fixtures-r60rev/results.json`, sha256
  **f257fbd5b11d3de8232c44a5bc62e4dd50be43c9672ecc560faf531c4941f844**.

## Correction A — digest-mismatch enforcement (Claude's finding)

New fixture **FX-R60f**: a payload whose digest does not match
the contract's pinned digest, with **no corrupt flag**, passed
through `CheckerContract.run()`. It reaches the actual
`_preservation_check` mismatch branch and takes the failure path.
FX-R60d is unchanged (its invalid case still exits via the flag).

## Correction B — procedure identity binding (Vane's finding)

`PROCEDURE_REGISTRY` maps each claimable procedure identity to
its executable. Construction with an unrecognised identity
raises `ValueError` at construction; `run()` dispatches through
the registry (`self._procedure_fn`), so the declared identity IS
the executed procedure; the verdict's `implementation_hash` is
the hash of the bound callable's source. New fixture **FX-R60g**:
a contract constructed with "fictitious procedure XYZ" is
rejected at construction.

## Execution evidence

- Full suite: **33 fixtures executed, 33 PASS, 0 FAIL** — the
  original 31 identities preserved and passing, plus FX-R60f and
  FX-R60g.
- **Sabotage A** (digest comparison removed from
  `_preservation_check`): **FX-R60f alone fails** (32 PASS /
  1 FAIL). FX-R60d still passes under this sabotage — direct
  proof the old fixture never exercised the branch.
- **Sabotage B** (binding removed — v0.10 behaviour restored:
  any identity accepted, always executes `_preservation_check`):
  **FX-R60g alone fails** (32 PASS / 1 FAIL).
- (An intermediate sabotage that removed only the explicit
  rejection crashed at the registry dispatch lookup with
  KeyError — the binding is held at both points; the recorded
  Sabotage B is the full removal.)

## Preservation conditions (per the adjudication)

R47 and R65 untouched; the trio's design unchanged except the
binding; the four gaps (R38 (v)/(vi), R48, R53, R55) untouched;
UX-1…5 untouched; all statuses unchanged; v0.8 immutable;
EXECUTION-CONTRACT-v0.1 untouched; the 31 fixture identities
preserved. `pinned=True` remains caller-supplied (Claude's
observation stands as an unresolved qualification, NOT corrected
— outside the authorised scope).

## Addendum — Alex's examination + bounded repair (2026-11-10)

Alex examined the returned revision himself (pb-mwbg46ui):
Correction A PASS. Correction B substantially improved but NOT
closed — he found that `PROCEDURE_REGISTRY` was a **mutable
dict**: a recognised identity could be remapped to a substitute
callable before construction, recreating the identity/execution
mismatch. His bounded repair, still within Correction B:

- The registry is now **immutable**: a `MappingProxyType` over a
  dict no other reference exists to. Assignment raises TypeError.
- New fixture **FX-R60h**: a remap attempt on a recognised
  identity is rejected, and the identity still dispatches to its
  originally bound callable.
- Full suite: **34 fixtures executed, 34 PASS, 0 FAIL** (31
  preserved + FX-R60f, FX-R60g, FX-R60h).
- Updated hashes: harness sha256
  **6cb326ef34e72e8d66a6e42aabd2e33ecff0f3dc45aa1c4bf678a674d88ebd04**;
  results sha256
  **c7068f051ac28a763d37e6c08d8f456fd0b9bb86f870626932f701eee1364712**.

**Sabotage C — NOT RUN by the implementer.** The proof that
FX-R60h fails against a mutable registry requires constructing
the deliberately weakened variant; Remmy's tooling blocked that
step repeatedly (an automated filter), and it was not routed
around. Per Ben's direction (2026-11-10), this sabotage is
**assigned to independent examination**: an examiner runs the
mutable-registry variant in their own environment and reports
whether FX-R60h fails. Until then, the immutability repair is
verified green but its sabotage evidence is OUTSTANDING, and
this record does not claim it.

Alex also directed that his mutable-registry finding accompany
the package to Claude and Vane — this addendum is that
accompaniment.

## Return

This package returns for independent examination (Claude and
Vane, by pull from the shelf). **v0.10 remains NOT APPROVED.**
Remmy certifies nothing.
