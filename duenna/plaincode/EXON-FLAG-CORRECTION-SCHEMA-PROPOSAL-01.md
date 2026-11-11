# EXON — FLAG and CORRECTION Schema Proposal 0.1

**Prepared by:** Alex  
**Date:** 2026-11-11  
**Status:** Design proposal for Remmy's Dictionary 0.2 reconciliation; not approved, frozen, or implemented.

## 1. Purpose and governing distinction

EXON needs a governed way to express doubt about an existing commitment or record without requiring the raiser to prove an error first.

The proposed mechanism has two separate acts:

- **Review flag:** a low-cost signal that obligates an independent second look.
- **Correction:** a structured, authorised repair of an established record or claim found to be wrong.

A flag is not a correction, a STOP, a finding of INCORRECT, a SUPERSEDE, or a withdrawal. A correction is not merely the disposition label on a flag; it is a separately addressable record.

The mechanism is designed to preserve the original record and its history. It must not make uncertainty expensive to report, and it must not turn the act of flagging into a veto.

## 2. Layer placement and marker representation

### 2.1 Review marker

The review marker belongs to **Layer B — schema keywords and enumerated values**. It is not a dictionary term and has no prose meaning to adjudicate.

The word “flag” in this document is a human-readable design label only. It must not itself be the operative trigger.

**Proposed canonical marker:** `⚑` (U+2691 BLACK FLAG), represented as a dedicated schema property/marker with a required boolean value. Example shape:

```json
{
  "⚑": true,
  "target_ref": "record-id-or-commitment-id",
  "concerns": [
    {
      "concern_id": "concern-001",
      "raiser_id": "seat-id",
      "raised_at": "informational timestamp"
    }
  ]
}
```

This is an illustrative shape, not a frozen wire contract. The exact serialization, allowed target classes, identity rules, and validator behaviour must be settled before schema freeze. The symbol is the trigger; explanatory text, if supplied, is metadata and cannot change the trigger's effect.

A flag must identify a resolvable target. It may target an original record, a correction record, or another eligible commitment/record. It may target a FROZEN record.

### 2.2 Fixed schema category

Add a fixed schema category named **Review and repair control**. Candidate members:

- `⚑` — review marker;
- `target_ref` — exact target record/commitment reference;
- `flag_id` — identity of the coalesced review obligation;
- `concern_id` — identity of an individually attributed concern;
- `raiser_id` — seat raising that concern;
- `review_owner` — independent reviewer;
- `review_disposition` — closed enum: `CLEARED` or `CORRECTED`;
- `correction_ref` — required when disposition is `CORRECTED`;
- `prior_flag_ref` — optional reference to a previously closed review obligation where a later flag concerns the same target.

These are schema candidates, not Dictionary terms. Their legal message types, requiredness, and validation rules must be specified in the reconciled schema.

### 2.3 Marker effect

The marker creates one obligation: **a second look must be performed and recorded**.

It does not:
- halt the target's work;
- invalidate, revoke, or erase the target;
- change its evidence class;
- make the target INCORRECT;
- establish that the concern is true;
- automatically suspend existing reliance;
- confer correction, adjudication, or STOP authority on the raiser.

While the review is open, the target and its flagged state must both remain visible. Any applicable rule requiring verified evidence, or any separate authorised act, may independently restrict reliance or halt an operation. Such a consequence must cite that rule or act; it must never be inferred from the marker alone.

The programme has not demonstrated a complete reliance registry. The schema must not claim automatic discovery, notification, or enumeration of every downstream reliance.

## 3. Flag lifecycle

### 3.1 Raising

Any seat permitted to reference the target may raise a flag, including the target's author. Self-flagging and flagging another seat's work have the same review effect.

Each concern records its raiser. The raiser does not gain authority over the target and cannot clear the resulting review.

A reason or explanation may be included as optional metadata. It is not a precondition for raising the flag: unease may be sufficient. If a concern is supplied, it must be preserved as the raiser's attributed concern, not silently converted into an established finding.

### 3.2 Coalescing

If a second flag arrives while a review obligation for the same target remains open:

