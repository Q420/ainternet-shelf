#!/usr/bin/env python3
"""CorpusSource contract tests (Spec §4, Batch 1 checkpoint):
section resolution, pilot-manifest: resolution, NOT FOUND
behaviour — plus the runtime-path rule (no live index, no trial
runner) made testable against the module's own source.

Usage: test_corpus_source.py <snapshot_dir> <data_dir> <module_path>
Exit 0 iff every check passes.
"""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(sys.argv[3]).parent))
from corpus_source import CorpusSource

SNAP, DATA, MOD = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
checks = []
def chk(name, ok, detail=""):
    checks.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name +
          (f" — {detail}" if detail else ""))

cs = CorpusSource(SNAP, DATA)
packs = json.loads((pathlib.Path(DATA) / "PILOT-DATA-PACKS-01.json")
                   .read_text())

s = cs.get_section("r60-revision-change-record#009")
chk("section resolution: known section found with its recorded hash",
    s.get("section_id") == "r60-revision-change-record#009" and
    s.get("sha256", "").startswith("854a") is False and
    len(s.get("sha256", "")) == 64 and len(s.get("text", "")) > 100)

missing = [item["section"] for t in packs["trees"].values()
           for item in t["pack"] if "section" in item
           and cs.get_section(item["section"]).get("verification")
           == "NOT FOUND"]
chk("section resolution: every pack section ref resolves",
    not missing, f"missing: {missing}" if missing else
    f"{sum(1 for t in packs['trees'].values() for i in t['pack'] if 'section' in i)} refs")

bad = []
for t in packs["trees"].values():
    for item in t["pack"]:
        ref = item.get("fixture_ref") or item.get("receipt_ref")
        if ref and cs.get_manifest_row(ref).get("verification") == "NOT FOUND":
            bad.append(ref)
chk("pilot-manifest: resolution: every pack fixture/receipt ref resolves",
    not bad, f"unresolved: {bad}" if bad else "all refs")

row = cs.get_manifest_row("pilot-manifest:PILOT-DATA-T09-01#receipt-FR-VALID")
chk("pilot-manifest: FR-VALID receipt content is the verbatim receipt",
    row.get("value", {}).get("evidence_status") == "[verified]" and
    row.get("value", {}).get("artifact") == "harness-r60rev.py")

row = cs.get_manifest_row("pilot-manifest:PILOT-DATA-FIXTURES-01#t01-pack-manifest-reference")
chk("pilot-manifest: T01 pack manifest reference resolves with its pin",
    row.get("value", {}).get("sha256", "").startswith("d544cad8"))

nf1 = cs.get_section("no-such-doc#999")
chk("NOT FOUND: unknown section id returns NOT FOUND, no exception",
    nf1.get("verification") == "NOT FOUND" and "text" not in nf1)
nf2 = cs.get_manifest_row("pilot-manifest:PILOT-DATA-FIXTURES-01#nope")
chk("NOT FOUND: unknown fixture key returns NOT FOUND",
    nf2.get("verification") == "NOT FOUND")
nf3 = cs.get_section("pilot-manifest:PILOT-DATA-FIXTURES-01#injection-note")
chk("NOT FOUND: pilot-manifest: ref sent to get_section is refused by namespace",
    nf3.get("verification") == "NOT FOUND")
nf4 = cs.get_manifest_row("duenna-plan")
chk("manifest row: a bare doc id resolves to its corpus manifest row",
    nf4.get("verification") != "NOT FOUND")

src = MOD.read_text()
chk("runtime path: module never references the live index or the trial runner",
    "pulse-bridge" not in src and "run_ab" not in src and
    "ainternet-shelf" not in src)

bad = [c for c in checks if not c[1]]
print(f"SUMMARY {len(checks) - len(bad)}/{len(checks)} checks pass")
sys.exit(1 if bad else 0)
