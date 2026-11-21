#!/usr/bin/env python3
"""Gated ground-truth release (Rev 4 SS13c), FAIL-CLOSED.

CORRECTION ROUND (2026-11-21, per Vane's trials-build examination):
- The gate now requires the COMPLETE scoring order in the sequence:
  SCORING_COMPLETED, then a SCORING_FROZEN after it. The build round's
  successful release pattern (SCORING_FROZEN present, SCORING_COMPLETED
  absent) now REFUSES.
- The SCORING_FROZEN anchor is validated STRUCTURALLY before the gate
  accepts it: the shelf read-back is parsed, and the anchor record's fields
  (seq, type, head_hash, path, anchor) must match the sequence event. A
  malformed or mismatched anchor record REFUSES release.
- The sealed material is the ACTUAL layer-4 packet (assembled mechanically
  from the pinned Rev 9 authorities and sealed under the loomgt identity by
  ledger/seal_ground_truth.py), not the build round's stand-in. The stand-in
  file and its evidence remain preserved as build history.
  GT_RELEASE_FILE overrides the packet path (used by negative tests only to
  point at a nonexistent file; the release order is unchanged).

Order of operations — the release path cannot hand over material before its
own access record is secured:
  1. Verify the complete scoring order exists in the ledger sequence.
  2. Verify + structurally validate the SCORING_FROZEN shelf anchor.
  3. Append GROUND_TRUTH_ACCESSED to the sequence.
  4. Anchor the GROUND_TRUTH_ACCESSED head on the shelf (record checked).
  5. ONLY THEN read the sealed material (as the loomgt identity, the only
     identity that can read it) and write it to the examiner output path.
If any of steps 1-4 fails, the material is NOT read and NOT released.
Set GT_RELEASE_SABOTAGE_ANCHOR=1 to simulate an anchoring failure."""
import hashlib, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_client import call as ledger_call
import anchor as anchor_mod

GT_FILE = os.environ.get(
    "GT_RELEASE_FILE",
    "/tmp/loom-trials-runtime/gt-store/layer4-packet.txt")

def parse_anchor_record(readback):
    """Parse the GitHub read tool's output into the anchor record dict.
    Returns (record, None) or (None, why). Structural only: no field is
    trusted until validate_anchor_record checks it against the event."""
    if not readback:
        return None, "no read-back returned"
    try:
        outer = json.loads(readback)
        contents = outer["result"]["content"]
    except Exception as e:
        return None, "read-back envelope unparsable: %s" % e
    text = None
    for item in contents:
        if item.get("type") == "resource" and "text" in item.get("resource", {}):
            text = item["resource"]["text"]
        if item.get("type") == "text" and item.get("text", "").lstrip().startswith("{"):
            text = item["text"]
    if text is None:
        return None, "no anchor record text in read-back"
    try:
        rec = json.loads(text)
    except Exception as e:
        return None, "anchor record is not valid JSON: %s" % e
    if not isinstance(rec, dict):
        return None, "anchor record is not a JSON object"
    return rec, None

def validate_anchor_record(rec, event):
    """The anchor record must structurally match the sequence event it
    claims to anchor: same seq, same type, head_hash equal to the event's
    hash, the canonical anchor path for that seq/type, and the expected
    anchor repository. Returns None if valid, else a why string."""
    if rec.get("seq") != event["seq"]:
        return "anchor seq %r != event seq %r" % (rec.get("seq"), event["seq"])
    if rec.get("type") != event["type"]:
        return "anchor type %r != event type %r" % (rec.get("type"), event["type"])
    if rec.get("head_hash") != event["hash"]:
        return "anchor head_hash does not match the sequence head hash at that position"
    if rec.get("path") != anchor_mod.anchor_path(event["seq"], event["type"]):
        return "anchor path %r is not the canonical path for seq/type" % rec.get("path")
    if rec.get("anchor") != "Q420/ainternet-shelf":
        return "anchor repository %r is not Q420/ainternet-shelf" % rec.get("anchor")
    return None

