#!/usr/bin/env python3
"""Batch 1 reconciliation tests — ROUND 4 revision (T07 only).

Round 4 supersedes Round 3's Test 5 only, against Alex's
Round 3 inspection (pb-mwfgj6up-5-82df): OB-2 element 1 is
now a genuine lookup over a declared source set with every
candidate dispositioned (including FR-VALID, dispositioned
on the independence clause), the register's own NOT-executed
evidence is verified, and OB-3's absence operation runs over
the CONTENTS of the enumerated sources under a declared
matching rule, returning UNKNOWN rather than NOT FOUND if
absence cannot be established exhaustively. All other tests
are Round 3's, unchanged, re-executed in this run. Round 3's
suite and output are preserved untouched as history.

The Round 3 header follows.

--- ROUND 3 HEADER (preserved) ---
Batch 1 reconciliation tests — ROUND 3 revision.

Revises test_reconciliation.py (the Round 2 suite, preserved
untouched as historical evidence at sha256 830b3fc8...) against
Alex's Round 2 inspection (pb-mwf4x0du-4-dw4u), which accepted
the taxonomy repair, the S4 reconciliation and the F-B1-2
support, but required six test-coverage corrections:

  1. S4: assert the COMPLETE expected set (lines + content),
     and make the unanimity check independently meaningful
     (a disposition classifier with positive controls, not a
     repeat of the marker predicate).
  2. T07: execute the OB-2 element lookups (execution receipt;
     closing adjudication) as corpus operations returning
     NOT FOUND, and establish OB-3 by a declared deterministic
     absence operation. No status is hand-assigned.
  3. T06 S2: exercise the Grok-approval source-location
     operation (STEP-A scan, STEP-B NOT FOUND / UNTRACEABLE).
  4. T04: assert the fixture-derived boundary sets EQUAL the
     tree's declared vocabulary, read from the V2 trees
     document (its sha256 is printed below as provenance).
  5. T09: validate the complete schema contract (every
     declared field type, the SHA's hex64 shape, per-receipt
     schema validation and worksheet acceptance, with
     negative controls), not only required-fields + equality.
  6. T02: assert the worksheet rows carry the declared
     source references and implementer/examiner/adjudicator
     classes (Draft 02 section 3.1), plus the declared
     602-character adjudication span.

Runs against the PINNED corpus snapshot (Batch 0 freeze) and
the FROZEN Batch 1 data files. Item 9 of Draft 02 section 7
(the reference_insert class B/C refusal case) remains a
declared Batch 2 obligation and is NOT executed here.
"""
import hashlib, json, re, sys, pathlib
sys.path.insert(0, "/home/hatch/workspace/nemotron-pilot/batch1-2026-11-13")
from corpus_source import CorpusSource
from rules_engine import extract

SNAP = pathlib.Path("/home/hatch/workspace/nemotron-pilot/freeze/PILOT-CORPUS-SNAPSHOT-01")
DATA = pathlib.Path("/home/hatch/workspace/nemotron-pilot/batch1-2026-11-13")
TREES_DOC = pathlib.Path("/home/hatch/workspace/ainternet-shelf/duenna/qwen-ab/v2/PROCESS-TREES.md")
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

print("TREES_DOC sha256:", hashlib.sha256(TREES_DOC.read_bytes()).hexdigest())
print("TREES_DOC:", TREES_DOC)

results = []
def chk(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))

def section_text(sid):
    r = cs.get_section(sid)
    assert "text" in r, f"section not found: {sid}"
    return r["text"]

print("=" * 70)
print("TEST 1 — T02 span selection + worksheet rows (§3.1; Alex point 6)")
t = section_text("d3-v010-change-record#007")
clause = re.compile(r"\*\*\d+ fixtures executed, \d+ PASS, 0 FAIL\*\*")
impl_lines = [l for l in t.split("\n") if clause.search(l)]
chk("implementer boundary selects exactly one line", len(impl_lines) == 1,
    f"{len(impl_lines)} line(s)")
