#!/usr/bin/env python3
"""PILOT-CORPUS-SNAPSHOT-01 verification — independent recomputation.
Implements the corpus's own verification semantics (per-section content hash
sha256(text) and the per-document digest chain seeded by the manifest's
canonical_sha256), coded here from the corpus format, run against the
SNAPSHOT copies. Also checks both snapshot files against the Stage 0 pins."""
import hashlib, json, pathlib

HERE = pathlib.Path(__file__).parent

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def file_pin(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

result = {}
result["sections_file_sha256"] = file_pin(HERE / "sections.jsonl")
result["sections_file_pin_expected"] = "b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e"
result["sections_file_pin_match"] = result["sections_file_sha256"] == result["sections_file_pin_expected"]
result["manifest_file_sha256"] = file_pin(HERE / "manifest.json")
result["manifest_file_pin_expected"] = "c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452"
result["manifest_file_pin_match"] = result["manifest_file_sha256"] == result["manifest_file_pin_expected"]

secs = [json.loads(l) for l in open(HERE / "sections.jsonl")]
man = json.load(open(HERE / "manifest.json"))
result["section_count"] = len(secs)
result["manifest_documents"] = [d["doc"] for d in man["documents"]]

bad_hash, bad_chain, bad_final = [], [], []
docs_seen = set()
for d in man["documents"]:
    rs = [r for r in secs if r["doc"] == d["doc"]]
    docs_seen.add(d["doc"])
    chain = d["canonical_sha256"]
    for r in rs:
        if sha(r["text"].encode()) != r["sha256"]:
            bad_hash.append(r["section_id"])
        chain = sha((chain + r["sha256"]).encode())
        if chain != r["chain_sha256"]:
            bad_chain.append(r["section_id"])
    if chain != d["final_chain_sha256"]:
        bad_final.append(d["doc"])

result["sections_with_unlisted_doc"] = sorted({r["doc"] for r in secs} - docs_seen)
result["per_section_hash_mismatches"] = bad_hash
result["chain_mismatches"] = bad_chain
result["document_final_chain_mismatches"] = bad_final
result["all_sections_verified"] = not (bad_hash or bad_chain or bad_final or result["sections_with_unlisted_doc"])
print(json.dumps(result, indent=2))
