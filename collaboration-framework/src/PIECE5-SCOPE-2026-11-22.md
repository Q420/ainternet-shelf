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

## Addendum — the three boundaries settled with Vane (2026-11-22)

On her scoping examination (filed `VANE-PIECE5-SCOPING-REPLIES-2026-11-22.md`):

**A. Classification over six fields.** Flag 2 is amended: the office diffs against the superseded version on **all six** R14 content fields — assignment, tree + highlighted part, evidence_boundary, verification_list, account, authority. Any change → semantic. (Record note: R16's sentence names three fields with the gloss "(a mechanical generation error)"; the examiner reads the exception against all six. The build follows her reading — the stricter direction; the dangerous error is a semantic correction taking the light route.)

**B. Every R14 field has a recorded source; ungrounded = verification fails.**

| Field | Recorded source |
|---|---|
| tree | `RUN_COMMISSIONED` payload's tree, verbatim |
| part (highlighted) | the commission's recorded brief for the seat (`briefs[seat].part`); must be a part of the recorded tree |
| assignment | the commission's recorded brief (`briefs[seat].assignment`) |
| verification_list | the commission's recorded brief (`briefs[seat].verification_list`) — the case names what needs verifying because the commission does |
| evidence_boundary | derived from the record: the material ids of `MATERIAL_SEALED` events whose recorded boundary includes the seat |
| account | the commissioned seat itself (`RUN_COMMISSIONED` seats entry) |
| authority | the §4 defaults for the seat's commissioned role, taken from the doorway's act-authority matrix |
| version | 1 for a new case; superseded version + 1 for a correction |

If any field cannot be grounded from those sources, generation fails verification and no case events are recorded (flag 3, as approved).

**C. The first-content rule, explicit.** A version's content is established by its **earliest content-carrying act** and never replaced: for version 1, CASE_VERIFIED carries the full content (the fold gains content-on-verified-if-none, mirroring the rule Piece 4 set for CASE_ISSUED); for a corrected version, its CASE_CORRECTED (already first-wins since Piece 4 round 2). A later CASE_VERIFIED or CASE_ISSUED for the same version never replaces the established content. The suite tests this, including a duplicate verification carrying different content.

## Addendum 2 — the last two boundaries, and the fold amendments they ride with (2026-11-22)

On her scoping follow-up (filed `VANE-PIECE5-SCOPING-FOLLOWUP-2026-11-22.md`) and her system-level examination (`VANE-SYSTEM-EXAMINATION-2026-11-22.md`):

**D. Preflight before append.** The office's sequence is fixed: generate the draft in memory → validate it fully (every field grounded per Addendum B, part in the recorded tree, seat commissioned, R14 complete, internally consistent) → compute the classification → **only then** append events, in the required order (v1: CASE_VERIFIED carrying the content; correction: CASE_CORRECTED → CASE_VERIFIED). A failed preflight appends **nothing** — no CASE_CORRECTED, no CASE_VERIFIED. A draft is examined before it is an act.

**E. Classification enforcement — owned by the doorway.** The office computes the six-field classification and submits it; the **doorway guarantees it**. On any CASE_CORRECTED submission the doorway recomputes the diff between the case's established current content (the highest established version's content) and the submitted corrected content, over the six fields. If the payload's `representational` value disagrees with the recomputed classification — or the submission names a version other than the established version + 1 — the act is refused, the refusal recorded as a REJECTION, and the event is not appended. The fold thereafter trusts a classification the doorway has verified, never a caller's assertion.

**F. Fold amendments riding with this piece** (from her system examination, points C and D):
- **Exact issuance order.** `version_issued` requires the full chain in order — correction (where applicable) < verification < examiner act (judgement or notification) < authorisation. A judgement or notification recorded before verification cannot issue the version.
- **First verification stands.** The first CASE_VERIFIED for a version establishes both its content (v1) and its verification position; a later CASE_VERIFIED replaces neither. (Authorisation re-issue, as settled in Piece 4 round 1, is unaffected.)

**G. Piece 5 acceptance tests (explicit).**
1. Invalid initial case → preflight fails, **zero** case events in the record.
2. Invalid correction → neither CASE_CORRECTED nor CASE_VERIFIED appended.
3. Duplicate verification carrying different content → established content and verification position unchanged on replay.
4. Late judgement (CASE_JUDGED before CASE_VERIFIED) → the version never issues on those acts.
5. Late notification (CASE_NOTIFIED before CASE_VERIFIED) → same, representational route.
6. Forged classification → a CASE_CORRECTED whose `representational` disagrees with the doorway's recomputed six-field diff is refused and recorded as a REJECTION; the event is not in the record.
7. Field-by-field → changing each of the six fields alone classifies semantic; the notification route cannot issue any of them.
8. Wrong seat → a case for an uncommissioned seat fails preflight.
9. Wrong tree part → a brief naming a part absent from the recorded tree fails preflight.
10. Incomplete R14 → a commission brief missing a required field fails preflight; nothing is issued.
11. Version transition → an issued correction still requires the seat's acknowledgement before work resumes (Piece 4 regression).
12. Replay consistency → folding the same history twice yields identical case content, classification, and issuance state.
13. Atomic pair → a failure injected between the two appends of a correction leaves **neither** event in the record; the head and the case's established state are unchanged.

**H. The correction pair commits atomically (addendum 3, 2026-11-22).** The store's discipline is caller-owned transactions: appends accumulate uncommitted and one `commit()` lands them together; anything that fails before the commit rolls the whole transaction back. The office's correction route uses exactly that: both acts are validated first (authority, and the doorway's classification recompute against the established content — neither check depends on the pair's other event), then CASE_CORRECTED and CASE_VERIFIED are appended inside **one transaction with a single commit**. All-or-none is therefore a property of the store, not of office care. The doorway gains a paired-submission path for this; its single-act path is unchanged.

## Out of scope for Piece 5

Onboarding (§3.6, Piece 6's neighbour), gates (§3.7), orchestrator functions beyond the office (§3.8), the observer (§3.9). The §7 "two live seats" acceptance still awaits a provider adapter. Stage 4's mechanisation of briefcase-building is out of scope per §1 — this piece is the core form §3.5 specifies.
