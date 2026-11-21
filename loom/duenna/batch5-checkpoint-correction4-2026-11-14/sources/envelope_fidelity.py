#!/usr/bin/env python3
"""C5-17 envelope byte fidelity verification — Duenna Stage 5,
Batch 5 checkpoint correction (Alex's C5-17 correction
specification, 2026-11-14; adjudication CLEAR WITH CORRECTIONS).

The original runner's `wire_envelope_matches_config` check parses
the captured request and compares Python values with ==. That is
a semantic comparison; it cannot establish the byte-for-byte
claim the checkpoint wording makes. This module performs the
stronger verification the correction requires:

  * A source-preserving scanner isolates each top-level member
    of the ORIGINAL captured request text, with exact key-token
    and value-token spans. Nothing is parsed-and-reserialised
    before comparison.
  * Each extracted key token is compared, byte for byte, with
    the RFC 8785 canonical bytes of that key (PILOT-JCS), and
    each value token with the canonical bytes of the
    corresponding frozen configuration value. The nested
    chat_template_kwargs object is compared as one complete
    value token, so its nested members are covered too.
  * Transport receipt: the bodies the transport double actually
    received are compared byte for byte with the captured
    request body, and the captured body's SHA-256 is recomputed
    against the record.
  * Negative controls prove the verifier rejects deliberately
    invalid fixtures; a control passes only when the verifier
    rejects its fixture.

Fail-closed throughout: malformed JSON, duplicate top-level
keys, missing expected members, or ambiguous extraction are
verification failures, never passes.
"""
import hashlib
import json
import os

import pilot_jcs


class FidelityError(Exception):
    """The request text cannot be unambiguously scanned."""


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def canonicalisation_info():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "pilot_jcs.py"), "rb") as f:
        source_sha = _sha(f.read())
    return {"name": pilot_jcs.NAME, "version": pilot_jcs.VERSION,
            "source_sha256": source_sha}


# ------------------------------------------------------------- scanner
#
# The scanner is an independent, complete JSON grammar validator
# (Alex's reinspection requirement, 2026-11-14): it must reject
# malformed content ANYWHERE in the document, not only in the
# envelope members being compared. Primitive tokens are validated
# against the literal / number grammar, string escapes are
# validated and unescaped control characters rejected, and nested
# objects / arrays are scanned recursively with full member
# grammar (key, colon, comma) rather than by delimiter counting.

_WS = " \t\n\r"
_HEX = set("0123456789abcdefABCDEF")


def _is_digit(c):
    """ASCII digits only. Python's str.isdigit() accepts
    non-ASCII digits (e.g. Arabic-Indic), which JSON's number
    grammar does not permit (Alex's reinspection 3)."""
    return "0" <= c <= "9"
_ESCAPES = set('"\\/bfnrt')
_MAX_DEPTH = 200


def _skip_ws(text, k):
    while k < len(text) and text[k] in _WS:
        k += 1
    return k


def _scan_string(text, i):
    """End index (exclusive) of the string token starting at i.
    Validates escape syntax and rejects unescaped control
    characters (code points below U+0020)."""
    j = i + 1
    while j < len(text):
        c = text[j]
        if c == "\\":
            if j + 1 >= len(text):
                raise FidelityError("unterminated escape sequence")
            e = text[j + 1]
            if e == "u":
                digits = text[j + 2:j + 6]
                if len(digits) != 4 or \
                        any(d not in _HEX for d in digits):
                    raise FidelityError(
                        "invalid \\u escape in string token")
                j += 6
                continue
            if e not in _ESCAPES:
                raise FidelityError(
                    f"invalid escape character in string: \\{e}")
            j += 2
            continue
        if c == '"':
            return j + 1
        if ord(c) < 0x20:
            raise FidelityError(
                "unescaped control character in string token")
        j += 1
    raise FidelityError("unterminated string token")


