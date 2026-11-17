# STAYTRUE — EDITION LIFECYCLE AND HISTORY SPECIFICATION 01 (DRAFT)

**Status:** DRAFT FOR REMMY REVIEW AND BEN APPROVAL  
**Prepared by:** Alex  
**Date:** 2026-11-17  
**Scope:** Edition lifecycle, authority records, run binding, interim Shelf evidence, and deterministic harness checks for the single evolving Staytrue file.  
**Authority:** Ben's accepted Staytrue design ruling and Alex's revised design review, 2026-11-17.  
**Implementation status:** DESIGN ONLY. No implementation, live tether, authority registry, or execution is authorised by this specification.  
**Review sequence:** Remmy review → Ben specification approval → separate implementation authorisation.

---

## 1. Purpose and governing decisions

This specification defines how one standing `Staytrue.md` changes over time without losing prior editions or allowing a worker to silently change the owner's settled intent.

The following are fixed design inputs, not open questions in this draft:

1. There is one standing `Staytrue.md`, evolving across scopes and projects.
2. Each approved edition is immutable and historically recoverable.
3. Changes to settled intent require Ben's approval, or approval by a delegate under an explicit, recorded, scope-bounded delegation.
4. Every run binding records the exact edition ID and full content digest.
5. Edition history is append-only; complete prior content is retained.
6. A bound run retains its pinned edition. A later edition never silently rewrites an existing binding.
7. Until a dedicated authoritative ledger is approved and implemented, pinned Shelf commits and blob/content digests provide interim version evidence.
8. Mindkeep is outside Duenna and is not part of this mechanism.

The file's words express intent. The harness does not interpret those words to decide what Ben meant. It performs the deterministic checks specified here and stops where authority or semantic judgement is required.

## 2. Terms

- **Staytrue item:** the one persistent logical artefact, with stable item ID `DUENNA-STAYTRUE`.
- **Edition:** one complete, immutable snapshot of the standing file's content and metadata.
- **Canonical file:** the current working path `duenna/Staytrue.md`; it must be byte-identical to the currently approved edition snapshot.
- **Edition snapshot:** immutable archived copy of a complete edition.
- **Change record:** immutable record describing a proposed edition transition, its authority, evidence, and disposition.
- **Current head:** the one edition currently designated CURRENT by the Shelf evidence record.
- **Run binding:** immutable record pinning the edition actually used by a run.
- **Applicability:** explicit project/scope identifiers declared in an edition's machine-readable metadata. Applicability is identifier matching, not semantic interpretation.
- **Delegation:** a recorded, bounded grant from Ben authorising a named delegate to perform a specified approval act within specified scope and conditions.

Identity, integrity, authority, applicability and meaning are separate:
- an ID identifies an edition;
- a digest checks bytes;
- an approval record establishes authority;
- scope identifiers establish declared applicability;
- none of these proves that the text is a faithful expression of intent. That last question belongs to the approving authority.

## 3. Shelf file structure

The following paths are normative for the proposed Shelf layout:

