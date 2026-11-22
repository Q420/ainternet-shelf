"""Canonical serialisation and hashing — Loom spec v0.1 Rev 9, section 3.

An event's canonical serialisation is JSON, UTF-8, object keys sorted
lexicographically at every depth, no insignificant whitespace, integers
without exponents. hash = SHA-256 over prev_hash (as hex) concatenated
with the canonical serialisation of the event excluding the hash field.
"""
import hashlib
import json


def canonical(obj) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def event_hash(prev_hash: str, event_without_hash: dict) -> str:
    return sha256_hex(prev_hash.encode("utf-8") + canonical(event_without_hash))
