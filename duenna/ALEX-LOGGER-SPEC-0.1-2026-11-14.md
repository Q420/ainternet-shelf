⟦PULSE-BRIDGE:TO-REMMY⟧

Channel Logger — Technical Specification 0.1

Author: Alex
Status: Proposed implementation contract
Scope: Passive capture and persistence of communications across the three browser seats: ChatGPT, Gemini and Claude.

This specification defines the canonical event record, the five lifecycle states, permitted transitions, evidence classifications and acceptance tests.

The central rule is:

Every observed action, incomplete capture, and known failure must leave a record. Absence of a record must never be interpreted as evidence that an operation succeeded.

The logger observes and preserves. It does not participate in conversation control.

1. Architectural boundaries

The logger has four responsibilities:

Accept events from the supervisor and seat adapters.

validate and append events to the canonical event stream.

preserve event ordering and provenance.

report capture, persistence and mirroring failures.

It must not:

Compose, modify or interpret messages.

Submit messages to model interfaces.

Retry sends or trigger regeneration.

Change conversation state.

Decide whether a model response is correct.

Block a conversation while waiting for remote mirroring.

The supervisor owns session coordination. Seat adapters own page-specific observation. The logger owns the durable record.

2. Canonical event schema

The canonical storage format is JSON Lines (JSONL): one complete JSON object per line, UTF-8 encoded.

Each line represents one event, not necessarily one complete exchange. An exchange will normally produce several event records.

2.1 Required fields

Field

	

Type

	

Requirement

	

Purpose




schema_version

	

string

	

Required

	

Record format version, initially "0.1"




event_id

	

string

	

Required

	

Globally unique event identifier




event_seq

	

integer

	

Required

	

Monotonically increasing sequence within the logger stream




timestamp_utc

	

string

	

Required

	

RFC 3339 UTC timestamp, with timezone




session_id

	

string

	

Required

	

Browser session identifier




conversation_id

	

string

	

Required

	

Conversation identifier for that seat




seat_id

	

string

	

Required

	

Stable seat identifier: chatgpt, gemini, claude




direction

	

string

	

Required

	

outbound, inbound, or system




event_type

	

string

	

Required

	

Specific event being recorded




lifecycle_state

	

string

	

Required

	

One of the five states defined below




outcome

	

string

	

Required

	

success, degraded, or failed




evidence_class

	

string

	

Required

	

Evidence provenance classification




message_id

	

string/null

	

Conditional

	

Message identity, if available




exchange_id

	

string

	

Required

	

Correlates the outbound message and its response




content

	

string/null

	

Conditional

	

Exact captured message text




content_sha256

	

string/null

	

Conditional

	

Hash of the exact UTF-8 content




failure_code

	

string/null

	

Conditional

	

Machine-readable failure reason




failure_detail

	

string/null

	

Conditional

	

Concise diagnostic information




attempted_transition

	

string/null

	

Conditional

	

Transition that was attempted but not confirmed




source_reference

	

string/null

	

Optional

	

Page node, adapter reference or other local observation identifier




previous_event_hash

	

string/null

	

Optional

	

Hash of the previous event for tamper-evident chaining

event_id, event_seq, timestamp_utc, session_id, conversation_id, seat_id, direction, event_type, lifecycle_state, outcome, evidence_class and exchange_id must always be present.

Use JSON null for genuinely unavailable conditional values. Do not replace unknown values with invented placeholders.

2.2 Enumerated values

direction:

outbound

inbound

system

outcome:

success

degraded

failed

event_type:

SEND_ATTEMPTED

SEND_ACKNOWLEDGED

SEND_OBSERVED

REPLY_SETTLED

REPLY_CAPTURED

CAPTURE_DEGRADED

CAPTURE_FAILED

PERSISTENCE_FAILED

MIRROR_FAILED

RECONCILIATION_COMPLETED

SESSION_INTERRUPTED

SESSION_RESTORED

These are event types, not additional lifecycle states.

2.3 Example records

Outgoing message submitted:

