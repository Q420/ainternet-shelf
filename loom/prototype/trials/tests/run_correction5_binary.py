#!/usr/bin/env python3
"""Correction round 5: the narrow binary post-anchor read correction.

Vane's correction-4 examination (D7-A residual): round 4's step 5 read
the sealed material with subprocess text mode and step 6 hashed
out.stdout.encode(). Text mode decodes the returned bytes and performs
newline normalization, so the digest was not byte-exact, and the
examiner output was also written in text mode. Bytes differing only in
ways text mode normalizes (LF vs CRLF) could pass the check while
different bytes were released.

The corrected gt_release.py (declared change, the only pre-existing
file modified this round) makes steps 5-6 binary end to end: step 5
captures the actual returned bytes (no text=True) into a bytes buffer;
step 6 hashes those bytes directly; on success that exact same verified
buffer is written to the examiner output in binary mode -- no reread,
no transformation. Nothing else changes behaviour; D7-B is untouched.

This runner builds ONE fresh valid DUMMY chain (correct SS13 order,
matching sheets-manifest binding, GROUND_TRUTH_SEALED recording the
real Annex D packet hash from the round-2 sealing record,
SCORING_FROZEN anchored), then invokes the release in FRESH
SUBPROCESSES:

  (i)    no GT_RELEASE_FILE set (round-3 preserved case, re-run)
  (ii)   GT_RELEASE_FILE = the Annex A/C packet (round-3 preserved, re-run)
  (iii)  GT_RELEASE_FILE = an arbitrary readable file, the sealed
         stand-in (round-3 preserved case, re-run)
  (iv)   round-4 mutation case, re-run unchanged: GT_RELEASE_FILE = a
         byte-exact swappable copy of the Annex D packet, invoked
         through tests/invoke_release_swap_once.py with the SAME
         tampered source as round 4; the real access anchor executes,
         then the copy's bytes are replaced with the tampered bytes
         before the post-anchor read. Must refuse at post-anchor-binding.
  (v)    NEW: LF-to-CRLF swap. GT_RELEASE_FILE = a second byte-exact
         swappable copy; the swap source is the Annex D packet's bytes
         with every LF replaced by CRLF -- a change text mode would
         normalize away (phase 0 records that a text-mode decode +
         re-encode of the variant reproduces the packet digest, i.e.
         the round-4 code would NOT have detected this change). The
         binary digest must detect it: refusal at post-anchor-binding,
         no examiner output, access event + anchor retained.
  (pos)  GT_RELEASE_FILE = the Annex D packet (round-3 preserved,
         re-run): released; the released file read back as RAW BYTES
         must hash to the sealed packet hash.

Every payload carries a DUMMY marker and a distinct round id; no record
here is, or can be presented as, trial evidence. All prior rounds'
evidence is untouched (verified by the closing preservation check)."""
import hashlib, io, json, os, subprocess, sys, time

ANCHOR_DIR = "trials-anchors/correction5-binary-round"
os.environ["TRIALS_ANCHOR_DIR"] = ANCHOR_DIR

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RT = "/tmp/loom-trials-runtime"
GT_STORE = RT + "/gt-store"
ANNEX_D_PACKET = GT_STORE + "/annex-d-packet.txt"
AC_PACKET = GT_STORE + "/layer4-packet.txt"
STANDIN = GT_STORE + "/annex-d-sealed-standin.txt"
SWAPPABLE_COPY = GT_STORE + "/annex-d-packet-correction5-copy.txt"
CRLF_COPY = GT_STORE + "/annex-d-packet-correction5-crlf-copy.txt"
CRLF_VARIANT = GT_STORE + "/annex-d-packet-crlf-variant.txt"
TAMPERED_R4 = GT_STORE + "/tampered-content-correction4.txt"
INVOKER = T + "/tests/invoke_release_once.py"
SWAP_INVOKER = T + "/tests/invoke_release_swap_once.py"
SWAP_RECORD = RT + "/work/swap-record-correction5.json"

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