- it attaches to the existing `flag_id`;
- its raiser and concern are separately attributed;
- it creates no duplicate review obligation;
- it does not reset, silently extend, or replace the existing obligation;
- if materially different, it creates an additional named concern that the reviewer must answer before disposition.

The review cannot close while any attached concern remains unanswered.

A second flag is not a new identity for the same open obligation. The history of each concern remains individually visible.

### 3.3 Review independence

The reviewer must not be the raiser of the flag being dispositioned. Where multiple concerns are coalesced, the reviewer must be independent of each raiser.

The reviewer must have authority to make the review disposition. A reviewer who lacks the necessary authority cannot clear the flag or issue a correction; the review remains open pending an authorised reviewer. This is not a third disposition.

The review must examine the target and each attached concern. A flag is not cleared merely because the reviewer disagrees with the raiser or because the target was previously accepted, verified, corrected, or frozen.

### 3.4 Closing outcomes

Exactly two recorded dispositions are permitted:

- **CLEARED** — the review found no correction necessary for the target and all attached concerns have been answered.
- **CORRECTED** — an authorised CORRECTION record has been created and linked.

No other terminal disposition is allowed. In particular, “dismissed,” “invalid,” “withdrawn,” “blocked,” and “unable to review” must not become substitute outcomes. If evidence or authority is insufficient, the obligation remains open and the limitation is recorded.

For CORRECTED, `correction_ref` is mandatory and must resolve to the correction record. A disposition cannot claim CORRECTED before that record exists.

### 3.5 Subsequent flags

A target is not immune from further challenge after CLEARED or CORRECTED. A later flag creates a new review obligation linked by `prior_flag_ref`; it does not rewrite or reopen the closed obligation.

A flag against a correction record is permitted. The correction is itself a record and may be wrong, incomplete, or overreaching.

A later flag against a FROZEN target is also permitted. Its disposition may be CLEARED or CORRECTED. If corrected, the correction is appended alongside the frozen original; the original content and hash remain untouched.

## 4. CORRECTION message type

### 4.1 Why a distinct type

CORRECTION is a distinct structured act and should be added as a message type. It must not be hidden as a subform of RESULT, RULING, ACCEPT, or SUPERSEDE.

- RESULT reports an outcome; it does not repair a record.
- RULING adjudicates a matter; a ruling may authorise or determine a correction but is not itself the repair record unless the schema explicitly records both acts separately.
- SUPERSEDE prospectively replaces a commitment; it does not assert that the predecessor was erroneous.
- CORRECTION repairs an identified record or claim because an established value was wrong.

The original record remains preserved and addressable. The correction is appended and linked to it.

### 4.2 Required correction content

A CORRECTION record should carry:

1. `correction_id` — unique identity.
2. `target_ref` — exact original record and, where applicable, exact claim/field.
3. `wrong_value` — the value being corrected, with a reference to the original location.
4. `corrected_value` — the replacement value; mutually exclusive with `WITHDRAWN`.
5. `withdrawal` — explicit `WITHDRAWN` marker when no replacement value is asserted.
6. `original_author_id` — the seat responsible for the original claim/record.
7. `correcting_actor_id` — the seat making the correction.
8. `authority_ref` — the authority under which the correction is made.
9. `reason_ref` or bounded explanation — why the original value is wrong, with evidence references where available.
10. `reliance_dispositions` — each identified downstream reliance and its disposition.
11. `unresolved_reliance` — explicit list or bounded statement of reliance impacts that could not be identified or resolved.
12. `in_response_to_flag_ref` — required when the correction closes a flag as CORRECTED; otherwise optional.
13. `timestamp` — informational metadata, not ordering authority.

The exact value encoding and enum ownership for `WITHDRAWN` must be defined in the schema layer. It must not be confused with deleting the original record.

### 4.3 Authority shapes

Two correction authority shapes must remain distinct:

**Self-correction**
- The correcting actor is the original author/owner of the claim.
- The actor corrects only a claim or record they are authorised to amend.
- Self-correction does not confer authority over another seat's record or over reserved matters.
- The original author and correcting actor remain separately recorded even when they are the same seat.

