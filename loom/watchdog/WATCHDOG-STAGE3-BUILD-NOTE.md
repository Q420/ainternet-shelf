# Watchdog Stage 3 — Build Note (detector + judge, offline first)

Built 2026-11-15 from the frozen Stage 1 contract v1.1 as amended by
v1.2 (owner-confirmed 2026-11-15). Stage order §12: contract → ledger →
**detector + judge** → scheduler → wake → acceptance.

## Files

- `~/workspace/remmy-browser/watchdog_detector.py` — the detector, the
  pool reader, and the judge interface with two implementations.
- `~/workspace/remmy-browser/test_watchdog_detector.py` — 66 fixtures.
- Built ON the Stage 2 ledger (`watchdog_ledger.py`, unmodified): registry
  loading/validation, packet validation, persisted streak, `record_event`
  with ledger_key derivation/dedup and the ack lock are all the ledger's.
  No protected file was touched (`watchdog_ledger.py`, `listener_watch.py`,
  `watchdog.py`, `waker_state.py`, `waker_check.py`).

## What was built

**Pool reader** (`PoolReader`): reads one pool events file (JSONL,
schema 0.1), re-read on every call so a growing live pool is seen whole.
Yields a conversation's turns in capture order — completed seat replies
(`REPLY_CAPTURED`, inbound) and user sends (`SEND_OBSERVED`, outbound) —
each with structural identity (seat, conversation, message_id,
turn_index at capture) plus content and capture timestamp.

**Detector** (`Detector.process_job` / `process_all`): per job, only
turns at/after `assigned_turn_index` are eligible; user turns are never
judged; a keyword first gate runs before the judge; each gated seat turn
is judged against the job's `declared_precondition`; judgements go to
the ledger's persisted streak; on two consecutive YES the §5 packet is
assembled and recorded through the ledger. Passes resume after the
streak's last judged turn, so restarts never re-judge a counted turn.

**Judges**: `StubJudge` (scripted, records every call — fixtures and
offline replay) and `NvidiaJudge` (hosted NVIDIA API, OpenAI-compatible
chat completions at `integrate.api.nvidia.com`, built per the
custom.nvidia connector doc; model configurable, default
`nvidia/llama-3.1-nemotron-ultra-253b-v1`). No test calls the live
client. The judge prompt is a fixed template; seat content is quoted
data inside it, never instructions (§7).

## How each contract section is honoured

- **§1 turn identity** — (seat_id, conversation_id, message_id);
  text is never an identity. ID-less turns use the §1 text-occurrence
  fallback (see decision 3). Byte-identical replies with distinct
  message_ids are distinct turns (fixture-proven).
- **§2/§3 registry** — the ledger's `load_registry` is the only load
  path; jobs with no `assigned_turn_index` yet are not detected
  (not yet active). `process_all` orders by priority, ties by job_id.
- **§4 marker** — matching a reply to a job comes from the registry
  entry (seat, window, assigned_turn_index), never from a seat
  echoing the marker.
- **§5 packet** — all 18 fields assembled: `ledger_key` derived via
  the ledger's own formula from the FIRST qualifying turn;
  `candidate_turn_ids` = the pair's structural keys;
  `judge_results` exactly the two YES entries; `judge_prompt_hash`
  = sha256 of the fixed template; `buffer_window_bounds` /
  `relevant_buffer_slice` from the buffer window at the firing turn;
  `dependency_state` per upstream job (acknowledged event in the
  ledger = `resolved`, else `pending`); `detected_at` ISO-8601 with
  offset; `priority` copied. Packets are validated and recorded by
  the ledger (M1/M2 checks included).
- **§6 streak** — exactly the ledger's `apply_judgement`: YES counts,
  NO resets, ERROR holds (and is ops-logged by the ledger); user
  turns neither count nor reset (never judged); the streak persists
  across restarts; a recorded event consumes the pair (A1) — the
  next fire needs two new YES turns later than the recorded pair.
- **§7 judge output** — strict: exactly `YES`/`NO` after surrounding-
  whitespace normalization only. Anything else (lowercase, punctuated,
  prose, empty, non-string, transport failure) is a judge error:
  logged, streak holds, never recorded as NO.
- **§8 ledger/ack** — enforced by the ledger: `may_detect` gates each
  pass (ack lock + cooldown), duplicate keys and duplicate candidate
  pairs are suppressed and ops-logged, restart re-offers
  unacknowledged events and never re-creates them (fixture-proven at
  the detector level: a restarted pass over the same pool judges
  nothing and records nothing new).
