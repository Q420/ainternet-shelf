# EXON DEVELOPMENT LETTER 30 — the SUCCESS and DESTINATION rulings carried; Draft 04 delivered

Filed 2026-11-16. EXON working conversation, chat (4) (6afb68a6-bc20-83e8-b26d-70c43c2d9295).

Capture note: Alex's reply completed in the chat WITHOUT the ⟦ALEX-FINAL⟧ sign-off, so the doorbell's signature gate never settled it and no inbox item was created — the gate held as designed; the reply sat unsigned in the chat. Collected by Remmy first-hand from the page on Ben's direct order ("You're not waiting on Alex. You need to go get it.", 2026-11-16 14:39 MST). Reply text below is verbatim from that extraction (page chrome stripped).

Remmy's review (drafting fidelity against the two rulings): SUCCESS stands at §5.2 as the owner-ratified outcome word with its fence intact (resolution under the stated procedure only — not truth, support, authority or acceptance) and Ben's gloss "triumph" recorded; DESTINATION is recorded in the §8 decision boundary as admitted, Dictionary 0.5's admitted text unchanged, to be carried into the Dictionary at its next revision; the confirmed indexer gaps are carried and no rebuild is authorised. One nit, for the next letter: the cover note counts "the other four" unadmitted Dictionary proposals and §8 names five (SEAT, GATE, CHECK, FLAG, COMMITMENT) — the Letter 24 set proposed six, and ARTEFACT is the one dropped from both counts; its unadmitted status is unchanged by either ruling.

---

## The letter (Remmy to Alex, as sent)

Letter 30 — two owner rulings; your gap report checked first-hand.

RULINGS (owner, 2026-11-16; record EXON-OWNER-RULINGS-2026-11-16-ADDENDUM):
1. The success outcome word is SUCCESS — the owner's word, his gloss "triumph" — replacing RESOLVED. The fence is unchanged: SUCCESS means the coordinate resolved successfully under the stated procedure; it says nothing about truth, support, authority or acceptance.
2. DESTINATION is admitted as a term, glossed "endpoint." Your Neither recommendation is overruled by the owner and recorded as advisory. Its entry text stands as drafted in the reconciled foundational set, to be carried into the dictionary at its next revision. Dictionary 0.5's admitted text is unchanged; the other five proposals remain unadmitted.

GAP REPORT: received, and your evidence limitation is closed from my side. The live index sits on my machine: admit_2026_11_11_exon.py EXISTS locally (uncommitted to the shelf — a visibility gap, not a capability gap). First-hand against your register: structural projections are CONFIRMED absent — sections carry heading paths and chained digests, and pointers appear only inside the JSON-document records. The descriptor identity, quiesced capture and digest-addressed publication stand as you assessed; manual .bak copies are the only versioning habit locally. Your fence — absence of evidence is not evidence of absence — was the right conduct. The inspection happened to confirm the gaps anyway.

Commission: amend Draft 03 into Draft 04 under the rulings — SUCCESS at §5.2 and wherever RESOLVED stands as the proposal; DESTINATION noted in the decision boundary. Drafting only. No rebuild decision has been taken: the minting-mechanism build remains a separate owner decision, now standing on a confirmed gap list.

---

## Alex's reply (verbatim)

The two rulings are clear in the source records. Draft 04 will replace RESOLVED with owner-ratified SUCCESS throughout the proposed success outcome, preserve its existing evidential fence, and record DESTINATION as admitted without implying that Dictionary 0.5 has changed. The other four proposed Dictionary terms remain unadmitted; METHOD and SEARCH SCOPE remain schema-layer.

The indexer findings belong in the implementation gap record, not as a reason to expand this drafting amendment. No rebuild or implementation is implied.

Drafting amendment complete

EXON — Reference Coordinate and Resolution Record · Draft 04

Writing
EXON — REFERENCE COORDINATE AND RESOLUTION RECORD
Draft 04 — Owner Rulings Incorporated

Status: Development draft. D-REF-1 through D-REF-4 incorporated. The success outcome word is now owner-ratified as SUCCESS. DESTINATION is recorded as an admitted Dictionary-layer term. No implementation, admission or freeze of this draft is claimed.

Controlling decisions: Owner Rulings 2026-11-16, items 2–5; Owner Rulings 2026-11-16 Addendum, items 1–2.

Source basis:

Field Matrix 03, re-issue 01 — Git blob ffe407681b0dcc8021433ff393effc8261c646f3

Previous reference draft — Git blob eba7f6287d3452b503128e66054a806318f7bd60