def _scan_primitive(text, i):
    """End index (exclusive) of a literal / number token at i,
    validated against the JSON grammar: true, false, null, or
    -?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?. The token
    must be followed by a structural delimiter, whitespace, or
    the end of the text — so `truue`, `01`, `1e` and `1.` all
    fail closed."""
    for lit in ("true", "false", "null"):
        if text.startswith(lit, i):
            j = i + len(lit)
            if j < len(text) and \
                    text[j] not in ",}]" + _WS:
                raise FidelityError(
                    f"invalid literal token at offset {i}")
            return j
    j = i
    if j < len(text) and text[j] == "-":
        j += 1
    if j < len(text) and text[j] == "0":
        j += 1
    elif j < len(text) and text[j] in "123456789":
        while j < len(text) and _is_digit(text[j]):
            j += 1
    else:
        raise FidelityError(f"invalid value token at offset {i}")
    if j < len(text) and text[j] == ".":
        j += 1
        if j >= len(text) or not _is_digit(text[j]):
            raise FidelityError(
                f"invalid number fraction at offset {i}")
        while j < len(text) and _is_digit(text[j]):
            j += 1
    if j < len(text) and text[j] in "eE":
        j += 1
        if j < len(text) and text[j] in "+-":
            j += 1
        if j >= len(text) or not _is_digit(text[j]):
            raise FidelityError(
                f"invalid number exponent at offset {i}")
        while j < len(text) and _is_digit(text[j]):
            j += 1
    if j < len(text) and text[j] not in ",}]" + _WS:
        raise FidelityError(f"invalid number token at offset {i}")
    return j


def _scan_object(text, i, depth):
    """End index (exclusive) of the object token starting at i,
    with full member grammar enforced."""
    j = _skip_ws(text, i + 1)
    if j < len(text) and text[j] == "}":
        return j + 1
    while True:
        j = _skip_ws(text, j)
        if j >= len(text) or text[j] != '"':
            raise FidelityError("expected a member key string")
        j = _scan_string(text, j)
        j = _skip_ws(text, j)
        if j >= len(text) or text[j] != ":":
            raise FidelityError("expected ':' after member key")
        j = _skip_ws(text, j + 1)
        if j >= len(text):
            raise FidelityError("missing member value")
        j = _scan_value(text, j, depth + 1)
        j = _skip_ws(text, j)
        if j < len(text) and text[j] == ",":
            j += 1
            continue
        if j < len(text) and text[j] == "}":
            return j + 1
        raise FidelityError("expected ',' or '}' in object")


def _scan_array(text, i, depth):
    """End index (exclusive) of the array token starting at i,
    with full element grammar enforced."""
    j = _skip_ws(text, i + 1)
    if j < len(text) and text[j] == "]":
        return j + 1
    while True:
        j = _skip_ws(text, j)
        if j >= len(text):
            raise FidelityError("unterminated array token")
        j = _scan_value(text, j, depth + 1)
        j = _skip_ws(text, j)
        if j < len(text) and text[j] == ",":
            j += 1
            continue
        if j < len(text) and text[j] == "]":
            return j + 1
        raise FidelityError("expected ',' or ']' in array")


def _scan_value(text, i, depth=0):
    """End index (exclusive) of the value token starting at i.
    Every token kind is grammar-validated, recursively."""
    if depth > _MAX_DEPTH:
        raise FidelityError("nesting depth limit exceeded")
    c = text[i]
    if c == '"':
        return _scan_string(text, i)
    if c == "{":
        return _scan_object(text, i, depth)
    if c == "[":
        return _scan_array(text, i, depth)
    return _scan_primitive(text, i)


