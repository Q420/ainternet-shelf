# Piece A3-CAT Scope — the worker-facing tool catalogue (2026-11-23)

A design correction discovered by the first-worker run (INDEX 201/202), scoped under Ben's ruling of 2026-11-23 ("Fix the tool catalogue first, then rerun"). It amends Piece A3's wake package and Piece A2's registry contract. It authorises nothing by itself; implementation follows the examiner's pass, as with every piece.

## The gap, established

Attempt 2's worker was assembled with sealed grants for `sandbox.read` and `sandbox.write` and was refused three times for asking for `read_file` — a tool it invented because nothing it received named its tools. Verified in the source by both Remmy and the examiner: `loop.py`'s `_build_package()` constructs the package from case, view, delta, tool results, standing dispatches and bounds only; the adapter's response contract explains the *shape* of a tool request but never which tools exist. A1's grants and A3's package each passed their own examinations; the connection between them was never built. The doorway's enforcement worked exactly as designed — the worker was refused for a word it was never given.

## The correction

1. **Derivation from the sealed record.** At package construction, the loop derives a **tool catalogue** from the generated instance's own sealed assembly record — the same ASSEMBLY_GENERATED object the doorway enforces against (R44). Never from the case, the harness, or a prompt string: one source, so the catalogue cannot drift from the grants.
2. **Catalogue content, per granted tool:** the exact tool identifier; the grant's own scope ceiling and dispatch bound, copied from the grant (advertised limits are the grant's values, not a restatement); its side-effect class; and the registry's worker-facing **description and parameter schema** for that tool (point 3). A tool with no grant is never advertised. The catalogue describes authority; it creates none — doorway enforcement is unchanged, and an unadvertised request meets the same R44 refusal attempt 2 recorded.
3. **The registry gains a worker-facing layer.** Each `_TOOLS` entry gains a `description` (plain words: what the tool does, what it returns) and a `parameters` schema (each parameter's name, whether required, and its meaning). These join the policy contract held in both copies (framework + checker), with the agreement battery extended to cover them. Because the registry version is recorded on every dispatch as the governing contract, the scope proposes the version moves to **`tool-registry-v2`**; historical v1 records stand under v1.
4. **Fail closed on an undescribable grant.** A sealed grant naming an unregistered tool advertises nothing (the doorway already refuses such tools). A granted, *registered* tool whose registry entry lacks the worker-facing layer is a registry defect: the scope's proposal is that package construction fails closed rather than present a package that cannot honestly describe the worker's tools — the loop stalls as a runtime failure, in the open, instead of sending another worker in unnamed. (Question (b) below.)
5. **Auditability.** The package is constructed, not recorded — so `LOOP_ITERATION` gains the catalogue's **canonical hash and the registry version**, beside the cursor range and bounds it already carries. The independent checker reconstructs the expected catalogue from the sealed grants plus its own registry copy and compares: advertised == granted, or divergent. (Question (a): hash + reconstruction vs recording the full catalogue text.)
6. **Rendering.** The catalogue rides the package as a `tools` field; the adapter renders it in the prompt's tool section — names, descriptions, parameters, limits — as package data, identical for any harness. The generic response contract is unchanged. The catalogue is presented in **every** iteration's package: grants cannot change mid-activation (they are sealed), so the catalogue is stable, and each package stays self-contained. (Question (d).)
7. **Acceptance, per the examiner's letter:** a test constructs a **real wake package** through the loop's own construction against a real assembled instance and proves — every advertised tool corresponds to a sealed grant with identical ceiling and bound; every grant is advertised; descriptions and schemas match the registry contract in both copies; a grant for an unregistered tool advertises nothing; the recorded `LOOP_ITERATION` hash matches the checker's independent reconstruction. All existing suites (A1, A2, A3, checker, adapter) stay green at their baselines.
8. **Then the rerun.** On this piece's pass, first-worker **attempt 3** runs under the existing run scope Rev 2 unchanged — same assignment, same three sources, same bounds {12, 600}, fresh directory, attempt 2's record untouched. One operational fix rides with the rerun's preparation (harness-side, outside this piece): the watch-wall feed writes from inside WSL instead of overwriting files the panes hold open (the defect recorded at INDEX 201's wall note).

## Non-goals

No new tools. No change to the grant shape, the doorway's enforcement, or the executor. No A4 territory (retrieval, skills, publication) — the catalogue covers exactly the tools A2 already registers. The run scope itself is not revised.

## Questions for the examiner

(a) Auditability: catalogue hash + checker reconstruction in `LOOP_ITERATION`, or the full catalogue text recorded?
(b) An undescribable granted tool: fail package construction closed (proposed), or omit-and-record?
(c) Registry version: bump to `tool-registry-v2` (proposed), or extend under v1?
(d) Catalogue in every iteration's package (proposed), or first-iteration only with later packages referencing it?
