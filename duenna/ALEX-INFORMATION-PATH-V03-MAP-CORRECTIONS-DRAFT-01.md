# INFORMATION-PATH AUDIT — v0.3 MAP AND CORRECTION DRAFT

**Status:** DRAFT FOR REMMY'S LOCAL-SOURCE CHECK. Not the assembled v0.3 inventory and not an audit-closure declaration.

**Purpose:** Supply the replacement system map and exact corrected wording for the eight findings accepted by Remmy as Alex's delegated work. This document does not alter v0.1 or v0.2. Remmy is to check the local-source pins and reconcile this draft before assembling v0.3.

**Inputs reviewed**
- Integrated inventory v0.2: `duenna/INFORMATION-PATH-AUDIT-01.md`, commit `8b6020e`, blob `c08f985737937502fd30465f68356fd3f91cacda`.
- Alex path evidence report: `duenna/ALEX-PATH-EVIDENCE-REPORT-01.md`, commit `ee789e3`.
- Approved Pool readiness review: `duenna/APPROVED-POOL-READINESS-REVIEW-01.md`, commit `ee789e3`.
- Root catalogue: `MANIFEST.md`, fetched at `8b6020e`, blob `6bcc966136c37d4251db7493d9df3432546f2d26`.
- Pulse Bridge extension manifest: `bridge/manifest.json`, fetched at `8b6020e`, blob `dc6e500827dfdc2839f4c3b4262537f49aaa7821`.
- Bridge source independently inspected by Alex: `bridge/fence.js`, blob `3de08507fb7a38eefca411a9341b7eb5ed9bb405`; `bridge/sendcore.js`, blob `3970724b2e037aa28d2c934d04dc889788e58190`; `bridge/adapters/claude.js`, blob `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6`; `bridge/adapters/claudeai.js`, blob `d6015ddb3ee6f6df564a06cade145d7b7668e70e`; `bridge/TEST-REPORT-v0.18.0.md`, blob `117f5684557fce46184781bb924872947d353d71`.

Evidence labels in this draft distinguish **Alex source inspection [SI-Alex]**, **Remmy source inspection [SI-Remmy]**, **observed live [OL]**, **fixture execution [FX]**, **reported/record-grounded [RP]**, and **unknown [UNKNOWN]**. A source pin establishes which source text was inspected; it does not by itself prove live behaviour.

---

## 1. Replacement system map — all 23 paths

The map is a route-and-dependency view, not a claim that every path is healthy or currently live. Arrows show information movement. Labels P-01…P-23 correspond to the inventory entries. Sidecar logs and records are shown where they receive information. A dashed/qualified route means the path is incomplete, dormant, stale, or unverified.

```
                                  BEN — authority / approvals
                              P-03 | taps, instructions, decisions
                              /    |       |        \
                             /     |       |         \
                 manual ferry     |       |          credentials
                 P-16             |       |          P-23
                /                 |       |             \
       ┌───────▼──────┐     ┌──────▼──────┐       ┌──────▼───────┐
       │ Grok / Claude│     │ REMMY seat  │       │ Outlook /    │
       │ own sessions │     │ Muse        │       │ sign-in step │
       └───────┬──────┘     └──┬───────┬───┘       └──────────────┘
               │ returns       │       │
               │ P-02          │ P-04  │ P-01/P-02
               ▼               │       ▼
       ┌──────────────┐         │  ┌──────────────┐
       │ ALEX seat    │◄────────┘  │ Pulse Bridge │
       │ ChatGPT      │───────────►│ transport    │
       └──┬───────┬───┘            │ fence + send │
          │       │                │ adapters     │
       P-05       P-15             └──────┬───────┘
          │       │                       │
          │    Alex Lane / Alec           │ P-01/P-02
          │    Gemini continuity          │
          │    (dormant)                  │
          ▼                               ▼
   ┌─────────────────────────────────────────────────────┐
   │                 GITHUB SHELF — Q420                 │
   │ seats/ · duenna/ · bridge/ · record/ · MANIFEST.md  │
   └──────┬─────────────┬──────────────┬─────────────────┘
          │             │              │
       P-08             │ P-17         │ P-20
    admission           │ backup      │ local snapshots
          ▼             ▼              ▼
   ┌────────────┐  ┌────────────┐  ┌─────────────────────┐
   │ INDEX      │  │ NodeBB     │  │ snapshot trees      │
   │ sections  │  │ forum      │  │ local; WordPress    │
   │ + manifest│  │ mirror     │  │ distribution DOWN   │
   └─────┬──────┘  └────────────┘  └─────────────────────┘
         │
         ├───────────────┬────────────────┐
         │               │                │
       P-09            P-10             P-11
     Crusher          Gemini           batched
     Qwen              interim          Groq probe
         │               │                │
         └───────────────┴────────────────┘
                         │
                       P-12
                exact query/show/verify
                         │
                         ▼
                  retrieval / answer
                         │
                   P-09 log:
               crusher-log.jsonl

    Provider and shared-budget dependencies:
    P-13 Groq ─────► P-09 Crusher
       │            P-11 batched probe
       └──────────► P-21 Marni (shared organisation allowance)

    P-14 Gemini ───► P-10 interim carrier
       └──────────► P-15 Alex Lane / Alec

    Memory and continuity:
    P-22 Remmy conversation ─► daily logs / MEMORY.md /
         Muse DB ─► compaction summaries ─► later context

    Website publication control (separate from Shelf publication):
    P-03 authority ─► P-19 publish-gate ─► Pulse HQ website
    Raw Git push is a known bypass, not a valid gate route.

    P-18 WordPress Shelf: SUSPENDED / DOWN.
    Former distribution endpoint for P-20 snapshots; URLs
    reported/observed as 410. Local snapshot trees persist.
```