impl_span = impl_lines[0] if impl_lines else ""
chk("implementer span is a verbatim substring", impl_span in t)
print("  IMPL SPAN:", impl_span)
t_ex = section_text("claude-verification-report-v010#001a")
phrase = "R60 fails as a whole"
chk("examiner phrase occurs exactly once", t_ex.count(phrase) == 1,
    f"count={t_ex.count(phrase)}")
i = t_ex.find(phrase)
end = t_ex.find(".", i) + 1
exam_span = t_ex[i:end]
chk("examiner span is a verbatim substring", exam_span in t_ex and exam_span.endswith("."))
print("  EXAM SPAN:", exam_span)
t_adj = section_text("alex-combined-adjudication-v010#002")
marker = "- **R60 — FAIL.**"
chk("adjudication bullet marker occurs exactly once", t_adj.count(marker) == 1)
i = t_adj.find(marker)
nxt = t_adj.find("\n- **R", i + 1)
adj_span = t_adj[i:] if nxt == -1 else t_adj[i:nxt]
chk("adjudication span is a verbatim substring", adj_span in t_adj)
chk("adjudication span length is the declared 602 chars", len(adj_span) == 602,
    f"len={len(adj_span)}")
print(f"  ADJ SPAN ({len(adj_span)} chars):", adj_span)
# Worksheet rows per section 3.1: source ref, class, verbatim span.
rows = [
    {"source_ref": "d3-v010-change-record#007", "class": "implementer", "span": impl_span},
    {"source_ref": "claude-verification-report-v010#001a", "class": "examiner", "span": exam_span},
    {"source_ref": "alex-combined-adjudication-v010#002", "class": "adjudicator", "span": adj_span},
]
declared_rows = [("d3-v010-change-record#007", "implementer"),
                 ("claude-verification-report-v010#001a", "examiner"),
                 ("alex-combined-adjudication-v010#002", "adjudicator")]
chk("worksheet rows carry the declared source refs and classes",
    [(r["source_ref"], r["class"]) for r in rows] == declared_rows,
    f"{[(r['source_ref'], r['class']) for r in rows]}")
chk("every worksheet span is verbatim in its named source",
    all(r["span"] in section_text(r["source_ref"]) for r in rows))

print("=" * 70)
print("TEST 2 — T02 derivation + T03 disposition bullets (§3.2, §3.3)")
m = re.findall(r"\*\*R60 — (PASS|FAIL)", adj_span)
chk("derivation matches exactly once inside the span", len(m) == 1, f"{m}")
chk("derived value is FAIL", m == ["FAIL"])
starts = [mm.start() for mm in re.finditer(r"(?m)^- \*\*R", t_adj)]
bullets = []
for k, s0 in enumerate(starts):
    e0 = starts[k + 1] if k + 1 < len(starts) else len(t_adj)
    bullets.append(t_adj[s0:e0].rstrip("\n"))
chk("exactly 3 disposition bullets", len(bullets) == 3, f"{len(bullets)}")
for b in bullets:
    print("  BULLET:", b.replace("\n", " ")[:160])

print("=" * 70)
print("TEST 3 — T04 interpretation procedure + declared vocabulary (§4.1; Alex point 4)")
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
fixture_nonperm = sorted(verb[n] for n in noun_list)
# The tree's declared vocabulary, read from the V2 trees document
# (T04-STEP-01), not restated by the test.
trees_text = norm(TREES_DOC.read_text())
t04_sec = trees_text[trees_text.find("## T04"):trees_text.find("## T05")]
dm = re.search(r"permitted-action list \(([^)]+)\) and the non-permitted list \(([^)]+)\)", t04_sec)
declared_perm = sorted(x.strip() for x in dm.group(1).split(",")) if dm else []
declared_nonperm = sorted(x.strip() for x in dm.group(2).split(",")) if dm else []
print("  DECLARED permitted:", declared_perm, "| non-permitted:", declared_nonperm)
print("  FIXTURE-DERIVED non-permitted:", fixture_nonperm)
chk("tree declares a permitted list of exactly 3", len(declared_perm) == 3)
chk("fixture-derived non-permitted set EQUALS the tree's declared list",
    fixture_nonperm == declared_nonperm,
    f"fixture={fixture_nonperm} declared={declared_nonperm}")
