# EXON — DUENNA ARCHITECTURE, Plain-Language Translation Draft 01

**Provenance:** Produced by Alex at the owner's direct
commission (2026-11-16) — the first translation of an
official shelf document under the EXON programme — and
pasted into main chat by the owner. As received, the
title reads "AXON": the owner's autocorrect (his note,
2026-11-16 01:42 MST — "My autocorrect keeps calling it
axon lol"). The intended name is EXON. The body below is
the received text verbatim (rendered-text capture).

**Verification:** Compared claim by claim against the
source, record/DUENNA-STEP6-ARCHITECTURE.md, before
filing: the four components and their boundaries, the
F5 governance/enforcement statement, the dependency
chain, all five consolidations with their conditions,
Pair 6 excluded / H-7 standalone / J-1 untouched, the
48-to-43 proposed count, C-3 unsplit, all six carried
unresolved matters, and the non-authorisation of
implementation — all faithful. The plain rendering omits
the F1-F6 discharge labels and fixture names; per its
own status line it is a translation proposal only and
the original remains authoritative.

---

### AXON — DUENNA ARCHITECTURE

Draft 01 · Plain-language translation of the agreed Step 6 document

### 1\. The four parts

### RECORD — Keeps the history

* Keeps original information unchanged.

* Gives each item a stable identity.

* Keeps a digest so changes can be detected.

* Adds new information instead of silently rewriting old information.

* Can record failed or missing bindings.

* Does not depend on BINDER.

The original record must never be silently changed.

### BINDER — Connects rules to approved contracts

* Takes authored rules and connects them to a specific approved contract.

* Performs this connection mechanically.

* Has no discretion when binding.

* Sends its results only to RECORD.

* Records either a successful binding or an explicit failure.

If no binding exists, that does not mean binding succeeded.

### EVALUATOR — Works out states and tracks obligations

EVALUATOR has two separate responsibilities:

* Work out lifecycle states using evidence.

* Account for every obligation as satisfied, blocked, unmet or indeterminate.

Both responsibilities use the same component, but each has its own tests. Passing one does not mean the other has passed.

EVALUATOR can add evaluation results, defect decisions and LINK entries to RECORD.

It cannot rewrite history. RECORD owns the preservation rules; EVALUATOR follows them.

LINK equivalence remains UNPROVEN until its required tests pass.

### EXAMINER SURFACE — Independently checks the work

* Starts with the original information preserved in RECORD.

* Uses the applicable pinned contract.

* Uses the defined reproduction rules.

* Independently works out the result.

* Does not rely on EVALUATOR's conclusions.

Additional report information must come through its specified evidence path. It cannot be guessed from EVALUATOR's conclusions.

No component is allowed to grade its own work.

### 2\. Authority and enforcement

F5 is not another component. It consists of two kinds of control operating across all four components.

Governance: Ben supplies the authority. Authority comes from outside the components.

Enforcement: Mechanical checks compare actions against approved, pinned documents at the required points.

No component creates its own permission.

A gate checks whether required evidence has been received. The approved contract defines what happens next. The machinery applies that consequence.

### 3\. How the parts depend on each other

* RECORD needs nothing else.

* BINDER needs RECORD.

* EVALUATOR needs RECORD and reads BINDER's results through it.

* EXAMINER needs RECORD, the pinned contract and the reproduction rules. It does not depend on EVALUATOR.

* Governance and enforcement apply across all four.

The key dependency: Remove BINDER and the system can still keep records. Remove RECORD and the other components have nothing reliable to work from.

### 4\. The five agreed consolidations

Five groups of requirements are combined, subject to these conditions:

* B-5 joins D-1. The surviving test must inspect EVALUATOR's output.

* D-5 joins D-3. Machinery defects must be labelled as computation-layer defects and must not receive an F4 disposition.

* D-6 joins D-3. Its recovery wording must be copied exactly into G-2/F-1 attempt material. The dual-pointer tombstone remains.

* D-2 is split as corrected in Step 5. B-2 receives only the agent-declared-state clause. D-3 keeps the machinery-defect, voiding and re-derivation consequences. Tests must identify which part owns each assertion.

* J-2 joins A-2, including its omission test.

Pair 6 remains excluded. H-7 stays separate. J-1 remains unchanged.

The proposal reduces the requirement count from 48 to 43. This is a proposed count, not a claim that implementation has happened.

C-3 remains one requirement. Its machinery is distributed across RECORD, EVALUATOR and EXAMINER SURFACE without splitting the requirement itself.

### 5\. Unresolved matters

The architecture carries these matters forward without pretending they have been solved:

* Stream-entry correction: A design obligation for Step 7.

* Checker-verdict correction: A design obligation for Step 7.

* Discharge-record supersession: An unresolved specification decision, not a design obligation.

* LINK equivalence: Not proven until the named tests pass.

* Identity taxonomy: Still provisional. Each kind needs a distinct failure case.

* CANON-1 excluded paths and Family E schema: Still unresolved and untouched.

These matters must remain visible. They cannot disappear through assumed inheritance or an invented implementation.

### 6\. The next step

The next step is to prepare one implementation plan containing:

* Stages.

* Dependencies.

* Acceptance criteria.

The plan must follow this architecture. It must not invent solutions for the unresolved matters.

Agreement on the architecture does not automatically authorise implementation or adoption of later changes.

Source: [DUENNA — STEP 6: THE SMALLEST VIABLE ARCHITECTURE](https://github.com/Q420/ainternet-shelf/blob/main/record/DUENNA-STEP6-ARCHITECTURE.md?utm_source=chatgpt.com)

Status: Translation proposal only. The original remains authoritative.