# ================= Phase 0: packets, swappable copies, CRLF variant =================
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
TAMPERED_SHA = loomgt_sha(TAMPERED_R4)
phase0["round4_tampered_source_reused_unchanged"] = {
    "path": TAMPERED_R4, "sha256_as_loomgt": TAMPERED_SHA,
    "matches_round4_record": TAMPERED_SHA == "5b27e5f2b343021f3fdd332d8a38409b05984fd2fc0217357ad624e520f42527"}
assert phase0["round4_tampered_source_reused_unchanged"]["matches_round4_record"], phase0

# Two byte-exact copies of the Annex D packet that the swaps may rewrite
# (the sealed original is never touched), plus the CRLF variant. All live
# in the gt-store, owned by loomgt, mode 600.
packet_bytes = open(ANNEX_D_PACKET, "rb").read()
assert sha(packet_bytes) == PACKET_SHA
assert b"\r" not in packet_bytes, "packet is not pure-LF; CRLF construction would be ambiguous"
CRLF_BYTES = packet_bytes.replace(b"\n", b"\r\n")
CRLF_SHA = sha(CRLF_BYTES)
assert CRLF_SHA != PACKET_SHA
# What the round-4 (text-mode) step 6 would have computed over the CRLF
# bytes: subprocess text mode decodes with universal-newlines translation
# (CRLF -> LF) and the old code hashed the re-encoded string. Simulated
# here with the same stdlib text wrapper, recorded as a simulation --
# it shows the old check would NOT have detected this byte change.
sim_text = io.TextIOWrapper(io.BytesIO(CRLF_BYTES), encoding="utf-8").read()
SIM_SHA = sha(sim_text.encode("utf-8"))
for src, dst in ((ANNEX_D_PACKET, SWAPPABLE_COPY), (ANNEX_D_PACKET, CRLF_COPY)):
    run(["cp", src, dst], check=True)
with open(CRLF_VARIANT, "wb") as f: f.write(CRLF_BYTES)
for p in (SWAPPABLE_COPY, CRLF_COPY, CRLF_VARIANT):
    run(["chown", "loomgt:loomgt", p], check=True)
    os.chmod(p, 0o600)
phase0["swappable_copy_mutation_rerun"] = {"path": SWAPPABLE_COPY,
    "sha256_as_loomgt": loomgt_sha(SWAPPABLE_COPY),
    "byte_exact_copy_of_annex_d_packet": loomgt_sha(SWAPPABLE_COPY) == PACKET_SHA}
phase0["swappable_copy_crlf"] = {"path": CRLF_COPY,
    "sha256_as_loomgt": loomgt_sha(CRLF_COPY),
    "byte_exact_copy_of_annex_d_packet": loomgt_sha(CRLF_COPY) == PACKET_SHA}
phase0["crlf_variant"] = {"path": CRLF_VARIANT,
    "construction": "Annex D packet bytes with every LF (0x0A) replaced by CRLF (0x0D 0x0A); the packet is pure LF (no CR anywhere), so the change is exactly LF-to-CRLF",
    "packet_bytes": len(packet_bytes), "variant_bytes": len(CRLF_BYTES),
    "lf_count": packet_bytes.count(b"\n"),
    "sha256_as_loomgt": loomgt_sha(CRLF_VARIANT),
    "sha256_computed_by_runner": CRLF_SHA,
    "differs_from_packet": CRLF_SHA != PACKET_SHA,
    "old_text_mode_simulation": {
        "method": "io.TextIOWrapper over the variant bytes (universal-newlines decode, as subprocess text=True performs), then .encode('utf-8') and SHA-256 -- a simulation of the round-4 step-6 computation, not a run of the old code",
        "simulated_round4_step6_sha256": SIM_SHA,
        "equals_packet_sha256": SIM_SHA == PACKET_SHA,
        "meaning": "the round-4 text-mode check would have computed the packet digest over these changed bytes and released; the binary check must refuse"}}
assert phase0["swappable_copy_mutation_rerun"]["byte_exact_copy_of_annex_d_packet"], phase0
assert phase0["swappable_copy_crlf"]["byte_exact_copy_of_annex_d_packet"], phase0
assert phase0["crlf_variant"]["sha256_as_loomgt"] == CRLF_SHA, phase0
assert phase0["crlf_variant"]["old_text_mode_simulation"]["equals_packet_sha256"], phase0
print("phase 0: Annex D packet matches the round-2 sealing record:", PACKET_SHA[:12],
      "| copies byte-exact | CRLF variant:", CRLF_SHA[:12],
      "| text-mode simulation reproduces packet digest:", SIM_SHA == PACKET_SHA)

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

