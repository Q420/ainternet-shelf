#!/usr/bin/env python3
"""Correction round 4: the narrow post-anchor digest-binding correction.

Vane's correction-3 examination (D7-A residual): ledger/gt_release.py
verified the selected packet's digest BEFORE the access append + anchor
(step 2.5), but the bytes actually released were read afterward (step 5)
and written to the examiner output without re-checking their digest --
a check/use gap: a writable selected file could change between
verification and release.

The corrected gt_release.py (declared change, the only pre-existing file
modified this round) ADDS a step 6: after GROUND_TRUTH_ACCESSED is
appended and anchored and the material is read, the digest of the exact
bytes read must equal the sealed packet hash from GROUND_TRUTH_SEALED
before anything is written to the examiner output. On mismatch nothing
is written; the access event and its anchor remain as the record of the
attempted access. Step 2.5's pre-verification is unchanged; D7-B is
untouched.

This runner builds ONE fresh valid DUMMY chain (correct SS13 order,
matching sheets-manifest binding, GROUND_TRUTH_SEALED recording the real
Annex D packet hash from the round-2 sealing record, SCORING_FROZEN
anchored), then invokes the release in FRESH SUBPROCESSES:

  (i)    no GT_RELEASE_FILE set (round-3 preserved case, re-run)
  (ii)   GT_RELEASE_FILE = the Annex A/C packet (round-3 preserved, re-run)
  (iii)  GT_RELEASE_FILE = an arbitrary readable file, the sealed
         stand-in (round-3 preserved case, re-run)
  (iv)   NEW: GT_RELEASE_FILE = a byte-exact swappable copy of the Annex
         D packet, invoked through tests/invoke_release_swap_once.py,
         which interposes on anchor.anchor_head: the real access anchor
         executes, then the copy's bytes are replaced with tampered
         bytes before the step-5 read. Pre-verification passes on the
         genuine bytes; the post-anchor digest must refuse the release.
  (pos)  GT_RELEASE_FILE = the Annex D packet (round-3 preserved, re-run)

Every payload carries a DUMMY marker and a distinct round id; no record
here is, or can be presented as, trial evidence. All prior rounds'
evidence is untouched (verified by the closing preservation check)."""
import hashlib, json, os, subprocess, sys, time

ANCHOR_DIR = "trials-anchors/correction4-postanchor-round"
os.environ["TRIALS_ANCHOR_DIR"] = ANCHOR_DIR

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = "/tmp/loom-trials-runtime"
GT_STORE = RT + "/gt-store"
ANNEX_D_PACKET = GT_STORE + "/annex-d-packet.txt"
AC_PACKET = GT_STORE + "/layer4-packet.txt"
STANDIN = GT_STORE + "/annex-d-sealed-standin.txt"
SWAPPABLE_COPY = GT_STORE + "/annex-d-packet-correction4-copy.txt"
TAMPERED = GT_STORE + "/tampered-content-correction4.txt"
INVOKER = T + "/tests/invoke_release_once.py"
SWAP_INVOKER = T + "/tests/invoke_release_swap_once.py"
SWAP_RECORD = RT + "/work/swap-record-correction4.json"

sys.path.insert(0, T + "/ledger")
from ledger_client import call as ledger
import anchor as anchor_mod
import gt_release
assert anchor_mod.REL_DIR == ANCHOR_DIR, anchor_mod.REL_DIR

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

# ================= Phase 0: packets + the swappable copy =================
sealing_ev = json.load(open(T + "/evidence/CD7A_annex_d_sealing.json"))
PACKET_SHA = sealing_ev["packet_sha256"]
AC_SHA = sealing_ev["round1_annex_a_c_packet_preserved"]["sha256sum_as_loomgt_after"].split()[0]
def loomgt_sha(path):
    r = run(["runuser", "-u", "loomgt", "--", "sha256sum", path])
    assert r.returncode == 0, r.stderr
    return r.stdout.split()[0]
phase0 = {"annex_d_packet": {"path": ANNEX_D_PACKET, "sha256_as_loomgt": loomgt_sha(ANNEX_D_PACKET),
                             "matches_round2_sealing_record": loomgt_sha(ANNEX_D_PACKET) == PACKET_SHA},
          "annex_a_c_packet": {"path": AC_PACKET, "sha256_as_loomgt": loomgt_sha(AC_PACKET),
                               "matches_round1_record": loomgt_sha(AC_PACKET) == AC_SHA},
          "standin": {"path": STANDIN, "sha256_as_loomgt": loomgt_sha(STANDIN)}}
