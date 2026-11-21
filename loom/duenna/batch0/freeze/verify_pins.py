#!/usr/bin/env python3
"""Batch 0 pin verification — recompute every Stage 0 / spec §2 pin from bytes.
Reads only; writes nothing. Emits a JSON table on stdout."""
import hashlib, json, pathlib, sys

def pin(path):
    p = pathlib.Path(path)
    if not p.exists():
        return {"path": str(p), "exists": False}
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"path": str(p), "exists": True, "bytes": p.stat().st_size,
            "sha256": h.hexdigest()}

SHELF = pathlib.Path.home() / "workspace/ainternet-shelf"
LETTERS = pathlib.Path.home() / "workspace/duenna-letters"
INDEX = pathlib.Path.home() / "workspace/pulse-bridge/index"

CASES = [
    # id, path, expected sha256 (None = record only), expected bytes (None = n/a)
    ("S1-living-local", LETTERS/"NEMOTRON-PILOT-PLAN-01-DRAFT.md", "2449c259cf73d688932d1ad1c91fb12a225eb35dc7cb3494d5e62adaeb1cb6f1", 7497),
    ("S1-shelf-copy",   SHELF/"duenna/NEMOTRON-PILOT-PLAN-01-DRAFT.md", None, None),
    ("S2-manifest-shelf", SHELF/"duenna/PILOT-MANIFEST-01.md", None, None),
    ("S2-manifest-local", LETTERS/"PILOT-MANIFEST-01.md", None, None),
    ("S3", SHELF/"duenna/PILOT-HARNESS-DESIGN-03.md", "b0fca1259c0f6432437535ad92224ad8cd824f71a078d91b7f455182c8df0d04", None),
    ("S4", SHELF/"duenna/NEMOTRON-ADAPTER-DESIGN-03.md", "5be7eb0e59793b98f5352c55778ca2da755e6078be70c00859e3dcc8174909bb", None),
    ("S5", SHELF/"duenna/PILOT-ACCEPTANCE-CRITERIA-04.md", "7608d74eef511b59ae59c33d18b299ac050c943ebebc10aeed816e101a822e2e", None),
    ("S6", SHELF/"duenna/INTERPRETATION-NOTE-01.md", "94d40cc7477fccc040013a24caf693826b1e28a07a7f3f1f6367fc7f8eb61771", None),
    ("S7", SHELF/"duenna/V2-QUALIFICATION-01.md", "6ae47780785001b6ffc68b73bc2b0a3e11cc9b0a8def493d958b86d60e2f623a", None),
    ("S10", LETTERS/"NOTE-20261112-duenna-flow-both.md", "a2eacc3aa1e32e6d7c6003087811f2eee3f92690df1273b659491551d753f257", None),
    ("SPEC13-shelf", SHELF/"duenna/STAGE5-BUILD-SPEC-13.md", None, 214041),
    ("row2",  SHELF/"duenna/qwen-ab/v2/V2-PACKAGE.md", "3dcda7b285f3eb26c979a4bf48b410196d0c804cf5b4f24482882cbe2cc3754f", 5796),
    ("row3",  SHELF/"duenna/qwen-ab/v2/PROCESS-TREES.md", "5528ab69bec2f7fcdea776748e9bdc2e84ec97b4fa1d4be35bf7fd386e24b0ad", 12631),
    ("row4",  SHELF/"duenna/qwen-ab/v2/tools.py", "e78f45d31ed6831253ed5fed1dc3f5dd22938b70e7c47cd15e190b912161cc1d", 7459),
    ("row5",  SHELF/"duenna/qwen-ab/v2/demo_tools.py", "6c960e442009c6c8978eaeab506311626f74df014aac50ef7bff42ff5bdb4648", 4446),
    ("row6",  SHELF/"duenna/qwen-ab/v2/DEMO-RESULTS.json", "baaca7a840d19a194a9754be513d8a95f92657ba2624a0cc62ec1f1663b02dbf", 26634),
    ("row7",  SHELF/"duenna/qwen-ab/run_ab.py", "acb647bd50bfa2f6a219415dd60242a3efbacbf5a68a2d16ac7c3dbd57663d53", 21273),
    ("row8",  INDEX/"query.py", "f8f2c7cad78089451399564dff19e22aa1c6fc6038f9efb832a9c01954905e32", 3515),
    ("row9",  INDEX/"sections.jsonl", "b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e", 3709804),
    ("row10", INDEX/"manifest.json", "c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452", 50881),
    ("row11", SHELF/"MANIFEST.md", "3b4462fbfb5c1ea644272e905d0e4ee3bf9121df57ab9a6a282346b7634ce21f", 13067),
    ("row12", SHELF/"duenna/qwen-ab/QWEN-AB-EVIDENCE-MANIFEST.json", "d544cad83cd86b5b54ebcd02120037c74451e678aa7d1d0e7415ede921bfd56d", 3863),
]

out = []
for cid, path, exp, exp_bytes in CASES:
    r = pin(path)
    r["id"] = cid
    r["expected_sha256"] = exp
    r["expected_bytes"] = exp_bytes
    if exp is None:
        r["verdict"] = "RECORDED"
    elif not r["exists"]:
        r["verdict"] = "MISSING"
    else:
        r["verdict"] = "MATCH" if r["sha256"] == exp else "MISMATCH"
    out.append(r)

print(json.dumps(out, indent=2))
bad = [r["id"] for r in out if r["verdict"] == "MISMATCH"]
print("MISMATCHES:", bad, file=sys.stderr)
