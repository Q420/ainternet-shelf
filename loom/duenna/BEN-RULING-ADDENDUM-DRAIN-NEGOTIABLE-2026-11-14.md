# Ben's ruling addendum — the STATUS drain ruling is negotiable (2026-11-14)

Ben's own words in the TerrAIrium chat, 2026-11-14 ~05:02 MST, given immediately after Alex's F-3 design decision landed (Mode B rejected; a plan-only architecture investigation commissioned, with Alex noting the candidate shape may change the frozen interface):

> "That ruling that I made for the status is negotiable."
> "whatever makes the system work more fluently, you can change it."

## Effect

- The drain ruling of 2026-11-14 (BEN-RULING-C0-DRAIN-2026-11-14.md) stands as the record of the objective: **the final STATUS must be delivered reliably; failure must never be silent.** That objective is NOT negotiable.
- The ruling's MECHANISM — empty the channel before exit, by a teardown drain — IS negotiable. So is the frozen descriptor/interface arrangement, where a change makes the system work more fluently.
- This addendum widens the authority of Alex's plan-only architecture investigation: candidates are no longer confined to shapes that preserve the drain or the exact frozen interface. Each candidate must still name exactly what it changes, its failure modes, and the tests that would prove it — and any concrete change still requires its design to be reviewed (Alex) before it is built; no build is authorised by this addendum.
- Recorded by Remmy from Ben's messages in chat; his words above are verbatim.
