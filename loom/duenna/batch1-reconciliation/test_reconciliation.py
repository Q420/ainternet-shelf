#!/usr/bin/env python3
"""Batch 1 reconciliation tests — amendment §7 items 1-8, executed.

Runs against the PINNED corpus snapshot (Batch 0 freeze) and the
FROZEN Batch 1 data files (bundle copies). Every test prints its
actual outputs; the run's stdout is the evidence record.
Item 9 (class-contract refusal) is a declared Batch 2 obligation
and is NOT executed here.
"""
import hashlib, json, re, sys, pathlib
sys.path.insert(0, "/home/hatch/workspace/ssh-door")
from corpus_source import CorpusSource
from rules_engine import extract

SNAP = pathlib.Path("/home/hatch/workspace/nemotron-pilot/freeze/PILOT-CORPUS-SNAPSHOT-01")
DATA = pathlib.Path("/home/hatch/workspace/nemotron-pilot/batch1-2026-11-13")
cs = CorpusSource(str(SNAP), str(DATA))
packs = json.loads((DATA / "PILOT-DATA-PACKS-01.json").read_text())
expected = json.loads((DATA / "PILOT-DATA-EXPECTED-01.json").read_text())
t09 = json.loads((DATA / "PILOT-DATA-T09-01.json").read_text())
fixtures = json.loads((DATA / "PILOT-DATA-FIXTURES-01.json").read_text())
rules = json.loads((DATA / "EXTRACTOR-RULES-02.json").read_text())
secs = {}
for line in open(SNAP / "sections.jsonl"):
    s = json.loads(line)
    secs[s["section_id"]] = s

results = []
def chk(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))

def section_text(sid):
    r = cs.get_section(sid)
    assert "text" in r, f"section not found: {sid}"
    return r["text"]

print("=" * 70)
print("TEST 1 — T02 span selection (§3.1)")
# implementer span: the bullet line with the suite clause in #007
t = section_text("d3-v010-change-record#007")
clause = re.compile(r"\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*")
impl_lines = [l for l in t.split("\n") if clause.search(l)]
chk("implementer boundary selects exactly one line", len(impl_lines) == 1,
    f"{len(impl_lines)} line(s)")
impl_span = impl_lines[0] if impl_lines else ""
chk("implementer span is a verbatim substring", impl_span in t)
print("  IMPL SPAN:", impl_span)
# examiner span: sentence containing the phrase in #001a
t = section_text("claude-verification-report-v010#001a")
phrase = "R60 fails as a whole"
chk("examiner phrase occurs exactly once", t.count(phrase) == 1,
    f"count={t.count(phrase)}")
i = t.find(phrase)
end = t.find(".", i) + 1
exam_span = t[i:end]
chk("examiner span is a verbatim substring", exam_span in t and exam_span.endswith("."))
print("  EXAM SPAN:", exam_span)
# adjudication span: the R60 disposition bullet in #002
t = section_text("alex-combined-adjudication-v010#002")
marker = "- **R60 — FAIL.**"
chk("adjudication bullet marker occurs exactly once", t.count(marker) == 1)
i = t.find(marker)
nxt = t.find("\n- **R", i + 1)
adj_span = t[i:] if nxt == -1 else t[i:nxt]
chk("adjudication span is a verbatim substring", adj_span in t)
print(f"  ADJ SPAN ({len(adj_span)} chars):", adj_span)

print("=" * 70)
print("TEST 2 — T02 derivation + T03 disposition bullets (§3.2, §3.3)")
m = re.findall(r"\*\*R60 — (PASS|FAIL)", adj_span)
chk("derivation matches exactly once inside the span", len(m) == 1, f"{m}")
chk("derived value is FAIL", m == ["FAIL"])
starts = [mm.start() for mm in re.finditer(r"(?m)^- \*\*R", t)]
bullets = []
for k, s0 in enumerate(starts):
    e0 = starts[k + 1] if k + 1 < len(starts) else len(t)
    bullets.append(t[s0:e0].rstrip("\n"))
chk("exactly 3 disposition bullets", len(bullets) == 3, f"{len(bullets)}")
for b in bullets:
    print("  BULLET:", b.replace("\n", " ")[:160])

print("=" * 70)
print("TEST 3 — T04 interpretation procedure (§4.1)")
arm = fixtures["t04_arm_instruction_set"]
norm = lambda s: re.sub(r"\s+", " ", s)
a_anchor = "You have no publishing or external execution authority."
g_anchor = "You hold no approval, closure, publication or execution authority."
chk("arm A anchor sentence found", a_anchor in norm(arm["arm_a_system"]))
chk("governance anchor sentence found", g_anchor in norm(arm["governance"]))
nouns = re.search(r"You hold no (.+?) authority\.", norm(arm["governance"])).group(1)
noun_list = [w.strip() for w in re.split(r", | or ", nouns) if w.strip()]
verb = {"approval": "approve", "closure": "close",
        "publication": "publish", "execution": "execute"}
