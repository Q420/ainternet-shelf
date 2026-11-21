#!/usr/bin/env python3
"""Author the validator corpus: one case per retained assertion and per
profile exception in Rev 4 SS4, each with the expected verdict."""
import json, copy

U1 = "550e8400-e29b-41d4-a716-446655440000"
U2 = "550e8400-e29b-41d4-a716-446655440001"
BASE = {"action": "contribute", "contribution": {
    "author": U1, "idempotency_id": U2,
    "base_versions": {"alpha": 3, "beta": 1},
    "read_set": ["alpha", "beta"], "write_set": ["alpha", "beta"],
    "operations": [{"kind": "replace_content", "region_id": "alpha", "new_content": "Revised."}],
    "rationale": "Stateless requests vs pinned sessions must be reconciled.",
    "discovery_source": "fabric_read", "discovery_ref": 1}}

def C(**kw):
    d = copy.deepcopy(BASE)
    for k, v in kw.items():
        if k == "ops": d["contribution"]["operations"] = v
        else: d["contribution"][k] = v
    return json.dumps(d)

cases = []
def add(name, raw, expected, category): cases.append({"name": name, "raw": raw, "expected_valid": expected, "category": category})

add("valid-full-contribution", C(), True, "positive")
add("valid-idle", '{"action":"idle"}', True, "positive")
add("valid-raise-tension-only", C(ops=[{"kind":"raise_tension","tension":{"type":"semantic","regions":["alpha","beta"],"description":"conflict"}}], write_set=[]), True, "positive")
add("valid-add-dependency-nonduplicate", C(ops=[{"kind":"add_dependency","dependency":{"source":"alpha","target":"beta","kind":"constrains"}}]), True, "positive")
add("valid-uppercase-uuid-author", C(author="550E8400-E29B-41D4-A716-446655440000"), True, "uuid-format")
add("invalid-author-not-uuid", C(author="not-a-uuid"), False, "uuid-format")
add("invalid-author-hyphenless", C(author="550e8400e29b41d4a716446655440000"), False, "uuid-format")
add("invalid-author-braced", C(author="{550e8400-e29b-41d4-a716-446655440000}"), False, "uuid-format")
add("invalid-idempotency-not-uuid", C(idempotency_id="abc"), False, "uuid-format")
add("invalid-region-gamma", C(read_set=["alpha","gamma"], base_versions={"alpha":3,"gamma":1}), False, "region-set")
add("invalid-region-uuid-form", C(read_set=["alpha", U1], base_versions={"alpha":3, U1:1}), False, "region-set")
add("invalid-op-region-gamma", C(ops=[{"kind":"append_content","region_id":"gamma","text":"x"}]), False, "region-set")
add("invalid-write-not-subset", C(write_set=["alpha","beta"], read_set=["alpha"], base_versions={"alpha":3}), False, "crossfield-i")
add("invalid-baseversions-missing-key", C(base_versions={"alpha":3}), False, "crossfield-ii")
add("invalid-baseversions-extra-key", C(base_versions={"alpha":3,"beta":1,"gamma":2}), False, "crossfield-ii-iv")
add("invalid-content-op-not-in-write", C(write_set=["beta"], ops=[{"kind":"replace_content","region_id":"alpha","new_content":"x"}]), False, "crossfield-iii")
add("invalid-two-content-ops-same-region", C(ops=[{"kind":"replace_content","region_id":"alpha","new_content":"x"},{"kind":"append_content","region_id":"alpha","text":"y"}]), False, "crossfield-iii")
add("invalid-adddep-endpoint-not-in-write", C(write_set=["alpha"], ops=[{"kind":"add_dependency","dependency":{"source":"alpha","target":"beta","kind":"extends"}}]), False, "crossfield-iii")
add("invalid-adddep-duplicate-active", C(ops=[{"kind":"add_dependency","dependency":{"source":"alpha","target":"beta","kind":"uses"}}]), False, "crossfield-iii")
add("invalid-remove-dependency-edge", C(ops=[{"kind":"remove_dependency","dependency_id":U1}]), False, "dependency-identity-edge")
add("invalid-raisetension-region-not-read", C(read_set=["alpha"], base_versions={"alpha":3}, write_set=[], ops=[{"kind":"raise_tension","tension":{"type":"semantic","regions":["beta"],"description":"d"}}]), False, "crossfield-iii")
add("invalid-discovery-source-enum", C(discovery_source="guessed"), False, "discovery")
add("valid-discovery-source-index-asserted", C(discovery_source="index"), True, "discovery")
add("invalid-discovery-ref-zero", C(discovery_ref=0), False, "discovery")
add("invalid-discovery-ref-float", C(discovery_ref=1.5), False, "discovery")
add("invalid-extra-top-level-field", json.dumps({**json.loads(C()), "extra": 1}), False, "shape")
add("invalid-idle-with-contribution", json.dumps({"action":"idle","contribution":BASE["contribution"]}), False, "shape")
add("invalid-contribute-missing-contribution", '{"action":"contribute"}', False, "shape")
add("invalid-op-wrong-fields", C(ops=[{"kind":"replace_content","region_id":"alpha","text":"x"}]), False, "shape")
add("invalid-tension-type-structural", C(ops=[{"kind":"raise_tension","tension":{"type":"structural","regions":["alpha"],"description":"d"}}]), False, "shape")
add("invalid-operations-empty", C(ops=[]), False, "shape")
add("invalid-read-set-empty", C(read_set=[], base_versions={}), False, "shape")
add("invalid-read-set-duplicates", C(read_set=["alpha","alpha","beta"]), False, "shape")
add("invalid-baseversion-zero", C(base_versions={"alpha":0,"beta":1}), False, "shape")
add("invalid-not-json", "I refuse to answer.", False, "raw")
add("invalid-json-array", '[{"action":"idle"}]', False, "raw")
add("invalid-json-string", '"idle"', False, "raw")
add("invalid-empty", "", False, "raw")
add("invalid-trailing-garbage", '{"action":"idle"} and then some', False, "raw")
add("invalid-missing-author", C(author=None).replace('"author": null, ', '') if False else json.dumps({**BASE, "contribution": {k: v for k, v in BASE["contribution"].items() if k != "author"}}), False, "shape")

json.dump(cases, open("tests/corpus.json", "w"), indent=1)
print(len(cases), "corpus cases")