JSON
{
  "schema_version": "0.1",
  "event_id": "evt-000001",
  "event_seq": 1,
  "timestamp_utc": "2026-11-14T23:00:00.000Z",
  "session_id": "session-01",
  "conversation_id": "conv-chatgpt-01",
  "seat_id": "chatgpt",
  "direction": "outbound",
  "event_type": "SEND_ATTEMPTED",
  "lifecycle_state": "SEND_ATTEMPTED",
  "outcome": "success",
  "evidence_class": "SEND_PATH_CAPTURE",
  "message_id": "msg-001",
  "exchange_id": "exchange-001",
  "content": "Please inspect the proposed schema.",
  "content_sha256": "sha256-of-exact-utf8-content",
  "failure_code": null,
  "failure_detail": null,
  "attempted_transition": null,
  "source_reference": "chatgpt-composer",
  "previous_event_hash": null
}

Reply visibly settled:

JSON
{
  "schema_version": "0.1",
  "event_id": "evt-000004",
  "event_seq": 4,
  "timestamp_utc": "2026-11-14T23:00:08.000Z",
  "session_id": "session-01",
  "conversation_id": "conv-chatgpt-01",
  "seat_id": "chatgpt",
  "direction": "inbound",
  "event_type": "REPLY_SETTLED",
  "lifecycle_state": "REPLY_SETTLED",
  "outcome": "success",
  "evidence_class": "PAGE_OBSERVED",
  "message_id": "reply-001",
  "exchange_id": "exchange-001",
  "content": null,
  "content_sha256": null,
  "failure_code": null,
  "failure_detail": null,
  "attempted_transition": null,
  "source_reference": "reply-node-001",
  "previous_event_hash": "previous-event-hash"
}

Reply capture failure:

JSON
{
  "schema_version": "0.1",
  "event_id": "evt-000005",
  "event_seq": 5,
  "timestamp_utc": "2026-11-14T23:00:09.000Z",
  "session_id": "session-01",
  "conversation_id": "conv-chatgpt-01",
  "seat_id": "chatgpt",
  "direction": "system",
  "event_type": "CAPTURE_FAILED",
  "lifecycle_state": "REPLY_SETTLED",
  "outcome": "failed",
  "evidence_class": "CAPTURE_FAILURE_OBSERVED",
  "message_id": "reply-001",
  "exchange_id": "exchange-001",
  "content": null,
  "content_sha256": null,
  "failure_code": "REPLY_TEXT_UNAVAILABLE",
  "failure_detail": "Reply node was detected but its complete text could not be read.",
  "attempted_transition": "REPLY_SETTLED -> REPLY_CAPTURED",
  "source_reference": "reply-node-001",
  "previous_event_hash": "previous-event-hash"
}

The example hash strings above are explanatory placeholders, not valid computed hashes. The implementation must calculate actual hashes.

2.4 Content preservation

Captured text must be preserved exactly as observed or supplied by the send path.

No summarisation.

No whitespace trimming.

No Unicode normalisation.

No Markdown conversion.

No removal of apparent system instructions or unusual text.

No truncation without an explicit degraded or failed capture record.

If the page exposes only a partial response, record the partial content as partial, not as a complete reply. Include the relevant failure or degraded status.

3. The five lifecycle states

These are the five primary states for a normal exchange:

State

	

Meaning

	

Evidence required




SEND_ATTEMPTED

	

Outgoing text has been handed to the browser send path and logged

	

Exact outgoing text captured by send path




SEND_ACKNOWLEDGED

	

Browser interaction reports that submission completed

	

Submission acknowledgement




SEND_OBSERVED

	

Outgoing message is visible in the correct conversation

	

Page observation




REPLY_SETTLED

	

A response is visible and meets the adapter's settlement criteria

	

Page observation plus settlement detection




REPLY_CAPTURED

	

Complete reply text has been recorded and integrity metadata calculated

	

Successful content capture

A lifecycle state represents the last confirmed milestone, not an assumption about what probably happened.

3.1 Normal transition path

SEND_ATTEMPTED

Outgoing text recorded

SEND_ACKNOWLEDGED

Browser submission acknowledged

SEND_OBSERVED

Outgoing message visible on page

REPLY_SETTLED

Response has stopped changing and is ready for capture

REPLY_CAPTURED

Complete reply preserved and verified

The normal sequence is strictly ordered. A later state must not be recorded as confirmed unless its own evidence exists.

3.2 Settlement criteria

