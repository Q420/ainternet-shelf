#!/usr/bin/env python3
"""T03 remediation audit — verifies PILOT-CALIBRATION-02 and
the re-freeze against the preserved pre-amendment artefacts:

  - cert 02 issued, all 13 ANSWERABLE, T03's four required
    values extracted exactly as Alex confirmed them;
  - T03 is the ONLY verdict that changed vs cert 01;
  - cert 01 preserved byte-for-byte (sha256 6f3e5979…);
  - the file amendments are exactly the authorised ones:
    rules +3 entries (the confirmed patterns), packs +1 T03
    pack entry, nothing else differs from the preserved
    originals, whose hashes match the old pin authority;
  - the corpus snapshot is untouched (its sections hash is
    still cert 01's pin) and the Correction B source section
    hash is the verified 393cba4c….
"""
import hashlib, json, sys
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
REM = H / "workspace/ssh-door/t03-remediation"
RULES_P = H / "workspace/ssh-door/EXTRACTOR-RULES-02.json"
PACKS_P = (H / "workspace/nemotron-pilot/batch1-2026-11-13"
           "/PILOT-DATA-PACKS-01.json")
SNAP = H / "workspace/nemotron-pilot/freeze/PILOT-CORPUS-SNAPSHOT-01"
sys.path.insert(0, str(B6 / "tools"))
from corpus_source import CorpusSource  # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


C1 = json.loads((B6 / "PILOT-CALIBRATION-01.json").read_bytes())
C2 = json.loads((B6 / "PILOT-CALIBRATION-02.json").read_bytes())


@case("cert 02 issued: all 13 ANSWERABLE, checks pass, basis recorded")
def _():
    assert C2["artefact"] == "PILOT-CALIBRATION-02"
    assert C2["all_answerable"] is True
    assert C2["synthetic_all_pass"] is True
    assert "amendment_basis" in C2 and "supersedes" in C2


@case("T03 ANSWERABLE: the four values extracted exactly")
def _():
    t = C2["instances"]["T03"]
    assert t["verdict"] == "ANSWERABLE" and t["failures"] == []
    d = t["expected_values"]["dispositions"]
    assert d["r47_disposition"] == {"expected": "PASS, narrow",
                                    "extracted": "PASS, narrow",
                                    "agree": True}
    assert d["r60_disposition"]["extracted"] == "FAIL"
    assert d["r65_disposition"]["extracted"] == "PASS, qualified"
    assert t["expected_values"]["correction_b"] == {
        "expected": "OPEN", "extracted": "OPEN", "agree": True}


@case("T03 is the only verdict change vs cert 01")
def _():
    for k, inst in C1["instances"].items():
        if k == "T03":
            assert inst["verdict"] == "UNANSWERABLE"
            assert C2["instances"][k]["verdict"] == "ANSWERABLE"
        else:
            assert C2["instances"][k]["verdict"] == inst["verdict"], k


@case("cert 01 preserved byte-for-byte")
def _():
    assert sha(B6 / "PILOT-CALIBRATION-01.json") == \
        "6f3e59793ad751b8d0d47d81c30f337cd1ed1d124493cff31f39229a51d15f0c"


@case("preserved originals match the old pin authority")
def _():
    assert sha(REM / "EXTRACTOR-RULES-02.pre-amendment.json") == \
        "61095f219e1d481ed74c65f3a95806a2cba2e7dc847bcb692373ade3974c5ee5"
    assert sha(REM / "PILOT-DATA-PACKS-01.pre-amendment.json") == \
        "c7eaec18db203651af894e7fbdb53c6df9b36a3da185c4b7ab703d73085b886c"


@case("rules amendment is exactly the three confirmed rules")
def _():
    old = json.loads((REM / "EXTRACTOR-RULES-02.pre-amendment.json")
                     .read_text())
    new = json.loads(RULES_P.read_text())
    assert new["version"] == old["version"]
    assert new["rules"][:len(old["rules"])] == old["rules"]
    added = new["rules"][len(old["rules"]):]
    assert [r["rule_id"] for r in added] == \
        ["EXT02-R47-1", "EXT02-R60-1", "EXT02-R65-1"]
    assert added[0]["pattern"] == "\\*\\*R47 — (PASS, narrow)\\.\\*\\*"
    assert added[1]["pattern"] == "\\*\\*R60 — (FAIL)\\.\\*\\*"
    assert added[2]["pattern"] == \
        "\\*\\*R65 — (PASS, qualified)\\.\\*\\*"
    assert all(r["value_type"] == "string" and r["group"] == 1
               for r in added)
    assert C2["inputs"]["rules"]["sha256"] == sha(RULES_P)


@case("packs amendment is exactly the one T03 pack entry")
def _():
    old = json.loads((REM / "PILOT-DATA-PACKS-01.pre-amendment.json")
                     .read_text())
    new = json.loads(PACKS_P.read_text())
    assert new["trees"]["T03"]["pack"][:-1] == \
        old["trees"]["T03"]["pack"]
    assert new["trees"]["T03"]["pack"][-1] == \
        {"section": "alex-combined-adjudication-r60rev#001"}
    for tree, entry in old["trees"].items():
        if tree != "T03":
            assert new["trees"][tree] == entry, tree
    t03_old = {k: v for k, v in old["trees"]["T03"].items()
               if k != "pack"}
    t03_new = {k: v for k, v in new["trees"]["T03"].items()
               if k != "pack"}
    assert t03_old == t03_new


@case("snapshot untouched; Correction B source hash verified")
def _():
    assert sha(SNAP / "sections.jsonl") == \
        "b107e8926abc5fed666c460591850adf41efd5b7d46067f2ee2f546e49c5823e"
    corpus = CorpusSource(SNAP, PACKS_P.parent)
    sec = corpus.get_section("alex-combined-adjudication-r60rev#001")
    assert sec["sha256"] == \
        "393cba4c8adae5b153580a1a42dede4543701712f8e99592b2694e0aa2aa366b"


fails = [r for r in RESULTS if r[1] != "PASS"]
for name, status in RESULTS:
    print(f"[{status}] {name}")
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} T03 remediation audit checks pass")
sys.exit(1 if fails else 0)
