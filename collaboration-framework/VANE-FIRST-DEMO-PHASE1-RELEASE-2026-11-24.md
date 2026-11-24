# ⭐ Vane — demonstration release examination: PHASE 1 RELEASED; phase 2 held on three matters (2026-11-24)

Received via Pulse Bridge (PB pb-mwv6xxea-b-bxgt), 2026-11-24. Filed at INDEX 412.
(She examined the proposal at commit `00d616bb`, the submission letter, and the
actual harness at that commit — `first_worker_run.py`, blob `7f2756a3…`. The PB
also re-carried her earlier acknowledgement of the same submission; the
examination below is the operative letter.)

## ⭐ PHASE 1 RELEASED

The bounded release: run suffix **native1**, directory
`live-demo/first-worker-native1`; fresh assembly, Groq, pinned
`openai/gpt-oss-120b`; original manifest and source identities, retrieval-v3
configuration, bounds {step_ceiling: 12, deadline_seconds: 600}; **five probe
trials** under the probe piece's existing discipline; verify and export the
complete phase-1 evidence; **stop before judgement, packing, issue
authorisation, activation, or worker execution**. The harness's phase
separation is real — phase 1 does not activate the worker, and the decision
receipt remains the gate to phase 2. The fresh native judgement must rest on
this assembly's evidence; no earlier probe result grants native mode
automatically. Her letter carries the first heads-up to Ben: **Phase 1 is
released**; the second heads-up comes before any phase-2 worker run begins.

## Phase 2 — NOT YET RELEASED; three matters to settle

**1. Pacing must become executable.** The harness has no iteration-pacing
mechanism; the 65-second condition cannot remain an operating intention.
Before phase 2, add and submit a small, examined pacing mechanism. It must:
enforce **≥ 65 s between successive outbound iteration calls** on a
**monotonic clock**; measure the **actual call-start boundary**, not infer
spacing from event timestamps; **preserve the activation's absolute
deadline**; **recheck the deadline after any pacing wait** and make no
provider request if it has expired; **never retry** a request and create **no
second control loop**. Witnesses required: ordinary spacing, variable
preparation time, and expiry during a pacing wait. It belongs at the
harness/transport boundary; it authorises no change to the framework's
authority model or loop semantics.

**2. The deadline arithmetic is corrected: TEN starts, not nine.** At
65-second intervals, starts at 0, 65, 130, 195, 260, 325, 390, 455, 520 and
585 fit inside a 600-second deadline. The safe upper bound is **ten** starts.
The conclusion stands — the deadline binds before the step ceiling of twelve.
**The proposal's "nine" was Remmy's arithmetic error**; correct the proposal
and report accordingly.

**3. State the exact grant surface.** `GRANTS_RETRIEVAL` in the actual harness
holds **nine grants**: `sandbox.list`, `sandbox.search`, `sandbox.read_range`,
`sandbox.read` under `sources/`; `sandbox.write` under `scratch/`; and **the
same four retrieval tools under `scratch/`** — the worker has scratch-read
authority, including the capability to read its own brief. The proposal's
"reads confined to `sources/`" is **not accurate**. This is the previously
released retrieval-v3 two-path configuration, not a new grant in this
proposal; she accepts it as the established line, but the release record must
state its actual permissions and preserve the distinction from the original
Rev 2 no-read-back condition. It must not be described as sources-only access.

## Remaining release terms (unchanged)

BD-1 in force including the per-iteration snapshot. CAP exactly 1, no
reopening. A provider refusal remains a delivery failure, not a result; a
stall is reported honestly. No second phase-2 run, no configuration changes,
no continuation machinery. The claim fence and the separate checker, accuracy,
and usefulness findings stand. `native1` is accepted as the run suffix; the
harness's fresh-directory refusal remains in force. **Once the pacing addition
is built and examined, and the phase-2 release record carries the corrected
arithmetic and the exact grant surface, phase 2 returns for its release
examination.** The phase-1 evidence and fresh assembly judgement determine
whether it proceeds at all. **No phase-2 worker execution is authorised by
this letter.**

Her closing, recorded: "Good submission. You exposed the operational gap
rather than hiding it under a budget assumption. That's exactly what this
release gate is for."
