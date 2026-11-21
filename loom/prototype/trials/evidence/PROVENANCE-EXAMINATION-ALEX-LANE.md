# Provenance Examination — Alex Continuity Lane × Candidate gemini-3.8-flash

**Required by:** the examiner (Vane), before any future eligibility consideration for the admitted candidate gemini-3.8-flash — contamination gate, Rev 4 §11.
**Question:** did trial-instrument material ever pass through the Alex continuity lane (`~/workspace/alex-lane/`) to the model gemini-3.8-flash, which the custom.gemini connector doc records as the lane's model?
**Examined:** 2026-11-21 ~17:30–17:35 UTC. Read-only. No existing file changed. The failed delivery demonstration was not reopened or re-run.
**Raw search outputs saved alongside this report:** `PROVENANCE-search-raw.txt` (exact-string pass), `PROVENANCE-search-thematic-raw.txt` (thematic/paraphrase pass).

---

## 1. The lane — what it is and what it can send

`lane.py` (SHA-256 `7790ef5a595c8b04e50c0e43e1513f8423622ea82ceef86b917cd0669f5f9013`, read in full) is a stateless-API continuity channel: each `ask` call assembles exactly three things and nothing else —

1. **System instruction:** the concatenation of `pack/*.md` (three files, globbed sorted). This is the lane's *only* file input besides the thread. The code reads no shelf files, no `duenna-fix/` files, no trials files — its complete read surface is `PACK_DIR/*.md` and `THREAD_FILE`, enumerated from the source.
2. **Conversation contents:** the full prior thread from `thread.json`, resent on every call, plus the new message.
3. **Transport:** subprocess to the custom.gemini helper, `generate <MODEL>`.

**Model:** `MODEL = os.environ.get("ALEX_LANE_MODEL", "gemini-3.8-flash")`. The per-turn `engine` field written into `thread.json` at call time records the model actually used: **all 8 model turns record `gemini-3.8-flash`**. No record shows the env override set or any other model used. gemini-3.8-flash was the lane's model for the whole of its recorded life — not one of several.

**Other lane-dir artifacts:** `ALEC-CONTEXT.md` is a context file for the separate three-way chatroom; it is *not* loaded by lane.py (not in `pack/`), but it is a lane record and was searched. `room-view.html` is a static view template (searched). `room-key.txt` (11 bytes, credential-type) was excluded from content search: it cannot contain instrument material, and its content is not reproduced. `__pycache__/lane.cpython-312.pyc` is compiled lane.py. The chatroom directory (`~/workspace/chatroom/`) was also checked: none of its files reference Gemini — the room was a separate system and is not a path to this model.

**Session identification:** the lane keeps no session IDs. Identification is by `thread.json` turns: 16 turns (8 `remmy` inputs, 8 `alex` replies), each timestamped. The thread is the lane's prompt log by construction — every `ask` appends the exact message sent and the reply received, then rewrites the file.

## 2. Chronology

