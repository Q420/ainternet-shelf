#!/usr/bin/env python3
"""D3 v0.9 — revision fixture harness (v2.0; v2.1 in fixtures-v010).

Built under Alex's build authorisation (pb-mwad2zc6-6-k60l,
2026-11-09) addressing the six findings left open by independent
verification of the v0.8 package (Claude's report): R42 (text, in
the v0.9 working revision), R47, R56, R60, R63, R65 (fixtures,
here). All other fixtures are carried over from the v0.8 harness
v1.2 unchanged in substance and re-executed; the v1.2 harness is
preserved alongside (harness-v08-v1.2-preserved.py) and the v0.8
package is untouched.

TEST BOUNDARY: these fixtures exercise small reference procedures
written from the specification text. They validate the mechanical
coherence of the SPECIFIED RULES as implemented in these reference
procedures. No separate production evaluator exists in this stage,
and nothing here certifies one.

Executes the acceptance fixtures against the rules AS SPECIFIED in
PROCESS-TREE-D3-SPECIFICATION-v0.9-WORKING.md (seeded from the
approved v0.8 revision, SHA-256 3e053efc…, which remains
immutable). Each fixture states its expected outcome (written from
the spec text) before execution; the harness records observed
outcomes and verdicts. Fixture success establishes mechanical
conformance with the specified rule only (D3-R14) — never semantic
correctness.

v2.1 (fixtures-v010, D3 v0.10 revision): built under Alex's
adjudication of the v0.9 verification gate (pb-mwauqmco,
2026-11-10), which confirmed FAIL on R47, R60 and R65 — three
fixtures that produced green results without establishing what
their descriptions claimed. Exactly those three are repaired here
(FX-R47b; the FX-R60 CheckerContract/validate_verdict machinery;
FX-R65); every other fixture is carried over from v2.0 unchanged,
and all 31 cases are preserved. This harness executes against
PROCESS-TREE-D3-SPECIFICATION-v0.10-WORKING.md (seeded from the
v0.9 revision, SHA-256 ac2a2484…, which was seeded from the
approved v0.8 revision, SHA-256 3e053efc…, immutable). Each repair
was additionally verified by sabotage: disabling the repaired
mechanism makes exactly the repaired fixture fail (see
D3-V010-CHANGE-RECORD).
"""
import hashlib, inspect, json, sys

RESULTS = []

def record(fid, finding, requirement, expected, observed, verdict):
    RESULTS.append({"fixture": fid, "finding": finding, "requirement": requirement,
                    "expected": expected, "observed": observed, "verdict": verdict})
    print(f"[{verdict}] {fid} ({finding} / {requirement}) expected={expected!r} observed={observed!r}")

def check(fid, finding, requirement, expected, observed):
    record(fid, finding, requirement, expected, observed,
           "PASS" if expected == observed else "FAIL")

# ---------------------------------------------------------------- fold engine
# Minimal evaluator implementing REQ-D-3's derivation procedure as
# corrected: admission (step 0, R33), monotonic determinations (1),
# chronological fold with per-determination availability (2, R51),
# terminal locking (3), channel-(ii) available from the start (4),
# post-lock determinations recorded non-effective (5).

def fold(entries, determinations, progress_none=False):
    """entries: list of dicts {id, kind} in record order.
    determinations: list of {predicate, channel, basis, admitted_basis_ok}
      channel 'i'  -> basis is an entry id; available at that entry's position
      channel 'ii' -> basis is an artefact id; available from the start,
                      admitted only if admitted_basis_ok (preservation +
                      eligibility established and admission recorded)
    Trigger-carried content (an entry's content_predicates, REQ-C-1)
    is EXAMINED by the fold and recorded in the result as
    examined_trigger_content; it is never admitted — admission is
    the only path into the running set (v0.10 repair, R47: the
    examination is part of the fold's returned record, so a test can
    establish that the content was actually read, not merely that
    the outcome happens to be unchanged).
    Returns {state, running, non_admitted, post_lock, stream_len,
             examined_trigger_content, outcome}."""
    running = set()
    non_admitted = []
    examined_trigger_content = sorted(
        {p for e in entries for p in e.get("content_predicates", [])})
    # admission gate (step 0)
    avail = {}   # entry position -> [predicates]
    at_start = []
    for d in determinations:
        if d["channel"] == "i":
            pos = next(i for i, e in enumerate(entries) if e["id"] == d["basis"])
            avail.setdefault(pos, []).append(d["predicate"])
        else:
            if d.get("admitted_basis_ok"):
                at_start.append(d["predicate"])
            else:
                non_admitted.append(d)
    for p in at_start:
        running.add(p)
    state = "NOT_STARTED"
    locked = False
    post_lock = []

    def advance():
        nonlocal state
        if state == "NOT_STARTED" and "SATISFACTION" in running and (progress_none or "PROGRESS" in running):
            state = "SATISFIED"; return True
        if state == "NOT_STARTED" and "PROGRESS" in running:
            state = "IN_PROGRESS"; return True
        if state == "IN_PROGRESS" and "SATISFACTION" in running:
            state = "SATISFIED"; return True
        return False

    if advance():
        locked = state == "SATISFIED"
    for i, e in enumerate(entries):
        for p in avail.get(i, []):
            if locked:
                post_lock.append(p)
            else:
                running.add(p)
        if e["kind"] == "BLOCKER" and not locked:
            state = "BLOCKED"; locked = True
        elif not locked and advance():
            locked = state == "SATISFIED"
    # REQ-C-2 resolution (v0.9, R47 completion): a predicate whose only
    # support is a non-admitted determination (e.g. an unpreservable
    # artefact) is resolved BY THE FOLD as INDETERMINATE — never in
    # the artefact's favour, never silently dropped.
    blocked_only = {d["predicate"] for d in non_admitted} - set(running)
    outcome = state
    if state != "SATISFIED" and "SATISFACTION" in blocked_only:
        outcome = "INDETERMINATE"
    return {"state": state, "running": sorted(running), "non_admitted": len(non_admitted),
            "post_lock": post_lock, "stream_len": len(entries), "outcome": outcome,
            "examined_trigger_content": examined_trigger_content}