R = "correction5-binary-round-DUMMY"
ev = {"item": "Correction round 5: binary post-anchor read",
      "round_id": R, "anchor_dir": ANCHOR_DIR, "phase0_packets": phase0,
      "expected_packet_sha256_from_sealing_record": PACKET_SHA,
      "tampered_content_sha256": TAMPERED_SHA,
      "crlf_variant_sha256": CRLF_SHA,
      "anchors": {}, "cases": {}}

rc = append("ROUND_CONSTITUTED", {"round_id": R, "DUMMY": True,
    "constitution_annex_sha256": genesis_prev,
    "purpose": "correction round 5 binary-read tests only"})
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
os.makedirs(T + "/evidence/dummy_trials_correction5", exist_ok=True)
val_outputs = []
for d in dummies:
    rp = f"{T}/evidence/dummy_trials_correction5/{d['trial_uid']}.response.txt"
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
json.dump(val_outputs, open(T + "/evidence/dummy_trials_correction5/validator_outputs.json", "w"), indent=1)

manifest = {"round": R, "DUMMY": True, "dummy_fixtures": True,
    "prompt_annex_a_sha256": A_hash, "profile_sha256": P_hash,
    "constitution_annex_sha256": genesis_prev,
    "responses_in_schedule_order": [{"trial_uid": d["trial_uid"], "sha256": sha(d["raw"])} for d in dummies],
    "validator_outputs_sha256": sha(json.dumps(val_outputs, sort_keys=True))}
mpath = T + "/evidence/freeze_manifest_correction5_dummy.json"
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
                                "schema_valid": vo["python"]["valid"]}, "correction5-demo-secret")
    sheet["examiner_fields_status"] = "DUMMY — correction round 5 demonstration; examiner judgment fields intentionally unscored"
    sheets.append(sheet); mapping[sheet["blind_ref"]] = d["trial_uid"]
