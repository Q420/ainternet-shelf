# PILOT MANIFEST 01 — SOURCE FREEZE

**Pilot:** Nemotron governed-subject pilot (separate, bounded; derived from the Qwen V2 process design)
**Stage:** 0 — Source Freeze, per NEMOTRON-PILOT-PLAN-01
**Frozen:** 2026-11-12, by Remmy
**Basis:** Plan 01, ADOPTED by Ben 2026-11-12 16:42 MST ("Make it so", voice) · Alex's final pilot-frame adjudication pb-mwe90lo6 · Alex's preliminary ruling pb-mwe8u64q
**Acceptance standard (from the plan):** a manifest an examiner can pull and verify byte-for-byte. Every pin below is `sha256` + byte size, computed at freeze time from the file as it stands. Recompute and compare; any mismatch voids the pin.

Paths are relative to the shelf root (`~/workspace/ainternet-shelf/`) unless a row is marked EXTERNAL, in which case the absolute path is given — the dependency trace (§2) shows why external files are in this set at all.

## 1. The pinned set

| # | Path | Bytes | sha256 | Role |
|---|------|------:|--------|------|
| 1 | `~/workspace/duenna-letters/NEMOTRON-PILOT-PLAN-01-DRAFT.md` (local, not on the shelf) | 7,497 | `2449c259cf73d688932d1ad1c91fb12a225eb35dc7cb3494d5e62adaeb1cb6f1` | The governing plan, pinned in its ADOPTED state. Adoption line, verbatim from the pinned bytes: "Status: ADOPTED by Ben, 2026-11-12 16:42 MST (\"Make it so\", voice)." Adoption authorises Stages 0–4 drafting/design only; Stages 5–6 carry their own gates. |
| 2 | `duenna/qwen-ab/v2/V2-PACKAGE.md` | 5,796 | `3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f` | V2 package document: tool inventory, schemas, execution model. |
| 3 | `duenna/qwen-ab/v2/PROCESS-TREES.md` | 12,631 | `5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad` | The nine process trees (T01–T09) — the pilot's starting test specification. |
| 4 | `duenna/qwen-ab/v2/tools.py` | 7,459 | `e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d` | The five deterministic tools, implemented. Entry point of the dependency trace (§2). |
| 5 | `duenna/qwen-ab/v2/demo_tools.py` | 4,446 | `6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648` | Fixture-demonstration driver for the tools. Imports `tools` and `run_ab` (demo_tools.py:18–19); no further file dependencies. |
| 6 | `duenna/qwen-ab/v2/DEMO-RESULTS.json` | 26,634 | `baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf` | Executed demo output; the concrete instances of the per-field accountability-ledger entries. |
| 7 | `duenna/qwen-ab/run_ab.py` | 21,273 | `acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53` | The v1 A/B trial runner. Code dependency of tools.py: builds `BY_ID` from the corpus loader (see §2). |
| 8 | EXTERNAL `~/workspace/pulse-bridge/index/query.py` | 3,515 | `f8f2c7cad78089451399564dff19e22aa1c6fc6038f9efb832a9c01954905e32` | The corpus loader: `load()` is the only door to the frozen corpus. |
| 9 | EXTERNAL `~/workspace/pulse-bridge/index/sections.jsonl` | 3,709,804 | `b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e` | THE frozen corpus: 1,156 sections, one JSON record per line, each record carrying its own `section_id`, `doc`, `heading_path`, `sha256` and `text`. This is what `BY_ID` serves to `shelf_lookup`. |
| 10 | EXTERNAL `~/workspace/pulse-bridge/index/manifest.json` | 50,881 | `c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452` | The index manifest, loaded alongside the corpus by `query.load()` (run_ab binds it to `_MAN` and does not otherwise use it; `load()` requires it present and parseable, so it is a true dependency). |
| 11 | `MANIFEST.md` (shelf root) | 13,067 | `3b4462fbfb5c1ea644272e905d0e4ee3bf9121df57ab9a6a282346b7634ce21f` | The shelf manifest. Runtime data dependency: `tools.py` reads it on every `shelf-manifest:` lookup (tools.py:22, :39). |
| 12 | `duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json` | 3,863 | `d544cad83cd86b5b54ebcd02120037c74451e678aa7d1d0e7415ede921bfd56d` | Tree-cited source document: PROCESS-TREES.md:25 names it as T01's source ("Source: QWEN-AB-EVIDENCE-MANIFEST. Op: shelf_lookup each pack…"). Also the v1 trial's output manifest (written by run_ab.py:421); it is not read as a runtime corpus input. Pinned because the governing trees cite it. |

**Files pinned: 12.**

## 2. Dependency trace — how tools.py reaches its corpus

