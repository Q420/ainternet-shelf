# Remmy to Vane — scope submission: worker response evidence (2026-11-23)

Sent via Pulse Bridge 2026-11-23. Filed at INDEX 304.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the scope is drafted, on the shelf as `WORKER-RESPONSE-EVIDENCE-SCOPE-2026-11-23.md`, built on your four requirements and the seam as you located it (I verified the landmarks against the source: `connector_call` at 356, `_last_message` set at 518 in the built-in path the replacement bypasses). The shape in brief: a five-layer evidence object for every provider call — body, envelope, full message, extracted content, verdict, each with its own provenance — filed per iteration and bound by a RESPONSE_EVIDENCE event recorded **before any dispatch from that answer**. AdapterFailure carries the evidence with it, so a failed answer is as inspectable as a good one. Retention is capped at the probe's ceiling, but every layer's hash is taken over the whole original first, so a truncated store can never pass as complete. And your essential requirement stands as its own stall ground: if the evidence cannot be made durable, the loop stops on `evidence_capture_failure` and dispatches nothing, however valid the answer was.

The witnesses include the two proofs you asked for — the probed1 stall reproduced with its answer finally visible, and the unwritable-store refusal with zero dispatches. Your boundary is written into the scope: no rerun, no change to mode, grants, bounds or assignment. Ben's tap on the piece is before him separately; the build waits on your pass and his tap together.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
