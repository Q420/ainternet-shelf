#!/usr/bin/env python3
"""C-D7(iii): establish the ACTUAL ground-truth store for the gate.

Assembles the real layer-4 packet MECHANICALLY from the pinned authority
(Rev 9 spec file): Annex A verbatim (the miniature as shown, including the
ground-truth facts it states — regions alpha v3 / beta v1 and tension T-1)
plus Annex C verbatim (the examiner-only adequacy rubric). Extraction is by
heading boundaries, byte-exact slices of the source file; nothing is
paraphrased, summarised, or retyped. The packet is sealed under the loomgt
OS identity (mode 700 store, mode 600 file). The build round's stand-in file
is NOT touched and remains preserved as build history.

Writes evidence/CD7_gt_sealing.json. Run as the operator (root)."""
import datetime, hashlib, json, os, subprocess, sys

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.expanduser("~/workspace/duenna-fix/LOOM-SPEC-V0.1-REV9-DRAFT-2026-11-21.md")
GT_DIR = "/tmp/loom-trials-runtime/gt-store"
GT_FILE = GT_DIR + "/layer4-packet.txt"

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def extract(lines, start_marker, end_marker):
    s = next(i for i, l in enumerate(lines) if l.startswith(start_marker))
    e = next(i for i, l in enumerate(lines) if i > s and l.startswith(end_marker))
    return s + 1, e, lines[s:e]  # 1-based start line, 1-based end line (exclusive)

def main():
    raw = open(SPEC, "rb").read()
    src_sha = hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    a_start, a_end, annex_a = extract(lines, "## Annex A", "## Annex B")
    c_start, c_end, annex_c = extract(lines, "## Annex C", "## Annex D")
    header = (
        "LAYER-4 PACKET — CONFORMANCE GATE GROUND TRUTH (EXAMINER ONLY)\n"
        "Assembled mechanically by ledger/seal_ground_truth.py from the pinned authority.\n"
        "Source: %s\n"
        "Source SHA-256: %s\n"
        "Annex A extracted verbatim: source lines %d-%d.\n"
        "Annex C extracted verbatim: source lines %d-%d.\n"
        "No paraphrase: every line below the header is a byte-exact slice of the source.\n"
        "\n" % (SPEC, src_sha, a_start, a_end - 1, c_start, c_end - 1)
    )
    packet = header + "".join(annex_a) + "\n" + "".join(annex_c)
    packet_bytes = packet.encode("utf-8")
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()

    # seal under loomgt: the packet is piped to a loomgt-owned write; the
    # operator never leaves a loomgt-readable copy in the trials tree.
    p = subprocess.run(["runuser", "-u", "loomgt", "--", "tee", GT_FILE],
                       input=packet, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    run(["runuser", "-u", "loomgt", "--", "chmod", "600", GT_FILE], check=True)
    listing = run(["ls", "-l", GT_DIR]).stdout
    stat = run(["runuser", "-u", "loomgt", "--", "sha256sum", GT_FILE]).stdout.strip()

    # negative tests: trial/scoring producing context (loomagent) cannot read it
    neg_agent = run(["runuser", "-u", "loomagent", "--", "cat", GT_FILE])
    neg_agent_id = run(["runuser", "-u", "loomagent", "--", "id"]).stdout.strip()

    ev = {
        "item": "C-D7(iii) actual ground-truth store",
        "sealed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_file": SPEC,
        "source_sha256": src_sha,
        "extraction": {
            "annex_a_lines": [a_start, a_end - 1],
            "annex_c_lines": [c_start, c_end - 1],
            "method": "heading-boundary byte-exact slices; header lines are mechanical metadata only",
        },
        "packet_path": GT_FILE,
        "packet_bytes": len(packet_bytes),
        "packet_sha256": packet_sha,
        "sealed_store_listing": listing,
        "sealed_store_sha256sum_as_loomgt": stat,
        "packet_hash_verified_under_sealing_identity": stat.startswith(packet_sha),
        "negative_tests": {
            "loomagent_identity": neg_agent_id,
            "loomagent_cat_returncode": neg_agent.returncode,
            "loomagent_cat_stderr": neg_agent.stderr.strip(),
        },
        "standin_preserved": os.path.exists(GT_DIR + "/annex-d-sealed-standin.txt"),
    }
    json.dump(ev, open(T + "/evidence/CD7_gt_sealing.json", "w"), indent=1)
    print(json.dumps(ev, indent=1))

if __name__ == "__main__":
    main()
