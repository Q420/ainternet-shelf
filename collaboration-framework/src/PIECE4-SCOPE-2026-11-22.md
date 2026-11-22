# Piece 4 scope — live seat drivers (§3.4)

**Date: 2026-11-22. Authority:** Ben's design ruling 2026-11-21 (Rev 5 pair approved; Stage 2 open) and his loop approvals (2026-11-22, "Proceed"). Pieces 2 and 3 passed Vane's final examination (7b677f71, f758a348). This note maps §3.4 (R11–R13) onto what stands before code, in the Piece 3 pattern — flags stated for examination, not decided silently.

## The requirements

- **R11.** A driver wakes its model with: the model's briefcase (current version), the bubble view within its evidence boundary, and the specific prompt the run's state calls for (a new contribution to answer, a gate outcome affecting its part, an orchestrator's recorded note). A driver never wakes its model with material outside the case's evidence boundary.
- **R12.** The model's outputs return only as proposed acts through the doorway (§3.2), which validates and records them. A model has no other write path.
- **R13.** A driver that fails (timeout, provider error, malformed output) records the failure as an event; the run pauses at that seat rather than proceeding on a fabricated contribution.

## The build

New module `src/framework/driver.py`. A `Driver` is constructed with the doorway, a seat id, the seat's doorway token, and a **model callable**. One wake cycle:

1. **Assemble the wake package from the record alone:** the seat's current briefcase (below), the seat's bubble view (Piece 3's scoped render), and the wake reasons the run's state calls for (below). The package contains nothing else — in particular not the token, and nothing outside the view's boundary (R11).
2. **Call the model** with the package. The model returns proposed acts as data; it holds no token, no store, no write path (R12).
3. **Submit each proposed act through the doorway** at the view's position. Refusals are returned in the cycle result, not hidden; on a staleness refusal the driver re-renders the view (R31) and returns it — re-prompting is the caller's decision, not a driver loop.
4. **On failure** — the model raises, or its output is malformed (not a list of act dicts with known types) — record the failure and pause at the seat (R13, mechanism flagged below). No contribution is fabricated, ever.

## Interpretations stated for examination

1. **The briefcase source.** Cases are §3.5's piece, but the record already carries case events and the fold tracks each seat's current case version. The driver takes the briefcase **from the record**: the latest case event recorded for the seat, payload and version. If no case stands recorded for the seat, the driver does not wake the model — there is nothing authorised to work from. Whether the case's three §3.5 acts stand is the office piece's judgement, not the driver's.
2. **Wake reasons, computed from the record.** The seat's baseline is its own last recorded act, or its case's issue, whichever is later. Reasons after that position: a contribution on the seat's part or answering its work; a comment on its contribution; a gate outcome at a joint of its part; a disagreement naming its claim. If a case stands and the seat has never acted, the assignment itself is the reason. No qualifying events → no wake. **Orchestrator notes** are named in R11 but their event type belongs to §3.8 (a later piece); this piece computes reasons from the event types that exist and flags the note reason as arriving with §3.8.
3. **The failure mechanism (R13).** No failure event type exists in the vocabulary. Proposal, following the doorway's own REJECTION pattern: a new event type `DRIVER_FAILURE`, appended by the doorway on the driver's report (authored by the doorway, naming the seat, the failure kind, and the seat's part), with the paused set for that part computed by the doorway from the recorded tree exactly as for an escalation — the fold applies it the same way. The run pauses at that seat; nothing is fabricated. This extends the framework vocabulary by one type, recorded here and in the build record, not silently.
4. **The model callable is the piece's boundary.** Live provider adapters (which provider, which endpoint) are not in this piece; the driver machinery, wake assembly, submission, and failure handling are, tested with scripted model callables. Consequence stated plainly: the §7 item "two live seats hold a job in the bubble…" still cannot complete until a provider adapter and §3.5 cases exist; this piece does not claim it.

## Not in this piece

The office and case issue (§3.5), onboarding (§3.6), the gates mechanism (§3.7), orchestrator functions incl. notes (§3.8), provider adapters, any scheduler (R29 forbids one).
