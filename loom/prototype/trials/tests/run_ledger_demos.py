#!/usr/bin/env python3
"""D4, D5, D6, D7, D9 against a BUILD-DEMO round in the trials ledger.
All trial records here are DUMMY build fixtures, labelled as such in every
payload; no gate trial is run or represented."""
import hashlib, json, os, re, subprocess, sys, time

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = "/tmp/loom-trials-runtime"
sys.path.insert(0, T + "/ledger")
from ledger_client import call as ledger
import anchor as anchor_mod

def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()
def run(cmd, **kw): return subprocess.run(cmd, capture_output=True, text=True, **kw)
def ts(): 
    import datetime; return datetime.datetime.now(datetime.timezone.utc).isoformat()

E = {"demonstrations": {}}

# ---------- reset runtime ----------
for pid in os.listdir("/proc"):
    if pid.isdigit():
        try:
            cl = open(f"/proc/{pid}/cmdline", "rb").read().decode(errors="replace")
            if "loom-trials-runtime" in cl and "ledger_ser" + "vice" in cl:
                os.kill(int(pid), 15)
        except Exception: pass
time.sleep(1)
for f in [RT + "/ledger-store/sequence.jsonl", RT + "/work/examiner-out.txt"]:
    if os.path.exists(f): os.unlink(f)
run([sys.executable, T + "/ledger/runtime_setup.py"])
for _ in range(60):
    try:
        if ledger({"op": "head"}).get("ok"): break
    except Exception: time.sleep(0.5)
else: raise AssertionError("ledger service did not become ready")

annex_bytes = open(T + "/constitution_annex.json", "rb").read()
annex = json.loads(annex_bytes)
genesis_prev = sha(annex_bytes)
A_hash = annex["artifacts"]["annex_a_instruction"]["sha256"]
P_hash = annex["artifacts"]["gate_schema_profile"]["sha256"]

def append(etype, payload):
    r = ledger({"op": "append", "type": etype, "payload": payload, "timestamp": ts(), "genesis_prev": genesis_prev})
    assert r.get("ok"), r
    return r

# ---------- ROUND_CONSTITUTED ----------
rc = append("ROUND_CONSTITUTED", {"constitution_annex_sha256": genesis_prev,
    "annex_a_sha256": A_hash, "gate_schema_profile_sha256": P_hash,
    "validators": annex["validators"], "build_demo": True})
anchor_mod.anchor_head(rc["seq"], "ROUND_CONSTITUTED", rc["hash"])

# ---------- dummy trials + validation ----------
corpus = {c["name"]: c for c in json.load(open(T + "/tests/corpus.json"))}
dummies = [
    {"trial_uid": "DUMMY-1", "raw": corpus["valid-full-contribution"]["raw"]},
    {"trial_uid": "DUMMY-2", "raw": corpus["invalid-not-json"]["raw"]},
]
os.makedirs(T + "/evidence/dummy_trials", exist_ok=True)
val_outputs = []
for d in dummies:
    rp = f"{T}/evidence/dummy_trials/{d['trial_uid']}.response.txt"
    open(rp, "w").write(d["raw"])
    py = json.loads(run([sys.executable, T + "/validator_py/validate_py.py", rp]).stdout)
    js = json.loads(run(["node", T + "/validator_js/validate_js.js", rp]).stdout)
    val_outputs.append({"trial_uid": d["trial_uid"], "python": py, "ajv": js, "agree": py["valid"] == js["valid"]})
    append("TRIAL_RECORDED", {"trial_uid": d["trial_uid"], "dummy_fixture": True,
        "layer1": {"annex_a_sha256": A_hash, "profile_sha256": P_hash},
        "layer2_response_sha256": sha(d["raw"])})
    append("VALIDATION_RECORDED", {"trial_uid": d["trial_uid"], "dummy_fixture": True,
        "python_valid": py["valid"], "ajv_valid": js["valid"], "agree": py["valid"] == js["valid"]})
json.dump(val_outputs, open(T + "/evidence/dummy_trials/validator_outputs.json", "w"), indent=1)

