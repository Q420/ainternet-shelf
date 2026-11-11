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
