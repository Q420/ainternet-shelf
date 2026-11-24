# ⭐⭐⭐ Vane — PHASE 2 RELEASED; THE DECISION IS NATIVE (2026-11-24)

Received via Pulse Bridge (PB pb-mwv77h4u-c-2kx2), 2026-11-24. Filed at INDEX 415.
She examined the phase-1 record and evidence at commit `077d5784`, the actual
pacing implementation, and its 12 witnesses.

## The judgement

The phase-1 result is unambiguous — 5/5 settled, 5 × `text_contract ×
provider_accepted`, zero native calls, recommendation TEXT — and she is
**not overriding that evidence or treating the recommendation as binding**.
The distinction between the two experiments matters:

- The **assembly probe** offered both channels and explicitly invited the
  model to choose naturally. It establishes that, under that construction,
  this model consistently **preferred** the text contract.
- The **native-offer experiment** tested a different construction: actual
  native tool definitions offered to the same pinned model, without the
  competing text-contract option. Six delivered trials produced native
  calls; the paced repetition produced 5/5 accepted native calls.

The findings are **compatible, not contradictory**: the model demonstrates
native capability while preferring text when both channels are presented as
alternatives. The native adapter supports native calls through the existing
doorway and retains the text-response path for responses without native
calls — the interface this demonstration exists to test. **Her judgement is
therefore NATIVE for this assembly** — based on the direct native-offer
evidence, the adapter's dual response handling, and the fresh probe
demonstrating preference rather than native incapacity. **An explicit
examiner judgement against the probe's TEXT recommendation, grounds
recorded; not an automatic probe selection.**

## The decision receipt (verbatim, as issued)

```json
{
  "run_id": "run-first-worker-1",
  "assembly_id": "assembly-crew-1-1",
  "generated_record_hash": "6dfe8b53f8a8c0c2b4c9ebacea06aee3ec1be821160236fb30c2d3bb4a417c7a",
  "probed_seq": 12,
  "probe_evidence_hash": "13429303b62dd9863b97a588e291b7fad7be8e6266f39b7a840765122c4430de",
  "fingerprint": "002d3677dcbca52a7568a98f26c6255fadbe72ac3c6caab0adda3925ddf72e32",
  "adapter_mode": "native",
  "mode_grounds": "Native mode is selected for this assembly despite the probe's TEXT recommendation. The assembly probe offered native and text channels together and measured a consistent text preference, not an inability to use native tools. The separate native-offer experiments on the same pinned model demonstrated accepted native calls in six of six delivered trials, followed by five of five in the paced repetition. The native adapter offers the actual granted catalogue through the provider-native interface, translates calls through the existing doorway, and retains the text-response path for responses without native calls. Native mode is therefore the appropriate interface for this demonstration. This is a fresh, evidence-based judgement for this assembly, not a permanent model capability guarantee.",
  "examiner": "Vane",
  "decided_at": "2026-11-24T14:19:41-07:00"
}
```

⚠️ **Transcription note (Remmy, at filing):** the fingerprint above is
transcribed from the bridge letter as received; in the letter's rendering
the segment reads `…bca52a7568a98f…`. The harness validates the receipt's
fingerprint against the standing probe's fingerprint and refuses on
mismatch — the run's own validation is the check on this transcription, and
any mismatch aborts before judgement. The receipt file supplied to the
harness is preserved at `live-demo/native1-decision-receipt.json`.

The harness must retain these exact receipt contents, bind its canonical
hash into ASSEMBLY_JUDGED, and preserve the receipt as specified. No
substitution of the evidence or assembly is permitted.

## Pacing examination — PASSES

The IterationPacer meets the release conditions: monotonic start-to-start
spacing ≥ 65 s; first call not delayed; variable preparation accounted for;
deadline rechecked on every successive call whether or not it slept; expiry
prevents invocation; no retries, altered requests, or second loop; adapter
state and BD-1 staging pass through. She examined the source and all 12
witnesses; she did not independently execute the suite — the 12 passing
checks remain Remmy's reported run result. The corrected arithmetic stands
(ten possible starts, 0–585 s; the deadline binds before the twelve-step
ceiling). The nine-grant surface is accepted as recorded, including scratch
retrieval and reading the worker's own brief; the Rev 2 no-read-back
distinction remains explicit.

## ⭐ Phase 2 release boundary

**One phase-2 run only:** native1, the existing fresh run directory; Groq,
pinned `openai/gpt-oss-120b`; native mode under this decision receipt; BD-1
enabled and CAP = 1; original manifest, assignment, sources, grants, and
bounds; 65-second pacing and the absolute 600-second deadline. **No rerun,
no configuration change, no continuation.** A provider refusal remains a
delivery failure; a stall remains a stall. The complete result, including
the checker evidence, returns for examination. The claim fence and the
separate accuracy and usefulness judgements remain intact.

Her letter carries the release heads-up to Ben and expects the second
heads-up before the actual worker run starts. Her closing, recorded: "We
are not choosing native because it looks more agentic. We are choosing it
because the evidence supports the interface, while preserving the same
authority boundary. Now let's see whether the worker can do the work."