# ---------- D9 freeze manifest + EVIDENCE_FROZEN ----------
manifest = {"round": "build-demo-round", "dummy_fixtures": True,
    "prompt_annex_a_sha256": A_hash, "profile_sha256": P_hash,
    "constitution_annex_sha256": genesis_prev,
    "candidate_fingerprint_dummy": {"route": "build-demo", "model_id": "DUMMY — no candidate", "note": "freeze mechanics demonstrated over dummy records only"},
    "responses_in_schedule_order": [{"trial_uid": d["trial_uid"], "sha256": sha(d["raw"])} for d in dummies],
    "validator_outputs_sha256": sha(json.dumps(val_outputs, sort_keys=True))}
mpath = T + "/evidence/freeze_manifest_dummy.json"
json.dump(manifest, open(mpath, "w"), indent=1)
manifest_hash = sha(open(mpath, "rb").read())
ef = append("EVIDENCE_FROZEN", {"manifest_sha256": manifest_hash})
# ---------- D6 anchoring ----------
ef_anchor = anchor_mod.anchor_head(ef["seq"], "EVIDENCE_FROZEN", ef["hash"])
readback = anchor_mod.read_anchor(ef["seq"], "EVIDENCE_FROZEN")
E["demonstrations"]["D6"] = {"anchored_seq": ef["seq"], "head_hash": ef["hash"],
    "anchor_commit": ef_anchor.get("anchor_commit"),
    "readback_contains_head_hash": bool(readback and ef["hash"] in readback),
    "proves": "a sequence head with this hash existed at this position no later than the anchor commit; wholesale chain reconstruction would contradict the anchored head",
    "does_not_prove": "that no unanchored parallel chain was kept privately; the shelf is an archival anchor independent of the trials system, not a trusted timestamp authority"}
# ---------- D7(i) release before SCORING_FROZEN ----------
sys.path.insert(0, T + "/ledger")
import gt_release
out_path = RT + "/work/examiner-out.txt"
r_early = gt_release.release("build-demo-examiner", out_path)
E["demonstrations"]["D7_i_release_before_scoring_frozen"] = {**r_early, "material_released": os.path.exists(out_path)}
# ---------- D5 append-only boundary ----------
shutil_client = RT + "/work/ledger_client.py"
open(shutil_client, "w").write(open(T + "/ledger/ledger_client.py").read())
os.chmod(shutil_client, 0o644)
d5 = {}
d5["direct_read_as_loomagent"] = run(["runuser", "-u", "loomagent", "--", "cat", RT + "/ledger-store/sequence.jsonl"]).returncode
d5["direct_append_as_loomagent"] = run(["runuser", "-u", "loomagent", "--", "python3", "-c",
    "open('/tmp/loom-trials-runtime/ledger-store/sequence.jsonl','a').write('x')"]).returncode
d5["direct_delete_as_loomagent"] = run(["runuser", "-u", "loomagent", "--", "rm", RT + "/ledger-store/sequence.jsonl"]).returncode
d5["service_delete_op"] = ledger({"op": "delete"})
d5["service_update_op"] = ledger({"op": "update"})
app_agent = run(["runuser", "-u", "loomagent", "--", "python3", shutil_client, "append",
                 "SCORING_COMPLETED", json.dumps({"sheets_manifest_sha256": "DEMO", "build_demo": True}), ts(), genesis_prev])
d5["append_via_service_as_loomagent"] = json.loads(app_agent.stdout) if app_agent.returncode == 0 else {"error": app_agent.stderr[-200:]}
E["demonstrations"]["D5"] = d5
scoring_completed_seq = d5["append_via_service_as_loomagent"].get("seq")
# ---------- scoring sheets (blinded) + SCORING_FROZEN ----------
sys.path.insert(0, T + "/scoring")
import scoring
sheets, mapping = [], {}
for d, vo in zip(dummies, val_outputs):
    parsed = None
    try: parsed = json.loads(d["raw"])
    except Exception: pass
    rec = {"trial_uid": d["trial_uid"], "parsed": parsed, "schema_valid": vo["python"]["valid"]}
    sheet = scoring.make_sheet(rec, "build-demo-secret")
    sheet["examiner_fields_status"] = "BUILD DEMO — sheet generated and pre-checks entered; examiner judgment fields intentionally left unscored (no examiner scoring occurs in the build round)"
    sheets.append(sheet); mapping[sheet["blind_ref"]] = d["trial_uid"]
