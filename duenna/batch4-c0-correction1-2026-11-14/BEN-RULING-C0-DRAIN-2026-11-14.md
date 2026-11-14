# Ben's ruling — the C0 teardown drain (2026-11-14)

**The ruling, in Ben's words** (tap on the ruling card, widget-cb36953d, 2026-11-14 04:01 MST, America/Dawson_Creek; repeated in his own typed message the same minute):

> "Rule for the drain — empty the channel before exit, fix STATUS for good"

## What was put to him

Alex's C0 adjudication (pb-mwgcr9xk; filed verbatim at duenna/ALEX-C0-ADJUDICATION-2026-11-14.md, sha256 468fe98d…, shelved at 12c2873f) held C0 NOT CLEARED on one finding, F-3: the demonstrated STATUS-loss on launcher exit with unread channel records is a failure against Rev 8 §A.2's Stage 6 closure outcome (gate handling, STATUS, exit 0), and the weakened NQ5' assertion does not establish that outcome. F-1 and F-2 were ACCEPTED; the correction path is confined to F-3.

Alex declined to clear the proposed teardown drain under the existing authority, on one ground: it changes the residue Ben accepted at fcc9c452 (BEN-RULING-REV8-ANCILLARY-RESIDUE-2026-11-14.md), which describes the queued ancillary record as UNRECEIVED with its descriptor never installed in the collector. The drain receives that record at teardown and discards it. Alex held the drain requires Ben's ruling. Ben has now given it.

## Terms of the ruling

1. The drain is authorised as a chunked C0 correction, confined to F-3 and its governing contract. Nothing else in the C0 pin, the cleared receive design, or the accepted residue is reopened.
2. The residue bookkeeping is amended exactly as disclosed to Ben before his tap: on exit, the launcher receives any records still queued in its channel and discards them unexamined; any descriptor arriving with a drained record is closed on sight, never installed, never used, never acted on. No classification, no actuation, and no protocol outcome changes — the drain runs after the protocol is complete, on the way out, solely so the exit leaves an empty queue and cannot reset away the final STATUS.
3. NQ5' is re-asserted in its strong form: the STATUS packet (raw exit word 71) must arrive; its loss is a failure again. The drained residue is evidenced by the test-hook drain line, distinct from receipt closures.
4. The correction is built from the shelf, pinned, bundled and resubmitted to Alex for his C0 re-inspection. C0 clearance and Batch 4 remain gated on his disposition, exactly as before.
5. No installation, no setuid, no privileged execution, no subject call is authorised by this ruling.

## Record

- Ruling card: widget-cb36953d ("Rule for the drain — empty the channel before exit, fix STATUS for good" / "Decline the drain — C0 stays blocked while we find another way").
- Authority chain: Rev 8 (fba0a629 @ f13dbdac) → Ben's residue ruling (d50c1f6f @ fcc9c452) → Rev 8 CLEARED (043c9bfd) → C0 bundle (de84c076) → Alex C0 adjudication NOT CLEARED on F-3 (468fe98d @ 12c2873f) → this ruling.
- This record is shelved BEFORE the correction it authorises is built.
