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
