# STAGE 6 SMOKE — REPLACEMENT EXECUTION SPECIFICATION 01 (2026-11-16)

**Status:** Drafted by Remmy under the owner's decision; for the
examiner's (Alex's) examination and ruling. NOT in force until
Alex approves it. Authorised by: the owner's decision for the
supervisor-less shape (Ben, main chat, 2026-11-16 17:36 MST —
tap plus words, the amendment consequence stated on the face
of the choice), made after Alex's venue ruling
(record/ALEX-DUENNA-VENUE-RULING-2026-11-16.md) held that this
shape requires exactly that: a new owner decision and a
replacement execution specification, not an amendment by
implication.

## 1. What this replaces — and what it does not

This specification replaces ONLY the execution-and-custody
clauses of the pre-flight clearance
(record/ALEX-DUENNA-STAGE6-SMOKE-PREFLIGHT-CLEARANCE-2026-11-16.md
@ d61a479e) for the single authorised smoke call: the pilot
supervisor, its launcher chain, and the START/TERMINAL
commitments do not form part of this execution.

Everything else in the clearance and the decided calls stands
unchanged: exactly one live call; tree T04; smoke config
sha256 ebb83d772a69da867721990917fef2326516fe71ad075b5693bc15e6e2b4f9ed
(max_attempts 1, max_tokens 4355, the accepted preventive
ceiling under the 5,000-token total cap); production endpoint;
no retry; no paid substitution; no battery call; the battery
pass bar is set by Alex from the smoke evidence; the battery
is not authorised by the smoke.

## 2. Why

Measured venue fact: every process on the VM venue runs with
NoNewPrivs=1 (verified in the agent shell, in su sessions, and
in a root systemd oneshot). The C3 launcher's privilege
transitions are therefore impossible on this venue, and the
custody chain refused two firing attempts pre-call
(SX_CHILD_TERMINATED_AT_HANDOFF; SX_ABORT_PRE_RELEASE), zero
spend. The refusals are valid custody outcomes and are part of
this run's evidence. The laptop venue preserves the custody
architecture but has no credential route; the owner has chosen
this shape instead, with the loss of the custody layer stated
plainly in §4.

## 3. Execution

- Programme: the filed smoke harness
  (duenna/stage6-smoke-assembly-2026-11-16/smoke_harness.py,
  sha256 a2639808b624b6f7922ef043f52a493d03fd9106d173c17b9e3f8b293f822f33)
  with the filed smoke adapter variant and smoke config,
  exactly as inspected and accepted in the assembly inspection
  (record/ALEX-DUENNA-SMOKE-ASSEMBLY-INSPECTION-2026-11-16.md).
- Invocation: one execution session, run by Remmy, environment
  SMOKE_MODE=live and PILOT_RUNS_ROOT set to a fresh runs root;
  the driver derives the run id (STAGE6SMOKE-<UTC date>-001).
  The session's full console output is captured to a log filed
  with the record.
- One-call bound: guaranteed by the tree shape (T04's single
  MODEL step, recovery None → driver max_attempts 1), by the
  smoke config (retry max_attempts 1), and by the preventive
  token ceiling (max_tokens 4355 against the bounded input;
  point 8 of the pre-flight, as accepted).
- The adapter is the accepted variant: production endpoint
  only, connector credential via the surrogate route, no key
  stored or read.

## 4. The record — and its stated limit

The run produces: the driver's run record (the pinned
pilot_record machinery, hash-chained), the adapter capture(s)
verbatim (including request_raw and response_usage), and the
run summary. The complete record is filed to the shelf for
Alex's adjudication, together with: this specification, the
two custody refusal records, and the firing log.

**Stated limit:** no supervisor commitments exist for this
run. The record's provenance is the pinned driver/adapter
machinery plus the filed firing log — a weaker provenance than
the custody-wrapped record, accepted by the owner for this
plumbing test. The run and every citation of it carry the
label **SUPERVISOR-LESS**; it must never be cited as a
custody-wrapped run. The smoke pass bar is unchanged: full
harness traversal plus a complete, well-formed record; the
token accounting is taken from the capture's response_usage
against the 5,000-token ceiling.

## 5. Bounds

One firing under this specification. Any failure class
(transport, authentication, adapter, truncation, driver) is
recorded as the smoke's outcome and reported; there is no
re-fire without a new examiner ruling. If Alex does not
approve this specification, it lapses and the smoke remains
unfired under the venue ruling's disposition.