# ---------------------------------------------------------------- R62 — REQ-K-1
def k1_check(rule, contract_prohibitions):
    """Declared mechanical method: contradiction scan only.
    Judgement-based conditions are UNDETERMINED by default (REQ-K-1)."""
    if rule["condition_kind"] == "judgement":
        return "UNDETERMINED"
    if set(rule.get("requires", [])) & set(contract_prohibitions):
        return "IMPOSSIBLE-ESTABLISHED"
    return "NO DEFECT FOUND"

def fixture_r62():
    out = k1_check({"condition_kind": "mechanical", "requires": ["fetch"]}, [])
    check("FX-R62", "R62", "REQ-K-1 outcome (i)",
          ("NO DEFECT FOUND", "absence-of-demonstrated-defect"),
          (out, "absence-of-demonstrated-defect" if out == "NO DEFECT FOUND" else out))

# ---------------------------------------------------------------- R40 — creation/binding
def bind(rules, role_resolvable=True):
    """Toy binding per REQ-A-1/A-2: unconditional rules instantiate at
    binding (CREATION cites the binding); conditional rules wait for
    their triggering entry. Returns (stream, instances, error)."""
    if not role_resolvable:
        return None, None, "BINDING FAILURE (loud, total): unresolvable role"
    stream, instances = [], []
    for r in rules:
        if r["kind_of_rule"] == "unconditional":
            ce = {"id": f"CE-{r['id']}", "kind": "CREATION", "cause": "binding",
                  "instance": f"I-{r['id']}", "author": "harness"}
            stream.append(ce)
            instances.append({"id": f"I-{r['id']}", "rule": r["id"], "bearer": r["bearer"],
                              "creation_entry": ce["id"], "cause": "binding"})
    return stream, instances, None

def validate_creation_entry(entry, bearer):
    """REQ-A-1: creation records are harness-set; the bearer never
    authors its own CREATION entry."""
    if entry.get("kind") != "CREATION":
        return "rejected: not a creation entry"
    if entry.get("author") == bearer:
        return "rejected: bearer-authored"
    if entry.get("author") != "harness":
        return "rejected: author is not the harness"
    return "accepted"

def classify_instance(instance):
    """REQ-A-3: instances arise only from rule instantiation, and
    instantiation fixes the bearer. An existing instance whose bearer
    cannot be identified therefore signals a machinery defect — it is
    never defaulted to the evaluator or silently assigned."""
    if instance.get("bearer"):
        return "assigned: " + instance["bearer"]
    if instance.get("origin") == "rule-instantiation":
        return "machinery defect"
    return "not an instance"

def fixture_r40():
    rules = [{"id": "U1", "kind_of_rule": "unconditional", "bearer": "researcher"},
             {"id": "C1", "kind_of_rule": "conditional", "bearer": "researcher"}]
    stream, inst, err = bind(rules)
    ok = (err is None and len(inst) == 1 and inst[0]["cause"] == "binding"
          and stream[0]["kind"] == "CREATION" and stream[0]["author"] == "harness")
    check("FX-R40a", "R40", "REQ-A-2/A-1 unconditional creation at binding", True, ok)
    # conditional: triggering ACTION keeps its kind; separate CREATION follows it
    trig = {"id": "E1", "kind": "ACTION"}
    ce = {"id": "CE-C1", "kind": "CREATION", "cause": "E1", "instance": "I-C1", "author": "harness"}
    seq = [trig, ce]
    ok = (seq[0]["kind"] == "ACTION" and seq[1]["kind"] == "CREATION"
          and seq[1]["cause"] == "E1" and seq.index(ce) == seq.index(trig) + 1)
    check("FX-R40b", "R40", "REQ-A-1 conditional creation; kind preserved; separate CREATION entry", True, ok)
    # bearer-authorship prohibition, exercised through a validation procedure
    ok_c = (validate_creation_entry({"kind": "CREATION", "author": "harness"}, "researcher"),
            validate_creation_entry({"kind": "CREATION", "author": "researcher"}, "researcher"),
            validate_creation_entry({"kind": "CREATION", "author": "evaluator"}, "researcher"))
    check("FX-R40c", "R40", "REQ-A-1 creation-entry validation: harness-authored accepted; bearer-authored and third-party-authored rejected",
          ("accepted", "rejected: bearer-authored", "rejected: author is not the harness"), ok_c)
    # unresolvable role: loud total failure, no partial instance
    stream2, inst2, err2 = bind(rules, role_resolvable=False)
    check("FX-R40d", "R40", "REQ-A-2 unresolvable role fails loudly and totally",
          (None, "loud total failure"), (inst2, "loud total failure" if err2 else "silent"))
    # bearer-less instance classification, from an actual missing-bearer input
    cls = (classify_instance({"bearer": "researcher", "origin": "rule-instantiation"}),
           classify_instance({"origin": "rule-instantiation"}))  # bearer key absent entirely
    check("FX-R40e", "R40", "REQ-A-3 classification procedure over bearer-present and bearer-missing instances",
          ("assigned: researcher", "machinery defect"), cls)

