# STAYTRUE — PER-PROJECT EDITION LIFECYCLE AND HISTORY SPECIFICATION 02 (DRAFT)

**Status:** DRAFT FOR BEN APPROVAL  
**Prepared by:** Alex  
**Date:** 2026-11-17  
**Scope:** Per-project Staytrue identity, edition lifecycle, authority records, run binding, interim Shelf evidence, and deterministic harness checks.  
**Authority:** Ben's owner ruling of 2026-11-17 and Remmy's review at `f7475a71`.  
**Implementation status:** DESIGN ONLY. No implementation, live tether, authority registry, or execution is authorised by this specification.  
**Review basis:** Remmy review findings F1–F5 and minor binding-derivation finding.  
**Approval gate:** Ben approves this revised specification before any implementation.

## 1. Purpose and governing decisions

This specification defines the lifecycle and history mechanism for **one Staytrue sheet per project**. A new project receives its own Staytrue item, canonical file, edition chain, current head, event history, and immutable run bindings. That sheet evolves as that project's scope changes. A Staytrue item is never shared by two projects.

The following are fixed design inputs:

1. Every project has exactly one logically distinct Staytrue item, with a stable project-bound item ID.
2. Each item's approved editions are immutable and historically recoverable.
3. Changes to settled intent require Ben's approval, or approval by a delegate under an explicit, recorded, scope-bounded delegation.
4. Every run binding records the exact edition ID, full content digest, and bound head commit.
5. Edition history is append-only; complete prior content is retained.
6. A bound run retains its pinned edition. A later edition never silently rewrites an existing binding.
7. Until a dedicated authoritative ledger is approved and implemented, pinned Shelf commits and blob/content digests provide interim version evidence.
8. Mindkeep is outside Duenna and is not part of this mechanism.
9. Every edition carries an owner-set `improvise` flag with value `YES` or `NO`. It controls whether a worker may propose a workaround after task failure; it never grants execution authority.
10. Project identity is structural: a run can resolve only the Staytrue item assigned to its exact project ID. Cross-project applicability is not a fallback or a semantic check.

The file's words express intent. The harness does not interpret those words to decide what Ben meant. It performs the deterministic checks specified here and stops where authority or semantic judgement is required.

## 2. Terms

- **Project ID:** the stable, unique identifier assigned to one project.
- **Staytrue item:** that project's one persistent governance artefact, with item ID `STAYTRUE-<PROJECT-ID>`. The project ID must follow the configured stable-ID grammar and may not be reused for another project.
- **Edition:** one complete, immutable snapshot of the project's standing file and machine-readable metadata.
- **Canonical file:** the current `Staytrue.md` for that project, byte-identical to the currently approved edition snapshot.
- **Edition snapshot:** immutable archived copy of a complete edition.
- **Change record:** immutable submitted snapshot describing one proposed edition transition.
- **Current head:** the one edition currently designated CURRENT for that project-specific item.
- **Run binding:** immutable record pinning the edition and head commit actually used by a run.
- **Applicability:** explicit scope identifiers declared in an edition's machine-readable metadata. Project identity is established by the item ID and project directory; scope applicability is exact identifier matching within that project.
- **Delegation:** a recorded, bounded grant from Ben authorising a named delegate to perform a specified approval act within specified scope and conditions.
- **Improvise flag:** the edition-pinned owner setting `YES` or `NO` governing whether a workaround proposal may be submitted after a task failure.

Identity, integrity, authority, applicability and meaning are separate:
- an item ID identifies the project-specific governance item;
- an edition ID identifies an edition within that item's chain;
- a digest checks bytes;
- an approval record establishes authority;
- scope identifiers establish declared applicability;
- none of these proves that the text is a faithful expression of intent. That last question belongs to the approving authority.

## 3. Shelf file structure

The following paths are normative. Replace `<project_id>` with the exact stable project ID; it is a path-safe identifier, not a display name.

```text
duenna/
  staytrue/
    projects/
      <project_id>/
        Staytrue.md
        HEAD.yaml
        events/
          STAYTRUE-EVENT-<unique-id>.yaml
        editions/
          STAYTRUE-E0001.md
          STAYTRUE-E0002.md
          ...
        changes/
          STAYTRUE-CHANGE-0001.yaml
          STAYTRUE-CHANGE-0002.yaml
          ...
        evidence/
          STAYTRUE-E0001-EVIDENCE.yaml
          STAYTRUE-E0002-EVIDENCE.yaml
          ...
        delegations/
          STAYTRUE-DELEGATION-<unique-id>.yaml
```

For project `<project_id>`, the item ID is exactly `STAYTRUE-<project_id>`; every edition, event, change record, evidence manifest, head pointer, and delegation record carries that item ID. The directory and item ID are assigned once and never repurposed.

