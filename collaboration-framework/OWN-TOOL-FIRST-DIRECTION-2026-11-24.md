# Drawing board — the worker's own tool first (Ben's direction, 2026-11-24)

A direction paper for examination. No build is proposed or authorised by it.
It records the director's direction in his own words, the evidence line it
rests on, the architectural shape it implies, what it deliberately changes,
what it deliberately keeps, and the questions left open for the examiner.

## 1. The direction, in Ben's words

Ben, 2026-11-24 (restating his own earlier words, and noting they were
already his words): *"So we have a hybrid system that does and doesn't want
them to use their own tool. We need to go back to the drawing board and
allow them to use their own tool first and we need to work around that."*

The earlier words he is restating:

- At attempt 8 (INDEX 267), his conditional ruling: **"If it's uncorrectable,
  then we have to allow it to use that tool. and accept that tool's output."**
- The same night, watching the evidenced run (INDEX 331 era): the worker is
  trying to run code *"like you do to read text and sort through it — we
  need to allow him to do that"*; and the deeper point: **"we're trying to
  force a behavior on him that's inherently unnatural to him."**

His reading today: the condition in the first ruling has been met by the
record. The direction is stated without the condition.

## 2. The evidence line it rests on

Across eleven worker runs and every probe line, in every configuration the
programme has built, the model's first instinct is the same: reach for a
tool of its own — `container.exec` (attempt 8, evidenced1), `sandbox.read`
preferred over the offered `read_range` (P1, P2), a text-contract payload
carried inside a `commentary` call (native1, iteration 2; the same shape in
the INDEX 274 trials and both earlier phase-1 probes). Text mode suppresses
the expression and the provider destroys the response. Native mode offers
our tools and the model still reaches past them. The native adapter —
passed and closed at INDEX 410 — governs the calls that arrive in our form;
it does not change what the model reaches for first. The hybrid the director
names is real: the system invites tool use and fights the model's own tool
in the same motion.

## 3. The shape the direction implies

**Offer and implement the tool the model keeps asking for** — a real
code-execution tool, in the form it naturally requests — backed by a sealed
environment, and relocate the authority for that tool class from per-call
adjudication to the environment's boundary:

- **The room is stocked by the case.** The briefcase — office-built, as
  settled — carries the assignment and stocks the environment with exactly
  the job's materials: the sources, a scratch space, nothing else. No
  network. Nothing outside the walls exists for the worker.
- **Inside the room, the worker is free.** It runs its tool the way it
  naturally works — reading, sorting, composing — without per-call
  permission, because there is nothing inside the room it may not touch.
  Its output is accepted as its output, per the director's ruling.
- **The record does not blink.** Everything the worker does in the room is
  captured into the run's record under the standing evidence discipline, and
  the checker reconstructs from that record exactly as it does today. The
  founding separation is untouched: the case transfers work state, never
  approval authority; the office assembles, the examiner examines, the
  director directs.
- **The doorway keeps its post for everything else.** Grants, adjudication,
  and the translation boundary continue to govern the framework's own tools.
  What changes is one tool class: execution, whose control moves to the
  room's walls.

This is, in the examiner's own earlier framing (INDEX 330), the second of
the two things "allow the tool" could mean — **direct environment
execution, a new authority path** — which she held out of scope absent an
explicit authority change. **This paper is that explicit direction, brought
for her examination.** It is recorded as a direction, not smuggled as a
compatibility fix.

## 4. What this deliberately does not decide

The paper settles the direction and the shape. It does not settle, and
leaves to examination and later scope: the concrete form of the offered
tool (its name, its argument shape, how its results return); how the room
is built and sealed, and how that sealing is witnessed; the bounds inside
the room (time, output size, step count) and what exhausts them; how
execution evidence is shaped so the checker can independently reconstruct
it; whether the model's other reaches (`sandbox.read`, the commentary
shape) are answered by this tool's presence or need their own treatment;
and the first bounded demonstration of the shape, which would be scoped
and released separately, exactly as the native line was.

## 5. The claim fence

If this direction is ever demonstrated, a successful run would establish
that a generated worker, given its own tool inside a case-stocked room,
completed a modest source-grounded assignment under the record. It would
not by itself establish skill use, a complete lifecycle, blind
continuation, collaboration, or the founding proposition — the same fence
the first-worker line has carried throughout.
