#!/usr/bin/env python3
"""Relay 01 — pinned invocation caller (package exhibit).

The ONLY code path by which Relay 01 participant calls are made.
It exists so the complete client-side invocation boundary is one
inspectable artefact: this file, the three provider helpers it
invokes (byte-identical exhibited copies, hash-verified before
every call), and their single dependency, dynamic_credentials
(exhibited alongside).

What it does, in order:
  1. Verifies the exhibited helper's SHA-256 against the pinned
     table below. Mismatch: refuse to run.
  2. Builds the request body from explicit text files named on
     the command line (--system once, --user one or more times)
     plus an optional --params JSON file merged verbatim. No
     other input is read. There is no conversation, session,
     thread, or retained-context input of any kind.
  3. Writes the body to <out>/<label>.body.json and hashes it.
  4. Invokes the exhibited helper with the body bytes on its
     standard input; saves the helper's stdout verbatim to
     <out>/<label>.resp.json and hashes it.
  5. Writes <out>/<label>.record.json: provider, model, helper
     path + verified hash, body/response file names + hashes,
     the provider's response identifier, timestamps, exit code.

Usage:
  relay_call.py --provider {nvidia,groq,gemini} --model ID
                --out DIR --label NAME [--max-tokens N]
                [--system FILE] --user FILE [--user FILE ...]
                [--params FILE]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

HELPERS = {
    "nvidia": ("nvidia_api.py",
               "aa181fe760cf8065edeb7511ffa78c91d8a39d3a0e38d06eed0a508637298f25",
               "chat"),
    "groq": ("groq_api.py",
             "44e87c17c68f47b1b5c5f7d08535fe32745e2cd0f034b93aa49047aa04b3f3c0",
             "chat"),
    "gemini": ("gemini_api.py",
               "b502ab3b37d617e96b08406105d364c779c3e871f7b58d7fe88baf452ba6f1d2",
               "generate"),
}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def now():
    return datetime.now(timezone.utc).isoformat()


def build_body(provider, model, system_text, user_texts, max_tokens, params):
    if provider in ("nvidia", "groq"):
        messages = []
        if system_text is not None:
            messages.append({"role": "system", "content": system_text})
        for text in user_texts:
            messages.append({"role": "user", "content": text})
        body = {"model": model, "messages": messages,
                "max_tokens": max_tokens}
    else:  # gemini generateContent shape
        body = {"contents": [{"role": "user",
                              "parts": [{"text": t} for t in user_texts]}]}
        if system_text is not None:
            body["system_instruction"] = {"parts": [{"text": system_text}]}
    if params:
        body.update(params)
    return body


def response_id(provider, resp_bytes):
    try:
        data = json.loads(resp_bytes.decode("utf-8"))
    except Exception:
        return None
    if provider in ("nvidia", "groq"):
        return data.get("id")
    return data.get("responseId")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=sorted(HELPERS))
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--system")
    ap.add_argument("--user", action="append", required=True)
    ap.add_argument("--params")
    args = ap.parse_args()

    helper_name, pinned_hash, verb = HELPERS[args.provider]
    helper_path = os.path.join(HERE, helper_name)
    actual_hash = sha256_file(helper_path)
    if actual_hash != pinned_hash:
        print(f"REFUSED: helper {helper_name} hash {actual_hash} "
              f"!= pinned {pinned_hash}", file=sys.stderr)
        return 3

    system_text = read_text(args.system) if args.system else None
    user_texts = [read_text(p) for p in args.user]
    params = None
    if args.params:
        params = json.loads(read_text(args.params))

    body = build_body(args.provider, args.model, system_text,
                      user_texts, args.max_tokens, params)
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

    os.makedirs(args.out, exist_ok=True)
    body_file = os.path.join(args.out, f"{args.label}.body.json")
    resp_file = os.path.join(args.out, f"{args.label}.resp.json")
    record_file = os.path.join(args.out, f"{args.label}.record.json")
    with open(body_file, "wb") as f:
        f.write(body_bytes)
    body_hash = sha256_bytes(body_bytes)

    started = now()
    proc = subprocess.run(
        [sys.executable, helper_path, verb, args.model],
        input=body_bytes, capture_output=True, timeout=600)
    finished = now()
    with open(resp_file, "wb") as f:
        f.write(proc.stdout)
    resp_hash = sha256_bytes(proc.stdout)
    stderr_file = os.path.join(args.out, f"{args.label}.stderr.txt")
    with open(stderr_file, "wb") as f:
        f.write(proc.stderr)
    stderr_hash = sha256_bytes(proc.stderr)

    record = {
        "label": args.label,
        "provider": args.provider,
        "model": args.model,
        "helper": helper_name,
        "helper_sha256_verified": actual_hash,
        "body_file": os.path.basename(body_file),
        "body_sha256": body_hash,
        "response_file": os.path.basename(resp_file),
        "response_sha256": resp_hash,
        "stderr_file": os.path.basename(stderr_file),
        "stderr_sha256": stderr_hash,
        "provider_response_id": response_id(args.provider, proc.stdout),
        "helper_exit_code": proc.returncode,
        "started_at_utc": started,
        "finished_at_utc": finished,
    }
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=1)
    print(json.dumps(record))
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
