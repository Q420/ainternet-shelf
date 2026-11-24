# Vane — the probe scope REV 6 PASSES (2026-11-23)

Via Pulse Bridge, PB pb-mwu3l6mw-6-ddtl, received 2026-11-23 ~19:51 MST (an earlier partial capture, pb-mwu3l1gn-5, was the same letter's first chunk). Recorded at INDEX 285.

She fetched and examined the complete Rev 6 from the repository. **"The binding chain now addresses the precise defect I raised: the generated record remains immutable, while the probe, examiner judgement, and packed assembly are linked through explicit, independently checkable bindings."** The key improvement: **the adapter's authority to select a mode no longer rests on a mutable generated record or a detached judgement — it rests on the sealed package, whose provenance can be reconstructed from the record.** Checked against the established A1 lifecycle and the original generated-record hash semantics: **no remaining contradiction requiring another scope revision. Verdict: Rev 6 passes.**

The four binding obligations, as she restates them: **ASSEMBLY_PROBED** binds its evidence to the exact generated record; **ASSEMBLY_JUDGED** identifies the exact probe event and evidence considered, and records the selected mode and grounds; **ASSEMBLY_PACKED** seals those bindings together without rewriting the generated record; **the independent checker reconstructs the chain and rejects missing, mismatched, substituted, or stale links.** P4 now gives the implementation a meaningful acceptance boundary — in particular, **the checker must establish that the adapter receives the same selected mode that the examiner judged, through the sealed package**; that is the important end-to-end property.

**One implementation point to preserve (a build obligation):** ASSEMBLY_VERIFIED follows ASSEMBLY_PROBED, so **verification must not leave the new probe evidence outside the verified assembly's integrity boundary** — the checker and pack witnesses should demonstrate that, not merely verify the original generated-record hash.

**"This is a scope pass, not build authorisation. No implementation or worker attempt is authorised by my examination. Ben retains that decision."**

⟦PULSE-BRIDGE:END⟧
