#!/usr/bin/env python3
"""Validator 1 (Python lineage): jsonschema Draft 2020-12 + format assertion,
implementing the Annex A gate-schema contract and the Rev 4 SS4 gate-validation
profile (cross-field rules) independently. Operates on the RAW response text:
no normalization, completion, or repair precedes validation.

Usage: validate_py.py <response-file>   -> prints one JSON verdict line.
"""
import json
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

HERE = __file__.rsplit("/", 1)[0]
SCHEMA = json.load(open(HERE + "/../instruments/gate_schema.json"))

checker = FormatChecker()
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@checker.checks("uuid", raises=ValueError)
def _uuid_format(value):
    # Annex P defines the UUID form: five hyphen-separated hex groups
    # (8-4-4-4-12). Non-hyphenated or braced forms are not that form.
    if not isinstance(value, str):
        return True  # type errors are the schema's, not the format's
    if not UUID_RE.match(value):
        raise ValueError("not a hyphenated UUID")
    return True


REGIONS = {"alpha", "beta"}
ACTIVE_DEPENDENCIES = {("alpha", "beta", "uses")}  # the one Annex A displays


def cross_field_errors(c):
    """Rev 4 SS4 profile: rules (i)-(iv) applied; (v) not applied (no
    authenticated identity); (vi) verification not applied (no DISCOVERY
    event). Returns a list of profile error strings."""
    errs = []
    read = c["read_set"]
    write = c["write_set"]
    read_s, write_s = set(read), set(write)
    # (i) write subset of read
    if not write_s <= read_s:
        errs.append("(i) write_set not a subset of read_set")
    # (ii) base_versions keys exactly read_set
    if set(c["base_versions"].keys()) != read_s:
        errs.append("(ii) base_versions keys != read_set")
    # (iv) every region id anywhere in the frozen set (schema enum covers most
    # positions; base_versions keys are covered here)
    for k in c["base_versions"].keys():
        if k not in REGIONS:
            errs.append("(iv) base_versions key outside frozen set: %r" % k)
    content_ops_per_region = {}
    for op in c["operations"]:
        kind = op["kind"]
        if kind in ("replace_content", "append_content"):
            rid = op["region_id"]
            if rid not in write_s:
                errs.append("(iii) content op region %r not in write_set" % rid)
            content_ops_per_region[rid] = content_ops_per_region.get(rid, 0) + 1
            if content_ops_per_region[rid] > 1:
                errs.append("(iii) more than one content op on region %r" % rid)
        elif kind == "add_dependency":
            d = op["dependency"]
            for ep in (d["source"], d["target"]):
                if ep not in read_s or ep not in write_s:
                    errs.append("(iii) add_dependency endpoint %r not in read_set and write_set" % ep)
            if (d["source"], d["target"], d["kind"]) in ACTIVE_DEPENDENCIES:
                errs.append("(iii) add_dependency duplicates the active dependency")
        elif kind == "remove_dependency":
            # Dependency-identity edge (Rev 4 SS4): Annex A supplies no
            # dependency identity, so this operation cannot pass the scope
            # check in a gate trial. No identity is invented.
            errs.append("(iii) remove_dependency cannot be grounded: the instrument supplies no dependency identity")
        elif kind == "raise_tension":
            for r in op["tension"]["regions"]:
                if r not in read_s:
                    errs.append("(iii) raise_tension region %r not in read_set" % r)
    return errs


def validate(raw_text):
    try:
        doc = json.loads(raw_text)
    except Exception:
        return {"valid": False, "schema_errors": ["response is not a single JSON value"], "profile_errors": []}
    if not isinstance(doc, dict):
        return {"valid": False, "schema_errors": ["response is not a JSON object"], "profile_errors": []}
    v = Draft202012Validator(SCHEMA, format_checker=checker)
    schema_errors = sorted(e.message for e in v.iter_errors(doc))
    profile_errors = []
    if not schema_errors and doc.get("action") == "contribute":
        profile_errors = cross_field_errors(doc["contribution"])
    return {
        "valid": not schema_errors and not profile_errors,
        "schema_errors": schema_errors,
        "profile_errors": profile_errors,
    }


if __name__ == "__main__":
    raw = open(sys.argv[1], "rb").read().decode("utf-8", errors="replace")
    print(json.dumps(validate(raw)))
