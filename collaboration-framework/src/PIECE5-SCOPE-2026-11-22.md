# Piece 5 scope — the office and briefcases (SPEC SHEET §3.5, R14–R17, R32)

Stage 2, piece 5 of 6. Pieces 1–4 passed. Scoping note written before code, per the pattern settled in Pieces 3–4; flags go to Vane first.

## What §3.5 requires

- The office is a **function of the orchestrator seat** — every office act is recorded under the orchestrator's identity, in its distinct acts. "The office" never appears as an unexplained authority.
- **R14** — a briefcase contains: the assignment; the whole process tree with the agent's part highlighted; the evidence boundary; the verification list (named); the account it works under; the authority it holds (§4 defaults); its version identifier.
- **R15** — issue requires three separate recorded acts: office verification (orchestrator — generated correctly from the recorded commission and tree; complete; internally consistent; version identifiable), examiner judgement (sufficiency), orchestrator authorisation. (The acts and their fold semantics stand from Piece 4, as amended through its correction rounds.)
- **R16** — corrections are new versions through the same acts; the proportionate exception (nothing about assignment, evidence boundary, or verification list changes) takes verification + notification + authorisation. Superseded versions remain; re-briefing is on the record only.
- **R17** — no agent authors, edits, or approves its own or another's case.

## What Piece 5 builds

`src/framework/office.py` — the orchestrator-side machinery, working through the doorway under the orchestrator's token:

- **Generate**: build the R14 case content from the recorded commission (RUN_COMMISSIONED: tree, seats) — never freehand: the tree is copied from the commission, the seat's part highlighted, version = next for that case.
- **Verify**: check the generated case against the recorded commission (seat commissioned, part in the tree, all R14 fields present and consistent, boundary well-formed). On success the office records CASE_VERIFIED; on failure it records nothing (flag 3).
- **Authorise**: record CASE_ISSUED carrying the authorised content for version 1 (corrections carry theirs on CASE_CORRECTED, per Piece 4).
- **Correct**: build the new version's content, compute its classification (flag 2), record CASE_CORRECTED then CASE_VERIFIED; the examiner's act (JUDGED or NOTIFIED) and the authorisation follow as their own acts — the office never performs the examiner's act.
- The examiner's judgement/notification remain the examiner seat's own doorway acts throughout; the office exposes the pending case for that judgement from the record.

## Flags for Vane (sent before code)

1. **Where version 1's content stands before authorisation.** The examiner must judge a case whose content, under Piece 4's fold, only enters the record on CASE_ISSUED — after the judgement. Proposal: the full content rides on **CASE_VERIFIED** (the act that attests it was generated correctly and completely), CASE_ISSUED authorises by name, and the fold takes a version's content from the earliest content-carrying act for it (VERIFIED for v1, CORRECTED for corrections), never overwritten later. The alternative — the examiner judging an office-presented copy outside the record — puts the judged thing off-record, which this framework exists to prevent.
2. **The R16 classification, computed.** The office classifies a correction by field-diff against the superseded version on exactly R16's three fields (assignment, evidence_boundary, verification_list): all three unchanged → representational; any changed → semantic. The classification is recorded in the CASE_CORRECTED payload, as Piece 4's fold requires — but computed by the office from the recorded versions, not asserted by whoever submits.
3. **Failed verification leaves no case events.** Generation and the office's checks happen before any case act; a case that fails verification never enters the record. (A draft is not a run state change.)
4. **Cases are generated for crew seats only**, and every office act is submitted under the orchestrator's token — R17 holds by construction, on top of the doorway's matrix.

## Out of scope for Piece 5

Onboarding (§3.6, Piece 6's neighbour), gates (§3.7), orchestrator functions beyond the office (§3.8), the observer (§3.9). The §7 "two live seats" acceptance still awaits a provider adapter. Stage 4's mechanisation of briefcase-building is out of scope per §1 — this piece is the core form §3.5 specifies.
