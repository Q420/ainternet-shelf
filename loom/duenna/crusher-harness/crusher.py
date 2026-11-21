#!/usr/bin/env python3
"""CRUSHER — the retrieval occupant (proof build, 2026-11-09).

Design: Ben's direction + Alex's CRUSHER-ADDRESSABILITY-PROOF-01.
- Occupant: Qwen (qwen/qwen3.8-27b via the custom.groq connector) —
  fast, light, fenced. STATELESS: no conversational memory is kept;
  the canonical corpus behind the index is the only memory.
- Job: retrieve relevant canonical sections, answer grounded in them,
  with provenance (source document, section identity, supporting text).
- Fences (Duenna role configuration, enforced by this harness):
  the occupant sees ONLY the question and the retrieved sections;
  it has no tools, no write path, and no transport authority.
  Absent evidence -> UNKNOWN. Conflicting evidence -> report the
  conflict. Fabrication of an answer or of provenance is a breach.
- Every question and answer is appended to crusher-log.jsonl.

Usage: crusher.py "question" [--requester remmy|alex|ben] [--k 4]
       crusher.py --usage [YYYY-MM-DD]   daily token accounting (UTC)

HARNESS v2.2 (2026-11-11) — the reporting fix, cleared by Alex
(pb-mwc4i085-9-bsdn) after CRUSHER-INFORMATION-AUDIT-01:
- Groq's complete HTTP error body is read and preserved; the
  provider's own wording is printed on failure (v1 never read it).
- The full returned usage block is logged on every success.
- Package ceiling PACKAGE_CAP_CHARS enforced BEFORE submission by
  deterministic section trimming (identity never removed; truncated
  content is labelled with shown/total chars, never as complete).
- Failed calls leave durable log records (attempts, status, body).
- BM25 retrieval scores are preserved alongside the sections.
- A running daily token total (provider accounting day, UTC —
  Groq resets at 00:00 UTC) is readable at any point and
  distinguishes known usage from unknown usage.
- NO automatic retry after a rate-limit refusal (HTTP 429):
  record the failure and stop. Bounded retries remain only for
  transient non-429 failures (the 2026-11-09 hardening).
- v2.2 correction (Alex's review of v2.1): retry maximum is TWO
  submissions total (initial + ONE retry) on both the 5xx and
  transport paths — v2/v2.1 permitted three.
- v2.1 correction (Alex's review of v2): EVERY failed attempt —
  including intermediate 5xx and transport failures on the retry
  path — leaves its own durable record (status, body, attempt
  number, timestamp), linked to the call's outcome by call_id,
  and counts separately as unknown usage in daily accounting.
The FENCE text below is byte-identical to v1. The v1 harness is
preserved at crusher_v1_archived.py.
"""
import argparse, datetime, json, pathlib, sys, time
import urllib.request, urllib.error

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from query import load, bm25_search  # noqa: E402
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

GROQ_HOST = "api.groq.com"
GROQ_URL = f"https://{GROQ_HOST}/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"
MAX_SECTION_CHARS = 2800
MIN_SECTION_CHARS = 400
PACKAGE_CAP_CHARS = 14000          # Ben's baseline, 2026-11-11 (Alex-cleared)
DAILY_TOKEN_CEILING = 200000       # Groq free plan, published (connector doc)
LOG_PATH = HERE / "crusher-log.jsonl"

FENCE = """You are Crusher, the retrieval officer of the Pulse Bridge.
Your only job: answer the question using ONLY the canonical sections
provided below, and show your evidence.

Rules, in order:
1. Answer solely from the provided sections. Cite the section id
   (for example d3-v07#054) for every fact you state, and include the
   supporting text you rely on, quoted exactly.
2. If the sections do not answer the question, reply exactly:
   UNKNOWN — the corpus does not say.
   Then, in one line, name the closest sections you were given.
3. If the sections conflict, report the conflict explicitly and cite
   both sides. Do not resolve a conflict by choosing silently.
4. Never invent an answer, a citation, or provenance. Never use
   knowledge from outside the provided sections.
5. You have no memory and no opinions. Treat this question as the
   only one that exists. Be brief and factual.
6. You hold no transport authority: you never confirm delivery of
   anything. You retrieve, ground, and answer — nothing else."""

