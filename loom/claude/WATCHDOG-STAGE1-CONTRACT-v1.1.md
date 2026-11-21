# Watchdog — Stage 1 Contract (FROZEN v1.1, 2026-11-15)

Status: frozen on adjudicator rulings and owner taps. Changes require a new
contract version and a new tapped card. No stage may depend on a field or
rule not stated here.

## 0. Principles (settled design, restated)
- The watchdog NOTICES. It never sends to a seat. It has no seat-send capability.
- The orchestrator alone composes and sends every seat message.
- Only marked assignments are judged. Unmarked conversation is never read for a trigger.
- Judge models see event packets only. They never see pages.
- A wake never fires twice for the same event; an unacknowledged wake is retained, never dropped.

## 1. Turn identity (prerequisite, built and proven)
A turn is identified structurally: `(seat_id, conversation_id, message_id)`.
- `message_id` is the page's own id (the data-response-body value).
- Text hash is NOT an identity. Byte-identical replies from one seat are distinct turns.
- Text-occurrence matching applies only to turns with no message_id, as a fallback.
- `turn_index` = the seat's pool-assigned ordinal over completed turns in the conversation (monotonic, assigned at capture, never reused).

## 2. Registry
- One registry file; the watchdog reads it, the orchestrator writes it.
- Key: `job_id`. Form: a short unique identifier; the job id appears in the marker.
- Validated at load. Load fails (no job starts) if any of these hold:
  a. a `depends_on` reference names an unknown job;
  b. the dependency graph has a cycle (rejected, not warned);
  c. two jobs share a `job_id`;
  d. a job names a seat not in the v1 seat set (ChatGPT, this seat).
- **Immutable once active.** A job becomes active when its assignment is sent. An active job's record is never edited. A changed precondition is a new `job_id`.
- The registry records the assignment's `assigned_turn_index` (the seat's turn index of the assignment message, filled on confirmation of the send).

## 3. Job record (static, in registry)
| field | type | rule |
|---|---|---|
| job_id | string | unique; in the marker |
| seat_id | string | v1: `chatgpt`, `this-seat` |
| conversation_id | string | the window the job lives in |
| task | string | orchestrator's description |
| declared_precondition | string | the exact question the judge answers YES/NO |
| depends_on | [job_id] | may be empty |
| priority | int | lower = earlier; ties broken by job_id |
| assigned_turn_index | int | set once, at assignment confirmation |
| state | enum | `active`, `resolved`, `retired` |

Precondition text is fixed when the job is active (see §2).

## 4. Assignment marker
- Form: `⟦WD:<job_id>⟧`, one line, in the assignment message the orchestrator sends.
- Verified: composer insertText and verified-post preserve it verbatim (TEST-1).
- The watchdog trusts the marker only as the registration of a job in the registry. Matching a reply to a job comes from the registry entry (seat, window, assigned_turn_index), not from the seat echoing the marker.

## 5. Event packet (per trigger)
| field | rule |
|---|---|
| schema_version | `1` |
| event_id | unique; generated at detection |
| ledger_key | `job_id + "|" + seat_id + "|" + conversation_id + "|" + turn_key` where turn_key is the structural turn identity of the FIRST qualifying turn (§1) |
| job_id, seat_id, window_id | as registry |
| declared_precondition | copied from the job record |
| trigger_reason | `two_consecutive_yes` |
| candidate_turn_ids | structural ids of the two qualifying turns |
| turn_index_range | [first, last] turn_index of the qualifying pair |
| judge_results | per turn: `YES` or `NO` (errors never appear here as a result) |
| judge_model | configured model name |
| judge_prompt_hash | hash of the exact judge prompt template |
| buffer_window_bounds | [first, last] turn_index visible to the judge |
| relevant_buffer_slice | the 20–30 turn buffer slice; job description referenced by job_id, not repeated |
| dependency_state | per upstream job: `resolved` or `pending` |
| detected_at | ISO-8601 with offset |
| priority | copied from job record |

Packets are immutable once written.