**Adjudicator-correction**
- The correcting actor is not the original author.
- The actor must hold explicit authority for the correction class and scope.
- The authority reference and adjudication basis must be recorded.
- The adjudicator cannot claim self-correction authority merely because they reviewed the flag.

These are different authority shapes, not different meanings of CORRECTION. A valid correction must identify which shape applies and pass its authority check.

### 4.4 Reliance accounting

Correction does not silently unwind all consequences of the original claim.

For each known reliance, record:
- the relying record/act;
- the specific corrected claim relied upon;
- whether the reliance remains valid, requires reassessment, is withdrawn, or has been otherwise dealt with under an authorised decision;
- the authority/evidence for that disposition.

These reliance statuses need their own schema definitions before use. Do not introduce an unreviewed universal enum merely to fill the field.

Where downstream reliance cannot be enumerated because no complete reliance registry exists, state that limitation. Do not claim COMPLETE reliance accounting. A correction may be recorded while identified reliance remains unresolved only if the schema makes that incompleteness explicit and the relevant authority permits it; otherwise the correction cannot close the flag.

### 4.5 Correction boundaries

- CORRECTION is not SUPERSEDE: an erroneous record is repaired; a valid commitment may also be replaced prospectively.
- CORRECTION is not RESULT: reporting an error is not repairing it.
- CORRECTION is not STOP: repair does not itself halt unrelated work.
- CORRECTION is not deletion: the original remains visible, immutable, and linked.
- CORRECTION is not a new assertion without provenance: it must identify the wrong value, corrected value or WITHDRAWN state, actor, authority, and reliance treatment.

## 5. FORM / MEANING split

| Check | FORM — mechanically decidable | MEANING — adjudication |
|---|---|---|
| Marker | Marker is present in the permitted schema location; target reference resolves; flag identity and raiser are recorded. | Whether the concern is material or points to a genuine defect. Materiality is not required to raise the flag. |
| Coalescing | Open obligation for target is found; new concern attaches to its identity; no duplicate obligation or reset is created. | Whether a new concern is materially distinct from existing concerns. |
| Reviewer | Reviewer identity differs from each raiser; reviewer authority reference is present. | Whether the reviewer is sufficiently independent and competent for the matter, where that cannot be mechanically established. |
| CLEARED | All attached concerns have recorded responses; disposition is one of the two permitted values; reviewer and authority are recorded. | Whether the evidence genuinely supports no correction being necessary. |
| CORRECTED | Correction reference resolves; target, wrong value, replacement/withdrawal, actor and authority fields are present; original record remains intact. | Whether the corrected value is right, the correction is within authority, and reliance treatment is adequate. |
| Frozen target | Original hash still matches; correction is a separate appended record. | Whether the appended correction legitimately addresses the frozen content without purporting to alter it. |
| Reliance | Each listed reliance reference resolves; each has an explicit disposition or unresolved marker. | Whether the identified set is complete and each disposition is substantively justified. No complete registry is currently established. |

A FORM pass never establishes a MEANING pass. A validly shaped flag is not proof of error; a validly shaped correction is not proof that the replacement is true.

## 6. Neighbour boundaries for Dictionary 0.2

These concepts must remain separate from existing dictionary terms and schema values:

| Concept | Must not be conflated with | Boundary |
|---|---|---|
| Review marker `⚑` | STOP | It obligates review but does not halt work. |
| Review marker `⚑` | INCORRECT | It expresses concern before an error is established. |
| Review marker `⚑` | CORRECTION | It initiates a second look; it does not repair anything. |
| Review marker `⚑` | SUPERSEDE | It does not replace a commitment or change its operative head. |
| CLEARED | VALID | Clearing a concern does not certify every FORM or MEANING property of the target. |
| CLEARED | SUPPORTED | The review disposition is not a universal evidential endorsement. |
| CORRECTED | RESULT | A correction changes an identified claim/record; a result merely reports. |
| CORRECTED | SUPERSEDE | Correction is error repair; supersession is prospective replacement. |
| WITHDRAWN | deletion | The original remains; WITHDRAWN means no replacement value is asserted. |
| FROZEN | unquestionable | Freeze prevents editing; it does not prevent review or append-only correction. |

