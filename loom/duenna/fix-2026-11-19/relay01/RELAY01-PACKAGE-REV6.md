# RELAY 01 — PACKAGE REVISION 6 (delta to Revision 5)

*Revision 6 incorporates Revision 5 (blob
dc9aa183ce0c8974226ba3785d0ff46ba1924717, Gate 1 PASS
2026-11-20) by reference and changes ONLY the invocation
path's timeout values, as recorded below. Every other
provision of Revision 5 — the design freeze, the
assignments, the initial ledger, the correction, the
no-start conditions — stands verbatim and unchanged.*

## 1. The ruling this revision answers

During the run's pre-clock archive verification, the
originator's provider (NVIDIA) repeatedly exceeded the
calling helpers' built-in 120-second read window:
multiple verification calls died on read timeouts while
the model was still working (records preserved in the
run's calls directory: the av-o and av-c series). Retries
landed intermittently; the window, not the work, was the
obstruction.

Ben's ruling (2026-11-20 18:13 MST, main chat): "The
obvious answer is to increase that instead of going in
circles and having it keep denying the work we know is
taking more than two minutes."

The orchestrator stopped the verification driver on that
ruling. This revision makes the change through the gate
rather than silently editing a pinned exhibit.

## 2. The changes (complete list)

In `exhibits/relay-helpers/`, one line in each helper —
the HTTP read timeout, 120 → 600 seconds:

| helper | REV5 SHA-256 | REV6 SHA-256 |
|---|---|---|
| nvidia_api.py | eaff1fb923ee7efd7c386ad7e23b494f6961f8af259be03e1dde3ca127b1c7e3 | 56ca6a4d82fe09b4de7bf96cfa3c3e58c86e849211692705310d6414409f5c7f |
| groq_api.py | 088efd1c59ab1c66ca729da4fa002a9e14d561dfa34601187a539251d6e7bfa4 | 8bed172ffc6017c6a322265ba5e1b7053d2cc4a74018f98ca1956d041b5d2369 |
| gemini_api.py | 01e8f4145241b2b5f2a048a640a2ee06d0a28027a2e28805755bf66702bef908 | c5108982df9ef94bdacd8d7da2d964ccfd3d8b098c24c999e12f52f6c13134f2 |

All three helpers carry the identical window, and the
relay proper will make long calls on all three providers;
the ruling is applied to the window wherever it sits, so
the same obstruction cannot recur on the Groq or Gemini
lanes mid-run.

In `exhibits/relay_call.py` (REV5 SHA-256
613389d62ad3dd7106811da9b226cf707da2c06a0583158f5c754716e05288b7;
REV6 SHA-256
293503759efd8aef9267f07f0be0b1a4bf8321a32aca804015b1fd77dc3bb5e1):

- the three helper pins updated to the REV6 hashes above;
- the helper-subprocess ceiling 600 → 900 seconds, so the
  caller's own limit cannot cut off a helper lawfully
  reading for up to 600.

`dynamic_credentials.py` is unchanged (SHA-256
8b1f42e80a76710edf0ff2abf8a51b0cde35b06474af865de108a7ca27d6728d);
its 5-second timeout serves the local credential socket
and is not part of this change. Nothing else in the
exhibits, the package, or the freeze changes.

## 3. Run state at this revision (stated, not repaired)

Pre-clock gates already executed under the Revision 5
path stand as recorded: catalogue gate PASS, run-start
invocations PASS, orchestrator archive byte verification
PASS. Participant archive verification is INCOMPLETE:
originator v1 partially verified (the 100-line first
chunk and 8 of 12 fifty-line parts carry shaped verdicts;
its aggregate did not land), originator v2 partial,
checker not started. No clock start has occurred. On a
Gate 1 PASS for this revision, the archive-verification
gate is completed under the revised path and every
remaining no-start condition applies exactly as Revision
5 states.

## 4. Revised path exercised

One preflight call through the revised caller
(preflight4/pf4-nvidia): NVIDIA / kimi, helper exit 0,
response chatcmpl-f8cd8e78-f3db-44bf-b8d3-33948006fc49,
record preserved with the dependency hash verified
(8b1f42e8…). The pin verification passed against the new
helper hashes before the call was made.
