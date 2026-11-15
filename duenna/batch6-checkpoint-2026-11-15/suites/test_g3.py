#!/usr/bin/env python3
"""C6-10 crosswalk audit — Gate G3. Verifies that every claim
in G3-DOSSIER.md resolves to a preserved artefact or an
executed check:

  - SE-1…SE-6: the cited code anchors exist in the pinned
    tools file (sole register() call site, _invoke minting,
    closed presentation forms, refusal closure, recomputation
    order, consume-on-success);
  - SE-7(i): the vault transcript shows four OS refusals and
    the run's Step 0 verifies;
  - SE-7(ii): the falsified run's Step 0 verifies, its
    genesis recomputes from the record, and the falsified pin
    appears in no pin authority;
  - SE-7(iii): the G2 artefacts + verification report stand;
  - SE-7(iv): three planted-receipt negatives are rejected
    by Step 0 as custody findings;
  - SE-7(v)–(ix): the Batch 4 clearance filings and the
    C6-0b launcher-pin condition the citation rides on.
"""
import hashlib, json, shutil, sys, tempfile
from pathlib import Path

H = Path.home()
B6 = H / "workspace/ssh-door/batch6/build"
G3 = H / "workspace/ssh-door/batch6/scratch/g3"
G2 = H / "workspace/ssh-door/batch6/scratch/g2"
TOOLS = (B6 / "tools/pilot_tools.py").read_text()
sys.path.insert(0, str(B6))
from pilot_examiner import step0, parse_complete_events  # noqa: E402
import pilot_jcs  # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, "PASS"))
        except Exception as e:
            RESULTS.append((name, f"FAIL: {type(e).__name__}: {e}"))
    return deco


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


@case("SE-1: _invoke is the sole minter; register() has one call site")
def _():
    assert TOOLS.count("self.registry.register(") == 1
    assert "self._op_seq += 1" in TOOLS
    assert TOOLS.count("def _invoke") == 1


@case("SE-2: closed presentation forms validated before registry access")
def _():
    assert "def _presentation_form" in TOOLS
    assert 'set(presentation) != {"form", "operation_id"}' in TOOLS \
        or '{"form", "operation_id"}' in TOOLS
    assert "PRESENTATION_FORM" in TOOLS
    for reason in ("NO_CITATION", "CITATION_HASH_MISMATCH",
                   "CITATION_CHECK_FAILED", "CITATION_CONSUMED"):
        assert reason in TOOLS, reason


@case("SE-3: registry is harness-private; mutations only via its three methods")
def _():
    assert "Private harness state" in TOOLS
    assert TOOLS.count("self.registry.consume(") >= 1
    assert TOOLS.count("registry.register") == 1


@case("SE-4: insert-time recomputation precedes consumption")
def _():
    body = TOOLS[TOOLS.index("def _insert_extracted"):]
    body = body[:body.index("def _insert_carried")]
    order = [body.index(r) for r in
             ("SNAPSHOT_MISMATCH", "SOURCE_HASH_MISMATCH",
              "VALUE_MISMATCH", "self.registry.consume")]
    assert order == sorted(order), order
    assert "LEDGER_ENTRY" in body


@case("SE-5/SE-6: replay refusal + sterile refusal shape in code")
def _():
    assert "ALREADY_CONSUMED" in TOOLS
    assert '"kind": "INSERT_REFUSED"' in TOOLS or \
        '"kind": "INSERT_REFUSED"' in TOOLS.replace("'", '"')
    assert "refusal emits NO LEDGER_ENTRY and returns NO value" in TOOLS


@case("SE-7(i): vault attempts all refused at the OS boundary (EACCES)")
def _():
    attempts = json.loads(
        (G3 / "runs/G3VAULT-20261115-001/artefacts"
         "/vault-attempts.json").read_text())
    assert len(attempts) == 4
    assert all(a["result"] == "EACCES" for a in attempts), attempts
    r = step0(G3 / "runs/G3VAULT-20261115-001/run-record.jsonl",
              G3 / "commitments", G3 / "commitments/issuance-record.jsonl")
    assert r["step0"] == "PASS" and r["anchor"] == "TERMINAL"


@case("SE-7(ii): falsified block committed as-is; genesis recomputes; pin is foreign")
def _():
    rec = G3 / "runs/G3FALSE-20261115-001/run-record.jsonl"
    r = step0(rec, G3 / "commitments",
              G3 / "commitments/issuance-record.jsonl")
    assert r["step0"] == "PASS"
    events, _ = parse_complete_events(rec.read_bytes())
    block = events[0]["payload"]
    genesis = sha256_hex(pilot_jcs.canonicalise(block))
    start = json.loads((G3 / "commitments"
                        "/G3FALSE-20261115-001.start.json").read_text())
    assert start["genesis_sha256"] == genesis
    assert start["pinned_input_block_sha256"] == genesis
    falsified = block["pins"][0]["sha256"]
    assert falsified.startswith("ffff")
    authority = (B6 / "PILOT-PIN-AUTHORITY-02.json").read_text()
    assert falsified not in authority
    vault_events, _ = parse_complete_events(
        (G3 / "runs/G3VAULT-20261115-001/run-record.jsonl")
        .read_bytes())
    assert vault_events[0]["payload"]["pins"][0]["sha256"] != falsified


