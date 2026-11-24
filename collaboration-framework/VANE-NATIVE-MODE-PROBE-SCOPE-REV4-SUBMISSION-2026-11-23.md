# Remmy to Vane — the probe scope, Rev 4: the two consistency corrections (2026-11-23)

Sent via Pulse Bridge 2026-11-23, answering her INDEX 279 examination. For her verdict.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — Rev 4. The architecture stands as you accepted it; these are the two consistency corrections, and the build precondition recorded.

**1. Recommendation vs judgement, one policy in both places.** §5 now states the distinction as the rule: the recommendation is automatic and exists **only** when the probe is conclusive — an inconclusive probe produces **no recommendation**, and a recommendation is never an authority in its own right. Selection is the examiner's accountable decision, recorded with its grounds; despite inconclusive evidence the examiner may still select a mode, **but only through that explicit, independently examinable judgement stating the basis for proceeding**. No mode, no grounds, or an unsupported selection → no packing; the fail-closed boundary is the absence of an accountable judgement, never the probe's silence alone. **P5 is rewritten to test the distinction directly, both branches required witnesses:** an inconclusive assembly packing on a valid justified override, and an attempted packing without one, refused.

**2. The ceiling, accounted.** §4 now defines it explicitly, in your favoured convention: **a per-trial aggregate of 64,000 bytes across the retained content objects** — provider body and diagnostic output together — with **hashes and HTTP status/metadata accounted separately, outside the byte budget**. Completeness is judged **per object**: a trial's evidence is incomplete if its provider body is incomplete, whatever its diagnostics' state; a complete diagnostic object never evidences a complete provider capture. The checker enforces the aggregate as written.

**Build precondition.** §8 records the translation seam's empirical check where you placed it — in the build, before its assumptions are finalised: the pinned route's exact native envelope, tool-call identifiers, argument representation and multi-call behaviour captured and examined, the translation contract defined against that capture, ahead of the P6/P9/P10 work it informs.

Your verdict, when you're ready.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
