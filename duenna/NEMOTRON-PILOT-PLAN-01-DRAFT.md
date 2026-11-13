# NEMOTRON GOVERNED-SUBJECT PILOT — PLAN 01 (DRAFT)

Status: ADOPTED by Ben, 2026-11-12 16:42 MST ("Make it so", voice).
Drafted by Remmy, 2026-11-12, from Alex's final pilot-frame
adjudication (pb-mwe90lo6) and the shelf record.
Adoption authorises Stages 0–4 drafting/design work only.
Stage 5 (build) and Stage 6 (execution) each carry their own gates;
no model calls are authorised by this adoption.

## The question the pilot answers

Can a different model operate through the same bounded, deterministic
governance machinery without being trusted to report its own compliance?

Subject: Nemotron-3 Nano 30B (reasoning), via Ben's NVIDIA API lane —
programmatic, logged, replayable; no browser seat.

Frame (Alex, final): a separate, bounded pilot derived from the V2
process design. NOT a ratio-study arm. NOT a subject swap inside the
Qwen V2 package. The ratio study stays paused and untouched.

## What the foundation actually is (Alex's inspection, accepted)

V2 is a useful process-and-tool implementation package. It is NOT yet
evidence of a complete, portable Duenna runtime:
- Nine specified process trees (T01–T09) and five deterministic tools exist.
- Per-field accountability entries are emitted by reference_insert;
  the ledger is process output (no standalone artefact — acceptable to
  Alex IF entries are preserved, complete, inspectable, reproducible).
- NOT established: a standalone driver that executes the full battery;
  model independence (tools.py imports run_ab and reads its frozen
  corpus via BY_ID — Qwen-tied); live Shelf retrieval (shelf_lookup
  reads a frozen corpus / local manifest); the general D3 obligation
  lifecycle; mechanical role enforcement (T04 is behavioural).
- Named defect candidate for qualification: reference_insert accepts
  both EXTRACTED and FOUND results — the pilot must verify an
  unextracted or unsuitable result cannot be inserted and represented
  as verified evidence.

## Stages (Alex §6, in order)

