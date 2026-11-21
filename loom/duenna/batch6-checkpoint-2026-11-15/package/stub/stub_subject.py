#!/usr/bin/env python3
"""Scripted stub subject for Batch 6 scratch runs (approved sheet C6-5).

The stub sits behind the adapter's harness-facing boundary: the real
Batch 5 adapter (pinned F-2 configuration) calls it over loopback HTTP,
so every stub invocation routes through the adapter's real
ADAPTER-CAPTURE-02 capture writer. The stub serves under its own visible
identity, STUB-SUBJECT-01 — never the pinned Nemotron model id.

Scripted per (tree, step, attempt) from a pinned JSON script whose
"calls" reuse the Batch 3 stub script's format. Kinds:
  output      well-formed 200 completion carrying raw_output
  refusal     200 completion whose content is refusal-shaped
  truncation  200 completion, finish_reason "length", content cut short
  malformed   200 with a non-JSON body (the adapter classifies it)
  http_error  the scripted HTTP status with a raw error body
              (429/5xx are retryable under the F-2 retry policy, which
              is how multi-attempt retry captures are produced)

The harness identifies the step under test with a leading message whose
content is "PILOT-TASK tree=<tree_id> step=<step_id>".
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STUB_MODEL_ID = "STUB-SUBJECT-01"


def _ok_body(content, finish="stop"):
    return json.dumps({
        "id": "chatcmpl-stub-1",
        "object": "chat.completion",
        "created": 1794700000,
        "model": STUB_MODEL_ID,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": finish,
        }],
        "usage": {"prompt_tokens": 11, "completion_tokens": 7,
                  "total_tokens": 18},
    }).encode("utf-8")


class StubScript:
    def __init__(self, path):
        doc = json.loads(Path(path).read_text())
        self.calls = doc.get("calls", {})
        self.default = doc.get("default", {"kind": "output", "raw_output": ""})
        self._counts = {}
        self._lock = threading.Lock()

    def next_entry(self, tree_id, step_id):
        with self._lock:
            key = (tree_id, step_id)
            n = self._counts.get(key, 0) + 1
            self._counts[key] = n
        return self.calls.get(f"{tree_id}|{step_id}|{n}", self.default), n


def _task_identity(messages):
    for m in messages or []:
        c = m.get("content") or ""
        if isinstance(c, str) and c.startswith("PILOT-TASK "):
            kv = dict(part.split("=", 1) for part in c.split()[1:]
                      if "=" in part)
            return kv.get("tree"), kv.get("step")
    return None, None


def make_server(script_path, host="127.0.0.1", port=0):
    script = StubScript(script_path)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                body = {}
            tree, step = _task_identity(body.get("messages"))
            entry, _n = script.next_entry(tree, step)
            kind = entry.get("kind", "output")
            if kind == "http_error":
                status = int(entry.get("http_status", 500))
                payload = str(entry.get("raw_output", "stub http error")).encode("utf-8")
            elif kind == "malformed":
                status = 200
                payload = str(entry.get("raw_output", "not json")).encode("utf-8")
            elif kind == "truncation":
                status = 200
                payload = _ok_body(str(entry.get("raw_output", "")), finish="length")
            else:  # output, refusal
                status = 200
                payload = _ok_body(str(entry.get("raw_output", "")))
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


class StubAdapter:
    """The stub subject on the harness side of the complete() contract.

    Mirrors the Batch 5 adapter's contract exactly — closed step_inputs
    keys, the F-2-shaped wire envelope, the retry policy, and the
    ADAPTER-CAPTURE-02 capture record (same 30 fields, same canonical
    write, same record_sha256 construction) — with the subject identity
    replaced by the stub's own. Scripted transport outcomes come from
    the pinned stub script; no network is touched.
    """

    def __init__(self, config_path, script_path, captures_dir):
        self.cfg = load_stub_config(config_path)
        import hashlib as _h
        import pilot_jcs as _jcs
        # the stub run configuration's own pin: the JCS-canonical hash of
        # the loaded configuration (verifiable from the config file)
        self._config_sha = _h.sha256(_jcs.canonicalise(self.cfg)).hexdigest()
        self.script = StubScript(script_path)
        self.captures_dir = Path(captures_dir)
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        self.envelope = self.cfg["envelope"]
        self.retry = self.cfg["retry_policy"]
        self.model = STUB_MODEL_ID
        import uuid as _uuid
        self._uuid = _uuid

    def _attempt(self, entry):
        kind = entry.get("kind", "output")
        if kind == "http_error":
            status = int(entry.get("http_status", 500))
            return status, str(entry.get("raw_output", "stub http error")), "HTTP_ERROR"
        if kind == "malformed":
            return 200, str(entry.get("raw_output", "not json")), "RESPONSE_RECEIVED"
        if kind == "truncation":
            return 200, _ok_body(str(entry.get("raw_output", "")), finish="length").decode("utf-8"), "RESPONSE_RECEIVED"
        return 200, _ok_body(str(entry.get("raw_output", ""))).decode("utf-8"), "RESPONSE_RECEIVED"

    def complete(self, step_inputs):
        import hashlib
        import pilot_jcs as _jcs
        keys = set(step_inputs.keys())
        if keys != {"correlation_id", "tree_id", "step_id", "messages"}:
            raise ValueError(
                "step_inputs must carry exactly correlation_id, "
                f"tree_id, step_id, messages; got {sorted(keys)}")
        env = self.envelope
        body_obj = {
            "model": self.model,
            "messages": step_inputs["messages"],
            "temperature": env["temperature"],
            "top_p": env["top_p"],
            "max_tokens": env["max_tokens"],
            "stream": env["stream"],
            "chat_template_kwargs": env["chat_template_kwargs"],
        }
        body_bytes = json.dumps(body_obj, separators=(",", ":"),
                                ensure_ascii=False).encode("utf-8")
        request_sha = hashlib.sha256(body_bytes).hexdigest()
        envelope_echo = {
            "model": env["model"],
            "temperature": env["temperature"],
            "top_p": env["top_p"],
            "max_tokens": env["max_tokens"],
            "stream": env["stream"],
            "chat_template_kwargs": env["chat_template_kwargs"],
        }
        max_attempts = int(self.retry["max_attempts"])
        attempts = []
        final = None
        for n in range(1, max_attempts + 1):
            entry, _ = self.script.next_entry(step_inputs["tree_id"],
                                              step_inputs["step_id"])
            status, body_text, outcome = self._attempt(entry)
            attempts.append({
                "attempt_no": n,
                "sent_at_utc": "2026-11-15T00:00:00Z",
                "received_at_utc": "2026-11-15T00:00:00Z",
                "http_status": status,
                "response_body_raw": body_text,
                "response_body_sha256": hashlib.sha256(body_text.encode("utf-8")).hexdigest(),
                "error_class": None if outcome == "RESPONSE_RECEIVED" else outcome,
                "error_detail": None,
            })
            final = (status, body_text, outcome)
            if n == max_attempts:
                break
            retryable = (status == 429 or (status is not None and 500 <= status <= 599)
                         or outcome in ("TIMEOUT", "TRANSPORT_ERROR"))
            if not retryable:
                break
        status, final_body_text, outcome = final
        failure_class = None
        failure_detail = None
        raw_output = None
        served_id = None
        finish_reason = None
        usage = None
        parsed = None
        if final_body_text is not None:
            try:
                parsed = json.loads(final_body_text)
            except (ValueError, TypeError):
                parsed = None
        if outcome == "RESPONSE_RECEIVED" and parsed is not None:
            served_id = parsed.get("model")
            try:
                choice = parsed["choices"][0]
                finish_reason = choice.get("finish_reason")
                content = choice["message"]["content"]
            except (KeyError, IndexError, TypeError):
                content = None
            usage = parsed.get("usage")
            if served_id is not None and served_id != self.model:
                failure_class = "ADAPTER_FAILURE"
                failure_detail = (f"served model id {served_id!r} != stub "
                                  f"identity {self.model!r}")
            else:
                raw_output = content
        elif outcome == "HTTP_ERROR":
            failure_class = "ADAPTER_FAILURE"
            failure_detail = f"HTTP {status}"
        capture_id = str(self._uuid.uuid4())
        record = {
            "schema": "ADAPTER-CAPTURE-02",
            "schema_version": "02",
            "capture_id": capture_id,
            "correlation_id": step_inputs["correlation_id"],
            "tree_id": step_inputs["tree_id"],
            "step_id": step_inputs["step_id"],
            "adapter_id": "STUB-ADAPTER-01 (Batch 6 scripted stub subject)",
            "adapter_config_sha256": self._config_sha,
            "endpoint": "stub://in-process (no network)",
            "subject_model_id_pinned": self.model,
            "subject_pin_catalogue_sha256": self.cfg["stub_script_sha256"],
            "subject_pin_captured_date": "2026-11-15",
            "request_envelope": envelope_echo,
            "request_raw": body_bytes.decode("utf-8"),
            "request_sha256": request_sha,
            "request_sent_at_utc": "2026-11-15T00:00:00Z",
            "response_raw": final_body_text,
            "response_sha256": hashlib.sha256(final_body_text.encode("utf-8")).hexdigest() if final_body_text is not None else None,
            "response_http_status": status,
            "response_model_id_served": served_id,
            "response_finish_reason": finish_reason,
            "response_usage": usage,
            "response_latency_ms": 0,
            "response_received_at_utc": "2026-11-15T00:00:00Z",
            "recorded_at_utc": "2026-11-15T00:00:00Z",
            "attempts": attempts,
            "transport_outcome": outcome,
            "failure_class": failure_class,
            "failure_detail": failure_detail,
        }
        record["record_sha256"] = hashlib.sha256(_jcs.canonicalise(record)).hexdigest()
        path = self.captures_dir / (capture_id + ".json")
        with open(path, "xb") as f:
            f.write(_jcs.canonicalise(record))
        return {"capture_record_id": capture_id, "raw_output": raw_output}


def load_stub_config(path):
    """The scratch-only guard: a stub run configuration must declare
    itself. Anything else is refused — the stub can never be selected
    by a non-scratch (live) run configuration."""
    cfg = json.loads(Path(path).read_text())
    if cfg.get("scratch_only") is not True:
        raise ValueError("stub configuration refused: scratch_only is not true")
    if cfg.get("subject_identity") != STUB_MODEL_ID:
        raise ValueError("stub configuration refused: subject_identity is not the stub identity")
    if cfg.get("live") is not False:
        raise ValueError("stub configuration refused: live is not false")
    return cfg


if __name__ == "__main__":
    import sys
    srv = make_server(sys.argv[1])
    print(f"stub subject at http://127.0.0.1:{srv.server_address[1]}")
    srv.serve_forever()