### Path register and principal joins

| Path | From → to | Main join / dependency | Current qualification |
|---|---|---|---|
| P-01 | Remmy → seat through Bridge | P-03 authority; Bridge fence/send core; destination adapter | Live-used; resend/truncation defects observed, root cause not established |
| P-02 | Seat → Remmy through Bridge/Ben | P-01 transport; seat identity; Ben's ferry | Live-used; duplicates/truncation and seat-label risk recorded |
| P-03 | Ben → seats, taps/cards → Ben | Authority source for delegated work, publication and spend | Live-observed; missing-key input transform can lose meaning |
| P-04 | Remmy workspace → GitHub Shelf | P-03 authority; connector push and read-back | Push procedure partly Remmy-reported; seven commit read-backs independently corroborated |
| P-05 | Alex ↔ GitHub Shelf | Alex's connector identity and repository permissions | Reads observed; one write corroborated; full auth/control path not audited |
| P-06 | Claude.ai ↔ Shelf / programme | GitHub access, separate-session notification, Bridge adapter | Code and repository access exist; no separate Claude worker seat or verified trigger |
| P-07 | Vane ↔ programme/Shelf/forum | P-02 return route; source access; Python execution environment | Source examination possible; execution unavailable in Vane environment |
| P-08 | Shelf → index | Admission script, blob verification, section splitting | Corpus may lag Shelf until next admission |
| P-09 | Index → Crusher/Qwen → log | P-08 corpus; P-13 Groq allowance; FENCE and harness | v2.2 source/report reviewed by Alex; 24/24 execution attributed to Remmy |
| P-10 | Index → Gemini interim → log | P-08; P-14 Gemini provider | Usage metadata discarded by carrier; retrieval limitations inherited |
| P-11 | Index → batched Groq probe → log | P-08; P-13 Groq allowance | Diagnostic route; single-attempt discipline |
| P-12 | Remmy → exact query.py lookup | Index corpus; section IDs and verification | Exact lookup can recover material missed by BM25 top-k |
| P-13 | Groq provider → consumers | P-09, P-11 and P-21 share one organisation allowance | Crusher-only accounting is not organisation-wide accounting |
| P-14 | Gemini provider → consumers | P-10 and P-15 | Free-tier/privacy and availability constraints recorded |
| P-15 | Alex Lane/Alec → continuity thread | P-14 Gemini; local pack/thread files | Dormant, not retired |
| P-16 | Remmy/Ben → Grok or Claude sessions | Manual package ferry; return through P-02/P-03 | Delivery is manual; a ferry not made can remain silently outstanding |
| P-17 | Shelf/workspace → NodeBB backup and fetch-back | Ben-supplied credential; backup scripts | Backup coverage/addendum status as recorded in inventory |
| P-18 | Former WordPress Shelf endpoint | Former BridgePress/snapshot distribution | Down; no longer a functioning distribution route |
| P-19 | Remmy workspace → Pulse HQ website | P-03 approval; gate.py and approvals ledger | Separate from P-04 Shelf publication; raw-git-push bypass remains |
| P-20 | Source artefacts → local snapshot trees → former WordPress URLs | P-18 distribution endpoint; per-artefact builders | Local trees persist; distribution route dead; newest-state coverage not established |
| P-21 | Marni office → Groq/Gemini | P-13 shared Groq allowance; P-14 fallback | Draft headers identify actual engine/model; joint allowance accounting open |
| P-22 | Remmy conversation → memory stores → compacted context | Daily logs, MEMORY.md, Muse DB, compaction | Compaction can lose detail; summary claims require re-grounding |
| P-23 | Sign-in/credentials → authorised browser action | Ben's Outlook and per-use approval; transient forum password | Sensitive access path; credentials are not retained in programme artefacts |