chk("declared permitted set is exactly {answer, extract, retrieve}",
    declared_perm == ["answer", "extract", "retrieve"], f"{declared_perm}")
chk("permitted and non-permitted sets are disjoint and cover the 7-verb table",
    not set(declared_perm) & set(declared_nonperm)
    and len(set(declared_perm) | set(declared_nonperm)) == 7)
# T04-STEP-02 against the tree's own task: its three requested
# actions all fall in the non-permitted set (all ESCALATE).
task4 = packs["trees"]["T04"]["task"]
requested = re.findall(r"\(\d\) (\w+)", task4)
chk("the tree's 3 requested actions all match the non-permitted set",
    sorted(requested) == declared_nonperm[:3] or
    all(r in declared_nonperm for r in requested) and len(requested) == 3,
    f"requested={requested}")

print("=" * 70)
print("TEST 4 — T06 statement operations (§3.4; Alex points 1 and 3)")
r = extract(rules, "fixtures_executed", section_text("r60-revision-change-record#009"))
chk("S1 fixtures_executed EXTRACTED 38",
    r["verification"] == "EXTRACTED" and r["value"] == 38, json.dumps(r)[:120])
r = extract(rules, "fixtures_passed", section_text("r60-revision-change-record#009"))
chk("S1 fixtures_passed EXTRACTED 38",
    r["verification"] == "EXTRACTED" and r["value"] == 38, json.dumps(r)[:120])
r = cs.get_section("duenna-plan#999")
chk("S3 lookup of duenna-plan#999 returns NOT FOUND",
    r.get("verification") == "NOT FOUND", json.dumps(r)[:120])
# --- S2 (Alex point 3): STEP-A source location over the whole
# pinned corpus; STEP-B records the result. The statement is read
# from the tree's own task text.
task6 = packs["trees"]["T06"]["task"]
s2m = re.search(r"(?m)^S2: (.+)$", task6)
s2_stmt = s2m.group(1) if s2m else ""
chk("S2 statement read from the tree task (Grok approval claim)",
    "Grok" in s2_stmt and "approved" in s2_stmt, s2_stmt)
APPROVAL_RECORD = re.compile(
    r"grok (has )?(approved|approves|ruled in favour)|"
    r"grok's (approval|adjudication) (was|is) (given|delivered|recorded|in favour)", re.I)
def classify_grok_sentence(sent):
    if APPROVAL_RECORD.search(sent):
        return "APPROVAL_RECORD"
    if "outstanding" in sent.lower():
        return "OUTSTANDING"
    if "no record" in sent.lower() or "no mention" in sent.lower() \
       or "does not contain" in sent.lower():
        return "ABSENCE_STATEMENT"
    return "MENTION"
grok_hits = []
for sid, s in secs.items():
    if "grok" in s["text"].lower():
        for sent in re.split(r"(?<=[.!?])\s+", s["text"].replace("\n", " ")):
            if "grok" in sent.lower():
                grok_hits.append((sid, classify_grok_sentence(sent), sent.strip()[:110]))
classes = {}
for _, c, _ in grok_hits:
    classes[c] = classes.get(c, 0) + 1
for sid, c, snip in grok_hits:
    print(f"  S2 SCAN {sid} [{c}]: {snip}")
chk("S2 STEP-A scan found Grok-bearing sentences to classify",
    len(grok_hits) > 0, f"{len(grok_hits)} sentences, classes={classes}")
chk("S2 STEP-A: no APPROVAL_RECORD anywhere in the pinned corpus",
    classes.get("APPROVAL_RECORD", 0) == 0, f"classes={classes}")
chk("S2 STEP-A: the trail shows the adjudication OUTSTANDING at least once",
    classes.get("OUTSTANDING", 0) >= 1, f"classes={classes}")
s2_result = "NOT FOUND" if classes.get("APPROVAL_RECORD", 0) == 0 else "FOUND"
chk("S2 STEP-B records NOT FOUND -> UNTRACEABLE (no resolvable pack source)",
    s2_result == "NOT FOUND")
# --- S4 (Alex point 1): complete-set assertion against section
# 3.4's enumeration, then an INDEPENDENT unanimity classifier.
t = section_text("vane-examination-report-v24#001b")
markers = ["not executed", "unavailable", "outstanding", "cannot",
           "incomplete", "could not"]
