# To Vane — the native1 demonstration: the complete result (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 416), under her phase-2 release
(INDEX 415). The run is spent; no rerun is sought or authorised by this return.
Read first-hand from the run's own record (`report.json`, `run-export.json`,
the captured response artifacts) in `live-demo/first-worker-native1/`, shelved
with this letter.

## The result, whole

**Outcome: STALLED — `provider_failure` (HTTP 400), at iteration 2.** 29
events; one dispatch; no brief written. The checker evidence stands in the
report: **all eleven checks ok** — run binding, chain hash and sequence,
replay, both schemas, replay equality, seal, assembly, dispatch, and loop
correspondence.

**Iteration 1 — the adapter's first live end-to-end passage.** The model's
native call — `sandbox.list`, provider call ID `fc_5f4344e5…` — was captured
as response evidence (979 L1 bytes, artifact `e5be23a6…`), classified and
persisted in a translation record, and **dispatched through the doorway**
(dispatch-1), its outcome returned as a result; the loop advanced to
iteration 2. Iteration 1's commitment records `disable_tool_validation:
true` — BD-1 stood in force, snapshotted as built. Call timings: iteration
1's call 1.73 s; iteration 2's span 65.50 s — the pacing held at the
call-start boundary as examined.

**Iteration 2 — the provider refused the response wholesale.** The captured
artifact (`responses/iteration-26.json`, 972 bytes) holds an HTTP 400,
code `tool_use_failed`: *"attempted to call tool 'commentary' which was not
in request.tools"*, with the `failed_generation` preserved in the evidence.
The framework recorded no refusal of its own (the refusal was the
provider's, before delivery); the loop stalled honestly on
`provider_failure`. Stated at envelope level, as always: the attempted name
was **`commentary`** — not `container.exec`, not `sandbox.read` — a channel
name from the model's own format surfacing as a call, refused by the
provider despite BD-1 standing in force. Why the flag did not deliver this
attempt as it delivered P1's unoffered calls is **not established by this
record** and is not claimed here; the distinction is examination material,
and the artifact preserves everything needed to examine it.

## What this establishes, inside the claim fence

The doorway-preserving path works live, once, end to end: a native call was
offered, captured, translated, adjudicated, dispatched, and answered, and
the loop continued — the seam that ended every prior run at iteration 1 is
crossed. The run then ended at a **different** boundary: a provider-side
wholesale refusal of a channel-name call attempt on the second response.
Composition competence remains **untested** — the worker received a listing
and never reached the sources' contents; no brief exists; nothing about the
assignment's completion is claimed. The record is complete and
checker-clean, and it is, per Ben's ruling, the exact state from which a
later agent could continue — recorded dispatches are never replayed, and
dispatch-1 stands.

The complete result returns for your examination, as the release requires.
