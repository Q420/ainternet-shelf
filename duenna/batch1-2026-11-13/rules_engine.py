#!/usr/bin/env python3
"""Checkpoint test instrument: applies EXTRACTOR-RULES-02 data under
the Harness §3.2 match semantics. This is Batch 1 checkpoint
machinery, NOT the pilot tool — Batch 2 builds source_extract on
the same rules data and the same semantics.

Semantics (Harness §3.2, stated once): find every match of the
rule's pattern in the text; for each match take the rule's group
and test it against value_type. Outcomes:
  no pattern matches            -> NOT FOUND (absence + reason)
  matches, all fail the type    -> TYPE FAILURE (matched text +
                                   expected type recorded, no value)
  exactly one valid match       -> EXTRACTED (value + evidence line)
  more than one valid match     -> AMBIGUOUS (every candidate
                                   recorded, no value)
Mixed valid/invalid: type-failing matches are recorded as rejected
candidates; the count runs over the valid ones. No tie-break of
any kind. A field with no rule is NOT FOUND by declared design.
"""
import re

_TYPES = {
    "integer": (r"[0-9]+", int),
    "hex64": (r"[0-9a-f]{64}", lambda s: s),
    "string": (r".+", lambda s: s),
}


def type_test(value_type, raw):
    pat, conv = _TYPES[value_type]
    if re.fullmatch(pat, raw):
        return True, conv(raw)
    return False, None


def apply_rule(rule, text):
    matches = list(re.finditer(rule["pattern"], text))
    if not matches:
        return {"verification": "NOT FOUND",
                "failure_reason": f"rule {rule['rule_id']} found no match"}
    valid, rejected = [], []
    for m in matches:
        raw = m.group(rule["group"])
        line = next((l.strip() for l in text.split("\n")
                     if m.group(0) in l), "")
        ok, value = type_test(rule["value_type"], raw)
        if ok:
            valid.append({"value": value, "matched": raw,
                          "evidence_line": line})
        else:
            rejected.append({"matched": raw,
                             "expected_type": rule["value_type"],
                             "evidence_line": line})
    if not valid:
        return {"verification": "TYPE FAILURE",
                "matched": [r["matched"] for r in rejected],
                "expected_type": rule["value_type"],
                "rejected_candidates": rejected}
    if len(valid) > 1:
        return {"verification": "AMBIGUOUS", "candidates": valid,
                "rejected_candidates": rejected}
    return {"verification": "EXTRACTED", "value": valid[0]["value"],
            "evidence_line": valid[0]["evidence_line"],
            "rejected_candidates": rejected}


def extract(rules_doc, field, text):
    rule = next((r for r in rules_doc["rules"] if r["field"] == field),
                None)
    if rule is None:
        return {"verification": "NOT FOUND",
                "failure_reason": f"no rule declared for field {field}"}
    return {**apply_rule(rule, text), "rule_id": rule["rule_id"]}