- Each project's `Staytrue.md` is the sole standing/current file for that project.
- `editions/` contains the complete byte-preserved snapshot of every edition that reached APPROVED.
- `changes/` contains one immutable submitted snapshot per proposed transition, including rejected and withdrawn proposals.
- `evidence/` contains detached edition evidence manifests, including full digests and Shelf pins.
- `events/` contains immutable lifecycle and authority events.
- `HEAD.yaml` is the one current-head pointer for that project's item.
- `delegations/` contains immutable authority grants and subsequent revocation events/records.
- No history file is overwritten. Only that project's canonical `Staytrue.md` and `HEAD.yaml` intentionally move; their Git history is retained.

A project cannot point to another project's Staytrue directory, item ID, head, edition or history. A new project starts a new item and edition chain; it does not inherit another project's current head or approval. A future implementation may use a different physical layout only through an approved specification amendment preserving these identity, immutability and retrieval properties.

## 4. Standing-file content structure

Every edition contains these three top-level sections in this order:

### 4.1 Standing rules

Rules intended to persist across projects and scopes. They remain operative unless changed by an approved edition. Each rule should have a stable rule ID within the file to make changes traceable. The harness may check IDs and schema, but it must not infer a rule's meaning.

### 4.2 Edition control settings

Each edition contains an explicit owner-set `improvise` field in its machine-readable header, with exactly one allowed value: `YES` or `NO`. The setting is edition-wide and applies to every scope entry in that project's edition.

The owner sets or approves the value as part of approving the complete edition. A worker may propose a value change in a candidate edition but cannot change the effective flag by editing the canonical file or a run record.

**Default:** if the field is absent, malformed, duplicated, or not exactly `YES` or `NO`, the effective value is `NO` and the harness records `IMPROVISE_FLAG_DEFAULTED_NO` or `IMPROVISE_FLAG_INVALID_DEFAULTED_NO`. This default grants no latitude by assumption. The edition remains subject to all other validity checks; a malformed flag is reported and corrected only through a properly approved edition.

### 4.3 Current scope

One or more explicit active scope entries. Each entry must identify:
- project ID;
- scope ID;
- scope approval reference;
- current intent statement;
- in-scope work;
- out-of-scope work;
- constraints and exclusions;
- acceptance conditions;
- required evidence;
- dependencies or prerequisite references, if any;
- scope state: ACTIVE or CLOSED.

Multiple active entries are permitted in the single file if the owner has approved them. A run must match one explicit project/scope entry; it may not infer applicability from similar names or prose. A scope not listed as ACTIVE is not made active by the existence of the file.

### 4.4 Transition record

A concise in-file record identifying:
- the immediately preceding edition;
- the change-record ID for this edition;
- the project/scope transition represented;
- the reason for the change;
- the approval reference;
- the effective event/reference.

This is an orientation aid, not the authoritative history ledger. The immutable change record and Shelf evidence are authoritative for the transition's provenance.

## 5. Edition header and identity

Each edition begins with a machine-readable header. The header is part of the immutable edition snapshot.

Required fields:

| Field | Requirement |
|---|---|
| `schema_version` | Header/schema version |
| `item_id` | Exact project-bound ID `STAYTRUE-<project_id>` |
| `project_id` | One exact stable project ID; must match the item ID and containing project directory |
| `edition_id` | Unique monotonic ID within this item's chain, e.g. `STAYTRUE-E0008` |
| `predecessor_edition_id` | Immediately preceding CURRENT edition; null only for initial edition |
| `change_record_id` | Unique ID of the transition record within this item |
| `created_by` | Authenticated author identity |
| `created_at` | UTC timestamp; informational, not ordering authority |
| `project_ids` | Exactly the singleton list containing this edition's `project_id` |
| `scope_ids` | Exact set of every scope-entry ID in this edition, including ACTIVE and CLOSED entries |
| `scope_approval_refs` | Exact set of owner-approved scope decision references represented by the scope entries |
| `approval_ref` | Exact approval event/reference for this edition |
| `effective_event_ref` | Event at which the edition became CURRENT |
| `canonicalisation_id` | Exact digest procedure identifier, initially `STAYTRUE-BYTES-UTF8-LF-v1` |
| `improvise` | Owner-set enum: `YES` or `NO`; absent/invalid defaults to effective `NO` |

The header's `project_ids`, `scope_ids`, and `scope_approval_refs` are redundant integrity indexes, not independent sources of applicability. They must exactly equal the values derived from all declared scope entries (including CLOSED entries). The project list must contain exactly one project ID. Missing, duplicate, extra or omitted values, or disagreement with the scope entries, returns `APPLICABILITY_AMBIGUOUS` and stops. The scope entries are the source records; the header lists must agree exactly.

The full content digest is stored in the detached evidence manifest, not self-embedded in the bytes it hashes. This avoids a self-referential digest. The manifest binds the digest to the item ID, edition ID, exact archived path, and Shelf commit/blob pins.

Edition IDs are never reused within an item. The numeric suffix advances by one from the last allocated edition ID; gaps are permitted only where the change history explains them. Timestamps do not determine edition order.

## 6. Change-record format

