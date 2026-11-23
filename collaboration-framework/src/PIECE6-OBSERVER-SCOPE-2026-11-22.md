# Piece 6, part 4 scope — the observer (§3.9) (2026-11-22)

For Vane's examination BEFORE code, in the standing pattern. Governing text: SPEC SHEET Rev 5 §3.9 (R27), §3.11 (R33's observer half), and the §7 Stage 2 checklist line: *"the observer renders the run using only recorded events."* Ben's analysis of 2026-11-22 named this piece's seam in advance: two parts of the system must never keep separate accounts of the same fact — the failure shape of every §3.8 finding. This scope is written against that warning.

## Diagnosis (verified against the source this session)

- **The carried observer renders substrate runs only.** `src/observer/export_events.py` reads the fabric events schema through a read-only URI, verifies with `fabric.engine.verify_chain` under the fabric constitution, and renders the fabric template, whose vocabulary is the prototype's (DISCOVERY reads, regions). It cannot read a framework run: the framework store carries two further columns (`run_id`, `ts`), its own constitution binding, and a wholly different event vocabulary.
- **The bridge is narrower than "two formats" — and that is the risk.** FrameworkStore (ADR-003) deliberately mirrors the substrate's discipline: same insert-only triggers, same hash-chain rule via `fabric.canonical`, and record.py already carries a framework `verify_chain` and `verify_run_binding`. The schemas are *similar*. Similar is not the same: the carried exporter's read query, constitution, and template are all fabric-specific, and a port that quietly reused them would render framework runs under the wrong verification.
- **The derivations the observer must show already exist — once.** Waiting states are derived by the gates enrichment (`derive_waiting`) and the fold (`holder_unavailable`, `seat_stalled` via DRIVER_FAILURE); gate passage, the operative set, claims and coverage by gates.py and orchestrator.py. R27 requires derived matter to be *labelled* derived. §3.8's lesson applies with full force: the observer consumes the one derivation stack read-only; it never re-derives.
- **The carried observer's safety discipline is the piece's inheritance:** read-only URI opens only (never a writable store constructor — observing must not alter the observed, not even an empty file); fail-closed on an unverifiable chain (no page); a missing or empty store refused, never seeded; embedded data escaped for its script context.

## Proposals

- **O1 — a framework observer module, substrate untouched.** New `src/framework/observer.py`: opens a framework run store read-only (SQLite RO URI; FrameworkStore is never instantiated), reads the run's events and run row, and verifies them with the framework's own `verify_chain` + `verify_run_binding`. Any failure — unreadable, missing, empty, unbound, chain-broken — is a refusal with no output.
- **O2 — the render is a data structure first.** `render_observer(events)` returns the observer's account in two tiers, per R27: a **plain-words summary** (run standing; per-part passage and waiting; who waits on what, by state name; the latest contributions, gate outcomes, disagreements, certifications) over the **full event detail** beneath. Every summary statement carries the event positions it rests on. Derived sections are computed by running the existing derivation stack (fold → gates enrichment → orchestrator derivations) over the read events, and are marked derived in the structure itself; recorded facts are presented as recorded.
- **O3 — waiting states by name (R33).** The summary renders `awaiting_gate`, `awaiting_ruling`, `holder_unavailable`, `seat_stalled`, and `paused_by_gate` by name wherever the derivations place them; no waiting state is rendered as progress, and none appears or clears except as the derivations move on recorded events.
- **O4 — sealed material: existence, never content.** Framework events can reference sealed evidence (R7). The observer shows that sealed material exists — its event, its material id, its holding seat — and never its content, carrying the prototype observer's no-sealed-ground-truth boundary into the framework. **(Q1 below.)**
- **O5 — an HTML export in the carried spirit.** A single self-contained page from a NEW framework template (the fabric template untouched), embedding the render via the same script-safe escaping. Plain rendering only: **the living-swarm skin Ben chose is not this piece** — its build stands deferred under his ruling, its design to be planned with Vane separately. This piece builds the account the skin will one day display, and the honesty rules it must obey.
- **O6 — no write path exists.** The module imports no doorway, holds no token, and opens nothing writable. Observing a run leaves its store byte-identical.

## Questions flagged for the examiner

- **Q1 — sealed existence vs content (O4).** The observer is the director's instrument, and the director commissioned the run. Does existence-only still hold for the director, or does the commission change the seal's meaning here? The scope proposes existence-only (the prototype boundary, and the safer default: an observer that can open seals is a doorway by another name), but the question is named rather than settled silently.
- **Q2 — the checker (§3.10, R28).** The §7 line pairs the checker and the observer, but the carried checker verifies substrate runs, and a framework-side independent checker is Stage 2's known remainder (R4 — whose technical independence must not be confused with epistemic independence, per the Piece 6 alignment). This scope proposes §3.9 closes with the **observer only**, the checker named as remaining — not silently absorbed into this piece.
- **Q3 — static export vs live page.** R27 says contributions land "as they land"; the carried observer is a static export, refreshed by re-exporting. This scope proposes the static form for the piece; a live page belongs with the deferred skin work.

## Acceptance sketch (to be settled with the examiner)

1. A render leaves the store byte-identical; the DB is opened read-only only.
2. A tampered chain, a failed run binding, a missing store, and an empty store each produce a refusal and no output.
3. The summary states each waiting state by name for a run standing in it (pre-assembly `awaiting_gate`; a declared `holder_unavailable`; a `seat_stalled` after DRIVER_FAILURE).
4. Every summary statement traces to named event positions; derived sections are marked derived; nothing in the render lacks a recorded source.
5. Sealed content never appears; sealed existence does.
6. A stored value containing `</script>` renders inert in the export.
7. A full run of the §3.8 shape (assembly → certification) renders end to end, showing its operative gate set and its certification coverage as recorded.
8. The substrate observer and its safety suite are untouched and green; all framework regressions green.
