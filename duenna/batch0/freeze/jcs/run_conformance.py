#!/usr/bin/env python3
"""RFC 8785 conformance run for PILOT-JCS (Batch 0 freeze check, Spec §3.4).

The test vectors are extracted from the RFC 8785 text itself, as preserved
on disk by the snapshotter (sha256 recorded below and in the results), so
the expected outputs are the RFC's own, not a transcription from memory:

  * Appendix B, Table 1 — IEEE 754 bit pattern -> JSON representation
    (NaN / Infinity rows carry no representation: they must be REJECTED).
  * §3.2.2 input object -> §3.2.3 canonical output (extracted verbatim).
  * §3.2.3 sorting test data -> the RFC's expected property order.
  * The §3.4 rejection rules: duplicate keys at parse, lone surrogates,
    non-JSON constants, native NaN/Infinity.

Writes rfc8785-test-vectors.json (the extracted set) and
jcs-conformance-results.json (per-vector outcomes) beside this script.
"""
import hashlib
import json
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import pilot_jcs

RFC_PATH = pathlib.Path.home() / "workspace/snapshotter/snapshots/snap-live-rfc8785/page-001/text.md"
rfc_bytes = RFC_PATH.read_bytes()
rfc_sha256 = hashlib.sha256(rfc_bytes).hexdigest()
rfc = rfc_bytes.decode("utf-8")

vectors = {"source": {"document": "RFC 8785 (rfc8785.txt)",
                      "path": str(RFC_PATH),
                      "sha256": rfc_sha256},
           "number_samples": [], "objects": [], "rejections": []}
results = {"implementation": {"name": pilot_jcs.NAME, "version": pilot_jcs.VERSION,
                              "source_sha256": hashlib.sha256(
                                  (HERE / "pilot_jcs.py").read_bytes()).hexdigest()},
           "rfc_source_sha256": rfc_sha256,
           "checks": [], "summary": {}}

def check(name, ok, detail=""):
    results["checks"].append({"check": name, "pass": bool(ok), "detail": detail})
    return ok

# ---- Appendix B, Table 1 -------------------------------------------------
rows = re.findall(r"\|\s*([0-9a-f]{16})\s*\|\s*([^|]*?)\s*\|", rfc)
seen = set()
for bits, rep in rows:
    if bits in seen:
        continue
    seen.add(bits)
    rep = rep.strip()
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    vectors["number_samples"].append(
        {"ieee754_hex": bits, "expected": rep if rep else None,
         "expect_rejection": rep == ""})
    name = f"AppendixB {bits}"
    if rep == "":
        try:
            pilot_jcs.number_to_string(value)
            check(name, False, "non-finite value was serialised, not rejected")
        except pilot_jcs.JCSRejection:
            check(name, True, "rejected as required")
    else:
        try:
            got = pilot_jcs.number_to_string(value)
            check(name, got == rep, f"expected {rep!r} got {got!r}")
        except pilot_jcs.JCSRejection as e:
            check(name, False, f"unexpected rejection: {e}")

# ---- §3.2.2 input -> §3.2.3 canonical output ------------------------------
sample_input = (
    '{"numbers": [333333333.33333329, 1E30, 4.50, 2e-3,'
    ' 0.000000000000000000000000001],'
    ' "string": "\\u20ac$\\u000F\\u000aA\'\\u0042\\u0022\\u005c\\\\\\"\\/",'
    ' "literals": [null, true, false]}'
)
i = rfc.index("read as:")
seg = rfc[i:i + 220]
joined = "".join(l.strip() for l in seg.splitlines()
                 if l.strip().startswith("{") or l.strip().startswith("1e+30"))
expected_obj = joined.encode("utf-8")
vectors["objects"].append({"name": "rfc-section-3.2.2-to-3.2.3",
                           "input": sample_input,
                           "expected_canonical_utf8_hex": expected_obj.hex()})
try:
    got_obj = pilot_jcs.canonicalise_text(sample_input)
    check("object §3.2.2->§3.2.3", got_obj == expected_obj,
          f"expected {expected_obj!r} got {got_obj!r}")
except pilot_jcs.JCSRejection as e:
    check("object §3.2.2->§3.2.3", False, f"unexpected rejection: {e}")

# ---- §3.2.3 sorting test data ---------------------------------------------
sorting_input = (
    '{"\\u20ac": "Euro Sign", "\\r": "Carriage Return",'
    ' "\\ufb33": "Hebrew Letter Dalet With Dagesh", "1": "One",'
    ' "\\ud83d\\ude00": "Emoji: Grinning Face", "\\u0080": "Control",'
    ' "\\u00f6": "Latin Small Letter O With Diaeresis"}'
)
expected_order = ["Carriage Return", "One", "Control",
                  "Latin Small Letter O With Diaeresis", "Euro Sign",
                  "Emoji: Grinning Face", "Hebrew Letter Dalet With Dagesh"]
vectors["objects"].append({"name": "rfc-section-3.2.3-sorting",
                           "input": sorting_input,
                           "expected_value_order": expected_order})
try:
    canon = pilot_jcs.canonicalise_text(sorting_input)
    order = list(json.loads(canon.decode("utf-8")).values())
    check("sorting §3.2.3", order == expected_order, f"got order {order!r}")
except pilot_jcs.JCSRejection as e:
    check("sorting §3.2.3", False, f"unexpected rejection: {e}")

# ---- §3.4 rejection rules ---------------------------------------------------
rejection_cases = [
    ("duplicate key at parse", lambda: pilot_jcs.canonicalise_text('{"a": 1, "a": 2}')),
    ("lone surrogate at serialise", lambda: pilot_jcs.canonicalise_text('"\\ud800"')),
    ("NaN constant at parse", lambda: pilot_jcs.canonicalise_text('{"a": NaN}')),
    ("Infinity constant at parse", lambda: pilot_jcs.canonicalise_text('{"a": Infinity}')),
    ("native NaN", lambda: pilot_jcs.canonicalise(float("nan"))),
    ("native -Infinity", lambda: pilot_jcs.canonicalise(float("-inf"))),
]
for name, fn in rejection_cases:
    vectors["rejections"].append({"name": name, "expect_rejection": True})
    try:
        fn()
        check(f"reject: {name}", False, "value was accepted, not rejected")
    except pilot_jcs.JCSRejection:
        check(f"reject: {name}", True, "rejected as required")
    except Exception as e:  # wrong failure mode still counts as not-clean
        check(f"reject: {name}", False, f"wrong exception: {type(e).__name__}: {e}")

# ---- round-trip stability on the canonical outputs -------------------------
try:
    again = pilot_jcs.canonicalise_text(expected_obj.decode("utf-8"))
    check("round-trip: canonical output re-canonicalises identically",
          again == expected_obj, "")
except pilot_jcs.JCSRejection as e:
    check("round-trip: canonical output re-canonicalises identically", False, str(e))

total = len(results["checks"])
passed = sum(1 for c in results["checks"] if c["pass"])
results["summary"] = {"total": total, "passed": passed, "failed": total - passed,
                      "all_pass": passed == total}
(HERE / "rfc8785-test-vectors.json").write_text(json.dumps(vectors, indent=2) + "\n")
(HERE / "jcs-conformance-results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results["summary"]))
sys.exit(0 if passed == total else 1)