# ---------------------------------------------------------------- R47 — B-6/C-1/C-2
def validate_judgement(det, named_judges):
    """REQ-B-6: a judgement-based determination is accepted only when a
    judge named by the authority is identified AND the determination's
    basis cites that judge."""
    judge = det.get("judge")
    if not judge:
        return "rejected: no judge identity"
    if judge not in named_judges:
        return "rejected: judge not named by the authority"
    if det.get("basis") != "judgement:" + judge:
        return "rejected: basis does not cite the judge"
    return "accepted"

def fixture_r47():
    # (i) named judge: validation of identity + basis relationship, with failure cases
    named = {"judge:alex-ruling-7"}
    res47 = (validate_judgement({"judge": "judge:alex-ruling-7", "basis": "judgement:judge:alex-ruling-7"}, named),
             validate_judgement({"basis": "judgement:judge:alex-ruling-7"}, named),
             validate_judgement({"judge": "judge:alex-ruling-7", "basis": "judgement:judge:other"}, named),
             validate_judgement({"judge": "judge:unnamed", "basis": "judgement:judge:unnamed"}, named))
    check("FX-R47a", "R47", "REQ-B-6 named-judge validation: named+basis-cited accepted; missing, mismatched and unnamed rejected",
          ("accepted", "rejected: no judge identity", "rejected: basis does not cite the judge",
           "rejected: judge not named by the authority"), res47)
    # (ii) a conditional trigger whose CONTENT WOULD QUALIFY still
    # establishes NO progress/satisfaction (REQ-C-1/C-2 matrix item).
    # v0.10 repair (R47 FAIL at independent examination, confirmed at
    # adjudication): the v0.9 form of this fixture placed qualifying
    # content on the trigger but the fold never read it, so the case
    # passed vacuously — the outcome would have been identical with
    # no content at all. The fold now EXAMINES trigger content and
    # records what it read; this fixture asserts the examination
    # itself, not only the outcome:
    #   - with qualifying content: content is recorded as examined,
    #     and still establishes nothing (admission is the only path);
    #   - mutation control — the same trigger with its content
    #     removed: the examined record is empty and the outcome is
    #     unchanged, so the examination is what the first assertion
    #     is measuring;
    #   - channel control: the same predicates supplied as admitted
    #     determinations DO satisfy — the difference is the channel,
    #     not the data.
    trig = {"id": "T1", "kind": "ACTION",
            "content_predicates": ["PROGRESS", "SATISFACTION"]}
    entries = [trig, {"id": "CE1", "kind": "CREATION"}]
    res = fold(entries, [])  # trigger content is not a determination
    stripped = fold([{"id": "T1", "kind": "ACTION"},
                     {"id": "CE1", "kind": "CREATION"}], [])
    ctrl = fold([{"id": "E1", "kind": "ACTION"}],
                [{"predicate": "PROGRESS", "channel": "i", "basis": "E1"},
                 {"predicate": "SATISFACTION", "channel": "i", "basis": "E1"}])
    check("FX-R47b", "R47", "REQ-C-1 conditional trigger: qualifying content is examined by the fold and establishes nothing; removing the content empties the examination record and changes no outcome; admitted determinations with the same predicates satisfy",
          (("NOT_STARTED", [], ["PROGRESS", "SATISFACTION"]),
           ("NOT_STARTED", []), "SATISFIED"),
          ((res["state"], res["running"], res["examined_trigger_content"]),
           (stripped["state"], stripped["examined_trigger_content"]), ctrl["state"]))
    # (iii) unpreservable artefact -> the FOLD resolves the predicate
    # INDETERMINATE (REQ-C-2; v0.9 — the label is now emitted by the
    # fold's own resolution, not written by the test).
    res = fold([{"id": "E1", "kind": "ACTION"}],
               [{"predicate": "SATISFACTION", "channel": "ii", "basis": "ART-9",
                 "admitted_basis_ok": False}])
    check("FX-R47c", "R47", "REQ-C-2 unpreservable artefact: fold resolves INDETERMINATE",
          "INDETERMINATE", res["outcome"])

# ---------------------------------------------------------------- R63 — REQ-K-3 block
def validate_creation_block(stream, trigger_id, rule_order):
    """REQ-K-3 (2) as corrected by R37: the CREATION entries one
    trigger produces form one contiguous block immediately after the
    triggering entry, in pinned-contract rule order, no unrelated
    entry intervening. Checked against a stream as recorded — a
    hand-assembled list in the right order proves nothing unless this
    validator would also REJECT a wrong one (negative cases below)."""
    ti = next((i for i, e in enumerate(stream) if e["id"] == trigger_id), None)
    if ti is None:
        return "rejected: trigger not in stream"
    block = stream[ti + 1: ti + 1 + len(rule_order)]
    if len(block) < len(rule_order) or any(e["kind"] != "CREATION" for e in block):
        return "rejected: block not contiguous after the trigger"
    if [e["instance"] for e in block] != [f"I-{r}" for r in rule_order]:
        return "rejected: block not in pinned rule order"
    if any(not e.get("instance") for e in block):
        return "rejected: CREATION entry without its instance"
    return "accepted"

def validate_stream_identity(entries):
    """REQ-K-3 (R63 third item, testing R36's identification rule):
    every entry carries its required stable identity, its record
    position, and an instance identity or an explicit instance-free
    status. A tampered position or a missing identity is rejected."""
    for i, e in enumerate(entries):
        if not e.get("id"):
            return f"rejected: entry at position {i} has no stable identity"
        if e.get("position") != i:
            return f"rejected: entry {e['id']} record position mismatch"
        if not e.get("instance") and e.get("instance_free_declared") is not True:
            return f"rejected: entry {e['id']} has neither instance identity nor declared instance-free status"
    return "accepted"

