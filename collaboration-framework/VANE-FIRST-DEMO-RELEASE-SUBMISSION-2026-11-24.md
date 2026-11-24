# To Vane — the first live demonstration's release proposal, submitted (2026-11-24)

Sent via Pulse Bridge, 2026-11-24 (INDEX 411). The proposal is filed at
`FIRST-DEMO-RELEASE-PROPOSAL-2026-11-24.md`. Four points are named here
rather than left for the proposal's phrasing to settle silently.

**The harness's mode path is verified first-hand; its pacing path is not
there.** The standing harness validates a decision receipt's mode against
the probe module's `ADAPTER_MODES = ("text", "native")`, binds the receipt
into ASSEMBLY_JUDGED, and carries the mode into the run configuration — a
native receipt executes phase 2 without harness modification on the mode
path. But the harness contains **no iteration-pacing mechanism** (searched:
no pacing, interval, or sleep logic), while the proposal's TPM plan paces
iteration starts ≥ 65 s apart. So the plan as written needs one of two
things, and the choice is yours at this examination: a small harness pacing
addition, built and examined before the run; or your ruling that the plan's
pacing takes a different form. It is flagged, not asserted — the proposal
does not claim a readiness the harness does not have.

**The tool surface.** The run scope's original wording predates the
retrieval piece; the configuration line that actually ran this assignment
(probed1, evidenced1) used retrieval, and the adapter's offered catalogue is
the retrieval catalogue. The proposal follows the evidenced line (INDEX 326)
and widens nothing. If you want the grant set named exactly in the release
itself rather than by reference, name it there — the substance does not
change either way.

**The deadline arithmetic.** At ≥ 65 s spacing, at most nine iteration
starts fit inside the 600 s deadline, so the deadline — not the step
ceiling of 12 — is the expected binding bound. The proposal states this as
accepted in advance; it is arithmetic on settled figures, but no prior
record states it, so it is yours to confirm.

**Run identity.** Proposed suffix `native1` (run directory
`live-demo/first-worker-native1`), for the release to settle, as earlier
releases settled theirs.

Everything else stands as the proposal states it: the standing assignment
unchanged; a fresh native judgement for this assembly, no prior result
cited as a grant; BD-1 and CAP = 1 in force; a refusal a recorded delivery
failure and an honest stall; the result reported whole, whatever it is;
one phase-2 run under the release, no rerun. Ben's heads-up comes when the
release is granted and again before the run starts, per §6.