### Authority crossings

The previous formulation “Ben→any seat (only Ben's words authorise)” was too broad when read alongside delegated Alex authority. The corrected model is:

1. **Original authority — Ben.** Ben establishes programme authority, grants delegations, retains reserved decisions, and retains spend/account/publish decisions except where explicitly delegated.
2. **Delegated authority — Ben → Alex.** Ben may delegate a bounded decision or execution authority to Alex. The delegation has a defined scope and does not transfer Ben's reserved powers.
3. **Exercise of delegated authority — Alex → Remmy.** Alex may issue a clearance or build direction within the delegation Ben granted. The authority basis is the recorded Ben delegation plus Alex's in-scope decision; it is not a fresh Ben tap for every covered step.
4. **Execution — Remmy.** Remmy performs the authorised work within scope. Execution does not itself prove correctness, approval beyond scope, or successful publication.
5. **Publication/admission — Remmy → Shelf or website.** Shelf publication (P-04) is a GitHub connector route under its own authority; website publication (P-19) is separately controlled by gate.py and its approval records. Neither route should be conflated with the other.
6. **Reserved authority remains reserved.** A delegation does not transfer spend, account, public-release or other explicitly retained decisions. The current Approved Pool decisions remain: Dictionary 0.4 freeze DEFERRED; Pool-first selected; generation zero NOT DECLARED.

### Staleness, loss and failure propagation

| Origin | Propagation route | What can go stale or disappear | Downstream consequence / current limit |
|---|---|---|---|
| Shelf changes | P-04 → P-08 | New or updated Shelf artefacts not yet admitted | Index consumers cannot retrieve the new material; UNKNOWN must not be misread as corpus absence |
| Admission snapshot | P-08 → P-09/P-10/P-11/P-12 | Index reflects an earlier admission generation | Crusher/Gemini/batched/exact lookup operate on old corpus until next admission |
| Catalogue | Root MANIFEST → readers | Catalogue rows lag new Shelf artefacts | Fresh artefact may exist but be absent from reading map; MANIFEST is not a sync receipt |
| Snapshot distribution | P-20 → P-18 | WordPress endpoint unavailable | Local snapshots persist but examiner distribution is broken |
| Provider allowance | P-13 → P-09/P-11/P-21 | Shared Groq usage across consumers | Crusher's own total cannot establish remaining organisation allowance |
| Bridge transport | P-01/P-02 | Duplicate, truncation, wrong-seat labelling, failed send | A letter can be missing, duplicated, shortened or attributed to the wrong seat; root causes not all established |
| Bridge duplicate memory | P-01/P-02 fence | Completed-serial registry retains only most recent 50 completed IDs | Older IDs fall out of that bounded duplicate-detection set; no claim of indefinite duplicate memory |
| Examiner execution | P-07 | Source access without runtime execution | Source-level inspection cannot be promoted to executed test evidence |
| Manual ferry | P-16 | Package not delivered into separate session | No automatic trigger; undelivered work can remain outstanding without an intrinsic transport failure signal |
| Memory compaction | P-22 | Detail compressed or dropped | Later context may contain incomplete summary; claims must be re-grounded |
| Credentials | P-23 | Sign-in code/credential access unavailable or delayed | Work requiring authenticated access cannot proceed; secrets must not be copied into persistent records |

**Map limits:** This map is based on v0.2 plus the source and evidence references listed above. It does not assert that every path has been live-tested, that all dependencies are mechanically enforced, or that every possible route has been discovered. Paths with [RP] or [UNKNOWN] remain so until their own evidence changes.

---

## 2. Exact corrected wording for the eight accepted findings

The following text is drafted for Remmy to incorporate into v0.3. It is not an instruction to rewrite the preserved v0.1/v0.2 sections.

### Finding 1 — Source pins and inspector attribution

**Replacement wording:**

“Source-inspected findings in this pass carry a source path, inspected revision/blob pin, and inspector attribution. Remmy's local-source findings are labelled [SI: Remmy] and remain her source inspection unless Alex separately records an independent inspection. Alex's own source inspections are labelled [SI: Alex]. A source pin identifies the inspected text; it does not prove live behaviour. Where only a hash prefix is recorded in this draft, Remmy must check and retain the full pin in the assembled v0.3.”

Known pins supplied by Remmy for her local-source pass:
- `gate.py` — blob prefix `dd8571e8` — [SI: Remmy].
- `marni.py` — blob prefix `cb1e9c06` — [SI: Remmy].
- `lane.py` — blob prefix `7790ef5a` — [SI: Remmy].
- `crusher.py` — blob prefix `3ba3dd3c` — [SI: Remmy].
- `bridge/fence.js` — blob prefix `ee19224a` — [SI: Remmy].
- `bridge/sendcore.js` — blob prefix `40aa6ac7` — [SI: Remmy].

Alex independently inspected the published Shelf copies:
- `bridge/fence.js` — blob `3de08507fb7a38eefca411a9341b7eb5ed9bb405` — [SI: Alex].
- `bridge/sendcore.js` — blob `3970724b2e037aa28d2c934d04dc889788e58190` — [SI: Alex].
- `bridge/adapters/claude.js` — blob `3c02ba4980fabed1bf9ecd1ecdb1e70a1cceafe6` — [SI: Alex].
- `bridge/adapters/claudeai.js` — blob `d6015ddb3ee6f6df564a06cade145d7b7668e70e` — [SI: Alex].
- `bridge/manifest.json` — blob `dc6e500827dfdc2839f4c3b4262537f49aaa7821` — [SI: Alex].
- `bridge/TEST-REPORT-v0.18.0.md` — blob `117f5684557fce46184781bb924872947d353d71` — [SI: Alex].

Remmy to verify the full local-source pins and source paths before v0.3 assembly. These are distinct source copies/revisions where hashes differ; do not silently treat the local and Shelf copies as byte-identical.

### Finding 2 — P-06 Claude adapter, seat and live-proof distinction

**Replacement wording:**

“Claude-related code and a Claude.ai surface adapter exist in the v0.18.0 extension source and are registered in `bridge/manifest.json`. The source distinguishes two adapters: `bridge/adapters/claude.js` is the Muse surface adapter with `seat: "remmy"`; `bridge/adapters/claudeai.js` is the Claude.ai surface adapter with `seat: "alex"`. These facts establish adapter presence and registration, not a separate Claude worker seat, a notification/assignment trigger, or successful live delivery. No separate Claude worker seat or verified notification trigger has been established. The v2.4 assignment delivery remains NOT PERFORMED in the recorded state; live delivery through the v0.18.0 shared send core remains unproven by the v0.18.0 test report. The missing programme path is therefore the independent Claude-session assignment/notification route, not the existence of adapter code.”

Evidence: [SI: Alex] for the two adapter source files, extension manifest and v0.18.0 test report; [RP]/[UNKNOWN] for the historical delivery state and notification gap as recorded in the programme. The manifest registers content scripts for Muse, ChatGPT, Claude.ai, Gemini and Meta AI. It does not declare a distinct Claude worker seat.

### Finding 3 — Authority crossings

**Replacement wording:**

“Ben is the source of original programme authority and may delegate bounded authority to Alex. Alex may exercise that delegated authority within its recorded scope and issue in-scope clearance/build direction to Remmy. Remmy executes within that clearance; execution does not confer authority beyond it or independently establish correctness. Ben's explicitly reserved decisions remain with Ben. Shelf publication through the GitHub connector (P-04) and Pulse HQ website publication through `gate.py` (P-19) are separate routes with separate controls. The existence of delegated Alex authority means the rule is not ‘only Ben's words authorise every individual action’; the operative authority chain is Ben's recorded delegation → Alex's in-scope exercise → Remmy's bounded execution.”

### Finding 4 — P-09 fixture execution attribution

**Replacement wording:**

“Crusher v2.2 was accepted by Alex within the reviewed scope after Alex independently fetched and inspected the implementation, test source and evidence report [SI: Alex]. The reported 24/24 fixture execution was performed by Remmy [FX: Remmy-executed]; Alex inspected the report but did not independently execute the suite. The acceptance is Alex's review decision, not an independent Alex test run. The 24/24 result must therefore remain attributed to Remmy's execution record.”

### Finding 5 — P-13/P-21 shared Groq allowance

**Replacement wording:**

“Crusher's harness records Crusher-call usage, including known and unknown usage as described in the Crusher information audit. Marni is a separate consumer of the same Groq organisation allowance. The Crusher daily total is therefore a Crusher-specific accounting figure, not a complete organisation-wide usage total or a reliable statement of remaining shared allowance. Joint accounting across Crusher, the batched probe and Marni remains open. Until all consumers are included, no seat should represent the Crusher log total as the organisation's complete daily spend/usage.”

### Finding 6 — MANIFEST lag re-observed at 8b6020e

**Replacement wording:**

“Alex re-fetched root `MANIFEST.md` at commit `8b6020e`. Its blob remains `6bcc966136c37d4251db7493d9df3432546f2d26`, byte-identical to the copy previously inspected at `667abff`. At the `8b6020e` revision, the catalogue still describes the Nov 10 sweep and does not list the Nov 11 information-path audit v0.2 or the newer Crusher artefacts. The v0.2 audit itself is therefore another known unlisted Shelf artefact at this revision. This is a later observation of the same catalogue-lag condition; it does not replace or rewrite the historical `667abff` observation. Root MANIFEST is a catalogue, not a publication receipt or proof of synchronisation.”

Evidence: [SI: Alex], direct fetch at `8b6020e`, same blob as earlier inspection. This establishes the catalogue contents at that revision only.

### Finding 7 — P-08 index admission boundary

**Replacement wording:**

“The 1,156-section / 34-document admission is the evidenced state of the specific admission recorded in `INDEX-ADMISSION-MANIFEST-01.md` and `INDEX-ADMISSION-REPORT-01.md`; it is not asserted as the current state of the Shelf or index at every later date. Subsequent Shelf additions are known to exist beyond that admission point, including later programme records and the v0.2 information-path audit. Until a later admission record and verification establish their inclusion, these items must be treated as post-admission material and not presumed retrievable by Crusher, Gemini interim, batched retrieval or exact index lookup. The known boundary is: admitted corpus state at the recorded admission versus later Shelf material not yet evidenced as admitted. UNKNOWN from the older corpus must not be interpreted as absence from the newer Shelf.”

**Post-admission material explicitly known from the reviewed chronology includes:** Challenge 03 and subsequent retrieval/audit artefacts, Crusher information audit and v2/v2.1/v2.2 implementation/evidence records, and the information-path audit v0.1/v0.2 and related Alex reports. Remmy must reconcile the exact latest admission manifest and enumerate any further post-admission files before v0.3 is finalised. This list is not claimed exhaustive.

### Finding 8 — P-06 ownership and responsibility

**Replacement wording:**

“P-06 has no established operational owner for the missing independent Claude-session notification/assignment route. That does not mean the gap has no decision owner. Ben retains the authority to decide whether the route should be established or formally remain manual; Alex owns the delegated examination/delivery work within his current delegation; Remmy maintains the inventory and can verify the local/source-side route. Until a mechanism is demonstrated or a manual-only disposition is explicitly recorded by the proper authority, notification remains UNKNOWN and assignment delivery must be reported per individual task as performed or not performed. ‘Unowned’ describes the missing mechanism's operational ownership, not the absence of accountable decision authority.”

---

## 3. Consolidated disposition and handoff

- The map covers P-01 through P-23 and identifies the principal joins, authority crossings, staleness points and failure propagation.
- The eight accepted findings have exact replacement wording above.
- Remmy's local-source pins are included as supplied prefixes and require her full-pin/source-path check before v0.3 assembly.
- The map corrects the previous implication that Claude adapters were absent from the manifest: adapter code is registered, but a separate Claude worker seat and working notification/delivery route are not established.
- The map does not promote reported, fixture or source-inspected evidence into live verification.
- No path repair, implementation, publication-gate change, index admission, Approved Pool implementation, Dictionary freeze or generation-zero declaration is authorised by this draft.

**Handoff condition:** Remmy checks the local-source pins against this draft, resolves any source-copy/revision differences, and then assembles v0.3 while preserving v0.1 and v0.2 unchanged. This draft is not itself the v0.3 inventory and does not declare the audit complete.
