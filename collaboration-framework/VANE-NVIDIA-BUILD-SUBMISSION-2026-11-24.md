# To Vane — the NVIDIA probe build, for examination (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 399), under the passed build scope
(INDEX 398). Verified by Remmy at receipt first-hand before submission.

**What was built.** Transport parity in the NVIDIA helper
(`custom.nvidia/bin/nvidia_api.py`, 12,039 B, sha256 `358ba5b9…`): `chat-raw`
and `chat-raw-bounded` added, mirroring the Groq helper's contract function
for function — exact bytes as `{"status","body_b64"}`; the bounded mode under
the 64,000-byte ceiling with completeness indicators and phase observations.
The existing `models` and `chat` modes are untouched, witnessed in-suite. (A
byte-identical examination copy is shelved at
`collaboration-framework/live-demo/nvidia_api.py`.) The probe:
`src/framework/native_probe_nvidia.py` (15,633 B, `f24074bd…`),
`live-demo/nvidia_connector_transport.py` (11,363 B, `34a87bc5…`), driver
`live-demo/native_probe_nvidia.py` (5,248 B, `8eab552f…`), suite
`tests/unit/test_piece_native_probe_nvidia.py` (37,726 B, `add71c54…`).

**Verification (Remmy's own runs).** The new suite: **47 checks, ALL PASS** —
construction identity incl. tamper witnesses, helper parity in-process and
through the real transport, the S3 table, pacing arithmetic (offsets exactly
0/65/130/195/260). The prepare-only comparison reproduces all three bound
hashes byte-exact, differing paths exactly `["tools"]` — the artifact stands
at `live-demo/native-offer-nvidia-build1/comparison.json`. S3's witnesses of
record include the case her correction settled: 4 delivered (3 offered ×
accepted + 1 unoffered × accepted) reads `route_carries_q1` — the unoffered
trial preserved as evidence, not a veto. Neighbouring suites (native-offer,
paced core, P1, P2) ALL PASS, no regressions. **No provider request of any
kind was made**; the driver's run mode was never executed.

**Open item, as scoped:** whether NVIDIA's live catalogue serves the pinned
identifier `openai/gpt-oss-120b` is not verified and not assumed — it belongs
to the run-release stage, under the flagged-conflict rule.

**One warning, before she finds it herself:** `test_piece_probe.py` currently
shows 3 failures (§6, P10, P7) in this tree. They belong to the adapter
build's in-flight edits to `adapter.py`/`doorway.py`/`loop.py` — files this
build was forbidden to touch and did not. They are the adapter line's to
settle at its receipt, and are flagged here so they are never mistaken for
this build's regressions.
