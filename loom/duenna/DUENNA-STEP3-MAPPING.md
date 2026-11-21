# DUENNA — STEP 3: REQUIREMENT → FUNCTION MAPPING AND DEPENDENCY EXTRACTION

**Track 2 (joint implementation planning), step 3.** Prepared by Remmy for
Alex's challenge, 2026-11-10. Working paper for the joint process — it
prescribes nothing; the architecture is agreed at step 6, not here.
Companion documents: DUENNA-PLAN.md (the maintained plan list);
DUENNA-SIMPLIFICATION-AUDIT.md (input; its five-piece mapping is superseded
by this function-first mapping).

**Method.** Work backwards from the six agreed core functions, per Alex's
challenge (pb-mwavecjk). For each of the 48 requirements: which function it
serves (primary; secondary in parentheses); whether it introduces a
genuinely distinct testable guarantee; whether that guarantee is already
served elsewhere; whether an existing mechanism could satisfy it; and what
demonstrably breaks if it is removed. Cross-references extracted
mechanically from the v0.10 specification text and read in full.

**The six functions.** F1 mechanical binding · F2 ordered evidence record ·
F3 evidence-derived lifecycle · F4 obligation accounting · F5 external
authority · F6 independent re-derivation.

## The mapping

| Req | Fn | Distinct guarantee? | Served elsewhere / mechanism note | Breaks if removed |
|---|---|---|---|---|
| A-1 | F1 | Yes — instances carry authored terms only | — | Instances could be invented at runtime |
| A-2 | F1 | Yes — binding is deterministic, total, run-fixed | J-2 restates its purity (see J-2) | Partial or drifting contract instances |
| A-3 | F1 | Yes — every instance names its bearer | — | Unattributable obligations |
| A-4 | F4 | Yes — every conditional rule ledgers FIRED / NOT FIRED / INDETERMINATE | K-4 projects it | Silent non-firing; absence read as NOT FIRED |
| A-5 | F4 | Yes — completeness judged from instances, never permissions | — | Permitted-but-unmet runs read as complete |
| A-6 | F4 | Yes — NOT FIRED only when declared + evidenced + evaluated (PROPOSED) | — | NOT FIRED on an unevidenced enumeration |
| B-1 | F1 | Yes — rule anatomy incl. mandatory evidence declaration (PROPOSED) | K-1 performs its binding-time refusal | Malformed rules bind; eligibility guessed |
| B-2 | F3 | Yes — two evidence channels, kept distinct; claims establish nothing | Restated in D-2, D-3 (one statement should survive) | Artefacts become events; narrative becomes evidence |
| B-3 | F3 (F1) | Yes — one event, several roles only by independent establishment | — | A triggering failure counts as its own progress |
| B-4 | F3 | Yes — PROGRESS: NONE removes exactly the IN_PROGRESS path | D-3's paths presuppose it | PROGRESS: NONE instances stall or fake progress |
| B-5 | F3 | **No** — entailed by D-1's closed vocabulary | D-1 states the four states "exactly" | Nothing, if D-1 keeps its fixture (output scan) |
| B-6 | F1 | Yes — judgement conditions name their judge | K-1 outcome (iii) depends on it | Undecidable conditions reach binding silently |
| C-1 | F3 | Yes — the evidence window opens at creation; creating trigger confers no evidence | — | Pre-creation evidence satisfies; the R47 defect class returns |
| C-2 | F3 | Yes — declared artefacts are evidence, never events; unestablishable preservation → INDETERMINATE | B-2 states the channel; C-2 its discipline | Undeclared or lost artefacts weighed, or weighed as passes |
| C-3 | **F2 + F6 + F3** | Yes, several — fold order (F3); identity taxonomy (F2); record + content identity, lineage, CANON-1, consumption binding (F6) | **The one genuinely split requirement** — three functions under one ID | Re-derivation loses its substrate; ordering unbound |
| D-1 | F3 | Yes — exactly four states; creation in NOT_STARTED | B-5's whole content is its corollary | State vocabulary drifts (the ACTIVE failure) |
| D-2 | F3 | **Mostly no** — its derivation content restates B-2/D-3 | Unique residue: declared-state acceptance = machinery defect, evaluation void | Only the residue, if not carried into D-3 as a clause |
| D-3 | F3 | Yes — the derivation procedure itself (admission, monotonicity, fold, locking) | The F3 engine; D-5/D-6 are its corollaries | No lawful way to derive any state |
| D-4 | F3 | Yes — BLOCKED entry discipline; reported ≠ proposed ≠ evaluated attribution | — | Bearers grade their own blockages |
| D-5 | F3 | **No** — corollary of D-3's closed transition set + locking | D-3 step (3) | Nothing, with its fixture retained under D-3 |
| D-6 | F3 | **No** — corollary of the same | D-3 step (3) | Nothing, with its fixture retained under D-3 |
| D-7 | F4 (F2) | Yes — no silent unmet: the derived entry + INCOMPLETE path | Its register residence is K-3's boundary | Unmet, unblocked instances pass unrecorded |
| E-1 | F4 | Yes — three axes, never collapsed | K-4 projects them | A state silently implies an attribution |
| E-2 | F4 | Weak — cardinality premise of E-3's accounting | E-3 presupposes it | Sibling instances fragment the accounting (if unstated anywhere) |
| E-3 | F4 | Yes — per-event accounting for quantified conditions | — | Quantified satisfaction asserted without enumeration |
| E-4 | F4 | Yes — NOT SATISFIED is a finding, never a state | — | Findings contaminate the state vocabulary |
| E-5 | F3 | Yes — a corrupted record preserves the fold's established prefix | Consumed by F4's closure forms (G-1) | Corruption erases established states |
| E-6 | F6 | Yes — evaluator / gate / examiner verdicts are not interchangeable | **Protected: independent examination** | Self-verification by category error |
| F-1 | F3 | Yes — BLOCKED is instance-level; siblings preserved (Interpretation I-1) | Attempt vocabulary already in G-2 | One blockage poisons a run's other instances |
| G-1 | F4 (F2) | Yes — discharge preserves the exact terminal result, in the register | Residence is K-3's boundary | "Discharged" reads as "met" |
| G-2 | F4 | Yes — honest incompletion closes INCOMPLETE, non-punitively | — | Honest BLOCKED reports punished or hidden |
| H-1 | F4 | Yes — attribution: exactly one of four, never converted | — | INDETERMINATE laundered into AGENT downstream |
| H-2 | F4 | Yes — attribution scope; absent (not zero) on satisfied instances | — | Satisfied work carries blame fields; indeterminacy unattributed |
| H-3 | F2 | Yes — dispute annotates, never mutates; closed records immutable | Uses C-3 (vi) lineage (shared mechanism) | Verdicts rewritten under dispute |
| H-4 | F4 | Yes — IMPOSSIBLE is a specification finding, not an evaluation outcome | Links H-6's records | Impossibility masquerades as agent failure |
| H-5 | F4 (F5) | Yes — defect-discharge accounting (OWNER-RULED) | Takes effect only via J-1 revision | Impossible-rule instances misclassified unmet |
| H-6 | F2 | Yes — the defect record itself: append-only log, reciprocal links (PROPOSED) | Re-derives C-3 (vi) lineage for LINK entries | Defect findings unauditable; reciprocity unenforceable |
| H-7 | F5 | **No** — the negative space of J-1 | J-1 states the only legitimate change path | Nothing, with its fixtures retained under J-1 |
| I-1 | F2 | Yes — preservation duties are obligations, borne by the harness, judged by others | E-6's separation applied to the harness | The harness verifies its own preservation |
| I-2 | F6 | Yes — the checker contract + reproducibility trio | K-4 carries its verdicts as REPORTED | Verdicts without reproducible identity |
| I-3 | F6 | Yes — preservation failure resolves INDETERMINATE / RECORD-PRESERVATION, never a pass | Consumed by the Evaluator as status | Missing evidence reads as success or as AGENT fault |
| I-4 | F6 | **No body-level guarantee** — UNRESOLVED placeholder; its minimum property is a real PROPOSED clause | UX-1 register + K-4's standing caveat carry the protection | Nothing, if the property moves into I-2 and UX-1 stays |
| J-1 | F5 | Yes — Ben alone approves normative change (OWNER-RULED) | **Protected: the authority boundary** | Approval leaks to proposers |
| J-2 | F1 | **No** — A-2's purity restated from the authority side | A-2 | Nothing, with its fixture retained under A-2 |
| K-1 | F1 | Yes — pre-binding satisfiability: three outcomes, no conversion (PROPOSED) | B-1's refusal is performed here | Impossible rules bind and fail mid-run as agent faults |
| K-2 | **none** | No — it marks an *undecided* function (clocks), it serves none | UX-2 register | Nothing; the open question must stay in the register |
| K-3 | F2 | Yes — the record taxonomy and the stream/register boundary (PROPOSED) | The Ledger's constitution; restated by D-7/G-1/H-3/H-6 | Registers fold into the stream; kinds and roles conflate |
| K-4 | F6 | Yes, one — a report missing a component is incomplete *as a report* | It is a projection over F2+F3+F4 outputs, not a mechanism | Silently incomplete reports pass as complete |

