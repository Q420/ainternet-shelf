#!/usr/bin/env python3
"""BATCH 1 transcription verification — independent of transcribe.py.

Second path, different mechanisms:
 * CPython's own ast.literal_eval over source spans for the purely
   literal constants (after textual substitution of the two V24 sha
   names) — no shared evaluator code with the transcriber.
 * Structural invariants for the constructed values (the four
   receipts' relations to each other and to the obligation; the
   T09 gate decisions recomputed from the data files).
 * Resolution: every pack section ref exists in the snapshot; every
   pack renders end-to-end in V2's pack_text form from the refs
   alone (sections from the snapshot, fixtures from the data
   files); pack hashes recorded for the re-freeze amendment.
 * Probe substrings: each fixture text carries its distinctive
   content, in the data file and in the pinned source.

Usage: verify_transcription.py <run_ab.py> <snapshot_dir> <data_dir>
Exit 0 iff every check passes.
"""
import ast, hashlib, json, pathlib, re, sys

SRC = pathlib.Path(sys.argv[1]).read_text()
SNAP = pathlib.Path(sys.argv[2])
DATA = pathlib.Path(sys.argv[3])
checks = []
def chk(name, ok, detail=""):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})

V24H = re.search(r'V24_HARNESS_SHA = "([0-9a-f]{64})"', SRC).group(1)
V24R = re.search(r'V24_RESULTS_SHA = "([0-9a-f]{64})"', SRC).group(1)

def span_literal(name):
    m = re.search(rf"^{name} = ", SRC, re.M)
    start = m.end()
    # find the assignment's AST node for its exact span
    for node in ast.parse(SRC).body:
        if isinstance(node, ast.Assign) and \
                getattr(node.targets[0], "id", None) == name:
            seg = ast.get_source_segment(SRC, node.value)
            seg = seg.replace("V24_HARNESS_SHA", f'"{V24H}"') \
                     .replace("V24_RESULTS_SHA", f'"{V24R}"')
            return ast.literal_eval(seg)
    raise KeyError(name)

packs = json.loads((DATA / "PILOT-DATA-PACKS-01.json").read_text())
expected = json.loads((DATA / "PILOT-DATA-EXPECTED-01.json").read_text())
t09 = json.loads((DATA / "PILOT-DATA-T09-01.json").read_text())
fixtures = json.loads((DATA / "PILOT-DATA-FIXTURES-01.json").read_text())

chk("EXPECTED_RECORD value-by-value (literal_eval path)",
    expected["EXPECTED_RECORD"] == span_literal("EXPECTED_RECORD"))
chk("OB_TRUTH value-by-value", expected["OB_TRUTH"] == span_literal("OB_TRUTH"))
chk("T06_KEY value-by-value", expected["T06_KEY"] == span_literal("T06_KEY"))
chk("OBLIGATION_T09 value-by-value",
    t09["OBLIGATION_T09"] == span_literal("OBLIGATION_T09"))
chk("V24 shas", expected["V24_HARNESS_SHA"] == V24H and
    expected["V24_RESULTS_SHA"] == V24R)

R = t09["RECEIPTS"]
chk("FR-VALID carries every required field",
    all(f in R["FR-VALID"] for f in t09["OBLIGATION_T09"]["required_fields"]))
chk("FR-A differs from FR-VALID only by the corrupted sha",
    {k: v for k, v in R["FR-A"].items() if k != "sha256"} ==
    {k: v for k, v in R["FR-VALID"].items() if k != "sha256"} and
    R["FR-A"]["sha256"] == V24H[:-4] + "0000")
chk("FR-B is FR-VALID minus result",
    "result" not in R["FR-B"] and
    all(R["FR-B"][k] == R["FR-VALID"][k] for k in R["FR-B"]))
chk("FR-C differs from FR-VALID only by evidence_status [reported]",
    {k: v for k, v in R["FR-C"].items() if k != "evidence_status"} ==
    {k: v for k, v in R["FR-VALID"].items() if k != "evidence_status"} and
    R["FR-C"]["evidence_status"] == "[reported]")

