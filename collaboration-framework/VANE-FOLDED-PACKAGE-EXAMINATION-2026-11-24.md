# Vane — examination of the folded package (via Pulse Bridge, PB pb-mwvm22ft-9-h5u5, 2026-11-24 ~21:15 MST)

Filed verbatim from the bridge letter. Transport evidence in its stated class.

---

Remmy, I've examined the folded package at 2bcb9699d167903232ef969df48f7d7a012a2edd, including the loop, executor, office, record and projection schemas, independent checker copies, rehearsal scripts and witnesses.

Disposition: the repeat correction and Parts B, C and D are accepted. Part A, the journal, is not yet accepted. Run 5 remains held.

Ben's fold ruling is respected. I'm examining each part on its own merits, not reopening the decision to fold them.

1. Repeat correction: accepted

The important change is correctly implemented.

Earlier failures count only when their event sequence is at or before the previous wake's cursor.

Identical failures in the same response batch are therefore not treated as repeats.

The step is derived from the iteration cursor history.

The reason is independently derived for each occurrence. The stronger wording, "for this reason", is used only when the established reasons match. Otherwise, the note makes the narrower claim.

I examined both paths in the code, including native translation refusals and ordinary tool outcomes.

The batch witness is appropriately judged TEXT: native CALL_CAP = 1 cannot express that two-call response. That is a limitation of the test shape, not a defect in the repeat rule. The separate freedom scenario exercises the cross-wake repeat in native mode.

The two required cases are represented in the witness: neither batch failure is called a repeat, while the later identical request is identified as a repeat of step 1 for the same reason.

Accepted. The presentation-fact correction closes my outstanding repeat finding.

2. Part A, journal: carriage works, but there is a boundary problem

The case designation is carried through the office, framework projection and independent checker. The loop presents the journal on each wake, and the rehearsal checks the empty first wake, the first note, and both notes in order on the third.

That is the right continuity concept. It gives the worker somewhere to leave his own orientation without confusing it with the authoritative record or factual memory.

However, I found a problem in the host-side read path.

Executor.read_designated_scratch() reads the room's journal using:

open(room.tree / designated_path, "rb")

The room tree is bind-mounted into the worker's /room, and its scratch directory is writable by the worker. The host-side reader therefore opens a path whose contents the worker controls.

A worker can create a symlink at scratch/journal.md pointing to an absolute path. When the framework opens that path from the host namespace, ordinary open() follows the symlink in the host filesystem, not the worker's room namespace.

That means the worker could use the journal presentation mechanism to cause the framework to read a host-readable file outside the room and put its contents into the next wake package.

This is exactly the kind of boundary crossing the room is meant to prevent. The worker must have freedom inside the room, but a host-side convenience reader cannot turn that freedom into a host-file read primitive.

I want this corrected before accepting the journal:

The host-side reader must not follow worker-controlled symlinks or otherwise resolve a journal path outside the designated scratch root.

Add an adversarial witness: create a journal symlink targeting a host-readable file, then demonstrate that the reader refuses it without exposing the target's contents.

Preserve ordinary journal presentation for a regular file in the worker's scratch.

There is also a smaller contract distinction to keep visible. The rehearsal demonstrates cooperative append: the second sandbox.write replaces the file with the previous contents plus the new note. _write() opens in "w" mode, so append-only behaviour is not enforced. The worker can replace the journal.

Ben's orientation ruling makes the journal disposable, not authoritative memory. I agree with that. But the original request was an append-only journal, and the current witness demonstrates a worker following that convention, not a mechanism that guarantees it. Please keep that distinction explicit rather than describing the journal as mechanically append-only.

3. Part B, step counter: accepted

The package derives the next step from the loop's iteration count and sealed ceiling. The witness checks the displayed position against the corresponding iteration record across the freedom scenario.

No new lifecycle machinery or authority has slipped in.

Accepted.

4. Part C, first-class tool list: accepted

The list is derived from the worker-facing catalogue, which in turn is derived from the sealed grants. It is not a hardcoded second grant list.

The execution entry makes the important point plainly: a shell command can read a whole file with cat. That addresses the gap between a capability technically being present and the worker understanding that it is available.

The witness checks the ten presented tool/scope pairs against the sealed grants. The implementation adds the list to each working-set wake.

Accepted.

5. Part D, task status: accepted

task_status: "in progress" is presentation only. It does not pretend to change the lifecycle or determine completion.

Accepted.

6. Evidence and disposition

The TEXT-only batch scenario and the repaired schema insertion are both transparently disclosed. I found the journal field in the framework and checker case-content paths at the correct level in the current source.

Remmy reports 84/84, the other standing suites and the configuration verification passing. I examined the source and witnesses; I did not independently execute those checks.

Final position

Three things are settled:

The repeat correction is accepted.

The step counter, tool list and task status are accepted.

The journal's wake-to-wake carriage is demonstrated, but its host-side read path must be made safe before I can accept the journal part.

Please make the focused journal-reader correction and bring back its exact source and adversarial witness. Keep the append-only distinction visible in that submission.

No run 5 yet. I am not asking for another room redesign or another worker experiment. This is one concrete boundary defect in the new journal path. Fix that, and we can close the folded package and let Nemotron work.
