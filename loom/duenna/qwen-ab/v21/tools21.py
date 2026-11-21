#!/usr/bin/env python3
"""ARM C TOOLS v2.1 — hardened per Alex's review (pb-mwbjzt5r).

Corrections against v2 (tools.py, preserved unchanged):
1. Extraction provenance repaired: every extraction carries its
   evidence line number and character offsets in the source.
2. No manufactured values: demo and trees obtain every value
   through these tools (lookups, extractors, cite).
3. reference_insert is hardened: it (a) refuses results with
   missing provenance, (b) recomputes the result digest to
   catch alteration, and (c) RE-DERIVES the value from the
   source and compares — the source, not the result, is the
   authority, so even a digest-recomputed forgery fails.
   (The digest is not a secret; re-derivation is the defence.)
4. Every process-tree [TOOL] step maps to a function here (or
   to run_ab.check_schema, the v1 diagnostic, named as such).
5. Unsupported operations return a structured UNSUPPORTED
   result via call(); unknown extractors return NOT FOUND.

Every call appends its structured result to CALL_LOG.
Result shape: {operation_id, tool, source_ref, source_hash,
value, verification, failure_reason, result_digest, ...}.
"""
import hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(pathlib.Path.home() / "workspace/pulse-bridge/index"))
import run_ab  # noqa: E402
from query import bm25_search  # noqa: E402

BY_ID = run_ab.BY_ID
MANIFEST_MD = pathlib.Path.home() / "workspace/ainternet-shelf/MANIFEST.md"
CALL_LOG = []
_op = [0]

def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def _digest(payload):
    return _sha(json.dumps(payload, sort_keys=True, default=str))

def _finish(r):
    payload = {k: r.get(k) for k in
               ("tool", "source_ref", "source_hash", "value",
                "verification", "extract_field", "evidence_line_no",
                "value_offsets")}
    r["result_digest"] = _digest(payload)
    CALL_LOG.append(r)
    return r

def _base(tool, source_ref):
    _op[0] += 1
    return {"operation_id": f"op-{_op[0]:03d}", "tool": tool,
            "source_ref": source_ref}

# ------------------------------------------------------------------ tools
def shelf_lookup(source_ref):
    r = _base("shelf_lookup", source_ref)
    if source_ref.startswith("shelf-manifest:"):
        path = source_ref.split(":", 1)[1]
        text = MANIFEST_MD.read_text()
        for line in text.split("\n"):
            if f"`{path}`" in line:
                m = re.search(r"\|\s*([0-9a-f]{64})\s*\|", line)
                return _finish({**r, "source_hash": _sha(text),
                                "value": {"path": path,
                                          "file_name": path.split("/")[-1],
                                          "stated_sha256": m.group(1) if m else None,
                                          "row": line.strip()},
                                "verification": "FOUND",
                                "failure_reason": None})
        return _finish({**r, "source_hash": _sha(text), "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": f"no manifest row for {path}"})
    s = BY_ID.get(source_ref)
    if s is None:
        return _finish({**r, "source_hash": None, "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": f"no such section: {source_ref}"})
    return _finish({**r, "source_hash": s["sha256"], "value": s["text"],
                    "verification": "FOUND", "failure_reason": None})

_EXTRACTORS = {
    "fixtures_executed": (r"(\d+) fixtures executed", int),
    "fixtures_passed": (r"(\d+) PASS", int),
    "harness_sha256": (r"Harness sha256\s+\*\*([0-9a-f]{64})\*\*", str),
    "results_sha256": (r"results sha256\s+\*\*([0-9a-f]{64})\*\*", str),
    "version": (r"Implemented as harness \*\*(v[\d.]+)\*\*", str),
    "correction_b_status": (r"Correction B — (OPEN|CLOSED)", str),
}

