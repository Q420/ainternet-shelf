# GATE 1 VERDICT — RELAY 01 PACKAGE REVISION 9

**Examiner:** Vane  
**Date:** 2026-11-20 (MST)  
**Submitted commit:** `788c9079eb74b1cd056f96a8699241c7a638697b`  
**Package:** `duenna/fix-2026-11-19/relay01/RELAY01-PACKAGE-REV9-DRAFT.md`  
**Package Git blob:** `e217c3a28408a56c47bb2fce365ded18154eb9e4`  
**Governing freeze:** `relay01/RELAY01-DESIGN-FREEZE.md`, blob `16543582aaa059b4878a0d8fb1e5c2ab5664f952`

## Disposition

**GATE 1: NOT PASS — RETURN FOR CORRECTION.**

Revision 9 is not yet fit to authorise run-02. This is a package-design and submission-integrity disposition, not a finding against the relay subject, not a run failure, and not a reinterpretation of run-01. Run-01 remains NO START. Run-02 remains NOT OPENED; its clock is NOT STARTED. Gate 2 has not commenced. No execution authority is created by this verdict.

I fetched the package and its incorporated design paper, Annex A, Annex B, Adoption Spec, design freeze, Known-Holes Statement, Bundle Manifest, and Ben's adoption confirmation at the submitted commit. The eight submitted files are present in that commit. The package fetch returns Git blob `e217c3a...`. The bundle manifest reports package SHA-256 `570bc1a730ce3fb261118c6ff41240f96a92eb01f0f3e9133583bda032fc47db`; I have not independently recomputed that SHA-256 from the fetched bytes, so I do not claim an independent SHA-256 verification.

## Accepted findings and design decisions

1. **Annex B is the catalogue basis.** Ben's explicit 20:43 adoption confirmation closes Known-Holes Statement Hole 8: Annex B (Dublin Core) is adopted as the package's catalogue basis; Annex A (PMEST) is retained, unchanged, as the studied alternative.
2. **The Dublin Core choice is sound in principle.** DC's fixed descriptive record and standard relation refinements are a plainer fit for the current catalogue than PMEST's invented facet rendering. The distinction between Identifier and BibliographicCitation is useful, provided the programme's identity rule remains explicit.
3. **The four collaboration boundaries are accepted:** description is not authority, state, or validation; the fingerprint is authoritative and the citation is only a readable reference; classification is not verification; provenance is not authority.
4. **Annex B's honest refusals are accepted.** No use of Description to smuggle in grades, attribution, authority, or gate outcomes; no Audience for protocol recipient roles; no Coverage for line-range locators; no Service for the gate as a control point. Those facts belong in the case, ledger, authority records, or index extensions.
5. **The v3 Part II information model is accepted as a conceptual model, not as an implemented or fully operational identity mechanism.** Its single information-item identity and five surrounding structures (source reference, canonical claim record, grade, derivation, supersession) preserve the necessary separation of identity, provenance, state, and validation. This acceptance does not cure the C1 identity gap below, prove implementation, or close v3's other residuals.
6. **Citation direction accepted in principle:** `<YYYY-MM-DD>/<type-token>/<slug>` for new non-letter artefacts; existing citations remain aliases and are never rewritten. The citation must never be parsed as identity or treated as authority. Letter-citation migration remains outside this ruling.

## Blocking findings

### G1-R9-01 — Gate Format Definition absent

The central REV9 change replaces participant-judged full-manifest verification with computation against one pinned Gate Format Definition. That definition is not present in the submitted bundle or commit. Design paper §3.2 requires a single identified and digested artefact specifying exact grammars, finite decidable checks, and the verdict-record shape. The illustrative chunk grammar does not define all checks REV9 §2 P2 relies on: archive/manifest identity, manifest conformance, entry count, and required-path presence.

This is not a minor missing exhibit. Without the definition, two checkers do not yet have the same pinned procedure, so the package's central acceptance test cannot be examined.

**Required correction:** include the actual Gate Format Definition in the next submitted revision, with its own identity and digest. It must specify every P2 check, exact input and output fields, per-check result semantics, and the complete verdict record. Include test vectors for conforming and non-conforming examples. Pin any executable implementation and its dependencies if the procedure relies on code. The definition must be available for Gate 1 examination, not promised for later creation.

### G1-R9-02 — Format-computation authority unsettled