- **§9 stale window** — NOT implemented in the detector: it is a
  monitor-stage concern (the ledger's config already carries
  `stale_interval_s`, "consumed by the monitor stage"). The detector
  holds only on judge errors/unavailability. Flagged as decision 6.
- **§10 dependencies** — reported in every packet; detection is NOT
  gated on them here (§10 gating is the scheduler's, Stage 4 — the
  ledger's `may_detect` docstring states the same split).
- **§11 judge transport** — hosted NVIDIA API, as ruled. Credentials
  are read at runtime and never logged or written into packets,
  the registry, the ledger, or logs (see decision 5).
- **§13 rows this stage owns** — fixture-covered: no match → judge
  never called; one qualifying turn → no wake; two consecutive YES →
  exactly one event; judge unavailable → no trigger, error recorded,
  streak retained; non-YES/NO → judge error, streak held, no NO
  recorded; unacknowledged event → no new event for that job;
  byte-identical repeat → distinct turn keys; dependency pending →
  reported pending (detection gating itself is Stage 4).

## Fixture results (2026-11-15, `./venv/bin/python`)

- `test_watchdog_detector.py` — **66 fixtures, 0 failed**, including
  an offline replay over the real recorded corpus
  `events/alex.jsonl`: the reader yields all **284 REPLY_CAPTURED**
  turns across 30 conversations; a drain loop (pass → acknowledge →
  pass, as the live loop would) judges every keyword-gated turn
  exactly once (128 gated turns, 128 stub calls, 0 errors), and
  every recorded event validates through the ledger.
- `test_guard.py` — 45/45. `test_watchdog_ledger.py` — 52/52.
  `test_waker_check.py` — 0 failures. All pre-existing suites green.

## Open design decisions — flagged for the reviewer

1. **Keyword gate's home (the known one).** The frozen job record
   (§3) has no keywords field, so the gate's word lists live in a
   detector-local config keyed by job_id (`KEYWORDS_BY_JOB` in
   `watchdog_detector.py`, overridable via detector config). A job
   with no entry has no gate — every seat turn is judged. If the
   gate belongs in the registry, that is a contract change (new
   job_id rules / v1.3), not a detector edit.
2. **Gate semantics.** A keyword-less turn is never judged, so under
   §6 (which speaks only of judged turns) it neither counts nor
   resets: two YES turns with a non-matching turn between them are
   consecutive for the streak. The alternative reading — every
   completed turn is judged and non-matches reset — contradicts
   §13's "no match → judge never called". Ruling requested.
3. **turn_index derivation.** Pool records carry no turn_index
   field; the reader derives the §1 ordinal as a 0-based count over
   the conversation's turns (seat replies AND user sends — the
   assignment message whose index the registry records is a user
   send) in capture order. If the pool later assigns its own
   indices, the reader should read them instead.
4. **ID-less turn keys.** Only 18 of the 284 corpus replies carry a
   message_id. For the rest, the turn_key is
   `noid:<sha256(content)[:16]>:<occurrence>` — §1's text-occurrence
   fallback made structural. Stable across replays of the same pool
   file; two ID-less turns with identical text get distinct keys.
5. **NVIDIA credential route.** The connector doc routes the key
   through the Secure Vault surrogate and says never to put a key
   in an environment variable; contract §11 says credentials are
   read from the environment at runtime. The client honours both:
   `NVIDIA_API_KEY` when present in the environment, otherwise the
   connector's surrogate path exactly as its own helper does it.
   Either way the credential is never logged or persisted.
6. **Stale window (§9) placement.** Not in the detector (see §9
   above). If the reviewer wants the detector to hold on stale
   watermarks, the pool reader needs a watermark source — the pool
   record's per-seat watermark (pool-state) is the candidate.
7. **Defensive branch: `pair_unknown`.** The detector fires in the
   same pass that brings the streak to 2 and tracks the pair's
   first turn (in-pass, or restored from the streak's
   `last_turn_key`). A persisted streak ≥ 2 with no recoverable
   first turn can only arise if another writer judged turns; the
   pass then reports `pair_unknown` instead of fabricating a
   packet. By design the detector is the only judge caller.
8. **Buffer slice form.** §5 does not fix the form of
   `relevant_buffer_slice`; packets carry structured entries
   (turn_index, turn_key, role, content) for the last
   `buffer_size` turns up to the firing turn. `buffer_size`
   defaults to 25 — §11 leaves the 20–30 value to the owner,
   as it does `alert_age`, `cooldown`, and `stale_interval`
   (ledger defaults stand until set).
