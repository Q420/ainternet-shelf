"""Stage 9 — the frozen STEP6 artefact family, pinned by digest.

The battery programme's Stage 6 tree set and acceptance criteria
(the STEP6 artefact family, staged as Stage 0 evidence) are
applied AS FROZEN: the vendored copies under ``frozen/`` are
verified byte-for-byte against the digests the record carries
before any run, at every tree trigger during a run, and again by
the examiner surface. A mismatch refuses the run — the battery
never executes against an unverified freeze.

Digest sources (read first-hand from the record, 2026-11-20):
- pilot_trees.json cd367933… — the corpus pin for the STEP6 tree
  set (PILOT-TREES-SUBSET-01), also the digest of the copy staged
  at stage6/evidence/pilot_trees.json.
- The five battery data files — the batch6-checkpoint-2026-11-15
  package set (the AMENDED PILOT-DATA-PACKS-01, proven operative
  in attempt 3: its T03 section alex-combined-adjudication-
  r60rev#001 exists only in this version).
- The corpus snapshot sections.jsonl b107e892… — attempt 3's own
  RUN_STARTED snapshot pin.
- pilot_jcs / rules_engine / corpus_source — the pinned stack of
  the attempt-3 examination package, digest-verified against the
  corpus index.
- actions-adapter-config.json 37e7c1ea… — the frozen adapter
  envelope (temperature, top_p, thinking kwargs, per-instance
  token ceilings, retry shape).
"""
import hashlib
import os

FROZEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "frozen")

EXPECTED_DIGESTS = {
    "pilot_trees.json":
        "cd367933c261d1172d024c65d4469c8880965cf954ccfcb7ae93edce30e24673",
    "data/PILOT-DATA-PACKS-01.json":
        "b197e93eeb057f3ec00aee2479144cc97a0247d56eac954ff9aaf420a5db1ded",
    "data/EXTRACTOR-RULES-02.json":
        "7910ef9f9b8592373a291ea7ecd95e546bf2171623fd4da280bb26ef8458c3cd",
    "data/PILOT-DATA-EXPECTED-01.json":
        "79db5c87d4c9ccc52cb53c68fec5c2477cf546c9b80babbc489a472d37e57863",
    "data/PILOT-DATA-T09-01.json":
        "55a6c979163a9ce0cb30fca4eb951aff0d02685979290df8bd18dfa28b355c4a",
    "data/PILOT-DATA-FIXTURES-01.json":
        "b02e0dd005e884c62d493c1f524da983d77b2468645cf342e2a7fc9d9d08d9e8",
    "snapshot/sections.jsonl":
        "b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e",
    "snapshot/manifest.json":
        "c93eaa1906a068c53bf7fc54e872941b5556a97200ba6129aaf350a65ac4c452",
    "src/pilot_jcs.py":
        "8a131cfce23c97623aff6962e5315faf1543fbeb1533af8cd96a91feb9660d6c",
    "src/rules_engine.py":
        "7a2329154081b6e9c0417c07b1cc7184b167d02c1e820081b68a18dbabafacf3",
    "src/corpus_source.py":
        "520f36fde41dfb76d5f92fe4da92b6c2f93ae8512051962f76d4942fb5c05a5a",
    "src/actions-adapter-config.json":
        "37e7c1ea7ddb33fd0d928bfa7ea9e44dcbf7461e9c4e769091c97ee8c8bce378",
}

TREE_SET_DIGEST = EXPECTED_DIGESTS["pilot_trees.json"]
SNAPSHOT_DIGEST = EXPECTED_DIGESTS["snapshot/sections.jsonl"]


class FreezeRefused(Exception):
    """A vendored frozen artefact does not match its pinned
    digest (or is missing). The battery does not run."""

    def __init__(self, mismatches):
        self.mismatches = mismatches
        super().__init__(f"frozen artefact mismatch: {mismatches!r}")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_freeze() -> dict:
    """Verify every vendored frozen artefact against its pin.
    Returns {relative_path: digest} on success; raises
    FreezeRefused carrying every mismatch otherwise."""
    digests = {}
    mismatches = {}
    for rel, expected in EXPECTED_DIGESTS.items():
        path = os.path.join(FROZEN_DIR, rel)
        if not os.path.exists(path):
            mismatches[rel] = {"expected": expected, "found": None}
            continue
        with open(path, "rb") as f:
            actual = sha256_hex(f.read())
        digests[rel] = actual
        if actual != expected:
            mismatches[rel] = {"expected": expected, "found": actual}
    if mismatches:
        raise FreezeRefused(mismatches)
    return digests
