#!/usr/bin/env python3
"""Generate PILOT-PIN-AUTHORITY-01.json from the frozen manifest
chain (§3.4 as amended by Rev 23). Every pre-existing artefact's
hash is asserted against the pin its governing document records
(CHAIN below, transcribed from PILOT-MANIFEST-01 and the
re-freeze continuations F2 / BATCH1 / BATCH2 / BATCH2-CORRECTION
/ BATCH3); any mismatch aborts generation. The corrected
artefacts (pilot_tools.py, pilot_driver.py, the budget stub
script) are hashed as they stand — their pins are minted by the
Batch 3 correction re-freeze continuation, which also records
this authority's own sha256 (the bootstrap anchor).

Usage: gen_authority.py <pilot_root> <output_path>
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# name, path (relative to pilot root), source, run, variant,
# chain pin (None for correction-minted artefacts)
ENTRIES = [
    ("corpus-snapshot-sections",
     "freeze/PILOT-CORPUS-SNAPSHOT-01/sections.jsonl",
     "PILOT-MANIFEST-01 (Batch 0 freeze)", True, None,
     "b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e"),
    ("corpus-snapshot-manifest",
     "freeze/PILOT-CORPUS-SNAPSHOT-01/manifest.json",
     "PILOT-MANIFEST-01 (Batch 0 freeze)", True, None,
     "c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452"),
    ("PILOT-DATA-PACKS-01", "batch1/work/PILOT-DATA-PACKS-01.json",
     "Re-freeze continuation BATCH1", True, None,
     "c7eaec18db203651af894e7fbdb53c6df9b36a3da185c4b7ab703d73085b886c"),
    ("PILOT-DATA-EXPECTED-01",
     "batch1/work/PILOT-DATA-EXPECTED-01.json",
     "Re-freeze continuation BATCH1", True, None,
     "79db5c87d4c9ccc52cb53c68fec5c2477cf546c9b80babbc489a472d37e57863"),
    ("PILOT-DATA-FIXTURES-01",
     "batch1/work/PILOT-DATA-FIXTURES-01.json",
     "Re-freeze continuation BATCH1", True, None,
     "b02e0dd005e884c62d493c1f524da983d77b2468645cf342e2a7fc9d9d08d9e8"),
    ("PILOT-DATA-T09-01", "batch1/work/PILOT-DATA-T09-01.json",
     "Re-freeze continuation BATCH1", True, None,
     "55a6c979163a9ce0cb30fca4eb951aff0d02685979290df8bd18dfa28b355c4a"),
    ("EXTRACTOR-RULES-02", "batch1/work/EXTRACTOR-RULES-02.json",
     "Re-freeze continuation BATCH1", True, None,
     "61095f219e1d481ed74c65f3a95806a2cba2e7dc847bcb692373ade3974c5ee5"),
    ("corpus_source.py", "batch1/work/corpus_source.py",
     "Re-freeze continuation BATCH1", True, None,
     "520f36fde41dfb76d5f92fe4da92b6c2f93ae8512051962f76d4942fb5c05a5a"),
    ("rules_engine.py", "batch1/work/rules_engine.py",
     "Re-freeze continuation BATCH1", True, None,
     "7a2329154081b6e9c0417c07b1cc7184b167d02c1e820081b68a18dbabafacf3"),
    ("pilot_jcs.py", "freeze/jcs/pilot_jcs.py",
     "Batch 0 freeze (RFC 8785 implementation)", True, None,
     "8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c"),
    ("pilot_tools.py", "batch3/correction/pilot_tools.py",
     "Re-freeze continuation BATCH3-CORRECTION (minted)", True,
     None, None),
    ("pilot_record.py", "batch3/correction/pilot_record.py",
     "Re-freeze continuation BATCH3 (unchanged by the "
     "correction)", True, None,
     "ed3f5c8521159d874fef7cefdf52accca7ef0fcf2c5b29d299ab4996ed1c7216"),
    ("pilot_driver.py", "batch3/correction/pilot_driver.py",
     "Re-freeze continuation BATCH3-CORRECTION (minted)", True,
     None, None),
    ("pilot_trees.json", "batch3/work/pilot_trees.json",
     "Re-freeze continuation BATCH3", True, None,
     "d23f35f660ee4967039c56726b8f4d3d416adf265d109e67190a0dc0603e29ec"),
    ("stub_subject.py", "batch3/work/stub_subject.py",
     "Re-freeze continuation BATCH3", True, None,
     "465d325a53f7ef57eb5da9074e59cc6e5413978834cd86820fb88291a6b6cae9"),
    ("stub_script_main.json", "batch3/work/stub_script_main.json",
     "Re-freeze continuation BATCH3", True, "stub_script_main",
     "dde24b6a5ad98f6890add04beaf59c723df932d66f01441c613da1c2f8eacf5d"),
    ("stub_script_lane.json", "batch3/work/stub_script_lane.json",
     "Re-freeze continuation BATCH3", True, "stub_script_lane",
     "ed590514b23bfef6267364a0f856d04a139fc3f97652e3df9f4c2832f4d056d3"),
    ("stub_script_budget.json",
     "batch3/correction/stub_script_budget.json",
     "Re-freeze continuation BATCH3-CORRECTION (minted)", True,
     "stub_script_budget", None),
]

entries = []
for name, rel, source, run, variant, chain_pin in ENTRIES:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"MISSING: {rel}")
    actual = sha(p)
    if chain_pin is not None and actual != chain_pin:
        raise SystemExit(
            f"CHAIN PIN MISMATCH: {name} expected {chain_pin}, "
            f"found {actual}")
    entries.append({"name": name, "path": rel, "sha256": actual,
                    "source": source, "run": run,
                    "variant": variant})
    print(f"OK {name} {actual[:12]}…"
          + (" (chain-verified)" if chain_pin else " (minted)"))

# the imported JCS copy in batch3/work must equal the freeze pin
work_jcs = sha(ROOT / "batch3/work/pilot_jcs.py")
assert work_jcs == dict((e["name"], e["sha256"]) for e in entries)[
    "pilot_jcs.py"], "batch3/work pilot_jcs.py diverges from freeze"
print("OK batch3/work/pilot_jcs.py == freeze/pilot_jcs.py")

doc = {"artefact": "PILOT-PIN-AUTHORITY-01",
       "generated_from": "PILOT-MANIFEST-01 and the re-freeze "
                         "continuations F2, BATCH1, BATCH2, "
                         "BATCH2-CORRECTION, BATCH3; anchored by "
                         "the hash recorded in the BATCH3-"
                         "CORRECTION continuation",
       "entries": entries}
OUT.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
print(f"AUTHORITY_SHA256 {sha(OUT)}")
print(f"WROTE {OUT} ({len(entries)} entries)")
