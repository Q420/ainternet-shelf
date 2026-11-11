# CRUSHER — INFORMATION AUDIT 01 (2026-11-11)

**Commissioned by Ben:** "audit all information he actually
receives and what he has the tools to use." Subject: Crusher —
Qwen (qwen/qwen3.8-27b via Groq) behind crusher.py. Method:
source inspection of crusher.py, query.py, groq_api.py,
interim_ask.py, groq_batched.py, and crusher-log.jsonl.
No live calls were made for this audit.

## 1. What the occupant RECEIVES (per call)

- The FENCE as system instruction (crusher.py): role, six
  rules, no other doctrine.
- One user block: "Question (from <requester>): <question>"
  plus up to k section blocks (default k=4; k=6 in recent
  rounds). Each block carries: section_id, doc name,
  heading_path, the first 16 characters of the section's
  sha256, and the section text truncated at 2,800 chars
  with an in-band truncation note.
- Parameters: temperature 0, reasoning_format "hidden".
- The requester label is ASSERTED by the caller. Nothing
  authenticates it — seat identity here is procedural,
  not enforced.

## 2. What the occupant NEVER receives

- The other ~1,150 sections of the 1,156-section corpus.
  It sees only BM25's top-k, chosen by a lexical ranking
  whose SCORES are computed and then discarded — the
  occupant cannot tell a strong match from a weak one.
- Full hashes (16 of 64 chars), chain_sha256, seq, char
  counts, the manifest, corpus totals — all exist in the
  record; none are passed.
- Its own history: stateless by design. No prior question,
  no prior answer, no spend total, no sense of the day.
- Any tool, file, or second look. If the top-k is wrong,
  its only lawful move is UNKNOWN (fence rule 2). The
  repeated "retrieval misses" of 2026-11-11 were therefore
  structural: BM25 chose; the occupant answered for
  sections it never saw.

## 3. What comes BACK — kept vs discarded

groq_api.py returns Groq's full JSON response. crusher.py
keeps exactly one field: choices[0].message.content.

DISCARDED on every call:
- **usage** — prompt_tokens, completion_tokens,
  total_tokens. Groq reports the exact price of every
  package; the harness throws it away. No component
  anywhere totals the day's spend against the 200,000
  token purse.
- finish_reason, the response's model echo, id, and any
  rate-limit headers on success.
- On FAILURE, Groq's error body — the one text that names
  the limit type and the wait — is never read at all:
  urllib raises HTTPError, the body stays inside the
  exception object, and crusher keeps only the last 600
  characters of stderr, which is traceback boilerplate
  plus the status line. ("Truncated" was generous; the
  body is unread, not shortened.)

## 4. Failure behaviour (observed cost)

- crusher.py retries a failed call twice more with the
  IDENTICAL full body (backoff 15s/30s). Under the daily
  amount limit each failure costs three full packages,
  and failed requests also count against the 1,000/day
  request quota.
- FAILED CALLS LEAVE NO LOG RECORD. crusher-log.jsonl is
  written only after a successful answer. The log holds
  118 Qwen exchanges and zero failures — every 429 of
  2026-11-11 is invisible in the system's own record and
  exists only in chat. The record is survivorship-shaped.

## 5. Tools within reach that the answer path does not use

- query.py verify (full hash-chain recomputation) —
  never called by crusher; the corpus is trusted per call
  on the strength of past admission checks.
- query.py show (exact section lookup) — the reliable
  route Remmy uses by hand; unavailable to the occupant,
  which cannot request a section it suspects exists.
- groq_api.py models — never consulted in the answer path.
- interim_ask.py (Gemini) repeats the pattern: it keeps
  the answer text and discards Gemini's usageMetadata.
  (Remmy's script; the discard is hers too.)
- groq_batched.py (Ben's direction) adds body-size logging
  and single-attempt discipline — evidence the fixes work;
  it is a side script, not the harness.

## 6. Findings

- F1. The occupant's blindness is structural, not a model
  fault: top-k lexical selection, scores discarded, no
  second look. UNKNOWN from Crusher means "not in the
  top-k shown", never "not in the corpus" — tonight's
  decision-evidence Q1 miss is the standing example.
- F2. The provider reports price and limits on every call;
  the harness discards both. "He should report" (Ben) is
  implementable from data already received.
- F3. The log records successes only; failures, attempts,
  sizes and usage are absent, so the system's own record
  cannot reconstruct a night like this one.
- F4. Retry-identical under an amount limit converts one
  refusal into three charges.
- F5. Seat identity in the question label is asserted,
  not verified — procedural only, per the gate ledger's
  labels-are-facts rule.

**Relation to the pending fix (Ben's card, untapped):**
the card already covers full error bodies, usage logging
and the ~14,000-char package cap. This audit ADDS, for
Ben's word before any widening: log failures and attempt
counts; record retrieval scores with each answer; keep a
running daily token total so the purse is visible before
it is empty.
