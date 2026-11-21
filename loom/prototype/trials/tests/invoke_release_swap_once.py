#!/usr/bin/env python3
"""Correction round 4 helper: ONE release invocation in a fresh process,
with a mechanical interposition that swaps the selected file's contents
at the exact point of the former check/use gap.

gt_release.release() verifies the selected packet's digest (step 2.5),
appends GROUND_TRUTH_ACCESSED (step 3), anchors it via
anchor.anchor_head (step 4), and only then reads the selected packet
(step 5). This invoker wraps anchor.anchor_head: the REAL anchor
executes first (the access head is written to the shelf staging tree and
pushed, exactly as in an unmodified invocation); immediately after it
returns for the GROUND_TRUTH_ACCESSED event -- after anchoring, before
the step-5 read -- the wrapper replaces the selected file's bytes with
the tampered bytes (as the loomgt identity, the store's owner, via
runuser cp). The release then performs its step-5 read on the swapped
bytes. Nothing in gt_release or anchor is altered on disk; the wrap
exists only inside this test process.

Environment (set by the calling runner):
  GT_RELEASE_FILE  the selected packet (a swappable copy of the Annex D
                   packet whose digest matches at pre-verification)
  GT_SWAP_SOURCE   path of the tampered-content file (in the gt-store)
  GT_SWAP_RECORD   path to write the swap record JSON (optional)
"""
import json, os, subprocess, sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T + "/ledger")
import anchor as anchor_mod
import gt_release

SWAP_SOURCE = os.environ.get("GT_SWAP_SOURCE")
SELECTED = os.environ.get("GT_RELEASE_FILE")
swap_record = {"interposed": False}

def _sha256_as_loomgt(path):
    r = subprocess.run(["runuser", "-u", "loomgt", "--", "sha256sum", path],
                       capture_output=True, text=True)
    return r.stdout.split()[0] if r.returncode == 0 and r.stdout.split() else None

_orig_anchor_head = anchor_mod.anchor_head

def swapping_anchor_head(seq, etype, head_hash, extra=None):
    rec = _orig_anchor_head(seq, etype, head_hash, extra)
    if etype == "GROUND_TRUTH_ACCESSED" and SWAP_SOURCE and SELECTED:
        before = _sha256_as_loomgt(SELECTED)
        cp = subprocess.run(["runuser", "-u", "loomgt", "--", "cp",
                             SWAP_SOURCE, SELECTED],
                            capture_output=True, text=True)
        after = _sha256_as_loomgt(SELECTED)
        swap_record.update({
            "interposed": True,
            "method": "in-process wrap of anchor.anchor_head: the real anchor "
                      "for GROUND_TRUTH_ACCESSED executed and returned; the "
                      "selected file's bytes were then replaced (runuser -u "
                      "loomgt -- cp <tampered> <selected>) before "
                      "gt_release.release() performed its step-5 read",
            "access_event_seq": seq,
            "anchor_commit_returned_by_real_anchor": rec.get("anchor_commit"),
            "selected_file": SELECTED,
            "selected_sha256_before_swap": before,
            "swap_cp_returncode": cp.returncode,
            "swap_cp_stderr_tail": cp.stderr[-200:],
            "selected_sha256_after_swap": after,
            "swap_source": SWAP_SOURCE,
            "swap_source_sha256_as_loomgt": _sha256_as_loomgt(SWAP_SOURCE)})
    return rec

anchor_mod.anchor_head = swapping_anchor_head

if __name__ == "__main__":
    result = gt_release.release(sys.argv[1], sys.argv[2])
    rec_path = os.environ.get("GT_SWAP_RECORD")
    if rec_path:
        with open(rec_path, "w") as f:
            json.dump(swap_record, f, indent=1)
    print(json.dumps({"gt_file_seen_by_module": gt_release.GT_FILE,
                      "gt_file_explicit": gt_release.GT_FILE_EXPLICIT,
                      "swap": swap_record,
                      "result": result}, indent=1))
