# ADR-001: Reuse the accepted prototype's record half as the build substrate

## Status

Proposed — recorded from COLLABORATION §11; takes effect when Ben rules on the Stage 1 design.

## Context

The framework needs a durable record layer: an append-only event history, mediated agent access, independent structural checking, and a read-only observer. The accepted Loom prototype (Stages 1–4, integrated evidence gate passed 2026-11-21) already provides that record half, proven under examination with scripted drivers in the agent seats. It does not provide live agents, the bubble as a working surface, the office, onboarding, or live gates.

## Decision

Build on the prototype's record half as the substrate and replace the scripted drivers with live seats. The bubble is built as the working surface over its event history; the harness becomes the seats' doorway; the checker serves as examiner instrumentation without replacing the examiner's judgement.

## Consequences

- Effort goes to the missing living parts instead of re-proving the record layer.
- The build inherits the prototype's constraints (Python substrate, its event model); if examination finds the substrate cannot carry the bubble honestly, this decision reopens as a recorded correction.
- The prototype's own record stays in the Loom folder as source material; this project pulls from it at build time under this decision.
