#!/usr/bin/env python3
"""C-D2 preparation: the examiner-corpus ingestion runner.

Ingests the examiner-authored corpus EXACTLY as supplied:
  - the supplied file is copied byte-for-byte to the output directory and
    its SHA-256 recorded BEFORE any parsing;
  - each case's raw response text is written to the validators byte-exactly
    as it appears in the corpus (no normalization, no repair);
  - both independent validators run unchanged (validator_py, validator_js);
  - the report carries per-case verdicts from both lineages, agreement, and
    — only where the corpus itself supplies an `expected_valid` field — the
    expectation check. Cases without that field are reported verdict-only.

Corpus format (the build-authored corpus's format, tests/corpus.json):
a JSON list of {"name": ..., "raw": <exact response text>,
"expected_valid": <bool, optional>, ...} objects.

Usage: run_examiner_corpus.py <corpus-file> <output-dir>
The run itself executes when the examiner's corpus arrives. This runner was
prepared in the correction round; NO examiner corpus existed at preparation
time and none was authored as a substitute."""
import hashlib, json, os, subprocess, sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_py(path):
    out = subprocess.run([sys.executable, T + "/validator_py/validate_py.py", path],
                         capture_output=True, text=True)
    return json.loads(out.stdout.strip())

def run_js(path):
    out = subprocess.run(["node", T + "/validator_js/validate_js.js", path],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("ajv validator failed: " + out.stderr)
    return json.loads(out.stdout.strip())

def main():
    corpus_path, out_dir = sys.argv[1], sys.argv[2]
    raw_bytes = open(corpus_path, "rb").read()
    corpus_sha = hashlib.sha256(raw_bytes).hexdigest()
    os.makedirs(out_dir, exist_ok=True)
    preserved = os.path.join(out_dir, "examiner_corpus_as_supplied.bin")
    with open(preserved, "wb") as f:
        f.write(raw_bytes)
    preserved_sha = hashlib.sha256(open(preserved, "rb").read()).hexdigest()
    cases = json.loads(raw_bytes.decode("utf-8"))
    results, disagreements, expectation_failures = [], [], []
    for i, case in enumerate(cases):
        p = os.path.join(out_dir, "case_%03d.raw" % i)
        with open(p, "wb") as f:
            f.write(case["raw"].encode("utf-8"))
        a, b = run_py(p), run_js(p)
        agree = a["valid"] == b["valid"]
        entry = {"case": case.get("name", "case_%03d" % i),
                 "python": a["valid"], "ajv": b["valid"], "agree": agree,
                 "python_detail": a, "ajv_detail": b}
        if "expected_valid" in case:
            entry["expected"] = case["expected_valid"]
            entry["expectation_met"] = a["valid"] == case["expected_valid"] and b["valid"] == case["expected_valid"]
            if not entry["expectation_met"]:
                expectation_failures.append(entry["case"])
        if not agree:
            disagreements.append(entry["case"])
        results.append(entry)
    report = {"corpus_source_path": corpus_path, "corpus_sha256": corpus_sha,
              "byte_preserved_copy": preserved, "byte_preserved_copy_sha256": preserved_sha,
              "byte_preservation_verified": corpus_sha == preserved_sha,
              "cases": len(cases), "disagreements": disagreements,
              "expectation_failures": expectation_failures, "results": results}
    json.dump(report, open(os.path.join(out_dir, "examiner_corpus_report.json"), "w"), indent=1)
    print(json.dumps({k: report[k] for k in
                      ("corpus_sha256", "byte_preservation_verified", "cases", "disagreements", "expectation_failures")}))

if __name__ == "__main__":
    main()
