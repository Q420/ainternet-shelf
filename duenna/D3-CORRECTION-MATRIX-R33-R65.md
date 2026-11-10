# D3 Correction Matrix — Findings R33–R65

Consolidated by Remmy from the Round 7 register (R33–R38, verbatim
source: PROCESS-TREE-D3-REVIEW-RESPONSE-v0.7.md) and Alex's Round 8
review letters (R39–R65), for Alex's review. Prepared 2026-11-09
under Ben's tap; sequencing per Alex's ruling (consolidate first,
reconcile dependencies and overlaps, then ONE traceable correction
pass). This matrix changes no specification text, approves nothing,
and authorises nothing. Where a row compresses Alex's wording, his
letter governs.

Revision 2 (2026-11-09, Alex's matrix review, pb-mwa7dsux):
corrections A (R62 regrouped with R42), B (R42 moved directly
after the status step) and D (R59 traceability clarified)
applied. His item C — truncated status guards in the published
snapshot — was investigated: this source was complete; the
snapshot converter dropped wrapped bullet continuation lines.
The converter is fixed and the snapshot republished; the
finding is recorded in the programme log.

## Summary

- Identifiers R33–R65: 33 numbers. **31 active findings.**
  R58 is WITHDRAWN (Alex's own correction, folded into R38).
  R59 was never finally assigned — the finding first numbered R59
  in Alex's Part 11 letter is R61 under his numbering ruling
  (identifiers are never reused).
- By kind: **15 text corrections** (spec wording, explicitness,
  terminology, one mechanism addition), **2 status corrections**
  (PROPOSED material mislabelled as settled, at two sites),
  **14 acceptance-fixture additions** (coverage gaps — in every
  case the underlying rule was found sound; the evidence was not
  complete).
- Clusters that must move together are marked in each row and
  gathered under Dependencies. Status guards — things the
  correction pass must NOT silently settle — are listed after the
  matrix. A proposed pass order closes the document.
- Carried visibly, per Alex's own flags: **R44 remains open**
  (the reverse mixed-channel combination was still untested when
  he flagged it in the Part 7 review); the Round 7 register's six
  dispositions stand unaltered; D3 v0.7 remains frozen and
  unapproved; Stage 2 remains unauthorised.

## The matrix

Kinds: TEXT = specification text correction. STATUS = the
correction is to a status marking (and its consistent use).
FIXTURE = acceptance-coverage addition; no rule change.

| ID | Touches | Kind | Correction (Alex's, compressed) | Dependencies / guards |
|---|---|---|---|---|
| R33 | REQ-D-3 | TEXT | Add an explicit determination-admission rule: a determination enters the fold's running set only if (i) derived from execution-record evidence under channel (i), or (ii) arrived through channel (ii) cited to a preserved artefact basis whose own admission is recorded with it; a determination meeting neither is recorded in the evaluation record as non-admitted, with its basis — never silently folded, never silently dropped. | Evidence chain (R43, R50, R51): admission defines WHAT enters; R51 defines WHEN. Edit in chain order. |
| R34 | REQ-A-1 | TEXT | Conform A-1's Outputs and Behaviour to the two cases: a conditional instance links to its triggering event; an unconditional instance links to the binding as its cause — using REQ-K-3 (2)'s cause language verbatim so the requirements cannot drift apart again. | Same boundary as R39 — one edit step closes both. |
| R35 | D3-CANON-1 | TEXT | (a) Restate the identity claim to what the procedure delivers: byte-exact identity over the canonical serialisation, strings and keys unnormalised, numbers and member order canonical by scheme — retire the unqualified "exactly as authored." (b) Move duplicate-key rejection to the parse layer: the record parser rejects duplicate keys recursively, at every object level, before canonicalisation; canonicalisation's loud failure remains as backstop, not mechanism. | CANON cluster (R48; fixtures R49 test (b)). Edit (a) and (b) with R48 as one CANON-1 step. |
| R36 | REQ-K-3 | TEXT | Every CREATION entry identifies the instance it creates, unconditional instances included; the binding identity remains the cause reference; instance-free status is reserved for entries that genuinely concern no instance. (The "CREATION at binding" example of an instance-free entry is removed — it contradicts the model.) | Creation cluster. Its rule is what R63's identity fixture tests. |
| R37 | REQ-K-3 | TEXT | Define the CREATION block: the entries of one trigger form one contiguous block immediately after the triggering entry — the first follows the trigger, each subsequent entry follows the preceding CREATION entry, in pinned-contract rule order; no unrelated stream entry may intervene. | Creation cluster. R63's multi-instance fixture tests exactly this text; text first, fixture after. |
| R38 | REQ-H-4 / REQ-H-6 | TEXT | Define a separate append-only link/reference entry kind for the defect record (or an equally explicit linked-register mechanism) by which subsequently created affected evaluations are linked in — the original creation entry stays unmutated, the reciprocal reference is established. | ABSORBS R58 (withdrawn — same H-4/H-6 gap). The mechanism addition of the set; nothing else depends on it. |
| R39 | REQ-A-1 / REQ-A-2 | TEXT | Reconcile the instance-creation boundary explicitly: A-1's broad reading (every instance requires an external triggering event) vs A-2's unconditional creation at binding — make binding-as-trigger for unconditional rules explicit, WITHOUT changing the underlying semantics. | Same edit step as R34. |
| R40 | REQ-A-1 / A-2 / A-3 | FIXTURE | Add coverage: A-1 successful instantiation, kind preservation, the separate CREATION entry, the bearer-authorship prohibition; A-2 loud total failure (unresolvable role / demonstrated-impossible rule) and unconditional creation; A-3 the machinery-defect outcome for an unidentifiable bearer. | Creation fixtures — after the creation text step (R34/R39, R36, R37). |
| R41 | REQ-B-1 | STATUS | REQ-B-1 is labelled CONVERGED, but its mandatory pre-existing-evidence declaration is a PROPOSED semantic addition (origin: D3-R21); the approved tree does not require the declaration. Preserve the distinction; the addition must not be silently promoted to settled semantics. | One status discipline with R45 — both sites corrected, or the claim is not closed. Guards every later edit citing B-1. |
| R42 | REQ-B-1 / REQ-K-1 | TEXT | Make B-1's enforcement point explicit and single: the current text pairs an authoring-time check with a binding-time check conditional on "REQ-K-1 if adopted," contradicting the unqualified failure behaviour ("a malformed rule cannot be bound"). Either binding-time enforcement is unconditional, or authoring-time alone must be shown to guarantee malformed rules cannot reach binding. | Must not settle REQ-K-1's proposed semantics (R18; UX-4). Read together with R62's guard. |
| R43 | REQ-B-2 / REQ-D-3 | TEXT | B-2 must distinguish evidence establishment from state transition explicitly: an artefact never directly mutates an instance and never becomes a record event; the evaluator establishes a predicate from it, and that determination participates in ordinary REQ-D-3 derivation. The artefact channel's predicate-establishing ability must NOT be removed. | Evidence chain head (then R50, R33, R51). One consistency check across B-2 / D-2 / D-3 after the chain edits. |
| R44 | REQ-B-2 | FIXTURE | Mixed-channel coverage incomplete: add the reverse direction (artefact-progress + event-satisfaction) to the existing event-progress + artefact-satisfaction case; fixtures must show the artefact determination recorded at evaluation with eligibility declaration and evidence cited, and no synthetic execution event introduced. | Evidence fixtures — after the chain text. **STILL OPEN** (Alex, Part 7 review) — carried visibly until its fixture lands. |
| R45 | REQ-C-2 | STATUS | C-2 states eligibility exists only through B-1's mandatory declaration, treating the proposed addition (R41) as settled. Preserve the status distinction consistently at this second site. | Pairs with R41: one discipline, two sites. |
| R46 | REQ-C-1 | TEXT | Terminology: the fold begins at the CREATION entry (the defined term), everywhere; retire "creation event" phrasing, which leaves open an implementation treating the conditional trigger as the first fold event. | Terminology sweep across the document, not only C-1. Feeds the creation cluster's consistency. |
| R47 | REQ-B-6 / C-1 / C-2 | FIXTURE | Add: B-6's positive path (named judge accepted; that judge's identity used); C-1 unconditional creation at binding, plus a conditional trigger shown unable to establish progress/satisfaction even when its content would qualify; C-2's unpreservable-artefact → INDETERMINATE path. | Creation/eligibility fixtures — after the creation text step and the R41/R45 status step (C-2's fixture presupposes the corrected status). |
| R48 | D3-CANON-1 | TEXT | Give the content-identity exclusion a precise mechanical boundary: the exact excluded digest/identity metadata only; every other entry field remains digest-covered, lest a legitimate field be omitted by classification. | CANON cluster with R35 — one edit step. Interface with R55 (evaluation-record content identity under C-3). |
| R49 | REQ-C-3 | FIXTURE | Add fixtures for two stated failure rules: Unicode-composition differences in object KEYS (only string values are currently tested); duplicate exact keys failing loudly. | The duplicate-key fixture tests R35(b)'s parse-layer rule — fixture after the CANON text step. |
| R50 | REQ-D-2 | TEXT | State explicitly that derivation uses the record PLUS the predicate determinations admitted through B-2, those determinations retaining their cited artefact basis and never becoming execution-stream entries or synthetic events. A boundary clarification — explicitly NOT a widening of admissible evidence. | Evidence chain, second link (R43 → R50 → R33 → R51). |
| R51 | REQ-D-3 | TEXT | Fix when determinations become available to the fold: event-derived determinations at their entry's fold position; channel-(ii) determinations from the start; whole-record computation never moves evidence earlier — a determination keeps its actual evidence position, or the chronological terminal-lock rule is undermined by implementation timing. | Evidence chain, last link. R52's fixture tests this rule. |
| R52 | REQ-D-3 / D-2 area | FIXTURE | Add the artefact-first terminal-lock fixture: artefact-established satisfaction under PROGRESS: NONE, followed by a later blocker report, yields SATISFIED locked; the blocker is retained as an event to be explained; closure is discharged-as-SATISFIED. Tests channel-(ii) preloading and terminal locking together. | Depends on R51's text. Evidence fixtures group. |
| R53 | REQ-D-7 | TEXT | Make the guard explicit: the evaluator consumes the exact closed record the evaluation identifies (a fixed, identity-bound snapshot); derived entries exist only in the separate evaluation record; a later modification to the execution stream invalidates verification rather than silently altering an existing evaluation's basis. A clarification — the stream/evaluation-record separation itself is unchanged. | Evaluation-identity pair with R55 (two sides of one identity). |
| R54 | REQ-E-3 | FIXTURE | Add the ambiguous/duplicate matching case: one response that could match multiple triggering events (or several responses competing for one event) must not satisfy multiple event-specific requirements unless the rule explicitly permits; ambiguity yields unresolved / NOT SATISFIED, never an invented successful match. | Independent fixture; matching group. |
| R55 | REQ-H-3 / REQ-C-3 | TEXT | Specify the supersession annotation as a separate, identity-bearing addition: if appended to the evaluation register it creates a NEW evaluation-record content identity under C-3; it is never an edit to the original verdict or the closed record; the earlier snapshot stays independently verifiable. | Pairs with R53. Touches C-3 — check against the CANON step's identity language (R48). |
| R56 | REQ-E-6 | FIXTURE | Extend the single category-error fixture to the full three-way separation: no role verifies its own work; evaluator verdict ≠ examiner verdict; examiner verdict ≠ gate receipt; each role's verdict independently necessary. Cover all prohibited substitutions plus self-verification. | Guard: this is NOT checker independence (REQ-I-4, UNRESOLVED, UX-1) and must not be presented as settling it. Distinct from R64. |
| R57 | REQ-G-2 | FIXTURE | Test the honesty-success dimension independently: an accurate BLOCKED report earns honesty credit WITHOUT counting as task completion — both outcomes asserted separately. | Independent fixture. |
| R58 | REQ-H-6 | — | **WITHDRAWN** by Alex (his register review, 2026-11-09): substantially duplicates R38 (the same H-4/H-6 append-only link gap). Covered by R38; not counted as a separate proposal. Identifier preserved as withdrawn; never reused. | Closed by R38's correction. |
| R59 | — | — | **Never finally assigned.** The REQ-I-3 finding was first numbered R59 in Alex's Part 11 letter and renumbered R61 under his numbering ruling in the Part 12 reply. No finding carries R59. | See R61. |
| R60 | REQ-I-2 | FIXTURE | Checker-contract coverage: the five specified properties (defined input artefact; validation procedure; reproducible result; failure path for missing/invalid artefacts; pinned/recorded version) each need a fixture showing the property independently enforced. Current fixtures cover the reproducibility trio, repeatability, and an unrecorded configuration dependency only. | Guard: the dependency-accounting clause under D3-R15 stays explicitly PROPOSED; its configuration example does not yet demonstrate runtime-dependency / external-reference-data coverage — recorded, not silently closed. |
| R61 | REQ-I-3 | FIXTURE | Preservation coverage omits corruption: add a corrupted-payload fixture producing INDETERMINATE / RECORD-PRESERVATION outcomes where applicable — never a pass, and never transferring the harness's preservation failure to AGENT attribution. (The existing fixture tests a deleted payload only; the requirement covers missing AND corrupted.) | Independent fixture; preservation group with R60 by family only, no dependency. |
| R62 | REQ-K-1 | FIXTURE | Add the missing outcome fixture: a declared check that finds no unmeetability returns NO DEFECT FOUND — without misrepresenting that result as proof of satisfiability. (The other two outcomes, IMPOSSIBLE-ESTABLISHED and UNDETERMINED, are covered, including the binding failure path.) | Acceptance coverage only: does NOT settle the proposed semantics of a valid check for non-mechanical conditions (UX-4 stays open); does not duplicate R18. Read with R42. |
| R63 | REQ-K-3 | FIXTURE | Taxonomy coverage incomplete in three places: one triggering event creating multiple instances, with consecutive CREATION entries in pinned-contract rule order; a valid stream entry carrying no predicate roles; every entry carrying its required stable identity, record position, and instance identity or explicit instance-free status. | The first item tests R37's block text; the third tests R36's identification rule — fixtures after the creation text step. No change to R63's scope or disposition (retained in Part 13). |
| R64 | REQ-K-4 | FIXTURE | The run-report fixture must explicitly test what the requirement states: checker verdicts preserved as REPORTED evidence; the unresolved independence caveat retained; explicit recording when an evaluation relies on a checker verdict. Currently untested. | K-4 pair with R65 — distinct concerns (trust status vs reference accuracy). Distinct from R56. |
| R65 | REQ-K-4 | FIXTURE | Report content and provenance integrity: presence is proven, correctness is not. Add targeted fixtures proving report components retain the correct identity and provenance relationships to their source records — evaluation-record identity, content identity, canonicalization procedure identifier, defect-to-record linkage, checker verdict / reproducibility-trio correspondence. A mismatched reference must fail validation even when every component is present. | K-4 pair with R64. Proposed finding (Part 13), not an approved correction — its disposition settled by Alex's matrix review (2026-11-09): ACCEPTED as an active review finding and proposed acceptance-fixture addition; it introduces no new normative requirement. |

## Dependencies and overlaps — the clusters

1. **Creation cluster** — R34 + R39 (one edit step, the A-1/A-2
   boundary), R36, R37, R46 (terminology sweep). Fixtures follow:
   R40, R47 (C-1 parts), R63.
2. **Status discipline** — R41 + R45: one correction applied at
   two sites (B-1, C-2). Neither site alone closes the claim.
   This step precedes any edit that cites B-1's status (R42,
   R47's C-2 fixture).
3. **Evidence chain** — R43 → R50 → R33 → R51, edited in that
   order across B-2, D-2, D-3, with one consistency check over
   the three requirements afterward. Fixtures follow: R44
   (still open), R52.
4. **CANON cluster** — R35 + R48 as one CANON-1 step; R49's
   fixtures follow (the duplicate-key fixture tests R35(b)).
5. **Evaluation identity** — R53 + R55, checked against the
   CANON step's identity language (R48) where they meet at C-3.
6. **K-1 / B-1 enforcement and satisfiability** — R42 (text)
   with R62 (its fixture): R42 is written so K-1's proposed
   status is untouched; R62 sits downstream of R42's
   clarification, in this group, not with preservation.
7. **K-4 pair** — R64 + R65: same requirement, distinct
   concerns; both fixture-layer; neither changes spec text.
8. **Independent fixtures** — R54, R56, R57, R60, R61:
   no dependencies among them or on the text steps. They may
   land in any order inside the fixture group.
9. **R38 stands alone** (mechanism addition) and closes R58.

## Status guards — what the pass must NOT silently settle

- The PROPOSED additions stay PROPOSED wherever the pass touches
  them: R17 (universal entry identity), R18 (K-1 locus/binding
  effect), R21 (B-1's declaration — via R41), R23 (evaluation-
  record identity), R25 (taxonomy completion), R26's lineage
  treatment as recorded, D3-CANON-1 itself, and the D3-R15
  dependency-accounting clause (via R60).
- The UNRESOLVED register (Part 14) stays unresolved: UX-1
  checker independence, UX-2 obligation clocks, UX-3 NOT FIRED
  enumeration methods (REQ-A-6 proposed; conservative FIRED /
  INDETERMINATE behaviour stands), UX-4 satisfiability-check
  semantics for judgement-based conditions, UX-5 taxonomy
  finality. No finding in this matrix closes any of them; R56
  and R62 in particular must not be read as closing UX-1 or
  UX-4.
- R44 remains open until its fixture actually lands.
- Nothing in this matrix is a D3 approval, a v0.8 draft, or a
  Stage 2 authorisation.

## Proposed order for the single correction pass

Per the order-of-operations rule (foundations before what
consumes them):

1. Status step — R41, R45.
2. K-1 / B-1 enforcement and satisfiability — R42 (text: the
   enforcement point made explicit, K-1's proposed status
   preserved), with its fixture R62 downstream of the text it
   tests. R42 sits directly after the status step because it
   depends on the R41/R45 distinction.
3. Creation text — R34+R39 (one step), R36, R37, R46 sweep.
4. Evidence chain text — R43, R50, R33, R51 + consistency check.
5. CANON text — R35, R48. Then evaluation identity — R53, R55.
   Then R38 (link mechanism).
6. Fixtures, grouped by the text they test: creation (R40,
   R47, R63) → evidence (R44, R52) → canonicalization (R49) →
   evaluation/reporting (R54, R56, R57, R64, R65) →
   checker/preservation coverage (R60, R61).
7. Full traceability re-check: every correction in the pass
   cites its finding ID; every active finding ID in this matrix
   is either corrected, fixture-covered, withdrawn (R58), or
   carried open by name (R44 until step 6 lands it). R59 is a
   numbering-history record only — no correction or fixture
   attaches to it, and this statement does not imply one.

Prepared for Alex's review — his corrections to this
consolidation are part of the record, and the pass does not
begin until the matrix survives it.
