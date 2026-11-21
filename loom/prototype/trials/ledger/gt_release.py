#!/usr/bin/env python3
"""Gated ground-truth release (Rev 4 SS13c), FAIL-CLOSED.
Order of operations — the release path cannot hand over material before its
own access record is secured:
  1. Verify SCORING_FROZEN exists in the ledger sequence.
  2. Verify the SCORING_FROZEN head anchor is present on the shelf.
  3. Append GROUND_TRUTH_ACCESSED to the sequence.
  4. Anchor the GROUND_TRUTH_ACCESSED head on the shelf.
  5. ONLY THEN read the sealed material (as the loomgt identity, the only
     identity that can read it) and write it to the examiner output path.
If any of steps 1-4 fails, the material is NOT read and NOT released.
Set GT_RELEASE_SABOTAGE_ANCHOR=1 to simulate an anchoring failure (D7 iii)."""
import hashlib, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_client import call as ledger_call
import anchor as anchor_mod

GT_FILE = "/tmp/loom-trials-runtime/gt-store/annex-d-sealed-standin.txt"

def release(examiner_id, out_path):
    events = ledger_call({"op": "list"})["events"]
    types = [e["type"] for e in events]
    if "SCORING_FROZEN" not in types:
        return {"released": False, "stage": "gate", "why": "SCORING_FROZEN does not exist in the sequence"}
    sf = events[types.index("SCORING_FROZEN")]
    # step 2: the SCORING_FROZEN anchor must be present on the shelf
    readback = anchor_mod.read_anchor(sf["seq"], "SCORING_FROZEN")
    if not readback or sf["hash"] not in readback:
        return {"released": False, "stage": "anchor-check",
                "why": "SCORING_FROZEN anchor not found on the shelf for seq %d" % sf["seq"]}
    # step 3: append the access record
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    app = ledger_call({"op": "append", "type": "GROUND_TRUTH_ACCESSED",
                       "payload": {"examiner": examiner_id, "scope": "layer-4 examination of the sealed ground truth (build stand-in)"},
                       "timestamp": ts, "genesis_prev": ""})
    if not app.get("ok"):
        return {"released": False, "stage": "append", "why": "GROUND_TRUTH_ACCESSED append failed: %s" % app}
    # step 4: anchor it — fail closed if this cannot be secured
    try:
        if os.environ.get("GT_RELEASE_SABOTAGE_ANCHOR") == "1":
            raise RuntimeError("simulated anchoring failure (D7 iii)")
        rec = anchor_mod.anchor_head(app["seq"], "GROUND_TRUTH_ACCESSED", app["hash"])
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
    return {"released": True, "access_event_seq": app["seq"], "access_anchor_commit": rec.get("anchor_commit"),
            "material_sha256": hashlib.sha256(out.stdout.encode()).hexdigest(), "out_path": out_path}

if __name__ == "__main__":
    print(json.dumps(release(sys.argv[1], sys.argv[2])))