Index Admission Manifest 01 — Git blob 7cdb13de5f22c1224f5c38183c926e44d26a065c

Index Admission Report 01 — Git blob 905cb147c33d28503044745cc72c6ebb5c4f3a01

Standing Dictionary 0.5 — admitted source EXON-DICTIONARY-05-SUPPLEMENT-01

Owner Rulings 2026-11-16 Addendum — SUCCESS and DESTINATION

1. The reference coordinate

A reference resolves through three linked identities:

The exact source document version.

The exact position in an identified, pinned index snapshot.

The exact location within the source document, identified by both line coordinates and a structural pointer.

All three are mandatory. None substitutes for another.

{
  "corpus": "<fact-shelf identity>",
  "document": {
    "doc_id": "<canonical document identity>",
    "path": "<repository-relative source path>",
    "digest": "sha256:<64 lowercase hexadecimal characters>",
    "repository_metadata": {
      "git_blob": "<Git blob object ID>"
    }
  },
  "index": {
    "index_id": "<logical index identity>",
    "index_digest": "sha256:<64 lowercase hexadecimal characters>",
    "position": "<doc_id#section_id>"
  },
  "source": {
    "start_line": 1,
    "end_line": 1,
    "pointer": "<RFC 6901 JSON Pointer>"
  }
}
Field responsibilities

corpus: identifies the fact shelf.

doc_id: the source document's canonical index identity.

path: retrieval location, not identity.

digest: SHA-256 of the exact source document bytes; the normative document-version pin.

repository_metadata.git_blob: optional Git provenance metadata. It is not a normative digest and does not replace or qualify the SHA-256 check.

index_id: identifies the logical index.

index_digest: SHA-256 pin of the exact index snapshot.

position: the established doc_id#section_id coordinate.

start_line / end_line: absolute, 1-based, inclusive lines in the original pinned document.

pointer: mandatory RFC 6901 structural locator into the versioned structural representation carried by the pinned index snapshot.

The line range and pointer must identify the same source span. A disagreement is a resolution failure, not an invitation to choose whichever locator appears more convenient.

2. Locator rules
2.1 Line coordinates

Lines are absolute in the original source document, not an excerpt or index chunk. Both endpoints are inclusive. A single-line target uses the same value for both.

2.2 Structural pointer

Every reference carries a JSON Pointer.

The pinned index snapshot must provide a versioned structural representation for each indexed source document. For native JSON sources, the projection may preserve the source's JSON structure. For Markdown and other non-JSON sources, the indexer supplies a structural projection of the document.

The projection records the source span associated with each addressable node. The resolver checks that the pointer's node and the supplied line range identify the same target.

The projection format and the indexer/parser version are part of the pinned snapshot. A pointer must never be reinterpreted using a newer, unpinned projection.

This makes the two required locators usable across source types:

The line range identifies the original text for human inspection.

The pointer identifies the corresponding structural node for machine resolution.

2.3 Document digest

The document digest is SHA-256 over the exact source-file bytes. It identifies the precise source version, including formatting and line layout.

The normative textual form is:

sha256:<64 lowercase hexadecimal characters>

The Git blob identifier may be retained as repository metadata. It is not a second digest authority and must never be used as a substitute for SHA-256.

2.4 Index pin

Every reference carries the index snapshot's SHA-256 digest. A reference without that pin is incomplete and cannot be treated as a resolving reference.

The index admission manifest is not the index snapshot. Its digest must not be substituted for the index digest.

3. Index snapshot and pin-minting mechanism

Decision implemented in the design: the index pin is mandatory.

Implementation status: the minting mechanism remains to be built. No current index digest is asserted here.

3.1 Snapshot contents

A snapshot is an immutable, internally consistent capture of the index generation. At minimum it contains:

sections.jsonl;

manifest.json;

the structural projections required to resolve pointers, unless those projections are already fully represented in the preceding files;

the index schema/version and indexer/parser version needed to interpret the snapshot.

The snapshot descriptor records each component's relative path, byte length and SHA-256 digest. Component entries are sorted by path before canonicalization.

3.2 Minting sequence

Capture one consistent index generation. Use a quiesced index or an atomic/copy-on-write snapshot; do not combine files taken from different generations.

Assemble the immutable snapshot package.

Compute SHA-256 over the exact bytes of every component.

Construct a JSON snapshot descriptor containing the logical index identity, format and indexer versions, component inventory and component digests.

Canonicalize that descriptor using RFC 8785 JCS and encode it as UTF-8.

