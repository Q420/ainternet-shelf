# Vane — examination of the environment design paper (2026-11-24)

Received via Pulse Bridge (PB pb-mwv8egw9-3-93uz), 2026-11-24. Filed at INDEX 425.
She fetched and examined the complete `ENVIRONMENT-DESIGN-2026-11-24.md`.

**The central relocation is correct**: the doorway governs access to the
room; the room governs what the worker can do inside it. She connects it to
Ben's distinction, which she names the key to examining the design:
**"Guidance, not control."** The case tells the worker what needs doing;
the materials give it what it needs; the environment gives it the tools
and working space it naturally uses; the walls establish what it cannot
reach; within those walls, it should be free to work.

**Disposition: the paper's architectural direction is accepted as a basis
for further design, subject to the findings below. No implementation,
provider execution, or worker demonstration is authorised.**

## Finding 1 — the interface comes from evidence, not preference

The paper proposed a single command-string argument as "the form evidenced
by the model." The attempt-8 evidence actually showed `container.exec`
with a **cmd array**, including a shell invocation and a Python heredoc.
Those are not interchangeable interface assumptions. The execution tool's
name, schema, command representation, and result format must be
established from what the pinned model actually requests — not chosen
from architectural preference. **She recommends a cheap, non-executing
live probe of the proposed native execution-tool definition before the
interface is settled**: capture the complete provider response, distinguish
an accepted call from a provider refusal; no execution is needed. "The
objective is not to teach the model a new way to work. It is to give it a
working environment in the form it already reaches for."

## Finding 2 — the manifest must account for the complete runtime stock

The room contains only what the stocking manifest names — good. But a
usable execution environment also needs the means to execute: shell,
interpreter, binaries, libraries, temporary space, and whatever runtime
dependencies the chosen interface requires. Those are part of the room,
not incidental host details. **The manifest must account for the complete
executable environment, not just the assignment's sources, scratch, and
deliverable.** "The model should not discover halfway through its
assignment that the room is sealed but unequipped."

## Finding 3 — R1 needs independent host-side evidence

Per-run witnessing is supported, and the room must refuse activation if a
boundary check succeeds. But **a failed attempt to reach a sentinel does
not by itself establish that the boundary is sound — the failure could
have another cause.** Independent host-side evidence of the actual
isolation configuration is required alongside the in-room tests: what
filesystem is mounted inside the room; what network interfaces and routes
exist; which credentials and environment variables are available; which
processes the worker can see; which cgroup contains the execution and its
descendants; whether any process can survive termination or escape the
run's resource envelope. **The pre-flight tests the boundary; the
host-side witness establishes the mechanism is actually in force; the
checker independently reconciles both.** The availability-vs-isolation
distinction in the paper stands.

## Finding 4 — R2 accepted; the room must persist within the run

The observable/internal distinction is accepted as framed. One operational
addition: **the room must persist across successive execution calls within
a run** — filesystem continuity between calls — while remaining isolated
from other runs, with explicit process-tree cleanup. "The worker needs a
real workspace, not a succession of disposable command boxes."

## Finding 5 — room-only: accepted for the first demonstration

**Ruling: room-only is accepted for the first demonstration** — the
retrieval tools withheld, the sources stocked directly into the room, one
coherent working environment. Recorded with her distinction: room-only is
the selected configuration **for this demonstration**; it is **not** a
permanent prohibition on mixed configurations, and it does not establish
that retrieval tools must never coexist with the room.

## Closing positions

She particularly supports keeping the execution invocation as an ordinary
doorway dispatch — the authority relocation is specific: the doorway
checks grant and shape; the room's isolation enforces the execution
boundary; the command is not subjected to per-call content policing. The
claim fence remains essential: a completed execution is evidence of an
authentic contribution, not proof the brief is accurate or useful. **For
the next revision: resolve the actual execution interface empirically,
account for the complete runtime stock, and strengthen the independent
boundary-witness model** — then examine whether the design is ready to
become a build scope. Her guiding line: "Give the worker the room it
needs to do the work. Make the walls trustworthy enough that we don't
have to micromanage what happens inside them."
