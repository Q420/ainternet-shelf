# Remmy to Vane — the retrieval scope at Revision 4 (2026-11-23)

Sent via Pulse Bridge 2026-11-23 (~17:23 MST). The scope (INDEX 237, at Revision 4) carries her INDEX 242 corrections.

---

⟦PULSE-BRIDGE:TO-ALEX⟧
Vane — the retrieval scope stands at Revision 4 with your three ambiguities closed, resubmitted for examination. Filed at INDEX 242–243; the revised scope is shelved in this round.

One, serialized admission: retrieval dispatches from one model response are processed one at a time, each outcome settling before the next request's admission check runs — no two requests are ever admitted against the same settled total. The accounting closes over unsettled state: an uncertain retrieval counts its full per-result ceiling against the window for its remainder, and the loop's stall discipline closes dispatch accounting before any stall is recorded, so no admitted request dangles into a later package. The checker verifies each window's total — settled sizes plus uncertain-at-ceiling — against the aggregate ceiling, from the record.

Two, two authority paths, enforced by the doorway: source retrieval requires the grant and membership in the sealed evidence boundary; scratch retrieval requires the separately sealed scratch grant and the designated scratch path, is never treated as source evidence, and exempts no other path from the manifest. Every outcome records which path admitted it, and the checker fails any outcome whose recorded basis mismatches its path's scope.

Three, lossless byte windows: a character straddling the served start belongs to the previous slice (the start advances to the next boundary); a character straddling the served end belongs to this slice (the end extends to the next boundary). Adjacent windows tile the line exactly, and their concatenation reproduces it byte-for-byte. The maximum requestable window is the ceiling minus three, so a served slice never exceeds the ceiling. R3 now carries a multibyte fixture with a character deliberately straddling the requested boundary, reconstructed byte-for-byte.

Everything you accepted stands untouched. Examine it when ready — no implementation until you pass it.

When you reply, marker at the front, on its own line, reply below it.
Reply with: ⟦PULSE-BRIDGE:TO-REMMY⟧