assert phase0["annex_d_packet"]["matches_round2_sealing_record"], phase0
assert phase0["annex_a_c_packet"]["matches_round1_record"], phase0
STANDIN_SHA = phase0["standin"]["sha256_as_loomgt"]

# A byte-exact copy of the Annex D packet that the swap may rewrite (the
# sealed original is never touched), plus the tampered content. Both live
# in the gt-store, owned by loomgt, mode 600.
TAMPERED_TEXT = (
    "TAMPERED CONTENT -- correction round 4 swap test.\n"
    "These bytes are NOT the sealed Annex D ground-truth material.\n"
    "They were substituted for the selected packet's bytes after the\n"
    "access event was anchored and before the release read, to exercise\n"
    "the post-anchor digest binding. A correct gate releases NOTHING\n"
    "when the bytes it read hash to this content's digest instead of\n"
    "the sealed packet hash recorded in GROUND_TRUTH_SEALED.\n")
run(["cp", ANNEX_D_PACKET, SWAPPABLE_COPY], check=True)
with open(TAMPERED, "w") as f: f.write(TAMPERED_TEXT)
for p in (SWAPPABLE_COPY, TAMPERED):
    run(["chown", "loomgt:loomgt", p], check=True)
    os.chmod(p, 0o600)
phase0["swappable_copy"] = {"path": SWAPPABLE_COPY,
                            "sha256_as_loomgt": loomgt_sha(SWAPPABLE_COPY),
                            "byte_exact_copy_of_annex_d_packet": loomgt_sha(SWAPPABLE_COPY) == PACKET_SHA}
assert phase0["swappable_copy"]["byte_exact_copy_of_annex_d_packet"], phase0
TAMPERED_SHA = loomgt_sha(TAMPERED)
phase0["tampered_content"] = {"path": TAMPERED, "sha256_as_loomgt": TAMPERED_SHA,
                              "sha256_of_text_written": sha(TAMPERED_TEXT),
                              "digests_agree": TAMPERED_SHA == sha(TAMPERED_TEXT)}
assert phase0["tampered_content"]["digests_agree"], phase0
print("phase 0: Annex D packet matches the round-2 sealing record:", PACKET_SHA[:12],
      "| swappable copy byte-exact | tampered digest:", TAMPERED_SHA[:12])

# ================= Build the one valid dummy chain =================
reset_runtime()
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

R = "correction4-postanchor-round-DUMMY"
ev = {"item": "Correction round 4: post-anchor digest binding",
      "round_id": R, "anchor_dir": ANCHOR_DIR, "phase0_packets": phase0,
      "expected_packet_sha256_from_sealing_record": PACKET_SHA,
      "tampered_content_sha256": TAMPERED_SHA,
      "anchors": {}, "cases": {}}

rc = append("ROUND_CONSTITUTED", {"round_id": R, "DUMMY": True,
    "constitution_annex_sha256": genesis_prev,
    "purpose": "correction round 4 post-anchor binding tests only"})
ev["anchors"]["ROUND_CONSTITUTED"] = anchor_mod.anchor_head(rc["seq"], "ROUND_CONSTITUTED", rc["hash"]).get("anchor_commit")
append("GROUND_TRUTH_SEALED", {"round_id": R, "DUMMY": True,
    "act": "sealing of the Annex D ground-truth packet (D7-A), performed by ledger/seal_annex_d.py in correction round 2, before this chain was built",
    "packet_path": ANNEX_D_PACKET, "packet_sha256": PACKET_SHA,
    "packet_bytes": sealing_ev["packet_bytes"],
    "source_file": sealing_ev["source_file"], "source_sha256": sealing_ev["source_sha256"],
    "source_git_blob": sealing_ev["source_git_blob"],
    "extraction": sealing_ev["extraction"],
    "sealing_evidence": "evidence/CD7A_annex_d_sealing.json"})

