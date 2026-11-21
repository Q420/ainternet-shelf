# EXON — Authority Precedent Study (input paper, 2026-11-16)

**Provenance:** Pasted by the owner into the main chat on
2026-11-16 and filed beside the Dictionary Chart as an input
paper, per his tap. The text arrived from a ChatGPT surface
(its reference links carry chatgpt.com tags); the authoring
seat is not identified on the record, and the study is filed
as pasted — an input to the chart workstream, not a ruling.
Table spacing normalised in filing; wording unchanged.

**Verification note (Remmy, before filing):** the study's one
claim about EXON's own texts was checked against them. The
field matrix does carry `authority_ref` — legal for RULING,
ACCEPT, DELEGATION, STOP, REGISTER_TASK and CORRECTION, and
required on RULING, DELEGATION, REGISTER_TASK and CORRECTION
(FIELD-MATRIX-01, FORM rule "resolves; scope check is
MEANING") — and Dictionary 0.4's AUTHORITY is already
grant-shaped: "The recorded right of a named seat to perform
a named class of act within a named scope." The study's
closing qualification therefore holds: the proposed model
builds on the existing design.

---

### Side-by-side comparison

The most useful precedents are SecPAL, XACML, NIST's Role-Based Access Control model (RBAC), and W3C PROV-O. They solve different parts of the problem.

| Design question | SecPAL | XACML | NIST RBAC | PROV-O |
| --- | --- | --- | --- | --- |
| Who holds authority? | Principal | Subject | User / role | Agent |
| What establishes authority? | Rights and credentials | Attributes and policies | Role assignment | Recorded relationships |
| What may they do? | Granted rights | Policy decision | Role permissions | Not its purpose |
| Can authority be delegated? | Yes, explicitly | Not its central model | Not its central model | Yes, records delegation |
| Can hierarchy exist? | Through rules | Through policy | Explicit role hierarchy | Not its purpose |
| Can origin be traced? | Credential chain | Policy issuer | Role assignment | Provenance chain |
| Can authority be time-sensitive? | Through constraints | Through environmental attributes | Requires additional policy | Entity/activity lifecycle |

Sources: microsoft.com +3

### What EXON should adopt

### 1. SecPAL: adopt the grant-and-delegation model

A grant should identify the authority holder, the rights granted, the scope, and whether those rights can be delegated.

Adopt: explicit authority provenance and bounded delegation.

Avoid: allowing a delegated authority to become broader than the authority from which it originated.

Reference: [Microsoft Research — SecPAL](https://www.microsoft.com/en-us/research/publication/secpal-design-semantics-decentralized-authorization-language/?utm_source=chatgpt.com).

### 2. XACML: adopt the action-specific decision model

Authority should be evaluated against a particular action and target, rather than assuming that a person's position automatically permits every action.

Adopt: subject + action + scope + applicable policy → decision.

Avoid: treating a person's authority level as sufficient proof of permission.

XACML's four decision outcomes are particularly useful: Permit, Deny, Indeterminate and NotApplicable. docs.oasis-open.org +1

Reference: [OASIS XACML 3.0](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html?utm_source=chatgpt.com).

### 3. NIST RBAC: adopt hierarchy cautiously

RBAC supports role hierarchies, where a senior role can inherit permissions from a junior role.

Adopt: the ability to define recognised authority levels and role relationships.

Avoid: assuming that every higher level automatically inherits every lower-level permission. That inheritance must be explicitly defined. CSRC +1

Reference: [NIST — Role-Based Access Control](https://csrc.nist.gov/projects/role-based-access-control/faqs?utm_source=chatgpt.com).

### 4. W3C PROV-O: adopt provenance tracking

PROV-O distinguishes agents, activities and entities, and provides relationships for attribution, derivation and delegation.

Adopt: the ability to trace who was responsible for an action and which authority relationship influenced it.

Avoid: treating provenance as proof that an action was authorised. Recording who did something does not establish that they had permission. w3.org

Reference: [W3C PROV-O](https://www.w3.org/TR/prov-o/?utm_source=chatgpt.com).

### Proposed EXON structure

I would keep the dictionary small and put most of the machinery into structured fields and referenced records.

Authority grant record

| Field | Purpose |
| --- | --- |
| principal | Who holds the authority |
| authority_level | Recognised authority classification |
| authority_scope | Which actions and subjects are covered |
| authority_ref | Exact source grant or record |
| delegated_from | Origin of delegated authority |
| delegation_limit | Whether, and how far, authority may be delegated |
| effective_from | When the grant becomes operative |
| effective_until | When it expires, if applicable |
| revocation_ref | Record establishing revocation, if applicable |

Authority decision record

| Field | Purpose |
| --- | --- |
| principal | Actor seeking to perform the act |
| action | Proposed or performed action |
| scope | Target of the action |
| authority_ref | Grant relied upon |
| decision | Permit / Deny / Indeterminate / NotApplicable |
| decision_ref | Record of the decision |
| decision_at | Time at which authority was evaluated |

This is a proposed design, not an assertion that the current EXON schema already supports these fields.

### The important distinction: level versus permission

Consider three people:

* Level 1: researcher.

* Level 2: project lead.

* Level 3: programme owner.

The project lead might be allowed to approve research, but not to authorise programme-wide execution. The programme owner might hold both powers.

A simple hierarchy would say Level 3 is above Level 2. It would not, by itself, explain which actions each can authorise.

The permission model does.

And this gives us a useful test case:

A person may have sufficient authority in general, but lack authority for this particular action.

EXON must be able to represent that without contradiction.

### Dictionary consequences

My recommendation for the existing four categories:

| Candidate | Recommended treatment |
| --- | --- |
| AUTHORITY | Keep |
| DELEGATION | Keep |
| RULING | Keep |
| AUTHORISE | Consider adding only if distinct from RULING |
| AUTHORITY_LEVEL | Structured field, not initially a dictionary term |
| PERMISSION | Structured concept or schema value |
| GRANT | Consider as an explicit authority act |
| REVOKE | Consider as an explicit authority act |
| SCOPE | Structured field |
| PERMIT / DENY | Decision values, not necessarily dictionary terms |

I would also keep `ACCEPT` separate from an authority decision. Accepting an artefact against criteria and permitting an actor to perform an action are fundamentally different operations.

### My conclusion

I would take the following design direction into the EXON chart:

* Use hierarchy to classify authority, not to determine every permission automatically.

* Use explicit grants to establish rights.

* Use scope to restrict those rights to particular actions and subjects.

* Use delegation records to preserve the chain of authority.

* Evaluate authority at the time of the action.

* Keep the decision to authorise separate from the record of the action actually performed.

That last distinction is essential. An authorisation record does not prove execution, and an execution record does not prove valid authorisation.

One important qualification: the current EXON Field Matrix already has `authority_ref` for RULING, DELEGATION, REGISTER_TASK and CORRECTION. The proposed model should build on that existing design rather than introduce a competing authority system.

The strongest design lesson from these precedents is that authority is a relationship with boundaries and provenance, not simply a number in a hierarchy.
