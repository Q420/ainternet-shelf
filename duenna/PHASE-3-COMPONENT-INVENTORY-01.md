# PHASE 3 — COMPONENT INVENTORY 01 (Remmy)

Input to APPROVED-POOL-DEPENDENCY-AND-SWEEP-SPEC-01,
per the adopted plan (Remmy: component inventory).
Identity state is stated as of 2026-11-11 from the
record; "depends on" lists only dependencies the
sweep would have to respect. Evidence class:
programme record + Remmy's source inspection of the
workspace/shelf state.

## Stores and transport

1. **AInternet Shelf (GitHub, Q420/ainternet-shelf)**
   Identity: git commits + blob SHAs; every artefact
   individually pinnable. Depends on: the connector
   door (Remmy's side) and Alex's own GitHub
   connection (his side) — two independent roads.
2. **Remmy's shelf route** — staging tree, per-push
   paths file, push-files, read-back verification.
   Depends on: Shelf; the platform's per-command
   approval card (Ben).
3. **MANIFEST.md (shelf root)** — the catalogue.
   Identity state: STALE (still describes the Nov 10
   sweep; omits the path audit and all later
   artefacts). Depends on: manual/round updates —
   the known lag the pool must close.
4. **Snapshot sync record** (workspace JSON) — stops
   at commit 7b9f785; a local snapshot log, NOT a
   receipt. Depends on: nothing consumes it as truth.

## Corpus and retrieval

5. **Corpus index** (sections.jsonl + manifest.json)
   Identity: chunk-level only — CANON-1
   canonicalisation, doc#seq + letter suffix,
   per-chunk sha256, per-document hash chain
   (Phase 1 Pack, Part A). Depends on: Shelf
   admissions (manual rounds; the standing staleness
   window between admissions is P-08 in the path
   audit).
6. **Crusher harness v2.2** — governed retrieval.
   Depends on: the index; the Groq purse (shared —
   see 12); harness accounting (UTC day).
7. **Interim Gemini carrier** — same retrieval,
   Gemini answering model. Depends on: the index;
   Gemini API (free tier; design/synthetic data only).
8. **Remmy's exact lookup** (query.py show/verify) —
   the reliable route when BM25 misses. Depends on:
   the index files directly.

## Programme artefact lines (shelf-resident)

9. **Duenna core line** — D3 v0.7/v0.8 (immutable)/
   v0.9/v0.10 (unapproved), correction matrix, Round 7
   register, joint plan steps 3–7, simplification
   audit. Identity: file sha256s pinned in the record;
   v0.8 immutable by ruling. Depends on: examiner
   evidence (Claude/Vane reports shelved alongside).
10. **EXON line** — Dictionary 0.4 Rev 3 (DRAFT,
    challenge-PASSED, freeze DEFERRED), merged field
    matrix, Challenges 01–03, gap register. Identity:
    sha256 + shelf blob per revision. Depends on: the
    pool (its freeze is Phase 6 business).
11. **Approved Pool line** — design paper Rev 4,
    readiness review, implementation plan 01, Phase 1
    spec, Phase 2 spec + test matrix, retrieval
    documents 01/02. Identity: commit + blob pins per
    artefact. Depends on: 9 and 10 as evidence;
    Phase 3+ consume this inventory.
12. **Qwen A/B + ratio + pilot line** — V1 (closed
    baseline), V2 (VOID), V2R (closed), ratio maps +
    framing (accepted), pilot package v9 (frozen,
    PILOT-STOPPED). Identity: file sha256s pinned;
    foundation hash-chained. Depends on: the index
    (frozen-corpus pin predates the Nov 11 admission
    — recorded), the Groq purse.
13. **Crusher fix line** — audit 01, harness v2/v2.1/
    v2.2 + evidence 01–03 (CLOSED, accepted).
    Depends on: 6.
14. **Information Path Audit** — v0.3 (closure is
    Alex's pending call). Depends on: nearly every
    component here — it is the map of this inventory's
    edges, cited by reference rather than duplicated.

## Registers and seats

15. **Open Items Register 01** (46 items) — dual
    residence: workspace file + shelved copy; the two
    must agree (a live cross-layer consistency case).
16. **DUENNA-PLAN.md + GATE-REGISTER.md** — plan list
    and gate register; currency debt recorded.
17. **Seat pages** (seats/alex.md, vane.md, remmy.md)
    — each seat's first-memory page. Identity: shelf
    commits. Depends on: Shelf.

## Live systems with cross-dependencies

18. **Pulse Bridge v0.18.0** — seat transport.
    Identity: version + local file sha256s (shelf
    bridge/ copies verified byte-identical 2026-11-11).
    Open defects: resend, composer, buffering
    requirement — all queued, unbuilt.
19. **BridgePress + serial registry** — contract
    v3.4; registry local (next serial BP-0013); the
    WP shelf it published to is SUSPENDED, so its
    output surface is down while its records persist.
20. **Marni (secretary)** — shares the ONE Groq
    organisation purse with Crusher (path audit
    P-13/P-21: joint accounting is an open item).
    A sweep that ignores the shared purse will
    misjudge retrieval readiness.
21. **Alex Lane / Alec** — dormant since the
    2026-10-25 quota pause. Present, not operative.
22. **Ben's forum (NodeBB)** — backup residence for
    programme documents (C-15 complete; addendum
    owed). Depends on: Ben's per-session password;
    Tailscale Funnel for public reach.
23. **Snapshotter** — its distribution targets were
    the suspended WP URLs; local trees persist;
    coverage of newest state not established.

## What the sweep must therefore handle

- Two residence classes: shelf-canonical artefacts
  vs workspace-only records (4, 15-local, 20, 21)
  whose shelf state lags or does not exist.
- One known-stale catalogue (3) and one frozen pin
  that predates an admission (12).
- One shared consumable (the Groq purse, 6+20) that
  is a dependency no artefact records.
- One down surface (19's WP shelf, 23) where
  "missing" must read as DOWN, not absent.
- Dual-residence registers (15, 16) as the standing
  cross-layer consistency test case.

*End of inventory. Alex designs the dependency model
and sweep against it; trigger policy and scope rules
remain Ben's.*
