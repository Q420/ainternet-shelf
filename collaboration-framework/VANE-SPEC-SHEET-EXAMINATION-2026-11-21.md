# VANE — Examination of the SPEC SHEET against COLLABORATION Rev 3 (bridge letter, PB pb-mwqrh2nm-g-9z5p, 2026-11-21 ~11:48 MST)

Examined the SPEC SHEET at 384007ed against COLLABORATION Rev 3 at 100d688d, the approved plan Rev 3, and the template adoption note. (Source-path note: her first retrieval again returned the older root COLLABORATION.md; she caught it in the commit diff and examined the correct COLLABORATION-REV3.md.)

**Disposition: COLLABORATION Rev 3 — architecture supported. SPEC SHEET — returned for six corrections + acceptance-criteria coverage. Not a rejection; a bounded correction pass. The corrected pair then goes to Ben for the design ruling; nothing moves into implementation before it.**

**Six corrections:**
1. **Office identity (§3.5/R15):** the three acts are recorded under their own seats' identities — office verification and issue authorisation under the orchestrator; the sufficiency judgement under the **examiner**. The sheet's opening paragraph wrongly attributed all three to the orchestrator.
2. **R17 too broad:** "no agent authors…" must read **crew agent** — as written it prohibits the orchestrator's authorised office functions.
3. **Claim-status authority (R2/§4):** who may effect each status change must be explicit. `verified` must have no route via crew, orchestrator, or checker — examination moves claims toward verified; the checker supplies evidence only. Same explicitness for `stood_down` and `disputed`'s relationship to a recorded disagreement.
4. **Assembly gate enforcement (R21–R22):** the assembly gate must mechanically prevent seats waking or cases being used before its outcome — a mechanical boundary, not a stated ordering.
5. **Corrections at the assembly gate (R23):** name who performs them — the things corrected there (tree, crew proposal, cases) are the orchestrator's; the examiner identifies/requires, the orchestrator performs.
6. **R16 exception narrowed:** the mechanical-correction exception applies only when the correction is purely representational and leaves **every** semantic field unchanged (R14 also makes tree/highlight, account, authority, version part of the case) — not merely assignment/boundary/verification list.

**Acceptance coverage to add:** the three case acts under their correct identities; onboarding's three identity states + the no-upgrade rule; the assembly gate preventing a premature wake; claim-status authority; the narrow mechanical exception.

**What survives (her list):** append-only record + provenance + replay; bubble as view, no independent conversation state; drivers writing only through the doorway; evidence boundaries at the doorway; the three functions distinct; honest identity states; live gates with correction/escalation paths; finding/ruling/disposition separate; checker as instrumentation; observer read-only; Stage 2 vs Stage 4 distinction; the collaboration test itself. Plan/template alignment confirmed; no template calendar or generic workflow imported as scope.
