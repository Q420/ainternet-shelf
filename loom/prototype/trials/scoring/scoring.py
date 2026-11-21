#!/usr/bin/env python3
"""Scoring support (Rev 4 SS7/SS7A). Generates BLINDED scoring sheets:
candidate identity and trial order are hidden; sheets carry a blind reference
only, and the blind->candidate mapping is written to a separate file that is
joined only after scoring completes. Remmy's mechanical pre-checks for
criteria 2 and 3 are computed here, each with an evidence pointer; they are
mechanical records, not verdicts. The trial-level verdict follows SS7: a
response counts adequate only if it is schema-valid AND at least 4 of 5
criteria are met (the schema-validity gate sits above the criterion count)."""
import hashlib, json

def precheck_criterion_2(resp):
    """Mechanical: do the operations satisfy the per-class scope rules?
    (This tooling's own implementation, for the pre-check only.)"""
    if not isinstance(resp, dict) or resp.get("action") != "contribute":
        return {"result": "not_met", "evidence": "no parseable contribution: no extractable operations"}
    c = resp["contribution"]
    read, write = set(c.get("read_set", [])), set(c.get("write_set", []))
    ops = c.get("operations", [])
    if not ops:
        return {"result": "not_met", "evidence": "operations: empty"}
    seen_content = set()
    for i, op in enumerate(ops):
        k = op.get("kind")
        if k in ("replace_content", "append_content"):
            if op.get("region_id") not in write:
                return {"result": "not_met", "evidence": f"operations[{i}].region_id not in write_set"}
            if op["region_id"] in seen_content:
                return {"result": "not_met", "evidence": f"operations[{i}]: second content op on {op['region_id']}"}
            seen_content.add(op["region_id"])
        elif k == "add_dependency":
            d = op.get("dependency", {})
            if not {d.get("source"), d.get("target")} <= (read & write):
                return {"result": "not_met", "evidence": f"operations[{i}].dependency endpoints not in read_set and write_set"}
            if (d.get("source"), d.get("target"), d.get("kind")) == ("alpha", "beta", "uses"):
                return {"result": "not_met", "evidence": f"operations[{i}]: duplicates the active dependency"}
        elif k == "remove_dependency":
            return {"result": "not_met", "evidence": f"operations[{i}]: remove_dependency cannot be grounded (no dependency identity in the instrument)"}
        elif k == "raise_tension":
            t = op.get("tension", {})
            if not set(t.get("regions", [])) <= read:
                return {"result": "not_met", "evidence": f"operations[{i}].tension.regions not in read_set"}
            if t.get("type") != "semantic":
                return {"result": "not_met", "evidence": f"operations[{i}].tension.type is not semantic"}
    return {"result": "met", "evidence": "operations[0..%d] satisfy the per-class scope rules" % (len(ops) - 1)}

def precheck_criterion_3(resp):
    """Mechanical: base_versions gives alpha = 3 and beta = 1 (Annex C)."""
    if not isinstance(resp, dict) or resp.get("action") != "contribute":
        return {"result": "not_met", "evidence": "no parseable contribution: no extractable base_versions"}
    bv = resp.get("contribution", {}).get("base_versions")
    if bv is None:
        return {"result": "not_met", "evidence": "base_versions absent"}
    ok = bv.get("alpha") == 3 and bv.get("beta") == 1
    return {"result": "met" if ok else "not_met",
            "evidence": "base_versions = %s" % json.dumps(bv, sort_keys=True)}

def blind_id(round_secret, trial_uid):
    return "blind-" + hashlib.sha256((round_secret + "|" + trial_uid).encode()).hexdigest()[:12]

def make_sheet(record, round_secret):
    """record: {trial_uid, raw_response_text, parsed (or None), schema_valid}"""
    parsed = record.get("parsed")
    return {
        "blind_ref": blind_id(round_secret, record["trial_uid"]),
        "schema_valid": record["schema_valid"],
        "criteria": {
            "1": {"result": None, "evidence": None, "scored_by": "examiner"},
            "2": {"result": None, "evidence": None, "scored_by": "examiner",
                  "precheck": precheck_criterion_2(parsed)},
            "3": {"result": None, "evidence": None, "scored_by": "examiner",
                  "precheck": precheck_criterion_3(parsed)},
            "4": {"result": None, "evidence": None, "scored_by": "examiner"},
            "5": {"result": None, "evidence": None, "scored_by": "examiner"},
        },
        "prechecks_confirmed_or_overridden": None,
        "scorer": None,
        "adequacy_verdict": None,
    }

def compute_verdict(schema_valid, criteria_results):
    """SS7: the schema-validity gate sits above the >=4-of-5 count."""
    met = sum(1 for r in criteria_results.values() if r == "met")
    if not schema_valid:
        return {"adequate": False, "ground": "schema-invalid gate (Rev 9 SS1: malformed outputs fail both rates)",
                "criteria_met": met}
    if met >= 4:
        return {"adequate": True, "ground": "schema-valid and %d of 5 criteria met" % met, "criteria_met": met}
    return {"adequate": False, "ground": "criterion count %d of 5 below the bar of 4" % met, "criteria_met": met}