def find_scoring_order(events):
    """Returns (completed_event, frozen_event, why). The complete order is:
    a SCORING_COMPLETED, then a SCORING_FROZEN strictly after it."""
    completed = None
    for e in events:
        if e["type"] == "SCORING_COMPLETED" and completed is None:
            completed = e
        if e["type"] == "SCORING_FROZEN" and completed is not None and e["seq"] > completed["seq"]:
            return completed, e, None
    types = [e["type"] for e in events]
    if "SCORING_FROZEN" in types and "SCORING_COMPLETED" not in types:
        return None, None, ("SCORING_FROZEN exists but SCORING_COMPLETED is absent: "
                            "the complete scoring order is not present")
    if completed is None:
        return None, None, "SCORING_COMPLETED does not exist in the sequence"
    return None, None, "no SCORING_FROZEN exists after SCORING_COMPLETED"

def release(examiner_id, out_path):
    events = ledger_call({"op": "list"})["events"]
    # step 1: the complete scoring order must be present
    completed, frozen, why = find_scoring_order(events)
    if frozen is None:
        return {"released": False, "stage": "gate", "why": why}
    # step 2: the SCORING_FROZEN anchor must be present AND structurally valid
    readback = anchor_mod.read_anchor(frozen["seq"], "SCORING_FROZEN")
    rec, perr = parse_anchor_record(readback)
    if rec is None:
        return {"released": False, "stage": "anchor-check",
                "why": "SCORING_FROZEN anchor could not be parsed: %s" % perr}
    verr = validate_anchor_record(rec, frozen)
    if verr:
        return {"released": False, "stage": "anchor-validation",
                "why": "SCORING_FROZEN anchor record failed structural validation: %s" % verr}
    # step 3: append the access record
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    app = ledger_call({"op": "append", "type": "GROUND_TRUTH_ACCESSED",
                       "payload": {"examiner": examiner_id,
                                   "scope": "layer-4 examination of the sealed ground truth (actual layer-4 packet, correction round)",
                                   "scoring_completed_seq": completed["seq"],
                                   "scoring_frozen_seq": frozen["seq"]},
                       "timestamp": ts, "genesis_prev": ""})
    if not app.get("ok"):
        return {"released": False, "stage": "append", "why": "GROUND_TRUTH_ACCESSED append failed: %s" % app}
    # step 4: anchor it — fail closed if this cannot be secured
    try:
        if os.environ.get("GT_RELEASE_SABOTAGE_ANCHOR") == "1":
            raise RuntimeError("simulated anchoring failure (fail-closed test)")
        arec = anchor_mod.anchor_head(app["seq"], "GROUND_TRUTH_ACCESSED", app["hash"])
        if arec.get("head_hash") != app["hash"] or arec.get("seq") != app["seq"]:
            raise RuntimeError("access anchor record does not match the appended access event")
    except Exception as e:
        return {"released": False, "stage": "anchor-access-record",
                "why": "GROUND_TRUTH_ACCESSED could not be anchored (%s); material NOT released" % e,
                "access_event_seq": app["seq"]}
    # step 5: only now is the material read (as loomgt) and released
    out = subprocess.run(["runuser", "-u", "loomgt", "--", "cat", GT_FILE],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return {"released": False, "stage": "read", "why": "sealed read failed: " + out.stderr[-200:]}
    with open(out_path, "w") as f: f.write(out.stdout)
    return {"released": True, "access_event_seq": app["seq"], "access_anchor_commit": arec.get("anchor_commit"),
            "material_sha256": hashlib.sha256(out.stdout.encode()).hexdigest(), "out_path": out_path,
            "gt_file": GT_FILE}

if __name__ == "__main__":
    print(json.dumps(release(sys.argv[1], sys.argv[2])))
