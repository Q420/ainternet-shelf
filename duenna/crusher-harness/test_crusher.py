#!/usr/bin/env python3
"""Acceptance tests for the Crusher harness v2 reporting fix.
NO LIVE GROQ CALLS: every test injects a fake transport.
Cleared scope: Alex, pb-mwc4i085-9-bsdn (2026-11-11).
Run: python3 test_crusher.py  (exit 0 = all pass)
"""
import json, pathlib, sys, tempfile, time

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import crusher  # noqa: E402

crusher.time.sleep = lambda s: None  # no real backoff in tests

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))

def read_log(path):
    return [json.loads(l) for l in open(path) if l.strip()]

LIMIT_BODY = json.dumps({"error": {
    "message": "Rate limit reached for model qwen/qwen3.8-27b on tokens "
               "per day (TPD): Limit 200000, Used 200000, Requested 4500. "
               "Please try again in 3600s.",
    "type": "tokens", "code": "rate_limit_exceeded"}})

def fake_429(calls):
    def t(body):
        calls.append(len(json.dumps(body)))
        return 429, {"Retry-After": "3600"}, LIMIT_BODY
    return t

def fake_success(calls, usage=None):
    def t(body):
        calls.append(len(json.dumps(body)))
        return 200, {}, {"choices": [{"message": {"content":
            "UNKNOWN — the corpus does not say."}}],
            "usage": usage or {"prompt_tokens": 1000, "completion_tokens": 50,
                               "total_tokens": 1050}}
    return t

def fake_503_then_success(calls):
    state = {"n": 0}
    def t(body):
        calls.append(len(json.dumps(body)))
        state["n"] += 1
        if state["n"] == 1:
            return 503, {}, json.dumps({"error": {"message": "overloaded"}})
        return 200, {}, {"choices": [{"message": {"content": "ok"}}],
                         "usage": {"prompt_tokens": 10, "completion_tokens": 2,
                                   "total_tokens": 12}}
    return t

Q = "The current ledger, generation, dependency and synchronisation artefacts, if any."

