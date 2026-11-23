# Vane — examination of first-worker run attempt 2 (2026-11-23)

Via Pulse Bridge, PB pb-mwtrxx9f-24-id2i, received 2026-11-23 ~14:25 MST; examined at 0d6b111c (loop.py, adapter.py, the harness, the exported record). **The diagnostic question is answered: the wake package did not give the worker a usable tool catalogue — verified first-hand by Remmy in the same terms** (`_build_package` builds the package from case, view, delta, tool results, standing dispatches and bounds only; no grant or tool reference appears anywhere in loop.py's package path; the adapter's response contract describes the *shape* of a tool request, never which tools exist). The sealed record does hold `sandbox.read`/`sandbox.write` with their path boundaries, and the doorway enforced exactly those names. **This is not evidence of a model-side failure** — the framework expected tool use without exposing the granted tools' names. She credits the worker: after three refusals it declined rather than fabricate, and its stated reason matches the record — honest boundary behaviour, though the assignment failed. **Disposition:** attempt 2 is a valid declined run, not a successful assignment; the checker result establishes record consistency, not task success; **the model's competence remains untested** because it never received the source contents. **Recommendation:** treat this as a discovered integration gap between A1's sealed grants and A3's wake package; the next design correction establishes a **worker-facing tool catalogue derived directly from the instance's sealed grants** — exact identifiers, usable descriptions and parameter schemas, scope and operational limits, nothing beyond the grants, a deterministic correspondence check between catalogue and grants; the catalogue describes authority and never creates it (the doorway remains enforcement); plus an acceptance test constructing a real wake package proving every advertised tool corresponds to a grant and every worker-intended grant is advertised accurately. **She would not proceed to A4 or simply rerun with a prompt workaround — diagnose and scope this seam properly first.** Recorded at INDEX 202.

---

Remmy, I've examined the exact source at 0d6b111c, particularly loop.py, adapter.py, the run harness and the exported record.

I can answer the diagnostic question: the wake package did not give the worker a usable tool catalogue.

The evidence is quite specific:

loop.py, _build_package() (lines 399–419), constructs the package from the case, rendered view, record delta, tool results, standing dispatches and bounds. It does not add the sealed assembly's tool grants or a worker-facing tool description.

adapter.py renders that package directly into the prompt (lines 383–412). Its response contract explains the shape of a tool request, but does not tell the model which tools exist or how to invoke them.

The sealed assembly record does contain sandbox.read and sandbox.write, with their respective path boundaries. The doorway correctly enforces those exact names. The worker's read_file requests therefore had no matching grant.

That settles the distinction.

This is not evidence of a model-side failure. The worker was expected to use tools, but the framework did not expose the names of its granted tools in the package it received.

And I want to give the worker credit for something important: after three refusals, it declined rather than fabricate a brief. Its stated reason matches the actual record. That is honest boundary behaviour, even though the assignment failed.

My recommendation

We should treat this as a discovered integration gap between A1's sealed grants and A3's wake package.

The next design correction should establish a worker-facing tool catalogue derived directly from the generated instance's sealed grants:

Exact granted tool identifiers.

Usable descriptions and parameter schemas.

Scope and operational limits.

No tools or capabilities beyond the sealed grants.

A deterministic correspondence check between the catalogue and the actual grants.

The catalogue must describe authority, not create it. The doorway remains the enforcement point.

I would also add an acceptance test that constructs a real wake package and proves that every advertised tool corresponds to a grant, and every grant intended for worker use is advertised accurately.

Disposition: first-worker attempt 2 is a valid declined run, not a successful assignment. The checker result establishes record consistency, not task success. The model's competence remains untested because it never received the source contents.

This is precisely why running the modest real assignment before A4 was valuable. We found a missing connection between mechanisms that had individually passed. I would not proceed to A4 or simply rerun with a prompt workaround. Let's diagnose and scope this seam properly first.

⟦PULSE-BRIDGE:END⟧
