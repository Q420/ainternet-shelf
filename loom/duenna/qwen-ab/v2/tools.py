#!/usr/bin/env python3
"""ARM C TOOLS — Qwen + Process trial (design: Alex pb-mwbjmwcc).

Five deterministic tools. Every call returns a structured result:
{operation_id, tool, source_ref, source_hash, value, verification,
failure_reason}. The tools operate on the frozen v1 packs/corpus
and the shelf manifest. They never invent a value: an extraction
that cannot be made returns verification NOT FOUND with a reason.

The worker (Qwen) consumes tool results; it does not recreate
their contents. reference_insert copies a verified value
byte-exactly from its tool result into a record field and emits
the accountability-ledger entry for that field.
"""
import hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import run_ab  # noqa: E402  (frozen packs, corpus, receipts, specs)

BY_ID = run_ab.BY_ID
MANIFEST_MD = pathlib.Path.home() / "workspace/ainternet-shelf/MANIFEST.md"
_op_counter = [0]

def _op(tool):
    _op_counter[0] += 1
    return {"operation_id": f"op-{_op_counter[0]:03d}", "tool": tool}

def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

# ---------------------------------------------------------------- tools
def shelf_lookup(source_ref):
    """Retrieve a designated source: a corpus section by id, or the
    shelf-manifest row for a shelved path."""
    r = _op("shelf_lookup")
    if source_ref.startswith("shelf-manifest:"):
        path = source_ref.split(":", 1)[1]
        text = MANIFEST_MD.read_text()
        for line in text.split("\n"):
            if f"`{path}`" in line:
                m = re.search(r"\|\s*([0-9a-f]{64})\s*\|", line)
                return {**r, "source_ref": source_ref,
                        "source_hash": _sha(text),
                        "value": {"path": path,
                                  "stated_sha256": m.group(1) if m else None,
                                  "row": line.strip()},
                        "verification": "FOUND", "failure_reason": None}
        return {**r, "source_ref": source_ref, "source_hash": _sha(text),
                "value": None, "verification": "NOT FOUND",
                "failure_reason": f"no manifest row for {path}"}
    s = BY_ID.get(source_ref)
    if s is None:
        return {**r, "source_ref": source_ref, "source_hash": None,
                "value": None, "verification": "NOT FOUND",
                "failure_reason": f"no such section: {source_ref}"}
    return {**r, "source_ref": source_ref, "source_hash": s["sha256"],
            "value": s["text"], "verification": "FOUND",
            "failure_reason": None}

_EXTRACTORS = {
    "fixtures_executed": (r"(\d+) fixtures executed", int),
    "fixtures_passed": (r"(\d+) PASS", int),
    "harness_sha256": (r"Harness sha256\s+\*\*([0-9a-f]{64})\*\*", str),
    "results_sha256": (r"results sha256\s+\*\*([0-9a-f]{64})\*\*", str),
}

def source_extract(source_ref, field):
    """Extract one canonical value from a source record by a named,
    deterministic extraction rule."""
    r = _op("source_extract")
    look = shelf_lookup(source_ref)
    if look["verification"] != "FOUND":
        return {**r, "source_ref": source_ref, "source_hash": None,
                "value": None, "verification": "NOT FOUND",
                "failure_reason": look["failure_reason"]}
    text = look["value"]
    pat, conv = _EXTRACTORS[field]
    m = re.search(pat, text)
    if not m:
        return {**r, "source_ref": source_ref,
                "source_hash": look["source_hash"], "value": None,
                "verification": "NOT FOUND",
                "failure_reason": f"extractor {field} found no match"}
    line = next((l for l in text.split("\n") if m.group(0) in l), "")
    return {**r, "source_ref": source_ref,
            "source_hash": look["source_hash"], "value": conv(m.group(1)),
            "verification": "EXTRACTED", "evidence_line": line.strip(),
            "failure_reason": None}

def reference_insert(field, process_step, extraction):
    """Populate a record field from a verified extraction result.
    The value is copied from the tool result, never retyped.
    Returns (value, ledger_entry)."""
    ok = extraction["verification"] in ("EXTRACTED", "FOUND")
    entry = {"field": field, "value": extraction["value"],
             "process_step": process_step,
             "source_ref": extraction["source_ref"],
             "source_hash": extraction["source_hash"],
             "operation": "reference_insert",
             "verification": "PASS" if ok else "FAIL",
             "verification_method": "tool_result_reference"}
    return extraction["value"], entry

def verify_field(field, value, expected, method="source_equality"):
    """Check one value against its source or contract."""
    r = _op("verify_field")
    ok = value == expected
    return {**r, "source_ref": field, "source_hash": None,
            "value": {"field": field, "value": value, "expected": expected},
            "verification": "PASS" if ok else "FAIL",
            "verification_method": method,
            "failure_reason": None if ok else
            f"{field}: got {value!r}, expected {expected!r}"}

def receipt_worksheet(obligation, receipt):
    """Compare a submitted receipt against the obligation's
    requirements, one row per requirement. The worksheet — not
    the model — produces the closure decision."""
    r = _op("receipt_worksheet")
    rows = []
    for f in obligation["required_fields"]:
        present = f in receipt
        rows.append({"requirement": f"field present: {f}",
                     "receipt_value": receipt.get(f), "pass": present,
                     "reason": None if present else "required field absent"})
    rows.append({"requirement": "sha256 equals the obligation hash",
                 "receipt_value": receipt.get("sha256"),
                 "pass": receipt.get("sha256") == obligation["sha256"],
                 "reason": "hash match" if receipt.get("sha256") == obligation["sha256"]
                           else "hash mismatch"})
    rows.append({"requirement": "result reports the required evidence",
                 "receipt_value": receipt.get("result"),
                 "pass": obligation["result_contains"] in str(receipt.get("result", "")),
                 "reason": "required evidence reported" if obligation["result_contains"] in str(receipt.get("result", ""))
                           else "required evidence not reported"})
    rows.append({"requirement": "evidence_status exactly [verified]",
                 "receipt_value": receipt.get("evidence_status"),
                 "pass": receipt.get("evidence_status") == obligation["evidence_status"],
                 "reason": "status class exact" if receipt.get("evidence_status") == obligation["evidence_status"]
                           else f"status is {receipt.get('evidence_status')!r}, required [verified]"})
    decision = "CLOSE" if all(x["pass"] for x in rows) else "REJECT"
    return {**r, "source_ref": "obligation-spec",
            "source_hash": _sha(json.dumps(obligation, sort_keys=True)),
            "value": {"rows": rows, "decision": decision,
                      "obligation_state": "CLOSED" if decision == "CLOSE" else "OPEN"},
            "verification": "PASS" if decision == "CLOSE" else "FAIL",
            "failure_reason": None if decision == "CLOSE" else
            "; ".join(x["requirement"] for x in rows if not x["pass"])}