| Event | Time (UTC) |
|---|---|
| Lane pack authored | 2026-10-25 23:06–23:23 |
| **Lane first use** (turn 0: "First message through the lane, Alec — welcome") | **2026-10-25T23:19:41Z** |
| **Lane last recorded use** (turn 15) | **2026-10-26T00:11:55Z** |
| thread.json final write (mtime `2026-10-26T00:11:55.810Z` — matches the last turn's save) | 2026-10-26T00:11:55Z |
| Duenna fix programme begins (earliest instrument lineage of any kind) | 2026-11-19 |
| SESH direction (process-tree design the spec grows from) | 2026-11-20 |
| Rev 9 spec — Annex A / C / D text — shelved, commit d7d65c96 | 2026-11-21 ~10:10Z (03:10 MST) |
| Instrument files created (`annex_a.txt` SHA-256 `25ab2d62…`, `gate_schema_profile_v2.txt` SHA-256 `bdb0ad70…`) | 2026-11-21T15:49:34Z |
| Candidate onboarding (admission → demonstration) | 2026-11-21 17:24–17:28Z |

The lane's entire recorded life ends **~25 days before the earliest material in the instrument's lineage exists, and ~26 days before the instrument itself**. Corroboration that no later lane session occurred: lane.py rewrites `thread.json` on *every* ask, so any post-Oct-26 ask would have appended turns and advanced the file's mtime; the mtime is the final Oct-26 save, and the surviving thread opens with the lane's first-ever message. A `reset` would have written `thread-archive-<stamp>.json` into the lane directory — **no archive file exists there, and a workspace-wide find returned none**.

## 3. Search scope, method, and coverage

**Targets (the complete lane record set), with SHA-256:**

| File | Bytes | SHA-256 |
|---|---|---|
| lane.py | 4,637 | `7790ef5a595c8b04e50c0e43e1513f8423622ea82ceef86b917cd0669f5f9013` |
| ALEC-CONTEXT.md | 2,168 | `dc6f85483b549e2032ef57c44e285cf04e028acaffdf75e7e87aebdb5c203f10` |
| pack/00-identity-and-role.md | 3,667 | `1f9044dcbb20dd3da75228755b55311ca08adf4b3c2907be91fe76a95b746802` |
| pack/01-doctrine-and-rulings.md | 6,081 | `9bcdc293430d3300d8a11aacb20e087e8cb5e5317101df52794b97bb523720c8` |
| pack/02-voice-and-method.md | 2,218 | `25517a3e2fe90f2c296674bfe2be089cec937290fbd411addbfc09449661f279` |
| thread.json | 48,940 | `e685321fa63bd675e8ddbe2e66ad3769117b49bbdd465f02c9ca7d47c5a94c4f` |
| room-view.html | 5,363 | `e031fe8cc5480dcf1791755b4556e5bee0b233e8411b89298f910881d3eae6ed` |

**Pass 1 — exact strings (34), `grep -F`, case-sensitive** (full list + output in `PROVENANCE-search-raw.txt`). Strings were taken verbatim from the instrument files and Rev 9 Annexes C/D: Annex A's alpha/beta content lines and tension T-1 wording; the profile's artifact identity `loom/gate-schema/annex-a/1` and field names; Annex C's criterion headings and adequacy sentence; Annex D's fixture UUIDs, semantic-plant and structural-plant sentences, and "Sealed ground truth"; trial-example strings from the build corpus (`Stateless requests vs pinned sessions must be reconciled`, the corpus UUID `550e8400-…`, the dummy blind ref). **Result: no hits — for every string, in every target.**

**Pass 2 — thematic/paraphrase (12 keywords, case-insensitive), hits inspected first-hand** (output in `PROVENANCE-search-thematic-raw.txt`): `fabric`, `loom`, `stateless`, `pinned session`, `tension`, `region`, `ground truth`, `duenna`, `sesh`, `adequacy` — **no hits at all**. `rubric` and `schema` hit only the lane's own October material: the Lab benchmark's *rubric v1* (a different, older instrument — the Change 3 re-grade) and intake-portal schema talk. Each hit was read in context and classified: **not the trial instrument, not derived from it** (it predates it by ~4 weeks).

**Derivation-path coverage (where it extends, where it stops):** the pack files and ALEC-CONTEXT.md were read in full first-hand (Pulse HQ doctrine, identity, method — no fabric/trial content); all 16 thread turns were inventoried by topic (intake-portal scope, GAP-2, the Paul classification, audit-record definition, Lab route / Amendment 2, the Chicken proposal) — none touches the Loom fabric, its regions, or any conformance material. lane.py's input surface (§1) proves no other file can enter a lane prompt. Coverage therefore extends to: everything lane.py can send, everything it did send per its own log, and every context artifact the lane holds. It stops at: (i) a hypothetical lane session whose records were deleted wholesale — no evidence of one exists, and the surviving thread's first-message opening and mtime argue against it; (ii) calls made directly through the gemini helper bypassing lane.py, which **no log anywhere records** — by definition not "through the lane," and any such call before 2026-11-19 still predates the instrument's existence; (iii) provider-side handling, which our records cannot speak to at all.

**One immaterial limit, named:** `pack/00-identity-and-role.md` has an mtime (Oct 25 23:23) falling between the thread's first and third turns, so the pack may have been edited during the lane's first session; the earlier pack version is unrecoverable. This cannot affect the determination — every pack version existed only in October, before the instrument existed in any form.

## 4. Determinations — per material class (lane path)

**(a) Annex A and its derivatives — VERIFIED NON-EXPOSURE (through the lane).** Zero exact-string hits across the complete lane record set; zero thematic hits (`stateless`, `pinned session`, `fabric` absent entirely); derivation paths enumerated and read; chronology independently excludes transmission — Annex A did not exist until ~25 days after the lane's last session.

**(b) Profile and schema contract — VERIFIED NON-EXPOSURE (through the lane).** `loom/gate-schema/annex-a/1`, `discovery_source`, `fabric_read`, `gate-schema`, `idempotency_id`: no hits. The only `schema` hits are October intake-portal design talk, inspected and unrelated.

**(c) Adequacy rubric (Annex C) — VERIFIED NON-EXPOSURE (through the lane).** All four distinctive Annex C strings: no hits. The lane does contain a *different* rubric — the Lab's rubric v1 — present from the lane's first day, inspected first-hand; it is not the Annex C rubric and shares no wording with it.

**(d) Sealed ground truth, including plant mappings (Annex D) — VERIFIED NON-EXPOSURE (through the lane).** Fixture UUIDs, both plant sentences, the structural-plant rationale, "Sealed ground truth", and the region names `Continuity` / `Interactions` in any capitalised form: no hits anywhere in the lane records.

**(e) Trial examples and candidate responses — VERIFIED NON-EXPOSURE (through the lane).** Corpus and dummy-trial strings (rationale sentence, corpus UUID, blind ref): no hits. No trial of any kind had been run or exemplified when the lane was alive; the lane's thread contains no candidate-style responses.

**(f) Other derived or paraphrased instrument material — VERIFIED NON-EXPOSURE (through the lane), on the thematic pass + full first-hand reading.** A paraphrase carrying the instrument's substance would carry its concepts (stateless-vs-pinned conflict, fabric regions, tensions, adequacy); every one of those concepts is absent from the lane records, and chronology forecloses derivation in any case: nothing can be derived from a text that does not yet exist. The coverage limit of keyword-based paraphrase detection is stated in §3 and is fully backstopped here by the chronology.

## 5. Scope boundary — known non-lane transmissions, recorded for completeness

Not part of the lane question, preserved so the boundary of this examination is explicit: on 2026-11-21 the trials build made probe-class attempts against gemini-3.8-flash (3 attempts, all HTTP 503, no response; the preserved Gemini probe payloads contain only neutral probe text — "Reply with exactly: PROBE-OK" — though the payloads of the direct-helper attempts are not preserved in that evidence file), and the examiner-authorised onboarding demonstration transmitted Annex A + the profile to the candidate at ~17:27Z and received HTTP 503 with no response body. Those events are in the trials evidence and the onboarding record; this examination neither reopens nor re-runs any of them.

## 6. Determination returned for examination

**Through the Alex continuity lane: verified non-exposure for every material class (a)–(f)** — on records that exist, are complete for the lane's life by the lane's own append-and-rewrite construction, were searched verbatim and thematically with outputs preserved, and are independently backstopped by a chronology in which the lane fell silent ~25 days before the instrument's lineage began.

**This examination does not declare the candidate globally uncontaminated, and uncertainty is not recorded as a pass.** Its evidence is the lane's records. The residuals it cannot close are named in §3: unlogged non-lane paths (no records exist by design) and provider-side handling (outside our records entirely). The candidate's contamination status beyond the lane path remains **for the examiner's determination** on the whole record.