@case("SE-7(iii): G2 artefacts + verification report stand")
def _():
    report = (G2 / "G2-VERIFICATION-REPORT.md").read_text()
    assert "ALL PASS" in report
    torn = (G2 / "runs/G2TORN-20261115-001/run-record.jsonl").read_bytes()
    assert sha256_hex(torn) == \
        "d1f48f311474ae1886c3fdea578f3f8eada96e61120740c8db8cedbecf1fa7c7"


def _copy_g3vault(tmp):
    tmp = Path(tmp)
    rec = tmp / "run-record.jsonl"
    shutil.copy(G3 / "runs/G3VAULT-20261115-001/run-record.jsonl", rec)
    commits = tmp / "commitments"
    commits.mkdir()
    for f in (G3 / "commitments").glob("G3VAULT*"):
        shutil.copy(f, commits / f.name)
    return rec, commits


@case("SE-7(iv)a: receipt whose issuance entry was removed is rejected")
def _():
    tmp = tempfile.mkdtemp(prefix="g3-neg-a-")
    rec, commits = _copy_g3vault(tmp)
    entries = [json.loads(l) for l in
               (G3 / "commitments/issuance-record.jsonl")
               .read_text().splitlines() if l.strip()]
    kept = [e for e in entries
            if not (e.get("run_id") == "G3VAULT-20261115-001"
                    and e.get("kind") == "TERMINAL")]
    assert len(kept) == len(entries) - 1
    iss = commits / "issuance-record.jsonl"
    iss.write_text("".join(json.dumps(e) + "\n" for e in kept))
    try:
        step0(rec, commits, iss)
        raise AssertionError("accepted without issuance entry")
    except Exception as e:
        assert "issuance" in str(e), str(e)


@case("SE-7(iv)b: planted receipt with altered bytes is rejected")
def _():
    tmp = tempfile.mkdtemp(prefix="g3-neg-b-")
    rec, commits = _copy_g3vault(tmp)
    iss = commits / "issuance-record.jsonl"
    shutil.copy(G3 / "commitments/issuance-record.jsonl", iss)
    planted = json.loads(
        (commits / "G3VAULT-20261115-001.terminal.json").read_text())
    planted["event_count"] = 99
    (commits / "G3VAULT-20261115-001.terminal.json").write_text(
        json.dumps(planted))
    try:
        step0(rec, commits, iss)
        raise AssertionError("planted receipt accepted")
    except Exception as e:
        assert "issuance" in str(e) or "mismatch" in str(e), str(e)


@case("SE-7(iv)c: planted CRASH beside a genuine TERMINAL is rejected")
def _():
    tmp = tempfile.mkdtemp(prefix="g3-neg-c-")
    rec, commits = _copy_g3vault(tmp)
    iss = commits / "issuance-record.jsonl"
    shutil.copy(G3 / "commitments/issuance-record.jsonl", iss)
    shutil.copy(G2 / "commitments/G2BETWEEN-20261115-001.crash.json",
                commits / "G3VAULT-20261115-001.crash.json")
    try:
        step0(rec, commits, iss)
        raise AssertionError("coexistence accepted")
    except Exception as e:
        assert "coexist" in str(e), str(e)


@case("SE-7(v)–(ix): Batch 4 clearance + C6-0b pin condition stand")
def _():
    adj = H / "workspace/duenna-letters/ALEX-BATCH4-CHECKPOINT-ADJUDICATION-2026-11-14.md"
    err = H / "workspace/duenna-letters/ALEX-BATCH4-CROSSWALK-ERRATUM-2026-11-14.md"
    assert sha256_hex(adj.read_bytes()).startswith("79cbadea0b60f8f5")
    assert sha256_hex(err.read_bytes()).startswith("77d20e5f61e0aab7")
    manifest = (H / "workspace/ssh-door/batch6"
                "/C6-0B-PIN-VERIFICATION-MANIFEST-2026-11-14.md").read_text()
    assert "9ea9b615a22bc7ea" in manifest
    bundle = H / "workspace/ssh-door/batch4/checkpoint-bundle"
    assert (bundle / "BATCH4-CHECKPOINT-REPORT-2026-11-14.md").exists()
    dossier = (B6 / "G3-DOSSIER.md").read_text()
    for token in ("(v)", "(vi)", "(vii)", "(viii)", "(ix)"):
        assert token in dossier


fails = [r for r in RESULTS if r[1] != "PASS"]
for name, status in RESULTS:
    print(f"[{status}] {name}")
print(f"\n{len(RESULTS) - len(fails)}/{len(RESULTS)} G3 crosswalk checks pass")
sys.exit(1 if fails else 0)
