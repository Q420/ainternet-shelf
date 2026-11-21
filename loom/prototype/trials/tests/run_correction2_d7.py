#!/usr/bin/env python3
"""Correction round 2 ledger work: D7-A (Annex D sealing, via
ledger/seal_annex_d.py) and D7-B (strengthened release gate: complete
SS13 order EVIDENCE_FROZEN -> SCORING_COMPLETED -> SCORING_FROZEN plus the
completed-scoring-sheets manifest binding).

Negative tests run on separate disposable DUMMY chains (fresh runtime per
configuration, own shelf anchor directory per chain); the positive
lifecycle runs on a final fresh chain of record. All releases target the
Annex D packet (GT_RELEASE_FILE). Every payload carries a DUMMY marker and
a distinct round id; no record here is, or can be presented as, trial
evidence. All round-1 and build-round evidence is untouched."""
import hashlib, json, os, subprocess, sys, time

# gt_release reads GT_RELEASE_FILE at import time: every release in this
# round operates on the Annex D packet sealed by ledger/seal_annex_d.py.
ANNEX_D_PACKET = "/tmp/loom-trials-runtime/gt-store/annex-d-packet.txt"
os.environ["GT_RELEASE_FILE"] = ANNEX_D_PACKET

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

def append(etype, payload):
    r = ledger({"op": "append", "type": etype, "payload": payload,
                "timestamp": ts(), "genesis_prev": genesis_prev})
    assert r.get("ok"), r
    return r

# ================= Phase 0: D7-A sealing of the Annex D packet =================
reset_runtime()
seal = run([sys.executable, T + "/ledger/seal_annex_d.py"])
assert seal.returncode == 0, seal.stdout + seal.stderr
sealing_ev = json.load(open(T + "/evidence/CD7A_annex_d_sealing.json"))
PACKET_SHA = sealing_ev["packet_sha256"]
print("D7-A sealed: packet", sealing_ev["packet_bytes"], "bytes, sha", PACKET_SHA[:12],
      "| A/C packet preserved:", sealing_ev["round1_annex_a_c_packet_preserved"]["unchanged"],
      "| denials:", {k: v["cat_returncode"] for k, v in sealing_ev["denial_tests"].items()})

# ================= D7-B negative tests (disposable chains) =================
H = sha("correction2 dummy completed scoring sheets")
H2 = sha("correction2 dummy DIFFERENT scoring sheets")
neg = {"item": "Correction round 2, D7-B: strengthened-gate negative tests",
       "target_packet": ANNEX_D_PACKET, "target_packet_sha256": PACKET_SHA,
       "tests": {}}

def fresh_chain(round_id, anchor_dir):
    anchor_mod.REL_DIR = anchor_dir
    reset_runtime()
    append("ROUND_CONSTITUTED", {"round_id": round_id, "DUMMY": True,
        "constitution_annex_sha256": genesis_prev,
        "purpose": "correction round 2 D7-B negative tests only"})

def attempt_release(round_id, out_name):
    out = RT + "/work/" + out_name
    if os.path.exists(out): os.unlink(out)
    head_before = ledger({"op": "head"})
    r = gt_release.release("correction2-demo-examiner", out)
    return {**r, "material_released": os.path.exists(out),
            "head_before": head_before, "head_after": ledger({"op": "head"}),
            "events": ledger({"op": "list"})["events"]}

def gate_case(name, round_id, builder):
    fresh_chain(round_id, "trials-anchors/correction2-neg-" + name)
    builder(round_id)
    neg["tests"][name] = attempt_release(round_id, "examiner-out-c2-%s.txt" % name)
    t = neg["tests"][name]
    print(name, "->", t.get("released"), t.get("stage"), "|", t.get("why"))

def b_missing_ef(r):
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("missing_evidence_frozen", "correction2-neg-missing-ef-DUMMY", b_missing_ef)

def b_ef_after_sc(r):
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("evidence_frozen_after_scoring_completed", "correction2-neg-ef-after-sc-DUMMY", b_ef_after_sc)

def b_mismatch(r):
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H2})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("mismatched_manifest_hashes", "correction2-neg-mismatch-DUMMY", b_mismatch)

def b_binding_absent(r):
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "note": "no manifest binding field"})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("binding_absent_on_scoring_completed", "correction2-neg-binding-absent-DUMMY", b_binding_absent)

def b_binding_empty(r):
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "sheets_sha256": ""})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("binding_empty_on_scoring_completed", "correction2-neg-binding-empty-DUMMY", b_binding_empty)