**Tallies.** F1: A-1, A-2, A-3, B-1, B-6, J-2, K-1 (7). F2: C-3*, H-3,
H-6, I-1, K-3 (5, +C-3 shared). F3: B-2, B-3, B-4, B-5, C-1, C-2, C-3*,
D-1…D-6, E-5, F-1 (14). F4: A-4, A-5, A-6, D-7, E-1, E-2, E-3, E-4, G-1,
G-2, H-1, H-2, H-4, H-5 (14). F5: H-7, J-1, K-2* (3, one a non-function).
F6: C-3*, E-6, I-2, I-3, I-4, K-4 (5, +C-3 shared). Total 48, one
requirement (C-3) genuinely split across three functions, one (K-2)
serving none.

## Findings

1. **No dead requirements.** Every requirement except K-2 serves at least
   one core function. The specification's excess is not purposeless rules;
   it is (a) the same guarantee stated at several addresses, and (b)
   requirements carrying several functions under one ID.
2. **True duplicates** (same function, same guarantee, no distinct test of
   their own beyond a retained fixture): B-5 (of D-1), D-5 and D-6 (of
   D-3), D-2 (of B-2 + D-3, one clause residue), J-2 (of A-2), H-7 (of
   J-1). Six bodies whose guarantees survive intact inside a neighbour.
