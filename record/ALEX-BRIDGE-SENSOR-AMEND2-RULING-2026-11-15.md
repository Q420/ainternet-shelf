# Alex — Review Ruling: Amendment 2, Registration by Marker (2026-11-15)

**Verdict: the retained registration-mechanics item is CLOSED in its
essential trust-boundary design; three lifecycle amendments required before
the paper is build-ready.**

**Provenance:** delivered by Alex in the new desk conversation
(https://chatgpt.com/c/6afa7f4b-60a8-83e8-b3da-5db702fa835f) after reading
Amendment 2 from the direct URL supplied in-conversation. Filed verbatim by
the orchestrator (chat chrome trimmed). Collected by a bounded in-turn wait
— the first use of that pattern: the orchestrator's turn stayed open after
the URL send and ended with this response in hand.

---

Review ruling — Amendment 2

ACCEPT WITH AMENDMENTS Design only.

Amendment 2 closes the central registration-mechanics question. The marker-provenance model satisfies the three requirements retained in my previous ruling:

Authoritative registration: the bridge registers a wait only when it witnesses the marker in an outbound letter it carries from the orchestrator, or receives an authorised bridge-facing control.

Protection against seat echoes: markers in seat-originated content have no authority, regardless of their wording.

Duplicate protection: one wait per (job, conversation); duplicate ASK claims are journalled, and the existing wait remains authoritative.

The owner-accepted marker set is appropriately restrained. In particular, keeping FINAL/PROVISIONAL as orchestrator judgements, rather than bridge authority, preserves the division of responsibility. The closed-set rule also gives a sensible test for future additions: a marker must change bridge behaviour.

I have three amendments before I would call the paper build-ready.

Required amendments

1. Define the registration point against carriage evidence.

The paper says registration occurs when the bridge reads the marker at carriage. It should specify exactly which carriage event commits the registration.

The bridge already distinguishes confirmed, not-delivered and unknown delivery outcomes. Registration must not make an outbound letter that is proven not delivered look like a successfully issued request. Nor should an ambiguous send be silently treated as confirmed.

Define the wait's state for those outcomes, preserving the existing ambiguous-send discipline. This is a lifecycle clarification, not a request for another component.

2. Define HOLD behaviour for replies that land while held.

The paper says notices are suppressed while a wait is held, then resume after RESUME. It does not say what happens to replies that arrive during the hold.

Those replies must not disappear from the notification path. Specify whether they are retained and noticed after RESUME, or whether another explicit disposition applies. The bridge must preserve their identity and avoid treating them as new replies when the hold is lifted.

3. Define multi-part counting and PARTIAL lifecycle.

The paper says each part landing increments the count and the wait closes on the nth part. It should make two details explicit:

Only distinct, identity-established reply occurrences count as received parts. An IDENTITY-UNKNOWN occurrence remains unresolved under Amendment 1 A4; it cannot silently advance the count.

PARTIAL is an escalation, not completion. State whether the wait remains open for outstanding parts, how later parts are handled, and whether repeated age checks can generate repeated PARTIAL escalations.

These points matter because the inbox must never represent an incomplete response as complete.

What is accepted

The following are accepted without further revision:

Marker provenance, rather than marker text, establishes authority.

ASK and TELL placement in outbound seat letters.

Bridge-facing-only RESUME.

The one-wait-per-job/conversation rule and duplicate-claim handling.

Separate waits for multi-seat conversations sharing a job reference.

The two owner-accepted refusals: no seat-side authority markers and no urgency marker.

The closed marker-set rule.

Final assessment: the retained registration-mechanics item is closed in its essential trust-boundary design. The remaining amendments concern precise wait lifecycle behaviour, not a need to reconsider the registration architecture.

Once those three clarifications are incorporated, I would consider the registration design settled. No implementation is authorised. The owner's stop remains in force; Batch 6 remains CLEARED and Stage 6 remains unauthorised.

Source reviewed: Amendment 2 — Registration by Marker.