with tempfile.TemporaryDirectory() as td:
    log = pathlib.Path(td) / "log.jsonl"

    # T1 — forced 429: full provider body exposed, ONE submission, durable record
    calls = []
    try:
        crusher.ask(Q, "alex", 6, transport=fake_429(calls), log_path=log)
        raised = ""
    except RuntimeError as e:
        raised = str(e)
    recs = read_log(log)
    check("T1a 429 body preserved verbatim in the raised error",
          "tokens per day (TPD)" in raised and "try again in 3600s" in raised)
    check("T1b 429 not retried (exactly one submission)", len(calls) == 1,
          f"submissions={len(calls)}")
    check("T1c failed call leaves durable records (attempt + closing)",
          len(recs) == 2 and recs[0]["outcome"] == "attempt-failed"
          and recs[1]["outcome"] == "failed")
    check("T1d records carry attempts + status + body + retry-after + call_id",
          recs[0]["attempt"] == 1 and recs[0]["http_status"] == 429
          and "tokens per day" in recs[0]["error_body"]
          and recs[0]["retry_after"] == "3600"
          and recs[1]["attempts"] == 1
          and recs[0]["call_id"] == recs[1]["call_id"])

    # T2 — success: full usage block recorded; scores survive; package size recorded
    log.unlink()
    calls = []
    rec = crusher.ask(Q, "alex", 6, transport=fake_success(calls), log_path=log)
    recs = read_log(log)
    check("T2a success records the full usage block",
          recs[0]["usage"] == {"prompt_tokens": 1000, "completion_tokens": 50,
                               "total_tokens": 1050})
    check("T2b retrieval scores survive into the record",
          len(recs[0]["scores"]) == len(recs[0]["sections"])
          and all(isinstance(x, float) for x in recs[0]["scores"]))
    check("T2c package size recorded and within the cap",
          0 < recs[0]["package_chars"] <= crusher.PACKAGE_CAP_CHARS,
          f"package_chars={recs[0]['package_chars']}")

    # T3 — daily total reconciles; known vs unknown distinguished
    with open(log, "a") as f:  # one legacy answered record without usage, same day
        f.write(json.dumps({"ts": rec["ts"], "date_utc": rec["date_utc"],
                            "requester": "remmy", "question": "legacy",
                            "sections": [], "answer": "old"}) + "\n")
    u = crusher.daily_usage(rec["date_utc"], log_path=log)
    check("T3a daily total reconciles with usage records",
          u["known_tokens"] == 1050 and u["known_calls"] == 1)
    check("T3b unknown usage counted separately",
          u["unknown_calls"] == 1, f"unknown={u['unknown_calls']}")
    check("T3c accounting date + ceiling identified",
          u["date_utc"] == rec["date_utc"] and u["daily_ceiling_tokens"] == 200000)

    # T4 — oversize package trimmed before submission; identities intact
    log.unlink()
    big = [{"section_id": f"synthetic#{i:03d}", "doc": "synthetic",
            "heading_path": "h", "sha256": "a" * 64,
            "embed_text": "ledger generation dependency pool " * 40,
            "text": "ledger generation dependency pool evidence " * 300}
           for i in range(6)]
    calls = []
    rec = crusher.ask("ledger generation dependency pool", "alex", 6,
                      transport=fake_success(calls), log_path=log, secs=big)
    check("T4a oversize package trimmed to the cap before submission",
          calls and calls[0] <= crusher.PACKAGE_CAP_CHARS,
          f"submitted={calls[0] if calls else None} cap={crusher.PACKAGE_CAP_CHARS}")
    check("T4b all section identities preserved under trimming",
          rec["sections"] == [s["section_id"] for s in big])
    check("T4c resulting package size recorded",
          rec["package_chars"] == calls[0])

    # T5 — transient 5xx: intermediate failure recorded + linked + accounted
    log.unlink()
    calls = []
    rec = crusher.ask(Q, "alex", 3, transport=fake_503_then_success(calls),
                      log_path=log)
    recs = read_log(log)
    fails = [r for r in recs if r["outcome"] == "attempt-failed"]
    oks = [r for r in recs if r["outcome"] == "answered"]
    check("T5a 5xx retried once then answered (attempts=2)",
          rec["outcome"] == "answered" and rec["attempts"] == 2
          and len(calls) == 2)
    check("T5b intermediate failure has its own durable record",
          len(fails) == 1 and fails[0]["http_status"] == 503
          and fails[0]["attempt"] == 1 and "overloaded" in fails[0]["error_body"])
    check("T5c attempt + success linked by a stable call_id",
          len(oks) == 1 and fails[0]["call_id"] == oks[0]["call_id"] == rec["call_id"])
    u = crusher.daily_usage(rec["date_utc"], log_path=log)
    check("T5d failed attempt counted in unknown usage",
          u["unknown_calls"] == 1 and u["known_calls"] == 1
          and u["known_tokens"] == 12,
          f"unknown={u['unknown_calls']} known_tokens={u['known_tokens']}")

    # T6 — transport exception then success: same per-attempt discipline
    log.unlink()
    state = {"n": 0}
    def flaky(body):
        state["n"] += 1
        if state["n"] == 1:
            raise ConnectionError("connection reset by peer")
        return 200, {}, {"choices": [{"message": {"content": "ok"}}],
                         "usage": {"prompt_tokens": 5, "completion_tokens": 1,
                                   "total_tokens": 6}}
    rec = crusher.ask(Q, "alex", 3, transport=flaky, log_path=log)
    recs = read_log(log)
    fails = [r for r in recs if r["outcome"] == "attempt-failed"]
    check("T6 transport failure recorded, linked, then answered",
          rec["outcome"] == "answered" and len(fails) == 1
          and fails[0]["error_kind"] == "ConnectionError"
          and "connection reset" in fails[0]["error_body"]
          and fails[0]["call_id"] == rec["call_id"])


    # T7 — two consecutive 5xx: max two submissions, both attempts logged
    log.unlink()
    calls = []
    def always_503(body):
        calls.append(1)
        return 503, {}, json.dumps({"error": {"message": "overloaded"}})
    try:
        crusher.ask(Q, "alex", 3, transport=always_503, log_path=log)
        raised = ""
    except RuntimeError as e:
        raised = str(e)
    recs = read_log(log)
    fails = [r for r in recs if r["outcome"] == "attempt-failed"]
    closing = [r for r in recs if r["outcome"] == "failed"]
    check("T7a two 5xx submissions maximum", len(calls) == 2,
          f"submissions={len(calls)}")
    check("T7b both attempts + closing logged, one call_id",
          len(fails) == 2 and len(closing) == 1
          and len({r["call_id"] for r in recs}) == 1
          and closing[0]["attempts"] == 2
          and [f["attempt"] for f in fails] == [1, 2])
    u = crusher.daily_usage(fails[0]["date_utc"], log_path=log)
    check("T7c unknown usage counts both attempts, closing not recounted",
          u["unknown_calls"] == 2 and u["known_tokens"] == 0,
          f"unknown={u['unknown_calls']}")

    # T8 — two consecutive transport failures: same discipline
    log.unlink()
    calls = []
    def always_down(body):
        calls.append(1)
        raise ConnectionError("connection reset by peer")
    try:
        crusher.ask(Q, "alex", 3, transport=always_down, log_path=log)
    except RuntimeError:
        pass
    recs = read_log(log)
    fails = [r for r in recs if r["outcome"] == "attempt-failed"]
    closing = [r for r in recs if r["outcome"] == "failed"]
    check("T8a two transport submissions maximum", len(calls) == 2)
    check("T8b both attempts + closing logged, one call_id",
          len(fails) == 2 and len(closing) == 1
          and len({r["call_id"] for r in recs}) == 1
          and all(f["error_kind"] == "ConnectionError" for f in fails))
    u = crusher.daily_usage(fails[0]["date_utc"], log_path=log)
    check("T8c unknown usage counts both transport attempts",
          u["unknown_calls"] == 2, f"unknown={u['unknown_calls']}")

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
sys.exit(1 if FAIL else 0)
