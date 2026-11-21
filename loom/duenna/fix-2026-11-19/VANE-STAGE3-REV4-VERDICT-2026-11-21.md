# Vane — Stage 3 Brief Rev 4 Verdict: DESIGN SETTLED (2026-11-21)

Delivered via the Pulse Bridge, 2026-11-21 ~05:02 MST (PB-ID pb-20261121-vane-stage3-rev4-verdict-01). Examined artifact: Stage 3 design brief Rev 4 at shelf head afea55b9, compared directly with the preserved Rev 3. Verdict: **STAGE 3 DESIGN SETTLED** — Rev 4 is accepted as the design authority; build authority confirmed under Ben's existing prototype commission. The build (dispatched on Rev 3) is accepted as continuing, provided the implementation and tests conform to Rev 4. Transcribed from the bridge delivery as received.

---

Rev 4 fetched and examined at head afea55b9. I compared it directly with the preserved Rev 3 artifact.

**STAGE 3 DESIGN SETTLED**

The missing condition is now correctly included. The evidence-binding predicate explicitly requires:

- Every cited contribution is accepted.
- Every cited contribution touched the claimed facet.
- facet_version equals the version left by the latest cited contribution.

All three are explicitly fold-computed counting conditions, never submission refusals. A claim failing any condition remains recorded and counts as no claim. That is the required distinction.

The header also accurately describes the changes from Rev 3. The rest of the design carries forward unchanged. I found no further substantive drift in the artifact.

Build authority: confirmed under Ben's existing prototype commission, with Rev 4 as the settled design text.

One point about the sequence: I acknowledge that dispatch began against Rev 3 before my examination arrived. The governing requirement was already present in Rev 9, and you have explicitly pinned the full predicate to the builder. I therefore accept the build continuing, provided the implementation and tests conform to Rev 4, not merely the earlier abbreviated wording.

The rejected-contribution test is particularly important. It must demonstrate that the claim is recorded, does not count, and does not become a submission rejection.

The agreed boundaries remain:

- No live agents.
- TV-3, 4, 5, 9–20 as named obligations.
- Stage 4-dependent setup must be identified as deferred, not simulated or claimed complete.
- Full prior regressions.
- Source, tests, and build notes shelved together for examination.
- No silent corrections.

Rev 4 is accepted as the design authority. The next gate is examination of the actual Stage 3 implementation and its evidence. Design settlement is not implementation acceptance.

Good. We have the contract pinned down. Now let the machinery show its work.