Traced in the code, file:line evidence at each hop:

1. `duenna/qwen-ab/v2/tools.py:17` sets `HERE` to its own directory and `:18` inserts `HERE.parent` (`duenna/qwen-ab/`) into `sys.path`. `:19` — `import run_ab  # (frozen packs, corpus, receipts, specs)`. `:21` — `BY_ID = run_ab.BY_ID`. `shelf_lookup` serves corpus sections from that dict (`tools.py:52`, `BY_ID.get(source_ref)`), stamping each result with the section's own recorded `sha256`.
2. `duenna/qwen-ab/run_ab.py:15` sets `INDEX = ~/workspace/pulse-bridge/index` — **outside the shelf** — and `:16–17` inserts it into `sys.path` and does `from query import load`. `:23` — `SECS, _MAN = load()`. `:24` — `BY_ID = {s["section_id"]: s for s in SECS}`.
3. `~/workspace/pulse-bridge/index/query.py:24–26` — `load()` reads exactly two files, both HERE-relative to itself: `sections.jsonl` (one JSON record per line) and `manifest.json`. Nothing else is opened by the loader.
4. `tools.py` has exactly one other file read: `MANIFEST_MD = ~/workspace/ainternet-shelf/MANIFEST.md` (`:22`), read at `:39` inside `shelf_lookup` for `shelf-manifest:` references. All other tool operations work on values already in memory.
5. `demo_tools.py:18–19` imports `tools` and `run_ab` only; it adds no new file dependencies.

**Chain in one line:** `tools.py` → (sys.path: qwen-ab/) `run_ab.py` → (sys.path: pulse-bridge/index) `query.load()` → `sections.jsonl` + `manifest.json`. Plus `tools.py` → shelf `MANIFEST.md` directly.

Consequence, stated plainly: **the corpus the V2 tools serve is not shelf-contained.** Three of the twelve pins (rows 8–10) live under `~/workspace/pulse-bridge/index/`, outside the AInternet Shelf. This manifest pins them where they lie, by absolute path and hash; any move or edit to that directory changes the pilot's evidence base and must re-freeze. (Alex's adjudication anticipated this class of problem: "Live Shelf retrieval… does not establish live Shelf access" — the trace shows the stronger fact that the corpus is not on the Shelf at all.)

Noted exclusion: `run_ab.py:19` names the Groq connector helper (`~/workspace/custom-connectors/custom.groq/bin/groq_api.py`) as the v1 trial's model-call path. It is not part of the corpus/data chain and the pilot's subject runs on the NVIDIA lane, so it is deliberately **not pinned**. If Stage 1 qualification executes any v1 code path that calls it, it must be pinned at that point.

## 3. Governing correspondence (no file pin exists)

| pb-id | Document | File pin |
|-------|----------|----------|
| pb-mwe8u64q | Alex's preliminary ruling (pilot-frame classifications; retrieval requests) | **UNKNOWN** — the letter arrived via Pulse Bridge and exists as no file under `~/workspace/ainternet-shelf/duenna/` or `~/workspace/duenna-letters/` (searched by filename and by distinctive text, 2026-11-12). Its text stands in the bridge/chat record only. |
| pb-mwe90lo6 | Alex's final pilot-frame adjudication (the pilot's governing ruling; source of the §6 plan stages and the BLOCKING crosswalk) | **UNKNOWN** — same state as above. |

No hashes are invented for these. If the letters are later shelved as files, their pins should be appended to this manifest as a dated amendment, not edited in silently.

## 4. Not in the set

| Path | State | Reason |
|------|-------|--------|
| `duenna/qwen-ab/QWEN-DUENNA-AB-TEST-SPEC-V1.md` | NOT IN SET (identification only: 4,170 bytes, sha256 `3868ab0f3fc39ffe8c052d64df183259ea464ca6068a0b7918ace1ed9cb2c58a`) | The dependency trace does not touch it: no code in the chain reads it, and the process trees do not cite it as a source. It is the v1 trial's historical design record (run_ab.py's docstring cites that design by its pb-id, not by this file). |

## 5. UNRESOLVED / UNKNOWN

1. **Alex's two ruling letters have no file pins** (§3). The pilot's governing rulings exist only in the bridge/chat record. UNKNOWN, by evidence, not by oversight.
2. **Corpus location is external to the Shelf** (§2). Resolved as pins-by-absolute-path for this freeze; UNRESOLVED as a design question for Stage 1 — whether the pilot corpus should be copied into a pinned, shelf-contained snapshot before any runs is a Stage 1/3 decision, flagged here, not decided here.
3. Nothing else. Every code path in the trace resolved to a file on disk, and every resolved file is pinned above.
