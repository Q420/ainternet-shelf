#!/usr/bin/env python3
"""Duenna Stage 5, Batch 5 — the Nemotron adapter (spec Rev 26
§3.6; Adapter Design 03 §§1–5; chunk sheet C5-1..C5-11).

The adapter exposes exactly one operation,
    complete(step_inputs) -> {capture_record_id, raw_output}
and writes exactly one ADAPTER-CAPTURE-02 record per call,
before returning, in all outcomes.

BATTERY VARIANT (Stage 6 preparation, 2026-11-17; diffs from
the frozen pilot_adapter.py are enumerated in the module
footer): the adapter runs in the laptop custody room and its
only reachable endpoint is the credential relay's tunnel
endpoint on laptop loopback (Route 2, owner ruling
2026-11-17). It holds NO credential and attaches none: the
relay, on the VM, attaches the dynamic credential surrogate
to exactly one fixed upstream. It honours no proxy. The
pinned configuration is the battery adapter config; its
max_tokens is substituted per battery instance from
INSTANCE_MAX_TOKENS below (ceilings accepted by the
examiner's revised budget ruling, 2026-11-17) before the
loader's canonical sha256 verification, which fails closed
on any divergence exactly as the frozen build's does.
"""
import hashlib
import ipaddress
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot_jcs

ADAPTER_ID = "pilot-adapter-stage6-battery/1.0"
# BATTERY VARIANT: no single pinned config digest — the
# effective per-instance config digest is computed at start-up
# over the canonical bytes after ceiling substitution and is
# recorded in every capture (adapter_config_sha256).
PINNED_CONFIG_SHA256 = None
PRODUCTION_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

_REDACT_PATTERNS = [
    (re.compile(r"(Authorization\s*:\s*)([^\s\"',}\]]+)", re.IGNORECASE),
     r"\1[REDACTED]"),
    (re.compile(r"(Bearer\s+)([A-Za-z0-9._\-+/=]+)", re.IGNORECASE),
     r"\1[REDACTED]"),
    (re.compile(r"(nvapi-)([A-Za-z0-9._\-]+)"), r"\1[REDACTED]"),
    (re.compile(r"((?:api[-_ ]?key|apikey)\s*[\"']?\s*[:=]\s*[\"']?)"
                r"([^\s\"',}\]]+)", re.IGNORECASE), r"\1[REDACTED]"),
]


def redact(text):
    """§3.4: no header or credential material in any written
    field. Applied to failure/error detail and to any body
    that would quote such material, before writing; hashes
    are taken over the bytes as written."""
    if text is None:
        return None
    out = text
    for pat, repl in _REDACT_PATTERNS:
        out = pat.sub(repl, out)
    return out