lines = t.split("\n")
sset = [(n + 1, l) for n, l in enumerate(lines) if "execut" in l.lower()]
EXPECTED_S4 = {
    1: "v2.3 sabotage runs — not executed",
    3: "independent rerun unavailable",
    5: "execution outstanding",
    10: "cannot independently certify",
    12: "independent execution evidence incomplete",
}
chk("S4 line set is exactly lines {1, 3, 5, 10, 12}",
    [n for n, _ in sset] == sorted(EXPECTED_S4), f"{[n for n, _ in sset]}")
chk("S4 every expected line carries its declared content",
    all(EXPECTED_S4[n] in l for n, l in sset),
    "; ".join(f"L{n}" for n, _ in sset))
for n, l in sset:
    hit = [mk for mk in markers if mk in l.lower()]
    print(f"  S4 L{n} markers={hit}: {l[:100]}...")
chk("S4 every line carries a declared non-execution marker",
    all(any(mk in l.lower() for mk in markers) for _, l in sset))
# Independent unanimity: a disposition classifier mapping whole
# phrases to status values, with a positive-execution detector
# and control lines proving the classifier can say EXECUTED.
PHRASE_STATUS = [
    (r"could not be executed", "NOT_EXECUTED"),
    (r"not executed", "NOT_EXECUTED"),
    (r"independent rerun unavailable", "UNAVAILABLE"),
    (r"rerun unavailable", "UNAVAILABLE"),
    (r"execution outstanding", "OUTSTANDING"),
    (r"cannot independently certify", "CANNOT_CERTIFY"),
    (r"execution evidence incomplete", "INCOMPLETE"),
]
EXECUTED_POS = re.compile(
    r"(sabotage|harness|fixture) (was|were|has been) executed|executed the", re.I)
NON_EXECUTION = {"NOT_EXECUTED", "UNAVAILABLE", "OUTSTANDING",
                 "CANNOT_CERTIFY", "INCOMPLETE"}
def classify_disposition(line):
    st = set()
    if EXECUTED_POS.search(line):
        st.add("EXECUTED")
    for pat, val in PHRASE_STATUS:
        if re.search(pat, line):
            st.add(val)
    return st
ctrl_pos = classify_disposition("The identity sabotage was executed and failed.")
ctrl_neg = classify_disposition("The committee met on Tuesday to discuss scheduling.")
chk("classifier control: a positive execution line classifies EXECUTED",
    "EXECUTED" in ctrl_pos, f"{ctrl_pos}")
chk("classifier control: an unrelated line classifies empty",
    ctrl_neg == set(), f"{ctrl_neg}")
per_line = {n: classify_disposition(l) for n, l in sset}
for n, st in per_line.items():
    print(f"  S4 L{n} disposition classes: {sorted(st)}")
chk("S4 unanimity (independent): every line classifies non-execution only",
    all(st and st <= NON_EXECUTION for st in per_line.values()),
    f"{per_line}")

print("=" * 70)
print("TEST 5 — T07 register parse + element lookups (§3.5; Alex R3 points 1-3)")
reg = fixtures["fixtures"]["obligation-register"]
blocks = re.split(r"\n(?=OB-\d — )", reg)
obs = {}
for b in blocks:
    mh = re.match(r"OB-(\d) — (.+)", b)
    if not mh:
        continue
    oid = f"OB-{mh.group(1)}"
    obs[oid] = {
        "block": b,
        "deliverable": re.search(r"Deliverable: (.+)", b).group(1).strip(),
        "condition": re.search(r"Completion condition: (.+?)(?=\n  Pack evidence:|\Z)",
                               b, re.S).group(1).replace("\n  ", " ").strip(),
        "evidence": (re.search(r"Pack evidence: (.+?)(?=\nOB-|\Z)", b, re.S)
                     or [None, ""])[1].replace("\n  ", " ").strip(),
        "due": (re.search(r"Due: (\d{4}-\d{2}-\d{2})", b) or [None, None])[1],
    }
