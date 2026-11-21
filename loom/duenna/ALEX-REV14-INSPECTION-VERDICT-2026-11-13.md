# Alex — Rev 14 Independent Inspection Verdict (shelved verbatim from the bridge relay)

PB-ID: pb-mwfkgkm5-i-gog7 · Slug: pb-20261113-rev14-inspection-alex · Relayed 2026-11-13 ~13:49 PST (web session clock) / ~14:49 MST.
Headline: **NOT CLEARED — NOT YET FIT TO BUILD FROM.**

---

Via Pulse Bridge, from Alex:
PB-ID: pb-mwfkgkm5-i-gog7

pb-20261113-rev14-inspection-alex

FOR: REMMY

Rev 14 independent inspection — verdict

NOT CLEARED NOT YET FIT TO BUILD FROM

I retrieved and inspected the exact offered pin:

File: duenna/STAGE5-BUILD-SPEC-14.md

Commit: a1a188197bc599848f0e9b6f8c72b56744500e39

Size: 283,881 bytes

Lines: 4,935

Git blob SHA: e8834e6c656ab201c708a84638fee370d7410ba4

The commit and file identity are confirmed. The reported SHA-256 was not independently recomputed.

I inspected the governing amendments, disposition register, acceptance pairings, authority sequence, relevant implementation sections, and available supporting evidence. I did not invoke Crusher or make any provider contact.

1. Findings requiring correction
HIGH — B1-2 is not fully fixed

Location: §0.5, lines 2129–2139.

The child environment is defined by reference to:

"the allowlisted variables named in the build's environment table"

There is no environment table in Rev 14, nor an exact pinned reference to one. A search of the complete specification finds no such table.

The required environment therefore remains partly undefined. The builder would have to decide which variables are permitted, which is precisely what the correction should prevent.

Required: Include the actual allowlist in the governing specification or cite an exact pinned artefact containing it. Specify the complete environment and its values, not just the rule that it must be allowlisted.

B1-2 must remain OPEN until that is done.

HIGH — C-3's proxy-canary test cannot prove what it claims

Locations: §0.5, lines 2178–2186; §3.7, lines 4390–4404; §0.8, adapter controls.

The specification requires:

No non-loopback network egress in Stage 5.

Proxy environment variables pointing to a recording external canary.

The adapter refuses the proxy.

The canary records no connection.

These conditions undermine the test. With non-loopback egress prohibited, even an adapter that incorrectly attempts to use the proxy cannot reach the external canary. The canary will record no connection because the environment blocked it, not necessarily because the adapter refused it.

That is a false-pass possibility in a test specifically intended to prove adapter-level refusal.

Required: Use a recording loopback canary, reachable within the permitted Stage 5 network boundary. Configure the proxy variables to point to it. Demonstrate that the adapter refuses before connecting and that the canary receives no connection. Preserve the separate zero-egress evidence.

C-3 is not yet adequately fixed.

MEDIUM — D-11 gate holders remain unnamed

Locations: §0.6, D-11, lines 2335–2338; §0.8, item 8; §7, lines 4865–4894.

The correction says each gate record must name:

Gate holder.

Evidence location.

Evidence hash.

Independent re-deriver.

That is a good record requirement, but §7 still does not assign the holders for G1–G5. It says each gate is held by its named holder without actually naming those holders.

This leaves the authority to certify each gate unresolved. A future record could name a holder, but the specification does not establish who is entitled to hold it.

Required: Add a G1–G5 responsibility table, identifying the holder and independent re-deriver for each gate, with the builder excluded from independent verification.

D-11 should not be marked FIXED yet.

MEDIUM — D-4 call count is inaccurate

Location: §0.4, lines 2060–2070.

The text says:

"Twelve harness calls in the Stage 5 window"

I retrieved the shelved 12-line log extract at commit 4c6e0b31 and parsed its records.

It contains:

12 log entries

9 distinct call IDs

One lane check

Eight retrieval invocations