# ---------------------------------------------------------------- transport
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call_groq(body: dict):
    """One submission. Returns (status, headers, payload) where payload
    is the parsed JSON dict on success, or the RAW response text on an
    HTTP error — the provider's complete error body, never discarded."""
    req = urllib.request.Request(
        GROQ_URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    # Groq's edge refuses the default client signature (connector doc).
    req.add_header("User-Agent", "Groq/Python 1.0 (Pulse HQ Crusher)")
    add_surrogate_to_request(req, "custom.groq", allowed_hosts=[GROQ_HOST])
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(req, timeout=120) as resp:
            return resp.status, dict(resp.headers), json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read().decode(errors="replace")

# ---------------------------------------------------------------- packages
def build_package(question: str, requester: str, hits):
    """Deterministically fit the package under PACKAGE_CAP_CHARS by
    shrinking the per-section text budget. Section identity is never
    removed; truncation is labelled with shown/total characters.
    Returns (body_dict, package_chars, section_budget)."""
    budget = MAX_SECTION_CHARS
    while True:
        blocks = []
        for _score, s in hits:
            text = s["text"]
            if len(text) > budget:
                text = (text[:budget] +
                        f"\n[section truncated for this answer: "
                        f"shown {budget} of {len(s['text'])} chars]")
            blocks.append(f"=== SECTION {s['section_id']} · doc {s['doc']} · "
                          f"{s['heading_path']} · sha256 {s['sha256'][:16]}… ===\n{text}")
        user = (f"Question (from {requester}): {question}\n\n"
                + "\n".join(blocks) if blocks else
                f"Question (from {requester}): {question}\n\n(no sections retrieved)")
        body = {"model": MODEL, "temperature": 0, "reasoning_format": "hidden",
                "messages": [{"role": "system", "content": FENCE},
                             {"role": "user", "content": user}]}
        size = len(json.dumps(body))
        if size <= PACKAGE_CAP_CHARS or budget <= MIN_SECTION_CHARS:
            return body, size, budget
        budget = max(MIN_SECTION_CHARS, int(budget * 0.7))

# ---------------------------------------------------------------- logging
def _now():
    return datetime.datetime.now(datetime.timezone.utc)

def _append(record: dict, log_path):
    with open(log_path, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def daily_usage(date_utc: str = None, log_path=LOG_PATH) -> dict:
    """Known vs unknown usage for one provider accounting day (UTC).
    Known: answered records carrying a provider usage block.
    Unknown: answered records without usage + failed/not-sent calls
    (failed requests may still consume quota; their token cost is
    not reported by the provider, so it is accounted as unknown)."""
    date_utc = date_utc or _now().date().isoformat()
    known_tokens, known_calls, unknown_calls = 0, 0, 0
    try:
        lines = open(log_path).read().splitlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        if not line.strip():
            continue
        r = json.loads(line)
        rdate = r.get("date_utc") or (r.get("ts", "")[:10] or None)
        if rdate != date_utc:
            continue
        usage = r.get("usage")
        outcome = r.get("outcome", "answered")
        if outcome == "answered" and isinstance(usage, dict):
            total = usage.get("total_tokens")
            if total is None:
                total = (usage.get("prompt_tokens", 0) +
                         usage.get("completion_tokens", 0))
            known_tokens += total
            known_calls += 1
        elif outcome == "attempt-failed":
            unknown_calls += 1  # each failed attempt: usage unknown
        elif outcome in ("failed", "not-sent") and r.get("call_id"):
            pass  # closing summary; its attempts are counted above
        else:
            unknown_calls += 1
    return {"date_utc": date_utc, "known_tokens": known_tokens,
            "known_calls": known_calls, "unknown_calls": unknown_calls,
            "daily_ceiling_tokens": DAILY_TOKEN_CEILING}

# ---------------------------------------------------------------- ask
def ask(question: str, requester: str, k: int = 4, transport=None,
        log_path=LOG_PATH, secs=None) -> dict:
    import uuid
    transport = transport or call_groq
    call_id = uuid.uuid4().hex[:12]
    if secs is None:
        secs, _man = load()
    hits = bm25_search(secs, question, k)
    section_ids = [s["section_id"] for _sc, s in hits]
    scores = [round(sc, 4) for sc, _s in hits]
    body, package_chars, budget = build_package(question, requester, hits)
    base = {"ts": _now().isoformat(), "date_utc": _now().date().isoformat(),
            "call_id": call_id,
            "requester": requester, "question": question,
            "sections": section_ids, "scores": scores,
            "package_chars": package_chars, "section_budget_chars": budget}
    if package_chars > PACKAGE_CAP_CHARS:
        rec = {**base, "outcome": "not-sent",
               "reason": f"package {package_chars} chars exceeds cap "
                         f"{PACKAGE_CAP_CHARS} even at minimum section budget"}
        _append(rec, log_path)
        raise RuntimeError(rec["reason"])
    attempts = 0
    while True:
        attempts += 1
        try:
            status, headers, payload = transport(body)
        except Exception as e:  # transport-level failure (no HTTP status)
            _append({**base, "ts": _now().isoformat(),
                     "outcome": "attempt-failed", "attempt": attempts,
                     "http_status": None, "error_kind": type(e).__name__,
                     "error_body": str(e)}, log_path)
            if attempts < 2:
                time.sleep(15 * attempts)
                continue
            rec = {**base, "outcome": "failed", "attempts": attempts,
                   "http_status": None, "error_kind": type(e).__name__,
                   "error_body": str(e)}
            _append(rec, log_path)
            raise RuntimeError(f"transport failed after {attempts} attempts: {e}")
        if status == 200 and isinstance(payload, dict):
            answer = payload["choices"][0]["message"]["content"].strip()
            rec = {**base, "outcome": "answered", "attempts": attempts,
                   "usage": payload.get("usage"), "answer": answer}
            _append(rec, log_path)
            return rec
        # HTTP failure. A rate-limit refusal is NEVER retried (Alex, F4):
        # record and stop. Other 4xx are deterministic — no retry either.
        # 5xx keeps the bounded transient retry from the 2026-11-09 proof.
        error_body = payload if isinstance(payload, str) else json.dumps(payload)
        _append({**base, "ts": _now().isoformat(),
                 "outcome": "attempt-failed", "attempt": attempts,
                 "http_status": status,
                 "retry_after": headers.get("Retry-After") or headers.get("retry-after"),
                 "error_body": error_body}, log_path)
        if status == 429 or 400 <= status < 500 or attempts >= 2:
            rec = {**base, "outcome": "failed", "attempts": attempts,
                   "http_status": status,
                   "retry_after": headers.get("Retry-After") or headers.get("retry-after"),
                   "error_body": error_body}
            _append(rec, log_path)
            raise RuntimeError(f"groq HTTP {status} after {attempts} attempt(s). "
                               f"Provider error body:\n{error_body}")
        time.sleep(15 * attempts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--requester", default="remmy")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--usage", nargs="?", const="", default=None,
                    help="print daily token accounting (UTC date optional)")
    a = ap.parse_args()
    if a.usage is not None:
        u = daily_usage(a.usage or None)
        print(f"Crusher usage — provider accounting day {u['date_utc']} (UTC, "
              f"resets 00:00 UTC)")
        print(f"  known:   {u['known_tokens']} tokens across {u['known_calls']} "
              f"answered calls")
        print(f"  unknown: {u['unknown_calls']} calls without provider usage "
              f"(pre-fix history, failures, not-sent)")
        print(f"  ceiling: {u['daily_ceiling_tokens']} tokens/day (published "
              f"free plan)")
        return
    if not a.question:
        ap.error("a question is required (or use --usage)")
    rec = ask(a.question, a.requester, a.k)
    print(f"CRUSHER ANSWER (requester: {rec['requester']}; "
          f"sections: {', '.join(rec['sections']) or 'none'}; "
          f"package: {rec['package_chars']} chars)\n")
    print(rec["answer"])
    u = daily_usage(rec["date_utc"])
    print(f"\n[daily usage {u['date_utc']}: {u['known_tokens']} known tokens "
          f"+ {u['unknown_calls']} unknown-usage calls of "
          f"{u['daily_ceiling_tokens']} ceiling]")

if __name__ == "__main__":
    main()