Each proposed transition receives a unique immutable change record at:

`duenna/staytrue/projects/<project_id>/changes/<change_record_id>.yaml`

The change record is a **submitted snapshot**, not a mutable lifecycle object. Its complete bytes are fixed when the candidate is submitted and are never edited to fill later decisions or publication pins.

Required immutable submitted-snapshot fields:

```yaml
schema_version: "STAYTRUE-CHANGE-2"
item_id: "STAYTRUE-<project_id>"
project_id: "<exact-project-id>"
change_record_id: "STAYTRUE-CHANGE-0008"
from_edition_id: "STAYTRUE-E0007"
candidate_edition_id: "STAYTRUE-E0008"
candidate_snapshot_path: "duenna/staytrue/projects/<project_id>/proposals/STAYTRUE-E0008.md"
candidate_content_sha256: "<full SHA-256>"
change_reason: "<why an edition change is proposed>"
change_summary: "<descriptive summary; not authority>"
affected_scope_ids: ["<scope-id>"]
improvise_change:
  previous_value: "NO"
  proposed_value: "YES"
changed_sections:
  - section_id: "<stable-rule-or-scope-entry-id>"
    change_type: "ADD | MODIFY | CLOSE | REMOVE"
    rationale: "<explanation>"
proposed_by: "<authenticated-principal>"
prepared_by: "<authenticated-principal>"
submitted_at: "<UTC timestamp>"
submission_event_ref: "<immutable SUBMITTED event ID>"
supersedes_change_record_id: null
```

The candidate snapshot path and digest bind the exact bytes submitted for approval. The submitted record does not contain mutable `change_state`, approval decision, approver, delegation result, effective event, publication commit, or final edition blob fields. Those facts exist only in immutable lifecycle events and the detached approved-edition evidence manifest.

Rules:
- Submission creates and pins the immutable change-record snapshot and exact candidate bytes. Later decisions never alter either.
- Approval/rejection/withdrawal, delegation-use consumption, publication, and supersession are represented only by new immutable events in the item's event chain.
- Publication pins (approved edition path, commit, blob ID and full digest) live in the edition evidence manifest and CURRENT/publication event, not by editing the submitted change record.
- A correction or amended candidate requires a new change-record ID and new submitted snapshot linked to the superseded proposal; it never replaces the original.
- The change summary and section diff are explanatory only. The complete candidate and approved edition bytes are retained.
- A change record cannot approve itself and does not become an edition merely because it has an allocated ID.

## 7. Lifecycle states and authority

### 7.1 States

The edition/change lifecycle uses these states:

1. **DRAFT** — candidate is being prepared; not submitted for approval.
2. **SUBMITTED** — candidate and change record are complete and awaiting an authorised approval decision.
3. **APPROVED** — the owner or valid delegate has approved the candidate content and declared scope.
4. **CURRENT** — the approved edition has passed deterministic integrity/authority checks and has been atomically advanced as the current head.
5. **SUPERSEDED** — a later edition has become CURRENT; this edition remains immutable and valid for historical bindings.
6. **REJECTED** — the approving authority declined the submitted candidate.
7. **WITHDRAWN** — proposer withdrew the candidate before approval, or the approving authority formally withdrew an approval before it became CURRENT.

APPROVED is not CURRENT. A failed publication or integrity check leaves the candidate APPROVED but not CURRENT and records the failure. It must not be silently treated as active.

### 7.2 Permitted transitions

| Transition | Who may cause it | Required evidence |
|---|---|---|
| none → DRAFT | Any worker may identify/propose; an authorised author prepares the candidate | Author identity and draft record |
| DRAFT → SUBMITTED | Candidate author or authorised submitter | Complete change record and candidate snapshot |
| SUBMITTED → APPROVED | Ben, or a valid delegate acting within recorded delegation | Approval event and authority check |
| SUBMITTED → REJECTED | Ben or valid delegate | Decision record and reason |
| DRAFT/SUBMITTED → WITHDRAWN | Proposer/author before approval; after approval but before CURRENT, Ben or valid delegate | Withdrawal event |
| APPROVED → CURRENT | Harness/publisher, mechanically | All §11 checks pass; successful atomic head advance |
| CURRENT → SUPERSEDED | Harness/publisher, mechanically, only as part of a successful next-head advance | New CURRENT edition and linked transition event |

No worker, author, technical lead, examiner, harness or publisher may approve changed intent merely by virtue of their technical role. A technical lead may prepare or review a proposal; approval remains Ben's unless a valid delegation says otherwise.

A CURRENT edition is never returned to DRAFT or edited. If the owner wishes to restore old wording, that is a new edition with a new ID and approval record, not a rollback that rewrites history.

### 7.3 Delegation record

A delegation must be recorded before it is exercised, within the project's item history, at:

`duenna/staytrue/projects/<project_id>/delegations/<delegation_id>.yaml`

Required fields:

