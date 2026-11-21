#!/usr/bin/env python3
"""Correction round ledger work: C-D7 gate negatives (chain 1), C-D9 fresh
dummy lifecycle in exact SS13 order (chain 2), C-D5 boundary evidence.

Chain 1 (round correction-negtests-DUMMY) exists only to exercise the
strengthened release gate's refusals; it is then discarded by a runtime
reset. Chain 2 is the correction round's dummy lifecycle of record.
Every payload in both chains carries a DUMMY marker and a distinct round id;
no record here is, or can be presented as, trial evidence.
All original build-round evidence is untouched."""
import hashlib, json, os, subprocess, sys, time

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = "/tmp/loom-trials-runtime"
sys.path.insert(0, T + "/ledger")
from ledger_client import call as ledger
import anchor as anchor_mod
import gt_release

def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()
def run(cmd, **kw): return subprocess.run(cmd, capture_output=True, text=True, **kw)
def ts():
    import datetime; return datetime.datetime.now(datetime.timezone.utc).isoformat()

def reset_runtime():
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                cl = open(f"/proc/{pid}/cmdline", "rb").read().decode(errors="replace")
                if "loom-trials-runtime" in cl and "ledger_ser" + "vice" in cl:
                    os.kill(int(pid), 15)
            except Exception: pass
    time.sleep(1)
    sf = RT + "/ledger-store/sequence.jsonl"
    if os.path.exists(sf): os.unlink(sf)
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
PACKET_SHA = "8bb7c08ade85f2c46233cdcf3998e7ad043c93764ef1d48637ac0e493aa26c15"

def append(etype, payload):
    r = ledger({"op": "append", "type": etype, "payload": payload,
                "timestamp": ts(), "genesis_prev": genesis_prev})
    assert r.get("ok"), r
    return r

# ================= CHAIN 1: C-D7 gate negatives =================
anchor_mod.REL_DIR = "trials-anchors/correction-negtests"
reset_runtime()
R1 = "correction-negtests-DUMMY"
ev1 = {"round_id": R1, "anchor_dir": anchor_mod.REL_DIR, "tests": {}}
append("ROUND_CONSTITUTED", {"round_id": R1, "DUMMY": True,
    "constitution_annex_sha256": genesis_prev, "purpose": "C-D7 gate negative tests only"})
sf1 = append("SCORING_FROZEN", {"round_id": R1, "DUMMY": True,
    "note": "frozen WITHOUT any SCORING_COMPLETED — the build round's successful-release pattern"})
a1 = anchor_mod.anchor_head(sf1["seq"], "SCORING_FROZEN", sf1["hash"])
out1 = RT + "/work/examiner-out-chain1.txt"
if os.path.exists(out1): os.unlink(out1)
head_before = ledger({"op": "head"})
r = gt_release.release("correction-demo-examiner", out1)
ev1["tests"]["release_with_scoring_completed_absent"] = {
    **r, "material_released": os.path.exists(out1),
    "head_before": head_before, "head_after": ledger({"op": "head"}),
    "anchor_commit_scoring_frozen": a1.get("anchor_commit")}
# complete the order, then attack the anchor structurally
append("SCORING_COMPLETED", {"round_id": R1, "DUMMY": True})
sf2 = append("SCORING_FROZEN", {"round_id": R1, "DUMMY": True, "note": "complete order now present"})
a2 = anchor_mod.anchor_head(sf2["seq"], "SCORING_FROZEN", sf2["hash"])
real_read_anchor = anchor_mod.read_anchor
def fake_readback(record_text):
    envelope = {"result": {"content": [
        {"text": "successfully downloaded text file (SHA: 0000)", "type": "text"},
        {"resource": {"mimeType": "text/plain; charset=utf-8", "text": record_text,
                      "uri": "repo://Q420/ainternet-shelf/contents/fake"}, "type": "resource"}]}}
    return json.dumps(envelope)
bad_rec = {"seq": sf2["seq"], "type": "SCORING_FROZEN", "head_hash": "0" * 64,
           "path": anchor_mod.anchor_path(sf2["seq"], "SCORING_FROZEN"),
           "anchor": "Q420/ainternet-shelf"}
anchor_mod.read_anchor = lambda seq, etype: fake_readback(json.dumps(bad_rec))
head_before = ledger({"op": "head"})
r = gt_release.release("correction-demo-examiner", out1)
ev1["tests"]["release_with_mismatched_anchor_record"] = {
    **r, "material_released": os.path.exists(out1),
    "head_before": head_before, "head_after": ledger({"op": "head"})}