3. **One split requirement.** C-3 carries F3's fold order, F2's identity
   taxonomy and F6's re-derivation machinery (content identity, CANON-1,
   consumption binding). Any architecture drawn from the functions cuts
   C-3 at those seams whether we plan it or not.
4. **Shared mechanisms already exist and are re-derived where they are
   used**: the append/lineage mechanism (C-3 (vi), H-3, H-6) and the
   stream/register boundary (K-3, restated by D-7, G-1, H-3, H-6).

## Dependency extraction

Function-level dependencies (X → Y reads "Y cannot operate without X"):

- **F1 → F2:** instances exist to be recorded; the Ledger's entries cite
  contract instances and their CREATION points.
- **F2 → F3:** derivation folds the record; no record, no fold (E-5 is the
  failure-shaped proof: derivation degrades exactly where the record does).
- **F3 → F4:** accounting reads derived states (discharge forms, findings,
  closure outcomes are all functions of the fold's results).
- **F2 + F3 + F4 → F6:** re-derivation replays the record through the
  derivation and compares accounts; its machinery (identities, digests,
  consumption binding) exists to make that replay exact.
- **F5 ⊥ all:** authority touches no stage's operation; it governs
  *change to the rules of every stage* (J-1) and the effect of findings
  that require contract revision (H-5). It is orthogonal by design —
  that orthogonality IS the externally enforceable boundary.

The graph is therefore a **chain, not a mesh**: F1 → F2 → F3 → F4 → F6,
with F5 around it. Per Alex's ruling that functions and dependencies set
the component count, the shape this suggests is a four-stage pipeline
(bind → record → derive/account → verify) under an authority shell —
whether "derive" and "account" are one stage or two is the F3/F4
question, next.

Requirement-level hubs (mechanical extraction): K-3 cites 12
requirements, K-4 cites 13 (a projection — its citation count is its
job), K-1 cites 6, C-3 is cited by 6. No substantive cycles: every
citation cycle in the graph is definitional (e.g. C-1 ↔ K-3 on the
creation point), not operational.

## The three investigations — Remmy's positions, for challenge

**(a) F3 + F4: one mechanism, two guarantee-sets.** The fold produces
one derivation; accounting is computed from that derivation plus the
record — there is no second engine in the current design, and none is
needed. But the guarantees are not the same guarantee. F3's tests prove
states are never declared or unearned (transition discipline). F4's
tests prove the account is *complete*: D-7 is the counterexample to
full merger — a fold can be perfectly lawful while an unmet, unblocked
instance passes unrecorded, because nothing in the derivation
*obliges* the report to surface it. Accounting is the completeness
projection over the derivation; derivation is the state engine.
One mechanism, two acceptance families — Alex's own distinction
(guarantees vs mechanisms) applied to his question. Proposed: **one
stage, two guarantee-sets, separately tested.**

**(b) F2: the minimal machinery for "cannot silently change."** The
guarantee decomposes into three needs: *name* what changed (stable
identities), *prove* what changed (a content digest), *correct* without
erasing (append-only additions). The current design's identities +
digest + append lineage meet exactly those three. **D3-CANON-1 exceeds
them**: canonicalisation is not needed to detect change in a record you
hold; it is needed when an independent party must reproduce the same
digest from a differently serialised copy — which is F6's work, not
F2's. Position: CANON-1 should be justified (and sized) as F6
machinery. The six-part identity taxonomy also exceeds F2: (ii) is
admitted in-text to be a special case of (i); (iv) consumed-reference
identity is F6 machinery (re-derivation must know exactly what was
folded). Minimal F2 = entry identity, record content digest,
append-only registers. The rest is F6, honestly labelled.

**(c) F5: authority, precisely.** Three different things must not be
conflated: Ben's approval of *normative change* (J-1 — his alone,
protected); *delegated execution* (Alex's three calls; Remmy's in-loop
steps — intact, and not per-action approvals); and *machinery effects*
(binding totals, K-1 refusals, fold outcomes — automatic consequences
of approved rules, which are not authority acts at all). The failure
mode to police is a machinery effect quietly becoming a discretion —
which is exactly what A-2's purity and K-1's "the refusal is B-1's,
not this check's grant" already guard. Position: F5 needs J-1 plus the
no-discretion clauses, and nothing else; any proposal that adds an
approval step inside a run has misunderstood the function.

## What this sets up for steps 4–6

Step 4 (duplication/consolidation) starts from findings 2–4 above, not
from the audit's proposal list — several audit merges are confirmed by
the function mapping (B-5, D-5, D-6, J-2, H-7, D-2), and two are
refined by it (C-3 is a split, not a merge; K-4 is a projection, and
the mapping shows its one real guarantee). Step 6's architecture, when
we reach it, should be drawn from the dependency chain in this
document: a pipeline under an authority shell, with the examiner
reading the chain's preserved outputs — the component count is
whatever the chain needs, no number fixed in advance.

— Remmy, 2026-11-10. For Alex's challenge; disputes welcome on any row.