STAGE 0 — SOURCE FREEZE (prerequisite #1 + #14, BLOCKING for input freeze)
  Pin the exact governing set for THIS pilot: the nine process trees,
  the five tools, the fixtures, and every dependency — path, version,
  sha256. Satisfied by a targeted pilot manifest, NOT by completing
  programme-wide housekeeping (#27–28 global pass not required).
  Gate Register / Duenna Plan currency pass (#26) runs PARALLEL only.
  Acceptance: a manifest an examiner can pull and verify byte-for-byte.

STAGE 1 — V2 QUALIFICATION (prerequisites #2 + #3, BLOCKING)
  Inspect the implementation and establish what is actually executable:
  which trees run end-to-end today, what the demo proves and does not
  prove (19-tool-call fixture demonstration ≠ full battery), and the
  reference_insert EXTRACTED/FOUND question, answered by a test.
  Every capability claim leaves this stage labelled EXECUTABLE /
  FIXTURE-ONLY / NOT PRESENT. Changes needed to make tree inputs
  model-neutral are declared and versioned here — never silently.
  Acceptance: a qualification report Alex can inspect.

STAGE 2 — NEMOTRON ADAPTER DESIGN (prerequisite #4, BLOCKING)
  The subject interface on paper: model identity and version pinning,
  request parameters, and the canonical capture — raw API request and
  response, errors, retries, timestamps, replay inputs — preserved for
  every call. Adapter failures must be distinguishable from subject
  failures and governance failures in the record.
  Acceptance: an adapter specification Alex can inspect. No calls yet.

STAGE 3 — PILOT HARNESS DESIGN (prerequisites #2 + #5, BLOCKING)
  The driver that executes the trees against the adapter; deterministic
  tool execution; the canonical execution record (event identity, tool
  invocations, returned payloads); trigger / progress / satisfaction /
  failure / closure semantics for the pilot's obligations; stop
  conditions; the replay procedure by which an examiner re-derives an
  outcome from the preserved record alone. A solo (ungoverned) arm with
  identical task inputs is retained ONLY where the research question
  requires measuring governance's effect — never confused with the
  ratio study.
  Acceptance: a harness specification Alex can inspect.

STAGE 4 — ACCEPTANCE CRITERIA (prerequisite #5, BLOCKING)
  Fixed before any execution: what counts as a successful, failed, or
  inconclusive run, against §4's minimum evidence — same pinned inputs
  reach the subject; raw request/response preserved; deterministic
  tools independently inspectable; failed verification cannot be
  silently converted to success; every produced field has an evidence
  trail; obligation decisions derived from the record, not the model's
  claim; independent re-derivation possible; model / infrastructure /
  governance failures distinguished.

STAGE 5 — BUILD + INDEPENDENT INSPECTION
  Build the adapter and harness to the frozen specifications, then the
  constructed pilot package is inspected (Alex, per his offer to review
  the harness architecture and take the source-to-requirement
  crosswalk) BEFORE any live model execution.

STAGE 6 — EXECUTION (separately authorised)
  No runs until: Stages 0–5 complete, the package has passed
  inspection, and Ben has adopted this plan and authorised execution
  as its own decision. Run count, battery composition, and stopping
  conditions are set at that authorisation, not here.

## Explicitly excluded from this pilot (Alex §5, Ben's deflate rule)

- Completing D3 v0.10 approval; the Correction B adjudication (#13–14
  NOT-NEEDED — the pilot claims no v0.10 conformance and relies on no
  unresolved Correction B semantics; any dependency that does rely on
  them becomes blocking for that dependency only).
- F1 fix (#15), Grok's adjudication (#16), v0.8 fixture/UX conditions
  (#18) — NOT-NEEDED on the same no-claim basis.
- Stage 1 proposal (#17) and the Gate Register currency pass (#13 in
  Alex's crosswalk) — PARALLEL programme work, not pilot gates.
- Stage 2 execution (#19) — NOT-NEEDED while this is explicitly a
  bounded V2 process-harness experiment; it becomes BLOCKING the
  moment the experiment claims to exercise the general D3 obligation
  engine. This plan makes no such claim.
- Ratio-study Draft 6 and its freeze sequence (#22) — NOT-NEEDED;
  the study stays paused, its inputs and freeze requirements untouched.
- The full Stage 1–4 programme; a general-purpose obligation
  lifecycle implementation; live Shelf integration (inputs are frozen
  and pinned instead); any general role-enforcement claim drawn from
  behavioural refusals; a multi-provider delegation experiment.

## Retained core (never cut)

Grounding, deterministic extraction, reference insertion, field
verification, receipt comparison, evidence attribution, failure
recording, independent re-derivation.

## Open decisions for Ben

1. Adopt this plan (adoption authorises Stages 0–4 drafting/design
   work only; build at Stage 5 and execution at Stage 6 each carry
   their own gates as written).
2. Crusher's shelf-currency retrieval (requested by Alex for the
   adjudication): Alex has now ruled without it, using the targeted
   pilot manifest at Stage 0 instead. The wake-Crusher question can
   lapse, or be exercised anyway as an independent check — Ben's call.
3. Alex's offered parallel work (source-to-requirement crosswalk +
   harness-architecture review) engages when the Stage 1/3 artefacts
   exist for him to review.

## Amendment — 2026-11-12 16:45 MST (Ben, ruling)

"Nothing should ever be able to edit the index ever. Only the system."

Recorded against Stage 3 (pilot harness design) and as a standing
programme rule: index artefacts are system-written only. No agent,
tool, seat, or harness may edit an index — read access only. For this
pilot: the frozen corpus under the bridge index folder is read-only
infrastructure. Stage 3's only remaining question is whether the
harness reads the corpus in place or reads a pinned copy into the
pilot set; editing is not an option at any stage. The Stage 0 hash
pins stand as the tripwire — any system-side index change surfaces
as a pin mismatch and forces a re-freeze.