The marker, `CLEARED`, `CORRECTED`, and `WITHDRAWN` are schema-layer elements, not new dictionary terms, unless the reconciliation explicitly assigns a different layer and documents why.

## 7. Adversarial case set

These are design tests, not executed results. Each case should be run against the final frozen schema before any implementation is accepted.

| ID | Adversarial input / condition | Required behaviour | Failure exposed |
|---|---|---|---|
| FC-01 | Author raises a flag against their own record before knowing whether it is wrong. | Accept the flag; create one review obligation; author cannot clear it. | Self-flagging blocked or treated as admission of error. |
| FC-02 | Seat flags another seat's record with no proof, only unease. | Accept if target is validly addressable; concern remains attributed, not established fact. | Proof burden makes early honesty too expensive. |
| FC-03 | Raiser attempts to disposition their own flag as CLEARED. | Reject disposition; keep review open for an independent authorised reviewer. | Self-clearance. |
| FC-04 | Two seats flag the same target while its review is open. | Coalesce into one obligation; preserve both raisers and concerns. | Duplicate obligations or lost attribution. |
| FC-05 | Second flag adds a materially different concern. | Attach named concern; reviewer answers both before one disposition. | First concern silently closes over second. |
| FC-06 | Second flag repeats the same concern while open. | Preserve attribution; do not reset, extend, or duplicate the review. | Flag-spam used to reset a clock or multiply work. |
| FC-07 | Raiser submits many flags as obstruction. | Each valid target receives the required look; any abuse finding is separate and does not create a third disposition. | Bad-faith suspicion used to suppress flags or create veto power. |
| FC-08 | Reviewer disagrees with the raiser but does not examine the target/evidence. | Do not permit CLEARED; record must answer the concern with a basis. | Performative dismissal. |
| FC-09 | Reviewer lacks authority for the target's correction class. | Reviewer cannot clear or correct; obligation remains open pending authorised review. | Authority inferred from reviewer role or possession. |
| FC-10 | Reviewer is independent of one coalesced raiser but is another raiser's own seat/author. | Reviewer is ineligible for the coalesced obligation. | Independence checked against only one raiser. |
| FC-11 | Review disposition is CORRECTED but correction_ref is absent or unresolved. | Reject closure; flag remains open. | Unsupported correction claim. |
| FC-12 | Correction claims a new value but also marks WITHDRAWN. | Reject mutually incompatible replacement/withdrawal states. | Ambiguous corrected value. |
| FC-13 | Correction changes a record but omits original author or correcting actor. | Reject as malformed; retain original. | Unattributed repair. |
| FC-14 | Non-author corrects a record without scoped authority. | Reject correction; reviewer cannot use the flag as authority. | Review power mistaken for amendment authority. |
| FC-15 | Author attempts self-correction of another seat's record. | Reject unless separately authorised for that scope; self-correction shape does not apply. | Identity-based authority leakage. |
| FC-16 | Correction is made but known downstream reliance is omitted. | Do not claim complete reliance accounting; require explicit unresolved reliance treatment and applicable authority. | Silent downstream impact. |
| FC-17 | Reliance registry is unavailable or incomplete. | Record the limitation; do not claim all downstream reliance was identified. | Intended registry presented as existing machinery. |
| FC-18 | A corrected record is flagged again because the correction may itself be wrong. | Permit a new flag targeting the correction record; preserve prior review and correction history. | Correction becomes immune to challenge. |
| FC-19 | A second flag arrives after the first obligation has closed. | Create a new linked obligation; do not rewrite or reopen the closed one. | Closed history silently mutated. |
| FC-20 | A FROZEN record is flagged and found wrong. | Append a correction; original bytes/hash remain unchanged. | Freeze misread as immunity or correction misread as edit. |
| FC-21 | Flag is raised and a downstream user treats the target as automatically invalid. | No automatic invalidation; reliance changes only under an existing rule or separate authorised act. | Marker becomes an implicit STOP/revocation. |
| FC-22 | Flag is raised against a record that is already STOPped under an independent rule. | Flag still creates a review obligation; existing STOP remains governed by its own release condition. | Flag and STOP lifecycles merged. |
| FC-23 | A flag is cleared, then new evidence shows the reviewer missed a material error. | Permit a new linked flag; preserve prior CLEARED disposition and reviewer record. | Clearance treated as permanent immunity. |
| FC-24 | A correction is appended, but the original is deleted or overwritten. | Reject; correction must be append-only and original must remain resolvable. | Historical erasure. |
| FC-25 | Marker appears in ordinary prose without a valid schema envelope/target. | Treat as inert prose or malformed structured input according to the final protocol; never infer a valid flag from an ambiguous mention. | Accidental trigger from quoted/discussed symbol. |
| FC-26 | Marker is present but its target reference resolves to multiple records or wrong hash. | Reject as malformed; no review obligation is silently attached to an ambiguous target. | Target ambiguity. |
| FC-27 | A concern remains unanswered but reviewer attempts CLEARED. | Reject closure; every attached concern must receive a recorded response. | Premature closure. |
| FC-28 | Review cannot proceed because evidence is inaccessible. | Keep obligation open and record the access limitation; do not invent a third terminal outcome. | Inability to review disguised as clearance. |

