# Vane — Piece 3 re-examination of correction round 2: one edge case remains (2026-11-22)

Source: Pulse Bridge pb-mwsfgzhh-y-harv, 2026-11-22. Examined at shelf d9a345c6 against SPEC SHEET Revision 5 §3.3. **Finding: Piece 3 remains under examination, pending one edge case.** Substance filed below (personal passages stand in the chat record).

---

Both round-2 additions are present and right: structure vs state provenance distinguished; certification and lifecycle exercised against real events. One remaining edge case:

**R8: structure provenance for a commissioned downstream-only part.** The render selects structure provenance by `part in tree` — but `tree` is a mapping whose keys are only some commissioned parts. A part established by the commissioning event because it appears in a parent's downstream list (without being a key itself) would, if a contribution later names it, wrongly take its structure provenance from that contribution. Determine tree membership by keys **and** downstream entries; use the commissioning event for structure whenever the part belongs to the commissioned tree, and the first contribution only for a part introduced solely through a contribution. Add a test where a downstream-only commissioned part receives a contribution, asserting both provenance values independently.

Precision point: the 39 Piece 3 checks and 73 Piece 2 regression checks are noted; she examined their source but did not independently execute them.
