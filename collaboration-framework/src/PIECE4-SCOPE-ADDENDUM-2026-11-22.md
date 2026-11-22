# Piece 4 scope addendum — the issuance vocabulary gap (2026-11-22)

**Date: 2026-11-22.** Follows Vane's scoping replies (`VANE-PIECE4-SCOPING-REPLIES-2026-11-22.md`). Checking her point 1 against the record as built found a gap the build cannot paper over:

**The three R15 acts have no event types.** The framework vocabulary (Piece 2) holds only `CASE_ISSUED` and `CASE_CORRECTED` for cases — both orchestrator acts. There is no type for office verification, none for the examiner's sufficiency judgement, and none for the R32 acknowledgement. So "the driver must not wake on a case whose required issue acts do not all stand" is not checkable against today's record: a lone CASE_ISSUED event cannot show the other two acts. Equally, R33's `seat_stalled` state and R13's failure event need their representations.

**Proposed minimal representation** (put to Vane before code, since it decides what counts as authority to work; it is groundwork §3.5 builds on, not the office itself):

- `CASE_VERIFIED` (orchestrator) — the office verification act, naming {case_id, version}.
- `CASE_JUDGED` (examiner) — the sufficiency judgement, naming {case_id, version}.
- `CASE_ISSUED` (orchestrator, existing) — authorisation + issue; for version 1 its payload carries the case content (R14).
- `CASE_CORRECTED` (orchestrator, existing) — a corrected version's content, naming whether the correction is purely representational (R16).
- A corrected version stands issued when VERIFIED + JUDGED stand for it **and** a `CASE_ISSUED` for that version authorises it; the **representational route** needs VERIFIED + that authorisation + an examiner-recorded notification naming the case and version (a FINDING), without JUDGED.
- `CASE_ACKNOWLEDGED` (crew) — the seat's R32 acknowledgement of a newly issued version, recorded by its driver before the seat acts again.
- `DRIVER_FAILURE` — appended by the doorway on the driver's report (doorway-authored like REJECTION, naming the seat, kind, and part, origin explicit); the fold marks the seat `seat_stalled` (R33). No paused tree, no retry, no clearing event invented.

The driver's effective-case rule then reads: the highest version for the seat whose required acts all stand, with its content as recorded; no complete version, no wake.

## The representation as approved, with Vane's corrections (2026-11-22, pb-mwsfuqpc)

- The three acts stand as proposed: `CASE_VERIFIED` (orchestrator), `CASE_JUDGED` (examiner), `CASE_ISSUED` (orchestrator, authorisation for that exact version). The fold never infers one act from another; CASE_ISSUED alone is never sufficient. Version 1's content rides on its CASE_ISSUED; version identity and content are preserved exactly for replay.
- **R16 correction:** the examiner notification is its own type, **`CASE_NOTIFIED`** (examiner) — not a FINDING. Routes: semantic correction = verification + judgement + authorisation; purely representational = verification + notification + authorisation. **The fold knows the route from the correction's recorded classification** (the CASE_CORRECTED payload's representational flag), never from whichever events happen to be present.
- **R32:** `CASE_ACKNOWLEDGED` names the seat, case_id, and version; it is the crew seat's own act through the doorway under its identity. **The driver may carry it but must not manufacture it** — in driver terms, the acknowledgement arrives as the model's proposed act in the re-wake cycle, and the driver submits no other act for that version until it stands.
- **DRIVER_FAILURE** as narrowed: doorway-authored on the driver's report; seat, kind, part, explicit driver-report origin; the fold marks the seat `seat_stalled`; no paused tree, no retry, no clearing event invented in this piece.
- Case selection: highest version that completed its required route; an incomplete or superseded newer version is never the effective case; R32's acknowledgement gates acting on a new version.