corpus = {c["name"]: c for c in json.load(open(T + "/tests/corpus.json"))}
dummies = [{"trial_uid": "DUMMY-1", "raw": corpus["valid-full-contribution"]["raw"]},
           {"trial_uid": "DUMMY-2", "raw": corpus["invalid-not-json"]["raw"]}]
os.makedirs(T + "/evidence/dummy_trials_correction4", exist_ok=True)
val_outputs = []
for d in dummies:
    rp = f"{T}/evidence/dummy_trials_correction4/{d['trial_uid']}.response.txt"
    open(rp, "w").write(d["raw"])
    py = json.loads(run([sys.executable, T + "/validator_py/validate_py.py", rp]).stdout)
    js = json.loads(run(["node", T + "/validator_js/validate_js.js", rp]).stdout)
    val_outputs.append({"trial_uid": d["trial_uid"], "python": py, "ajv": js,
                        "agree": py["valid"] == js["valid"]})
    append("TRIAL_RECORDED", {"round_id": R, "DUMMY": True, "trial_uid": d["trial_uid"],
        "layer1": {"annex_a_sha256": A_hash, "profile_sha256": P_hash},
        "layer2_response_sha256": sha(d["raw"])})
    append("VALIDATION_RECORDED", {"round_id": R, "DUMMY": True, "trial_uid": d["trial_uid"],
        "python_valid": py["valid"], "ajv_valid": js["valid"], "agree": py["valid"] == js["valid"]})
json.dump(val_outputs, open(T + "/evidence/dummy_trials_correction4/validator_outputs.json", "w"), indent=1)

manifest = {"round": R, "DUMMY": True, "dummy_fixtures": True,
    "prompt_annex_a_sha256": A_hash, "profile_sha256": P_hash,
    "constitution_annex_sha256": genesis_prev,
    "responses_in_schedule_order": [{"trial_uid": d["trial_uid"], "sha256": sha(d["raw"])} for d in dummies],
    "validator_outputs_sha256": sha(json.dumps(val_outputs, sort_keys=True))}
mpath = T + "/evidence/freeze_manifest_correction4_dummy.json"
json.dump(manifest, open(mpath, "w"), indent=1)
manifest_hash = sha(open(mpath, "rb").read())
ef = append("EVIDENCE_FROZEN", {"round_id": R, "DUMMY": True, "manifest_sha256": manifest_hash})
ev["anchors"]["EVIDENCE_FROZEN"] = anchor_mod.anchor_head(ef["seq"], "EVIDENCE_FROZEN", ef["hash"]).get("anchor_commit")

sys.path.insert(0, T + "/scoring")
import scoring
sheets, mapping = [], {}
for d, vo in zip(dummies, val_outputs):
    parsed = None
    try: parsed = json.loads(d["raw"])
    except Exception: pass
    sheet = scoring.make_sheet({"trial_uid": d["trial_uid"], "parsed": parsed,
                                "schema_valid": vo["python"]["valid"]}, "correction4-demo-secret")
    sheet["examiner_fields_status"] = "DUMMY — correction round 4 demonstration; examiner judgment fields intentionally unscored"
    sheets.append(sheet); mapping[sheet["blind_ref"]] = d["trial_uid"]
json.dump(sheets, open(T + "/evidence/dummy_scoring_sheets_correction4.json", "w"), indent=1)
json.dump(mapping, open(T + "/evidence/dummy_scoring_mapping_correction4.json", "w"), indent=1)
sheets_hash = sha(open(T + "/evidence/dummy_scoring_sheets_correction4.json", "rb").read())
append("SCORING_COMPLETED", {"round_id": R, "DUMMY": True, "sheets_sha256": sheets_hash})
sf = append("SCORING_FROZEN", {"round_id": R, "DUMMY": True, "sheets_sha256": sheets_hash})
ev["anchors"]["SCORING_FROZEN"] = anchor_mod.anchor_head(sf["seq"], "SCORING_FROZEN", sf["hash"]).get("anchor_commit")
ev["sheets_manifest_sha256"] = sheets_hash
ev["chain_before_invocations"] = [e["type"] for e in ledger({"op": "list"})["events"]]
print("chain built:", ev["chain_before_invocations"])