## 6. Streak and debounce (ruling 1a, refined)
- The streak counts **completed turns that reached the pool**, for one job, in one seat conversation.
- **Counts:** a completed turn that the judge answered YES. **Resets:** a completed turn the judge answered NO.
- **Holds (neither advances nor resets):** a judge error; a stale window (§9); a turn still generating or not yet in the pool.
- User turns neither count nor reset.
- A fire requires two consecutive counted YES turns. The streak is persisted (survives restart).

## 7. Judge output (strict)
- The judge returns exactly `YES` or `NO`, after normalization of surrounding whitespace only.
- Any other output is a **judge error**: logged, the streak holds, no result is recorded as NO.
- The judge is never shown instructions from seat text as instructions. Its prompt is a fixed template; seat content is quoted data.

## 8. Ledger and acknowledgement (ruling 1b, refined)
- Ledger is durable. Writes are atomic: temp file, fsync, rename.
- Each event is recorded once, keyed by `ledger_key`. A second detection with the same ledger_key is not written and is logged as `duplicate_suppressed`.
- **Acknowledgement lock:** while a job has an event in state `unacknowledged`, no new event may be created for that job.
- **Cooldown** starts at acknowledgement, not detection. Cooldown gates only new detections after acknowledgement, for a per-job interval set in configuration.
- An `unacknowledged` event older than the configured alert age raises an operational alert. It is never dropped.
- Restart: on start, the ledger is read; `unacknowledged` events are re-offered to the orchestrator; no event is re-created.

## 9. Stale window (ruling 1c)
- A window is **stale** when the seat's pool watermark has not advanced within a configured interval while the window is known to be open.
- A stale window raises an operational alert and HOLDS the streak. It never produces a trigger and never counts as NO.
- Stale-window alerts are not events and do not enter the ledger.

## 10. Dependencies (scheduler, Stage 5)
- A dependency is **resolved** when the upstream job's event has been acknowledged. Not when the upstream precondition is merely true.
- Downstream jobs are held (no detection) until every `depends_on` job is resolved.
- Ordering across windows is upstream-first by priority, ties by job_id.

## 11. Configuration decisions (owner)
- **Judge transport: SETTLED by owner ruling (2026-11-15). The judge runs on the hosted NVIDIA API.** There is no local model, and none is to be designed for.
- Seat conversation content in event packets may be sent to that API. This is an accepted data flow, not an open question.
- Credentials are read from the environment at runtime. They are never written into packets, the registry, the ledger, or logs.
- Stage 3 live wiring is no longer blocked by this item. It remains subject to the owner tap on the Stage 3 card and to the acceptance table (§13).
- `alert_age`, `cooldown`, `stale_interval`, buffer size (20–30): configuration, with defaults set by the owner.

## 12. Stage order (frozen)
(Ruling 2026-11-15: judge transport is settled as hosted; see §11.)
1. **Contract** (this document) + pool reader as the monitor (replaces Stage 2 as a separate stage).
2. **Ledger** (Stage 4), before any live wake exists.
3. **Detector + judge**, offline against recorded pool data first; live wiring gated by §11.
4. **Scheduler** (Stage 5).
5. **Wake integration** (Stage 6), starting with the existing event-file pattern.
6. **Acceptance** (Stage 7).

## 13. Acceptance table (Stage 7, must all pass before live use)
| case | expected |
|---|---|
| no match | judge never called |
| one qualifying turn | no wake |
| two consecutive YES | exactly one wake |
| same event after restart | no second wake (ledger) |
| judge unavailable | no trigger; error recorded; streak retained |
| judge returns non-YES/NO | judge error; streak held; no NO recorded |
| stale window | operational alert; no trigger; streak held |
| unacknowledged event | no new event for that job; alert past alert_age |
| byte-identical repeat from one seat | distinct turns by message_id; two distinct turn keys |
| cycle in registry | load fails |
| dependency pending | downstream not detected |

## 14. Out of scope for v1
- API seats; any seat other than `chatgpt` and `this-seat`.
- Any watchdog-initiated send.
- Page observers of its own (the pool is the only source).