```text
duenna/
  Staytrue.md
  staytrue/
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

- `duenna/Staytrue.md` is the sole standing/current file. It is updated to the content of the newly CURRENT edition.
- `editions/` contains the complete byte-preserved snapshot of every edition that reached APPROVED. Rejected and withdrawn proposals may be retained as proposal artefacts but must never be presented as approved editions.
- `changes/` contains one immutable change record per proposed transition, including rejected and withdrawn proposals.
- `evidence/` contains the detached edition evidence manifest, including full digests and Shelf pins.
- `events/` contains immutable lifecycle events: submission, approval/rejection/withdrawal, publication, head advance, supersession, and any later authority decision.
- `HEAD.yaml` is the single current-head pointer for the configured Shelf branch. It is updated only in the same commit that adds the new immutable event and edition evidence. Its prior values remain recoverable through Git history.
- `delegations/` contains the immutable authority records needed to verify delegated approval. A revocation is a new record referencing the delegation; the original is not edited.
- No history file is overwritten. The canonical `Staytrue.md` is the only intentionally moving path; its Git history is retained, and every approved version also has a permanent edition path.

A future implementation may use a different physical layout only through an approved specification amendment. It must preserve these identity, immutability and retrieval properties.

## 4. Standing-file content structure

Every edition contains these three top-level sections in this order:

### 4.1 Standing rules

Rules intended to persist across projects and scopes. They remain operative unless changed by an approved edition. Each rule should have a stable rule ID within the file to make changes traceable. The harness may check IDs and schema, but it must not infer a rule's meaning.

### 4.2 Current scope

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

### 4.3 Transition record

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
| `item_id` | Constant `DUENNA-STAYTRUE` |
| `edition_id` | Unique monotonic ID, e.g. `STAYTRUE-E0008` |
| `predecessor_edition_id` | Immediately preceding CURRENT edition; null only for initial edition |
| `change_record_id` | Unique ID of the transition record |
| `created_by` | Authenticated author identity |
| `created_at` | UTC timestamp; informational, not ordering authority |
| `project_ids` | Explicit project identifiers represented by active scope entries |
| `scope_ids` | Explicit scope identifiers represented by active scope entries |
| `scope_approval_refs` | Exact owner-approved scope decision references |
| `approval_ref` | Exact approval event/reference for this edition |
| `effective_event_ref` | Event at which the edition became CURRENT |
| `canonicalisation_id` | Exact digest procedure identifier, initially `STAYTRUE-BYTES-UTF8-LF-v1` |

The full content digest is stored in the detached evidence manifest, not self-embedded in the bytes it hashes. This avoids a self-referential digest. The manifest binds the digest to the edition ID, exact archived path, and Shelf commit/blob pins.

Edition IDs are never reused. The numeric suffix advances by one from the last allocated edition ID; gaps are permitted only where the change history explains them. Timestamps do not determine edition order.

## 6. Change-record format

Each proposed transition receives a unique immutable change record at:

`duenna/staytrue/changes/<change_record_id>.yaml`

Required fields:

```yaml
schema_version: "STAYTRUE-CHANGE-1"
change_record_id: "STAYTRUE-CHANGE-0008"
item_id: "DUENNA-STAYTRUE"
from_edition_id: "STAYTRUE-E0007"
candidate_edition_id: "STAYTRUE-E0008"
change_state: "SUBMITTED"
change_reason: "<why an edition change is proposed>"
change_summary: "<descriptive summary; not authority>"
affected_project_ids: ["<project-id>"]
affected_scope_ids: ["<scope-id>"]
changed_sections:
  - section_id: "<stable-rule-or-scope-entry-id>"
    change_type: "ADD | MODIFY | CLOSE | REMOVE"
    rationale: "<explanation>"
proposed_by: "<authenticated-principal>"
prepared_by: "<authenticated-principal>"
submitted_at: "<UTC timestamp>"
approval:
  decision: "PENDING | APPROVED | REJECTED | WITHDRAWN"
  approver: null
  authority_type: "OWNER | DELEGATE"
  delegation_id: null
  approval_evidence_ref: null
  decided_at: null
effective:
  event_ref: null
  effective_at: null
shelf:
  proposal_commit: null
  approved_edition_commit: null
  edition_blob_sha: null
  full_content_sha256: null