anchor_mod.read_anchor = lambda seq, etype: "this is not a read-back envelope"
r = gt_release.release("correction-demo-examiner", out1)
ev1["tests"]["release_with_malformed_anchor_readback"] = {
    **r, "material_released": os.path.exists(out1)}
anchor_mod.read_anchor = real_read_anchor
# fail-closed against the real store, complete order, valid anchor
os.environ["GT_RELEASE_SABOTAGE_ANCHOR"] = "1"
r = gt_release.release("correction-demo-examiner", out1)
os.environ.pop("GT_RELEASE_SABOTAGE_ANCHOR")
ev1["tests"]["fail_closed_anchor_sabotage_real_store"] = {
    **r, "material_released": os.path.exists(out1),
    "events_after": [e["type"] for e in ledger({"op": "list"})["events"]]}
ev1["chain1_events"] = ledger({"op": "list"})["events"]
json.dump(ev1, open(T + "/evidence/CD7_gate_negatives_chain1.json", "w"), indent=1)
print("chain1 negatives:", json.dumps({k: (v.get("released"), v.get("stage")) for k, v in ev1["tests"].items()}))

# ================= CHAIN 2: C-D9 fresh dummy lifecycle =================
anchor_mod.REL_DIR = "trials-anchors/correction-dummy-round"
reset_runtime()
R2 = "correction-dummy-round-DUMMY"
ev2 = {"round_id": R2, "anchor_dir": anchor_mod.REL_DIR, "anchors": {}}
rc = append("ROUND_CONSTITUTED", {"round_id": R2, "DUMMY": True,
    "constitution_annex_sha256": genesis_prev, "annex_a_sha256": A_hash,
    "gate_schema_profile_sha256": P_hash, "validators": annex["validators"]})
ev2["anchors"]["ROUND_CONSTITUTED"] = anchor_mod.anchor_head(rc["seq"], "ROUND_CONSTITUTED", rc["hash"]).get("anchor_commit")

corpus = {c["name"]: c for c in json.load(open(T + "/tests/corpus.json"))}
dummies = [{"trial_uid": "DUMMY-1", "raw": corpus["valid-full-contribution"]["raw"]},
           {"trial_uid": "DUMMY-2", "raw": corpus["invalid-not-json"]["raw"]}]
os.makedirs(T + "/evidence/dummy_trials_correction", exist_ok=True)
val_outputs = []
for d in dummies:
    rp = f"{T}/evidence/dummy_trials_correction/{d['trial_uid']}.response.txt"
    open(rp, "w").write(d["raw"])
    py = json.loads(run([sys.executable, T + "/validator_py/validate_py.py", rp]).stdout)
    js = json.loads(run(["node", T + "/validator_js/validate_js.js", rp]).stdout)
    val_outputs.append({"trial_uid": d["trial_uid"], "python": py, "ajv": js,
                        "agree": py["valid"] == js["valid"]})
    append("TRIAL_RECORDED", {"round_id": R2, "DUMMY": True, "trial_uid": d["trial_uid"],
        "layer1": {"annex_a_sha256": A_hash, "profile_sha256": P_hash},
        "layer2_response_sha256": sha(d["raw"])})
    append("VALIDATION_RECORDED", {"round_id": R2, "DUMMY": True, "trial_uid": d["trial_uid"],
        "python_valid": py["valid"], "ajv_valid": js["valid"], "agree": py["valid"] == js["valid"]})
json.dump(val_outputs, open(T + "/evidence/dummy_trials_correction/validator_outputs.json", "w"), indent=1)

manifest = {"round": R2, "DUMMY": True, "dummy_fixtures": True,
    "prompt_annex_a_sha256": A_hash, "profile_sha256": P_hash,
    "constitution_annex_sha256": genesis_prev,
    "responses_in_schedule_order": [{"trial_uid": d["trial_uid"], "sha256": sha(d["raw"])} for d in dummies],
    "validator_outputs_sha256": sha(json.dumps(val_outputs, sort_keys=True))}
mpath = T + "/evidence/freeze_manifest_correction_dummy.json"
json.dump(manifest, open(mpath, "w"), indent=1)
manifest_hash = sha(open(mpath, "rb").read())
ef = append("EVIDENCE_FROZEN", {"round_id": R2, "DUMMY": True, "manifest_sha256": manifest_hash})
ev2["anchors"]["EVIDENCE_FROZEN"] = anchor_mod.anchor_head(ef["seq"], "EVIDENCE_FROZEN", ef["hash"]).get("anchor_commit")

