# ALEX DESIGN REVIEW — STAYTRUE AS A LIVING TETHER (2026-11-17)

Provenance: issued by Alex in the "Confirm Correction Order (4)" ChatGPT
conversation, in reply to the orchestrator's design letter of 2026-11-17
(Staytrue scope-tether rulings) as corrected by the owner's fork ruling
("it's an evolving file it stays and changes per scope per project").
This revised review supersedes Alex's initial reply to the uncorrected
letter. Received via the seat capture (events spool), transport class
[reported]. Filed verbatim below. No build is authorised by the review;
the edition lifecycle and history mechanism require specification and
owner approval before implementation.

---

Duenna design review — Staytrue as a living tether
Owner's fork ruling accepted

The correction changes the design in one important way: Staytrue is one persistent, evolving artefact, not a collection of scope-specific documents.

Ben's ruling is clear:

"it's an evolving file it stays and changes per scope per project."

I accept that shape. The architecture should preserve one canonical Staytrue.md, while making every approved edition immutable and historically recoverable.

The file evolves. Its history does not get rewritten.

1. What an edition change means

An edition change is a controlled amendment to the standing tether.

It is not simply someone editing a Markdown file. It changes the recorded statement of the owner's settled intent and therefore needs an identifiable authority event.

I propose this lifecycle:

Change proposed: a worker identifies that the current tether no longer represents the scope or that a new scope requires an update.

Change prepared: an authorised author drafts the new edition.

Owner approval: Ben approves the changed intent, or an explicitly recorded delegate approves within the exact scope of their delegation.

Edition committed: the approved content receives a new immutable edition identity and digest.

Current edition advanced: the canonical Staytrue.md points to the newly approved edition.

History preserved: the previous edition and its change record remain retrievable.

Who may change it?

I recommend separating authorship from approval:

Activity

	

Authority




Identify need for change

	

Any worker




Prepare proposed amendment

	

Authorised worker or technical lead




Clarify or restructure wording

	

Author, without changing intent




Approve changed intent

	

Ben, or an explicitly delegated authority within recorded scope




Publish approved edition

	

Designated repository/publishing mechanism




Bind an edition to a run

	

Harness, mechanically

This follows the existing Duenna governance distinction between authoring, approval and binding. A worker may prepare a change, but cannot turn their interpretation into the owner's intent by publishing it.

Important: a new project or scope does not automatically authorise an amendment. It creates a reason to examine whether the tether needs changing.

2. How a worker identifies the edition checked

The worker must never merely say, "I checked Staytrue.md."

That statement is insufficient because the file can change.

Each edition should have:

A stable item identity: DUENNA-STAYTRUE

A monotonically advancing edition number

A full content digest

An approval reference

An effective scope or project reference

A predecessor edition reference

For example, illustratively:

Plain text
Item:       DUENNA-STAYTRUE
Edition:    STAYTRUE-E0007
Scope:      STAGE6-BATTERY
Approval:   OWNER-DECISION-REF
Digest:     <full SHA-256>
Supersedes: STAYTRUE-E0006

A worker's run binding then records:

Plain text
staytrue_item_id
staytrue_edition_id
staytrue_content_digest
staytrue_approval_ref

The worker checks the exact edition bound to the run.

If the canonical file advances during that run, the existing binding does not silently advance with it. The run continues under its original pinned edition unless an authorised change process explicitly stops and rebinds it.

This is consistent with the existing Execution Contract's requirement to record exact versions used in immutable run configuration.

3. How the living file keeps its history

I recommend two representations, but only one standing file.

Canonical living file

Current approved edition
Staytrue.md

Contains the currently operative intent, scope context, boundaries and acceptance conditions.

Immutable edition history

E0005 — Previous project

Preserved content, digest and approval record.

E0006 — Stage 6 preparation

Preserved content, digest and approval record.

E0007 — Stage 6 battery

Current

New approved content and change record.

Each edition should have a corresponding change record containing:

Record

	

Purpose




Previous edition

	

Establishes exactly what changed from




New edition

	

Establishes the new content




Content digests

	

Establish integrity




Change reason

	

Explains why the amendment was needed




Scope/project reference

	

Establishes where it applies




Proposed by

	

Identifies the author




Approved by

	

Identifies the authority




Approval evidence

	

Links to the actual owner decision




Effective point

	

Establishes when the new edition becomes operative




Change summary

	

Makes the difference understandable

The complete old content must remain available. A summary or diff alone is not sufficient historical evidence.

This follows the Approved Pool identity design: stable item identity, immutable version identity, full digest retention, and a current-head reference. The Approved Pool documents also make clear that the ledger mechanism itself must not be assumed to exist merely because it has been designed. Until an authoritative ledger is operational, the Shelf's pinned commits and blob digests can provide the version evidence.

4. How it handles changing scopes

There is one subtle design requirement here.

Because Staytrue is a standing file, it must distinguish the persistent principles from the currently operative project scope.

I recommend three content areas:

Standing fidelity rules: principles that remain applicable across projects unless the owner changes them.

Current scope and project: the active owner's intent, boundaries, deliverables and acceptance conditions.

Transition record: the reference to the previous edition and the reason the tether changed.

The transition record is not a substitute for edition history. It makes the evolution understandable from inside the current file.

When a project ends and another begins, the new edition replaces the active scope section. It does not erase the previous project's history or imply that its old scope remains active.

A worker must check both the current edition and its applicability to the run. A correctly pinned edition used against the wrong project is still a scope failure.

5. What happens when the tether changes during work?

This needs a straightforward rule:

A changed tether cannot silently alter an already-bound run.

For example:

Run A binds to E0006.

Ben approves E0007 while Run A is still active.

Run A remains bound to E0006.

New Run B binds to E0007.

If E0007 makes Run A's continued work incompatible with the owner's newly settled intent, that conflict must be surfaced and the run stopped or explicitly re-authorised. The system must not pretend the old binding somehow became current.

This preserves the distinction between historical correctness and present authority.

6. Revised architectural disposition

Decision

	

Disposition




One standing Staytrue.md

	

Owner ruled




File evolves across scopes and projects

	

Owner ruled




Immutable editions behind the living file

	

Recommend




Owner approval for changes to settled intent

	

Recommend, consistent with governance




Explicit delegation permitted within recorded scope

	

Recommend




Edition ID and full digest in run binding

	

Recommend




Append-only change history

	

Recommend




Old runs retain their original edition

	

Recommend




Mindkeep excluded from Duenna

	

Owner ruled




Per-scope separate tether documents

	

Rejected by owner's correction

Final design principle

Staytrue is the persistent record of what the owner means the work to remain faithful to as the work evolves.

It must be able to change without losing what it used to say, and it must be possible to establish exactly which edition governed any particular action.

That gives Duenna something stronger than a document workers are asked to remember to read: a versioned scope tether that can be checked, bound, challenged and audited.

No build is authorised. This is the revised design recommendation for the owner's standing-file ruling. The proposed edition lifecycle and history mechanism still require specification and approval before implementation.

⟦ALEX-FINAL⟧
