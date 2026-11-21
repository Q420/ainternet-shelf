# QWEN–DUENNA A/B V2.4 — SINGLE-FIX TOOLS REVISION

Prepared under Alex's ruling (response to
pb-20261110-battery-voided-report). **V2, V2.1, V2.2 and
V2.3 are preserved unchanged. No battery runs.** Files:
tools24.py · demo24.py · DEMO24-RESULTS.json (63 tool
calls). Companion documents in the foundation package:
TREES-V24-AMENDMENTS.md · CLAUDE-FINDINGS-DISPOSITIONS.md ·
FOUNDATION-MANIFEST.md + FOUNDATION.json.

## The single fix

tools24.locate now populates `embed_text` in the search
records it builds for bm25_search — the missing field that
raised the KeyError which stopped the voided battery at
T01 Arm C. **No other change from tools23.py.** The diff is
one added line in one function, plus this version's header.

## Verification

demo24.py re-runs the full V2.3 fixture suite against
tools24 (D1–D3, N1–N8c) — every result identical to V2.3 —
plus the new fixture:

- **L1 locate:** the T01 pack search now returns FOUND with
  the correct section (r60-revision-change-record#009),
  through tools24.locate itself — no driver substitute
  exists in the frozen driver; run_c.py calls T.locate.

## The frozen foundation (summary)

The battery's whole execution stack is frozen and hashed
in FOUNDATION.json: tools24, the Arm C driver (run_c.py,
restored to the reviewed tools — the voided run's
driver-level locate substitute is removed), the runner
(run_v2.py), the A/B harness (run_ab.py), the BM25 ranker
(query.py), both tree documents plus the V2.4 amendments,
and the evidence corpus files. The runner ENFORCES the
freeze: it recomputes every hash at startup and aborts on
any mismatch; on a technical failure it records the
incident, writes BATTERY-STOPPED.lock, and any later launch
refuses while the lock exists. Removing the lock is the
physical trace of a new adjudication ruling. Copies of
every component are shelved with the manifest so the hashes
are independently verifiable from the shelf alone.