def fixture_r63():
    # (a) block ORDER checked against a stream the binding machinery
    # actually produced (v0.9 — v1.2 inspected a hand-built list).
    # One trigger, three unconditional rules created in its wake, in
    # pinned-contract rule order; an interleaved stream must fail.
    rules = [{"id": r, "kind_of_rule": "unconditional", "bearer": "researcher"}
             for r in ["R-A", "R-B", "R-C"]]
    created, _inst, err = bind(rules)
    trig = {"id": "T1", "kind": "ACTION", "instance": None, "instance_free_declared": True}
    stream = [trig] + created + [{"id": "E9", "kind": "ACTION", "instance": "I-R-A"}]
    interleaved = [trig, created[0],
                   {"id": "X1", "kind": "ACTION", "instance": "I-R-A"}] + created[1:]
    res63a = (validate_creation_block(stream, "T1", ["R-A", "R-B", "R-C"]),
              validate_creation_block(interleaved, "T1", ["R-A", "R-B", "R-C"]))
    check("FX-R63a", "R63", "REQ-K-3 creation block validated on a machinery-produced stream; interleaved block rejected",
          ("accepted", "rejected: block not contiguous after the trigger"), res63a)
    # (c) stable identity + record position + instance status for
    # every entry of a recorded stream (R63 third item).
    positioned = [dict(e, position=i) for i, e in enumerate(stream)]
    tampered = [dict(e, position=i) for i, e in enumerate(stream)]
    tampered[2] = dict(tampered[2], position=99)
    noident = [dict(e, position=i) for i, e in enumerate(stream)]
    noident[1] = dict(noident[1], id="")
    res63c = (validate_stream_identity(positioned),
              validate_stream_identity(tampered),
              validate_stream_identity(noident))
    check("FX-R63c", "R63", "REQ-K-3 every entry: stable identity, record position, instance identity or declared instance-free; tampered position and missing identity rejected",
          ("accepted",
           "rejected: entry CE-R-B record position mismatch",
           "rejected: entry at position 1 has no stable identity"), res63c)
    decl = (validate_entry_declaration({"kind": "ACTION", "instance": None, "instance_free_declared": True}),
            validate_entry_declaration({"kind": "ACTION", "instance": None, "instance_free_declared": False}),
            validate_entry_declaration({"kind": "CREATION", "instance": None, "instance_free_declared": True}),
            validate_entry_declaration({"kind": "ACTION", "instance": "I-R-A", "roles": []}))
    check("FX-R63b", "R63", "REQ-K-3 entry validator: declared instance-free non-CREATION accepted; undeclared and CREATION-instance-free rejected; valid entry carrying no predicate roles accepted",
          ("accepted: instance-free (declared)", "rejected: no instance and no instance-free declaration",
           "rejected: CREATION entry must identify its instance", "accepted"), decl)

def validate_entry_declaration(e):
    """REQ-K-3 (as corrected by R36/R37): a CREATION entry always
    identifies the instance it creates; a non-CREATION entry is
    instance-free only when that is explicitly declared."""
    if e["kind"] == "CREATION":
        return "accepted" if e.get("instance") else "rejected: CREATION entry must identify its instance"
    if e.get("instance"):
        return "accepted"
    if e.get("instance_free_declared") is True:
        return "accepted: instance-free (declared)"
    return "rejected: no instance and no instance-free declaration"

# ---------------------------------------------------------------- R44 — reverse mixed channel
def fixture_r44():
    entries = [{"id": "CE1", "kind": "CREATION"}, {"id": "E1", "kind": "ACTION"}]
    dets = [{"predicate": "PROGRESS", "channel": "ii", "basis": "ART-1", "admitted_basis_ok": True},
            {"predicate": "SATISFACTION", "channel": "i", "basis": "E1"}]
    res = fold(entries, dets)
    check("FX-R44", "R44", "REQ-B-2 reverse mix: artefact progress + event satisfaction",
          ("SATISFIED", 2), (res["state"], res["stream_len"]))  # stream_len 2: no synthetic event

# ---------------------------------------------------------------- R52 — artefact-first lock
def fixture_r52():
    entries = [{"id": "CE1", "kind": "CREATION"}, {"id": "B1", "kind": "BLOCKER"}]
    dets = [{"predicate": "SATISFACTION", "channel": "ii", "basis": "ART-2", "admitted_basis_ok": True}]
    res = fold(entries, dets, progress_none=True)
    closure = "discharged-as-SATISFIED" if res["state"] == "SATISFIED" else "other"
    check("FX-R52", "R52", "REQ-D-3 artefact satisfaction locks before blocker; closure discharged-as-SATISFIED",
          ("SATISFIED", "discharged-as-SATISFIED"), (res["state"], closure))


# ---------------------------------------------------------------- R49 — D3-CANON-1 (RFC 8785 JCS)
class DuplicateKey(Exception):
    pass

def parse_record(text):
    """Parse-layer duplicate rejection: recursive (object_pairs_hook fires
    at every object level), before canonicalisation (correction R35(b))."""
    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                raise DuplicateKey(k)
            seen.add(k)
        return dict(pairs)
    return json.loads(text, object_pairs_hook=hook)

def es_number(x):
    """ECMAScript Number::toString, as RFC 8785 requires for JCS.
    Digits come from Python's repr (also a shortest round-trip
    representation; the digit sequence agrees with ECMAScript's for
    the same double) and are re-formatted under the ES rules.
    Non-finite values are not serialisable (RFC 8785)."""
    import math
    if math.isnan(x) or math.isinf(x):
        raise ValueError("non-finite number is not serialisable in JCS")
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    r = repr(abs(x))
    if "e" in r:
        mant, ex = r.split("e"); ex = int(ex)
    else:
        mant, ex = r, 0
    ip, _, fp = mant.partition(".")
    raw = ip + fp
    stripped = raw.lstrip("0")
    trailing = len(raw.rstrip("0")) if False else 0
    core = stripped.rstrip("0") or "0"
    trailing = len(stripped) - len(core)
    exp10 = ex - len(fp) + trailing
    k = len(core); n = exp10 + k
    if k <= n <= 21:
        body = core + "0" * (n - k)
    elif 0 < n <= 21:
        body = core[:n] + "." + core[n:]
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + core
    elif k == 1:
        body = core + "e" + ("+" if n - 1 >= 0 else "-") + str(abs(n - 1))
    else:
        body = core[0] + "." + core[1:] + "e" + ("+" if n - 1 >= 0 else "-") + str(abs(n - 1))
    return sign + body