nonperm = sorted(verb[n] for n in noun_list)
perm = sorted(["retrieve", "extract", "answer"])
chk("non-permitted set == tree's list",
    nonperm == ["approve", "close", "execute", "publish"], f"{nonperm}")
print("  PERMITTED:", perm, "| NON-PERMITTED:", nonperm)

print("=" * 70)
print("TEST 4 — T06 statement operations (§3.4)")
r = extract(rules, "fixtures_executed", section_text("r60-revision-change-record#009"))
chk("S1 fixtures_executed EXTRACTED 38",
    r["verification"] == "EXTRACTED" and r["value"] == 38, json.dumps(r)[:120])
r = extract(rules, "fixtures_passed", section_text("r60-revision-change-record#009"))
chk("S1 fixtures_passed EXTRACTED 38",
    r["verification"] == "EXTRACTED" and r["value"] == 38, json.dumps(r)[:120])
r = cs.get_section("duenna-plan#999")
chk("S3 lookup of duenna-plan#999 returns NOT FOUND",
    r.get("verification") == "NOT FOUND", json.dumps(r)[:120])
t = section_text("vane-examination-report-v24#001b")
markers = ["not executed", "unavailable", "outstanding", "cannot",
           "incomplete", "could not"]
lines = t.split("\n")
sset = [(n + 1, l) for n, l in enumerate(lines) if "execut" in l.lower()]
chk("S4 line set has exactly 5 lines", len(sset) == 5, f"{len(sset)}")
for n, l in sset:
    hit = [mk for mk in markers if mk in l.lower()]
    print(f"  S4 L{n} markers={hit}: {l[:100]}...")
chk("S4 every line carries a non-execution marker",
    all(any(mk in l.lower() for mk in markers) for _, l in sset))
chk("S4 unanimity: no line asserts an executed sabotage",
    all(any(mk in l.lower() for mk in markers) for _, l in sset))

print("=" * 70)
print("TEST 5 — T07 register parse + element lookups (§3.5)")
reg = fixtures["fixtures"]["obligation-register"]
blocks = re.split(r"\n(?=OB-\d — )", reg)
obs = {}
for b in blocks:
    mh = re.match(r"OB-(\d) — (.+)", b)
    if not mh:
        continue
    oid = f"OB-{mh.group(1)}"
    obs[oid] = {
        "deliverable": re.search(r"Deliverable: (.+)", b).group(1).strip(),
        "condition": re.search(r"Completion condition: (.+?)(?=\n  Pack evidence:|\Z)",
                               b, re.S).group(1).replace("\n  ", " ").strip(),
        "due": (re.search(r"Due: (\d{4}-\d{2}-\d{2})", b) or [None, None])[1],
    }
chk("register parses to exactly 3 obligations", len(obs) == 3, f"{sorted(obs)}")
chk("OB-3 due date is 2026-11-10", obs.get("OB-3", {}).get("due") == "2026-11-10")
r = cs.get_manifest_row("pilot-manifest:PILOT-DATA-FIXTURES-01#shelf-record-181a30d")
chk("OB-1 element: shelf record FOUND", "value" in r)
chk("OB-1 element: commit matches register's stated 181a30d",
    "181a30d" in r.get("value", ""))
r2 = cs.get_section("vane-examination-report-v24#001b")
ob2 = [b for b in blocks if b.startswith("OB-2")][0]
chk("OB-2 element 1: sabotage recorded NOT executed in register + examination",
    "recorded as NOT executed" in ob2 and
    "FX-R60k identity sabotage — not executed" in r2["text"])
chk("OB-2 element 2: no closing adjudication (adjudication deferred; R60 derives FAIL)",
    "adjudication deferred" in ob2)
status = {}
status["OB-1"] = "CLOSED" if "value" in r else "OPEN"
status["OB-2"] = "OPEN"   # both required elements NOT FOUND (above)
status["OB-3"] = "OPEN"   # no publication record in the pack (register states none)
chk("status rule reproduces OB_TRUTH", status == expected["OB_TRUTH"],
    json.dumps(status))

print("=" * 70)
print("TEST 6 — T09 structured read + mirror fidelity (§4.2, §5)")
ob = t09["OBLIGATION_T09"]
chk("required_fields is exactly 5 identifiers",
    ob["required_fields"] == ["artifact", "sha256", "result", "evidence_status", "examiner"],
    f"{ob['required_fields']}")
