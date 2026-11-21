#!/usr/bin/env python3
"""PILOT-JCS — the Nemotron pilot's RFC 8785 (JSON Canonicalization Scheme)
implementation.

Name:    PILOT-JCS
Version: 1.0.0
Role:    The single canonicalisation implementation the Stage 5 build uses
         for every structured artefact it serialises and hashes (Stage 5
         Build Spec §3.4). Pinned at Batch 0 by name, version, and the
         sha256 of this source file, recorded in the re-freeze amendment.
         Any change to this file is a re-freeze event.

Contract (RFC 8785, as pinned by Spec §3.4):
  * No insignificant whitespace; output encoded UTF-8.
  * Object members ordered by the UTF-16 code unit sequence of their
    names, recursively.
  * Strings: minimal escape set of RFC 8785 §3.2.2.2 — \\b \\t \\n \\f \\r,
    \\u00xx (lowercase hex) for the remaining C0 controls, \\" and \\\\;
    every other code point serialised as-is.
  * Numbers: ECMAScript Number::toString (the algorithm RFC 8785
    §3.2.2.3 normatively adopts), over IEEE 754 doubles.
  * Rejection, never coercion: NaN and +/-Infinity; duplicate object
    keys at parse; strings containing lone surrogates; any value of an
    unsupported type.
"""

import json
import math

NAME = "PILOT-JCS"
VERSION = "1.0.0"


class JCSRejection(Exception):
    """A value that cannot be safely represented under RFC 8785."""


# ---------------------------------------------------------------- numbers

def _shortest_digits(x):
    """Decompose a finite positive double into (digits, E) such that
    x == int(digits) * 10**E, where `digits` is the shortest decimal
    digit string that round-trips to x, with no leading or trailing
    zeros. Python's repr() supplies the shortest round-trip digits
    (round-half-even, as ECMAScript requires); this function only
    re-expresses them, it never rounds."""
    r = repr(x)
    if "e" in r:
        mant, _, exp = r.partition("e")
        e10 = int(exp)
    else:
        mant, e10 = r, 0
    if "." in mant:
        ip, _, fp = mant.partition(".")
        point = len(ip) + e10            # value = int(ip+fp) * 10**(point - len(ip+fp))
        digits = ip + fp
    else:
        point = len(mant) + e10
        digits = mant
    E = point - len(digits)
    digits = digits.lstrip("0")
    stripped = digits.rstrip("0")
    E += len(digits) - len(stripped)     # each trailing zero removed raises E by 1
    return stripped, E


def number_to_string(x):
    """ECMAScript Number::toString for a JSON number (a double, or an int
    routed through the double data model as ECMAScript parses it)."""
    if isinstance(x, bool):
        raise JCSRejection("boolean is not a number")
    if isinstance(x, int):
        x = float(x)
    if not isinstance(x, float):
        raise JCSRejection(f"not a number: {type(x).__name__}")
    if math.isnan(x) or math.isinf(x):
        raise JCSRejection("NaN and Infinity are not permitted (RFC 8785 §3.2.2.3)")
    if x == 0:
        return "0"                       # covers -0.0 as well
    sign = "-" if x < 0 else ""
    digits, E = _shortest_digits(abs(x))
    k = len(digits)                      # number of digits in s
    n = E + k                            # value = s * 10**(n-k)
    if k <= n <= 21:
        out = digits + "0" * (n - k)
    elif 0 < n <= 21:                    # here n < k: point falls inside digits
        out = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        out = "0." + "0" * (-n) + digits
    else:                                # exponential form
        if k == 1:
            mant = digits
        else:
            mant = digits[0] + "." + digits[1:]
        e = n - 1
        out = mant + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + out


# ---------------------------------------------------------------- strings

_SHORT_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def _check_no_lone_surrogates(s):
    for ch in s:
        o = ord(ch)
        if 0xD800 <= o <= 0xDFFF:
            raise JCSRejection("lone surrogate in string (RFC 8785 §3.2.2.2)")


def string_to_jcs(s):
    if not isinstance(s, str):
        raise JCSRejection(f"not a string: {type(s).__name__}")
    _check_no_lone_surrogates(s)
    parts = ['"']
    for ch in s:
        esc = _SHORT_ESCAPES.get(ch)
        if esc is not None:
            parts.append(esc)
        elif ord(ch) < 0x20:
            parts.append("\\u%04x" % ord(ch))
        else:
            parts.append(ch)
    parts.append('"')
    return "".join(parts)


# ---------------------------------------------------------------- values

def _utf16_sort_key(name):
    _check_no_lone_surrogates(name)
    # UTF-16BE byte order is exactly UTF-16 code unit order.
    return name.encode("utf-16-be")


def serialise(value):
    """Serialise a Python value (None/bool/int/float/str/list/dict) to
    its RFC 8785 canonical form, returned as a str."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return string_to_jcs(value)
    if isinstance(value, (int, float)):
        return number_to_string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(serialise(v) for v in value) + "]"
    if isinstance(value, dict):
        keys = list(value.keys())
        for key in keys:
            if not isinstance(key, str):
                raise JCSRejection(f"object key is not a string: {key!r}")
        keys.sort(key=_utf16_sort_key)
        return "{" + ",".join(
            string_to_jcs(key) + ":" + serialise(value[key]) for key in keys
        ) + "}"
    raise JCSRejection(f"unsupported type: {type(value).__name__}")


def canonicalise(value):
    """Canonical bytes (UTF-8) for a Python value."""
    return serialise(value).encode("utf-8")


# ---------------------------------------------------------------- parsing

def _reject_constant(name):
    raise JCSRejection(f"non-JSON constant in input: {name}")


def _object_no_duplicates(pairs):
    obj = {}
    for key, val in pairs:
        if key in obj:
            raise JCSRejection(f"duplicate object key at parse: {key!r}")
        obj[key] = val
    return obj


def parse(text):
    """Parse JSON text under the pilot's rejection rules. All numbers
    become doubles, as in the ECMAScript data model JCS is defined
    over. Duplicate keys and the non-JSON constants are rejected."""
    return json.loads(
        text,
        object_pairs_hook=_object_no_duplicates,
        parse_constant=_reject_constant,
        parse_float=float,
        parse_int=float,
    )


def canonicalise_text(text):
    """Canonical bytes for JSON input text: parse under the rejection
    rules, then serialise. A value that cannot round-trip to identical
    canonical bytes is rejected by construction or by the caller
    comparing canonicalise_text(serialise(parse(text))) — see Spec §3.4."""
    return canonicalise(parse(text))