- `delegation_id` — unique immutable ID;
- `item_id` — exact project-bound Staytrue item ID;
- `delegator` — Ben's authenticated principal;
- `delegate` — exact authenticated principal permitted to act;
- `act_class` — one exact value from the enumerated set: `APPROVE_STAYTRUE_EDITION` or `APPROVE_STAYTRUE_WORKAROUND`. The latter authorises approval/rejection of a workaround proposal only; it does not imply edition-approval authority.
- `project_id` — the one exact project ID for this item;
- `scope_ids` — explicit bounded scope; no implicit global authority;
- `conditions` — any exact restrictions;
- `valid_from`, `expires_at` — validity interval;
- `use_limit` — positive integer count of permitted approvals;
- `issued_at` and `owner_decision_ref` — evidence that Ben granted it;
- `issuance_event_id` — event establishing the grant in the item's event chain.

Revocation is a new immutable `DELEGATION_REVOKED` event referencing the delegation ID. Do not edit the delegation record to add a revocation timestamp or overwrite its original state.

**Mechanical use counting and revocation rule:**

1. Validate that the delegation's issuance event is in the same verified event chain and is an ancestor of the proposed approval event.
2. Count prior successful approval events in that chain position that reference the same delegation ID, act class and item ID. Count only events whose decision is APPROVED; rejected proposals do not consume an approval use unless the delegation's own explicit conditions say otherwise.
3. The current approval consumes the next use. It is valid only when the number of prior counted uses is less than `use_limit`. Record the resulting one-based `use_number` in the approval event. Duplicate event IDs or duplicate use numbers are invalid.
4. Evaluate revocation by chain position, not wall-clock timestamp: a valid `DELEGATION_REVOKED` event that is an ancestor of the approval event invalidates the delegation. A revocation event later in the same chain does not retroactively invalidate an earlier approval. If revocation and approval are on divergent/unverifiable histories, pause with `DELEGATION_INVALID`.
5. Also validate exact delegate identity, act class, item/project/scope membership, validity interval at the approval event's recorded time, conditions, and issuance-before-approval. A missing or ambiguous event chain, expired grant, exhausted use limit, revoked grant, or out-of-scope act is invalid. No inferred authority is permitted.

The approval event must record the delegation ID, act class, `use_number`, and exact scope entry or workaround proposal approved. For `APPROVE_STAYTRUE_WORKAROUND`, it must also identify the exact run ID and proposal ID. A delegation for one project cannot approve another project's item. A delegation does not transfer or enlarge itself.

### 7.4 Lifecycle event record

Every lifecycle or authority transition is represented by a new immutable event at `duenna/staytrue/projects/<project_id>/events/<event_id>.yaml`. Required fields are:

- `event_id`, `event_type`, `item_id`, `project_id`, `edition_id` and `change_record_id`, where applicable;
- `from_state` and `to_state`, where applicable;
- `actor` and `actor_role`;
- `authority_ref`, `delegation_id`, `act_class`, and `use_number`, where applicable;
- `decision` and `decision_target_ref`, for approval/rejection events;
- `evidence_refs`;
- `occurred_at` (informational timestamp);
- `previous_event_id`, where a prior event exists;
- `shelf_commit` containing the event.

An event is append-only. Corrections are additional events that explicitly reference the event corrected; the original event remains intact. Event order and delegation status are established by the predecessor chain and pinned Git history, not timestamps alone.

### 7.5 Current-head pointer

For each project, `duenna/staytrue/projects/<project_id>/HEAD.yaml` contains exactly one current-head declaration:

```yaml
schema_version: "STAYTRUE-HEAD-2"
item_id: "STAYTRUE-<project_id>"
project_id: "<project_id>"
current_edition_id: "STAYTRUE-E0008"
current_content_sha256: "<full SHA-256>"
current_edition_path: "duenna/staytrue/projects/<project_id>/editions/STAYTRUE-E0008.md"
current_change_record_id: "STAYTRUE-CHANGE-0008"
current_event_id: "<CURRENT event ID>"
current_commit: "<full commit SHA containing this pointer and event>"
```

The pointer is a mutable discovery record, not an immutable historical record. Its full prior versions remain in Git history. The item ID and project ID must match the containing directory and edition header. A project has exactly one current head; heads are never shared between projects.

## 8. Approval and publication separation

Approval establishes acceptance of the exact candidate content and declared scope. Publication establishes that the approved edition became CURRENT for this project's item.

The approval event binds:
- item ID and project ID;
- exact edition ID, candidate digest and change-record ID;
- exact scope IDs and scope approval references;
- approver identity and authority type;
- delegation ID, act class and use number, if delegated;
- approval evidence reference and decision time.

After approval, the publisher/harness:
1. retrieves the exact approved candidate snapshot;
2. verifies its digest and authority record;
3. verifies its predecessor is still the current head for this project-specific item;
4. writes the immutable edition snapshot and evidence manifest;
5. updates this project's canonical `Staytrue.md` to byte-identical content;
6. records the effective event and new current-head pin;
7. marks the prior head SUPERSEDED in the append-only event history.

