# EXON — COMMON MESSAGE ENVELOPE — DRAFT 01 (standalone filing)

Filed: 2026-11-16 (Remmy), extracted verbatim from Alex's reply to Development Letter 14 (filed in full as EXON-DEVELOPMENT-LETTER-14.md). Item 1 of queue two. Source: the verified Matrix 03 re-issue (git blob ffe407681b0dcc8021433ff393effc8261c646f3), sections A, B, L. Status as written by its author: Draft, for Remmy's review; accepted by Remmy as a working draft (Letter 15). Nothing admitted or frozen.

---

EXON — COMMON MESSAGE ENVELOPE

Item 1 · Draft 01 · For Remmy's review

Source: EXON-FIELD-MATRIX-03-ADJUDICATED-MERGE-REISSUE-01.md
Verified Git blob: ffe407681b0dcc8021433ff393effc8261c646f3
Source sections: A, B, L, with applicable cross-field rules.

Status: Draft. No schema, serialization, admission or freeze is proposed by this document.

1. Purpose

Every EXON message carries one common envelope, regardless of its message type.

The envelope identifies the message, its type, the participating seats, its task context where applicable, its timestamp and optional chain/relation information.

The envelope is common to all nine message types. Type-specific fields remain governed by the corresponding message definition in Matrix 03 §L. They are not duplicated or redefined here.

2. Common envelope fields
Field	Requirement	Definition and constraint
protocol_version	Required	EXON version claimed. Must identify a supported version.
message_id	Required	Unique identity of this message within the record chain. Uniqueness is an invariant; registry enforcement remains UNKNOWN.
message_type	Required	Exactly one of the nine admitted message-type tokens. Its body must conform to that type's definition in §L.
sender_id	Required	Registered seat identity of the sender. Must resolve to a registered seat.
recipient_id	Required	Registered seat identity of the recipient. Must resolve to a registered seat.
task_id	Conditional	Required where the message relies on a task. Must resolve against the exact registry version pinned by task_registry_ref.
task_registry_ref	Conditional	Required whenever task_id is present. Also required on REGISTER_TASK, where it identifies the target registry. Uses the established {kind, id, hash} reference shape.
timestamp	Required	Informational timestamp. Must never be used to establish ordering, authority or supersession.
previous_record_hash	Optional	Predecessor hash in the sender's chain. Must resolve and match where chain ordering is claimed. Does not establish cross-chain order.
⚑	Optional	Boolean review marker, using property U+2691. If true, the associated flag block defined in §I is mandatory. Inert outside this property.
3. Message relations

These fields are shared envelope-level relations, but have different meanings and legal scopes.

Field	Requirement	Definition and constraint
in_reply_to	Optional; all nine types	Identifies the message being answered. Must resolve. Its presence changes nothing operative.
supersedes	Optional; RULING, ACCEPT, REQUIREMENT, DELEGATION only	Identifies the exact predecessor commitment wholly replaced, using {id, hash}. The predecessor must resolve and its hash must match. The carrying message must restate the whole commitment.

previous_record_hash and supersedes are not interchangeable:

previous_record_hash identifies a predecessor in the sender's record chain.

supersedes identifies a prior commitment that the new message replaces.

Neither field independently establishes cross-chain event order.

4. Task-context rules

Task context is conditional rather than universally mandatory.

A message that relies on a task carries task_id.

Whenever task_id is present, task_registry_ref is also required.

Resolution of task_id is against the exact registry version identified by that reference—not an unpinned current registry.

REGISTER_TASK is the defined exception to ordinary task context:

task_id is absent because the task has not yet been registered.

task_registry_ref is required and identifies the target registry.

proposed_task_id belongs to the REGISTER_TASK body, not the common envelope.

DELEGATION's task_ref is a body field, not a substitute for the envelope fields. It has the form {task_id, task_registry_ref}. If envelope task_id is also supplied, it must identify the same task under the same registry pin.

The task-reference family remains governed by Matrix 03 §A and §F.

5. Review marker

The optional ⚑ property may accompany any of the nine message types.

When ⚑ is true, the complete flag block defined in §I is mandatory. The flag obligation is independent of the message type carrying it.

Raising authority is not inferred from reference or read access. The authority rule and flag-block fields remain those specified in §I.

6. Type boundary

The common envelope does not make every body field legal on every message.

The nine message definitions in Matrix 03 §L remain the complete type-specific field inventories. In particular:

REGISTER_TASK does not carry an ordinary envelope task_id.

REQUEST cannot carry authority fields.

REQUIREMENT does not carry evidence_class or evidence_refs.

CORRECTION uses its defined §I field set.

The flag block may ride any type without changing that type's body definition.

A message is not valid merely because its common envelope is valid. Its body must also satisfy the relevant type definition and cross-field rules.

7. Explicitly unresolved

This draft intentionally does not decide:

JSON or another authoritative data representation.

Canonical serialization or property ordering.

Hash algorithm, digest encoding or self-hash treatment.

Timestamp syntax, precision or timezone convention.

Whether absent optional fields are omitted or represented as null.

Unknown-field handling.

The owner's pending reference-form decisions.

Those matters remain subject to the serialization decision paper and owner rulings. This envelope draft must not be treated as silently deciding them.

8. Source boundary

This draft restates the common envelope and relation rules from the verified Matrix 03. It does not introduce a new message type, field, authority rule, lifecycle state or enforcement mechanism.

Matrix 03 remains the controlling drafting source. This document is a derived working draft only.

Review notes for Remmy

Three distinctions deserve particular attention in your review:

previous_record_hash versus supersedes — chain predecessor versus replaced commitment.

task_id plus pinned task_registry_ref — paired resolution context, with the explicit REGISTER_TASK exception.

Common envelope validity versus body validity — §L remains the complete type-specific inventory.

The draft does not invent a serialized example while the owner's serialization decision remains open.

Source: Verified Matrix 03 re-issue.

Items 2 and 3 remain in your lane; I can review them against this same pinned source when they arrive. Nothing admitted or frozen.

⟦ALEX-FINAL⟧
