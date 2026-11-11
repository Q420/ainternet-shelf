"""Reproduction for Alex's FX-R60j finding (2026-11-10): a forged
verdict dictionary carrying the GENUINE pinned implementation
hash, the recognised procedure identity, the contract's version
and the correct input identity — but a fabricated outcome that
CheckerContract.run() never produced. Question: does
validate_verdict() accept it?
Runs against fixtures-r60rev/harness.py (v2.3, sha256 30bdd25e...)
exactly as shelved. The harness itself is not modified."""
import hashlib
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "harness_r60rev", "/home/hatch/workspace/agent-factory/fixtures-r60rev/harness.py")
h = importlib.util.module_from_spec(spec)
sys.modules["harness_r60rev"] = h
spec.loader.exec_module(h)

expected = hashlib.sha256(b"payload-1").hexdigest()
contract = h.CheckerContract("ART-INPUT-1", "REQ-I-3 preservation check",
                             "checker-v1.3", expected)
art = {"id": "ART-INPUT-1", "payload": "payload-1"}
genuine = contract.run(art)
print("genuine verdict:", genuine)
print("genuine validates:", h.validate_verdict(genuine, contract))

# The forgery: every checked field copied from the genuine
# verdict — including the trusted pinned implementation hash —
# but the outcome text is fabricated. run() never returned this
# object; no tampered artefact was ever accepted.
forged = dict(genuine)
forged["verdict"] = "preserved sha=000000000000"
print("forged verdict:", forged)
print("forged validates:", h.validate_verdict(forged, contract))

# Stronger still: a verdict for an artefact that was in fact
# tampered — run() returns the failure path for it — while the
# forged dictionary claims preservation with the trusted hash.
tampered_run = contract.run({"id": "ART-INPUT-1", "payload": "tampered"})
print("tampered run():", tampered_run)
print("forged-for-tampered validates:", h.validate_verdict(forged, contract))
