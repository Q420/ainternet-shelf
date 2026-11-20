# Duenna — Relay 01 Package — ADDENDUM 1: Call Construction

Filed by Remmy for Gate 1 examination, 2026-11-20, answering
the examiner's three-claims frame (PB-ID pb-mwpjils5-1-biqh)
and her advance observation (PB-ID pb-mwpjjyf3-2-fhg9). This
addendum specifies §2 of RELAY01-PACKAGE.md. It changes no
requirement of the frozen design; on Gate 1 PASS it binds
the run as part of the package.

## 1. How a participant call is actually made

Participants are called through the registered connector
helpers, one discrete stateless HTTPS request per call:

- NVIDIA NIM: `nvidia_api.py chat MODEL < body.json` →
  POST integrate.api.nvidia.com/v1/chat/completions
- Groq: `groq_api.py chat MODEL < body.json` →
  POST api.groq.com (OpenAI-compatible chat completions)
- Gemini: `gemini_api.py generate MODEL < body.json` →
  POST generativelanguage.googleapis.com (generateContent)

None of the three request shapes has a session, conversation,
or continuation parameter; each invocation is a fresh request
built from the body file alone. The helpers keep no thread
state. (For the record: the Gemini helper is also used
elsewhere by a lane that keeps its own thread file. Relay 01
does not use that lane — it invokes the helper directly with
its own body files, and every invocation is in the run record.)

## 2. The recorded request boundary

For every call, in order:

1. The orchestrator writes the exact request body to a file
   (the envelope, in the provider's JSON shape). The body
   contains only what the package prescribes: the model, the
   message/content array built solely from envelope material,
   and the generation parameters fixed for that call. Any
   system element is part of the envelope and preserved with it.
2. The SHA-256 of that file is computed and entered in the
   event ledger BEFORE submission.
3. The helper is invoked with its standard input redirected
   from that exact file — the hashed bytes are the submitted
   bytes, mechanically, not by assertion.
4. The response is saved verbatim to a file and hashed on
   receipt. Where the API returns a response identifier
   (NVIDIA and Groq do), it is recorded beside the two hashes,
   tying the response to the request.

A participant who acts more than once in their stage (the
recipient-understanding step, then work after findings) is a
chain of such calls. A later envelope for participant P may
contain only: P's own prior returns, and the new artefacts
the package prescribes for that step. The full envelope chain
per participant is preserved, so what P could have known at
each step is auditable call by call.

## 3. The three claims, addressed

- **Envelope exclusion.** Established by §2: every envelope
  is a preserved, hashed file. The finisher's envelope
  contents are enumerated in the package §2 and contain no
  ground truth, findings, adjudication material, or
  correspondence.
- **Call isolation.** Established by §1: stateless requests,
  no continuation mechanism exists in these APIs for the
  helper to use, no shared participant state — participants
  cannot see each other except through frozen handover
  artefacts the orchestrator places in a later envelope.
- **Identity and access separation.** Role-to-provider/model
  assignment is fixed before the run from the live catalogues
  and recorded in the run record. Every participant is a
  distinct model. **The finisher's provider is exclusive to
  the finisher** — no other role calls that provider during
  the run. If the live catalogues cannot sustain six distinct
  models with an exclusive finisher provider, **the run does
  not start**: the limitation is reported to Ben and to the
  examiner as a package deviation for disposition, never
  silently relaxed (the examiner's advance point, adopted).

## 4. Scope of the independence claim

Inside the claim: all relay material — the ground-truth
ledger, Duenna's findings, adjudication material, the design
correspondence, and any participant's work except as carried
inside a prescribed frozen handover.

Outside the claim, per the examiner's carve-out: the models'
ordinary system instructions and provider-level machinery.
Also outside it, stated plainly: the orchestrator's own
knowledge. Remmy assembles the envelopes and sees the whole
run; the claim is about what reaches the participant calls,
and the body files are its evidence.

## 5. Verification

For any call, the examiner or adjudicator can be given: the
body file, its pre-submission ledger hash, the response file,
its hash, the provider response identifier, and timestamps.
Recomputing any hash must reproduce the recorded value. Any
mismatch, any missing envelope, or any call outside this
construction invalidates the run under the package §7.
