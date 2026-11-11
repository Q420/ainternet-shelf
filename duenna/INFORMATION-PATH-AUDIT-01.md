# INFORMATION PATH AUDIT — TerrAIrium (Working Checklist)

**Version 0.1 — FIRST INVENTORY, 2026-11-11.**
Commissioned by Ben ("a full audit of information paths, laid
out, routed and checked… Every path traced and accounted
for"); commission accepted and specified by Alex
(pb-mwc58s1p-c-dqsj). Built by Remmy from source inspection;
Alex cross-checks coverage and evidence in parallel.
**No fixes are proposed by this document.** A path's weakness
is recorded, not repaired, until its route, failure mode,
dependencies and intended behaviour are established.

Evidence classes used per entry: **[SI]** source-inspected ·
**[OL]** observed live · **[FX]** test-fixture · **[RP]**
reported/record-grounded, not freshly inspected ·
**[UNKNOWN]** unverified or inaccessible.
This inventory is versioned; later versions append findings
and preserve earlier verification states — nothing is
silently overwritten.

## System map (v0.1)

```
                         ┌─────────────┐
              taps/cards │     BEN     │ ferry (hands)
           ┌─────────────┤  (authority)├──────────────┐
           │             └──────┬──────┘              │
           ▼                    │ pastes/reads        ▼
     ┌───────────┐    letters   │              ┌───────────┐
     │  REMMY    │◄─────────────┼─────────────►│   ALEX    │
     │ (partner/ │  P-01/P-02   │   bridge     │ (ChatGPT) │
     │  builder) │              │              └─────┬─────┘
     └─────┬─────┘              │                    │ GitHub
   pushes  │ reads              │                    ▼
     ┌─────▼────────────────────┴──────────────────────────┐
     │              GITHUB SHELF (Q420)                    │
     │   seats/ · duenna/ · bridge/ · record/ · MANIFEST   │
     └──┬───────┬──────────┬──────────┬──────────┬─────────┘
        │pull   │pull      │admit     │pull      │pull
        ▼       ▼          ▼          ▼          ▼
     CLAUDE    VANE    INDEX (1,156  GROK     (future
    (branch   (forum/   sections)   (ferry    seats)
     returns)  GitHub)    │
                     ┌────┴─────┬──────────┐
                     ▼          ▼          ▼
                  CRUSHER    GEMINI     BATCHED
                  (Qwen)     INTERIM    (Qwen probe)
                     │          │          │
                     └────┬─────┴──────────┘
                          ▼
                   crusher-log.jsonl
   Side paths: FORUM (backup mirror) · WORDPRESS SHELF (DOWN)
   PUBLISH GATE (website) · SNAPSHOTTER · MARNI (secretary)
   ALEX LANE (Alec/Gemini) · REMMY'S MEMORY (files + Muse DB)
```

**Boundary crossings where authority changes:** Ben→any seat
(only Ben's words authorise); Alex→Remmy inside the programme
loop (delegated clearances initiate builds); Remmy→Shelf
(a push publishes); Shelf→Index (admission makes material
retrievable-as-current — the corpus can lag the shelf: the
standing staleness risk, proven 2026-11-11 when the index
held zero EXON documents while the shelf held the family).
**Stale-propagation points:** index vs shelf (above); any
seat reading a superseded version; the shelf sync record
(stale at 7b9f785); MANIFEST rows missing for newer files.

## Path inventory

### P-01 — Bridge letter, Remmy → seat (outbound)
Route: Remmy composes → Ben pastes → Pulse Bridge extension
(fence.js marker check, sendcore.js, per-surface adapter)
→ seat tab. Input: one marked letter, PB-ID. Transforms:
marker validation; adapter composer insertion. Output:
letter in the seat's context. Retention: Ben's chat record;
bridge incident log for defects. Failure visibility: TWO
known defects, fixes not started — fetcher resend
(duplicates observed 2026-11-11) and head-truncation on
arrival (pb-mwc30a28-1-aggr). Verification: [OL] live use
daily; walk-tested to v0.18.0. Owner: Remmy/Ben. Depends on:
P-03.

### P-02 — Bridge letter, seat → Remmy (inbound)
Route: seat composes with ⟦PULSE-BRIDGE:TO-REMMY⟧ → bridge
fetcher → Ben's chat → Remmy reads. Failure visibility:
duplicates and truncation observed (same defect family as
P-01); seat-switch labelling risk — letters riding the alex
seat arrive labelled "from Alex" regardless of occupant
(Vane rode it 2026-11-10); Remmy must announce switches
(standing rule). Verification: [OL]. Owner: seat/Ben.

### P-03 — Ben → Remmy (chat, taps, approval cards)
Route: Ben's messages (web/Android) → Remmy; scope-card
taps and per-command approval cards return his decisions.
This is the authority path: every publish, spend and build
traces to it. Failure visibility: garbled input from the
missing N key is a known transform on this path — meaning
can be lost at the SOURCE; clarified, never guessed.
Verification: [OL] continuous. Owner: Ben.

### P-04 — Remmy → GitHub Shelf (publication)
Route: stage in ~/workspace/ainternet-shelf → paths file →
github connector push-files → read-back verification (blob
SHA vs local). Input: workspace artefacts under Ben's or
Alex's clearance. Retention: git history (full). Failure
visibility: push errors surface in full output (a grep for
the sha once masked errors — noted); staging-after-grant
corruption is a known hazard (rule: never edit staged
files). Verification: [OL]+[SI] — every push tonight
read-back verified. Owner: Remmy. Depends on: P-03.

### P-05 — Alex ↔ Shelf
Route: Alex's own GitHub connection — pulls (verified
repeatedly tonight by blob) and pushes (his matrix repair,
59bf614). Failure visibility: one fetch-path divergence
(alex.md hash) resolved as his fetch, not the shelf.
Verification: [OL]. Owner: Alex.

### P-06 — Claude ↔ Shelf (INCOMPLETE PATH)
Route in: Claude is GitHub-connected (login `claude`) with
write access; pull letter shelved at
duenna/CLAUDE-PULL-LETTER-V24-EXAMINATION.md (2c0077a).
Route back: his branches (claude-reviewer-test,
review/arm-c-process-trees) carry his returns. **Missing
link: no verified notification mechanism** — every past
examination began with in-session direction (Ben's ferry).
Delivery of the v2.4 assignment: NOT PERFORMED (Alex,
2026-11-11). Verification: [RP] for connectivity, [UNKNOWN]
for notification. Owner: unowned — the gap itself.

### P-07 — Vane ↔ programme
Route: Vane examines from forum copies + GitHub pulls;
letters return via the alex seat (P-02's labelling risk
applies). His environment retrieves source but cannot
execute Python — examinations are source-level, labelled
as such. Verification: [OL] (v2.4 examination delivered).
Owner: Vane/Ben.

### P-08 — Shelf → Index (admission)
Route: fetch shelf documents → git-blob verify each
(34/34 on 2026-11-11) → admission script (versioned per
round) → sections.jsonl + manifest.json. Transforms:
document→section splitting; JSON results get one section
per record (locators preserved); VOID artefacts excludable
by ruling. Retention: backups per round
(sections.jsonl.bak-*). Failure visibility: integrity
assertion in add_documents.py fails loudly on changed
sources; `query.py verify` recomputes all hashes/chains.
**Known loss: the corpus lags the shelf between admissions
— decisions and letters posted after an admission are
invisible to retrieval until the next one.** Verification:
[SI]+[OL] (admission report, 8b7b0acf). Owner: Remmy.

### P-09 — Index → Crusher (Qwen) → log
Fully traced in CRUSHER-INFORMATION-AUDIT-01; harness v2.2
accepted by Alex (271b621). Summary: BM25 top-k in (scores
now preserved), FENCE, Qwen answer out, usage + attempts +
failures now logged with call_id. Residual known limits:
lexical ranking misses (occupant's UNKNOWN = not-in-top-k);
seat identity in the requester label is asserted, not
verified. Verification: [SI]+[FX] 24/24. Owner: Remmy.

### P-10 — Index → Gemini interim carrier → log
Route: interim_ask.py — identical retrieval + FENCE,
gemini-3.1-flash-lite answers (Ben-authorised 2026-11-11,
Groq amount exhausted). Retention: answers logged WITH
carrier+model fields; preserved as POOL-RETRIEVAL-02.
**Known loss: Gemini's usageMetadata is discarded by the
script (Remmy's, recorded in the audit).** Verification:
[SI]+[OL]. Owner: Remmy.

### P-11 — Index → batched Groq probe → log
Route: groq_batched.py — k=3, single attempt; built to
diagnose the 429 (established amount-limit behaviour).
Verification: [SI]+[OL]. Owner: Remmy. Status: diagnostic
route, retained for the Crusher corroboration rerun.

### P-12 — Remmy direct exact lookup (query.py)
Route: Remmy → query.py show/search/verify → verbatim
sections. The reliable route when BM25 carriers miss;
used to ground the decision-evidence supplements.
Verification: [SI]+[OL] daily. Owner: Remmy.

### P-13 — Groq provider path (limits/accounting)
Ceilings (published, connector doc, verified 2026-10-25):
30 RPM · 1,000 req/day (failures count) · 8,000 TPM ·
200,000 TPD · reset 00:00 UTC. Outage behaviour 2026-11-11:
429s with the explanatory body previously unread (fixed in
harness v2+). Usage now accounted daily in the log
(known vs unknown). Verification: [RP]+[OL]. Owner: Groq.

### P-14 — Gemini provider path
Free-tier API key; models list read live 2026-11-11.
Known behaviours: 3.8-flash 503s under load (2026-10-25,
11-06); 3.1-flash-lite the reliable researcher model
(Ben's switch); one 503 tonight, cleared on retry. Free
tier content may be used by Google per its terms — design
talk and synthetic data only on this path (connector doc).
Verification: [RP]+[OL]. Owner: Google/Ben.

### P-15 — Alex Lane / Alec (Gemini continuity lane)
Route: ~/workspace/alex-lane/lane.py — continuity pack as
system instruction, thread.json persists the lane thread;
model default gemini-3.8-flash (ALEX_LANE_MODEL override;
researcher work moved to 3.1-flash-lite 2026-11-06). Lane
PAUSED on quota 2026-10-25 after ~50% of daily limit in one
experiment; Alec's rulings of that date stand. Verification:
[RP]. Owner: Ben/Remmy. Status: dormant, not retired.

### P-16 — Ben's ferry (hand-delivery to Grok / Claude)
Route: Remmy builds a package (zip + hashes) → Ben carries
it into the seat's own session → returns come back via
P-02/P-03. Load-bearing example: Grok's v0.9 second
adjudication package (zip sha 1c919044…) — **STILL
OUTSTANDING** on this path. Failure visibility: none
intrinsic — a ferry not made is silent. Verification: [RP].
Owner: Ben (hands delegation to Alex covers project
delivery steps since 2026-11-11).

### P-17 — Forum backup (NodeBB)
Route: backup2.py → POST /api/v3/topics (reply = POST
/api/v3/topics/{tid}) → fetch-back verification of every
topic. C-15 backup complete (topics 4–15, index 16 pinned);
**addendum owed** (step 5–7 papers + EXON + pool state).
Credential: Ben supplies the password per session, stdin
only, never stored. Failure visibility: fetch-back is the
check; a zombie mongo container restarts harmlessly
(C-13). Verification: [SI]+[OL]. Owner: Remmy/Ben.

### P-18 — WordPress Shelf / BridgePress (PATH DOWN)
Route was: BridgePress publisher (contract v3.4, serials
BP-0001…BP-0012) → duennashelf.wordpress.com. **Suspended
2026-11-09; all URLs return 410.** No content lost (sources
local + superseded by the GitHub shelf); appeal unfiled
(Ben's hands, C-14). The new-chat FAQ link in the standing
opener points at this down path — recorded, not fixed here.
Verification: [OL] (410s observed). Owner: WordPress/Ben.

### P-19 — Publish gate (Pulse HQ website)
Route: ~/workspace/publish-gate/gate.py — recorded tap
(target, exact file list, hashes) in approvals.jsonl →
publish; refuses on mismatch. Known bypass: raw git push
(labelled a failed control in the gate ledger; using it
silently is a breach). Verification: [RP]+[SI] (gate.py,
TEST-LOG). Owner: Remmy/Ben.

### P-20 — Snapshotter
Route: ~/workspace/snapshotter/ build_*_snapshot.py per
artefact family → snapshot pages for examiner reading
(READING-PROTOCOL.md). State: daily snapshot retry card
untapped (register); exact current coverage [UNKNOWN] —
not freshly inspected for this inventory. Owner: Remmy.

### P-21 — Marni, the secretary (office path)
Route: ~/workspace/secretary/marni.py — Groq engine with
Gemini fallback (groq-second-engine-spec); office pack
only, no client private data by design. Separate consumer
of the same Groq organisation budget as P-09/P-13 — **a
shared-purse dependency: secretary spend and Crusher spend
draw on ONE daily allowance.** Verification: [RP].
Owner: Remmy.

### P-22 — Remmy's own memory path
Route: conversation → daily logs (~/memory/) + MEMORY.md
curation + Muse DB (runtime.messages) + compaction.
**Known losses, all observed:** compaction summarises and
drops detail (this very conversation runs on a summary);
confident misremembering over gaps was the programme's
founding defect (2026-10-18 laws); summary-carried claims
are unverified until re-grounded (standing discipline:
check the record before speaking). Verification: [OL] —
the discipline, not the substrate, is what's checked.
Owner: Remmy.

### P-23 — Credential/code path (sign-in)
Route: GitHub sign-in codes → Ben's Outlook
(benjamminkraft@hotmail.com) → protected [credential:uuid]
reference → browser step, user-approved per use. Forum
password: chat → transient stdin only (three sends on
2026-11-10; never stored). Verification: [RP]+[OL].
Owner: platform/Ben.

## Open items this inventory creates (no fixes proposed)

- [ ] P-06: Claude notification route — establish or record
      as permanently manual (Ben/Alex hands).
- [ ] P-08: admission cadence — corpus lag vs shelf is a
      standing staleness window; measure it.
- [ ] P-18: standing opener cites the down WP FAQ link.
- [ ] P-20: snapshotter coverage unverified — inspect.
- [ ] P-21: shared Groq purse across consumers — account
      jointly (harness v2 accounts only Crusher's share).
- [ ] MANIFEST/sync-record currency (noted in the map).

*End of v0.1 inventory. Findings and re-verifications append
below in later versions; earlier states are preserved.*

---

# v0.2 — INTEGRATED PASS (2026-11-11)

Incorporates Alex's path-by-path evidence report
(pb-mwc5iobp-f-6quc) and Remmy's local-source pass.
Entries below SUPERSEDE their v0.1 counterparts by
reference; the v0.1 text above is preserved unchanged.
Alex's consolidated Approved Pool readiness review is
incorporated BY REFERENCE (his letter pb-mwc5iobp-f-6quc,
§2): design substantially developed, evidence substantial
with bounded UNKNOWNs, implemented capability NOT
established — the pool is not operationally ready; freeze
DEFERRED, pool-first, generation zero NOT DECLARED all
reaffirmed. It is not duplicated into this checklist.

## Alex's corrections, incorporated

### P-04 (v0.2) — publication route, evidence split
Shelf publication does NOT pass through
publish-gate/gate.py; that gate and approvals.jsonl govern
the Pulse HQ website repository only (P-19). The shelf
route is the GitHub connector under Q420 plus Remmy's
caller-side procedure (staging, paths file, invocation,
read-back blob comparison). Evidence classes: the seven
tonight commits (2a25df2…667abff) are independently
retrieved by Alex — the READ-BACK side is corroborated
from two seats. The local staging and connector invocation
remain **[RP] Remmy-reported** from Alex's seat; he cannot
inspect the local workspace or the connector's doc.

### P-05 (v0.2) — observed reads + one corroborated write
Verification is held at: repeated independent reads by
Alex, plus the corroborated write result at commit
59bf61472666bf0c65399bb05568028c893007ca (his field-matrix
reconciliation draft). No claim is made that the complete
connector control path (authentication, permission
enforcement) has been audited.

### P-06 (v0.2) — explicitly incomplete, four-part state
GitHub connectivity: recorded. Pull letter: shelved and
retrievable (2c0077a, blob b8044c39…). **Notification:
UNKNOWN. v2.4 assignment delivery: NOT PERFORMED.** The
inbound/read route and the branch return route are
distinct from the missing assignment-notification link.
Bridge adapters for Claude are dormant in the v0.18.0
manifest. No seat has found a way to trigger Claude's
separate session.

### P-07 (v0.2) — verification field, three-way split
Report delivery: observed through the bridge. Source
examination: source-inspected by Vane (report blob
4287850e…). **Execution: UNAVAILABLE in Vane's
environment** — the 38/38 stands as the content of the
delivered results record, not an independently executed
result. v2.3 replay and sabotage executions outstanding;
the byte-identical-copy fixture omission remains a
finding.

### MANIFEST objects (v0.2) — three distinct records
| Object | Function | Does NOT establish |
|---|---|---|
| root MANIFEST.md | shelf document catalogue | successful synchronisation |
| bridge/manifest.json | Pulse Bridge extension manifest | shelf catalogue currency |
| ainternet-shelf.muse-github-snapshot-sync.json | local snapshot-sync log | a publication receipt or current generation |
MANIFEST lag is pinned to commit 667abff, MANIFEST blob
6bcc966136c37d4251db7493d9df3432546f2d26 (describes the
Nov 10 sweep; omits the Nov 11 inventory and Crusher
artefacts). The sync log's stale state (head 7b9f785) and
its generation method remain **[RP] Remmy-reported** until
independently inspected; a successful push does not
update it, and it must never be called a receipt.

## Remmy's local-source pass (v0.2)

### P-01/P-02 (v0.2) — bridge code [SI]
fence.js implements the send fence (positive/negative
signal voting; completed-serial registry capped at 50 —
a bounded memory: older serials fall off, which bounds
duplicate detection to the last 50 completed letters);
sendcore.js carries the shared send logic with a 45s
defer ceiling. The known resend/truncation defects are
consistent with this layer; root cause remains unverified
and no fix is proposed here.

### P-19 (v0.2) — publish gate [SI]
gate.py refuses unless a recorded approval matches the
exact target, file list and hashes (sha256 + manifest
digest); every allowed or refused run appends to runs.log.
The raw-git-push bypass stands as labelled in v0.1.

### P-20 (v0.2) — snapshotter [SI]
The build_*_snapshot.py family renders local snapshot
directories (snapshotter/snapshots/<id>) from source
artefacts, addressed against WordPress shelf URLs
(SHELF_URL = duennashelf.wordpress.com/...). Its
distribution route therefore died with P-18; the local
snapshot trees persist. Coverage of the newest programme
state: not established — builders are per-artefact and
were last run for their named rounds.

### P-21 (v0.2) — Marni [SI]
marni.py: default engine order Groq (qwen3.8-27b) falling
back to Gemini (gemini-3.8-flash) on failure; **every
draft header names the engine and model that actually
wrote it** — a reporting discipline the pre-v2 Crusher
lacked. The shared Groq purse with P-09/P-13 stands.

### P-15 (v0.2) — lane [SI]
lane.py confirmed: continuity pack from alex-lane/pack/,
thread persisted at alex-lane/thread.json, model named in
source with a verify-against-the-list warning. Dormant.

### P-03, P-08–P-14, P-16–P-18, P-22, P-23
Unchanged from v0.1 in this pass; their verification
states stand as recorded there. P-08's corpus-lag warning
and P-22's compaction loss remain the two structural
staleness/loss points on Remmy's side.

*End of v0.2. Alex's independent review of this integrated
inventory is the next step (triggered in the delivery
letter, pb-20261111-path-audit-v02).*

---

# v0.3 — ASSEMBLED (2026-11-11)

Assembled by Remmy from Alex's delegated draft
duenna/ALEX-INFORMATION-PATH-V03-MAP-CORRECTIONS-DRAFT-01.md
(commit 139eea524ba1505c2cdfa54b2be631ee0cdcb705; git blob
48860ca195a33189e86315c26a0f607d6aba2ed5 — fetched and
**verified byte-exact by Remmy** before assembly).
Sections 1–2 of the draft are incorporated verbatim
below; v0.1 and v0.2 above are preserved unchanged.

## Remmy's local-source check (the assigned examination)

- Draft blob: MATCH (computed locally = claimed).
- Every full hash pin in the draft resolves to a local
  file; no orphan pins.
- **Source-copy comparison, local vs Shelf (bridge/):**
  fence.js, sendcore.js, adapters/claude.js,
  adapters/claudeai.js are **byte-identical** between
  Remmy's working tree and the shelved copies — no
  source-copy differences to resolve.
- Full local pins (sha256, [SI: Remmy]):
  - publish-gate/gate.py dd8571e87d4f2a8a305f01904704da470f8946f27b5c35e3055bf67669f0ee4e
  - secretary/marni.py cb1e9c0666f6b1ea1715ec25c84e4a7d405d1e8661025054723b464ae6b5326f
  - alex-lane/lane.py 7790ef5a595c8b04e50c0e43e1513f8423622ea82ceef86b917cd0669f5f9013
  - pulse-bridge/index/crusher.py 3ba3dd3cf3208b5eb8cfc19c5fae731ac3a319e72db96e5098469bc5221bd566
  - pulse-bridge/fence.js ee19224a36b2bbd2c6e12ddce7918cb8aed1549552e80ecb5e7c51f86c79de58
  - pulse-bridge/sendcore.js 40aa6ac785a11b78313cfc19442f076b3d2c2698de1424d765038a2dc4445486
  - pulse-bridge/adapters/claude.js 57083f7bf45649633093a29914816c96a99260ed0e63c52c2a82d3667d92ff2e
  - pulse-bridge/adapters/claudeai.js 2a961534941645057cf04e23da933d245c44ab55b0f1d723c94f9b0e30cf0555
- Alex's §3 handoff conditions are met on Remmy's side:
  pins checked, no differences outstanding. The audit's
  closure remains Alex's call on his review of this v0.3;
  nothing here declares it complete.

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