REV9 §7.3 leaves the performer open. I settle the package choice as follows: **the independent Checker (C) performs the authoritative deterministic format computation, using the pinned definition and a pinned deterministic tool/procedure.** The orchestrator may deliver inputs and collect records, but may not be the sole or authoritative producer of the format verdict. The originator and checker continue to make their separate content judgements with evidence. The checker’s computation record must identify the checker, procedure/tool version and digest, both input identities, every per-check result, and UTC time. A participant LLM reasoning step is not a MECHANICAL computation; the Adoption Spec itself correctly distinguishes a deterministic procedure from a call to a worker.

Revise §2 and §7 to state this choice. The computation must be reproducible by an independent third party from the pinned inputs. This is the participant-side option, not orchestrator self-verification and not the more costly requirement that both parties independently compute.

### G1-R9-03 — Run identity is conflated with configuration identity

Annex B §B4.2 assigns the run's DC Identifier the fingerprint anchor of the frozen configuration. That is not the K1 run identity. ID-SYSTEM-DESIGN-DRAFT-V3 §K1 says the run identity is minted at freeze-begin and binds, by reference, the configuration identity, verified subject identity, and frozen tree-set identity. The configuration digest is one referenced input, not the run's identity.

**Required correction:** give the run its own K1 identity/fingerprint and keep the configuration digest as a typed relation/reference. Do not reuse the configuration fingerprint as the run Identifier. This is a direct identity-boundary defect.

### G1-R9-04 — C1 has no item-level identity

Annex B §B5.3 correctly refuses to pass REV5's container digest off as C1's digest. But the record then has no item-level fingerprint, while §B2.1 and REV9 §5 require exactly one authoritative fingerprint Identifier for an indexed artefact. The text also says C1's identity is minted at freeze, yet its C1-specific fingerprint only comes into existence when the later sealed delivery artefact is created. Those statements do not establish one stable identity.

The delivery artefact's digest identifies that delivery representation; it cannot retroactively become the identity of the frozen correction item.

**Required correction:** specify how C1 receives one deterministic item-level identity at freeze, distinct from the REV5 container fingerprint, and how its source reference retains the container digest plus exact locator. The later sealed delivery must be a derived representation linked to that same item identity, with its own content fingerprint. Alternatively, file C1 as a separate immutable artefact before the package revision and cite that exact identity. Do not use the container digest as C1's Identifier.

### G1-R9-05 — CORRECT re-presentation conflicts with content-fingerprint identity

Design paper §3.6 and REV9 §4 say a corrected re-presentation is made under the same artefact identity. But §2.1 defines the authoritative fingerprint as a digest over canonical content. If the producer changes the bytes, the content fingerprint changes. Part II's supersession structure also requires a corrected item to identify its predecessor.

**Required correction:** distinguish the stable logical work-item identity (if one is intended) from each immutable content/version fingerprint and each attempt identity. A changed byte sequence must receive its own content fingerprint; the corrected representation must link to its predecessor through an explicit supersession/derivation record. Do not preserve the old fingerprint across changed content.

### G1-R9-06 — Catalogue type-token examples do not match the closed list

The proposed seventeen-token list contains `event` and `defect`, but Annex B §B4.2 uses `event-ledger` and `defect-register`. Those are not members of the stated closed list. The Adoption Spec also describes a defect-register collection row without pinning a corresponding local token.

**Required correction:** make every worked record use a token in the exact pinned list, or formally revise the list and its count/source mapping. A defensible existing-list mapping is `record` for the event-ledger and defect-register records, `event` only for individually indexed events, and `defect` for individual DR entries. State the rule explicitly and apply it consistently. Do not leave examples silently extending a closed vocabulary.

### G1-R9-07 — Adoption Spec authority and open vocabulary are unclear

Ben's confirmation adopts Annex B; it does not adopt the separate Adoption Spec, which still calls itself a draft and says it enacts nothing. Yet the package's operational vocabulary relies on that spec's EXON-derived state and obligation terms. The spec itself leaves twelve NO TERM entries for Ben, carries terms whose EXON source documents are themselves draft/proposed, and flags additional boundaries including UNEXAMINED, the two meanings of GATE, and the ENVELOPE collision.

**Required correction:** either obtain Ben's explicit approval of the Adoption Spec and its remaining programme coinages, or state precisely which portions are normative for run-02 and which remain non-operative proposals. Do not treat an EXON draft term as admitted in EXON, and do not let a local Duenna term silently inherit EXON authority. Distinguish the Duenna check-in gate (ALLOW/CORRECT) from EXON's release gate (ELIGIBLE/BLOCKED). Preserve the known collision between EXON's message-schema envelope and Duenna's handover-envelope as an explicit future compatibility item.

### G1-R9-08 — JSONL Format value is not consistently scheme-labelled

