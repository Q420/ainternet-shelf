# EXON — COMMON MESSAGE ENVELOPE — ADOPTED SERIALIZATION, WORKED EXAMPLE 01

Filed by Remmy, 2026-11-16, extracted verbatim from Alex's reply to Letter 26 (see EXON-DEVELOPMENT-LETTER-26.md). The first concrete instance of the adopted serialization package (owner ruling 6, 2026-11-16).

---

EXON — COMMON MESSAGE ENVELOPE
Adopted Serialization — Worked Example 01

Status: Worked serialization example for review. It demonstrates the adopted JSON / RFC 8785 JCS / SHA-256 package. It does not admit or freeze the envelope, syntax skeleton or message body.

Source basis:

Common Message Envelope Draft 01 — Git blob 554fe5465f1d798b9401febcfe6236e91fad4d61

Field Matrix 03, re-issue 01 — Git blob ffe407681b0dcc8021433ff393effc8261c646f3

Serialization Decision Paper 01 — Git blob 5f4a29d6166bc5930cc7d923269db40dfe6ebe42

Owner Rulings 2026-11-16 — serialization item 6

1. Example message

This is a complete illustrative REQUEST message so that the digest covers the entire message, not an isolated envelope fragment.

The sender and recipient use the alex and remmy seat identities. protocol_version and message_id are fixture values only: this example does not assert a supported protocol release or claim that the synthetic message ID has been registered as unique.

Human-readable JSON view
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

The common envelope fields are:

Field	Example value
protocol_version	0.1
message_id	exon-example-0001
message_type	REQUEST
sender_id	alex
recipient_id	remmy
timestamp	2026-11-16T12:27:00-08:00

The REQUEST body fields are:

Field	Example value
ask	Please review the reference-coordinate draft.
asked_seat	remmy

No task context is included because this example does not rely on a task. Optional relation fields and the review marker are omitted.

2. Canonical bytes

RFC 8785 JCS sorts object properties according to its canonicalization rules and emits compact JSON without insignificant whitespace.

The exact canonical UTF-8 byte sequence for this example is the following single line, with no trailing newline:

{"ask":"Please review the reference-coordinate draft.","asked_seat":"remmy","message_id":"exon-example-0001","message_type":"REQUEST","protocol_version":"0.1","recipient_id":"remmy","sender_id":"alex","timestamp":"2026-11-16T12:27:00-08:00"}

Canonical byte length: 241 bytes.

3. Normative digest

The digest is SHA-256 over those exact canonical UTF-8 bytes.

sha256:6869e3eabfa3bdd4d70579ae14123f51e179faadadeb543fb954c8e9dc35c742

The digest is external to the message. It is not inserted into the object whose bytes it hashes.

4. Interpretation

JSON is the authoritative data representation.

RFC 8785 JCS produces the canonical serialization.

UTF-8 encoding of those canonical bytes is the digest input.

SHA-256 is the sole normative digest algorithm.

The sha256: prefix explicitly identifies the algorithm.

Canonical bytes are authoritative. The pretty-printed JSON above is a human-readable view only.

The digest covers the complete message, including both envelope and body fields.

A formatting-only change to the human view does not change the digest if the structured data remains identical and JCS produces the same canonical bytes. A change to any message value changes the canonical bytes and therefore the digest.

5. Scope and validity boundary

This example demonstrates serialization and digest calculation. It is not a claim that the message passes every EXON FORM check.

In particular:

protocol_version is illustrative and has not been asserted to be a supported version.

message_id is synthetic; uniqueness enforcement remains a separate programme invariant.

The timestamp is an example string, not a decision on timestamp syntax or precision.

The example does not establish any authority or evidential conclusion.

The serialization ruling settles the representation and hashing package. It does not silently settle those separate matters.
