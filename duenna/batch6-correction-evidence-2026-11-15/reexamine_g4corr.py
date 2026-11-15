#!/usr/bin/env python3
"""Re-examination of G4CORR-20261115-001 (evidence correction,
Alex's RB-43 restatement, 2026-11-15).

The original CLI examination (g4corr-examination.json) was run
without the pin-authority / manifest inputs, so its Step 2
index was empty: pins_checked 0, eleven "pin not found"
findings. That artefact is preserved untouched.

This re-examination runs the corrected examiner's own step
functions (pilot_examiner.py, sha256 56492523…) over the
preserved run with the pin index built as the audit suite
builds it: PILOT-PIN-AUTHORITY-02 + the freeze manifest via
build_pin_index, with G4CORR-STACK-MANIFEST.sha256 layered
over it by direct assignment (the correction stack's own
manifest is the authority for the files the run loaded), and
the PILOT-CORPUS-SNAPSHOT-01 pin keyed to the stack
manifest's sections.jsonl hash (b107e892…). The run record
and all preserved artefacts are read, never modified.
Output: g4corr-examination-02.json.
"""
import hashlib, json, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
CORR = H / "workspace/ssh-door/batch6/correction"
RUN = (H / "workspace/ssh-door/batch6/scratch/g4corr/runs"
       "/G4CORR-20261115-001")
COMMITS = H / "workspace/ssh-door/batch6/scratch/g4corr/commitments"
STACK = CORR / "stack"
TOOLS_DIR = STACK / "work"
SNAP = STACK / "snapshot"
DATA = STACK / "data"
RULES = DATA / "EXTRACTOR-RULES-02.json"
AUTH02 = B6 / "PILOT-PIN-AUTHORITY-02.json"
FZMAN = H / "workspace/ssh-door/freeze-manifest.sha256"
STACKMAN = CORR / "G4CORR-STACK-MANIFEST.sha256"
STUB_CFG_PATH = STACK / "work/stub_run_config.json"
TREES_PATH = STACK / "work/pilot_trees.json"
OUT = CORR / "g4corr-examination-02.json"

sys.path.insert(0, str(B6))
sys.path.insert(0, str(TOOLS_DIR))
from pilot_examiner import (step0, step1_chain, step2_inputs,
                            build_pin_index, load_tool_env,
                            step3_replay, step4_audit,
                            step5_capture, step5_model_link,
                            step6_reconstruct,
                            parse_complete_events)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    events, _ = parse_complete_events((RUN / "run-record.jsonl").read_bytes())
    out = {"run_id": "G4CORR-20261115-001",
           "examination": "re-examination (evidence correction, 2026-11-15)",
           "examiner_sha256": sha(B6 / "pilot_examiner.py"),
           "step2_index": {
               "authority": f"PILOT-PIN-AUTHORITY-02.json sha256 {sha(AUTH02)}",
               "freeze_manifest": f"freeze-manifest.sha256 sha256 {sha(FZMAN)}",
               "stack_manifest": f"G4CORR-STACK-MANIFEST.sha256 sha256 {sha(STACKMAN)}",
               "construction": "build_pin_index(authority, freeze manifest), "
                               "then the stack manifest's entries assigned over "
                               "the index (direct assignment, as in "
                               "test_g4corr.py); PILOT-CORPUS-SNAPSHOT-01 keyed "
                               "to the stack manifest's sections.jsonl hash."},
           "supersedes_step2_of": "g4corr-examination.json (preserved; its "
                                  "Step 2 ran with an empty pin index)"}

    out["step0"] = step0(RUN / "run-record.jsonl", COMMITS,
                         COMMITS / "issuance-record.jsonl")
    out["step1"] = step1_chain(events)

    index = build_pin_index([AUTH02], [FZMAN])
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2:
            index[parts[1]] = parts[0]
            index[f"basename:{Path(parts[1]).name}"] = parts[0]
    for line in STACKMAN.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].endswith("sections.jsonl"):
            index["PILOT-CORPUS-SNAPSHOT-01"] = parts[0]
    out["step2"] = step2_inputs(events[0], index, SNAP)

    with tempfile.TemporaryDirectory() as td:
        tools, record, seen = load_tool_env(
            TOOLS_DIR, SNAP, DATA, RULES,
            Path(td) / "replay-scratch.jsonl",
            "G4CORR-20261115-001", events)
        out["step3"] = step3_replay(events, tools, record, seen)
        record.close()

    sections = {}
    for ln in (SNAP / "sections.jsonl").read_text().splitlines():
        if ln.strip():
            s = json.loads(ln)
            sections[s["section_id"]] = s
    out["step4"] = step4_audit(events, sections)

    stub_cfg = json.loads(STUB_CFG_PATH.read_text())
    cap_findings, caps = [], {}
    for f in sorted((RUN / "adapter-captures").glob("*.json")):
        cap = json.loads(f.read_text())
        r = step5_capture(cap, stub_cfg)
        if r["findings"]:
            cap_findings.append({f.name: r["findings"]})
        caps[cap["correlation_id"]] = cap
    link_findings = []
    links = [e for e in events if e["event_type"] == "MODEL_CALL_LINKED"]
    for ev in links:
        r = step5_model_link(ev)
        if r["findings"]:
            link_findings.append({f"{ev['tree_id']}/{ev['step_id']}": r["findings"]})
    out["step5"] = {"captures_checked": len(caps),
                    "capture_findings": cap_findings,
                    "links_checked": len(links),
                    "link_findings": link_findings}

    trees_doc = json.loads(TREES_PATH.read_text())
    out["step6"] = step6_reconstruct(events, trees_doc)

    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("wrote", OUT)
    print("step2:", json.dumps(out["step2"])[:300])
    print("step3 divergence:", out["step3"].get("divergence"),
          "| reexecuted:", out["step3"].get("reexecuted"))
    print("step4 findings:", out["step4"].get("findings"))
    print("step5:", out["step5"])
    print("step6 divergences:", out["step6"].get("divergences"),
          "| terminal:", out["step6"].get("run_terminal"))


if __name__ == "__main__":
    main()