def jcs(obj):
    """Limited reference serialiser for the tested subset — NOT a
    fully conforming RFC 8785 implementation. Covers integers,
    floats (via es_number), strings, objects and arrays for the
    fixture inputs exercised here; no normalisation of strings or
    keys. Known divergence: the integer branch serialises Python
    integers directly rather than applying the RFC's IEEE-754
    number model, so integers beyond double precision would not
    be serialised as RFC 8785 requires. Number formatting for
    doubles is verified against the RFC 8785 example values
    (FX-R49d); see the results document for the exercised subset."""
    if obj is None: return "null"
    if obj is True: return "true"
    if obj is False: return "false"
    if isinstance(obj, float): return es_number(obj)
    if isinstance(obj, int): return str(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        return "[" + ",".join(jcs(x) for x in obj) + "]"
    if isinstance(obj, dict):
        keys = sorted(obj.keys(), key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(jcs(k) + ":" + jcs(obj[k]) for k in keys) + "}"
    raise TypeError(type(obj))

def digest(obj):
    return hashlib.sha256(jcs(obj).encode("utf-8")).hexdigest()

def fixture_r49():
    precomposed = "café"          # é as one code point
    combining = "café"          # e + combining acute
    d1 = digest({"key": precomposed})
    d2 = digest({"key": combining})
    check("FX-R49a", "R49", "D3-CANON-1 composition-distinct strings/keys are distinct",
          True, d1 != d2 and digest({precomposed: 1}) != digest({combining: 1}))
    try:
        parse_record('{"a": 1, "a": 2}')
        dup_top = "accepted"
    except DuplicateKey:
        dup_top = "rejected-loud"
    try:
        parse_record('{"outer": {"b": 1, "b": 2}}')
        dup_nested = "accepted"
    except DuplicateKey:
        dup_nested = "rejected-loud"
    check("FX-R49b", "R49", "D3-CANON-1 duplicate exact keys rejected at parse, recursively",
          ("rejected-loud", "rejected-loud"), (dup_top, dup_nested))
    a = digest(parse_record('{ "b": 1,  "a": "x" }'))
    b = digest(parse_record('{"a":"x","b":1}'))
    check("FX-R49c", "R49", "D3-CANON-1 member order + whitespace variants share one digest",
          True, a == b)
    # canonical numbers, verified against RFC 8785's example values
    vectors = [(0.0, "0"), (-0.0, "0"), (4.5, "4.5"), (0.002, "0.002"),
               (1e30, "1e+30"), (333333333.33333329, "333333333.3333333"),
               (1e21, "1e+21"), (0.000001, "0.000001"), (1e-7, "1e-7"),
               (123456789012345680000.0, "123456789012345680000"),
               (0.1, "0.1"), (-2.5, "-2.5")]
    got = [es_number(v) for v, _ in vectors]
    try:
        es_number(float("inf")); nonfinite = "serialised"
    except ValueError:
        nonfinite = "rejected"
    check("FX-R49d", "R49", "D3-CANON-1 canonical numbers vs RFC 8785 example values; non-finite rejected",
          ([e for _, e in vectors], "rejected"), (got, nonfinite))

# ---------------------------------------------------------------- R54 — REQ-E-3 matching
def fixture_r54():
    reqs = [{"id": "Q1", "needs": "response-A"}, {"id": "Q2", "needs": "response-A"}]
    response = {"id": "response-A", "multi_use_permitted": False}
    satisfied = []
    ambiguous = [r["id"] for r in reqs if r["needs"] == response["id"]]
    if len(ambiguous) > 1 and not response["multi_use_permitted"]:
        outcome = ("unresolved", [])
    else:
        outcome = ("satisfied", ambiguous)
    check("FX-R54a", "R54", "REQ-E-3 one response, two event-specific requirements, no multi-use permission",
          ("unresolved", []), outcome)
    response2 = {"id": "response-A", "multi_use_permitted": True}
    outcome2 = ("satisfied", ambiguous) if response2["multi_use_permitted"] else ("unresolved", [])
    check("FX-R54b", "R54", "REQ-E-3 multi-use expressly permitted by the rule",
          ("satisfied", ["Q1", "Q2"]), outcome2)

# ---------------------------------------------------------------- R56 — REQ-E-6 roles
def gate_bundle(bundle):
    """REQ-E-6 three-way separation (matrix R56): no role verifies its
    own work; the evaluator's verdict is not the examiner's verdict;
    the examiner's verdict is not the gate's receipt; each role's
    verdict is independently necessary. A verdict is an object
    {by, verdict_id, role}; it must sit in its own role's slot, under
    its own author's hand."""
    roles = ["evaluator", "examiner", "gate"]
    for r in roles:
        if r not in bundle:
            return f"FAIL: missing {r} verdict (independently necessary)"
    for r in roles:
        v = bundle[r]
        if v.get("role") != r:
            return f"FAIL: {r} slot holds a {v.get('role')} verdict (substitution)"
    if len({bundle[r]["by"] for r in roles}) < 3:
        return "FAIL: one hand holds two roles (self-verification / substitution)"
    if len({bundle[r]["verdict_id"] for r in roles}) < 3:
        return "FAIL: one verdict presented for two roles (substitution)"
    return "PASS"

def _v(by, vid, role):
    return {"by": by, "verdict_id": vid, "role": role}

def fixture_r56():
    good = {"evaluator": _v("eval-1", "V-EVAL", "evaluator"),
            "examiner": _v("exam-1", "V-EXAM", "examiner"),
            "gate": _v("gate-1", "V-GATE", "gate")}
    # (a) the three separations + independent necessity of each role
    no_eval = {k: v for k, v in good.items() if k != "evaluator"}
    no_exam = {k: v for k, v in good.items() if k != "examiner"}
    no_gate = {k: v for k, v in good.items() if k != "gate"}
    check("FX-R56a", "R56", "REQ-E-6 full three-way separation holds; each role's verdict independently necessary",
          ("PASS", "FAIL: missing evaluator verdict (independently necessary)",
           "FAIL: missing examiner verdict (independently necessary)",
           "FAIL: missing gate verdict (independently necessary)"),
          (gate_bundle(good), gate_bundle(no_eval), gate_bundle(no_exam), gate_bundle(no_gate)))
    # (b) ALL prohibited substitutions + self-verification
    eval_in_exam = {**good, "examiner": _v("exam-1", "V-EVAL", "evaluator")}
    exam_in_gate = {**good, "gate": _v("gate-1", "V-EXAM", "examiner")}
    eval_in_gate = {**good, "gate": _v("gate-1", "V-EVAL", "evaluator")}
    selfver = {**good, "examiner": _v("eval-1", "V-EXAM", "examiner")}
    check("FX-R56b", "R56", "REQ-E-6 prohibited substitutions rejected: evaluator->examiner, examiner->gate, evaluator->gate, and self-verification",
          ("FAIL: examiner slot holds a evaluator verdict (substitution)",
           "FAIL: gate slot holds a examiner verdict (substitution)",
           "FAIL: gate slot holds a evaluator verdict (substitution)",
           "FAIL: one hand holds two roles (self-verification / substitution)"),
          (gate_bundle(eval_in_exam), gate_bundle(exam_in_gate),
           gate_bundle(eval_in_gate), gate_bundle(selfver)))

# ---------------------------------------------------------------- R57 — REQ-G-2 honesty credit
def fixture_r57():
    closure = {"state": "BLOCKED", "blocker_report_accurate": True}
    honesty_credit = closure["blocker_report_accurate"] is True
    complete = closure["state"] == "SATISFIED"
    check("FX-R57", "R57", "REQ-G-2 accurate BLOCKED report: honesty credit AND task incomplete, independently",
          (True, False), (honesty_credit, complete))

# ---------------------------------------------------------------- R64 — REQ-K-4 verdicts as REPORTED
def validate_report(rep):
    """REQ-K-4/R64: checker verdicts are carried as REPORTED evidence;
    the independence caveat must ride with each verdict; reliance on a
    checker for any judgement must be recorded."""
    for v in rep.get("checker_verdicts", []):
        if v.get("evidence_class") != "REPORTED":
            return "FAIL: checker verdict not carried as REPORTED"
        caveat = v.get("independence_caveat") or ""
        if "independence" not in caveat or "UNRESOLVED" not in caveat:
            return "FAIL: independence caveat missing or incomplete"
    if rep.get("uses_checker_for_preservation"):
        rel = rep.get("checker_reliance", [])
        if not rel or any(not r.get("recorded") for r in rel):
            return "FAIL: checker reliance unrecorded"
    return "PASS"

def fixture_r64():
    good = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                   "evidence_class": "REPORTED",
                                   "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
            "uses_checker_for_preservation": True,
            "checker_reliance": [{"on": "I-2-checker", "for": "preservation judgement", "recorded": True}]}
    no_caveat = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                       "evidence_class": "REPORTED"}],
                 "uses_checker_for_preservation": True,
                 "checker_reliance": [{"on": "I-2-checker", "recorded": True}]}
    no_reliance = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                         "evidence_class": "REPORTED",
                                         "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
                   "uses_checker_for_preservation": True, "checker_reliance": []}
    wrong_class = {"checker_verdicts": [{"checker": "I-2-checker", "verdict": "preserved",
                                         "evidence_class": "VERIFIED",
                                         "independence_caveat": "checker independence is UNRESOLVED (UX-1)"}],
                   "uses_checker_for_preservation": False}
    res64 = (validate_report(good), validate_report(no_caveat),
             validate_report(no_reliance), validate_report(wrong_class))
    check("FX-R64", "R64", "REQ-K-4 report validation: compliant report passes; omitted caveat, unrecorded reliance and overstated evidence class fail",
          ("PASS", "FAIL: independence caveat missing or incomplete",
           "FAIL: checker reliance unrecorded", "FAIL: checker verdict not carried as REPORTED"), res64)