def scan_top_level(text):
    """Isolate the top-level members of a JSON object text.

    Returns a list of dicts: name (decoded key), key_token,
    value_token, key_span, value_span — tokens and spans taken
    from the original text, unmodified. Raises FidelityError on
    malformed input or duplicate top-level keys. The scanner
    must consume the complete document: only trailing JSON
    whitespace may follow the closing brace.
    """
    n = len(text)

    def skip_ws(k):
        while k < n and text[k] in _WS:
            k += 1
        return k

    def finish(k):
        if skip_ws(k) != n:
            raise FidelityError(
                "trailing content after end of document")
        return members

    i = skip_ws(0)
    if i >= n or text[i] != "{":
        raise FidelityError("request body is not a JSON object")
    i = skip_ws(i + 1)
    members = []
    seen = set()
    if i < n and text[i] == "}":
        return finish(i + 1)
    while True:
        i = skip_ws(i)
        if i >= n or text[i] != '"':
            raise FidelityError("expected a member key string")
        kend = _scan_string(text, i)
        key_token = text[i:kend]
        try:
            name = json.loads(key_token)
        except Exception:
            raise FidelityError("undecodable member key token")
        if not isinstance(name, str):
            raise FidelityError("member key is not a string")
        if name in seen:
            raise FidelityError(f"duplicate top-level key: {name!r}")
        seen.add(name)
        i = skip_ws(kend)
        if i >= n or text[i] != ":":
            raise FidelityError("expected ':' after member key")
        i = skip_ws(i + 1)
        if i >= n:
            raise FidelityError("missing member value")
        vend = _scan_value(text, i)
        members.append({
            "name": name,
            "key_token": key_token,
            "value_token": text[i:vend],
            "key_start": kend - len(key_token),
            "key_end": kend,
            "value_start": i,
            "value_end": vend,
        })
        i = skip_ws(vend)
        if i < n and text[i] == ",":
            i += 1
            continue
        if i < n and text[i] == "}":
            return finish(i + 1)
        raise FidelityError("expected ',' or '}' after member value")


# ------------------------------------------------------- verification

def _token_report(actual_text, expected_bytes):
    actual = actual_text.encode("utf-8")
    return {
        "actual_bytes": len(actual),
        "actual_sha256": _sha(actual),
        "expected_bytes": len(expected_bytes),
        "expected_sha256": _sha(expected_bytes),
        "match": actual == expected_bytes,
    }


def verify_envelope(request_raw, cfg_envelope):
    """Byte-level comparison of the original request's envelope
    member tokens against the frozen configuration's canonical
    bytes. Returns {"passed", "members", "failures"}."""
    failures = []
    try:
        members = scan_top_level(request_raw)
    except FidelityError as e:
        return {"passed": False, "members": [],
                "failures": [f"scan failed: {e}"]}
    by_name = {m["name"]: m for m in members}
    reports = []
    for key, cfg_value in cfg_envelope.items():
        entry = {"member": key, "present": key in by_name}
        if key not in by_name:
            entry["match"] = False
            failures.append(f"missing envelope member: {key}")
            reports.append(entry)
            continue
        m = by_name[key]
        key_rep = _token_report(
            m["key_token"],
            pilot_jcs.string_to_jcs(key).encode("utf-8"))
        val_rep = _token_report(
            m["value_token"], pilot_jcs.canonicalise(cfg_value))
        entry["key_token"] = key_rep
        entry["value_token"] = val_rep
        entry["match"] = key_rep["match"] and val_rep["match"]
        if not key_rep["match"]:
            failures.append(f"key token bytes differ: {key}")
        if not val_rep["match"]:
            failures.append(f"value token bytes differ: {key}")
        reports.append(entry)
    return {"passed": not failures, "members": reports,
            "failures": failures}


