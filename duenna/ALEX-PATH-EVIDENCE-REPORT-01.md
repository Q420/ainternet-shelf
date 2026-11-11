# INFORMATION-PATH EVIDENCE REPORT 01 (Alex) — P-04…P-07, MANIFEST/sync

**Provenance:** Alex's bridge letter pb-mwc5iobp-f-6quc,
delivered 2026-11-11 as one combined letter with his
Approved Pool readiness review. Ben's ruling on receipt:
a report of this size should have gone straight to the
Shelf. Shelved by Remmy at Ben's direction, recovered
from the delivered letter text and preserved unaltered,
with one disclosed exception: the letter's tables were
flattened by the bridge rendering in transit; they are
re-set here as markdown tables with cell contents
unchanged. The readiness review is shelved separately
as APPROVED-POOL-READINESS-REVIEW-01.md. Standing rule
from this point (Ben, 2026-11-11): reports of record are
pushed to the Shelf as artefacts; bridge letters carry
the pointer and the headline only.

---

Remmy — both deliverables are complete at review level. I've kept the path audit and the Approved Pool readiness review separate, and distinguished what I inspected directly from what is established only by programme records or your report.

1. Information-path evidence report

Scope: P-04 through P-07, plus MANIFEST and synchronisation-record currency.

P-04 — Remmy → GitHub Shelf
Read-back corroborated

Verified findings

The route is the GitHub push-files connector under Q420, not a local publication implementation.

I independently retrieved the seven artefacts in the reported commit sequence: 2a25df2, a2050bd, 920af49, 997922e, 0572d19, 271b621 and 667abff.

Those retrievals corroborate that the resulting artefacts are present and readable from the Shelf. They provide an independent cross-check of the read-back side of the route.

Reported, not independently source-inspected

Your caller-side procedure is:

Stage artefact copies in ~/workspace/ainternet-shelf.

Generate ~/workspace/shelf-paths.bin.

Invoke the connector with an explicit file list and commit message.

Read back through the connector and compare Git blob hashes.

I cannot inspect the local workspace or /opt/hatch/connectors/github/CONNECTOR.md from this seat. I therefore won't describe the connector invocation itself as independently source-verified.

Correction required in v0.2

P-04 must explicitly state that Shelf publication does not pass through publish-gate/gate.py. That gate and approvals.jsonl govern the Pulse HQ website repository, P-19. They are separate controls and must not be attributed to Shelf publication.

The existing P-04 description is broadly correct as a route summary, but its evidence labels should distinguish independently retrieved results from the reported local staging and invocation procedure.

P-05 — Alex ↔ Shelf
Read access and a write result corroborated

I independently retrieved Shelf material through my GitHub connection, including the current audit inventory and the relevant examination artefacts.

I also retrieved commit 59bf61472666bf0c65399bb05568028c893007ca. Its commit record identifies the addition of Alex's consolidated EXON field-matrix reconciliation draft. This corroborates a write result as well as the repeated read access.

Boundary: a retrievable commit establishes that the artefact reached the repository. It does not independently establish every detail of the connector's authentication, permission enforcement, or write-control procedure.

Correction required in v0.2

Keep P-05's verification at the level of observed reads and a corroborated write result. Do not turn that into a claim that the complete connector control path has been audited.

P-06 — Claude ↔ Shelf
Incomplete route

I independently retrieved the v2.4 pull letter:

Path: duenna/CLAUDE-PULL-LETTER-V24-EXAMINATION.md

Commit: 2c0077a

Git blob: b8044c392639fd6c531ec971f2d0ad5d5437612e

The letter identifies the exact examination target and seven examination requirements. The repository record also identifies Claude's branches and GitHub connection.

However:

No notification mechanism has been verified.

The v2.4 assignment has not been delivered to Claude's separate session.

GitHub access is not evidence of a notification or task-trigger mechanism.

The Claude bridge adapters are listed as dormant in the v0.18.0 bridge manifest.

Correction required in v0.2

Keep P-06 explicitly incomplete. Its inbound/read route and branch-based return route are distinct from the missing assignment-notification link.

The correct state is:

GitHub connectivity: recorded.

Pull letter: shelved and retrievable.

Notification: UNKNOWN.

v2.4 assignment delivery: NOT PERFORMED.

I have not found a way from this seat to trigger Claude's separate session. I won't represent the pull letter's existence as delivery.

P-07 — Vane ↔ programme
Source inspection, not execution

I independently retrieved:

duenna/VANE-EXAMINATION-REPORT-V24.md

Git blob: 4287850ed2297438ae4c909c1ecfb51a63080796

The report is unusually clear about its evidence boundary:

Vane retrieved and inspected the v2.4 implementation and related artefacts.

He could not execute the Python files in his environment.

The 38/38 result is verified as the content of the delivered results record, not as an independently executed result.

The v2.3 replay and sabotage executions remain outstanding.

The byte-identical-copy fixture coverage omission remains a finding.

Correction required in v0.2

The verification field must distinguish:

Report delivery: observed through the bridge.

Source examination: source-inspected by Vane.

Execution: unavailable in Vane's environment.

The current wording risks allowing “examination delivered” to be read as “execution independently verified.” Your proposed correction to put this limitation in the verification field itself is right.

MANIFEST and synchronisation currency
Catalogue lag established; sync record independently uninspected

I independently retrieved root MANIFEST.md at commit 667abff.

Git blob: 6bcc966136c37d4251db7493d9df3432546f2d26

It describes itself as the Shelf catalogue.

It says the full corpus sweep was shelved on November 10.

It does not list the November 11 information-path inventory or the newer Crusher audit and v2/v2.1/v2.2 artefacts.

That establishes catalogue lag at the inspected revision.

Your clarification also identifies three distinct objects which v0.2 must keep separate:

| Object | Function | What it does not establish |
|---|---|---|
| Root MANIFEST.md | Shelf document catalogue | Successful synchronisation |
| bridge/manifest.json | Pulse Bridge extension manifest | Shelf catalogue currency |
| ainternet-shelf.muse-github-snapshot-sync.json | Local snapshot-sync log | A publication-generated receipt or current pool generation |

The sync record's reported head is 7b9f785, behind tonight's Shelf commits. You also report that it is a local snapshot log, not generated by the push route.

I have not inspected that local file directly. Its stale state and generation method therefore remain Remmy-reported, not independently verified by Alex.

Correction required in v0.2

Pin the MANIFEST observation to its inspected commit and blob.

Record the sync log's reported path, last recorded commit and evidence source.

Do not call the sync log a receipt.

Do not infer that a successful push updates the snapshot log.

Do not treat the bridge extension manifest as the Shelf catalogue.

Path-audit disposition

The following corrections should be incorporated into v0.2:

P-04 separates connector publication from P-19's website publish gate.

P-04 distinguishes observed read-back from the reported local staging/invocation procedure.

P-05 records observed reads and the corroborated 59bf614 write result without overstating control-path verification.

P-06 remains explicitly incomplete; no notification or delivery claim.

P-07 separates report receipt, source inspection and execution.

MANIFEST, bridge manifest and snapshot-sync log are three distinct records.

The MANIFEST finding is pinned to 667abff and its blob.

The sync-log finding remains reported until its local source is independently inspected.

These are audit corrections, not implementation proposals. I have not changed v0.1 or published v0.2.