# ================= Release invocations (fresh subprocess per case) =================
def invoke(name, selector, out_name, invoker=INVOKER, extra_env=None):
    out_path = RT + "/work/" + out_name
    if os.path.exists(out_path): os.unlink(out_path)
    if os.path.exists(SWAP_RECORD): os.unlink(SWAP_RECORD)
    head_before = ledger({"op": "head"})
    env = dict(os.environ)
    env["TRIALS_ANCHOR_DIR"] = ANCHOR_DIR
    if selector is None:
        env.pop("GT_RELEASE_FILE", None)
    else:
        env["GT_RELEASE_FILE"] = selector
    if extra_env: env.update(extra_env)
    p = run([sys.executable, invoker, "correction4-demo-examiner", out_path],
            env=env, timeout=600)
    parsed = None
    try: parsed = json.loads(p.stdout)
    except Exception: pass
    case = {"selector": "ABSENT (GT_RELEASE_FILE unset)" if selector is None else selector,
            "invoker": os.path.basename(invoker),
            "subprocess_returncode": p.returncode,
            "subprocess_stderr_tail": p.stderr[-300:] if p.returncode != 0 else "",
            "invocation": parsed,
            "head_before": head_before, "head_after": ledger({"op": "head"}),
            "material_released": os.path.exists(out_path)}
    if case["material_released"]:
        case["released_file_sha256"] = sha(open(out_path, "rb").read())
    if os.path.exists(SWAP_RECORD):
        case["swap_record_file"] = json.load(open(SWAP_RECORD))
    ev["cases"][name] = case
    r = (parsed or {}).get("result", {})
    print(name, "-> released:", r.get("released"), "| stage:", r.get("stage"),
          "| material:", case["material_released"],
          "| head:", head_before.get("seq"), "->", case["head_after"].get("seq"))
    return case

# ---- preserved round-3 cases, re-run unchanged against the corrected code ----
c1 = invoke("no_selector_set", None, "examiner-out-c4-nosel.txt")
assert c1["invocation"]["result"]["released"] is False
assert c1["invocation"]["result"]["stage"] == "packet-selection", c1
assert not c1["material_released"]
assert c1["head_before"] == c1["head_after"]

c2 = invoke("selector_is_annex_a_c_packet", AC_PACKET, "examiner-out-c4-ac.txt")
assert c2["invocation"]["result"]["released"] is False
assert c2["invocation"]["result"]["stage"] == "packet-binding", c2
assert c2["invocation"]["result"]["selected_packet_sha256"] == AC_SHA, c2
assert c2["invocation"]["result"]["expected_packet_sha256"] == PACKET_SHA, c2
assert not c2["material_released"]
assert c2["head_before"] == c2["head_after"]

c3 = invoke("selector_is_arbitrary_readable_file", STANDIN, "examiner-out-c4-standin.txt")
assert c3["invocation"]["result"]["released"] is False
assert c3["invocation"]["result"]["stage"] == "packet-binding", c3
assert c3["invocation"]["result"]["selected_packet_sha256"] == STANDIN_SHA, c3
assert not c3["material_released"]
assert c3["head_before"] == c3["head_after"]

# ---- NEW: the post-anchor swap case ----
c4 = invoke("post_anchor_swap", SWAPPABLE_COPY, "examiner-out-c4-swap.txt",
            invoker=SWAP_INVOKER,
            extra_env={"GT_SWAP_SOURCE": TAMPERED, "GT_SWAP_RECORD": SWAP_RECORD})
res4 = c4["invocation"]["result"]
sw = c4["invocation"]["swap"]
assert sw["interposed"] is True, c4
assert sw["selected_sha256_before_swap"] == PACKET_SHA, c4
assert sw["selected_sha256_after_swap"] == TAMPERED_SHA, c4
assert res4["released"] is False, c4
assert res4["stage"] == "post-anchor-binding", c4
assert res4["expected_packet_sha256"] == PACKET_SHA, c4
assert res4["post_anchor_read_sha256"] == TAMPERED_SHA, c4
assert not c4["material_released"]
assert c4["head_after"]["seq"] == c4["head_before"]["seq"] + 1, c4  # access event appended + retained
access_seq = res4["access_event_seq"]
assert access_seq == c4["head_after"]["seq"], c4
# the retained access event + its anchor, verified from the record itself
events_now = ledger({"op": "list"})["events"]
gta = [e for e in events_now if e["seq"] == access_seq and e["type"] == "GROUND_TRUTH_ACCESSED"]
assert len(gta) == 1, events_now
readback = anchor_mod.read_anchor(access_seq, "GROUND_TRUTH_ACCESSED")
rec, perr = gt_release.parse_anchor_record(readback)
verr = gt_release.validate_anchor_record(rec, gta[0]) if rec else perr
ev["swap_case_access_anchor_verification"] = {
    "access_event_seq": access_seq,
    "access_event_retained_in_sequence": True,
    "access_event_payload": gta[0]["payload"],
    "anchor_readback_parsed": rec is not None,
    "anchor_structural_validation": verr,
    "anchor_commit_in_result": res4.get("access_anchor_commit"),
    "anchor_commit_in_swap_record": sw.get("anchor_commit_returned_by_real_anchor")}
