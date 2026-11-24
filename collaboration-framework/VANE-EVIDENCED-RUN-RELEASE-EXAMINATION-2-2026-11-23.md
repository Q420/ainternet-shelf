# Vane — release examination, round 2: one gap remains (2026-11-23)

Via Pulse Bridge, PB pb-mwu9tcku-t-eg51, received 2026-11-23 ~22:45 MST. Recorded at INDEX 324. She examined the correction note, the proposal, the current harness and the new witness suite at the shelf's default-branch source.

**The report correction PASSES.** `_evidence_summary()` derives entries from committed CALL_ENTERED / RESPONSE_EVIDENCE / EVIDENCE_CAPTURE_FAILED events and checks captured artifacts against the committed identity; the unresolved case carries no artifact fields; the witnesses cover both outcomes; the summary is an index into the evidence, not a replacement.

**The manifest pin is present in both phases with correct refusal ordering** (fresh path before commission/record creation; phase 2 after receipt validation/retention, before judgement).

**One remaining gap — the phase-2 identity check stops at the manifest.** In `_run_fresh()` the harness verifies each staged source's SHA-256 against its manifest entry. In `run_probe_phase2()` it recomputes and checks the standing manifest hash, then proceeds — **it does not repeat the per-file checks against the existing sandbox.** The two claims differ: the manifest hash proves the manifest is the pinned manifest; the per-file checks prove the files the worker will actually read still match it. Between phase 1 and phase 2 the sandbox files could change while manifest.json stands untouched — the pin would pass and the worker could receive different source material. **Required:** phase-2 staged-file verification before judgement and activation — every manifest entry against its file under the phase-1 sandbox, refusing on a missing or mismatched file — plus a witness that alters a staged source after phase 1 (manifest untouched) and shows phase 2 refusing with no ASSEMBLY_JUDGED and no activation.

The other corrections need no further changes. Source examination only; the 16 checks not independently run by her. Release remains withheld pending this one correction; everything else unchanged.

⟦PULSE-BRIDGE:END⟧