The head advance must be atomic or compare-and-swap guarded. The new head commit must have the previous head commit as its direct parent for a normal publication. If the current head changed or ancestry is inconsistent, publication stops with `HEAD_CONFLICT`. It must not overwrite the newer head or silently rebase the candidate.

## 9. Run-binding record

Every run that relies on Staytrue must have this immutable binding in its run configuration before work begins:

```yaml
schema_version: "STAYTRUE-RUN-BINDING-2"
run_id: "<unique-run-id>"
item_id: "STAYTRUE-<project_id>"
project_id: "<exact-project-id>"
edition_id: "STAYTRUE-E0008"
content_sha256: "<64 lowercase hex characters>"
edition_snapshot_path: "duenna/staytrue/projects/<project_id>/editions/STAYTRUE-E0008.md"
shelf_commit: "<full edition commit SHA>"
shelf_blob_sha: "<full Git blob object ID>"
bound_head_commit: "<full commit SHA of HEAD.yaml when this run bound>"
bound_head_event_id: "<current-head event ID at binding>"
change_record_id: "STAYTRUE-CHANGE-0008"
approval_ref: "<approval-event-reference>"
scope_id: "<exact scope ID>"
scope_approval_ref: "<exact owner-approved scope reference>"
bound_at: "<UTC timestamp>"
canonicalisation_id: "STAYTRUE-BYTES-UTF8-LF-v1"
improvise: "NO"
improvise_source: "DEFAULTED_NO"
improvise_derivation: "FIELD_ABSENT"
```

The `improvise` value is copied from the exact pinned edition header, or is effective `NO` if absent/invalid. `improvise_source` must be exactly `EDITION_HEADER` or `DEFAULTED_NO`. `improvise_derivation` records one of `EXPLICIT_YES`, `EXPLICIT_NO`, `FIELD_ABSENT`, or `FIELD_INVALID`. For explicit header values, `improvise` and `improvise_derivation` must agree. The binding must also record the observed raw field or validation error when defaulted, so the reason for defaulting is auditable. The edition remains the source of authority.

The binding is created by the harness, not supplied by the worker. The worker may report which edition it inspected, but that report does not establish the binding. A run cannot proceed if any required field is absent, if the item/project identity does not match, or if the edition does not apply to the run's exact scope.

A run's binding never changes in place. Rebinding means creating a new run or a separately authorised new attempt with a new binding and preserved relationship to the prior attempt.

## 10. Interim Shelf evidence mechanism

Until an authoritative Staytrue ledger is separately approved and implemented, the Shelf Git history is the interim evidence source for each project's independent item.

For each approved edition, the evidence manifest records:
- item ID and project ID;
- edition ID and full SHA-256 of exact edition bytes;
- canonicalisation ID;
- immutable edition path;
- Git blob object ID for that path;
- full commit SHA containing the edition and its change/approval evidence;
- that project's canonical `Staytrue.md` path and corresponding blob ID at that commit;
- predecessor edition ID and predecessor commit pin;
- approval event/reference and authority record;
- exact scope/applicability identifiers.

Interim rules:

1. Pin full commit SHA, never a moving branch name, tag name or `main` reference alone.
2. Pin the full Git blob object ID and independently computed full SHA-256 of the exact file bytes.
3. Verify that the immutable edition path and that project's canonical file at the pinned commit are byte-identical.
4. Verify that the commit contains the linked change record and approval/delegation evidence.
5. Preserve each approved edition at its immutable edition path in addition to the Git history of the canonical file.
6. Treat the Git commit as immutable version evidence, not as proof of approval or truth. Approval evidence remains separately required.
7. If the Shelf commit, blob or full digest cannot be retrieved or verified, edition status is UNKNOWN and the run must not bind to it.
8. A branch head is a discovery pointer only. It is not a historical pin and does not replace the full commit SHA.
9. Each current-head advance for one project is one commit containing that project's new edition snapshot, detached evidence manifest, immutable submitted change record (or its already-pinned reference), approval/lifecycle event, canonical file update and `HEAD.yaml` update. The previous head commit is its parent. A failed or conflicting update leaves the prior head untouched.
10. Project item directories, histories and head pointers are independent. A commit or head for another project cannot satisfy this item's evidence requirements.

A later dedicated ledger may replace the interim current-head lookup only by approved migration. Historical Shelf pins remain valid evidence and must remain resolvable.

## 11. Deterministic harness procedures

These checks are mechanical. The harness must not interpret natural-language intent.

### 11.1 Resolve current edition

Input: exact requested project ID and scope ID; trusted Shelf repository/ref configuration.