supersedes_change_record_id: null
```

The example values are illustrative. The final schema must define allowed nullability, enumerations, ID grammar and timestamp format before implementation.

Rules:
- The change record is append-only. A state change is recorded as a new event/addendum or a new immutable record version linked to the original; the original submitted record is not silently rewritten.
- The change summary and section diff are explanatory only. The complete candidate and approved edition bytes are retained.
- The approval evidence must point to the actual owner decision or valid delegation-backed decision, not merely to a worker's report that approval occurred.
- A change record cannot approve itself.
- A change record does not become an edition merely because it has an allocated ID.

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

A delegation must be recorded before it is exercised, at:

`duenna/staytrue/delegations/<delegation_id>.yaml`

Required fields:

- `delegation_id` — unique immutable ID;
- `delegator` — Ben's authenticated principal;
- `delegate` — exact authenticated principal permitted to act;
- `act_class` — exact value `APPROVE_STAYTRUE_EDITION`;
- `item_id` — `DUENNA-STAYTRUE`;
- `project_ids` and `scope_ids` — explicit bounded scope; no implicit global authority;
- `conditions` — any exact restrictions;
- `valid_from`, `expires_at` — validity interval;
- `use_limit` — one-use or explicitly stated bounded count;
- `issued_at` and `owner_decision_ref` — evidence that Ben granted it;
- `revocation_ref` — null unless a later immutable revocation record exists.

The harness validates delegate identity, act class, item, project/scope membership, time window, use limit, conditions and revocation status. Missing, ambiguous, expired, revoked or out-of-scope delegation is invalid. It does not fall back to inferred authority.

The approval event must record the delegation ID and the exact scope entry approved. A delegation for one project or scope cannot approve another. A delegation does not transfer or enlarge itself.

### 7.4 Lifecycle event record

Every lifecycle transition is represented by a new immutable event at `duenna/staytrue/events/<event_id>.yaml`. Required fields are:

- `event_id`, `event_type`, `item_id`, `edition_id`, and `change_record_id`;
- `from_state` and `to_state`;
- `actor` and `actor_role`;
- `authority_ref` and `delegation_id`, where applicable;
- `evidence_refs`;
- `occurred_at` (informational timestamp);
- `previous_event_id`, where a prior event exists;
- `shelf_commit` containing the event.

An event is append-only. Corrections are additional events that explicitly reference the event corrected; the original event remains intact. Event order is established by the predecessor chain and pinned Git history, not timestamps alone.

### 7.5 Current-head pointer

`duenna/staytrue/HEAD.yaml` contains exactly one current-head declaration:

```yaml
schema_version: "STAYTRUE-HEAD-1"
item_id: "DUENNA-STAYTRUE"
current_edition_id: "STAYTRUE-E0008"
current_content_sha256: "<full SHA-256>"
current_edition_path: "duenna/staytrue/editions/STAYTRUE-E0008.md"
current_change_record_id: "STAYTRUE-CHANGE-0008"
current_event_id: "<CURRENT event ID>"
current_commit: "<full commit SHA containing this pointer and event>"
```

The pointer is a mutable discovery record, not an immutable historical record. Its full prior versions remain in Git history. A valid head advance commits the new immutable edition, evidence manifest, lifecycle event, canonical `Staytrue.md`, and updated `HEAD.yaml` together. The commit must have the previously observed head commit as its parent. Concurrent advances must fail rather than overwrite one another.

The configured Shelf branch is the interim authoritative discovery location. A branch name alone is never a run pin: the resolved commit SHA, edition blob ID and full SHA-256 are copied into the run binding.

## 8. Approval and publication separation

Approval establishes that the named authority accepted the exact candidate content and declared applicability. Publication establishes that the approved bytes became the current canonical file.

The approval event must bind:
- candidate edition ID;
- full candidate content digest;
- change-record ID;
- project/scope IDs;
- scope approval references;
- approver identity;
- OWNER or DELEGATE authority type;
- delegation ID, if applicable;
- approval evidence reference;
- approval timestamp.

After approval, the publisher/harness:
1. retrieves the exact approved candidate snapshot;
2. verifies its digest and authority record;
3. verifies its predecessor is still the current head;
4. writes the immutable edition snapshot and evidence manifest;
5. updates canonical `duenna/Staytrue.md` to byte-identical content;
6. records the effective event and new current-head pin;
7. marks the prior head SUPERSEDED in the append-only event history.

The head advance must be atomic or compare-and-swap guarded. If the current head changed since the candidate was prepared, publication stops with HEAD_CONFLICT. It must not overwrite the newer head or silently rebase the candidate. A fresh candidate/change record is required.

## 9. Run-binding record

Every run that relies on Staytrue must have this immutable binding in its run configuration before work begins:

```yaml
schema_version: "STAYTRUE-RUN-BINDING-1"
run_id: "<unique-run-id>"
item_id: "DUENNA-STAYTRUE"
edition_id: "STAYTRUE-E0008"
content_sha256: "<64 lowercase hex characters>"
edition_snapshot_path: "duenna/staytrue/editions/STAYTRUE-E0008.md"
shelf_commit: "<full commit SHA>"
shelf_blob_sha: "<full Git blob object ID>"
change_record_id: "STAYTRUE-CHANGE-0008"
approval_ref: "<approval-event-reference>"
project_id: "<exact project ID>"
scope_id: "<exact scope ID>"
scope_approval_ref: "<exact owner-approved scope reference>"
bound_at: "<UTC timestamp>"
canonicalisation_id: "STAYTRUE-BYTES-UTF8-LF-v1"
```

The binding is created by the harness, not supplied by the worker. The worker may report which edition it inspected, but that report does not establish the binding.

The harness records the binding in the canonical run record. A run cannot proceed if any required field is absent or if the edition does not apply to the run's exact project/scope identifiers.

A run's binding never changes in place. Rebinding means creating a new run or a separately authorised new attempt with a new binding and preserved relationship to the prior attempt.

## 10. Interim Shelf evidence mechanism

Until an authoritative Staytrue ledger is separately approved and implemented, the Shelf Git history is the interim evidence source.

For each approved edition, the evidence manifest records:

- item ID and edition ID;
- full SHA-256 of exact edition bytes;
- canonicalisation ID;
- immutable edition path;
- Git blob object ID for that path;
- full commit SHA containing the edition and its change/approval evidence;
- canonical `duenna/Staytrue.md` path and corresponding blob ID at that commit;
- predecessor edition ID and predecessor commit pin;
- approval event/reference and authority record;
- project/scope applicability identifiers.

Interim rules:

1. Pin full commit SHA, never a moving branch name, tag name or `main` reference alone.
2. Pin the full Git blob object ID and independently computed full SHA-256 of the exact file bytes.
3. Verify that the immutable edition path and canonical file at the pinned commit are byte-identical.
4. Verify that the commit contains the linked change record and approval/delegation evidence.
5. Preserve each approved edition at its immutable edition path in addition to the Git history of the canonical file.
6. Treat the Git commit as immutable version evidence, not as proof of approval or truth. Approval evidence remains separately required.
7. If the Shelf commit, blob or full digest cannot be retrieved or verified, edition status is UNKNOWN and the run must not bind to it.
8. A branch head is a discovery pointer only. It is not a historical pin and does not replace the full commit SHA.
9. Each current-head advance is one commit containing the new edition snapshot, detached evidence manifest, change record, approval/lifecycle event, canonical file update and `HEAD.yaml` update. The previous head commit is its parent. A failed or conflicting update leaves the prior head untouched.

A later dedicated ledger may replace the interim current-head lookup only by approved migration. Historical Shelf pins remain valid evidence and must remain resolvable.

## 11. Deterministic harness procedures

These checks are mechanical. The harness must not interpret natural-language intent.

### 11.1 Resolve current edition

Input: requested project ID and scope ID; trusted Shelf repository/ref configuration.

1. Resolve the configured Shelf branch to one full commit SHA.
2. Retrieve `duenna/staytrue/HEAD.yaml` at that commit and require exactly one current-head declaration for `DUENNA-STAYTRUE`.
3. Verify that the referenced CURRENT event, edition, evidence manifest and change record exist at that same commit and agree with the pointer.
4. Retrieve the exact edition snapshot, approval evidence, and delegation evidence if referenced.
5. Verify all references resolve at the pinned commit.
6. If the pointer is absent, malformed, or internally inconsistent, return `NO_CURRENT_HEAD` or `CONFLICTING_CURRENT_HEADS` and STOP.

### 11.2 Verify digest and identity

1. Retrieve edition bytes from the immutable edition path at the pinned commit.
2. Apply the declared canonicalisation procedure. For `STAYTRUE-BYTES-UTF8-LF-v1`: require valid UTF-8; normalise line endings to LF; require one terminal LF; do not trim whitespace, alter Unicode normalisation, reorder metadata, or otherwise transform content.
3. Compute SHA-256 over those exact canonical bytes.
4. Compare the full 64-character digest with the detached evidence manifest and run-binding value.
5. Verify item ID, edition ID, predecessor ID, change-record ID and Shelf blob/commit pins against the evidence manifest.
6. Verify canonical `duenna/Staytrue.md` at that same commit is byte-identical to the immutable edition snapshot.
7. Any mismatch returns `DIGEST_MISMATCH`, `IDENTITY_MISMATCH` or `CANONICAL_SNAPSHOT_MISMATCH`; STOP.

The digest establishes byte identity only. It does not establish owner approval, truth or semantic fidelity.

### 11.3 Verify approval authority

1. Resolve the approval event referenced by the edition/change record.
2. Require the approval event to bind the exact candidate edition ID, digest, change-record ID, project/scope IDs and scope approval references.
3. If approver is Ben, verify the approval event's authenticated owner provenance.
4. If approver is a delegate, resolve the referenced delegation and mechanically validate every condition in §7.3, including exact delegate identity, act class, item, project/scope, validity interval, use limit and non-revocation at approval time.
5. Require the approval event to precede publication/effective event.
6. Missing or inconsistent evidence returns `APPROVAL_UNVERIFIED` or `DELEGATION_INVALID`; STOP.

A worker's statement that Ben approved, a name typed into a file, or a commit authored by a trusted collaborator is not approval evidence by itself.

**Authentication boundary:** this draft does not assume that Git commit authorship authenticates Ben or a delegate. Before implementation, the approval-evidence source and its verification method must be explicitly designated and approved. If the harness cannot verify the owner/delegate provenance from that designated source, it returns `APPROVAL_UNVERIFIED`; a Shelf commit alone cannot cure that gap.

### 11.4 Verify applicability

1. Read the edition's machine-readable `project_ids` and `scope_ids` and its explicit active scope entries.
2. Require an exact project ID match and exact scope ID match for the run.
3. Require the matching scope entry to be ACTIVE.
4. Require its `scope_approval_ref` to equal the run's supplied owner-approved scope reference.
5. Require the run-binding project/scope values to equal the values selected from the matched entry.
6. If there is no exact match, return `TETHER_NOT_APPLICABLE`; STOP.
7. If IDs are duplicated, missing, malformed or map to multiple active entries without an explicit unique scope selection, return `APPLICABILITY_AMBIGUOUS`; STOP.

No fuzzy matching, project-name similarity, inferred parent/child relationship, or natural-language interpretation is permitted. Any scope relationship requiring judgement must be resolved in the owner-approved scope record before binding.

### 11.5 Create run binding

1. Resolve current head.
2. Run §§11.2–11.4.
3. Record all §9 fields, including full commit, blob and SHA-256 pins.
4. Persist the binding in the canonical run record before the first governed action.
5. Make the binding immutable for the run.
6. If any check fails or evidence is unavailable, do not start governed work.

### 11.6 Detect a mid-run edition advance

At each harness-defined governed action boundary, compare the current head for `DUENNA-STAYTRUE` with the run's pinned edition.

- Resolve the configured Shelf branch and read `HEAD.yaml` at its latest commit; verify the pointer and its event chain as in §11.1.
- If the current head is unchanged, continue.
- If the current head has advanced but its declared project/scope applicability does not include the run's exact project/scope, retain the original binding and continue. Record the observed head and non-overlap result.
- If the new current edition explicitly includes the run's exact project/scope, pause before the next governed action and return `TETHER_ADVANCED_REVIEW_REQUIRED`.
- If the new head or its applicability cannot be resolved, pause and return `TETHER_HEAD_UNKNOWN`.
- Never replace the run's edition ID or digest automatically.
- Never infer whether the new wording is compatible with the old run's work.

To resume after `TETHER_ADVANCED_REVIEW_REQUIRED`, require a new owner decision explicitly choosing one of:
  1. **CONTINUE_PINNED_EDITION** — authorises this identified run to continue under its original edition despite the newer current head; records the exact run, pinned edition, new head, decision authority and rationale.
  2. **STOP_AND_REBIND** — closes or suspends the current attempt and requires a new run/attempt with the new edition bound.
  3. **STOP** — no continuation authorised.

A valid delegate may choose only if the delegation explicitly covers this act and exact run/scope. Otherwise Ben decides. The harness checks the decision record and authority mechanically; it does not decide which option is substantively appropriate.

A later edition never retroactively changes the historical binding or the record of actions already performed.

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
- `TETHER_HEAD_UNKNOWN`
- `SHELF_EVIDENCE_UNAVAILABLE`

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
