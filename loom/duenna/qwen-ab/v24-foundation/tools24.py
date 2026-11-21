#!/usr/bin/env python3
"""ARM C TOOLS v2.4 — single correction per Alex's ruling
(pb-20261110-battery-voided-report response): locate() now
populates embed_text in the search records bm25_search
requires (the defect that stopped the voided battery at
T01 Arm C). No other change from v2.3. v2–v2.3 preserved.

Inherited header (v2.3): mandatory evidence provenance per
Alex's review (pb-20261110-v22-review-findings). v2, v2.1
and v2.2 preserved unchanged.

V2.3 correction against v2.2: for source_extract and
extract_line results, ALL provenance fields are mandatory
at insert — source_ref, source_hash, result_digest,
evidence_line, evidence_line_no, value_offsets. Missing or
null fields are rejected at the provenance-completeness
check, BEFORE re-derivation; _rederive no longer treats
absent evidence as optional (the conditional comparisons
that allowed a strip-and-recompute bypass are gone).

Inherited from v2.2:
1. The result digest now covers the evidence line itself
   (v2.1 covered only its number), and re-derivation compares
   the evidence line AND its line number against the fresh
   result — an altered evidence line can no longer pass.
2. Re-derivation now compares the fresh SOURCE HASH against
   the extraction's recorded source hash — a recomputed
   digest no longer establishes source identity by itself.
3. extract_line computes offsets from the actual line
   position while iterating (cumulative), not by searching
   the text again — no first-occurrence ambiguity when
   identical lines occur more than once.
The digest payload key list is a single constant
(DIGEST_KEYS) shared by issue, insert and the fixtures, so
the three can never drift apart again — that drift is what
produced gap 1.

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

DIGEST_KEYS = ("tool", "source_ref", "source_hash", "value",
               "verification", "extract_field", "evidence_line",
               "evidence_line_no", "value_offsets")

def _finish(r):
    payload = {k: r.get(k) for k in DIGEST_KEYS}
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
    pos = 0
    for i, line in enumerate(text.split("\n")):
        if anchor in line:
            return _finish({**r, "source_hash": look["source_hash"],
                            "value": line.strip(),
                            "verification": "EXTRACTED",
                            "evidence_line": line.strip(),
                            "evidence_line_no": i,
                            "value_offsets": [pos, pos + len(line)],
                            "failure_reason": None})
        pos += len(line) + 1
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
    if fresh["source_hash"] != extraction["source_hash"]:
        return False, ("source hash differs from the source actually "
                       f"retrieved: recorded {extraction['source_hash']!r}, "
                       f"retrieved {fresh['source_hash']!r}")
    if fresh["verification"] != extraction["verification"]:
        return False, "re-derived verification differs"
    if fresh["value"] != extraction["value"]:
        return False, ("re-derived value differs: "
                       f"{fresh['value']!r} != {extraction['value']!r}")
    if extraction.get("value_offsets") is not None and \
            fresh.get("value_offsets") != extraction["value_offsets"]:
        return False, "re-derived offsets differ"
    if extraction.get("tool") in ("source_extract", "extract_line"):
        # Evidence provenance is mandatory for these tools
        # (v2.3): absence is a failure, never a skipped check.
        if extraction.get("evidence_line") is None or \
                extraction.get("evidence_line_no") is None:
            return False, "missing evidence provenance in extraction"
        if fresh.get("evidence_line") != extraction["evidence_line"]:
            return False, ("evidence line differs from the retrieved source: "
                           f"recorded {extraction['evidence_line']!r}, "
                           f"retrieved {fresh.get('evidence_line')!r}")
        if fresh.get("evidence_line_no") != extraction["evidence_line_no"]:
            return False, ("evidence line number differs: recorded "
                           f"{extraction['evidence_line_no']}, retrieved "
                           f"{fresh.get('evidence_line_no')}")
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
    # (a) provenance completeness — for extraction tools the
    # evidence fields are mandatory too (v2.3). Missing or
    # null is rejected here, before any re-derivation.
    missing = [k for k in ("source_ref", "source_hash", "result_digest")
               if extraction.get(k) is None]
    if extraction.get("tool") in ("source_extract", "extract_line"):
        missing += [k for k in ("evidence_line", "evidence_line_no",
                                "value_offsets")
                    if extraction.get(k) is None]
    if missing:
        return None, entry("FAIL", "provenance_check",
                           "missing provenance: " + ", ".join(missing))
    # (b) digest integrity
    payload = {k: extraction.get(k) for k in DIGEST_KEYS}
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
             "embed_text": t,
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