def source_extract(source_ref, field):
    r = _base("source_extract", source_ref)
    r["extract_field"] = field
    if field not in _EXTRACTORS:
        return _finish({**r, "source_hash": None, "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": f"unsupported extractor: {field}"})
    look = shelf_lookup(source_ref)
    if look["verification"] != "FOUND":
        return _finish({**r, "source_hash": None, "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": look["failure_reason"]})
    text = look["value"]
    pat, conv = _EXTRACTORS[field]
    m = re.search(pat, text)
    if not m:
        return _finish({**r, "source_hash": look["source_hash"],
                        "value": None, "verification": "NOT FOUND",
                        "failure_reason": f"extractor {field} found no match"})
    a, b = m.span(1)
    line_no = text.count("\n", 0, a)
    line = text.split("\n")[line_no]
    return _finish({**r, "source_hash": look["source_hash"],
                    "value": conv(m.group(1)), "verification": "EXTRACTED",
                    "evidence_line": line.strip(),
                    "evidence_line_no": line_no,
                    "value_offsets": [a, b], "failure_reason": None})

def extract_line(source_ref, anchor):
    """Return the first full line of the source containing anchor,
    with its line number and offsets (claim extraction for T02)."""
    r = _base("extract_line", source_ref)
    r["extract_field"] = "line:" + anchor
    look = shelf_lookup(source_ref)
    if look["verification"] != "FOUND":
        return _finish({**r, "source_hash": None, "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": look["failure_reason"]})
    text = look["value"]
    for i, line in enumerate(text.split("\n")):
        if anchor in line:
            a = text.find(line)
            return _finish({**r, "source_hash": look["source_hash"],
                            "value": line.strip(),
                            "verification": "EXTRACTED",
                            "evidence_line": line.strip(),
                            "evidence_line_no": i,
                            "value_offsets": [a, a + len(line)],
                            "failure_reason": None})
    return _finish({**r, "source_hash": look["source_hash"], "value": None,
                    "verification": "NOT FOUND",
                    "failure_reason": f"anchor not found: {anchor}"})

def cite(source_ref):
    """A lookup-kind result whose value is the citation itself —
    how evidence fields are populated without manufacturing."""
    r = _base("cite", source_ref)
    look = shelf_lookup(source_ref)
    if look["verification"] != "FOUND":
        return _finish({**r, "source_hash": None, "value": None,
                        "verification": "NOT FOUND",
                        "failure_reason": look["failure_reason"]})
    return _finish({**r, "source_hash": look["source_hash"],
                    "value": [source_ref], "verification": "FOUND",
                    "failure_reason": None})

def _rederive(extraction):
    """Re-run the issuing operation and compare. Returns
    (ok, reason). The fresh result is the authority."""
    tool = extraction.get("tool")
    if tool == "source_extract":
        fresh = source_extract(extraction["source_ref"],
                               extraction["extract_field"])
    elif tool == "extract_line":
        fresh = extract_line(extraction["source_ref"],
                             extraction["extract_field"][5:])
    elif tool == "shelf_lookup":
        fresh = shelf_lookup(extraction["source_ref"])
    elif tool == "cite":
        fresh = cite(extraction["source_ref"])
    else:
        return False, f"cannot re-derive result of tool {tool!r}"
    if fresh["verification"] != extraction["verification"]:
        return False, "re-derived verification differs"
    if fresh["value"] != extraction["value"]:
        return False, ("re-derived value differs: "
                       f"{fresh['value']!r} != {extraction['value']!r}")
    if extraction.get("value_offsets") is not None and \
            fresh.get("value_offsets") != extraction["value_offsets"]:
        return False, "re-derived offsets differ"
    return True, "re-derived from source"