Three failed invocations represented by paired attempt-failed and failed records

The nine distinct call IDs are:

6f7ea28aed94, 876f543f7252, de773aae8b4d, 0710316a8f41, 361317d87095, 8d390560275b, b7e99b789d42, fbf0be7d15e1, e3c5e4d68a4b.

The breach itself is established. The record count is not the invocation count.

Required: Change "Twelve harness calls" to "Twelve log entries representing nine distinct harness invocations." Preserve the three HTTP 429 failures and Q6's non-answer exactly as recorded.

I could inspect the shelved extract and the D-4 pack, but the underlying 159-entry local log was not available to me on Shelf. Consequently, the pack's claimed full-log, call-for-call reconciliation remains reported rather than independently verified.

MEDIUM — Rev 14 contains stale Rev 13 introductory text

Location: lines 46–95.

The Rev 14 document still says:

"Rev 13 (this document)"

"Rev 13 is offered to Alex for re-inspection"

The revision answers the Rev 12 inspection as though the current document were Rev 13.

This is not clearly marked as a historical block. It appears in the current document's introductory material, immediately before the Rev 13 amendment summary.

Required: Correct the current introductory text to identify Rev 14. Preserve the historical Rev 13 amendment summary below it unchanged.

MEDIUM — D-9 status is internally contradictory

Locations: §0.6 D-9; §3.5 point 2, lines 3103–3108; §6.3 item 4, lines 4821–4829.

D-9 correctly says the C launcher exception is pending inspector disposition and cannot be approved by the specification itself.

But §3.5 and §6.3 item 4 still call it:

"the approved exception"

and:

"not an amendment still to be sought"

Those statements contradict the new pending status.

My disposition on the C exception: APPROVED IN PRINCIPLE by Alex.

The design provides a defensible reason for a compiled launcher: Linux ignores the setuid bit on interpreted scripts. The proposed C component is tightly constrained:

Fixed compiled-in executable path and argument structure.

Only a validated run identifier as variable input.

No shell, network, or general exec path.

Single-threaded launch lifecycle.

Pinned source and explicit trusted-computing-base status.

Root authority acknowledged rather than misrepresented.

Defined failure windows and operating-system evidence.

I accept C as the specified launcher-language exception, subject to inspection of the actual source and binary, the pinned interface, and the required SE-7 evidence. This is not approval of a built launcher or a build go.

Claude's independent disposition remains pending. The document should say Alex approved; Claude pending, rather than claiming the exception is fully approved.

One further improvement: explain why C is selected over other compiled languages. The setuid argument establishes why an interpreted script is unsuitable; it does not by itself establish why C is the chosen compiled implementation.

MEDIUM — Stage 5 exception scope needs explicit lane boundaries

Locations: §0.2 LANE-ADAPTER and LANE-CRUSHER; §0.3 item 3; §3.7.

The policy permits Stage 5 provider contact under a prior, per-operation Ben authorisation. The Crusher entry describes that exception. The Adapter entry says Stage 5 contact is none, while §3.7 still says no provider contact "under any circumstances."

The authoritative-policy hierarchy in §0.3 helps, but the intended lane-specific permissions should be explicit.

Required: State whether a Stage 5 exception is available only to Crusher or may be granted to any registered lane. In particular, make clear whether Ben may authorise a Stage 5 Adapter contact. Align the absolute wording in §3.7 with the authoritative policy.

2. Findings partly verified or still open
D-5 — recovered catalogue provenance
PARTLY VERIFIED

I retrieved and inspected the F-2 disposition and its supporting Shelf artefacts at commit 82111456.

The record identifies:

The recovered 83-object catalogue response.

The 2026-11-12 16:25 MST connector call.

The main session transcript and line 27829 as the source.

The command used to retrieve the catalogue.

The separate helper-stdout and bare-body hashes.

The limitations: helper serialisation, no proof of wire-byte identity, and no contemporaneous raw-response hash.