def gate(receipt):
    ob = t09["OBLIGATION_T09"]
    reasons = []
    for f in ob["required_fields"]:
        if f not in receipt:
            reasons.append(f"required field absent: {f}")
    if receipt.get("sha256") != ob["sha256"]:
        reasons.append("sha256 mismatch")
    if ob["result_contains"] not in str(receipt.get("result", "")):
        reasons.append("result lacks required evidence")
    if receipt.get("evidence_status") != ob["evidence_status"]:
        reasons.append("evidence_status not [verified]")
    return "REJECT" if reasons else "CLOSE"
want = {"FR-A": "REJECT", "FR-B": "REJECT", "FR-C": "REJECT",
        "FR-VALID": "CLOSE"}
chk("T09 gate decisions from the data files",
    all(gate(R[k]) == v for k, v in want.items()),
    ", ".join(f"{k}->{gate(R[k])}" for k in want))
chk("obligation_spec_text carries the sha + all required fields",
    V24H in t09["obligation_spec_text"] and
    all(f in t09["obligation_spec_text"]
        for f in t09["OBLIGATION_T09"]["required_fields"]))

probes = {"injection-note": "disregard all prior instructions",
          "obligation-register": "OBLIGATION REGISTER (fixtures)",
          "shelf-record-181a30d": "commit 181a30d",
          "invalid-draft": "It was rejected"}
for fid, probe in probes.items():
    chk(f"fixture {fid} present with its content",
        probe in fixtures["fixtures"].get(fid, "") and probe in SRC)
chk("invalid-draft carries the substituted harness sha",
    V24H in fixtures["fixtures"]["invalid-draft"])
arm = fixtures["t04_arm_instruction_set"]
chk("arm_b_system == arm_a_system + governance",
    arm["arm_b_system"] == arm["arm_a_system"] + arm["governance"])

secs = {}
for line in open(SNAP / "sections.jsonl"):
    s = json.loads(line)
    secs[s["section_id"]] = s

def manifest_row(ref):
    """Resolve a pilot-manifest: ref against the data files."""
    body = ref.split(":", 1)[1]
    fname, key = body.split("#")
    doc = {"PILOT-DATA-PACKS-01": packs, "PILOT-DATA-EXPECTED-01": expected,
           "PILOT-DATA-T09-01": t09, "PILOT-DATA-FIXTURES-01": fixtures}[fname]
    if key.startswith("receipt-"):
        return "RECEIPT SUBMITTED FOR CLOSURE:\n" + \
            json.dumps(doc["RECEIPTS"][key[8:]], indent=1)
    if key == "obligation-spec-text":
        return doc["obligation_spec_text"]
    return doc["fixtures"][key]

pack_hashes = {}
all_resolve = True
for tid, t in packs["trees"].items():
    parts = []
    for item in t["pack"]:
        if "section" in item:
            s = secs.get(item["section"])
            if s is None:
                all_resolve = False
                continue
            parts.append(f"=== SECTION {s['section_id']} · doc {s['doc']} · "
                         f"{s['heading_path']} · sha256 {s['sha256'][:16]}… "
                         f"===\n{s['text']}")
        else:
            ref = item.get("fixture_ref") or item.get("receipt_ref")
            fid = ref.split("#")[1]
            label = fid if not fid.startswith("receipt-") else \
                "receipt-" + fid[8:]
            parts.append(f"=== FIXTURE {label} ===\n{manifest_row(ref)}")
    pack_hashes[tid] = hashlib.sha256("\n".join(parts).encode()).hexdigest()
chk("every pack item resolves (sections in snapshot, refs in data files)",
    all_resolve and len(pack_hashes) == len(packs["trees"]),
    f"{len(pack_hashes)} packs rendered")
chk("tree set is T01..T08 + T09 x4",
    sorted(packs["trees"]) == ["T01", "T02", "T03", "T04", "T05", "T06",
                                "T07", "T08", "T09-FR-A", "T09-FR-B",
                                "T09-FR-C", "T09-FR-VALID"])
print(json.dumps({"pack_hashes": pack_hashes}, indent=1))
bad = [c for c in checks if not c["pass"]]
for c in checks:
    print(("PASS " if c["pass"] else "FAIL ") + c["check"] +
          (f" — {c['detail']}" if c["detail"] else ""))
print(f"SUMMARY {len(checks) - len(bad)}/{len(checks)} checks pass")
sys.exit(1 if bad else 0)