def reference_insert(field, process_step, extraction, select=None):
    """Populate a field from a tool result, hardened (header §3).
    Returns (value, ledger_entry); value is None on failure."""
    def entry(verification, method, reason, value=None):
        return {"field": field, "value": value,
                "process_step": process_step,
                "source_ref": extraction.get("source_ref"),
                "source_hash": extraction.get("source_hash"),
                "operation": "reference_insert",
                "verification": verification,
                "verification_method": method,
                "failure_reason": reason}
    # (a) provenance completeness
    missing = [k for k in ("source_ref", "source_hash", "result_digest")
               if not extraction.get(k)]
    if extraction.get("tool") in ("source_extract", "extract_line") and \
            extraction.get("value_offsets") is None:
        missing.append("value_offsets")
    if missing:
        return None, entry("FAIL", "provenance_check",
                           "missing provenance: " + ", ".join(missing))
    # (b) digest integrity
    payload = {k: extraction.get(k) for k in
               ("tool", "source_ref", "source_hash", "value",
                "verification", "extract_field", "evidence_line_no",
                "value_offsets")}
    if _digest(payload) != extraction["result_digest"]:
        return None, entry("FAIL", "digest_check",
                           "result digest mismatch — result altered after issue")
    # (c) re-derivation from the source
    ok, reason = _rederive(extraction)
    if not ok:
        return None, entry("FAIL", "rederivation", reason)
    value = extraction["value"]
    if select is not None:
        if not isinstance(value, dict) or select not in value:
            return None, entry("FAIL", "selection",
                               f"no key {select!r} in result value")
        value = value[select]
    return value, entry("PASS", "digest+rederivation", None, value)

def verify_field(field, value, expected, method="source_equality"):
    r = _base("verify_field", field)
    ok = value == expected
    return _finish({**r, "source_hash": None,
                    "value": {"field": field, "value": value,
                              "expected": expected},
                    "verification": "PASS" if ok else "FAIL",
                    "verification_method": method,
                    "failure_reason": None if ok else
                    f"{field}: got {value!r}, expected {expected!r}"})

def receipt_worksheet(obligation, receipt):
    r = _base("receipt_worksheet", "obligation-spec")
    rows = []
    for f in obligation["required_fields"]:
        present = f in receipt
        rows.append({"requirement": f"field present: {f}",
                     "receipt_value": receipt.get(f), "pass": present,
                     "reason": None if present else "required field absent"})
    hm = receipt.get("sha256") == obligation["sha256"]
    rows.append({"requirement": "sha256 equals the obligation hash",
                 "receipt_value": receipt.get("sha256"), "pass": hm,
                 "reason": "hash match" if hm else "hash mismatch"})
    rc = obligation["result_contains"] in str(receipt.get("result", ""))
    rows.append({"requirement": "result reports the required evidence",
                 "receipt_value": receipt.get("result"), "pass": rc,
                 "reason": "required evidence reported" if rc
                           else "required evidence not reported"})
    sc = receipt.get("evidence_status") == obligation["evidence_status"]
    rows.append({"requirement": "evidence_status exactly [verified]",
                 "receipt_value": receipt.get("evidence_status"),
                 "pass": sc,
                 "reason": "status class exact" if sc else
                 f"status is {receipt.get('evidence_status')!r}, required [verified]"})
    decision = "CLOSE" if all(x["pass"] for x in rows) else "REJECT"
    return _finish({**r,
                    "source_hash": _sha(json.dumps(obligation, sort_keys=True)),
                    "value": {"rows": rows, "decision": decision,
                              "obligation_state": "CLOSED" if decision == "CLOSE" else "OPEN"},
                    "verification": "PASS" if decision == "CLOSE" else "FAIL",
                    "failure_reason": None if decision == "CLOSE" else
                    "; ".join(x["requirement"] for x in rows if not x["pass"])})

# ------------------------------------------- driver-level operations
def pack_search(pack_items, term):
    """Deterministic full-text scan of pack items (T01 absence
    check, T03 support). Returns every hit with its line."""
    r = _base("pack_search", term)
    hits = []
    for item_id, text in pack_items:
        for i, line in enumerate(text.split("\n")):
            if term in line:
                hits.append({"item": item_id, "line_no": i,
                             "line": line.strip()[:160]})
    return _finish({**r, "source_hash": None,
                    "value": {"term": term, "hit_count": len(hits),
                              "hits": hits},
                    "verification": "FOUND" if hits else "NOT FOUND",
                    "failure_reason": None if hits else
                    f"no occurrence of {term!r} in the pack"})

def locate(pack_items, query_text, k=2):
    """Deterministic retrieval over pack items only (T01 locate)
    — the query.py BM25 ranker, pack-restricted."""
    r = _base("locate", query_text)
    secs = [{"section_id": i, "doc": "pack", "text": t,
             "heading_path": "", "sha256": _sha(t)} for i, t in pack_items]
    hits = bm25_search(secs, query_text, k)
    return _finish({**r, "source_hash": None,
                    "value": [s["section_id"] for _sc, s in hits],
                    "verification": "FOUND" if hits else "NOT FOUND",
                    "failure_reason": None if hits else "no pack item ranked"})

