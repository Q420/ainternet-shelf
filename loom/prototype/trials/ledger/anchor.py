#!/usr/bin/env python3
"""Per-act shelf anchoring (Rev 4 SS13b). Writes the sequence head record into
the ainternet-shelf staging tree and pushes it to Q420/ainternet-shelf via the
GitHub connector, then reads it back. The anchor proves a head with that hash
existed at that position no later than the anchor commit; it is a
content-addressed archival anchor, not a trusted timestamp authority."""
import json, os, subprocess, sys

STAGING = os.path.expanduser("~/workspace/ainternet-shelf")
REL_DIR = "trials-anchors/build-demo-round"

def anchor_path(seq, etype):
    return "%s/%04d-%s.json" % (REL_DIR, seq, etype)

def anchor_head(seq, etype, head_hash, extra=None):
    rec = {"seq": seq, "type": etype, "head_hash": head_hash,
           "anchor": "Q420/ainternet-shelf", "path": anchor_path(seq, etype)}
    if extra: rec.update(extra)
    dest = os.path.join(STAGING, rec["path"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as f: json.dump(rec, f, indent=1, sort_keys=True)
    paths_file = "/tmp/loom-trials-runtime/work/anchor-paths.bin"
    with open(paths_file, "wb") as f: f.write((rec["path"] + "\0").encode())
    out = subprocess.run(["/opt/hatch/bin/github", "push-files", "--owner", "Q420",
                          "--repo", "ainternet-shelf", "--branch", "main",
                          "--message", "Trials anchor: seq %d %s head %s" % (seq, etype, head_hash[:12]),
                          "--source-dir", STAGING, "--paths-file", paths_file],
                         capture_output=True, text=True, timeout=180)
    if out.returncode != 0:
        raise RuntimeError("anchor push failed: " + out.stdout[-400:] + out.stderr[-400:])
    res = json.loads(out.stdout)
    text = res["result"]["content"][0]["text"]
    rec["anchor_commit"] = json.loads(text)["object"]["sha"]
    with open(dest, "w") as f: json.dump(rec, f, indent=1, sort_keys=True)
    return rec

def read_anchor(seq, etype):
    args = json.dumps({"owner": "Q420", "repo": "ainternet-shelf", "path": anchor_path(seq, etype)})
    out = subprocess.run(["/opt/hatch/bin/github", "call-read-tool", "--name", "get_file_contents",
                          "--arguments-json", args], capture_output=True, text=True, timeout=120)
    if out.returncode != 0: return None
    return out.stdout

if __name__ == "__main__":
    print(json.dumps(anchor_head(int(sys.argv[1]), sys.argv[2], sys.argv[3])))
