"""Stage 9 — the live subject transport (the adapter, rebuilt on
the staged governance).

The frozen adapter (actions_adapter.py, config 37e7c1ea) called
the NVIDIA endpoint directly with the credential in-process.
Stage 9 calls the same endpoint through the custom.nvidia
connector's own surrogate mechanism — ``add_surrogate_to_request``
from the connector-setup machinery, the same mechanism the stock
helper uses: the request carries an ``hsurr:`` surrogate and the
registered egress path swaps it for the real credential. The real
key never touches stage9 code, environment, or logs.

Two frozen parameters are load-bearing and are NOT the stock
helper's: the per-attempt timeout is 600 s (Alex's timeout ruling,
2026-11-17 — attempt 2 was lost at 120 s; DR-21), and the request
body is built byte-exactly as the frozen adapter builds it
(model, messages, the frozen envelope fields, compact JSON
separators, ensure_ascii=False).

Classification ports the frozen adapter exactly:
- served model id present and != requested -> ADAPTER_FAILURE
- HTTP error / timeout / transport error -> ADAPTER_FAILURE
  (detail carries the frozen vocabulary: HTTP_ERROR / TIMEOUT /
  TRANSPORT_ERROR)
- otherwise a capture record in the frozen ADAPTER-CAPTURE v2
  shape: request/response raw + hashes, served id, usage,
  attempts.
Retries port the frozen config: byte-identical resend, at most
``max_attempts`` attempts, fixed delay, retryable statuses
429 / 5xx / timeout / connection error.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(
    0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

HOST = "integrate.api.nvidia.com"
PRODUCTION_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
ENDPOINT_CLASS = "nvidia-nim-openai-compatible"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

TIMEOUT_S = 600  # Alex's timeout ruling 2026-11-17 (DR-21).


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class LiveTransport:
    """One subject lane: complete(messages, ceiling) -> capture.

    ``envelope`` is the frozen adapter envelope (from the pinned
    actions-adapter-config.json, read through the frozen run's
    governed config — the transport holds no private copy of the
    values it sends).
    """

    def __init__(self, model_id: str, envelope: dict = None,
                 retry: dict = None):
        self.model_id = model_id
        self.envelope = envelope
        self.retry = retry
        self.endpoint = PRODUCTION_ENDPOINT

    def set_envelope(self, envelope: dict, retry: dict):
        """Receive the governed envelope + retry policy from the
        frozen run's access path (never from a private copy)."""
        self.envelope = envelope
        self.retry = retry

    # -- one attempt -------------------------------------------------
    def _attempt(self, messages, max_tokens):
        body = {
            "model": self.model_id,
            "messages": messages,
            "temperature": self.envelope["temperature"],
            "top_p": self.envelope["top_p"],
            "max_tokens": max_tokens,
            "stream": self.envelope["stream"],
            "chat_template_kwargs":
                self.envelope["chat_template_kwargs"],
        }
        raw_body = json.dumps(body, separators=(",", ":"),
                              ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=raw_body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "NVIDIA/Python 1.0 (Pulse HQ Remmy)")
        add_surrogate_to_request(req, "custom.nvidia",
                                 allowed_hosts=[HOST])
        opener = urllib.request.build_opener(NoRedirect())
        try:
            with opener.open(req, timeout=TIMEOUT_S) as resp:
                status = resp.status
                raw = resp.read()
        except urllib.error.HTTPError as e:
            raw = e.read() if hasattr(e, "read") else b""
            return {"outcome": "HTTP_ERROR", "status": e.code,
                    "raw_body": raw_body, "raw_response": raw}
        except TimeoutError:
            return {"outcome": "TIMEOUT", "status": None,
                    "raw_body": raw_body, "raw_response": b""}
        except urllib.error.URLError as e:
            reason = getattr(e, "reason", e)
            if isinstance(reason, TimeoutError):
                return {"outcome": "TIMEOUT", "status": None,
                        "raw_body": raw_body, "raw_response": b""}
            return {"outcome": "TRANSPORT_ERROR", "status": None,
                    "raw_body": raw_body, "raw_response": b"",
                    "error": repr(e)}
        except Exception as e:  # connection errors surface variously
            return {"outcome": "TRANSPORT_ERROR", "status": None,
                    "raw_body": raw_body, "raw_response": b"",
                    "error": repr(e)}
        return {"outcome": "RESPONSE", "status": status,
                "raw_body": raw_body, "raw_response": raw}

    # -- the lane call ------------------------------------------------
    def complete(self, messages, max_tokens):
        """Run one logical call (with the frozen retry shape) and
        return either a capture dict (kind == "capture") or an
        adapter-failure dict (kind == "adapter_failure") in the
        driver's vocabulary."""
        retry = self.retry
        max_attempts = int(retry["max_attempts"])
        delay = float(retry["delay_seconds"])
        attempts = []
        last = None
        for n in range(1, max_attempts + 1):
            started = time.monotonic()
            res = self._attempt(messages, max_tokens)
            elapsed = time.monotonic() - started
            attempt_rec = {"attempt": n, "outcome": res["outcome"],
                           "status": res["status"],
                           "elapsed_s": round(elapsed, 3)}
            attempts.append(attempt_rec)
            last = res
            if res["outcome"] == "RESPONSE":
                break
            retryable = res["outcome"] in ("TIMEOUT",
                                           "TRANSPORT_ERROR") or (
                res["outcome"] == "HTTP_ERROR" and (
                    res["status"] == 429 or
                    (res["status"] is not None and res["status"] >= 500)))
            if not retryable or n == max_attempts:
                break
            time.sleep(delay)
        if last["outcome"] != "RESPONSE":
            return {"kind": "adapter_failure",
                    "classification": "ADAPTER_FAILURE",
                    "detail": last["outcome"],
                    "status": last["status"],
                    "attempts": attempts,
                    "request_sha256": _sha256(last["raw_body"])}
        raw = last["raw_response"]
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except Exception:
            return {"kind": "adapter_failure",
                    "classification": "ADAPTER_FAILURE",
                    "detail": "UNPARSEABLE_RESPONSE",
                    "status": last["status"], "attempts": attempts,
                    "request_sha256": _sha256(last["raw_body"]),
                    "response_sha256": _sha256(raw)}
        served = parsed.get("model")
        if served is not None and served != self.model_id:
            return {"kind": "adapter_failure",
                    "classification": "ADAPTER_FAILURE",
                    "detail": "SERVED_MODEL_MISMATCH",
                    "served_model_id": served,
                    "status": last["status"], "attempts": attempts,
                    "request_sha256": _sha256(last["raw_body"]),
                    "response_sha256": _sha256(raw)}
        choices = parsed.get("choices") or []
        content = ""
        if choices:
            content = (choices[0].get("message") or {}).get(
                "content") or ""
        return {
            "kind": "capture",
            "request": {"raw": last["raw_body"].decode("utf-8"),
                        "sha256": _sha256(last["raw_body"])},
            "response": {"raw": raw.decode("utf-8", "replace"),
                         "sha256": _sha256(raw),
                         "status": last["status"],
                         "served_model_id": served,
                         "content": content,
                         "usage": parsed.get("usage")},
            "attempts": attempts,
        }

    def _pinned_envelope_retry(self):
        """The pre-freeze lane parameters, from the pinned adapter
        config artefact itself (digest-verified vendored copy).
        The verification call precedes the freeze, so no governed
        values exist yet; after the freeze, set_envelope replaces
        these with the frozen run's values (identical — the config
        draft is built from this same pinned artefact)."""
        import pins
        pins.verify_freeze()
        with open(os.path.join(
                pins.FROZEN_DIR, "src",
                "actions-adapter-config.json"),
                encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg["envelope"], cfg["retry_policy"]

    # -- the K2 verification lane --------------------------------------
    def verification_call(self):
        """The mandatory one-call live verification (Alex's pin
        ruling, 2026-11-17): a minimal call naming the exact model
        id. Returns (served_identity, endpoint, evidence) — the
        binder's lane shape plus the evidence dict the run records.
        On any failure the served identity returned is whatever the
        evidence establishes (None when nothing answered), so the
        freeze refuses: an unverifiable subject never starts a
        scored run."""
        if self.envelope is None or self.retry is None:
            envelope, retry = self._pinned_envelope_retry()
            self.set_envelope(envelope, retry)
        messages = [{"role": "user", "content": "Say: lane open"}]
        result = self.complete(messages, max_tokens=512)
        evidence = {"endpoint": self.endpoint,
                    "endpoint_class": ENDPOINT_CLASS,
                    "requested_model_id": self.model_id,
                    "result": result}
        if result["kind"] != "capture":
            return None, self.endpoint, evidence
        served = result["response"]["served_model_id"]
        content = result["response"]["content"]
        evidence["served_model_id"] = served
        evidence["non_empty_response"] = bool(content and
                                              content.strip())
        evidence["usage"] = result["response"]["usage"]
        if not evidence["non_empty_response"]:
            return None, self.endpoint, evidence
        return served, self.endpoint, evidence


def list_models():
    """The connector's standing pre-check: the live model list on
    the key (a harmless read). Returns the parsed list response or
    an error dict. Used as corroborating evidence for the pin's
    availability clause — the verification call itself is the
    controlling evidence."""
    req = urllib.request.Request(
        "https://integrate.api.nvidia.com/v1/models", method="GET")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "NVIDIA/Python 1.0 (Pulse HQ Remmy)")
    add_surrogate_to_request(req, "custom.nvidia",
                             allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": repr(e)}