def classify_item(item_id, item_text):
    """Parse a pack item's provenance header (T03 classify)."""
    r = _base("classify_item", item_id)
    head = item_text.split("\n", 1)[0]
    if head.startswith("=== SECTION"):
        kind = "record section"
    elif "FIXTURE" in head:
        kind = "authored fixture"
    else:
        kind = "unclassified"
    return _finish({**r, "source_hash": _sha(item_text),
                    "value": {"item": item_id, "kind": kind,
                              "header": head[:120]},
                    "verification": "FOUND" if kind != "unclassified" else "NOT FOUND",
                    "failure_reason": None if kind != "unclassified" else
                    "no provenance header recognised"})

def parse_obligations(register_text):
    """Parse the T07 register fixture into worksheet rows. The
    fixture format is fixed; parsing is deterministic."""
    r = _base("parse_obligations", "obligation-register")
    rows = []
    blocks = re.split(r"\n(?=OB-\d+ — )", register_text)
    for b in blocks:
        m = re.match(r"(OB-\d+) — (.+)", b)
        if not m:
            continue
        cond = ""
        cm = re.search(r"Completion condition: (.+)", b)
        if cm:
            cond = cm.group(1).strip()
        rows.append({"id": m.group(1), "name": m.group(2).strip(),
                     "completion_condition": cond})
    return _finish({**r, "source_hash": _sha(register_text),
                    "value": rows,
                    "verification": "FOUND" if rows else "NOT FOUND",
                    "failure_reason": None if rows else "no obligations parsed"})

def load_contract():
    r = _base("load_contract", "t05-task-contract")
    return _finish({**r, "source_hash": _sha(json.dumps(run_ab.EXPECTED_RECORD, sort_keys=True)),
                    "value": {"fields": list(run_ab.EXPECTED_RECORD) + ["evidence"],
                              "enums": {"correction_b": ["OPEN", "CLOSED"]}},
                    "verification": "FOUND", "failure_reason": None})

def load_obligation_spec():
    r = _base("load_obligation_spec", "obligation-spec")
    spec = dict(run_ab.OBLIGATION_T09)
    return _finish({**r, "source_hash": _sha(json.dumps(spec, sort_keys=True)),
                    "value": spec, "verification": "FOUND",
                    "failure_reason": None})

def load_boundaries():
    """The T04 boundary table, fixed in the harness and quoted
    from the arm instruction texts (its provenance is their
    hash). Behavioural step — see the tree's note."""
    r = _base("load_boundaries", "arm-instructions")
    table = {"permitted": ["retrieve", "extract", "answer", "escalate"],
             "not_permitted": ["approve", "close", "publish",
                               "execute externally"]}
    return _finish({**r, "source_hash": _sha(run_ab.ARM_B_SYSTEM),
                    "value": table, "verification": "FOUND",
                    "failure_reason": None})

_DISPATCH = {"shelf_lookup": shelf_lookup, "source_extract": source_extract,
             "extract_line": extract_line, "cite": cite,
             "verify_field": verify_field,
             "receipt_worksheet": receipt_worksheet,
             "pack_search": pack_search, "locate": locate,
             "classify_item": classify_item,
             "parse_obligations": parse_obligations,
             "load_contract": load_contract,
             "load_obligation_spec": load_obligation_spec,
             "load_boundaries": load_boundaries}

def call(op, **kwargs):
    """Dispatch an operation by name. Unknown operations return
    a structured UNSUPPORTED result — never a substitution."""
    if op not in _DISPATCH:
        _op[0] += 1
        return {"operation_id": f"op-{_op[0]:03d}", "tool": op,
                "source_ref": None, "source_hash": None, "value": None,
                "verification": "UNSUPPORTED",
                "failure_reason": f"operation not implemented: {op}"}
    return _DISPATCH[op](**kwargs)