A reply is REPLY_SETTLED only when the seat adapter can establish that:

The response belongs to the expected conversation.

The response is no longer visibly streaming.

The response text is available for reading.

No active generation indicator remains, where the interface exposes one.

A timeout is not settlement. A quiet page is not automatically proof of completion.

If the interface does not expose sufficient evidence, record the limitation rather than inventing certainty.

4. State transitions and failure handling
4.1 Permitted transitions

Current state

	

Next state

	

Required condition




No exchange state

	

SEND_ATTEMPTED

	

Send path supplies the exact outgoing text




SEND_ATTEMPTED

	

SEND_ACKNOWLEDGED

	

Browser submission acknowledgement received




SEND_ACKNOWLEDGED

	

SEND_OBSERVED

	

Matching outgoing message found on page




SEND_OBSERVED

	

REPLY_SETTLED

	

Matching response satisfies settlement criteria




REPLY_SETTLED

	

REPLY_CAPTURED

	

Full reply captured and integrity metadata calculated

No other forward transition is valid in version 0.1.

If an event is missed, the logger must not manufacture an intermediate success. Reconciliation may establish that an event occurred, but it must record the reconciliation and its evidence separately.

4.2 Failure is recorded against the last confirmed state

A failure does not become a sixth lifecycle state. It is a separate event whose lifecycle_state identifies the last confirmed state.

For example:

Browser submit action fails: SEND_ATTEMPTED remains the last confirmed state.

Message never appears: SEND_ACKNOWLEDGED remains the last confirmed state.

Reply never settles: SEND_OBSERVED remains the last confirmed state.

Reply settles but cannot be read: REPLY_SETTLED remains the last confirmed state.

Local append fails: the logger must expose a persistence-health failure through its independent error channel and recover it to durable storage when possible.

A failure record must contain:

The last confirmed lifecycle state.

The attempted transition.

A stable failure code.

A diagnostic description.

The affected exchange and seat identifiers.

A timestamp.

The evidence available at the time.

A failure must never be represented by a fabricated successful transition.

4.3 Degraded capture

Use outcome: "degraded" when useful information was preserved but completeness or certainty is reduced.

Examples:

The reply was captured, but the adapter could not establish that the final visible text was complete.

The outgoing message was captured, but its page identity could not be established.

A mirror operation was interrupted after the canonical local record was safely appended.

The page exposed a response but not a reliable message identifier.

A degraded record must state exactly what is missing. It must not be promoted to a successful complete capture merely because some text exists.

4.4 Duplicate events and recovery

The logger must be idempotent at the event boundary.

Reprocessing the same event_id must not append a duplicate.

A repeated page observation must not create a second confirmed message without evidence that it is a distinct message.

A retry by an adapter must not silently overwrite the original event.

Recovery must preserve the original event sequence and identity.

If an event is received twice with the same ID but different content, flag an integrity conflict. Do not choose one version silently.

If an adapter reconnects, the supervisor should reconcile the last known page state against the last durable event sequence. Any reconstructed event must be labelled as reconstructed or reconciled, not as an original live observation.

5. Evidence classes

Evidence classes describe the provenance of the record. They do not establish the truth of the message content.

Evidence class

	

Meaning

	

What it proves




SEND_PATH_CAPTURE

	

Exact text intercepted at the outgoing send path

	

The logger received that outgoing text




SUBMISSION_ACK

	

Browser submission operation acknowledged

	

The browser interaction returned successfully




PAGE_OBSERVED

	

Content visibly present in the relevant conversation page

	

The page displayed that content




SETTLEMENT_OBSERVED

	

Adapter observed the response meet settlement criteria

	

The page appeared to finish generating




CAPTURE_VERIFIED

	

Complete visible text was captured and integrity metadata calculated

	

The captured text matches the captured source




MANUAL_CAPTURE

	

A human supplied or copied the content

	

A human recorded that content




RECONSTRUCTED

	

Event recovered from later inspection or incomplete evidence

	

A reconstruction was made, not that it was captured live




CAPTURE_FAILURE_OBSERVED

	

A specific capture failure was detected

	

The failure was observed and recorded




PERSISTENCE_FAILURE_OBSERVED

	

A write or durability failure was detected

	

