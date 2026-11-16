# EXON — REFERENCE COORDINATE AND RESOLUTION RECORD — DRAFT 02

Item 3 · Queue two · Drafted by Remmy · For Alex's review

Revision (Draft 02, 2026-11-16): per Alex's review
(Development Letter 16 reply) — the D-REF-3 flag is
carried into the worked example; the FAILED reuse in
section 4.1 is marked PROPOSED, not adopted, and the
question is added to the owner list as D-REF-4;
evidence_ref is disambiguated. No other change.

Sources: the reference-form proposal (Development Letter
06, Alex) and the failed-resolution addition with the
live-index inspection (Development Letter 07, Alex),
under the owner's design ruling of 2026-11-16: the EXON
shelf is the glossary and index of the fact shelf; every
solidified entry carries its source coordinates.

Status: Draft, to final shape EXCEPT the owner
decisions (three from Letters 06–07; a fourth, D-REF-4,
added in Draft 02 per Alex's ruling). Wherever a decision bites, the shape carries
an explicit ⟦OWNER DECISION — PENDING⟧ flag and states
the options; nothing is assumed. The record shapes below
are presented in YAML-like notation as shapes, not as
EXON syntax — serialization itself is before the owner
in the serialization decision paper. No admission,
freeze or implementation is proposed.

---

## 1. The reference coordinate

A reference resolves through three linked coordinates:
the exact source document version; its exact position in
a named, pinned index; its exact location within the
original document. All three are necessary. None
silently substitutes for another.

```
REFERENCE:
  corpus: <fact-shelf identity>

  document:
    doc_id: <canonical document identity>
    path: <repository-relative source path>
    digest:
      algorithm: SHA-256            ⟦D-REF-3⟧
      value: <digest of the pinned content>
    git_blob: <Git blob object ID>   (cross-check; §2.3)

  index:
    index_id: <index identity>
    index_digest: <pinned index digest>   ⟦D-REF-1⟧
    position: <doc_id#section_id>

  source:
    locator_type: LINE | JSON_POINTER
    start: <absolute source line>         ⟦D-REF-2⟧
    end: <absolute source line>           ⟦D-REF-2⟧
    pointer: <RFC 6901 pointer>           (JSON_POINTER only)
```

Field responsibilities: corpus — which fact shelf holds
the source. doc_id — the document's canonical index
identity. path — where it is stored (a retrieval aid,
not identity). digest — the exact content version; the
controlling pin. git_blob — the corresponding Git
object, an independent repository cross-check.
index_id — the index consulted. index_digest — the exact
index version. position — the document's section in that
index, in the established doc_id#section_id form.
source — the exact location in the original document.

## 2. Coordinate rules

2.1 Lines. Numbered from 1. start and end are absolute
lines in the original pinned document; both endpoints
inclusive; a single line uses the same value twice.
These are never line numbers in a retrieved excerpt or
index chunk. (RFC 5147 precedent, adapted: EXON states
its own 1-based convention rather than adopting the
RFC's zero-based positions.)

2.2 Pins do not move. The document digest makes the
coordinate version-specific: if the document changes,
the old coordinate continues to identify the old version
and fails against the new content. A resolver must never
silently substitute a newer document, index or nearby
location.

2.3 Digests are not interchangeable. A Git blob ID is
not a raw-file SHA-256: Git object identifiers
incorporate object type and size as well as content.
The blob is retained as a cross-check, never as the
content digest. ⟦D-REF-3 decides whether it remains
normative metadata or optional.⟧

2.4 Structured sources. For JSON and other structured
documents, locator_type JSON_POINTER names the
structural object using RFC 6901, including its escaping
rules; no EXON vocabulary is created for it.
⟦D-REF-2 decides whether the line range remains
mandatory alongside the pointer, or the pointer alone
suffices for structured sources.⟧

## 3. What a coordinate promises

A valid reference promises exactly:
- Identity: the named document can be resolved.
- Version: the retrieved content matches the pinned
  digest.
- Index location: the named section exists in the
  pinned index.
- Source location: the locator resolves inside that
  exact document version.
- Uniqueness: the complete coordinate identifies one
  source location, not an ambiguous collection.

It does NOT promise: that the source is true; that it
supports the claim being made; that it is current or
operative; that it has authority; that the
interpretation drawn from it is correct.

Location is not support. The reference is a provenance
mechanism, not an evidential verdict.

## 4. The resolution record

Every resolution attempt is recorded — success or
failure. Silence is not an outcome.

### 4.1 Failure (specified in Letter 07)

```
REFERENCE_RESOLUTION:
  reference_ref: <the submitted coordinate>
  resolver:
    method: <named resolver>
    version: <resolver version>
  outcome: FAILED
  failure:
    stage: DOCUMENT | INDEX | SOURCE
    reason: <closed code, below>
    expected: <expected identity or location>
    observed: <actual observation, if available>
  attempted_at: <timestamp>
  evidence_ref: <the resolver's attempt evidence — the
    run record evidencing this attempt; NOT this
    resolution record itself>
```

Closed failure codes:
- DOCUMENT_DIGEST_MISMATCH — retrieved document does
  not match the pinned digest. (stage: DOCUMENT)
- INDEX_DIGEST_MISMATCH — retrieved index does not
  match the pinned index identity. (stage: INDEX)
- INDEX_POSITION_ABSENT — the requested position is
  absent from the pinned index. (stage: INDEX)
- SOURCE_LOCATION_UNRESOLVED — the document resolves
  but the line range or structural locator does not.
  (stage: SOURCE)
- SOURCE_UNAVAILABLE — the resolver could not inspect
  the source; absence has NOT been established.
  (stage: SOURCE)

Fences: the record preserves the submitted coordinate
and the exact stage of failure. FAILED describes the
resolution attempt — never the referenced material: it
does not establish that the material is false, absent
from every source, or invalid for every purpose.
SOURCE_UNAVAILABLE must never be reported as
INDEX_POSITION_ABSENT.

STATUS — UNRESOLVED: the FAILED reuse is PROPOSED, not
adopted. Letter 07 offered this shape as a proposal and
said so; FAILED is defined in Matrix 03 section G as a
RESULT outcome, which does not by itself establish a
resolution-record outcome. Whether the resolution
record carries its own schema-level outcome semantics
is owner decision D-REF-4 (section 5).

### 4.2 Success — FLAGGED OPEN

Letters 06–07 specify the failure record; the success
record's outcome word is NOT settled there. A success
record minimally carries: reference_ref, resolver
(method + version), attempted_at, and the verified
coordinate (document digest as retrieved, index
position as found, source location as resolved). This
draft does not invent a success token. Alex's ruling
(Letter 16 reply): returned to the owner — a design
choice, not a reviewer-level wording correction. It is
owner decision D-REF-4 (section 5), the same decision
that governs the FAILED reuse in 4.1.

## 5. The owner decisions (flagged, not assumed)

D-REF-1 — INDEX PIN. Does every reference carry the
index snapshot's digest, or does the position resolve
through a separately pinned index manifest?
Alex's recommendation (Letter 06): require the pin in
the reference. Consequence, from the Letter 07
inspection: NO live index pin exists today — the
published records establish document admission and
run-time verification, not a live snapshot identity.
Either option therefore requires BUILDING the pinning
mechanism before references can be carried in this
form. Until the owner rules, index_digest above is a
flagged field, not a fillable one.

D-REF-2 — LOCATOR POLICY. Are line coordinates
mandatory even when a JSON Pointer is supplied, or may
a structural locator alone suffice for some source
types? Alex's position (Letter 06): retain both when
available — structural and human-readable coordinates
without competing. Until the owner rules, start/end are
carried in the shape marked ⟦D-REF-2⟧.

D-REF-3 — DIGEST POLICY. Is SHA-256 the sole normative
document digest, with Git blob identity retained as
optional repository metadata? Alex's recommendation
(Letter 06): yes. Until the owner rules, the digest
block names SHA-256 as the working algorithm, flagged.

D-REF-4 — RESOLUTION-RECORD OUTCOME SEMANTICS (added
Draft 02, per Alex's Letter 16 ruling). Does the
resolution record carry its own schema-level outcome
semantics? If yes: the FAILED reuse in 4.1 is validated
as proposed, and the success side needs an explicitly
chosen outcome representation in a separate success
record. If no: the resolved reference's own citation
suffices and no separate success record exists. Alex
returned this to the owner rather than inventing a
token; the FAILED reuse stays visibly proposed until
it is ruled.

## 6. Worked example (real, except where flagged)

Dictionary 0.4, evidence-and-reference section:

```
REFERENCE:
  corpus: Q420/ainternet-shelf

  document:
    doc_id: exon-dictionary-04
    path: duenna/plaincode/DICTIONARY-04.md
    digest:
      algorithm: SHA-256            ⟦D-REF-3⟧
      value: 0717bb6c3b372be3f5eb6091bef63338d88e22b7
             fd8edacb1c0d85c2569047f6
    git_blob: 49c2408065110ef5e096781862d4b9a59f449623

  index:
    index_id: <pinned corpus index>        ⟦D-REF-1⟧
    index_digest: <UNRESOLVED — not invented>
    position: exon-dictionary-04#009

  source:
    locator_type: LINE
    start: 204
    end: 224
```

The document digest was computed by Remmy on 2026-11-16
from the local canonical copy after verifying that copy's
Git blob equals the recorded 49c24080… — the digest is
therefore the pinned document's own. The index fields
remain placeholders for the reason Letter 06 stated: no
published record establishes the live index snapshot's
digest, and this draft does not invent one.

## 7. Acceptance test (from Letter 06)

Before this form is admitted, it must be demonstrable
that: a reference resolves to the exact document and
version; a changed document fails the old digest check;
a changed index fails the old index pin; a valid index
position with an incorrect source line is rejected; a
reference to a historical document remains resolvable
without being mistaken for the current candidate; and a
successful resolution does not automatically confer
evidential support.

## 8. Borrowing register

Git object model — immutable content-addressed identity
(blob as cross-check). SHA-256 — explicit content
integrity digest (document pin). RFC 5147 — line/range
location plus integrity (adapted to 1-based lines).
RFC 6901 — structured location within JSON (reused, not
re-vocabularised). Existing shelf index — doc_id#section_id
position form (retained). No external standard is adopted
as EXON's complete grammar.

## 9. Source boundary

Sections 1–3 and 7–8 restate Letters 06–07 without
alteration of substance; section 4.1 is Letter 07's
shape verbatim in substance; 4.2, the decision flags
and D-REF-4 (per Alex's Letter 16 ruling) are this
draft's additions, each marked. Nothing here decides
D-REF-1, D-REF-2, D-REF-3 or D-REF-4, and nothing is
admitted or frozen.

— Remmy, 2026-11-16. Draft for Alex's review.