json.dump(sheets, open(T + "/evidence/dummy_scoring_sheets.json", "w"), indent=1)
json.dump(mapping, open(T + "/evidence/dummy_scoring_mapping.json", "w"), indent=1)
sheets_hash = sha(open(T + "/evidence/dummy_scoring_sheets.json", "rb").read())
sf = append("SCORING_FROZEN", {"sheets_manifest_sha256": sheets_hash, "build_demo": True})
sf_anchor = anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
E["demonstrations"]["scoring_freeze"] = {"scoring_completed_seq": scoring_completed_seq,
    "scoring_frozen_seq": sf["seq"], "anchor_commit": sf_anchor.get("anchor_commit")}
# ---------- D7(iii) fail-closed ----------
if os.path.exists(out_path): os.unlink(out_path)
os.environ["GT_RELEASE_SABOTAGE_ANCHOR"] = "1"
r_sab = gt_release.release("build-demo-examiner", out_path)
os.environ.pop("GT_RELEASE_SABOTAGE_ANCHOR")
E["demonstrations"]["D7_iii_fail_closed"] = {**r_sab, "material_released": os.path.exists(out_path)}
# ---------- D7(ii) successful gated release ----------
r_ok = gt_release.release("build-demo-examiner", out_path)
standin_hash = sha(open("/tmp/gtstage/annex-d-sealed-standin.txt", "rb").read())
E["demonstrations"]["D7_ii_gated_release"] = {**r_ok,
    "material_hash_matches_standin": r_ok.get("material_sha256") == standin_hash}
# ---------- D9 verification + D4 ----------
ver = ledger({"op": "verify"})
events = ledger({"op": "list"})["events"]
E["demonstrations"]["D9"] = {"manifest": manifest, "manifest_sha256": manifest_hash,
    "chain_verify": ver, "event_types_in_order": [e["type"] for e in events],
    "chronology_check": "EVIDENCE_FROZEN precedes SCORING_COMPLETED/SCORING_FROZEN, which precede GROUND_TRUTH_ACCESSED, each hash-linked"}
spec = open("/home/hatch/workspace/duenna-fix/LOOM-SPEC-V0.1-REV9-DRAFT-2026-11-21.md").read()
annex_d = spec.split("## Annex D")[1].split("## Annex E")[0]
words = re.findall(r"[a-z0-9']+", annex_d.lower())
shingles = {" ".join(words[i:i+6]) for i in range(len(words) - 5)}
hits = []
for root, dirs, files in os.walk(T):
    if "node_modules" in root or "catalogues" in root: continue
    for fn in files:
        p = os.path.join(root, fn)
        try: text = open(p, errors="ignore").read().lower()
        except Exception: continue
        tw = re.findall(r"[a-z0-9']+", text)
        tsh = {" ".join(tw[i:i+6]) for i in range(len(tw) - 5)}
        common = shingles & tsh
        if common: hits.append({"file": p.replace(T, "trials"), "shingles": sorted(common)[:3]})
gt_read = run(["runuser", "-u", "loomagent", "--", "cat", RT + "/gt-store/annex-d-sealed-standin.txt"])
src_refs = run(["grep", "-rn", "duenna-fix\\|loom-prototype/fabric\\|fixture", T + "/adapters", T + "/validator_py",
                T + "/validator_js/validate_js.js", T + "/scoring", T + "/ledger",
                "--include=*.py", "--include=*.js"]).stdout
E["demonstrations"]["D4"] = {
    "gt_store_read_as_loomagent_returncode": gt_read.returncode,
    "annex_d_shingle_hits_in_trials_tree": hits,
    "component_source_refs_to_spec_or_fabric": src_refs.strip() or "none",
}
json.dump(E, open(T + "/evidence/D4_D5_D6_D7_D9_ledger.json", "w"), indent=1)
print(json.dumps({k: (v if not isinstance(v, dict) else "...") for k, v in E["demonstrations"].items()}, indent=1))
print("D5:", json.dumps(d5)[:400])
print("D7i:", r_early, "| D7iii released:", r_sab.get("released"), "| D7ii released:", r_ok.get("released"))
print("D4 gt read rc:", gt_read.returncode, "| shingle hits:", hits)
print("chain verify:", ver)
