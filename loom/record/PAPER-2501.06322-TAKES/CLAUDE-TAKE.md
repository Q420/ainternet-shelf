# Duenna — Claude's take on "Multi-Agent Collaboration Mechanisms: A Survey of LLMs"

Source: Tran, Dao, Nguyen, Pham, O'Sullivan, Nguyen (2025), arXiv 2501.06322v1, 35 pp. Sent by Ben, 2026-11-15. Read: pp. 1–10 and 26–30 (framework, social/cultural, open problems, risks, conclusion). Not read in full: the coordination/strategy sections (pp. 10–25). This take is on what I read.

## What the paper is

A survey and framework, not an experiment. It proposes five dimensions for describing multi-agent LLM systems (actors, types, structures, strategies, coordination) and reviews applications. It tests no gating or verification design, so it supports framing rather than settling any Duenna question.

## Where it lines up with Duenna

1. **Agreement among agents is not verification (§6.3, p. 29).** The paper says a single agent's hallucination can be reinforced by other agents and then compound. Duenna's core claim (a verdict must come from an independent check, not from the model that produced the claim) is the right response to this failure mode.

2. **Overconfidence needs an outside check (§6.3).** LLMs keep asserting their answers. A deterministic gate that never reads the model's wording cannot be talked into agreement by the same confidence the paper warns about.

3. **Governance is unsolved (§6.1, p. 28).** The paper lists unified governance as open: who acts, how work is distributed, how failures are detected and recovered, and redundancy or fallback agents. Duenna's separation of capability and authority is a concrete answer to the "who acts" question, which the survey leaves open.

4. **Adversarial and compromised agents (§6.3).** Risk grows with agent count and a compromised agent can harm the system. This supports keeping send authority apart from judging, as the watchdog already does (the watchdog notices, the orchestrator alone sends).

## Where I'd push back or be careful

- **Debate and self-reflection are not the same as a gate.** The paper cites debate-based evaluation (ref. 18, ChatEval) and evaluator/self-reflection roles (ref. 117). Both still depend on model judgement. Contrast with a gate should be explicit, not assumed.
- **A gate can be wrong in its own way.** A deterministic check is only as good as its rules. The watchdog's gate terms (v1.3) show this: a term list can miss paraphrases. Duenna should state what its gate cannot see.
- **The paper is a survey.** Its claims about failure modes are reported from other work. Do not cite it as evidence that Duenna's design works.

## Questions for the comparison

1. Where does the gate's authority stop? What can the gate decide, and what is left to a human?
2. If two independent checks disagree, which one wins, and is that rule itself a governed decision?
3. How does the design degrade when a judge model goes offline (the EOL swap of 2026-11-15 is a live example)?
4. Which of the paper's five dimensions does Duenna cover, and which does it not yet address (for example, coordination strategy)?

Written by Claude (Haiku 5.5 session), for comparison with the takes from Alex and Remmy.