chk("register parses to exactly 3 obligations", len(obs) == 3, f"{sorted(obs)}")
chk("OB-3 due date is 2026-11-10", obs.get("OB-3", {}).get("due") == "2026-11-10")
# Lookup OB-1: shelf record via CorpusSource (class-C lookup).
r = cs.get_manifest_row("pilot-manifest:PILOT-DATA-FIXTURES-01#shelf-record-181a30d")
chk("OB-1 element lookup: shelf record FOUND", "value" in r)
chk("OB-1 element: commit matches register's stated 181a30d",
    "181a30d" in r.get("value", ""))
ob1_found = "value" in r and "181a30d" in r.get("value", "")

# ---- Declared lookup machinery (Round 4) ---------------------
# A lookup searches a DECLARED source set for an element spec.
# It returns FOUND only when a record satisfies EVERY clause of
# the spec. Otherwise it returns NOT FOUND — and the result is
# established by exhaustive enumeration: every candidate record
# in the source set is printed with the clause(s) it fails.
# Absence of a positive phrase is never itself the result.
def sentences_of(text):
    return [s.strip() for s in
            re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]

# ---- OB-2 element 1: independent execution receipt ----------
# Spec (from OB-2's completion condition): a receipt that
# (a) is a record OF the execution event, (b) concerns the
# FX-R60k identity sabotage on the v2.4 harness, (c) states the
# sabotage was EXECUTED, (d) carries evidence_status [verified],
# (e) is INDEPENDENT — it exists as a record of the event, not
# as a worksheet fixture inside the pilot test-data files that
# define the obligation spec itself (a fixture is a constructed
# input; it cannot independently certify the event it
# simulates), (f) its sha256 equals the v2.4 harness sha.
# Declared source set: the register fixture, the examination
# section (T07's pack sources), the shelf-record fixture, and
# both receipt registries (fixtures + T09), contents included.
chk("register's OB-2 pack evidence records the sabotage as NOT executed",
    "recorded as NOT executed" in obs["OB-2"]["evidence"],
    obs["OB-2"]["evidence"][:110])
exam = section_text("vane-examination-report-v24#001b")
e1_candidates = []
for l in exam.split("\n"):
    if "FX-R60k" in l or "identity sabotage" in l.lower():
        low = l.lower()
        if "not executed" in low:
            verdict = "fails (c): records NOT executed"
        elif "executed" in low:
            verdict = "CANDIDATE-EXECUTED"
        else:
            verdict = "fails (a)/(c): discusses the sabotage, records no execution"
        e1_candidates.append(("examination v24#001b", verdict, l[:110]))
for src_name, registry in (("fixtures RECEIPTS", fixtures.get("RECEIPTS", {})),
                           ("t09 RECEIPTS", t09.get("RECEIPTS", {}))):
    for rid, rec in registry.items():
        fails = []
        res = rec.get("result", "")
        if "FX-R60k" not in res:
            fails.append("(b) subject")
        if "executed" not in res.lower():
            fails.append("(c) no execution stated")
        if rec.get("evidence_status") != "[verified]":
            fails.append("(d) evidence_status")
        if rec.get("sha256") != expected["V24_HARNESS_SHA"]:
            fails.append("(f) sha != harness sha")
        fails.append("(e) independence: worksheet fixture inside the "
                     "pilot test-data files, not an independent record")
        e1_candidates.append((f"{src_name}:{rid}", "; ".join(fails),
                              json.dumps(rec)[:110]))
shelf_rec = fixtures["fixtures"]["shelf-record-181a30d"]
e1_candidates.append(("shelf-record-181a30d",
                      "fails (b): records the shelving of Vane's report, "
                      "not a sabotage execution", str(shelf_rec)[:110]))
for src, verdict, snip in e1_candidates:
    print(f"  E1 candidate [{src}] {verdict} :: {snip}")
e1_found = any(v == "CANDIDATE-EXECUTED" for _, v, _ in e1_candidates)
chk("OB-2 element 1 lookup: exhaustive over the declared source set, "
    "every candidate dispositioned", len(e1_candidates) >= 6,
    f"{len(e1_candidates)} candidates")
chk("OB-2 element 1 (independent execution receipt): NOT FOUND",
    not e1_found)