sys.path.insert(0, T + "/scoring")
import scoring
sheets, mapping = [], {}
for d, vo in zip(dummies, val_outputs):
    parsed = None
    try: parsed = json.loads(d["raw"])
    except Exception: pass
    sheet = scoring.make_sheet({"trial_uid": d["trial_uid"], "parsed": parsed,
                                "schema_valid": vo["python"]["valid"]}, "correction-demo-secret")
    sheet["examiner_fields_status"] = "DUMMY — build/correction demonstration; examiner judgment fields intentionally unscored"
    sheets.append(sheet); mapping[sheet["blind_ref"]] = d["trial_uid"]
json.dump(sheets, open(T + "/evidence/dummy_scoring_sheets_correction.json", "w"), indent=1)
json.dump(mapping, open(T + "/evidence/dummy_scoring_mapping_correction.json", "w"), indent=1)
sheets_hash = sha(open(T + "/evidence/dummy_scoring_sheets_correction.json", "rb").read())
sc = append("SCORING_COMPLETED", {"round_id": R2, "DUMMY": True, "sheets_sha256": sheets_hash})
sf = append("SCORING_FROZEN", {"round_id": R2, "DUMMY": True, "sheets_sha256": sheets_hash})
ev2["anchors"]["SCORING_FROZEN"] = anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"]).get("anchor_commit")

out2 = RT + "/work/examiner-out-correction.txt"
if os.path.exists(out2): os.unlink(out2)
r_ok = gt_release.release("correction-demo-examiner", out2)
ev2["release"] = {**r_ok, "material_hash_matches_packet": r_ok.get("material_sha256") == PACKET_SHA}
ev2["anchors"]["GROUND_TRUTH_ACCESSED"] = r_ok.get("access_anchor_commit")
l4 = append("LAYER4_RECORDED", {"round_id": R2, "DUMMY": True,
    "released_material_sha256": r_ok.get("material_sha256"), "packet_sha256": PACKET_SHA,
    "access_event_seq": r_ok.get("access_event_seq")})
ev2["chain_verify"] = ledger({"op": "verify"})
ev2["events"] = ledger({"op": "list"})["events"]
ev2["event_types_in_order"] = [e["type"] for e in ev2["events"]]
ev2["manifest_sha256"] = manifest_hash
json.dump(ev2, open(T + "/evidence/CD9_dummy_lifecycle.json", "w"), indent=1)
print("chain2 order:", ev2["event_types_in_order"])
print("chain2 release:", r_ok.get("released"), "| verify:", ev2["chain_verify"])

# ================= C-D5 boundary evidence =================
store = RT + "/ledger-store/sequence.jsonl"
client_copy = RT + "/work/ledger_client.py"
open(client_copy, "w").write(open(T + "/ledger/ledger_client.py").read())
os.chmod(client_copy, 0o644)
def as_agent(cmd):
    p = run(["runuser", "-u", "loomagent", "--"] + cmd)
    return {"returncode": p.returncode, "stdout": p.stdout.strip()[-300:], "stderr": p.stderr.strip()[-300:]}
ev5 = {"item": "C-D5 boundary evidence (against the chain-2 store, live)",
    "executing_identity": run(["runuser", "-u", "loomagent", "--", "id"]).stdout.strip(),
    "store_dir_listing": run(["ls", "-ld", RT + "/ledger-store"]).stdout.strip(),
    "store_file_listing": run(["ls", "-l", store]).stdout.strip(),
    "socket_listing": run(["ls", "-l", RT + "/sock"]).stdout.strip(),
    "direct_read": as_agent(["cat", store]),
    "direct_append": as_agent(["python3", "-c", "open('%s','a').write('x')" % store]),
    "direct_delete": as_agent(["rm", store]),
    "service_delete_op": as_agent(["python3", client_copy, "delete"]),
    "service_update_op": as_agent(["python3", client_copy, "update"]),
    "service_append_as_loomagent": as_agent(["python3", client_copy, "append", "BUILD_DEMO_NOTE",
        json.dumps({"round_id": R2, "DUMMY": True, "purpose": "C-D5 positive-path append via the service only"}),
        ts(), genesis_prev]),
    "chain_verify_after": ledger({"op": "verify"}),
    "note": "Direct attempts name the store path and fail at the store boundary (loomledger mode-700 directory / mode-660 file owned by loomledger). The service offers no delete/update operation. The only successful write is the service append."}
json.dump(ev5, open(T + "/evidence/CD5_boundary_evidence.json", "w"), indent=1)
print("C-D5:", json.dumps({k: (v.get("returncode") if isinstance(v, dict) else v) for k, v in ev5.items() if k in
      ("direct_read", "direct_append", "direct_delete")}), "| append:", ev5["service_append_as_loomagent"]["stdout"][:120])