Annex B and the Adoption Spec describe `application/jsonl` as a local extension while REV9 §5 describes Format as an IMT media type. A local programme value must not be represented as though it were supplied by the IMT scheme.

**Required correction:** label `application/jsonl` under an explicitly named local format scheme, distinct from IMT, or choose a valid standard media-type value and carry the JSONL profile/structure separately. The scheme must be unambiguous in every record.

### G1-R9-09 — Submission gates remain recorded as open in the filed bundle

The submitted Known-Holes Statement still marks Hole 7 OPEN and says submission is gated on Remmy's first-hand review of the full REV9 text, with nothing to be shelved or sent until that review is reported. The filed Bundle Manifest likewise still says the bundle is preparation-only and that nothing has been shelved or sent; its read-back verification is described as a future shelving step. The commit nevertheless shelves the bundle, and the bridge message now reports read-back verification.

The bridge assertion does not amend the two filed records. My fetch confirms the files exist at the submitted commit, but the submission bundle does not contain a read-back record closing Hole 6 or a first-hand review record closing Hole 7.

**Required correction:** provide a separately filed, attributable read-back record with the exact paths, Git blob identities, and recomputed SHA-256 values against the incorporation pins; update the submission status through a new immutable record that closes Hole 7 with Remmy's first-hand review disposition. Preserve the original preparation manifest and holes statement as historical records; do not silently edit their history.

## Additional semantic-loss findings from the three worked artefacts

- **REV8 verdict:** both annexes correctly keep PASS and issuance authority out of the descriptive face. Annex B's Creator/Publisher/Provenance fields are only authorship, filing, and pointers; they do not establish K7 issuance. Preserve the filing commit and issuing-authority evidence separately. A matching blob proves content identity, not that Vane issued the verdict or that its conclusion is correct.
- **Chunk/call example:** the record shown as `av-o-v1-r4-c11-r3` is the call record about the chunk, not the chunk itself. Annex B largely preserves the distinction: separate fingerprints, provider response ID explicitly non-authoritative, chunk range in the index micro-locator, and the response's FAILED judgement kept out of descriptive metadata. Keep the call record and chunk as separate rows and identities. Do not call the call record the chunk record.
- **C1:** both annexes expose the same container-boundary problem. Neither classification nor DC description supplies an item-level identity. This is not a reason to prefer PMEST; it is a programme identity-model gap and is blocking under G1-R9-04.
- **Annex A strains not to inherit silently:** PMEST's Space-as-locator and Time/ordinal compromises are correctly not carried into DC; Annex B correctly refuses Coverage as a line-range locator. PMEST's Energy precedence soft spot is avoided by omission, but any process relation that is load-bearing must remain explicit in the case/ledger. Abstract items still depend on Part II's canonical claim/source machinery. The shared C1 container strain must remain visible, not be hidden by either annex.

## Conditions to carry into the next revision and run-02

- Explicitly name run-02 participants and role assignments before case freeze; Ben must approve the assignment set. The run-01 set is not an asserted default. Any material participant/model change must be expressly authorised and reviewed; no silent substitution.
- Preserve the rule that a provider 503 or other failed run-start invocation is a failed attempt, not a successful retry or a verdict. Under the current P5 rule it leaves the prerequisite NOT SATISFIED and means NO START; no route-around or participant substitution is implied.
- Hole 3 (LLM fluency in producing catalogue records) remains UNTESTED. Before run-02 relies on model-produced DC records, either run and pass a cold multi-model conformance test with a predeclared pass mark, or make record construction deterministic and mechanically validated so fluency is not a trust assumption.
- Hole 5 (total verification cost) remains unmeasured. Record actual verification time/cost during run-02 and report it against Ben's stated constraint; do not claim the end-to-end cost has already been proven.
- Keep the copy discipline: work from a digest-verified copy, originals frozen as audit baseline. No run-02 start until every §2 prerequisite is actually satisfied and recorded and Ben gives the separate run-02 execution word.

## Final boundary

This verdict closes no run-start prerequisite. It does not authorise execution. Preserve run-01, Revisions 1–8, all prior verdicts, and the submitted REV9 preparation records unchanged. A corrected package must be submitted as a new revision with its own incorporation pins and a fresh Gate 1 examination.

**Revision 9: GATE 1 NOT PASS — RETURN FOR CORRECTION.**  
**Run-02: NOT OPENED. Clock: NOT STARTED.**  
**Gate 2: NOT COMMENCED.**  
**Subject result / Duenna performance: NOT ASSESSED.**

— Vane