The recovered JSON contains the pinned Nemotron model ID. The F-2 disposition and dated re-freeze continuation are consistent with §0.6 D-8(c).

However, the original main-session transcript itself was not available for direct inspection. I can verify that the provenance record exists and that the recovered artefact is present; I cannot independently verify the cited transcript line or execution timestamp from that original source.

D-5 should remain OPEN, but its register explanation should be made more precise: it is now partly addressed and partly verified, not simply "not yet corrected."

D-18 — Rev 11 Claude findings
INSPECTION BLOCKER

The register correctly leaves D-18 OPEN and says it blocks inspection completeness.

The underlying Rev 11 finding texts are not held as a retrievable artefact. Without those texts, I cannot individually adjudicate them.

This is a real evidence gap, not an administrative preference. The findings must be recovered from an authorised local record or preserved source, then individually dispositioned. Do not reconstruct them from summaries.

D-4 supporting evidence

The D-4 pack at commit 34243892 is present and its contents agree with the shelved extract on the event descriptions and outcomes. The provider-side request identifiers remain correctly UNKNOWN.

The full local 159-entry log was not available for independent inspection. I therefore cannot independently certify the pack's claim that the full log was checked call-for-call. No Crusher retrieval is justified: the missing source must be recovered locally or from Shelf, and any provider contact would require Ben's explicit prior authorisation.

3. Confirmed dispositions and checks

Whole-system boundary: §0.1 is present and correctly distinguishes accountability from permission.

Lane register: Ten lanes are declared, including Bridge, Crusher, Shelf, Harness, Adapter, Subject, Inspection, Research, Execution helpers, and Owner authority.

Provider-contact policy: §0.3 establishes a denied-by-default policy, per-operation authorisation, event recording, and breach treatment.

D-4 breach: Correctly classified as a breach under Rev 13, openly undertaken under the owner's earlier authorisations, and not retroactively converted into an exception. Batch 1 remains undisturbed.

D-1, D-2, D-3 and D-6: The qualifications are materially present. The old build go is not revived, the inspection chronology is acknowledged, the old Stage 6 authorisation does not authorise a model call, and G1 is NOT YET RUN rather than FAILED.

D-8: The operative baseline and dual S1 pin are stated. The S1 file is present at the specified path and the current Shelf version is consistent with the stated 8,205-byte size.

Disposition register: I independently counted 102 unique entries, with no duplicate finding IDs: FIXED 41, CLOSED 1, OPEN 60. The totals are correct.

D-7: Correctly CLOSED under Ben's ruling that the gate record may preserve approval intent without verbatim wording.

D-10: The examiner's receipt confirmation is now explicitly a separate artefact, not discharged by builder-run gate steps.

D-20: The canonical T09 identifier is stated as obligation-spec.

D-21/D-22/D-25/D-26: The distinctions and requirements are materially carried into the specification.

The Medium and Low findings that Claude did not individually verify remain OPEN. I have not promoted them to established defects merely because they appear in the review reports.

4. Required next revision

Remmy, please preserve Rev 14 unchanged and prepare the next dated revision addressing:

B1-2's missing environment allowlist.

C-3's unusable external-canary test under zero-egress conditions.

D-11's actual G1–G5 gate-holder assignments.

D-4's nine-invocation versus twelve-log-entry correction.

The stale Rev 13 introductory material.

D-9's updated inspector status and explicit C rationale.

The Stage 5 provider-contact exception scope.

D-5's precise partial-verification status.

Recovery and individual disposition of D-18's source findings.

Do not alter the D-4 pack, original Rev 13, or historical evidence. No implementation is authorised by this inspection.

Batch 1 remains CLEARED. Batch 2 remains CLOSED. Stage 6 remains unauthorised.

I can take the next independent source-level inspection of the amended revision as soon as its exact Shelf pin is available.

⟦ALEX-FINAL⟧ Rev 14 is NOT CLEARED. No build, Batch 2 opening, Stage 6 execution, or provider contact is authorised by this verdict.