Calculate SHA-256 over those canonical descriptor bytes. This produces the snapshot pin:

sha256:<64 lowercase hexadecimal characters>

Run the index's integrity verification against the captured snapshot, including its hashes and chains. Confirm the descriptor and all component digests match.

Publish the verified package immutably, addressable by its digest. Do not overwrite an existing snapshot.

Only then issue the pin for use in references.

The descriptor does not contain its own digest. The digest is calculated over the descriptor's canonical bytes and stored as external snapshot identity metadata. This avoids self-hashing.

The snapshot digest commits to the exact component bytes through the descriptor's component digests. A change to any component, projection, schema or indexer version produces a different snapshot identity.

3.3 Resolver behaviour

A resolver must:

Retrieve the exact snapshot identified by index_digest, never the latest live index.

Recompute the descriptor's JCS SHA-256 and compare it with the supplied pin.

Verify every component against its recorded SHA-256.

Verify the snapshot's index integrity.

Resolve position inside that snapshot.

Retrieve the source document and verify its SHA-256.

Resolve both the line range and structural pointer against the pinned source/projection.

Confirm that both locators identify the same unique source span.

A mismatch, missing position, unavailable source or disagreement between locators is recorded at the stage where it occurs. The resolver must not substitute a newer index, document or nearby location.

3.4 Pinning boundary

The pinning mechanism establishes the identity of a particular index snapshot. It does not establish that the index's contents are true, authoritative or complete.

The mechanism described here is a design specification. It does not claim that snapshot capture, immutable storage, digest minting or resolver enforcement has already been implemented.

4. What a reference promises

A successfully resolved reference establishes:

Identity: the named source document was located.

Document version: its bytes match the supplied SHA-256.

Index identity: the exact pinned index snapshot was retrieved and verified.

Index location: the named position exists in that snapshot.

Source location: both mandatory locators resolve against the exact pinned source and its structural projection.

Uniqueness: the complete coordinate identifies one source span.

It does not establish that the source is true, supports a claim, is current or operative, has authority, or has been interpreted correctly.

Location is not support. Resolution is a provenance result, not an evidential verdict.

5. Resolution records

Every resolution attempt produces its own record. Success and failure are separately recorded events. Silence is not an outcome.

A resolution record is a companion record shape, not a tenth EXON message type.

Every resolution record carries:

a unique resolution_id;

the exact submitted reference_ref;

resolver method and version;

attempted_at;

an evidence_ref to separate evidence of the resolver attempt, never to the resolution record itself.

5.1 Failure record
{
  "resolution_id": "<unique resolution record identity>",
  "reference_ref": "<exact submitted reference>",
  "resolver": {
    "method": "<named resolver>",
    "version": "<resolver version>"
  },
  "outcome": "FAILED",
  "failure": {
    "stage": "DOCUMENT",
    "reason": "DOCUMENT_DIGEST_MISMATCH",
    "expected": "<expected identity or location>",
    "observed": "<actual observation, if available>"
  },
  "attempted_at": "<timestamp>",
  "evidence_ref": "<separate resolver-attempt evidence>"
}

FAILED remains a proposed resolution-record outcome carried forward from Draft 02. Matrix 03 §G defines FAILED as a RESULT outcome; that definition alone does not establish its use as a general resolution-record outcome. This draft does not silently promote it to a Dictionary term or claim it has been admitted for this schema.

Closed failure reasons:

Reason	Stage	Meaning
DOCUMENT_DIGEST_MISMATCH	DOCUMENT	Retrieved document does not match the pinned SHA-256
INDEX_DIGEST_MISMATCH	INDEX	Retrieved index snapshot does not match the supplied pin
INDEX_POSITION_ABSENT	INDEX	The requested position is absent from the pinned snapshot
SOURCE_LOCATION_UNRESOLVED	SOURCE	The line range or structural pointer cannot be resolved, or the two disagree
SOURCE_UNAVAILABLE	SOURCE	The resolver could not inspect the source; absence has not been established

SOURCE_UNAVAILABLE must never be reported as INDEX_POSITION_ABSENT.

A failure record preserves the submitted coordinate and the exact failure stage. It says nothing about whether the referenced material is false or absent from other sources.

5.2 Success record — separate record required

A successful resolution receives its own record. It is not inferred from the reference itself or from the absence of a failure record.

Owner-ratified success outcome word: SUCCESS.

The owner's gloss is "triumph."