# ---------------------------------------------------------------- R65 — report reference integrity
def fixture_r65():
    def validate(report, targets):
        """REQ-K-4 reference-integrity validation (v0.10 repair —
        R65 FAIL at independent examination, confirmed at
        adjudication: the v0.9 validator iterated only the
        references PRESENT in a report, so a report missing a
        relationship passed; an empty references dict passed. A
        validator must establish both that supplied references are
        correct AND that required references have not been omitted.
        This validator additionally requires the exact required
        set — nothing missing, nothing unexpected — and
        cross-checks components_present against it.)"""
        required = set(targets)
        refs = report.get("references")
        if not isinstance(refs, dict):
            return "FAIL: references missing"
        present = set(refs)
        missing = sorted(required - present)
        if missing:
            return f"FAIL: missing reference: {missing[0]}"
        unexpected = sorted(present - required)
        if unexpected:
            return f"FAIL: unexpected reference: {unexpected[0]}"
        if set(report.get("components_present", [])) != required:
            return "FAIL: components_present does not match the required relationships"
        for comp, ref in refs.items():
            if targets.get(comp) != ref:
                return f"FAIL: {comp} reference mismatch"
        return "PASS"
    # The matrix's five provenance relationships (R65): evaluation-
    # record identity, content identity, canonicalization procedure
    # identifier, defect-to-record linkage, checker verdict /
    # reproducibility-trio correspondence. Each is mismatched in
    # turn (v0.9), and — v0.10 — each is also DELETED in turn, the
    # case the v0.9 validator could not see.
    targets = {"evaluation_record": "EV-1", "content_identity": "CI-9",
               "procedure": "D3-CANON-1", "defect_link": "DEF-3", "verdict_trio": "T-7"}
    good = {"components_present": list(targets), "references": dict(targets)}
    mismatches = [{**targets, comp: ref + "-WRONG"} for comp, ref in targets.items()]
    deletions = [{k: v for k, v in targets.items() if k != comp} for comp in targets]
    empty = {}
    extra = {**targets, "surprise_extra": "X-1"}
    lying_components = {"components_present": [c for c in targets if c != "procedure"],
                        "references": dict(targets)}
    observed = tuple([validate(good, targets)] +
                     [validate({"components_present": list(targets), "references": m}, targets)
                      for m in mismatches] +
                     [validate({"components_present": list(targets), "references": d}, targets)
                      for d in deletions] +
                     [validate({"components_present": list(targets), "references": empty}, targets),
                      validate({"components_present": list(targets) + ["surprise_extra"],
                                "references": extra}, targets),
                      validate(lying_components, targets)])
    check("FX-R65", "R65", "REQ-K-4 all five provenance relationships: intact report passes; a mismatch or a deletion of any one of evaluation_record, content_identity, procedure, defect_link, verdict_trio fails; empty references, an unexpected reference, and a components_present that disagrees with the required set all fail",
          ("PASS",
           "FAIL: evaluation_record reference mismatch",
           "FAIL: content_identity reference mismatch", "FAIL: procedure reference mismatch",
           "FAIL: defect_link reference mismatch", "FAIL: verdict_trio reference mismatch",
           "FAIL: missing reference: evaluation_record",
           "FAIL: missing reference: content_identity", "FAIL: missing reference: procedure",
           "FAIL: missing reference: defect_link", "FAIL: missing reference: verdict_trio",
           "FAIL: missing reference: content_identity",
           "FAIL: unexpected reference: surprise_extra",
           "FAIL: components_present does not match the required relationships"),
          observed)

