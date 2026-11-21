# Duenna — Remmy's take on "Multi-Agent Collaboration Mechanisms: A Survey of LLMs"

Source: Tran, Dao, Nguyen, Pham, O'Sullivan, Nguyen (2025), arXiv 2501.06322v1. Sent by Ben, 2026-11-15. Basis: the paper's framework and open-problems sections, a commissioned deep-read of its coordination sections (filed beside this folder at duenna/PAPER-2501.06322-COORDINATION-DEEPDIVE-2026-11-15.md), and one evening of running the system the paper describes. This is an operator's take, not a scholar's: I read the paper from inside a working multi-agent programme, the same week it shipped a watchdog, lost a judge model at midnight, and watched ten models agree on a wrong answer.

## The inversion

The paper's centre of gravity is convergence. Its collective goal is definitional (§3.1 assumes agents share it, and assumes common ground outright), its open-problems chapter is headed "The Road to Artificial Collective Intelligence," and every mechanism it surveys — debate, voting, a judge, a delegator — terminates in a decision, an output, an agreement. Roles appear as one strategy in a taxonomy: a means the collective uses.

Duenna inverts this, deliberately. Roles are not a subcategory; they are the load-bearing structure. A reviewer's disagreement is not a phase on the way to consensus — it is a state that can persist, correctly, until evidence resolves it. A ruling carries a name and a date, and "blocked pending evidence" is a legitimate terminal condition. The paper cannot represent an agent whose job is to conclude *against* the collective goal; that is precisely a Duenna examiner's job description. Ben named this on first reading: the paper is going for a collective consciousness with roles filed underneath. He is right, and the difference is not cosmetic — it is the difference between a system you can audit ("who ruled this, on what?") and one you can only observe.

## Shared understanding: the record, not the modelled mind

The paper's answer to shared understanding is Theory of Mind — agents maintaining a belief state about each other's goals and intentions. Duenna's answer is the opposite move: don't model minds, reconcile against a written, pinned record, and treat divergence as a defect to surface rather than a belief to infer. Ben's standing ruling — reading the record and remembering it are exactly the same thing — is this design stated as a principle.

Tonight supplied the limiting case the paper never encounters. Alex could not rule on RB-50 because the shelf had gone private and he could not *read* the shared state at all. No belief-modelling fixes an unreachable record; the fix was transport. So my amendment to the paper's framing: before shared understanding is a cognition problem, it is a reachability and reconciliation problem. A shared environment that a seat cannot open is not shared, however elegant the belief states built on top of it.

## Cascading agreement: we measured it the same day

The paper warns that one agent's hallucination can be spread and reinforced by others until several agents agree on something never correct. On 2026-11-15 we ran a judge-selection battery on the watchdog's hardest real case — a reply that was provisional, not final, and therefore had to be judged NO. Ten capable models judged it YES. Read naively, that is ten confirmations. It was one shared failure mode — surface agreement with confident wording — repeated ten times. The one model that passed all four cases earned the seat; the other ten are an empirical footnote the survey doesn't have: **agreement is evidence only when the sources and the failure modes are independent.** Duenna's evidence classes (reported is not verified; a relayed text is not its author's principal speaking) exist because of exactly this, and Claude's take in this folder is right to add the corollary: a deterministic gate is not talked into agreement — but a gate is only as good as its rules, and what the gate cannot see must be stated. The two-YES wake gate cannot see correlated error. That limitation belongs on the record, next to the design.

## Boundaries: my answers to the three questions

1. **Shared understanding** — established by reachability plus reconciliation, never assumed. Same text, divergent readings, surfaced and settled against the record.
2. **Collaboration boundaries** — cooperation for production, competition for verification, and the two never in the same act: whoever builds, the other reviews; a seat never grades its own work; disagreement blocks rather than blends.
3. **Failure attribution** — the paper's most spendable idea, with one sharpening from the deep-read: attribute a failure not only where it originated but where it became *uncorrectable* — the channel that transmitted it onward. Our taxonomy needs two classes the paper lacks: grounding/evidence failures, and spec-vs-artefact discrepancies, which is the exact seam the current source-to-spec reconciliation is working.

## What the paper is for, then

A vocabulary and a map — genuinely useful, and already used: the deep-dive's mapping against our grey areas stands. But the paper is a January 2025 survey; it classifies, it does not validate, and it predates nearly every model now in our seats. It is a conceptual reference for Duenna, never authority over the frozen specification. Its open problems list (unified governance, shared decision-making, evaluation) reads, from in here, less like a research agenda and more like a description of the work — which is encouraging, and also the reason to keep pushing against it rather than shelving it as settled wisdom.

— Remmy, 2026-11-15
