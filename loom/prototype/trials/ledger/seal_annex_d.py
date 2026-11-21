#!/usr/bin/env python3
"""Correction round 2, D7-A: seal the ACTUAL Annex D ground truth.

Rev 9 identifies Annex D as the sealed ground truth: the six fixture-region
identities, the semantic plant, and the structural plant. The correction
round 1 packet (ledger/seal_ground_truth.py) extracted Annex A + Annex C --
the candidate-facing prompt and the adequacy rubric -- which are NOT the
sealed ground truth. That packet (gt-store/layer4-packet.txt) is preserved
unchanged as submitted evidence and is not touched by this script.

This script extracts the Annex D section MECHANICALLY from the pinned
Rev 9 authority (heading-boundary byte slice: from the '## Annex D' heading
line up to, not including, the '## Annex E' heading line; byte-exact, no
paraphrase, no reconstruction) and seals it OUTSIDE the trials tree under
the loomgt OS identity at gt-store/annex-d-packet.txt (mode 700 store,
mode 600 file). The packet is a mechanical-metadata header followed by the
byte-exact Annex D slice.

Writes evidence/CD7A_annex_d_sealing.json, including denial evidence:
read attempts from the producing identity (loomagent) and from the ledger
identity (loomledger) both fail at the store boundary. Run as the operator
(root)."""
import datetime, hashlib, json, os, subprocess

T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.expanduser("~/workspace/duenna-fix/LOOM-SPEC-V0.1-REV9-DRAFT-2026-11-21.md")
SPEC_BLOB = "6a7e3d54b4b653ed6b8ca76392c59d283d8b2b1a"  # pinned Rev 9 blob (Rev 4 authority)
GT_DIR = "/tmp/loom-trials-runtime/gt-store"
GT_FILE = GT_DIR + "/annex-d-packet.txt"
AC_PACKET = GT_DIR + "/layer4-packet.txt"  # round-1 Annex A/C packet: preserved, untouched

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def main():
    raw = open(SPEC, "rb").read()
    src_sha = hashlib.sha256(raw).hexdigest()
    blob = run(["git", "-C", os.path.dirname(SPEC), "hash-object", SPEC]).stdout.strip()
    lines = raw.splitlines(keepends=True)
    offsets = [0]
    for l in lines:
        offsets.append(offsets[-1] + len(l))
    s = next(i for i, l in enumerate(lines) if l.startswith(b"## Annex D"))
    e = next(i for i, l in enumerate(lines) if i > s and l.startswith(b"## Annex E"))
    # 1-based inclusive line range [s+1, e]; byte range [offsets[s], offsets[e])
    annex_d = raw[offsets[s]:offsets[e]]
    annex_d_sha = hashlib.sha256(annex_d).hexdigest()
    header = (
        "ANNEX D PACKET -- CONFORMANCE GATE SEALED GROUND TRUTH (EXAMINERS ONLY)\n"
        "Assembled mechanically by ledger/seal_annex_d.py (correction round 2, D7-A)\n"
        "from the pinned Rev 9 authority. Every byte below this header is a\n"
        "byte-exact slice of the source file: the Annex D section itself.\n"
        "Source: %s\n"
        "Source SHA-256: %s\n"
        "Source git blob: %s\n"
        "Annex D extracted verbatim: source lines %d-%d (1-based inclusive),\n"
        "source bytes %d-%d (0-based, end exclusive), %d bytes, SHA-256 %s.\n"
        "\n" % (SPEC, src_sha, blob, s + 1, e, offsets[s], offsets[e],
                len(annex_d), annex_d_sha)
    )
    packet_bytes = header.encode("utf-8") + annex_d
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()

    ac_before = run(["runuser", "-u", "loomgt", "--", "sha256sum", AC_PACKET]).stdout.strip()

    # seal under loomgt: the packet is piped as raw bytes to a loomgt-owned
    # write; no loomgt-readable copy is left in the trials tree.
    p = subprocess.run(["runuser", "-u", "loomgt", "--", "tee", GT_FILE],
                       input=packet_bytes, capture_output=True)
    assert p.returncode == 0, p.stderr.decode("utf-8", errors="replace")
    run(["runuser", "-u", "loomgt", "--", "chmod", "600", GT_FILE], check=True)
    listing = run(["ls", "-l", GT_DIR]).stdout
    stat = run(["runuser", "-u", "loomgt", "--", "sha256sum", GT_FILE]).stdout.strip()
    ac_after = run(["runuser", "-u", "loomgt", "--", "sha256sum", AC_PACKET]).stdout.strip()

    # denial evidence: producing identity (loomagent) and ledger identity
    # (loomledger) -- neither is the sealing identity; both fail at the
    # mode-700 loomgt store boundary.
    denials = {}
    for ident in ("loomagent", "loomledger"):
        r = run(["runuser", "-u", ident, "--", "cat", GT_FILE])
        denials[ident] = {
            "identity": run(["runuser", "-u", ident, "--", "id"]).stdout.strip(),
            "cat_returncode": r.returncode,
            "cat_stderr": r.stderr.strip(),
        }

    ev = {
        "item": "Correction round 2, D7-A: Annex D sealed ground truth",
        "sealed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_file": SPEC,
        "source_sha256": src_sha,
        "source_git_blob": blob,
        "source_blob_matches_pin": blob == SPEC_BLOB,
        "extraction": {
            "method": "heading-boundary byte-exact slice of the Annex D section "
                      "(from the '## Annex D' heading line to just before the "
                      "'## Annex E' heading line); header lines are mechanical "
                      "metadata only; no paraphrase, no reconstruction",
            "source_lines_1based_inclusive": [s + 1, e],
            "source_byte_range_0based_end_exclusive": [offsets[s], offsets[e]],
            "annex_d_bytes": len(annex_d),
            "annex_d_sha256": annex_d_sha,
            "contents_as_identified_by_rev9": [
                "the six fixture-region identities",
                "the semantic plant",
                "the structural plant",
            ],
        },
        "packet_path": GT_FILE,
        "packet_bytes": len(packet_bytes),
        "packet_sha256": packet_sha,
        "sealed_store_listing": listing,
        "sealed_store_sha256sum_as_loomgt": stat,
        "packet_hash_verified_under_sealing_identity": stat.startswith(packet_sha),
        "denial_tests": denials,
        "round1_annex_a_c_packet_preserved": {
            "path": AC_PACKET,
            "sha256sum_as_loomgt_before": ac_before,
            "sha256sum_as_loomgt_after": ac_after,
            "unchanged": ac_before == ac_after and ac_before.startswith(
                "8bb7c08ade85f2c46233cdcf3998e7ad043c93764ef1d48637ac0e493aa26c15"),
            "note": "The round-1 packet contains Annex A + Annex C extracts. It is "
                    "preserved unchanged as submitted evidence. It is NOT the "
                    "Annex D packet and is not described as such.",
        },
        "standin_preserved": os.path.exists(GT_DIR + "/annex-d-sealed-standin.txt"),
    }
    json.dump(ev, open(T + "/evidence/CD7A_annex_d_sealing.json", "w"), indent=1)
    print(json.dumps(ev, indent=1))

if __name__ == "__main__":
    main()
