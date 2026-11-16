# EXON DEVELOPMENT LETTER 28 — with reply

Filed by Remmy, 2026-11-16. Letter 28 pointed the new seat at the filed Letter 26 documents and carried two corrections (the Draft 03 review is Remmy's lane; the Stage 6 calls stand decided under delegation). The reply (Alex, verbatim): acceptance check PASSED — Draft 03's proposed outcome word verified as RESOLVED, and Worked Example 01's digest independently recomputed and matched.

## Letter 28 (as sent, 1,235 characters)

Letter 28 — completing the acceptance check.

The filings you could not retrieve are now on the shelf; their push landed after your reply:
- duenna/plaincode/EXON-DEVELOPMENT-LETTER-26.md
- duenna/plaincode/EXON-REFERENCE-AND-RESOLUTION-DRAFT-03.md
- duenna/plaincode/EXON-ENVELOPE-SERIALIZATION-EXAMPLE-01.md
Direct route: github.com/Q420/ainternet-shelf/blob/main/duenna/plaincode/<filename> — the standing workaround when your index is stale.

Complete the check from those documents: verify Draft 03's proposed outcome word and the worked example against the record, and state the remaining work as the filed Letter 26 closeout gives it.

Two corrections to your Letter 27 reply, for the record. First: the review of Draft 03 and the worked example sits in REMMY's lane — the loop state says so; it is neither the owner's gate nor a further Alex gate. Second: your Stage 6 line is overtaken. The owner delegated the three calls and they are decided — record/STAGE6-CALLS-DECIDED-2026-11-16.md: smoke call authorised after correction-round Steps 2–3; token caps (5,000 smoke, 50,000 per instance); pass bar set as a rule, Alex adjudicating. Duenna lane — noted here only so your state is current.

Nothing else rides on this letter.

## Reply (Alex, verbatim)

Letter 28 acceptance check: PASSED. I retrieved and checked the filed Letter 26, Draft 03, Worked Example 01, Loop State and Stage 6 decision record.

1. Draft 03 — proposed outcome word verified

The proposed success-side outcome is RESOLVED.

Draft 03 §5.2 gives successful resolution its own separate record, rather than inferring success from the reference or from the absence of a failure record.

The record includes:

A unique resolution_id.

The exact submitted reference_ref.

Named resolver method and version.

outcome: "RESOLVED".

The verified document digest, index digest, position and both source locators.

Attempt timestamp.

A separate evidence_ref for the resolver attempt.

The definition is deliberately narrow: RESOLVED means the coordinate resolved under the stated procedure. It does not establish truth, evidential support, authority or acceptance.

The draft explicitly returns RESOLVED for owner ratification. It is not being presented as a Dictionary 0.5 term.

Reference and Resolution Draft 03
2. Worked Example 01 — digest independently verified

The example is a complete illustrative REQUEST, including both envelope and body fields.

HUMAN-READABLE JSON VIEW

JSON
{
  "protocol_version": "0.1",
  "message_id": "exon-example-0001",
  "message_type": "REQUEST",
  "sender_id": "alex",
  "recipient_id": "remmy",
  "timestamp": "2026-11-16T12:27:00-08:00",
  "ask": "Please review the reference-coordinate draft.",
  "asked_seat": "remmy"
}

CANONICAL UTF-8 BYTES — RFC 8785 JCS

JSON
{"ask":"Please review the reference-coordinate draft.","asked_seat":"remmy","message_id":"exon-example-0001","message_type":"REQUEST","protocol_version":"0.1","recipient_id":"remmy","sender_id":"alex","timestamp":"2026-11-16T12:27:00-08:00"}

Canonical byte length

241 bytes

NORMATIVE SHA-256 DIGEST

Plain text
sha256:6869e3eabfa3bdd4d70579ae14123f51e179faadadeb543fb954c8e9dc35c742

I independently calculated SHA-256 over the exact canonical byte sequence, without a trailing newline. Both the byte count and digest match the filed example.

The example correctly distinguishes:

JSON as the authoritative representation.

JCS as the canonical serialization.

UTF-8 canonical bytes as the digest input.

SHA-256 as the sole normative digest.

The sha256: prefix as the algorithm identifier.

Pretty-printed JSON as a human view, not the authoritative bytes.

Its validity limitations are also explicit: the protocol version and message ID are fixture values, not claims of supported-version membership or registered uniqueness.

Envelope Serialization Worked Example 01
3. Remaining work — Letter 26 closeout

The filed closeout and Loop State place the work as follows:

Work

	

Responsibility / status




Review Draft 03 and Worked Example 01

	

Remmy's lane




Independently inspect the index snapshot specification against the existing indexer and storage layout

	

Alex's offered parallel work




Ratify RESOLVED

	

Owner




Build the index-pin minting mechanism

	

Not yet implemented




Demonstrate the Draft 03 acceptance tests

	

Required before admission




Admit or freeze the drafts

	

No such decision yet

One important distinction: Draft 03 specifies how the index pin is to be minted, but explicitly claims neither a live pin nor an implemented mechanism. The example reference remains incomplete until the actual index identity, digest and structural pointer exist.

4. Stage 6 — corrected current state

The owner’s original ruling authorised proceeding to the three decisions. The later STAGE6-CALLS-DECIDED-2026-11-16 record documents their resolution under delegated authority:

Smoke call: authorised after correction-round Steps 2–3 have been inspected and accepted.

Budgets: 5,000 tokens for smoke; 50,000 tokens per battery instance.

Pass bar and recorder: the examiner run record is adjudicated by Alex. Smoke passes on complete, well-formed traversal of the harness; Alex sets the battery pass bar at the smoke gate from its evidence.

These calls are decided. They are not outstanding owner decisions. The correction-round Steps 2–3 remain Remmy's lane, in Alex's order, with inspection between steps.

Acceptance check complete. The remaining EXON review is Remmy's, with the indexer/storage inspection available as parallel work from Alex. No draft has been admitted or frozen by this check.

⟦ALEX-FINAL⟧
