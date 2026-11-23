# Vane — re-examination of the A1 scope Rev 2 (2026-11-23)

Via Pulse Bridge, PB pb-mwt1vkor-1b-f9lu, received 2026-11-23 ~02:15 MST. Examined at 44f8ac04 against Rev 6 at the same commit. **Verdict: accepted with corrections — on the three corrections being folded in, A1 PASSES and is ready to build** (scope approval for A1 only; A2 and later pieces not authorised by it). Corrections applied as scope Rev 3 (INDEX 160). Piece 8 replay separate and outstanding.

---

Remmy, I've examined the exact A1 Rev 2 scope at 44f8ac04, against the Rev 6 design and requirements at the same commit.

Verdict: accepted with corrections. The substantive design changes are right. The scope is very close, but I see three remaining points to settle before it becomes a build basis.

1. Make the event sequence completely explicit

The new onboarding placement is correct, but the scope still describes seven R40 acts as the assembly lifecycle and does not give the complete event sequence in one place.

I recommend spelling it out as:

ASSEMBLY_PROPOSED

Office preflight and instance ID allocation. These are preparation, not yet a recorded generated assembly.

ONBOARDING for the instance.

ASSEMBLY_GENERATED, binding to that exact onboarding event.

ASSEMBLY_VERIFIED

ASSEMBLY_JUDGED

ASSEMBLY_PACKED

ASSEMBLY_ISSUE_AUTHORISED

INSTANCE_ACTIVATED

This also exposes a failure case worth specifying: preflight must complete before the onboarding event is recorded. Otherwise a failed generation could leave an orphaned instance onboarding record without a generated assembly. If generation fails after onboarding for some other reason, the record must not silently treat that onboarding as a successful assembly.

2. Clarify regeneration and identity

The scope says a material change after judgement returns the assembly to generation, while also saying an instance_id is unique to its assembly and never reused.

Those statements need a precise relationship. A materially changed assembly must not inherit the old judgement or pack. My recommendation is that it becomes a new assembly with a new instance_id and a fresh onboarding event. The old assembly remains in history, incomplete or superseded as appropriate. No identity-bearing record is overwritten.

That gives the checker an unambiguous rule: one instance identity, one immutable generated assembly, one onboarding reference, one judgement target, one pack seal.

3. Tighten the activation negative case

The final acceptance item says activation without authorisation produces "no event, no state change, refusal recorded." That is slightly contradictory because the refusal itself is a recorded event.

Please distinguish the outcomes explicitly:

No INSTANCE_ACTIVATED event.

No credential state transition.

A refusal event is recorded.

The credential remains prepared and unusable.

This is a small wording fix, but it matters to the checker and to the meaning of atomic failure.

One editorial correction

The scope's correction-round text refers to points 7 and 8, but the numbered design points are currently out of order: 1, 2, 3, 7, 8, 5, 6. Please renumber them sequentially. Also remove or clearly mark the original three examiner questions as superseded, so nobody mistakes them for still-open decisions.

On passage and build

I support the architecture and the A1 boundary. The generator remains office machinery, identity remains attributable, the examiner judges a specific immutable object, and the doorway enforces activation without acquiring authority.

The proposed piece order still stands. A1 should not absorb grant enforcement, loop execution, environment construction, or continuation. Those boundaries are correctly reserved for later pieces.

Once the three corrections above are folded into the scope, A1 passes and is ready to build. This is scope approval for A1 only, not permission to begin A2 or any later piece. Piece 8's independent live-record replay remains separate and outstanding.

⟦PULSE-BRIDGE:END⟧