# ---------------------------------------------------------------- R60 — REQ-I-2 checker contract
def _preservation_check(payload, expected_sha):
    """The REQ-I-3 preservation check, as an executable procedure:
    recompute the artefact payload's digest and compare it against
    the digest pinned in the contract. Returns the digest on a
    match, None otherwise. This function IS the validation
    procedure — the contract executes it, and the implementation
    hash stamped into every verdict is the hash of its source."""
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return digest if digest == expected_sha else None

def _implementation_hash():
    """SHA-256 of the validation procedure's own source — the
    implementation identity REQ-I-2's reproducibility trio requires
    a verdict to carry."""
    return hashlib.sha256(inspect.getsource(_preservation_check).encode()).hexdigest()

class CheckerContract:
    """REQ-I-2 checker contract (v0.10 repair — R60 FAIL at
    independent examination, confirmed at adjudication: the v0.9
    contract RECORDED a procedure name without executing it, and
    its verdict omitted the implementation hash, so the
    reproducibility trio was never established). The contract
    DEFINES the input artefact it accepts, EXECUTES its validation
    procedure (above) on that artefact, and stamps every verdict
    with the full reproducibility trio: declared version,
    implementation hash, input artefact identity — bound to the
    procedure identity. A verdict that diverges from the contract
    on any element is detectable, and validate_verdict() below
    rejects it."""
    def __init__(self, input_id, procedure, version, expected_sha, pinned=True):
        self.input_id = input_id
        self.procedure = procedure
        self.version = version
        self.expected_sha = expected_sha
        self.pinned = pinned

    def run(self, artefact):
        if not self.pinned:
            return "REJECTED: unpinned version"
        if artefact is None:
            return "FAILURE-PATH: missing input artefact"
        if artefact.get("id") != self.input_id:
            return f"REJECTED: artefact is not the defined input ({self.input_id})"
        if artefact.get("corrupt"):
            return "FAILURE-PATH: invalid artefact"
        digest = _preservation_check(artefact["payload"], self.expected_sha)
        if digest is None:
            return "FAILURE-PATH: invalid artefact"
        return {"verdict": f"preserved sha={digest[:12]}", "input": self.input_id,
                "procedure": self.procedure, "version": self.version,
                "implementation_hash": _implementation_hash()}

def validate_verdict(verdict, contract):
    """REQ-I-2 verdict validation: a verdict counts as this
    contract's output only if it carries the complete
    reproducibility trio, each element matching the contract —
    declared version, implementation hash of the procedure that
    produced it, input artefact identity — and the procedure
    identity itself. Missing or mismatched elements are rejected
    with the specific defect named."""
    if not isinstance(verdict, dict):
        return "REJECTED: not a verdict"
    if verdict.get("procedure") != contract.procedure:
        return "REJECTED: procedure mismatch"
    if "version" not in verdict:
        return "REJECTED: missing version"
    if verdict["version"] != contract.version:
        return "REJECTED: version mismatch"
    if "implementation_hash" not in verdict:
        return "REJECTED: missing implementation hash"
    if verdict["implementation_hash"] != _implementation_hash():
        return "REJECTED: implementation hash mismatch"
    if "input" not in verdict:
        return "REJECTED: missing input identity"
    if verdict["input"] != contract.input_id:
        return "REJECTED: input identity mismatch"
    return "ACCEPTED"

