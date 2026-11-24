# Attempt 7 — release proposal (2026-11-23)

For Vane's release examination (reserved at INDEX 255), under Ben's authorisation (INDEX 256). The assignment, sources, manifest and result criteria stand exactly as the first-worker run scope (INDEX 188–190) fixed them; only the route, model and access mechanism are as settled since. Nothing here reopens the retrieval piece (passed, INDEX 255).

## Configuration

- **Route/model:** Groq, pinned `openai/gpt-oss-120b` (as attempt 6; identity pin stop active pre-activation).
- **Assembly:** full A1 lifecycle, the sealed record declaring the **retrieval-v3** contract (generator's retrieval path); catalogue derived from the grants under v3.
- **Grants (explicit, two authority paths):**
  - *Source path* (manifest-bound, the three staged files under `sources/`): `sandbox.list`, `sandbox.search`, `sandbox.read_range`, `sandbox.read`.
  - *Scratch path* (`scratch/`, the worker's desk): `sandbox.write`, `sandbox.list`, `sandbox.search`, `sandbox.read_range`, `sandbox.read`.
  - The deliverable is written at **`scratch/brief.md`** — the one run-configuration change from attempts 1–6 (where brief.md sat at the sandbox root), required by the two-path discipline: sources are read-only evidence; everything the worker writes lives on its own desk. The harness collects the brief from there. The assignment's substance (a ≤~600-word plain-words brief, inventing nothing, disagreements named) is unchanged.
- **Bounds {12 steps, 600 s} — proposed to stand**, judged from the witness counts: the R5 scripted run completed a harder retrieval pattern (list → search → read_range + notebook round-trip + re-pull → yield against a 58,423-byte corpus) in **5 iterations**; the real assignment's plausible path (list, search/read the needed sections, compose, write, yield) sits inside that shape with headroom for a real model's less direct route. On the Groq route, attempt 6's calls took 1.59 s and 0.64 s; 600 s is a guard, not an expectation.

## Envelope evidence

- Attempt 6 was refused at **134,605 bytes** rendered (HTTP 413) — the only empirical refusal point; Groq's exact limit is not published to us and is not claimed.
- The passed design's measured packages: R5 witness requests **10,831–20,087 bytes** (dispatcher-captured, committed artifact figures, INDEX 255).
- Attempt 7's worst credible package, by construction of the caps: ≤36,000 retrieved content (the aggregate ceiling) + ~5,516 catalogue (the six-tool grant set) + provenance/dispatch material of the attempt-6 order (~12,305 at 31 events) + ~1,589 case + ~1,846 overhead ≈ **57,000 bytes** — under half the refused size, with the retrieved component hard-capped rather than estimated.

## Harness work under the release (before the run, verified pre-activation as before)

`first_worker_run.py` gains the retrieval assembly: the retrieval-v3 contract, the two-path grant set above, sources staged identically (pre-run manifest sha256 `bd6f3cae…` must stand in the evidence boundary before activation, as the run scope requires), the brief collected from `scratch/brief.md`, the watch feed's agent pane live. Attempts 1–6 and their directories stand untouched; attempt 7 runs in a fresh directory.

## Result discipline (unchanged)

Yield/stall/decline are all results, reported in the four classes; a completed brief is judged by Vane claim-by-claim (two passes) and by Ben for usefulness, as separate findings; the checker verdict is reported whatever it is.
