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

CORRECTION ROUND 3 (2026-11-21, per Vane's correction-2 examination, D7-A
residual): PACKET SELECTION. The module previously defaulted GT_FILE to
gt-store/layer4-packet.txt (the Annex A/C packet) when GT_RELEASE_FILE was
unset, so a release invocation without that setting silently selected the
wrong packet; the round-2 runner avoided it only by setting the variable
before import. Selection is now EXPLICIT (chosen shape (b) of the round-3
dispatch): GT_RELEASE_FILE must be set, and its absence fails closed at
the packet-selection stage before the sequence is even consulted. In
addition, before any release the gate hashes the selected file (as the
loomgt identity) and requires equality with the Annex D packet hash
recorded in the sequence's GROUND_TRUTH_SEALED event. A readable-but-wrong
file -- the Annex A/C packet, or any other file -- therefore never
releases: selection by filename alone is not trusted.

CORRECTION ROUND 2 (2026-11-21, per Vane's correction examination, D7-B):
- The gate now verifies the COMPLETE SS13 order in the sequence:
  EVIDENCE_FROZEN -> SCORING_COMPLETED -> SCORING_FROZEN, each present, in
  that relative order. Raw evidence must be frozen before any scoring
  begins; the round-1 gate did not enforce EVIDENCE_FROZEN's position.
- It also verifies the MANIFEST BINDING: SCORING_COMPLETED and
  SCORING_FROZEN must bind the SAME non-empty completed-scoring-sheets
  manifest hash (a well-formed SHA-256 in the recorded binding field).
  Two correctly ordered event names referring to different scoring
  artifacts no longer pass. Absent, out-of-order, or inconsistently bound
  sequences REFUSE, with the reason recorded in the result.

Sealed packets (D7-A): GT_RELEASE_FILE selects the sealed packet the
release operates on, and it must be set explicitly -- there is no default
(correction round 3). The correction round 1 packet
(gt-store/layer4-packet.txt) contains Annex A + Annex C extracts --
preserved build history, NOT the sealed ground truth, and it can no
longer be selected by omission. The actual sealed ground truth is the
Annex D packet (gt-store/annex-d-packet.txt), sealed under the loomgt
identity by ledger/seal_annex_d.py. Whichever file is selected, the gate
verifies its SHA-256 against the packet hash recorded in the sequence's
GROUND_TRUTH_SEALED event before releasing (see step 2.5 below). The
build round's stand-in file and its evidence remain preserved as build
history.

Order of operations — the release path cannot hand over material before its
own access record is secured:
  0. Verify the packet selection is explicit (GT_RELEASE_FILE set).
  1. Verify the complete scoring order + manifest binding in the sequence.
  2. Verify + structurally validate the SCORING_FROZEN shelf anchor.
  2.5. Verify the selected packet: hash it (as loomgt) and require
     equality with the Annex D packet hash recorded in the sequence's
     GROUND_TRUTH_SEALED event.
  3. Append GROUND_TRUTH_ACCESSED to the sequence.
  4. Anchor the GROUND_TRUTH_ACCESSED head on the shelf (record checked).
  5. ONLY THEN read the sealed material (as the loomgt identity, the only
     identity that can read it) and write it to the examiner output path.
If any of steps 0-4 fails, the material is NOT read and NOT released.
Set GT_RELEASE_SABOTAGE_ANCHOR=1 to simulate an anchoring failure."""
import hashlib, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger_client import call as ledger_call
import anchor as anchor_mod

# Correction round 3: NO default packet. Selection is explicit via
# GT_RELEASE_FILE; when the variable is absent, GT_FILE is None and
# release() fails closed at the packet-selection stage. (Previously this
# defaulted to gt-store/layer4-packet.txt -- the Annex A/C packet -- so an
# invocation without the setting silently selected the wrong packet.)
GT_FILE_EXPLICIT = "GT_RELEASE_FILE" in os.environ
GT_FILE = os.environ.get("GT_RELEASE_FILE")

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

# The completed-scoring-sheets manifest hash is recorded in the scoring
# events' payloads under the first of these fields present (the ledger's
# recorded convention is "sheets_sha256", as in the correction round 1
# dummy lifecycle). The binding value must be a well-formed SHA-256.
MANIFEST_KEYS = ("sheets_sha256", "sheets_manifest_sha256",
                 "completed_sheets_manifest_sha256")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

def manifest_binding(event):
    """Returns (value, status, detail): status is "ok", "missing" (no
    binding field in the payload), or "malformed" (field present but the
    value is empty, not a string, or not a well-formed SHA-256)."""
    payload = event.get("payload") or {}
    for key in MANIFEST_KEYS:
        if key in payload:
            v = payload[key]
            if not isinstance(v, str) or not v:
                return None, "malformed", ("field %r is present but its value is "
                                            "empty or not a string" % key)
            if not _SHA256_RE.match(v):
                return None, "malformed", ("field %r value is not a well-formed "
                                            "SHA-256 hash" % key)
            return v, "ok", key
    return None, "missing", "no completed-scoring-sheets manifest hash field in the payload"

def find_scoring_order(events):
    """Returns (evidence_frozen, completed, frozen, manifest_sha256, why).

    The complete SS13 order, verified in full:
      EVIDENCE_FROZEN -> SCORING_COMPLETED -> SCORING_FROZEN
    each present, in that relative order, AND the SCORING_COMPLETED and
    SCORING_FROZEN of the accepted triple bind the same non-empty
    completed-scoring-sheets manifest hash. On any failure the event
    triple is (None, None, None, None) and why names the defect."""
    by_type = {}
    for e in events:
        by_type.setdefault(e["type"], []).append(e)
    frozen_evs = by_type.get("EVIDENCE_FROZEN", [])
    completed_evs = by_type.get("SCORING_COMPLETED", [])
    scoring_frozen_evs = by_type.get("SCORING_FROZEN", [])
    if not frozen_evs:
        return None, None, None, None, (
            "EVIDENCE_FROZEN is absent from the sequence: raw evidence must "
            "be frozen before any scoring begins (SS13 order not present)")
    if not completed_evs:
        return None, None, None, None, (
            "SCORING_COMPLETED is absent from the sequence: the complete "
            "scoring order is not present")
    if not scoring_frozen_evs:
        return None, None, None, None, (
            "SCORING_FROZEN is absent from the sequence: the complete "
            "scoring order is not present")
    ef = frozen_evs[0]
    completed_after = [e for e in completed_evs if e["seq"] > ef["seq"]]
    if not completed_after:
        return None, None, None, None, (
            "EVIDENCE_FROZEN (seq %d) does not precede SCORING_COMPLETED "
            "(earliest at seq %d): the complete SS13 order is not present"
            % (ef["seq"], completed_evs[0]["seq"]))
    binding_failure = None
    for sc in completed_after:
        sc_val, sc_status, sc_detail = manifest_binding(sc)
        for sf in scoring_frozen_evs:
            if sf["seq"] <= sc["seq"]:
                continue
            sf_val, sf_status, sf_detail = manifest_binding(sf)
            if sc_status == "ok" and sf_status == "ok" and sc_val == sf_val:
                return ef, sc, sf, sc_val, None
            if binding_failure is None:
                if sc_status != "ok":
                    binding_failure = (
                        "SCORING_COMPLETED (seq %d) manifest binding is %s: %s"
                        % (sc["seq"], sc_status, sc_detail))
                elif sf_status != "ok":
                    binding_failure = (
                        "SCORING_FROZEN (seq %d) manifest binding is %s: %s"
                        % (sf["seq"], sf_status, sf_detail))
                else:
                    binding_failure = (
                        "mismatched completed-scoring-sheets manifest hashes: "
                        "SCORING_COMPLETED (seq %d) binds %s but SCORING_FROZEN "
                        "(seq %d) binds %s" % (sc["seq"], sc_val, sf["seq"], sf_val))
    if binding_failure is not None:
        return None, None, None, None, binding_failure
    return None, None, None, None, (
        "no SCORING_FROZEN exists after a SCORING_COMPLETED that follows "
        "EVIDENCE_FROZEN (seq %d)" % ef["seq"])

def sealed_packet_binding(events):
    """Returns (seq, packet_sha256, why). The expected sealed packet is the
    one recorded by the sequence's GROUND_TRUTH_SEALED event (the most
    recent one, if several): its payload's packet_sha256 must be present
    and a well-formed SHA-256. This is the value the selected file is
    verified against -- read from the sealing record in the sequence,
    never hardcoded here."""
    sealed = [e for e in events if e["type"] == "GROUND_TRUTH_SEALED"]
    if not sealed:
        return None, None, ("no GROUND_TRUTH_SEALED event in the sequence: "
                            "there is no recorded sealed packet to bind the "
                            "release to")
    ev = sealed[-1]
    v = (ev.get("payload") or {}).get("packet_sha256")
    if not isinstance(v, str) or not v:
        return None, None, ("GROUND_TRUTH_SEALED (seq %d) carries no "
                            "packet_sha256 in its payload" % ev["seq"])
    if not _SHA256_RE.match(v):
        return None, None, ("GROUND_TRUTH_SEALED (seq %d) packet_sha256 is "
                            "not a well-formed SHA-256" % ev["seq"])
    return ev["seq"], v, None

def selected_packet_sha256():
    """Returns (sha256, why). Hashes the selected packet file as the
    loomgt identity -- the only identity that can read the sealed store,
    and the same identity step 5 reads the material as. Nothing is
    written anywhere; the file's bytes are not returned, only its hash."""
    out = subprocess.run(["runuser", "-u", "loomgt", "--", "sha256sum", GT_FILE],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None, ("the selected packet file could not be hashed as "
                      "loomgt: " + out.stderr.strip()[-200:])
    digest = out.stdout.split()[0] if out.stdout.split() else ""
    if not _SHA256_RE.match(digest):
        return None, "sha256sum on the selected packet returned no well-formed digest"
    return digest, None

def release(examiner_id, out_path):
    # step 0: the packet selection must be explicit (correction round 3).
    # Absence of GT_RELEASE_FILE fails closed here, before the sequence is
    # consulted and before any material can be read: there is no default
    # packet, so the Annex A/C packet can never be selected by omission.
    if not GT_FILE_EXPLICIT or not GT_FILE:
        return {"released": False, "stage": "packet-selection",
                "why": "GT_RELEASE_FILE is not set: packet selection is explicit "
                       "and there is no default packet (correction round 3); "
                       "release refused, no material read"}
    events = ledger_call({"op": "list"})["events"]
    # step 1: the complete scoring order + manifest binding must verify
    ef, completed, frozen, manifest_sha, why = find_scoring_order(events)
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
    # step 2.5: the selected packet must BE the sealed Annex D material
    # (correction round 3). Its hash, computed as loomgt, must equal the
    # packet hash recorded in the sequence's GROUND_TRUTH_SEALED event.
    # A readable-but-wrong file refuses here -- before the access record
    # is appended and before any material is read for release.
    binding_seq, expected_packet_sha, bwhy = sealed_packet_binding(events)
    if expected_packet_sha is None:
        return {"released": False, "stage": "packet-binding", "why": bwhy}
    actual_packet_sha, hwhy = selected_packet_sha256()
    if actual_packet_sha is None:
        return {"released": False, "stage": "packet-binding",
                "why": "selected packet (%s) could not be verified: %s" % (GT_FILE, hwhy)}
    if actual_packet_sha != expected_packet_sha:
        return {"released": False, "stage": "packet-binding",
                "why": "selected packet (%s) SHA-256 %s does not equal the sealed "
                       "Annex D packet hash %s recorded in GROUND_TRUTH_SEALED "
                       "(seq %d); release refused, no material read"
                       % (GT_FILE, actual_packet_sha, expected_packet_sha, binding_seq),
                "selected_packet_sha256": actual_packet_sha,
                "expected_packet_sha256": expected_packet_sha,
                "sealed_event_seq": binding_seq}
    # step 3: append the access record
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    app = ledger_call({"op": "append", "type": "GROUND_TRUTH_ACCESSED",
                       "payload": {"examiner": examiner_id,
                                   "scope": "layer-4 examination of the sealed ground truth (packet file: %s)" % os.path.basename(GT_FILE),
                                   "evidence_frozen_seq": ef["seq"],
                                   "scoring_completed_seq": completed["seq"],
                                   "scoring_frozen_seq": frozen["seq"],
                                   "sheets_manifest_sha256": manifest_sha,
                                   "packet_sha256": expected_packet_sha,
                                   "packet_binding_event_seq": binding_seq,
                                   "selected_packet_sha256_verified": actual_packet_sha},
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
            "gt_file": GT_FILE, "packet_sha256": expected_packet_sha,
            "packet_binding_event_seq": binding_seq,
            "selected_packet_sha256_verified": actual_packet_sha}

if __name__ == "__main__":
    print(json.dumps(release(sys.argv[1], sys.argv[2])))