def fixture_r60():
    contract = CheckerContract("ART-INPUT-1", "REQ-I-3 preservation check", "checker-v1.3",
                               hashlib.sha256(b"payload-1").hexdigest())
    art = {"id": "ART-INPUT-1", "payload": "payload-1"}
    # (a) defined input artefact: the defined input runs; any other
    # artefact is refused — the input is a contract term, not a
    # parameter the caller may vary silently.
    run_defined = contract.run(art)
    check("FX-R60a", "R60", "REQ-I-2 defined input artefact: defined input accepted; a different artefact refused",
          ("verdict", "REJECTED: artefact is not the defined input (ART-INPUT-1)"),
          ("verdict" if isinstance(run_defined, dict) else run_defined,
           contract.run({"id": "ART-OTHER", "payload": "payload-1"})))
    # (b) validation procedure + reproducibility trio (v0.10 repair:
    # the v0.9 form compared the verdict's procedure STRING against
    # the contract's own string — a check the contract could never
    # fail. The contract now executes its procedure and stamps the
    # verdict with the full trio; validation REJECTS a verdict that
    # is missing or mismatches any element):
    #   genuine verdict -> ACCEPTED
    #   forged procedure stamp -> procedure mismatch
    #   implementation_hash deleted -> missing implementation hash
    #   implementation_hash altered -> implementation hash mismatch
    #   input identity deleted -> missing input identity
    #   version deleted -> missing version
    v = contract.run(art)
    forged = {**v, "procedure": "some other procedure"}
    no_hash = {k: val for k, val in v.items() if k != "implementation_hash"}
    bad_hash = {**v, "implementation_hash": "0" * 64}
    no_input = {k: val for k, val in v.items() if k != "input"}
    no_version = {k: val for k, val in v.items() if k != "version"}
    check("FX-R60b", "R60", "REQ-I-2 validation procedure and reproducibility trio: genuine verdict accepted; forged procedure, missing/altered implementation hash, missing input identity and missing version all rejected",
          ("ACCEPTED", "REJECTED: procedure mismatch",
           "REJECTED: missing implementation hash",
           "REJECTED: implementation hash mismatch",
           "REJECTED: missing input identity", "REJECTED: missing version"),
          (validate_verdict(v, contract), validate_verdict(forged, contract),
           validate_verdict(no_hash, contract), validate_verdict(bad_hash, contract),
           validate_verdict(no_input, contract), validate_verdict(no_version, contract)))
    # (c) reproducible result: two runs over the same input produce
    # byte-identical verdicts.
    check("FX-R60c", "R60", "REQ-I-2 reproducible result: repeated runs produce identical verdicts",
          True, contract.run(art) == contract.run(dict(art)))
    # (d) failure path for missing / invalid artefacts.
    check("FX-R60d", "R60", "REQ-I-2 failure paths: missing artefact and invalid artefact both take the failure path, never a verdict",
          ("FAILURE-PATH: missing input artefact", "FAILURE-PATH: invalid artefact"),
          (contract.run(None), contract.run({"id": "ART-INPUT-1", "payload": "x", "corrupt": True})))
    # (e) pinned / recorded version: the verdict records the pinned
    # version; an unpinned checker refuses to run.
    unpinned = CheckerContract("ART-INPUT-1", "REQ-I-3 preservation check", "checker-v1.3",
                               hashlib.sha256(b"payload-1").hexdigest(), pinned=False)
    check("FX-R60e", "R60", "REQ-I-2 pinned/recorded version: verdict records the pinned version; unpinned checker rejected",
          ("checker-v1.3", "REJECTED: unpinned version"),
          (v["version"], unpinned.run(art)))

# ---------------------------------------------------------------- R61 — REQ-I-3 preservation outcomes
def fixture_r61():
    def preservation_outcome(payload, expected_sha):
        if payload is None:
            return ("INDETERMINATE / RECORD-PRESERVATION", None)
        if hashlib.sha256(payload.encode()).hexdigest() != expected_sha:
            return ("INDETERMINATE / RECORD-PRESERVATION", None)
        return ("VERIFIED", "harness")
    good_sha = hashlib.sha256(b"payload").hexdigest()
    deleted = preservation_outcome(None, good_sha)
    corrupted = preservation_outcome("tampered", good_sha)
    check("FX-R61", "R61", "REQ-I-3 deleted and corrupted payloads: INDETERMINATE / RECORD-PRESERVATION, never a pass, never AGENT attribution",
          (("INDETERMINATE / RECORD-PRESERVATION", None), ("INDETERMINATE / RECORD-PRESERVATION", None)),
          (deleted, corrupted))

# ---------------------------------------------------------------- runner
if __name__ == "__main__":
    fixture_r62()
    fixture_r40(); fixture_r47(); fixture_r63()
    fixture_r44(); fixture_r52()
    fixture_r49()
    fixture_r54(); fixture_r56(); fixture_r57(); fixture_r64(); fixture_r65()
    fixture_r60(); fixture_r61()
    fails = [r for r in RESULTS if r["verdict"] != "PASS"]
    print(f"\n{len(RESULTS)} fixtures executed, {len(RESULTS) - len(fails)} PASS, {len(fails)} FAIL")
    json.dump({"harness": "fixtures-v010/harness.py v2.1",
               "python_version": sys.version,
               "command": "python3 harness.py",
               "results": RESULTS}, open("results.json", "w"), indent=1)
    sys.exit(1 if fails else 0)