def b_binding_nonhash(r):
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    append("SCORING_COMPLETED", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": "not-a-hash"})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("binding_nonhash_on_scoring_frozen", "correction2-neg-binding-nonhash-DUMMY", b_binding_nonhash)

def b_sc_absent(r):
    append("EVIDENCE_FROZEN", {"round_id": r, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
    sf = append("SCORING_FROZEN", {"round_id": r, "DUMMY": True, "sheets_sha256": H})
    anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"])
gate_case("scoring_completed_absent", "correction2-neg-sc-absent-DUMMY", b_sc_absent)

# Shared valid chain for the anchor-validation + fail-closed tests.
R_AV = "correction2-neg-anchor-DUMMY"
fresh_chain(R_AV, "trials-anchors/correction2-neg-anchor")
append("EVIDENCE_FROZEN", {"round_id": R_AV, "DUMMY": True, "manifest_sha256": sha("c2 dummy freeze manifest")})
append("SCORING_COMPLETED", {"round_id": R_AV, "DUMMY": True, "sheets_sha256": H})
sf_av = append("SCORING_FROZEN", {"round_id": R_AV, "DUMMY": True, "sheets_sha256": H})
anchor_mod.anchor_head(sf_av["seq"], "SCORING_FROZEN", sf_av["hash"])
real_read_anchor = anchor_mod.read_anchor
def fake_readback(record_text):
    envelope = {"result": {"content": [
        {"text": "successfully downloaded text file (SHA: 0000)", "type": "text"},
        {"resource": {"mimeType": "text/plain; charset=utf-8", "text": record_text,
                      "uri": "repo://Q420/ainternet-shelf/contents/fake"}, "type": "resource"}]}}
    return json.dumps(envelope)
bad_rec = {"seq": sf_av["seq"], "type": "SCORING_FROZEN", "head_hash": "0" * 64,
           "path": anchor_mod.anchor_path(sf_av["seq"], "SCORING_FROZEN"),
           "anchor": "Q420/ainternet-shelf"}
anchor_mod.read_anchor = lambda seq, etype: fake_readback(json.dumps(bad_rec))
neg["tests"]["mismatched_anchor_record"] = attempt_release(R_AV, "examiner-out-c2-anchor.txt")
print("mismatched_anchor_record ->", neg["tests"]["mismatched_anchor_record"].get("released"),
      neg["tests"]["mismatched_anchor_record"].get("stage"))
anchor_mod.read_anchor = lambda seq, etype: "this is not a read-back envelope"
neg["tests"]["malformed_anchor_readback"] = attempt_release(R_AV, "examiner-out-c2-anchor.txt")
print("malformed_anchor_readback ->", neg["tests"]["malformed_anchor_readback"].get("released"),
      neg["tests"]["malformed_anchor_readback"].get("stage"))
anchor_mod.read_anchor = real_read_anchor
os.environ["GT_RELEASE_SABOTAGE_ANCHOR"] = "1"
neg["tests"]["fail_closed_anchor_sabotage_annex_d"] = attempt_release(R_AV, "examiner-out-c2-anchor.txt")
os.environ.pop("GT_RELEASE_SABOTAGE_ANCHOR")
neg["tests"]["fail_closed_anchor_sabotage_annex_d"]["events_after"] = \
    [e["type"] for e in ledger({"op": "list"})["events"]]
print("fail_closed_anchor_sabotage_annex_d ->",
      neg["tests"]["fail_closed_anchor_sabotage_annex_d"].get("released"),
      neg["tests"]["fail_closed_anchor_sabotage_annex_d"].get("stage"),
      "| material:", neg["tests"]["fail_closed_anchor_sabotage_annex_d"]["material_released"])
json.dump(neg, open(T + "/evidence/CD7B_gate_negatives.json", "w"), indent=1)

# ================= Positive lifecycle against the Annex D packet =================
anchor_mod.REL_DIR = "trials-anchors/correction2-dummy-round"
reset_runtime()
R2 = "correction2-dummy-round-DUMMY"
ev2 = {"round_id": R2, "anchor_dir": anchor_mod.REL_DIR, "anchors": {},
       "target_packet": ANNEX_D_PACKET, "target_packet_sha256": PACKET_SHA}
rc = append("ROUND_CONSTITUTED", {"round_id": R2, "DUMMY": True,
    "constitution_annex_sha256": genesis_prev, "annex_a_sha256": A_hash,
    "gate_schema_profile_sha256": P_hash, "validators": annex["validators"]})
ev2["anchors"]["ROUND_CONSTITUTED"] = anchor_mod.anchor_head(rc["seq"], "ROUND_CONSTITUTED", rc["hash"]).get("anchor_commit")
# the recorded sealing act for the Annex D packet (sealed in phase 0)
append("GROUND_TRUTH_SEALED", {"round_id": R2, "DUMMY": True,
    "act": "sealing of the Annex D ground-truth packet (D7-A), performed by ledger/seal_annex_d.py before this chain was built",
    "packet_path": ANNEX_D_PACKET, "packet_sha256": PACKET_SHA,
    "packet_bytes": sealing_ev["packet_bytes"],
    "source_file": sealing_ev["source_file"], "source_sha256": sealing_ev["source_sha256"],
    "source_git_blob": sealing_ev["source_git_blob"],
    "extraction": sealing_ev["extraction"],
    "sealing_evidence": "evidence/CD7A_annex_d_sealing.json"})

corpus = {c["name"]: c for c in json.load(open(T + "/tests/corpus.json"))}
dummies = [{"trial_uid": "DUMMY-1", "raw": corpus["valid-full-contribution"]["raw"]},
           {"trial_uid": "DUMMY-2", "raw": corpus["invalid-not-json"]["raw"]}]
os.makedirs(T + "/evidence/dummy_trials_correction2", exist_ok=True)
val_outputs = []
for d in dummies:
    rp = f"{T}/evidence/dummy_trials_correction2/{d['trial_uid']}.response.txt"
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
json.dump(val_outputs, open(T + "/evidence/dummy_trials_correction2/validator_outputs.json", "w"), indent=1)

manifest = {"round": R2, "DUMMY": True, "dummy_fixtures": True,
    "prompt_annex_a_sha256": A_hash, "profile_sha256": P_hash,
    "constitution_annex_sha256": genesis_prev,
    "responses_in_schedule_order": [{"trial_uid": d["trial_uid"], "sha256": sha(d["raw"])} for d in dummies],
    "validator_outputs_sha256": sha(json.dumps(val_outputs, sort_keys=True))}
mpath = T + "/evidence/freeze_manifest_correction2_dummy.json"
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
                                "schema_valid": vo["python"]["valid"]}, "correction2-demo-secret")
    sheet["examiner_fields_status"] = "DUMMY — correction round 2 demonstration; examiner judgment fields intentionally unscored"
    sheets.append(sheet); mapping[sheet["blind_ref"]] = d["trial_uid"]
json.dump(sheets, open(T + "/evidence/dummy_scoring_sheets_correction2.json", "w"), indent=1)
json.dump(mapping, open(T + "/evidence/dummy_scoring_mapping_correction2.json", "w"), indent=1)
sheets_hash = sha(open(T + "/evidence/dummy_scoring_sheets_correction2.json", "rb").read())
sc = append("SCORING_COMPLETED", {"round_id": R2, "DUMMY": True, "sheets_sha256": sheets_hash})
sf = append("SCORING_FROZEN", {"round_id": R2, "DUMMY": True, "sheets_sha256": sheets_hash})
ev2["anchors"]["SCORING_FROZEN"] = anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"]).get("anchor_commit")
ev2["sheets_manifest_sha256"] = sheets_hash

out2 = RT + "/work/examiner-out-correction2.txt"
if os.path.exists(out2): os.unlink(out2)
r_ok = gt_release.release("correction2-demo-examiner", out2)
ev2["release"] = {**r_ok, "material_hash_matches_annex_d_packet": r_ok.get("material_sha256") == PACKET_SHA}
ev2["anchors"]["GROUND_TRUTH_ACCESSED"] = r_ok.get("access_anchor_commit")
l4 = append("LAYER4_RECORDED", {"round_id": R2, "DUMMY": True,
    "released_material_sha256": r_ok.get("material_sha256"), "packet_sha256": PACKET_SHA,
    "packet_kind": "Annex D sealed ground truth (correction round 2, D7-A)",
    "access_event_seq": r_ok.get("access_event_seq")})
ev2["chain_verify"] = ledger({"op": "verify"})
ev2["events"] = ledger({"op": "list"})["events"]
ev2["event_types_in_order"] = [e["type"] for e in ev2["events"]]
ev2["manifest_sha256"] = manifest_hash
json.dump(ev2, open(T + "/evidence/CD7_positive_lifecycle.json", "w"), indent=1)
print("positive order:", ev2["event_types_in_order"])
print("positive release:", r_ok.get("released"), "| hash match:", ev2["release"]["material_hash_matches_annex_d_packet"],
      "| verify:", ev2["chain_verify"])

# ================= Preservation check vs the pre-round baseline =================
baseline = {}
for line in open("/tmp/trials-baseline-round2.txt"):
    h, p = line.rstrip("\n").split("  ", 1)
    baseline[p[2:] if p.startswith("./") else p] = h  # strip leading ./
now = {}
for root, dirs, files in os.walk(T):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, T)
        now[rel] = sha(open(full, "rb").read())
modified = sorted(p for p in baseline if p in now and baseline[p] != now[p])
deleted = sorted(p for p in baseline if p not in now)
added = sorted(p for p in now if p not in baseline)
declared = {"ledger/gt_release.py"}
violations = [p for p in modified + deleted
              if p not in declared and "__pycache__" not in p]
pres = {"item": "Correction round 2 preservation check (vs pre-round full-tree SHA-256 baseline)",
        "baseline_files": len(baseline),
        "modified": modified, "deleted": deleted,
        "declared_code_changes": sorted(declared & set(modified)),
        "pycache_regenerated": [p for p in modified if "__pycache__" in p],
        "added_files": added,
        "preservation_violations": violations,
        "original_submissions_preserved": not violations}
json.dump(pres, open(T + "/evidence/C2_preservation_check.json", "w"), indent=1)
print("preservation violations:", violations)
print("modified:", modified)