json.dump(sheets, open(T + "/evidence/dummy_scoring_sheets_correction5.json", "w"), indent=1)
json.dump(mapping, open(T + "/evidence/dummy_scoring_mapping_correction5.json", "w"), indent=1)
sheets_hash = sha(open(T + "/evidence/dummy_scoring_sheets_correction5.json", "rb").read())
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
    p = run([sys.executable, invoker, "correction5-demo-examiner", out_path],
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
        raw = open(out_path, "rb").read()
        case["released_file_sha256_raw_bytes"] = sha(raw)
        case["released_file_bytes"] = len(raw)
    if os.path.exists(SWAP_RECORD):
        case["swap_record_file"] = json.load(open(SWAP_RECORD))
    ev["cases"][name] = case
    r = (parsed or {}).get("result", {})
    print(name, "-> released:", r.get("released"), "| stage:", r.get("stage"),
          "| material:", case["material_released"],
          "| head:", head_before.get("seq"), "->", case["head_after"].get("seq"))
    return case

def verify_retained_access(case, key):
    """The refused attempt's GROUND_TRUTH_ACCESSED event must remain in
    the sequence, with its shelf anchor read back and structurally
    validated by the gate's own functions."""
    res = case["invocation"]["result"]
    access_seq = res["access_event_seq"]
    assert access_seq == case["head_after"]["seq"], case
    events_now = ledger({"op": "list"})["events"]
    gta = [e for e in events_now if e["seq"] == access_seq and e["type"] == "GROUND_TRUTH_ACCESSED"]
    assert len(gta) == 1, events_now
    readback = anchor_mod.read_anchor(access_seq, "GROUND_TRUTH_ACCESSED")
    rec, perr = gt_release.parse_anchor_record(readback)
    verr = gt_release.validate_anchor_record(rec, gta[0]) if rec else perr
    record = {"access_event_seq": access_seq,
              "access_event_retained_in_sequence": True,
              "access_event_payload": gta[0]["payload"],
              "anchor_readback_parsed": rec is not None,
              "anchor_structural_validation": verr,
              "anchor_commit_in_result": res.get("access_anchor_commit"),
              "anchor_commit_in_swap_record": case["invocation"]["swap"].get("anchor_commit_returned_by_real_anchor")}
    assert rec is not None and verr is None, record
    ev[key] = record
    return record

# ---- preserved round-3 cases, re-run unchanged against the corrected code ----
c1 = invoke("no_selector_set", None, "examiner-out-c5-nosel.txt")
assert c1["invocation"]["result"]["released"] is False
assert c1["invocation"]["result"]["stage"] == "packet-selection", c1
assert not c1["material_released"]
assert c1["head_before"] == c1["head_after"]

c2 = invoke("selector_is_annex_a_c_packet", AC_PACKET, "examiner-out-c5-ac.txt")
assert c2["invocation"]["result"]["released"] is False
assert c2["invocation"]["result"]["stage"] == "packet-binding", c2
assert c2["invocation"]["result"]["selected_packet_sha256"] == AC_SHA, c2
assert c2["invocation"]["result"]["expected_packet_sha256"] == PACKET_SHA, c2
assert not c2["material_released"]
assert c2["head_before"] == c2["head_after"]

c3 = invoke("selector_is_arbitrary_readable_file", STANDIN, "examiner-out-c5-standin.txt")
assert c3["invocation"]["result"]["released"] is False
assert c3["invocation"]["result"]["stage"] == "packet-binding", c3
assert c3["invocation"]["result"]["selected_packet_sha256"] == STANDIN_SHA, c3
assert not c3["material_released"]
assert c3["head_before"] == c3["head_after"]

# ---- preserved round-4 mutation case, re-run unchanged ----
c4 = invoke("post_anchor_swap_rerun", SWAPPABLE_COPY, "examiner-out-c5-swap.txt",
            invoker=SWAP_INVOKER,
            extra_env={"GT_SWAP_SOURCE": TAMPERED_R4, "GT_SWAP_RECORD": SWAP_RECORD})
res4 = c4["invocation"]["result"]
sw4 = c4["invocation"]["swap"]
assert sw4["interposed"] is True, c4
assert sw4["selected_sha256_before_swap"] == PACKET_SHA, c4
assert sw4["selected_sha256_after_swap"] == TAMPERED_SHA, c4
assert res4["released"] is False, c4
assert res4["stage"] == "post-anchor-binding", c4
assert res4["expected_packet_sha256"] == PACKET_SHA, c4
assert res4["post_anchor_read_sha256"] == TAMPERED_SHA, c4
assert not c4["material_released"]
assert c4["head_after"]["seq"] == c4["head_before"]["seq"] + 1, c4
verify_retained_access(c4, "swap_rerun_access_anchor_verification")
ev["anchors"]["GROUND_TRUTH_ACCESSED_swap_rerun_attempt"] = res4.get("access_anchor_commit")
print("mutation re-run: access event seq", res4["access_event_seq"],
      "appended + anchored + retained; post-anchor digest refused the release")

# ---- NEW: the LF-to-CRLF post-anchor swap case ----
c5 = invoke("post_anchor_crlf_swap", CRLF_COPY, "examiner-out-c5-crlf.txt",
            invoker=SWAP_INVOKER,
            extra_env={"GT_SWAP_SOURCE": CRLF_VARIANT, "GT_SWAP_RECORD": SWAP_RECORD})
res5 = c5["invocation"]["result"]
sw5 = c5["invocation"]["swap"]
assert sw5["interposed"] is True, c5
assert sw5["selected_sha256_before_swap"] == PACKET_SHA, c5  # pre-verification passed on genuine bytes
assert sw5["selected_sha256_after_swap"] == CRLF_SHA, c5
assert res5["released"] is False, c5
assert res5["stage"] == "post-anchor-binding", c5
assert res5["expected_packet_sha256"] == PACKET_SHA, c5
assert res5["post_anchor_read_sha256"] == CRLF_SHA, c5  # the binary digest saw the CRLF bytes
assert not c5["material_released"]  # no examiner output produced
assert c5["head_after"]["seq"] == c5["head_before"]["seq"] + 1, c5
verify_retained_access(c5, "crlf_case_access_anchor_verification")
ev["anchors"]["GROUND_TRUTH_ACCESSED_crlf_attempt"] = res5.get("access_anchor_commit")
ev["crlf_case_summary"] = {
    "selected_file_before_swap_sha256": sw5["selected_sha256_before_swap"],
    "selected_file_after_swap_sha256": sw5["selected_sha256_after_swap"],
    "expected_packet_sha256": PACKET_SHA,
    "post_anchor_read_sha256": res5["post_anchor_read_sha256"],
    "binary_digest_detected_change": res5["post_anchor_read_sha256"] == CRLF_SHA != PACKET_SHA,
    "old_text_mode_would_have_computed": SIM_SHA,
    "old_text_mode_would_have_released": SIM_SHA == PACKET_SHA,
    "stage": res5["stage"], "material_released": False}
print("CRLF case: access event seq", res5["access_event_seq"],
      "appended + anchored + retained; binary digest detected the LF->CRLF change; nothing released")

# ---- preserved round-3 positive case, re-run unchanged ----
cpos = invoke("positive_annex_d_packet", ANNEX_D_PACKET, "examiner-out-c5-annexd.txt")
res = cpos["invocation"]["result"]
assert res["released"] is True, cpos
assert res["material_sha256"] == PACKET_SHA, cpos
assert res["post_anchor_read_sha256"] == PACKET_SHA, cpos
# the released file, read back as RAW BYTES, must hash to the packet hash
assert cpos["released_file_sha256_raw_bytes"] == PACKET_SHA, cpos
assert cpos["released_file_bytes"] == len(packet_bytes), cpos
ev["anchors"]["GROUND_TRUTH_ACCESSED"] = res.get("access_anchor_commit")
ev["positive_release"] = {**res,
    "released_file_sha256_raw_bytes": cpos["released_file_sha256_raw_bytes"],
    "released_file_bytes": cpos["released_file_bytes"],
    "material_hash_matches_annex_d_packet": res["material_sha256"] == PACKET_SHA}

l4 = append("LAYER4_RECORDED", {"round_id": R, "DUMMY": True,
    "released_material_sha256": res.get("material_sha256"), "packet_sha256": PACKET_SHA,
    "packet_kind": "Annex D sealed ground truth (correction round 5 positive re-run)",
    "access_event_seq": res.get("access_event_seq"),
    "swap_attempt_rerun": {"access_event_seq": res4["access_event_seq"], "stage": res4["stage"],
                     "expected_packet_sha256": PACKET_SHA,
                     "post_anchor_read_sha256": TAMPERED_SHA,
                     "material_released": False},
    "crlf_attempt": {"access_event_seq": res5["access_event_seq"], "stage": res5["stage"],
                     "expected_packet_sha256": PACKET_SHA,
                     "post_anchor_read_sha256": CRLF_SHA,
                     "material_released": False}})
ev["chain_verify"] = ledger({"op": "verify"})
ev["events"] = ledger({"op": "list"})["events"]
ev["event_types_in_order"] = [e["type"] for e in ev["events"]]
ev["manifest_sha256"] = manifest_hash
json.dump(ev, open(T + "/evidence/CD7E_binary_read.json", "w"), indent=1)
print("positive release:", res.get("released"),
      "| released file raw-bytes hash match:", ev["positive_release"]["material_hash_matches_annex_d_packet"],
      "| verify:", ev["chain_verify"])

# ================= Preservation check vs the pre-round baseline =================
baseline = json.load(open("/tmp/trials-baseline-round5.json"))
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
pres = {"item": "Correction round 5 preservation check (vs pre-round full-tree SHA-256 baseline)",
        "baseline_files": len(baseline),
        "modified": modified, "deleted": deleted,
        "declared_code_changes": sorted(declared & set(modified)),
        "pycache_regenerated": [p for p in modified if "__pycache__" in p],
        "added_files": added,
        "preservation_violations": violations,
        "original_submissions_preserved": not violations}
json.dump(pres, open(T + "/evidence/C5_preservation_check.json", "w"), indent=1)
print("preservation violations:", violations)
print("modified:", modified)
