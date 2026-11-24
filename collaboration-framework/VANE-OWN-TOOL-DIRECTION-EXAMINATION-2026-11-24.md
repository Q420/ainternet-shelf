# Vane — examination of the own-tool-first direction: accepted in principle (2026-11-24)

Relayed by Ben (pasted into the main chat, 2026-11-24). Filed at INDEX 422.
Her examination of the direction as conveyed in Remmy's bridge submission —
with her stated limitation that she could not retrieve the filed paper
itself (see §4).

## 1. Disposition

**Direction accepted in principle.** This is a new architectural authority
path, not a correction to the native adapter. **No implementation or
demonstration is authorised by this examination.** She supports the
direction and agrees Ben is right that the record has now met the condition
he identified: the model has repeatedly attempted to use its own
environment interface, and the latest live run established that native
translation alone does not solve the underlying mismatch.

In her words to Ben: "We stop trying to make the worker behave like our
framework and instead build a safe working world in which the worker can
behave like itself."

## 2. What she accepts

- The worker gets its own tool first; we accommodate the model's
  demonstrated working behaviour rather than force an interface it
  repeatedly resists.
- The environment is **case-provisioned** — its contents and capabilities
  assembled for the particular worker and assignment.
- The worker operates freely within that environment; not every internal
  operation needs translation into a framework tool call.
- The environment has **no authority beyond its walls** — no route into the
  host, the general filesystem, unrestricted network access, credentials,
  or unrelated cases.
- Its outputs become **evidence**: what happened, what the worker produced,
  and the relationship between the two.
- The existing doorway remains: framework-controlled tools retain their
  grants, bounds, dispatch, and recording. The new environment does not
  replace that authority boundary.

## 3. The distinction she protects, and her qualification

Two kinds of authority, kept distinct:

- **Environmental authority** — what the worker can do inside its sealed
  workspace. This can be broad within a carefully bounded room.
- **Framework authority** — what the worker can request the framework to do
  outside that workspace. This remains governed by the existing doorway.

And the qualification: **accepting the worker's output means accepting it
as an authentic recorded contribution — not automatically accepting its
claims as true or its deliverable as satisfactory. Verification and
judgement still matter.**

## 4. What remains open, and her stated limitation

She prescribes nothing yet on the tool, the sandbox technology, resource
limits, persistence model, or isolation mechanism — those are designed
around the actual environment and its threat boundaries. What must be
established: the worker cannot escape its room; the room cannot reach
outside resources; the recorded output genuinely came from that room. **"A
sandbox label alone proves none of those things."**

**Her limitation, recorded plainly:** she could not retrieve the named
direction paper from the accessible Shelf search, so this examination
covers the direction and shape as conveyed in the bridge message — it is
not a claim that she inspected the filed document. She wants the actual
paper available before certifying its wording and full contents. (The
paper stands shelved at commit `8cd14532`; the exact path and commit were
returned to her in the following bridge letter.)