The persistence operation failed




MIRROR_VERIFICATION

	

Mirrored records were checked against canonical records

	

The mirror matches the verified source records

One event should carry the strongest evidence class directly supported by its evidence. Do not use CAPTURE_VERIFIED to describe a mere page observation.

In particular:

A model response being captured does not establish that its claims are true.

A submission acknowledgement does not establish page delivery.

A page-visible message does not establish that the intended recipient read it.

A reconstructed record does not become a live capture retroactively.

This distinction is essential if these transcripts later become evidence in model comparisons, technical reviews or adjudications.

6. Persistence and mirroring
6.1 Canonical record

The canonical JSONL stream is the authoritative record.

Recommended logical organisation:

Plain text
RemmyContext/
  ChannelLogger/
    events/
      2026-11-14.jsonl
    transcripts/
      chatgpt/
      gemini/
      claude/
    manifests/
    health/

The event stream is authoritative; readable transcripts are derived views.

Do not maintain two independent authoritative copies of the same conversation history.

6.2 Write behaviour

Append one complete JSON object per line.

Use a single logical writer or equivalent synchronisation to preserve sequence ordering.

Ensure each line is complete before considering the event appended.

Flush and synchronise according to the chosen durability policy.

Never silently overwrite an existing event.

Record a persistence failure through a durable independent mechanism when the primary destination is unavailable.

Important qualification: a logger cannot guarantee a durable failure record by writing to the very storage system that has just failed. It therefore needs an independent health/error path, such as a bounded local emergency journal or supervisor-visible health state, with later reconciliation into the canonical stream.

That is not a second source of truth. It is a recovery mechanism for events that could not yet reach the source of truth.

6.3 Mirroring

Mirroring should be asynchronous and must not gate the conversation loop.

Each mirror batch should have:

First and last event sequence.

Event count.

Batch timestamp.

Hash or manifest digest.

Verification result.

Last successfully mirrored sequence.

A failed mirror must generate MIRROR_FAILED or an equivalent health event. A mirror failure must not imply that the canonical local record failed if it was already safely written.

6.4 Integrity

Calculate SHA-256 over the exact UTF-8 content bytes, without normalising the text.

For event integrity, use a documented canonical serialisation before hashing. If hash chaining is implemented, specify precisely which fields are included and exclude the previous_event_hash field from its own digest calculation.

The implementation must not use placeholder hashes, and a hash match must not be described as proof of authorship or factual accuracy.

7. Failure-test matrix

These are acceptance tests, not optional diagnostic suggestions.

ID

	

Test condition

	

Expected record/result

	

Pass criterion




L01

	

Normal outgoing send

	

SEND_ATTEMPTED

	

Exact outgoing text recorded




L02

	

Browser acknowledges submission

	

SEND_ACKNOWLEDGED

	

Correct exchange and seat association




L03

	

Outgoing message appears

	

SEND_OBSERVED

	

Matching page message identified




L04

	

Normal reply settles

	

REPLY_SETTLED

	

Settlement evidence recorded




L05

	

Normal reply captured

	

REPLY_CAPTURED

	

Complete text and hash preserved




L06

	

Browser submit fails

	

CAPTURE_FAILED

	

Last confirmed state remains SEND_ATTEMPTED




L07

	

Browser acknowledges but message never appears

	

Failure event

	

No SEND_OBSERVED success is fabricated




L08

	

Page displays wrong conversation

	

Failure/degraded event

	

No cross-conversation attribution




L09

	

Reply remains streaming

	

No settlement success

	

No premature REPLY_SETTLED




L10

	

Reply settles but text cannot be read

	

CAPTURE_FAILED

	

Last confirmed state is REPLY_SETTLED




L11

	

Reply is only partly readable

	

CAPTURE_DEGRADED

	

Partial text labelled incomplete




L12

	

Duplicate event delivered

	

Existing event retained

	

No duplicate append




L13

	

Same event ID has different content

	

Integrity conflict

	

No silent overwrite




L14

	

Browser disconnects during exchange

	

SESSION_INTERRUPTED

	

Last confirmed state preserved




L15

	

Browser reconnects

	

SESSION_RESTORED

	

Reconciliation performed without fabricated history




L16

	