1. Construct the only permitted item ID, `STAYTRUE-<project_id>`, and resolve only `duenna/staytrue/projects/<project_id>/`. Do not search other project directories or fall back to a shared/global Staytrue.
2. Resolve the configured Shelf branch to one full commit SHA.
3. Retrieve that project's `HEAD.yaml` at that commit and require exactly one current-head declaration for the constructed item ID and exact project ID.
4. Verify that the referenced CURRENT event, edition, evidence manifest and immutable submitted change record exist at that same commit and agree with the pointer.
5. Retrieve the exact edition snapshot, approval evidence, and delegation evidence if referenced.
6. Verify all references resolve at the pinned commit and all item/project identifiers agree with the directory and each other.
7. If the pointer is absent, malformed, cross-project, or internally inconsistent, return `NO_CURRENT_HEAD`, `CONFLICTING_CURRENT_HEADS`, or `IDENTITY_MISMATCH` and STOP.

### 11.2 Verify digest and identity

1. Retrieve edition bytes from the immutable edition path at the pinned commit.
2. Apply the declared canonicalisation procedure. For `STAYTRUE-BYTES-UTF8-LF-v1`: require valid UTF-8; normalise line endings to LF; require one terminal LF; do not trim whitespace, alter Unicode normalisation, reorder metadata, or otherwise transform content.
3. Compute SHA-256 over those exact canonical bytes.
4. Compare the full 64-character digest with the detached evidence manifest and run-binding value.
5. Verify item ID, edition ID, predecessor ID, change-record ID and Shelf blob/commit pins against the evidence manifest.
6. Verify canonical `duenna/staytrue/projects/<project_id>/Staytrue.md` at that same commit is byte-identical to the immutable edition snapshot.
7. Any mismatch returns `DIGEST_MISMATCH`, `IDENTITY_MISMATCH` or `CANONICAL_SNAPSHOT_MISMATCH`; STOP.

The digest establishes byte identity only. It does not establish owner approval, truth or semantic fidelity.

### 11.3 Verify approval authority

1. Resolve the approval event referenced by the edition/evidence manifest and verify its position in this item's event predecessor chain.
2. Require the approval event to bind the exact item ID, project ID, candidate edition ID, digest, change-record ID, scope IDs and scope approval references.
3. If approver is Ben, verify the approval event's authenticated owner provenance.
4. If approver is a delegate, resolve the referenced delegation and its issuance event. Verify the issuance event is an ancestor of the approval event.
5. Count prior successful approval events referencing that delegation ID, act class and item ID by traversing the verified predecessor chain from issuance to immediately before the approval event. Count only `APPROVED` decisions. Require the approval event's `use_number` to equal prior count + 1 and not exceed `use_limit`. Reject duplicate use numbers or duplicated event identities.
6. Determine revocation at the approval event's chain position. If a `DELEGATION_REVOKED` event for this delegation is an ancestor of the approval event, the delegation was already revoked and is invalid. A revocation event occurring later in the same verified chain does not invalidate the earlier approval. If approval and revocation are on divergent histories or ancestry cannot be established, return `DELEGATION_INVALID` and STOP.
7. Validate exact delegate identity, act class, item/project/scope membership, validity interval at approval time, conditions, remaining use count, and issuance-before-approval. For workaround approval, require `APPROVE_STAYTRUE_WORKAROUND` and exact run/proposal IDs; edition authority alone is insufficient.
8. Require the approval event to precede publication/effective event in the same verified chain.
9. Missing or inconsistent evidence returns `APPROVAL_UNVERIFIED` or `DELEGATION_INVALID`; STOP.

A worker's statement that Ben approved, a name typed into a file, or a commit authored by a trusted collaborator is not approval evidence by itself.

**Authentication boundary:** this draft does not assume that Git commit authorship authenticates Ben or a delegate. Before implementation, the approval-evidence source and its verification method must be explicitly designated and approved. If the harness cannot verify the owner/delegate provenance from that designated source, it returns `APPROVAL_UNVERIFIED`; a Shelf commit alone cannot cure that gap.

### 11.4 Verify applicability

1. Verify that the item's `item_id`, `project_id`, containing directory and run-binding values all identify the same one project. Any cross-project mismatch returns `IDENTITY_MISMATCH` and STOP.
2. Read the edition's explicit scope entries, including ACTIVE and CLOSED entries.
3. Derive the exact set of all scope-entry IDs and scope approval references. Require the header's `project_ids` to equal the singleton project ID, and its `scope_ids` and `scope_approval_refs` to equal the corresponding sets derived from all scope entries. Duplicate, missing, malformed, extra or mismatched values return `APPLICABILITY_AMBIGUOUS` and STOP.
4. Require exactly one scope entry with the run's exact scope ID.
5. Require that entry to be ACTIVE and its `scope_approval_ref` to equal the run's supplied owner-approved scope reference.
6. Require the run-binding project/scope values to equal the values selected from the matched entry.
7. If there is no matching scope entry for a new run, return `TETHER_NOT_APPLICABLE`; STOP.
8. If IDs are duplicated, missing, malformed or map to multiple entries, return `APPLICABILITY_AMBIGUOUS`; STOP.

No fuzzy matching, project-name similarity, inferred parent/child relationship, or natural-language interpretation is permitted. A run for one project cannot bind to another project's item, even if scope IDs happen to match.