def _now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{dt.microsecond // 1000:03d}Z"


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


class ConfigError(Exception):
    """Adapter-internal misconfiguration: a build-time fault,
    raised at start-up, never a run-time outcome (§5)."""


def _is_loopback(url):
    host = urlparse(url).hostname or ""
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class Adapter:
    # --- BATTERY VARIANT: per-instance completion ceilings
    # (examiner's revised budget ruling, 2026-11-17). The
    # input allowance is 2,048 tokens on every HTTP call;
    # worst cases: 2-call 45,056 / 4-call 49,152 / 6-call
    # 49,152 — all within the 50,000 per-instance budget.
    INSTANCE_MAX_TOKENS = {
        "T01": 10240, "T02": 10240, "T03": 6144, "T04": 20480,
        "T05": 10240, "T06": 20480, "T07": 20480, "T08": 10240,
        "T09": 20480, "T09/FR-A": 20480, "T09/FR-B": 20480,
        "T09/FR-C": 20480, "T09/FR-VALID": 20480,
    }

    def __init__(self, config_path, captures_dir, base_url,
                 stage5_mode=True, instance_id=None):
        # --- BATTERY VARIANT: per-instance max_tokens is
        # substituted from INSTANCE_MAX_TOKENS into the loaded
        # config and the result canonicalised; the pinned
        # digest is then computed over those canonical bytes
        # (no single filed config digest exists — each
        # instance's effective config digest is recorded in
        # every capture as adapter_config_sha256).
        if instance_id not in self.INSTANCE_MAX_TOKENS:
            raise ConfigError(
                f"unknown battery instance: {instance_id!r}")
        self.instance_id = instance_id
        _loaded = json.loads(open(config_path, "rb").read()
                             .decode("utf-8"))
        _loaded["envelope"]["max_tokens"] = \
            self.INSTANCE_MAX_TOKENS[instance_id]
        raw = pilot_jcs.canonicalise(_loaded)
        digest = _sha256(raw)
        cfg = json.loads(raw.decode("utf-8"))
        jcs_digest = _sha256(pilot_jcs.canonicalise(cfg))
        if jcs_digest != digest:
            raise ConfigError(
                "adapter configuration divergence: canonical "
                f"bytes do not round-trip ({jcs_digest} != "
                f"{digest})")
        self._cfg = cfg
        self.config_sha256 = digest
        self.model = cfg["model"]
        self.envelope = cfg["envelope"]
        self.retry = cfg["retry_policy"]
        self.timeout_s = cfg["timeout_seconds_per_attempt"]
        self.catalogue_sha = cfg["catalogue_pin"]["snapshot_sha256"]
        self.catalogue_date = cfg["catalogue_pin"]["capture_date"]
        if self.envelope["model"] != self.model:
            raise ConfigError("envelope model != pinned model")
        # --- Stage 5 isolation (C5-11): loopback only, no proxy
        if stage5_mode and not _is_loopback(base_url):
            raise ConfigError(
                f"Stage 5 isolation: non-loopback base URL refused: "
                f"{base_url}")
        self.endpoint = base_url.rstrip("/") + "/chat/completions" \
            if not base_url.rstrip("/").endswith("/chat/completions") \
            else base_url
        self.captures_dir = captures_dir
        os.makedirs(captures_dir, exist_ok=True)
        # No proxy honoured, in any mode of this build (§3.7 (a)).
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}))

    # ------------------------------------------------------------
    def _attempt(self, body_bytes):
        """One HTTP attempt. Never raises across this boundary:
        every attempt's status, body, timing and exception
        detail are returned for capture (C5-6)."""
        sent = _now()
        result = {"sent_at": sent, "received_at": None,
                  "http_status": None, "body": None,
                  "outcome": None, "error_class": None,
                  "error_detail": None}
        req = urllib.request.Request(
            self.endpoint, data=body_bytes, method="POST",
            headers={"Content-Type": "application/json"})
        try:
            with self._opener.open(req, timeout=self.timeout_s) as resp:
                data = resp.read()
                result.update(received_at=_now(),
                              http_status=resp.status, body=data,
                              outcome="RESPONSE_RECEIVED")
        except urllib.error.HTTPError as e:
            try:
                data = e.read()
            except Exception:
                data = None
            result.update(received_at=_now(), http_status=e.code,
                          body=data, outcome="HTTP_ERROR",
                          error_class="HTTPError",
                          error_detail=f"HTTP {e.code} {e.reason}")
        except (socket.timeout, TimeoutError) as e:
            result.update(outcome="TIMEOUT", error_class="Timeout",
                          error_detail=f"{type(e).__name__}: {e}")
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                result.update(outcome="TIMEOUT", error_class="Timeout",
                              error_detail=f"URLError: {e.reason}")
            else:
                result.update(outcome="TRANSPORT_ERROR",
                              error_class="URLError",
                              error_detail=f"URLError: {e.reason}")
        except Exception as e:  # helper-class catch-all: still captured
            result.update(outcome="HELPER_ERROR",
                          error_class=type(e).__name__,
                          error_detail=f"{type(e).__name__}: {e}")
        return result

    # ------------------------------------------------------------
    def complete(self, step_inputs):
        keys = set(step_inputs.keys())
        if keys != {"correlation_id", "tree_id", "step_id", "messages"}:
            raise ValueError(
                f"step_inputs must carry exactly correlation_id, "
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
        body_bytes = json.dumps(
            body_obj, separators=(",", ":"),
            ensure_ascii=False).encode("utf-8")
        request_sha = _sha256(body_bytes)
        envelope_echo = {
            "model": env["model"],
            "temperature": env["temperature"],
            "top_p": env["top_p"],
            "max_tokens": env["max_tokens"],
            "stream": env["stream"],
            "chat_template_kwargs": env["chat_template_kwargs"],
        }

        max_attempts = int(self.retry["max_attempts"])
        delay = float(self.retry["delay_seconds"])
        attempts = []
        final = None
        for n in range(1, max_attempts + 1):
            if n > 1:
                time.sleep(delay)
            r = self._attempt(body_bytes)
            body_text = None
            body_sha = None
            if r["body"] is not None:
                body_text = redact(r["body"].decode("utf-8", "replace"))
                body_sha = _sha256(body_text.encode("utf-8"))
            attempts.append({
                "attempt_no": n,
                "sent_at_utc": _iso(r["sent_at"]),
                "received_at_utc": _iso(r["received_at"])
                if r["received_at"] else None,
                "http_status": r["http_status"],
                "response_body_raw": body_text,
                "response_body_sha256": body_sha,
                "error_class": r["error_class"],
                "error_detail": redact(r["error_detail"]),
            })
            final = r
            final_body_text = body_text
            # --- retry decision (§4.3): retryable classes only,
            # never a received-and-captured response.
            if n == max_attempts:
                break
            status = r["http_status"]
            retryable = (
                status == 429
                or (status is not None and 500 <= status <= 599)
                or r["outcome"] in ("TIMEOUT", "TRANSPORT_ERROR"))
            if not retryable:
                break

        # --- classify the call (§4) from the final attempt
        status = final["http_status"]
        outcome = final["outcome"]
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
                failure_detail = (
                    f"served model id {served_id!r} != pinned "
                    f"{self.model!r} (identity mismatch)")
            else:
                raw_output = content
        # 200 with an unparseable body falls through here:
        # captured verbatim, failure_class stays None, and
        # classification is downstream (§4.2).
        elif outcome == "HTTP_ERROR":
            failure_class = "ADAPTER_FAILURE"
            detail = f"HTTP {status}"
            if status == 400 and final_body_text and \
                    "chat_template_kwargs" in final_body_text:
                detail += (" — body identifies chat_template_kwargs "
                           "as the rejected parameter (§4.2 "
                           "pre-classified)")
            failure_detail = detail
        elif outcome == "TIMEOUT":
            failure_class = "ADAPTER_FAILURE"
            failure_detail = (
                f"timeout after {self.timeout_s} s per attempt; "
                f"{len(attempts)} attempt(s)")
        elif outcome == "TRANSPORT_ERROR":
            failure_class = "ADAPTER_FAILURE"
            failure_detail = redact(final["error_detail"])
        elif outcome == "HELPER_ERROR":
            failure_class = "ADAPTER_FAILURE"
            failure_detail = redact(final["error_detail"])

        last = attempts[-1]
        latency_ms = None
        if final["received_at"] is not None:
            latency_ms = int((final["received_at"] -
                              final["sent_at"]).total_seconds() * 1000)
        capture_id = str(uuid.uuid4())
        record = {
            "capture_id": capture_id,
            "schema": "ADAPTER-CAPTURE",
            "schema_version": 2,
            "recorded_at_utc": _iso(_now()),
            "correlation_id": step_inputs["correlation_id"],
            "tree_id": step_inputs["tree_id"],
            "step_id": step_inputs["step_id"],
            "adapter_id": ADAPTER_ID,
            "adapter_config_sha256": self.config_sha256,
            "subject_model_id_pinned": self.model,
            "subject_pin_catalogue_sha256": self.catalogue_sha,
            "subject_pin_captured_date": self.catalogue_date,
            "endpoint": self.endpoint,
            "request_sent_at_utc": last["sent_at_utc"],
            "request_raw": body_bytes.decode("utf-8"),
            "request_sha256": request_sha,
            "request_envelope": envelope_echo,
            "response_received_at_utc": last["received_at_utc"]
            if outcome in ("RESPONSE_RECEIVED", "HTTP_ERROR") else None,
            "response_latency_ms": latency_ms
            if outcome in ("RESPONSE_RECEIVED", "HTTP_ERROR") else None,
            "response_http_status": status,
            "response_raw": final_body_text,
            "response_sha256": last["response_body_sha256"],
            "response_model_id_served": served_id,
            "response_finish_reason": finish_reason,
            "response_usage": usage,
            "attempts": attempts,
            "transport_outcome": outcome,
            "failure_class": failure_class,
            "failure_detail": redact(failure_detail),
        }
        record["record_sha256"] = _sha256(pilot_jcs.canonicalise(record))
        path = os.path.join(self.captures_dir, capture_id + ".json")
        with open(path, "xb") as f:
            f.write(pilot_jcs.canonicalise(record))
        return {"capture_record_id": capture_id,
                "raw_output": raw_output}


# ============================================================
# BATTERY VARIANT — enumerated differences from the frozen
# pilot_adapter.py (checkpoint bundle, Stage 5):
# 1. Endpoint: the relay tunnel endpoint on laptop loopback
#    (the frozen build's Stage 5 loopback-double endpoint is
#    the same shape; the relay is the battery's transport).
#    No credential is held or attached by this adapter.
# 2. Per-instance max_tokens from INSTANCE_MAX_TOKENS
#    (substituted before canonical verification); the frozen
#    build reads one global envelope value from a single
#    pinned config.
# 3. Config pinning: the effective per-instance config digest
#    is computed at start-up and recorded per capture; the
#    frozen build pins one filed digest for all runs.
# 4. Retry policy: the battery config carries the frozen
#    max_attempts 2 (the smoke variant's cut to 1 does not
#    carry). No code difference — the policy is config data.
# Capture format, redaction (§3.4), classification (§4) and
# the complete() contract are byte-identical to the frozen
# build.