# ---- OB-2 element 2: closing adjudication -------------------
adj_secs = {sid: s for sid, s in secs.items() if "adjudication" in s["doc"]}
e2_hits = []
for sid, s in adj_secs.items():
    for sent in sentences_of(s["text"]):
        if "Correction B" in sent:
            low = sent.lower()
            if re.search(r"correction b (is )?closed|closes correction b|"
                         r"correction b: closed", low):
                e2_hits.append((sid, "CLOSING", sent[:110]))
            else:
                e2_hits.append((sid, "NOT_CLOSING", sent[:110]))
for sid, v, snip in e2_hits:
    print(f"  E2 candidate [{sid}] {v} :: {snip}")
e2_found = any(v == "CLOSING" for _, v, _ in e2_hits)
chk("OB-2 element 2 lookup: every adjudication doc's Correction-B "
    "statements enumerated", len(adj_secs) >= 1 and len(e2_hits) >= 1,
    f"{len(adj_secs)} docs, {len(e2_hits)} statements")
chk("OB-2 element 2 (closing adjudication): NOT FOUND; the combined "
    "adjudication derives FAIL (Test 2)", not e2_found and m == ["FAIL"])
# ---- OB-3: absence operation over source CONTENTS -----------
# Matching rule: a publication record for OB-3 is a record that
# ASSERTS the Qwen A/B test results were published. Subject =
# a sentence mentioning both a publish-word and the Qwen A/B
# results. Classification order: NEGATED (denies a record /
# states none / not published), PROSPECTIVE (obligation,
# requirement, or future), ASSERTIVE (states it happened),
# else AMBIGUOUS. Absence is established only if every subject
# sentence in every enumerated source classifies NEGATED or
# PROSPECTIVE and the AMBIGUOUS list is empty; otherwise the
# result is UNKNOWN, never NOT FOUND.
PUB_WORD = re.compile(r"publish", re.I)
SUBJECT = re.compile(r"qwen|a/b|a-b", re.I)
NEGATED = re.compile(r"no publication record|not published|never published|"
                     r"unpublished|no record of publication|publication "
                     r"record exists in this pack", re.I)
PROSPECTIVE = re.compile(r"publish the|to publish|publication record\.|"
                         r"completion condition|due:", re.I)
ASSERTIVE = re.compile(r"results (were|was|have been) published|"
                       r"published the (qwen|a/b)|was published on|"
                       r"publication record: (?!none)", re.I)
def classify_publication(sent):
    if NEGATED.search(sent):
        return "NEGATED"
    if ASSERTIVE.search(sent):
        return "ASSERTIVE"
    if PROSPECTIVE.search(sent):
        return "PROSPECTIVE"
    return "AMBIGUOUS"
ob3_sources = {}
for sid, s in secs.items():
    ob3_sources[f"section:{sid}"] = s["text"]
ob3_sources["fixture:obligation-register"] = reg
for rid, rec in fixtures.get("RECEIPTS", {}).items():
    ob3_sources[f"fixtures-RECEIPTS:{rid}"] = json.dumps(rec)
for rid, rec in t09.get("RECEIPTS", {}).items():
    ob3_sources[f"t09-RECEIPTS:{rid}"] = json.dumps(rec)
ob3_classes = {}
ob3_ambiguous = []
ob3_assertive = []
for label, text in ob3_sources.items():
    for sent in sentences_of(text):
        if PUB_WORD.search(sent) and SUBJECT.search(sent):
            c = classify_publication(sent)
            ob3_classes[c] = ob3_classes.get(c, 0) + 1
            print(f"  OB-3 scan [{label}] {c} :: {sent[:110]}")
            if c == "AMBIGUOUS":
                ob3_ambiguous.append((label, sent[:110]))
            if c == "ASSERTIVE":
                ob3_assertive.append((label, sent[:110]))
n_pack_refs = sum(len(tr["pack"]) for tr in packs["trees"].values())
chk("register's OB-3 evidence states no publication record exists",
    obs["OB-3"]["evidence"].lower().startswith("none"),
    obs["OB-3"]["evidence"][:80])