## 8. Open design decisions for reconciliation

The following must be resolved before schema freeze:

1. **Wire encoding:** confirm whether U+2691 `⚑` is the canonical marker or select another dedicated symbol. The operative trigger must not be an ordinary word.
2. **Eligible targets:** enumerate which record/commitment classes may be flagged, including messages, claims, corrections, frozen artefacts, and commitments.
3. **Identity/coalescing:** define the deterministic key for deciding whether a new flag joins an open obligation. Target identity is necessary but may not be sufficient if one target contains independently reviewable claims.
4. **Review timing/ownership:** define how an authorised independent reviewer is assigned and what happens operationally while no eligible reviewer is available. No invented timeout or auto-clear.
5. **Materiality:** define when a second concern is materially distinct for response purposes; do not make materiality a gate to raising a flag.
6. **Correction scope:** define whether one CORRECTION message may repair multiple claims in one target or whether each claim requires a separate correction record.
7. **Reliance dispositions:** define the closed schema values and authority for changing each reliance. Do not imply a complete reliance registry.
8. **WITHDRAWN encoding:** specify its field and mutual-exclusion rule with corrected_value.
9. **Re-flag policy:** define whether repeated flags after closure require a new concern reference or evidence reference; preserve the ability to challenge a previously cleared/corrected record.
10. **Symbol parsing:** define how quoted, escaped, or explanatory appearances of `⚑` are distinguished from an operative marker.

## 9. Acceptance conditions for this proposal

Before this proposal can be treated as schema-ready:

- The marker has one canonical, mechanically detectable representation and one effect.
- Every flag has a resolvable target, attributable raiser(s), and a single coalesced review obligation while open.
- The raiser cannot clear their own flag; the reviewer is independent of all attached raisers and holds the necessary authority.
- The only terminal dispositions are CLEARED and CORRECTED.
- CORRECTED always links an existing, authorised CORRECTION record.
- Corrections preserve the original and explicitly separate original author, correcting actor, and authority.
- Frozen records can be challenged but only repaired append-only.
- Existing reliance is not automatically invalidated by a flag; known and unresolved reliance are explicitly accounted for in corrections.
- No automatic reliance registry, notification system, timer, concurrency control, or enforcement capability is claimed without source and independent test evidence.
- All adversarial cases are converted into fixtures and executed only after schema freeze and explicit authorisation.

## 10. Disposition

This artefact proposes a coherent FLAG/CORRECTION design for Remmy's whole Dictionary 0.2 reconciliation. It does not approve the final schema, establish implementation, amend historical records, authorise validator construction, authorise formal replay, or reopen the pilot.

**EXON remains the governing name. The pilot remains paused.**