### 11.5 Verify improvise flag

1. Read the `improvise` field from the exact edition header pinned for the run.
2. If exactly `YES`, bind `YES`. If exactly `NO`, bind `NO`.
3. If absent, duplicated, malformed or any other value, bind effective `NO` and emit the corresponding default/invalid outcome. Do not infer a value from a previous edition, another scope, a worker preference or the current canonical file.
4. Verify the run-binding copy equals the derived effective value. A mismatch returns `IMPROVISE_BINDING_MISMATCH` and STOP.

### 11.6 Create run binding

1. Resolve current head.
2. Run §§11.2–11.5.
3. Record all §9 fields, including full commit, blob and SHA-256 pins and the effective `improvise` value.
4. Persist the binding in the canonical run record before the first governed action.
5. Make the binding immutable for the run.
6. If any check fails or evidence is unavailable, do not start governed work.

### 11.7 Detect a mid-run edition advance

At each harness-defined governed action boundary, compare the current head for the run's exact project-bound item with the run's pinned edition and bound head commit.

1. Resolve the latest head and verify its event chain and commit graph.
2. Verify mechanically that the newly observed head commit descends from `bound_head_commit` recorded in the run binding. Use the Git commit graph/ancestor relation, not timestamps or matching file content. If the bound head commit is not an ancestor, or ancestry cannot be established because history was rewritten, shallow, unavailable or divergent, pause and return `TETHER_HEAD_UNKNOWN` (or `HEAD_ANCESTRY_CONFLICT` where the graph positively proves divergence). Do not treat the new head as a valid continuation.
3. If the current head is unchanged, continue.
4. If the head advanced and the new edition still contains the run's exact scope entry as ACTIVE with the same scope approval reference, compare the edition's declared scope transition. If the change record identifies only other scope entries and makes no change to the bound scope, retain the original binding and continue; record the observed head and the verified non-overlap.
5. If the new edition explicitly marks the bound scope CLOSED, or its immutable change record explicitly records `CLOSE` or `REMOVE` for the bound scope ID, pause before the next governed action and return `TETHER_ADVANCED_REVIEW_REQUIRED`. Closure/removal is a settled owner decision about the run's own scope, not an unrelated applicability miss.
6. If the new edition omits the bound scope and there is no explicit, verifiable CLOSE/REMOVE record, do not assume either closure or harmless non-overlap. Pause with `TETHER_HEAD_UNKNOWN` for authority clarification.
7. If the new edition changes the bound scope's approval reference, constraints, status, acceptance conditions or other declared scope entry, pause with `TETHER_ADVANCED_REVIEW_REQUIRED`.
8. If the new head or its applicability/change evidence cannot be resolved, pause and return `TETHER_HEAD_UNKNOWN`.
9. Never replace the run's edition ID, digest, improvise value or binding automatically. Never infer whether new wording is compatible with the old run's work.

To resume after `TETHER_ADVANCED_REVIEW_REQUIRED`, require a new owner decision explicitly choosing one of:
1. **CONTINUE_PINNED_EDITION** — authorises this identified run to continue under its original edition despite the newer current head and its scope decision; records the exact run, pinned edition, new head, decision authority and rationale.
2. **STOP_AND_REBIND** — closes or suspends the current attempt and requires a new run/attempt with the new edition bound.
3. **STOP** — no continuation authorised.

A valid delegate may choose only if the delegation explicitly covers this exact act and run/scope. Otherwise Ben decides. The harness checks the decision record and authority mechanically; it does not decide which option is substantively appropriate.

A later edition never retroactively changes the historical binding or the record of actions already performed. The run's `improvise` setting remains the value pinned at run binding; an edition advance cannot silently enable or disable workaround proposals for that run.

### 11.8 Handle task failure and workaround proposals

On a task failure, read only the effective `improvise` value in the run binding:

- **NO:** stop the failed task, preserve its failure evidence, and report the failure. Do not generate or submit a workaround proposal.
- **YES:** the agent may prepare and submit a workaround proposal. It must not attempt, execute, publish or otherwise enact the workaround merely because the flag is YES.

A workaround proposal must use this record shape:

```yaml
schema_version: "STAYTRUE-WORKAROUND-PROPOSAL-1"
proposal_id: "<unique-id>"
run_id: "<run-id>"
project_id: "<project-id>"
scope_id: "<scope-id>"
pinned_edition_id: "<edition-id>"
pinned_content_sha256: "<full SHA-256>"
improvise_value: "YES"
task_id: "<failed-task-id>"
failure:
  observed_result: "<what failed>"
  expected_result: "<what was expected>"
  evidence_refs: ["<failure evidence references>"]
workaround:
  description: "<proposed alternative>"
  steps: ["<proposed step>"]
tether_delta:
  affected_rule_ids: ["<stable rule IDs, or empty>"]
  affected_scope_fields: ["<scope fields, or empty>"]
  constraints_or_exclusions_touched: ["<exact references, or empty>"]
  change_description: "<what differs from the pinned tether>"
  impact: "<scope, deliverable, evidence, dependency or risk impact>"
  requires_tether_edition_change: true
proposed_by: "<authenticated agent/worker identity>"
submitted_at: "<UTC timestamp>"
status: "PROPOSED"
approval_ref: null
```