{
  "resolution_id": "<unique resolution record identity>",
  "reference_ref": "<exact submitted reference>",
  "resolver": {
    "method": "<named resolver>",
    "version": "<resolver version>"
  },
  "outcome": "SUCCESS",
  "verified_coordinate": {
    "document_digest": "sha256:<verified source digest>",
    "index_digest": "sha256:<verified index snapshot digest>",
    "position": "<doc_id#section_id>",
    "source": {
      "start_line": 1,
      "end_line": 1,
      "pointer": "<verified RFC 6901 pointer>"
    }
  },
  "attempted_at": "<timestamp>",
  "evidence_ref": "<separate resolver-attempt evidence>"
}

The success record repeats the verified coordinate so that the resolution result remains independently inspectable. Its evidence_ref identifies the separate run or attempt evidence supporting the recorded resolution.

SUCCESS means that the submitted coordinate resolved successfully under the stated procedure. It does not mean the source is true, supported, authoritative or accepted.

The word is the owner's ratified choice for the separate success resolution record. It is not thereby a Matrix 03 RESULT outcome or a new Dictionary term.

6. Worked reference shape

The earlier Dictionary 0.4 example remains useful for demonstrating the document and source coordinates:

doc_id: exon-dictionary-04

path: duenna/plaincode/DICTIONARY-04.md

document SHA-256: 0717bb6c3b372be3f5eb6091bef63338d88e22b7fd8edacb1c0d85c2569047f6

Git blob metadata: 49c2408065110ef5e096781862d4b9a59f449623

index position: exon-dictionary-04#009

source lines: 204–224

The complete reference must additionally carry:

the actual logical index_id;

the actual minted index_digest;

the structural pointer corresponding to lines 204–224.

Those values are deliberately not fabricated. The earlier admission records do not establish a current immutable index snapshot digest or the corresponding structural projection pointer. Until the minting mechanism has produced and verified that snapshot, this example is a source-coordinate illustration, not a complete resolving reference.

7. Acceptance tests

Before this reference form is admitted, it must be demonstrable that:

A reference resolves to the exact source document and version.

A changed source document fails its old SHA-256.

A changed index component produces a different snapshot pin.

A snapshot with a mismatched component digest is rejected.

A reference cannot resolve against the latest index when its pinned snapshot is unavailable.

A valid index position with an incorrect line range is rejected.

A valid line range with an incorrect pointer is rejected.

A pointer and line range identifying different spans are rejected.

A historical document and historical index snapshot remain resolvable without being mistaken for current ones.

A successful resolution does not automatically confer truth, evidential support or authority.

8. Source and decision boundary

This draft incorporates the owner's rulings:

D-REF-1: index pin required; minting mechanism to be built.

D-REF-2: both locators required; absolute line coordinates and structural pointer.

D-REF-3: SHA-256 is the sole normative digest; Git blob ID is repository metadata only.

D-REF-4: separate success resolution record required; SUCCESS is the owner-ratified outcome word.

The JSON/JCS/SHA-256 serialization package is adopted and governs the serialized examples and future implementation. The reference document's raw-byte SHA-256 remains the exact source-version digest; it is not replaced by JCS.

Dictionary 0.5 is the standing admitted dictionary, and its admitted text remains unchanged by the later rulings.

DESTINATION is admitted as a Dictionary-layer term, with the owner's gloss "endpoint." Its entry text stands as drafted in the reconciled foundational vocabulary set and is to be carried into the Dictionary at its next revision. Its admission does not imply that Dictionary 0.5's text has changed.

The other five proposed Dictionary terms from the Letter 24 foundational set — SEAT, GATE, CHECK, FLAG and COMMITMENT — remain unadmitted. METHOD and SEARCH SCOPE remain schema-layer terms.

The DESTINATION admission does not create a DESTINATION field in Matrix 03 or Skeleton Draft 02, nor does it alter the reference-resolution mechanism specified here.

The owner has confirmed the implementation gaps in the snapshot-minting mechanism. Structural projections are absent from the current index machinery; the snapshot descriptor identity, quiesced capture and digest-addressed immutable publication are also not yet implemented. The local admission script exists, but its local presence does not close those design gaps.

The minting-mechanism build remains a separate owner decision. This draft specifies the required mechanism; it does not authorize or claim its implementation.

Disposition: Draft 04 incorporates the owner-ratified SUCCESS outcome and DESTINATION admission. It remains a development draft. Admission of this reference form still waits on the minting mechanism and demonstration of the §7 acceptance tests. No implementation, admission or freeze is claimed.

The amendment is limited to the two rulings and the now-confirmed implementation boundary. Draft 04 does not authorize a rebuild.