def verify_transport(rec, received_bodies):
    """The double's received bodies against the captured body."""
    failures = []
    captured = rec["request_raw"].encode("utf-8")
    captured_sha = _sha(captured)
    if captured_sha != rec["request_sha256"]:
        failures.append(
            "captured request_raw SHA-256 does not recompute to "
            "the record's request_sha256")
    attempts = []
    for idx, body in enumerate(received_bodies):
        match = body == captured
        attempts.append({
            "attempt": idx + 1,
            "received_bytes": len(body),
            "received_sha256": _sha(body),
            "matches_captured": match,
        })
        if not match:
            failures.append(
                f"transport-received body for attempt {idx + 1} "
                "differs from the captured request body")
    if len(received_bodies) != len(rec["attempts"]):
        failures.append(
            f"transport received {len(received_bodies)} requests "
            f"but the record carries {len(rec['attempts'])} attempts")
    return {
        "passed": not failures,
        "captured_request_sha256": captured_sha,
        "record_request_sha256": rec["request_sha256"],
        "attempts_recorded": len(rec["attempts"]),
        "transport_requests_received": len(received_bodies),
        "attempts": attempts,
        "failures": failures,
    }


def verify_capture(rec, cfg_envelope, received_bodies):
    """Full C5-17 verification for one captured scenario."""
    env = verify_envelope(rec["request_raw"], cfg_envelope)
    trans = verify_transport(rec, received_bodies)
    return {
        "capture_id": rec["capture_id"],
        "adapter_config_sha256": rec["adapter_config_sha256"],
        "captured_request_sha256": rec["request_sha256"],
        "attempts_recorded": len(rec["attempts"]),
        "transport_requests_received": len(received_bodies),
        "envelope": env,
        "transport": trans,
        "passed": env["passed"] and trans["passed"],
    }


# --------------------------------------------------- negative controls

def _member(raw, name):
    for m in scan_top_level(raw):
        if m["name"] == name:
            return m
    raise FidelityError(f"control construction: no member {name!r}")


def _remove_member(raw, name):
    members = scan_top_level(raw)
    idx = [k for k, m in enumerate(members) if m["name"] == name]
    if not idx:
        raise FidelityError("control construction: member absent")
    i = idx[0]
    m = members[i]
    if i + 1 < len(members):
        # Cut from this key's start to the next key's start: removes
        # the member, its value, and the separating comma.
        return raw[:m["key_start"]] + raw[members[i + 1]["key_start"]:]
    # Last member: cut from the previous value's end to this
    # value's end (removes the comma and the member).
    prev_end = members[i - 1]["value_end"]
    return raw[:prev_end] + raw[m["value_end"]:]