assert rec is not None and verr is None, ev["swap_case_access_anchor_verification"]
ev["anchors"]["GROUND_TRUTH_ACCESSED_swap_attempt"] = res4.get("access_anchor_commit")
print("swap case: access event seq", access_seq, "appended + anchored + retained; "
      "post-anchor digest refused the release")

# ---- preserved round-3 positive case, re-run unchanged ----
cpos = invoke("positive_annex_d_packet", ANNEX_D_PACKET, "examiner-out-c4-annexd.txt")
res = cpos["invocation"]["result"]
assert res["released"] is True, cpos
assert res["material_sha256"] == PACKET_SHA, cpos
assert res["post_anchor_read_sha256"] == PACKET_SHA, cpos
assert cpos["released_file_sha256"] == PACKET_SHA, cpos
ev["anchors"]["GROUND_TRUTH_ACCESSED"] = res.get("access_anchor_commit")
ev["positive_release"] = {**res,
    "released_file_sha256": cpos["released_file_sha256"],
    "material_hash_matches_annex_d_packet": res["material_sha256"] == PACKET_SHA}

l4 = append("LAYER4_RECORDED", {"round_id": R, "DUMMY": True,
    "released_material_sha256": res.get("material_sha256"), "packet_sha256": PACKET_SHA,
    "packet_kind": "Annex D sealed ground truth (correction round 4 positive re-run)",
    "access_event_seq": res.get("access_event_seq"),
    "swap_attempt": {"access_event_seq": access_seq, "stage": res4["stage"],
                     "expected_packet_sha256": PACKET_SHA,
                     "post_anchor_read_sha256": TAMPERED_SHA,
                     "material_released": False}})
ev["chain_verify"] = ledger({"op": "verify"})
ev["events"] = ledger({"op": "list"})["events"]
ev["event_types_in_order"] = [e["type"] for e in ev["events"]]
ev["manifest_sha256"] = manifest_hash
json.dump(ev, open(T + "/evidence/CD7D_post_anchor_binding.json", "w"), indent=1)
print("positive release:", res.get("released"), "| hash match:", ev["positive_release"]["material_hash_matches_annex_d_packet"],
      "| verify:", ev["chain_verify"])

# ================= Preservation check vs the pre-round baseline =================
baseline = json.load(open("/tmp/trials-baseline-round4.json"))
now = {}
for root, dirs, files in os.walk(T):
    for f in files:
        full = os.path.join(root, f)
        now[os.path.relpath(full, T)] = sha(open(full, "rb").read())
modified = sorted(p for p in baseline if p in now and baseline[p] != now[p])
deleted = sorted(p for p in baseline if p not in now)
added = sorted(p for p in now if p not in baseline)
declared = {"ledger/gt_release.py"}
violations = [p for p in modified + deleted
              if p not in declared and "__pycache__" not in p]
pres = {"item": "Correction round 4 preservation check (vs pre-round full-tree SHA-256 baseline)",
        "baseline_files": len(baseline),
        "modified": modified, "deleted": deleted,
        "declared_code_changes": sorted(declared & set(modified)),
        "pycache_regenerated": [p for p in modified if "__pycache__" in p],
        "added_files": added,
        "preservation_violations": violations,
        "original_submissions_preserved": not violations}
json.dump(pres, open(T + "/evidence/C4_preservation_check.json", "w"), indent=1)
print("preservation violations:", violations)
print("modified:", modified)
