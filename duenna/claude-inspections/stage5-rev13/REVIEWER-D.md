# Rev 13 inspection, agent D: sections 6–7, scope notes, Parts 3–4

Source: /mnt/user-data/attachments/475f6377-dfad-5672-a7f4-a435c6bdea33/581de8c8-attachment.txt
Lines read in full: 3814–4105 (292 lines).
Cross-check reads outside the range: 3660–3715 (Batch 6 and §5 G1 wording), plus grep hits for cross-referenced terms.

---

## D-1 (High): Build go issued while the second inspection stood at "not yet"; no Rev 12/13 verdict

- Lines: 3980–3982 (§7 step 3); 4054; 4065; 4066
- Quote: "Only after both inspections stand"
- What is wrong: §7 step 3 makes Ben's build go conditional on both inspections standing. Part 3 C records Claude's only verdict as "Fit to build from: not yet" (on Rev 11, about 22:09 MST), and states "Claude has issued no verdict on Rev 12 or Rev 13." Ben's go followed at 22:22 MST, quoted as "Alex approves it, I approve it". Rev 13 is described as cleared (4054, 4064) by Alex alone. The go's stated precondition was not met, and the file gives no record that it was waived.
- Fix: Record the 22:22 go as void against the §7 step 3 precondition, or re-issue it. Batch 2 and any further build step stop until Claude files a Rev 13 verdict as a retrievable artefact, not chat text. Part 3 C should state the build status as "not authorised pending second inspection".

## D-2 (High): The two inspections are not independent, though §7 says they must be

- Lines: 3977–3978 (§7 step 2); 3948 (§6.3 item 5); 3921 (§6.3 item 4); 3882–3884 (§6.3 item 1)
- Quote: "neither inspector's verdict is an input"
- What is wrong: §6.3 item 5 says the catalogue reversal "strikes a point he accepted, on the second inspector's reasoning" (3948). Item 4 says "Rev 12 names the one exception (Claude's finding 3)" (3921). Claude's Rev 11 findings were folded into Rev 12 and 13, and Alex's Rev 12 re-inspection adjudicated those changes. Alex's Rev 12 clearance therefore takes Claude's verdict as an input, which §7 step 2 forbids.
- Fix: Either state in the spec that Alex's Rev 12/13 adjudications were made with the Claude findings visible and are therefore not independent, or have Claude re-inspect Rev 12 and 13 from the spec text alone, with the findings withheld until after the verdict. Add to §7 step 2 that an amendment answering an inspector's finding cannot be cleared by the same inspector who raised it.

## D-3 (High): Stage 6 authorisation predates the gates it is supposed to follow

- Lines: 3994–3997 (§7 step 7); 4067 (Part 3 C)
- Quote: "effective once the build passes its gates"
- What is wrong: §7 step 7 requires Ben's Stage 6 authorisation to be "against the inspected package, the calibration certificate (§5.3)". Part 3 C says Ben's Stage 6 authorisation was given "2026-11-12 ~19:13 MST" and is "effective once the build passes its gates". That date is before the Stage 5 go (22:22), before any build gate, before inspection, and before the calibration certificate exists. Either the 19:13 authorisation is not the step 7 decision, or step 7 is not being followed. Under §6.1 item 1, the interrupted-write repetition must be decided in the step 7 authorisation, and no such decision is recorded.
- Fix: State in Part 3 C that the 19:13 item is not a Stage 6 authorisation. Record a new step 7 authorisation after the package is inspected, naming the run count, battery and the §6.1 decisions. Remove "effective once the build passes its gates" from the record.

## D-4 (High): Stage 5 provider or model contact is recorded, contrary to the zero-contact rule