def negative_controls(sample_raw, cfg_envelope):
    """Deliberately invalid fixtures. Each control passes only
    when the verifier REJECTS its fixture."""
    controls = []

    def record(name, fn):
        try:
            rejected, detail = fn()
        except Exception as e:  # construction error = control failure
            rejected, detail = False, f"control error: {e}"
        controls.append({
            "control": name,
            "expected": "rejected",
            "rejected": rejected,
            "passed": bool(rejected),
            "detail": detail,
        })

    def env_rejects(mutant):
        r = verify_envelope(mutant, cfg_envelope)
        return (not r["passed"]), "; ".join(r["failures"][:2])

    # 1. An envelope value changed, still valid JSON.
    m = _member(sample_raw, "temperature")
    mutant = (sample_raw[:m["value_start"]] + "0.7" +
              sample_raw[m["value_end"]:])
    record("changed_envelope_value", lambda: env_rejects(mutant))

    # 2. A missing envelope member.
    record("missing_envelope_member",
           lambda: env_rejects(_remove_member(sample_raw, "top_p")))

    # 3. An unexpected duplicate envelope member.
    m = _member(sample_raw, "stream")
    pair = (sample_raw[m["key_start"]:m["value_end"]])
    mutant = (sample_raw[:m["value_end"]] + "," + pair +
              sample_raw[m["value_end"]:])
    record("duplicate_envelope_member", lambda: env_rejects(mutant))

    # 4. A noncanonical lexical representation of an equivalent
    # value: escape one character of the model string (\u006e = n).
    # The parsed value is unchanged; the bytes are not canonical.
    m = _member(sample_raw, "model")
    tok = m["value_token"]
    assert tok[1] == "n"
    mutant_tok = tok[:1] + "\\u006e" + tok[2:]
    mutant = (sample_raw[:m["value_start"]] + mutant_tok +
              sample_raw[m["value_end"]:])
    record("noncanonical_lexical_value", lambda: env_rejects(mutant))

    # 5. A changed nested chat_template_kwargs value.
    m = _member(sample_raw, "chat_template_kwargs")
    assert "16384" in m["value_token"]
    mutant_tok = m["value_token"].replace("16384", "16385")
    mutant = (sample_raw[:m["value_start"]] + mutant_tok +
              sample_raw[m["value_end"]:])
    record("changed_nested_kwargs_value", lambda: env_rejects(mutant))

    # 6. A transport-received body that differs from the capture.
    good = sample_raw.encode("utf-8")
    bad = good[:-2] + b"X}"
    fake_rec = {"request_raw": sample_raw,
                "request_sha256": _sha(good),
                "attempts": [{}]}
    r = verify_transport(fake_rec, [bad])
    record("transport_received_body_differs",
           lambda: (not r["passed"], "; ".join(r["failures"][:2])))

    # 7. Mismatched delimiters: the kwargs object's closing
    # brace replaced with a bracket. A depth counter alone
    # would accept this; the delimiter stack must not.
    m = _member(sample_raw, "chat_template_kwargs")
    vend = m["value_end"] - 1
    assert sample_raw[vend] == "}"
    mutant = sample_raw[:vend] + "]" + sample_raw[vend + 1:]
    record("mismatched_delimiters", lambda: env_rejects(mutant))

    # 8. Trailing garbage after the complete document: the
    # scanner must consume the whole input, allowing only
    # trailing JSON whitespace.
    record("trailing_garbage_after_document",
           lambda: env_rejects(sample_raw + " garbage"))

    # 9. An invalid primitive literal in a NON-envelope member
    # (Alex's reinspection 2 example): `truue` must be rejected
    # by the scanner's own grammar validation even though the
    # member is never compared against the configuration.
    k = sample_raw.rfind("}")
    mutant = (sample_raw[:k] + ',"unrelated":truue' +
              sample_raw[k:])
    record("invalid_primitive_in_nonmember",
           lambda: env_rejects(mutant))

    # 10. An invalid string escape in a NON-envelope member:
    # \x is not a JSON escape; the scanner must reject it
    # anywhere in the document.
    mutant = (sample_raw[:k] + ',"unrelated":"bad\\xescape"' +
              sample_raw[k:])
    record("invalid_escape_in_nonmember",
           lambda: env_rejects(mutant))

    # 11. Malformed nested syntax: the colon of the first
    # nested pair inside chat_template_kwargs removed. The
    # recursive scanner must reject the nested object even
    # though the envelope comparison treats it as one token.
    m = _member(sample_raw, "chat_template_kwargs")
    tok = m["value_token"]
    colon = tok.index(":")
    mutant_tok = tok[:colon] + tok[colon + 1:]
    mutant = (sample_raw[:m["value_start"]] + mutant_tok +
              sample_raw[m["value_end"]:])
    record("malformed_nested_object_syntax",
           lambda: env_rejects(mutant))

    # 12-14. Non-ASCII digits in numbers (Alex's reinspection
    # 3): Python's str.isdigit() accepts Unicode digits such
    # as Arabic-Indic ٢ (U+0662); JSON permits ASCII 0-9
    # only. One control per position — integer, fraction,
    # exponent — each in an added non-envelope member.
    mutant = (sample_raw[:k] + ',"unrelated":1\u0662' +
              sample_raw[k:])
    record("non_ascii_digit_integer",
           lambda: env_rejects(mutant))
    mutant = (sample_raw[:k] + ',"unrelated":1.5\u0665' +
              sample_raw[k:])
    record("non_ascii_digit_fraction",
           lambda: env_rejects(mutant))
    mutant = (sample_raw[:k] + ',"unrelated":1e1\u0662' +
              sample_raw[k:])
    record("non_ascii_digit_exponent",
           lambda: env_rejects(mutant))

    return controls