The proposal must identify the failed task and supporting evidence, describe the alternative, and make the delta against the exact pinned edition explicit. `requires_tether_edition_change` must be a boolean: `true` when any settled tether term would change; `false` only when the requested workaround is a run-scoped deviation that leaves the standing tether unchanged. It must not rewrite the tether, alter the run binding, or describe itself as approved. The approval record must identify the exact proposal ID, run ID, pinned edition, decision (`APPROVED` or `REJECTED`), approver, authority type, delegation ID if applicable, permitted actions/limits, and approval evidence reference.

The proposal enters the same authority chain used for changes to settled intent: Ben, or a delegate whose recorded delegation explicitly covers the relevant approval act and scope. For a delegate, the required act class is `APPROVE_STAYTRUE_WORKAROUND`; `APPROVE_STAYTRUE_EDITION` alone does not imply workaround-approval authority. The authority must approve or reject the exact proposal and its tether delta. Silence, receipt, acknowledgement, or a worker's own assessment is not approval.

If accepted workaround changes settled intent, scope, constraints, exclusions, acceptance conditions, or any other tethered term, it cannot be executed until a new Staytrue edition has been prepared, approved and made CURRENT through the normal lifecycle. If the authority instead approves a strictly run-scoped deviation without changing the standing tether, that approval must explicitly identify the exact run, pinned edition, proposal ID, permitted actions and limits; it does not alter the tether or authorise reuse in another run. The harness verifies the approval record and scope mechanically. If the approval's classification or bounds are missing or ambiguous, STOP.

A rejected proposal returns the run to stopped/failed status; no workaround action is taken. A YES flag permits proposal only, not unilateral action.

## 12. Required machine outcomes

The harness must emit stable, distinguishable outcomes, at minimum:

- `PASS`
- `NO_CURRENT_HEAD`
- `CONFLICTING_CURRENT_HEADS`
- `EDITION_NOT_FOUND`
- `DIGEST_MISMATCH`
- `IDENTITY_MISMATCH`
- `CANONICAL_SNAPSHOT_MISMATCH`
- `APPROVAL_UNVERIFIED`
- `DELEGATION_INVALID`
- `TETHER_NOT_APPLICABLE`
- `APPLICABILITY_AMBIGUOUS`
- `HEAD_CONFLICT`
- `TETHER_ADVANCED_REVIEW_REQUIRED`
- `TETHER_HEAD_UNKNOWN`\n- `HEAD_ANCESTRY_CONFLICT`
- `SHELF_EVIDENCE_UNAVAILABLE`
- `IMPROVISE_FLAG_DEFAULTED_NO`
- `IMPROVISE_FLAG_INVALID_DEFAULTED_NO`
- `IMPROVISE_BINDING_MISMATCH`
- `WORKAROUND_PROPOSAL_NOT_PERMITTED`
- `WORKAROUND_APPROVAL_UNVERIFIED`

Each result records run/change ID, input pins, check procedure/version, observed values, result code and timestamp. UNKNOWN/unavailable evidence is never converted to PASS.

## 13. Invariants

1. Exactly one canonical standing file exists at the designated path.
2. Every approved edition has a unique immutable edition ID and complete retained bytes.
3. No approved edition or change record is overwritten.
4. Every CURRENT edition has one verifiable approval event.
5. Every delegated approval resolves to a valid, prior, bounded delegation.
6. Every run binding pins edition ID, full digest and immutable Shelf location.
7. A run binds only to an edition explicitly applicable to its exact project and scope.
8. A later edition does not mutate an existing run binding.
9. A relevant mid-run head advance requires an explicit authority decision before further governed action.
10. Hashes and deterministic checks never claim to establish semantic fidelity to owner intent.
11. Mindkeep and personal-memory content are not part of this artefact or its checks.
12. An effective `improvise` value of `YES` permits proposal only; it never grants permission to execute a workaround.
13. An effective `improvise` value of `NO` requires stop-and-report on task failure, without workaround proposal.
14. A run's effective flag is determined solely by its pinned edition and cannot change mid-run through canonical-file advancement.

## 14. Review and non-authorisation

This document is a draft specification for Remmy's review and Ben's approval. It does not:
- create or populate the live `Staytrue.md`;
- approve any particular tether content or edition;
- establish a live delegation;
- create an authoritative ledger or authority registry;
- implement the harness procedures;
- authorise a run, execution, migration or Stage 6 action.

Remmy's review should identify defects or contradictions against the accepted owner ruling and existing Shelf governance. Ben's approval is required before this specification becomes an approved design basis. Implementation requires separate authorisation after that approval.

---

**End of draft.**