- Lines: 3935–3936 (§6.3 item 5, "no request to the provider host is made in Stage 5 at all"); 4067 ("No model call is made or authorised anywhere in Stage 5"); 4085 ("confirms the provider failures"); 4023 ("the Crusher comparison")
- Quote: "No model call is made or authorised anywhere in Stage 5"
- What is wrong: Part 4, Basis 1, records HTTP 429 provider failures on Crusher retrieval calls during Batch 1 (Q3's first attempt, Q6's two attempts). Batch 1 is Stage 5 work. Crusher is also named in the scope notes as a parked project that must not be "smuggled into Stage 5" (4023–4026). The file never says what Crusher is. If it calls a model or provider endpoint, Stage 5 contains provider contact, and Part 3 C's statement is false. The record does not show that this was reviewed as a breach.
- Fix: Define Crusher in the record. If it reaches a provider or model endpoint, file a breach record for Batch 1, quarantine its output, and have Alex and Claude rule on it before Batch 2. Add an explicit line that Crusher's retrieval is out of Stage 5 scope, or amend §6.3 item 5 to cover it.

## D-5 (High): Provenance of the "recovered catalogue response" is not shown to be design-time snapshot

- Lines: 3932–3936 (§6.3 item 5, freeze evidence is "the design-time catalogue snapshot"); 4059 (Part 3 B.4)
- Quote: "F-2's recovered catalogue response"
- What is wrong: §6.3 item 5 says the Stage 5 freeze evidence is the design-time snapshot "pinned by its hash in the re-freeze amendment", with no provider request. Part 3 B.4 says the adapter_config_sha256 changed to 6cf57195… because of "F-2's recovered catalogue response", which was "incorporated at 82111456" and "CLEARED". The file does not say whether this response came from the design-time snapshot or from a live provider call. If it is a live call, §6.3 item 5 is breached. If it is the snapshot, the snapshot hash has changed, and the re-freeze amendment named in §6.3 item 5 is not the one now in force.
- Fix: File the provenance of the F-2 response (source, timestamp, whether any request left the environment). Confirm that the re-freeze amendment pins the 6cf57195… hash. If the response came from a live request, treat it under D-4.

## D-6 (High): G1 is not passed, S1 is "carried open by agreement", and §5 forbids partial passes

- Lines: 3683–3686 (§5, "All five gates must pass" and "no waiver recorded in prose"); 4058 (Part 3 B.3)
- Quote: "S1 carried open by agreement"
- What is wrong: §5 requires all five gates to pass before the package is offered for inspection, with "no partial pass and no waiver recorded in prose". Part 3 B.3 records G1 "expressly NOT passed" and S1 "carried open by agreement", deferred to Batch 6. An agreement recorded in prose is a waiver of the kind §5 forbids. §7 step 5 also requires G1–G5 to pass before inspection, and Batch 6 is the checkpoint that runs them (3671–3672), so deferring G1 to Batch 6 is consistent with §4 only if Batch 6 precedes inspection, which the file does not show in this range.
- Fix: Record G1 as "not yet run" in Part 3, with no reference to "carried open". Remove "by agreement" or move it to a written amendment that inspectors clear. Confirm that Batch 0 and Batch 1 freeze acceptance does not depend on G1.

## D-7 (High): The authority for Batch 2 is contested, and its only record is a builder paraphrase