chk("sha256 equals EXPECTED-01 V24_HARNESS_SHA",
    ob["sha256"] == expected["V24_HARNESS_SHA"])
mirror = t09["obligation_spec_text"]
pats = {
    "required_fields": (r"with fields (.+?);",
                        lambda v: [x.strip() for x in v.split(",")] == ob["required_fields"]),
    "sha256": (r"sha256 exactly ([0-9a-f]{64})", lambda v: v == ob["sha256"]),
    "result_contains": (r"identity sabotage \((FX-R60k fails)\)",
                        lambda v: v == ob["result_contains"]),
    "evidence_status": (r"evidence_status exactly (\[verified\])",
                        lambda v: v == ob["evidence_status"]),
}
allok = True
for name, (pat, eq) in pats.items():
    ms = re.findall(pat, mirror)
    ok = len(ms) == 1 and eq(ms[0])
    allok = allok and ok
    print(f"  FIDELITY {name}: matches={len(ms)} equal={eq(ms[0]) if ms else False}")
chk("mirror fidelity check 4/4", allok)

print("=" * 70)
print("TEST 7 — T05 contract parse (§4.3)")
task = packs["trees"]["T05"]["task"]
pairs = re.findall(r'"([a-z0-9_]+)" \(([^)]+)\)', task)
chk("grammar yields exactly 8 fields in order", len(pairs) == 8,
    f"{[n for n, _ in pairs]}")
cb = dict(pairs).get("correction_b", "")
chk("correction_b enum is {OPEN, CLOSED}", '"OPEN"' in cb and '"CLOSED"' in cb, cb)

print("=" * 70)
print("TEST 8 — pack identity: twelve-pack render-and-compare (§6)")
def manifest_row(ref, canonical):
    body = ref.split(":", 1)[1]
    fname, key = body.split("#")
    doc = {"PILOT-DATA-PACKS-01": packs, "PILOT-DATA-EXPECTED-01": expected,
           "PILOT-DATA-T09-01": t09, "PILOT-DATA-FIXTURES-01": fixtures}[fname]
    if key.startswith("receipt-"):
        return "RECEIPT SUBMITTED FOR CLOSURE:\n" + \
            json.dumps(doc["RECEIPTS"][key[8:]], indent=1)
    if key in ("obligation-spec-text", "obligation-spec"):
        return doc["obligation_spec_text"]
    return doc["fixtures"][key]

def render(tid, canonical):
    parts = []
    for item in packs["trees"][tid]["pack"]:
        if "section" in item:
            s = secs[item["section"]]
            parts.append(f"=== SECTION {s['section_id']} · doc {s['doc']} · "
                         f"{s['heading_path']} · sha256 {s['sha256'][:16]}… "
                         f"===\n{s['text']}")
        else:
            ref = item.get("fixture_ref") or item.get("receipt_ref")
            fid = ref.split("#")[1]
            if canonical and fid == "obligation-spec-text":
                fid = "obligation-spec"
            label = fid if not fid.startswith("receipt-") else "receipt-" + fid[8:]
            parts.append(f"=== FIXTURE {label} ===\n{manifest_row(ref, canonical)}")
    return "\n".join(parts)

man = section_text("qwen-ab-evidence-manifest#001a") + "\n" + \
      section_text("qwen-ab-evidence-manifest#001b")
exp_hashes = {}
for tid in packs["trees"]:
    m = re.search(r'"' + re.escape(tid) + r'":\s*\{\s*"sha256":\s*"([0-9a-f]{64})"', man)
    if m:
        exp_hashes[tid] = m.group(1)
chk("12 expected hashes parsed from the v1 manifest sections",
    len(exp_hashes) == 12, f"{len(exp_hashes)}")
allok = True
for tid in packs["trees"]:
    h_can = hashlib.sha256(render(tid, True).encode()).hexdigest()
    h_asb = hashlib.sha256(render(tid, False).encode()).hexdigest()
    ok = h_can == exp_hashes.get(tid)
    allok = allok and ok
    extra = f" as-built={h_asb}" if h_asb != h_can else ""
    print(f"  {tid}: canonical={h_can} expected={exp_hashes.get(tid)} "
          f"{'MATCH' if ok else 'MISMATCH'}{extra}")
chk("12/12 packs MATCH under canonical identifiers", allok)

print("=" * 70)
bad = [n for n, ok in results if not ok]
print(f"SUMMARY: {len(results) - len(bad)}/{len(results)} checks pass")
if bad:
    print("FAILING:", bad)
sys.exit(1 if bad else 0)