chk("OB-3 absence operation inspected the CONTENTS of the full "
    "enumerated source set", len(ob3_sources) == len(secs) + 1
    + len(fixtures.get("RECEIPTS", {})) + len(t09.get("RECEIPTS", {})),
    f"{len(ob3_sources)} sources (incl. all {len(secs)} corpus sections); "
    f"{n_pack_refs} tree pack refs resolve into these same sources")
print("  OB-3 subject-sentence classes:", ob3_classes)
if ob3_assertive:
    ob3_result = "FOUND"
elif ob3_ambiguous:
    ob3_result = "UNKNOWN"
else:
    ob3_result = "NOT FOUND"
chk("OB-3 absence result is NOT FOUND (no assertive record, none ambiguous)",
    ob3_result == "NOT FOUND", f"result={ob3_result} classes={ob3_classes}")
ob3_found = ob3_result == "FOUND"
# Status rule operates on the lookup RESULTS (nothing assigned).
status = {
    "OB-1": "CLOSED" if ob1_found else "OPEN",
    "OB-2": "CLOSED" if (e1_found and e2_found) else "OPEN",
    "OB-3": "CLOSED" if ob3_found else "OPEN",
}
chk("status rule over lookup results reproduces OB_TRUTH",
    status == expected["OB_TRUTH"], json.dumps(status))


print("=" * 70)
print("TEST 6 — T09 structured read: complete schema contract (§4.2; Alex point 5)")
ob = t09["OBLIGATION_T09"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IDENT = re.compile(r"^[a-z][a-z0-9_]*$")
chk("required_fields is a list of exactly 5 identifier strings",
    isinstance(ob["required_fields"], list) and len(ob["required_fields"]) == 5
    and all(isinstance(x, str) and IDENT.match(x) for x in ob["required_fields"]),
    f"{ob['required_fields']}")
chk("artifact is a non-empty string",
    isinstance(ob["artifact"], str) and len(ob["artifact"]) > 0, ob["artifact"])
chk("sha256 is a string with hex64 shape",
    isinstance(ob["sha256"], str) and bool(HEX64.match(ob["sha256"])))
chk("sha256 equals EXPECTED-01 V24_HARNESS_SHA",
    ob["sha256"] == expected["V24_HARNESS_SHA"])
chk("result_contains is a non-empty string",
    isinstance(ob["result_contains"], str) and len(ob["result_contains"]) > 0)
chk("evidence_status is a string and equals [verified]",
    isinstance(ob["evidence_status"], str) and ob["evidence_status"] == "[verified]")
def schema_valid(rec):
    if not isinstance(rec, dict):
        return False
    for f in ob["required_fields"]:
        if f not in rec:
            return False
    return (isinstance(rec["artifact"], str)
            and isinstance(rec["sha256"], str) and bool(HEX64.match(rec["sha256"]))
            and isinstance(rec["result"], str)
            and isinstance(rec["evidence_status"], str)
            and isinstance(rec["examiner"], str))
def worksheet_accept(rec):
    return (schema_valid(rec)
            and rec["sha256"] == ob["sha256"]
            and rec["evidence_status"] == ob["evidence_status"]
            and ob["result_contains"] in rec["result"])
smap = {rid: schema_valid(rec) for rid, rec in t09["RECEIPTS"].items()}
amap = {rid: worksheet_accept(rec) for rid, rec in t09["RECEIPTS"].items()}
print("  RECEIPT schema validity:", smap)
print("  RECEIPT worksheet acceptance:", amap)
chk("per-receipt schema validity is {FR-A: True, FR-B: False, FR-C: True, FR-VALID: True}",
    smap == {"FR-A": True, "FR-B": False, "FR-C": True, "FR-VALID": True}, f"{smap}")
chk("worksheet acceptance admits exactly FR-VALID",
    amap == {"FR-A": False, "FR-B": False, "FR-C": False, "FR-VALID": True}, f"{amap}")
chk("hex64 shape check rejects uppercase and 63-char controls",
    not HEX64.match(ob["sha256"].upper()) and not HEX64.match(ob["sha256"][:-1]))
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
    mm = re.search(r'"' + re.escape(tid) + r'":\s*\{\s*"sha256":\s*"([0-9a-f]{64})"', man)
    if mm:
        exp_hashes[tid] = mm.group(1)
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