- Lines: 4046 (source record, "in the day's memory record"); 4048 ("the grant runs through Batch 2 built under Spec Rev 13 at its pin"); 4050 (note on form, verbatim withheld); 4104 (Alex's letter, "remains closed and unauthorised")
- Quote: "remains closed and unauthorised"
- What is wrong: Part 3 A says Ben's standing approval covers Batch 2's go. Part 4 says Alex's letter states Batch 2 "remains closed and unauthorised". The conflict is not resolved; 4104 only puts the question to Alex. The approval is recorded only as Remmy's paraphrase and "reading", drawn from Remmy's memory, with the verbatim withheld. §7 step 3 requires Ben's decision to be his own, and §5 requires gate evidence to be preserved, not summarised. The grant also names a spec pin (Rev 13) that is no longer the operative baseline (D-8).
- Fix: Batch 2 does not start until Ben files a verbatim, retrievable record of his go, and Alex answers the checkpoint question in writing. The go should name the spec revision actually in force (see D-8).

## D-8 (High): The operative baseline differs from the Rev 13 pin, with no amendment and no re-inspection

- Lines: 3984 (§7 step 4, "Deviations from this spec stop the batch (§2.1)"); 4031–4034 (scope notes, the divergence "is an amendment item ... never a silent preference"); 4048 ("Spec Rev 13 at its pin"); 4057 ("Supersedes: the spec's nominal identity values"; "the 'wsl' reading accepted by the requirement's intent"); 4059 ("adopted into the baseline")
- Quote: "Supersedes: the spec's nominal identity values"
- What is wrong: Part 3 B changes the environment of record (VM to laptop room), the measured identities (uid 999/997, gid 986/985), and the adapter_config_sha256, and marks these as superseding the spec. The scope notes say a divergence is an amendment item, not a silent preference. §7 step 4 says deviations stop the batch. None of this is recorded as an amendment to the spec, and Part 3 says Batch 2 proceeds "under Spec Rev 13 at its pin". The environment change was accepted on "the 'wsl' reading ... by the requirement's intent", which is an inspector interpreting the spec, not an amendment.
- Fix: Issue Rev 14 (or a dated amendment) listing each superseded value, its measured replacement, the evidence hash, and the inspector who accepted it. Re-inspect under §7 step 2. Re-state the Batch 2 authority against Rev 14's pin.

## D-9 (High): The launcher-language exception is declared "approved" by the spec itself

- Lines: 3876 (§6.3 heading, "inspectors judge them"); 3919–3924 (§6.3 item 4)
- Quote: "not an amendment still to be sought"
- What is wrong: §6.3 item 4 says a different language for any component "is an inspector-approved amendment", and then records the C launcher as "the approved exception ... not an amendment still to be sought". Nothing in the file shows Alex or Claude approved this. Claude's Rev 11 finding 3 raised the issue, and Claude has not verified Rev 12. A spec cannot approve its own exception to an inspector-approval rule. The §6.3 heading says the inspectors judge these items.
- Fix: Mark the C launcher as a proposed exception pending inspector approval. It becomes approved only when the inspector's verdict is filed. Delete "approved exception" and "not an amendment still to be sought".

## D-10 (High): Receipt confirmation is discharged by a build gate, not by the examiner

- Lines: 3871–3874 (§6.2, "discharged by gate G3/G4's step-0 verification"); 3991–3992 (§7 step 6, "confirmation of the receipts")
- Quote: "discharged by gate G3/G4's step-0"
- What is wrong: §7 step 6 requires the examiner (Alex and Claude) to confirm receipts against the supervisor's issuance record at inspection. §6.2 says that duty is "discharged by gate G3/G4's step-0 verification", which is a build gate. Build gates are run by the builder (§7 step 5, and the §6.4 rule that the builder examines nothing it built). The builder therefore discharges the examiner's check, and §6.4 and §7 are contradicted.
- Fix: Remove the discharge sentence from §6.2. Require the examiner's receipt check to be a separate step-6 artefact with the examiner's name. The G3/G4 step-0 output can be an input, not the discharge.

## D-11 (Medium): Gate holders and record locations are unnamed, and the builder authors the gate record

- Lines: 3985–3986 ("pass on preserved evidence"); 3688–3689 (§5, "not by trusting its summary"); 4066 (builder of record); 4081 ("Remmy is authorised to record the freeze")
- Quote: "pass on preserved evidence"
- What is wrong: §7 step 5 says G1–G5 "pass on preserved evidence" but names no holder who certifies a pass, no record location, and no re-derivation step. Part 3 and Part 4 are written by Remmy, the builder, who is also "authorised to record the freeze". The §6.4 rule that the builder examines nothing it built is not extended to recording the builder's own gate passes. §5 requires re-derivation, but §7 does not say who re-derives.
- Fix: Add a gate table to §7: each of G1–G5 with holder, evidence artefact and hash, re-deriver (not the builder), and PB-ID of the examiner's acceptance. Builder-written summaries are allowed only if the examiner's re-derivation is filed alongside them.

## D-12 (Medium): The build go does not name the builder, as §7 requires

- Lines: 3981–3982 (§7 step 3, "The go names the builder (§6.4)"); 4066 (Part 3 C)
- Quote: "Alex approves it, I approve it"
- What is wrong: Part 3 C says Remmy is builder of record "under Ben's build go" and quotes the go as "Alex approves it, I approve it". The quoted text names no builder. The builder is therefore inferred from the record, not from the go, which §7 step 3 requires.
- Fix: Attach Ben's go verbatim and check that it names the builder. If it does not, re-issue the go naming the builder.

## D-13 (Medium): The interrupted-write test has two different deciders, and no Stage 5 result is recorded

- Lines: 3818 ("UNDECIDED"); 3826–3827 ("It must be decided — by Alex/Ben"); 3998–3999 (§7 step 7, "deciding the §6.1 open items")
- Quote: "It must be decided — by Alex/Ben"
- What is wrong: §6.1 item 1 names Alex/Ben as decider. §7 step 7 gives the decision to Ben alone. Separately, Alex asked for the test at Stage 5 (3823–3824), and no Stage 5 result for it appears in Part 3 B or C.
- Fix: Name Ben as sole decider in §6.1 item 1, to match §7 step 7. Record the Stage 5 interrupted-write result, or record it as an open Stage 5 item that blocks inspection.

## D-14 (Medium): The 404 re-pin at Stage 6 is not classified against the invalidation rule

- Lines: 3831–3833 (§6.1 item 2, "a 404 there follows the §1.4 re-pin procedure"); 3855–3857 (§6.2, "3rd invalidation stops the run")
- Quote: "a 404 there follows the §1.4"
- What is wrong: The first authorised Stage 6 call is the one that establishes served status. A 404 there triggers a re-pin, which changes the pinned subject. The file does not say whether a re-pin is a run invalidation (counting toward the 3-invalidation stop), a pre-run correction, or a change that voids earlier runs.
- Fix: State in §6.1 item 2 that a re-pin is a pre-run event that counts as zero invalidations and voids no runs, or state the count. Add the classification to the §1.4 procedure text.

## D-15 (Medium): The 120 s per-attempt timeout may exceed the 60 s budget tier

- Lines: 3858 ("60 s / 300 s / 3,600 s / 4 h"); 3864–3865 ("retry bounds 2 attempts, 5 s"; "timeout 120 s")
- Quote: "timeout 120 s (§7 Q6)"
- What is wrong: §6.2 lists four budget tiers but does not say which one covers an adapter call. Two attempts at 120 s plus the 5 s retry bound is 245 s. That fits the 300 s tier, but not the 60 s tier. If adapter calls fall under 60 s, the timeout breaks the budget. The file does not say.
- Fix: Name the budget tier for adapter calls in §6.2. Show the worst-case arithmetic (2 × 120 s + 5 s = 245 s) against that tier.

## D-16 (Medium): "Stage 5 freeze" and "after Stage 5" are never defined

- Lines: 3821 ("changed after Stage 5"); 3872 ("at Stage 5 inspection"); 3930 ("at the Stage 5 freeze")
- Quote: "at the Stage 5 freeze"
- What is wrong: The repetition default (Criteria §9 Q3), the catalogue evidence requirement (Adapter §1.4) and the examiner's receipt check all depend on an event called "the Stage 5 freeze" or "after Stage 5". §7 does not define that event. Batch 1 has been "frozen" in Part 4 while Batches 2–6 are open, so the term has at least two readings.
- Fix: Define the Stage 5 freeze as one named step in §7 (for example, after G1–G5 pass and the examiner's acceptance is filed). Use that term consistently in §6.1 and §6.3.

## D-17 (Medium): Two sections are headed VERBATIM but contain paraphrase and withheld text

- Lines: 4038 and 4071 (section headings "VERBATIM"); 4044 ("verbatim withheld"); 4060 ("The paraphrase is Alex's")
- Quote: "PART 3 — THE BASELINE EVIDENCE PACK, VERBATIM"
- What is wrong: The headings promise verbatim text. Part 3 A states the verbatim is withheld and is summarised from memory. Part 3 B.5 says the characterisation of Ben's report is Alex's paraphrase. Part 4 quotes only the disposition line and summarises the rest. Readers relying on the headings would treat paraphrase as the record.
- Fix: Change both headings to "summary of record" or equivalent. Keep each verbatim quotation where it exists, and mark each paraphrase as one.

## D-18 (Medium): Claude's Rev 11 findings have no recorded per-finding disposition

- Lines: 4065 (Part 3 C, "three medium, two low, plus two Batch 0 gaps")
- Quote: "three medium, two low, plus two Batch 0 gaps"
- What is wrong: The three high findings are dispositioned (folded into Rev 12 and 13). The three medium, two low and two Batch 0 gaps have no recorded disposition in this file. §7 step 2 says findings are answered by amendment and re-inspected "as the finding requires".
- Fix: List each of the eight non-high findings, with its disposition (fixed, rejected with reason, or open), the spec line where it was answered, and the inspector who accepted the answer.

## D-19 (Medium): The "twelve entries" in the Crusher log cannot be counted from the entries listed, and Q6 has no answer

- Lines: 4085 (Part 4, Basis 1)
- Quote: "Twelve entries present"
- What is wrong: The enumerated entries are: lane check (1), Q1, Q2, Q4, Q5 (4), Q3 first attempt (1), Q3 resumed (1), Q6 two attempts (2). That is nine. The record claims twelve but does not list the other three. The entry list also shows Q6 with two HTTP 429 failures and no answered record, yet the basis says the six retrieval questions were answered.
- Fix: Itemise all twelve entries by call ID and status. State whether Q6 was answered elsewhere, or record Q6 as unanswered and address the gap in the disposition.

## D-20 (Medium): "Identical" and "differs in exactly one line" are both claimed; the authoritative identifier is not recorded

- Lines: 4092–4094 (Part 4, item 4)
- Quote: "The resolved content is identical"
- What is wrong: The four T09 pairs differ in one line: "obligation-spec-text" in the as-built output versus "obligation-spec" in the canonical render. Calling the content "identical" is a judgement, not a result. The file does not say which identifier the pinned fixture file contains, and so which one the as-built output should carry. The canonical render matching the v1 manifest does not settle that, because the as-built hashes are the ones actually produced.
- Fix: Record which identifier the pinned fixture file contains, and whether the as-built output or the canonical render is the artefact that ships. Change "identical" to "identical except for the identifier line, which is recorded as ...".

## D-21 (Medium): G1 is labelled "network isolation proof" but §5 defines it as the sabotage battery

- Lines: 4058 (Part 3 B.3, "G1 (network isolation proof)"); 3691–3692 (§5, "G1 — The sabotage battery S1–S5"); 3711–3714 (zero-egress evidence as a sub-item of G1)
- Quote: "G1 (network isolation proof)"
- What is wrong: Part 3 treats G1 as a network-isolation gate, and says it is "Batch 6's obligation". §5 defines G1 as the S1–S5 sabotage battery, with zero-egress evidence as one of its sub-items. The record and the spec disagree about what G1 tests, so "G1 not passed" does not tell the reader which tests have passed.
- Fix: Use the §5 definition in Part 3. State separately which S1–S5 tests have passed and which zero-egress evidence items are filed.

## D-22 (Medium): The no-provider-credential and connector-path isolation claims have no evidence in Part 3

- Lines: 3896–3898 (§6.3 item 2, "the build environment holds no provider credential"); 3917–3918 (§6.3 item 4, "the sanctioned helper"); 4058 (Part 3 B.3, G1 not passed)
- Quote: "holds no provider credential"
- What is wrong: §6.3 item 2 says the build environment holds no provider credential and that G1 shows connector paths. The sanctioned connector helper is the live path (§6.3 item 4). Part 3 B.2 records capability sets and a loopback namespace, but no credential check and no connector-path check. G1 is not passed (D-6). The no-call rule is therefore asserted, not evidenced.
- Fix: File the credential-absence check and the connector-helper check as G1 sub-evidence, with the commands run and their output hashes, before Batch 2.

## D-23 (Low): Part 3 B.3 gives results with no hashes, bundle references only

- Lines: 4058 (Part 3 B.3)
- Quote: "28/28 freeze files byte-identical in-room"
- What is wrong: The 28/28 byte-identity, the 35/35 JCS conformance, and "custody trees ... live-tested" are stated without hashes or per-file results. Only the bundle shelf reference (894bde0b) is given. The claim cannot be checked from this file.
- Fix: Attach the per-file hash list or the bundle's manifest hash to Part 3 B.3.

## D-24 (Low): The "outdated" characterisation is disputed and left unresolved

- Lines: 4060 (Part 3 B.5)
- Quote: "The paraphrase is Alex's"
- What is wrong: Alex's letter says Ben reported the spec outdated. Remmy says no such statement exists. The file records the dispute but does not resolve it, and it bears on whether the spec was out of date when Ben's go was given.
- Fix: Either locate Ben's statement and file it, or record that none exists and that Alex withdraws the characterisation.

## D-25 (Low): Scope excludes live Shelf integration, but PILOT-TOOLS-01 includes shelf_lookup

- Lines: 4020 (scope notes, "no live Shelf integration"); 4067 (Part 3 C, "shelf_lookup")
- Quote: "no live Shelf integration"
- What is wrong: The scope notes exclude live Shelf integration. Part 3 C puts shelf_lookup inside the Batch 2 tool set without saying whether it reads the pinned snapshot or the live Shelf. The file does not say.
- Fix: State in Part 3 C that shelf_lookup reads only the pinned snapshot, and cite the spec line that says so.

## D-26 (Low): §6.3 status text is stale or inconsistent with Part 3

- Lines: 3882 ("stated as a proposal for the inspectors"); 3946–3947 ("Alex's re-inspection is asked to adjudicate"); 3923 ("approved exception"); 4064 ("the catalogue reversal accepted")
- Quote: "stated as a proposal for the inspectors"
- What is wrong: §6.3 items 1 and 5 describe the decisions as proposals awaiting inspection. Part 3 C says Alex has already accepted the catalogue reversal, and §6.3 item 4 calls the launcher an "approved exception". The spec body and the evidence record give different statuses for the same items.
- Fix: Give each §6.3 item a status line (proposed, accepted by whom, filed where), and make the spec body match Part 3 C.

---

## Summary by severity

- High: 10 (D-1 to D-10)
- Medium: 12 (D-11 to D-22)
- Low: 4 (D-23 to D-26)
- Total: 26

## NOT CHECKED

- Cross-referenced sources not read: Harness §§5, 6.1, 6.3, 6.6, 8; Adapter §§1.3(e), 1.4, 3.2, 3.6, 3.7, 7; Criteria §§1.1(6), 2, 3.3, 4, 5, 5.3, 6, 7.2, 8, 9; Plan Stages 5 and 6; REVISION-02 and REVISION-04 notes; spec §§2.1, 2.4, 3.4–3.7, 4 (batch list), 5.3. Whether each adopted default in §6.2 matches its source, and whether §6.1 item 1's repetition default matches Criteria §9 Q3, is unverified.
- Whether §4 places Batch 6 before the §7 step 5 gate check (affects D-6 and D-21).
- Whether the spec body's §3.5 and §5 contain the "wsl" environment requirement that Part 3 B.2 cites (affects D-8).
- Whether "the nine trees", "Harness §8 Q3" and "SE-1…SE-7" are defined consistently elsewhere in the spec (not read).
- Part 3 and Part 4 hashes, commit IDs and PB-IDs (for example 6cf57195…, 82111456, 894bde0b, 260796c8, 018a29c6, 4c6e0b31, 017a413a…, pb-mwel7brk, pb-mwfht1ot-b-861t): not resolvable from this file and no repository or Pulse Bridge access was used. I checked only that the figures repeat consistently inside the file (for example 1,156 sections in B.3 and Part 4).
- Test results (73/73 PASS, 35/35 JCS, 28/28 byte-identity, the Round 6 suite): not re-executed; taken as reported.
- Ben's verbatim go wording (Part 3 A): withheld in the file itself, so the quoted go at 4066 is the only text available.
- Lines 3660–3715 were read as a cross-check only. Lines 1–3659 and 3716–3813 were not read; grep hits for cross-referenced terms outside the range were not analysed beyond the lines cited above.
- Line 4105: read as the final line, no content.