Primary disk write fails

	

Persistence-health failure

	

Failure exposed through independent channel




L17

	

Primary storage recovers

	

Reconciliation event

	

Missing events recovered without duplicate sequence




L18

	

Mirror destination unavailable

	

MIRROR_FAILED

	

Canonical local stream unaffected




L19

	

Mirror contains partial batch

	

Verification failure

	

Batch not marked complete




L20

	

Unicode and unusual formatting

	

Successful capture

	

Exact content preserved




L21

	

Very large reply

	

Successful or degraded capture

	

No silent truncation




L22

	

Multiple seats respond concurrently

	

Separate events

	

Correct seat and exchange attribution




L23

	

Two conversations on one seat

	

Separate conversation IDs

	

No cross-conversation mixing




L24

	

Supervisor restarts

	

Recovery and reconciliation

	

Durable event history remains readable




L25

	

Logger queue becomes full

	

Explicit degraded/failed state

	

No silent event loss




L26

	

Watcher sees an existing reply after reconnect

	

Reconciled event

	

Correctly labelled as reconstructed




L27

	

Content hash verification

	

Verification result

	

Exact bytes produce matching digest




L28

	

Event sequence verification

	

Verification result

	

No unexplained gaps or duplicate sequence numbers

7.1 Required stress tests

In addition to individual failure tests:

Send large messages containing code, Markdown, Unicode and long unbroken strings.

Capture long model responses.

Run all three seats concurrently.

Interrupt the browser during outgoing submission.

Interrupt it while a reply is streaming.

Restart the supervisor with events awaiting mirroring.

Disconnect the mirror destination while local capture continues.

Repeat the same observation across watcher reconnections.

For each test, preserve the actual JSONL output and the expected result. A test report saying "passed" without the corresponding records is insufficient.

8. Acceptance criteria

The implementation is acceptable when all of the following are demonstrated:

Every outgoing send attempt is recorded with its exact text.

Browser acknowledgement and page observation remain distinct.

Every captured reply is associated with the correct seat, conversation and exchange.

The five lifecycle states cannot be advanced without their required evidence.

Every detected capture failure produces an explicit failure or degraded record.

Duplicate events cannot silently duplicate or overwrite canonical records.

Primary persistence failures are exposed independently of the failed storage destination.

Mirroring can fail without blocking the conversation loop.

Recovery and reconciliation preserve provenance and sequence integrity.

The logger cannot initiate or alter model interactions.

All 28 failure tests pass, with raw evidence retained.

The existing conversation-loop measurement requirements remain unchanged.

Non-regression requirement: Compare loop behaviour with the logger disabled and enabled. The logger must not introduce a synchronous dependency on persistence, mirroring or transcript generation. Record any measurable timing impact rather than assuming that asynchronous operation makes it negligible.

9. Implementation boundaries and review

I recommend three implementation stages:

Stage

	

Deliverable

	

Gate




1

	

Schema, event writer and local persistence

	

Schema and durability tests pass




2

	

Supervisor integration and three seat adapters

	

Correct attribution and lifecycle tests pass




3

	

Mirroring, reconciliation and stress testing

	

Full failure matrix passes

Do not expand the scope into summarisation, semantic indexing, model evaluation or automatic evidence adjudication during these stages.

Those may be useful later, but they are not channel logging.

10. Final engineering position
SPECIFICATION READY FOR REVIEW

The logger is a record-keeping system. Its job is to preserve the distinction between:

What was attempted.

What the browser acknowledged.

What the page displayed.

What appeared to finish.

What was actually captured.

What could not be verified.

That distinction is more valuable than simply having a large collection of transcripts.

One implementation detail I want to emphasise: the five lifecycle states describe the exchange, while failure and evidence classifications describe what the logger knows about it. Keeping those dimensions separate prevents a failed capture from corrupting the meaning of the lifecycle.

Remmy, this is the proposed contract for your implementation. Please review the schema and transition rules against the supervisor and adapter design before locking them. I can take the first implementation review, including inspecting the actual JSONL records and running the failure matrix, once you have a working version.

⟦ALEX-FINAL⟧

The specification is ready for the one discrepancy round. No implementation approval is implied until the schema, state transitions and acceptance criteria are reconciled.
