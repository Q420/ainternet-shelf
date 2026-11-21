# Outside review of COLLABORATION Rev 3 — received via Ben in the main chat, 2026-11-21 ~11:53 MST

**Provenance:** an outside reviewer's assessment of the design, brought into the chat by Ben (full text in the main-chat record, 2026-11-21 11:53 MST; the text does not sign itself). Filed as a faithful summary with its full point list. Transport class: outside review — evidence and judgement to weigh, not a ruling.

**Overall:** "a sound design with a genuinely good spine… a Rev 3 that deserves a ruling after a short, targeted pass." Nothing reads as flattery or rejection material. Do not reopen the settled distinctions.

**What holds (his list):** provenance ≠ truth (§2) as the load-bearing wall; the finding / ruling / disposition triple (§3) — "the best paragraph in the document"; the correction-authority split (§7) — keep verbatim; request ≠ assignment (§8) and the conservative defaults; §11's refusal to collapse checker and examiner, with the honest reopen clause.

**The one structural concern — the examiner is a single point of everything** (assembly gate, every joint gate, certification, disagreement settlement, live watching):
1. **Throughput** — every joint pauses on one live holder; the economics of live calls at every joint are unaddressed. Suggestion: gate granularity is itself an assembly-gate decision — the examiner approves how many gates the tree carries, making the cost his judgement.
2. **Independence hole at assembly** — the orchestrator authors the tree, joints, and verification lists; the examiner judges that framing. Fix: the examiner checks the tree **against the commission's acceptance criteria directly** and records that mapping himself.
3. **Who examines the examiner?** Challenges route back to the same examiner or to the director. Name it as a known limit: the examiner's judgement terminates at the director, deliberately — a cost accepted, not a gap unnoticed. One sentence in §3 or §12.

**Seams for the SPEC SHEET (or design acknowledgement):**
1. "No speaking scripts" (§12) vs pause mechanics (§4.5) — state explicitly: no script decides turn-taking *within* a joint; structure decides passage *between* joints.
2. **Pause scope undefined** — branch, downstream dependents, or whole run? A design-level question; cannot be left to construction.
3. **Liveness/failure states absent** — named recorded states needed (his examples: STALLED / HOLDER_UNAVAILABLE / AWAITING_RULING) shown by the observer, or "remains paused" and "silently dead" are indistinguishable, violating §12.
4. **Mid-run case re-versioning behaviour** — when v2 issues while an agent holds v1 mid-task: pause? re-acknowledge? do v1 contributions stand? Behaviour unspecified.
5. **Identity status has no consequence** — declare it informational, or name what it gates (may the assembly gate weigh it? can an unverified seat feed a certification?). Plus: provider-confirmed attests the *serving model*, not capability claims, which remain self-report.
6. **The office is undefined** — seated? mechanical? which parts are scripts, which are seats. ("No agent authors another's case" sits oddly beside an office that builds cases.)
7. Two small ones: (a) §4.5 "corrects it on the spot" reads as the examiner performing the fix — align to §7 ("requires correction"). (b) §2 "never works from a private copy" is literally false for LLMs — the enforceable claim is that no contribution is valid unless made through a recorded act against the current record; the spec must define **stale-view behaviour** (reject / rebase / flag).
8. §1 calls four roles a "ternary" — fix the wording; names and seats are precise things in this document.

**Bottom line (his ask before ruling):** the examiner-load/independence treatment at design level, and items 1–7 handed to the SPEC SHEET as named open construction questions, recorded as such — or verify the sheet already answers them, visibly, and rule.
