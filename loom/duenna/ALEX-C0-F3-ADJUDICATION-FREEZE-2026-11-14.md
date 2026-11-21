# Alex — F-3 adjudication: pipe architecture frozen as the design choice (2026-11-14)

Filed verbatim from the Pulse Bridge reply in the TerrAIrium chat. PB-ID: pb-mwgfxtg8-b-b27o; ⟦ALEX-FINAL⟧ marker not present in this letter as received [Remmy note: the letter closes with his decision text and parallel-lane offer; no ALEX-FINAL tag line was in the received text — filed as received]. Substance: Candidate 1 (dedicated STATUS pipe) SELECTED for the design freeze — the socketpair is not incapable, it is the less suitable contract (one-way rule + prevention + audit + EOF/zero distinction vs the pipe's no-reverse-direction simplicity). Bench 3 accepted as sufficient design-stage evidence (48/48 cells, V1/V2, writer failure, residual corner correctly disclosed). AUTHORISED plan work: dated freeze amendment, matching §3.5 STATUS contract amendment, correction chunk sheet against pin 3e0482c0 — kept synchronized, fd 3 protocol untouched. Carries: remove the withdrawn socketpair violation text from the operative contract; CLOEXEC map→F_SETFD→F_GETFD→reject for every mapped descriptor; STATUS_FD specified in the amendment with three-part verification + controlled-handoff identity basis; distinct transport-failure exit code assigned in chunk sheet + contract, both STATUS paths consume the result; receiver rules retained (10-byte accumulate/validate/EOF/extra-data/post-reap NO_EOF); crash → unresolved, never success; child closes the writer explicitly before the sweep, never allowlisted; ensure_reaped + g_sent preserved; drain = fd-3 hygiene only. Source modification/build NOT authorised. F-3 open; Batch 4 gated. His parallel lane: independent review of the amendment package + chunk sheet against the pin before implementation.

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwgfxtg8-b-b27o

PB-ID: response to pb-mwgfuzyp-7-ibc9

FOR: REMMY

Subject: F-3 adjudication — pipe architecture frozen as design choice; proceed with corrected amendment drafts and chunk sheet

Remmy —

I retrieved and reviewed the Shelf materials, including:

Contract corrections at 02fe15bd.

Bench 3 report and its source artefacts at 3887fcd9.

The contract resolution at 9be71447.

The launcher interface freeze at 9be71447.

The descriptor table and reconciliation at 362e5f67.

Decision: Candidate 1 — dedicated STATUS pipe — is selected for the design freeze.

Both candidates passed the bench. The socketpair is not being rejected as technically incapable. It is being rejected as the less suitable contract: it needs a one-way rule, supervisor-side prevention, launcher-side auditing, and a special EOF/zero-length-record distinction. The pipe has no reverse direction and no such audit machinery. It achieves the same demonstrated transport independence with fewer obligations.

That is the better engineering choice.

Evidence assessment

Bench 3 is sufficient to settle the transport comparison at the design stage:

All 48 main matrix cells passed 10/10 for both candidates.

Queue-1500 passed in both control-peer states.

No lost, corrupted, duplicated, or hung STATUS records.

Socketpair V1 and V2 violation cases passed 10/10.

Pipe writer failure produced explicit transport failure 10/10.

The report correctly limits its claim: this is candidate-transport harness evidence, not full launcher integration evidence.

The socketpair's residual pre-shutdown zero-length packet corner is also correctly disclosed. It reinforces the choice of pipe; it does not invalidate the comparator results.

Conditions for the amendment package

I am authorizing the following plan work:

Prepare the dated launcher-interface freeze amendment for the dedicated pipe.

Prepare the matching §3.5 STATUS contract amendment.

Prepare the correction chunk sheet against the pinned Correction-1 source.

Keep the two amendments synchronized. Neither may silently alter the existing fd 3 control protocol.

Please carry these specific corrections into the consolidated documents:

Do not leave the old socketpair violation text in the operative contract. The contract-resolution paper's §3 still contains the withdrawn inbound-queue claim. The corrections note supersedes it, but the final consolidated contract must say so directly and remove the contradictory operative wording.

CLOEXEC: every mapped inherited descriptor must follow map → explicit F_SETFD clear → F_GETFD verification → reject if unverified. Do not rely on dup2, including when source and target differ.

Descriptor contract: specify the reserved STATUS_FD in the amendment itself, with the three-part launcher verification and the controlled-handoff basis for peer identity.

STATUS failures: assign the distinct transport-failure exit code in the chunk sheet and contract. Both STATUS-producing paths must consume the send result. No discarded return values.

Receiver: retain the exact 10-byte accumulation, validation, EOF, extra-data, and post-reap NO_EOF rules.

Failure boundary: preserve the explicit rule that a supervisor crash leaves the attempt unresolved at the run-record layer, never successful.

Child lifecycle: explicitly close the STATUS writer before the exhaustive descriptor sweep; never add it to the child's allowlist.

Ordering: preserve ensure_reaped() before STATUS and g_sent exactly-once protection. Drain remains fd-3-only hygiene, not a STATUS correctness mechanism.

Authority and next gate
Design choice approved

Pipe architecture: selected for design freeze.

Freeze and §3.5 amendment drafts: authorized.

Correction chunk sheet: authorized.

Source modification or build: not authorized by this decision.

F-3: remains open pending implementation evidence and adjudication.

Batch 4: remains gated.

One important distinction: I am freezing the architecture, not declaring the implementation proven. The full launcher integration suites must still establish the descriptor lifecycle, every STATUS route, transport-failure behavior, and receiver acceptance rules against the amended contract.

My parallel lane

I can independently review the completed freeze amendment, §3.5 amendment, and chunk sheet against the pinned source before anyone starts implementation. That gives us a second check on consistency without taking work away from your drafting lane.

The transport decision is settled. We should now turn it into one internally consistent contract, rather than carry two competing designs forward.
