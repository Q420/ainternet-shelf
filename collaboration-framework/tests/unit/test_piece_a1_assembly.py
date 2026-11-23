"""Piece A1 tests — assembly and identity (agent layer; SPEC
SHEET Rev 6, R37–R40, R55's assembly part), against the passed
scope PIECE-A1-SCOPE-2026-11-23.md (Rev 3) and its acceptance
sketch: the normative sequence with attribution; out-of-order
refusals recorded; the credential invariant (prepared →
refused → active only on authorised activation, failing closed
exactly); activation refused without a grants section; two
instances of one role and model fully distinct; identity
evidence kinds distinct, a provider id never raising status;
a second assembly for the same slot through the full sequence;
a stale judgement refused at pack; preflight leaving no
orphaned onboarding; and the checker's assembly correspondence
— hash correspondence, one-to-one, incomplete histories
rejected.

Run: PYTHONPATH=src python3 tests/unit/test_piece_a1_assembly.py
Exits 0 when every check passes.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from framework import gates as _gates  # noqa: E402
from framework import onboarding as ob  # noqa: E402
from framework import projection  # noqa: E402
from framework.doorway import Doorway, DoorwayRefusal  # noqa: E402
from framework.generator import Generator  # noqa: E402
from framework.office import Office  # noqa: E402
from framework.record import (CONSTITUTION_HASH, FrameworkStore,  # noqa: E402
                              assembly_record_hash,
                              declaration_fingerprint,
                              instance_credential_fingerprint)

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
PROVIDER_ID = "example/model-4.2"
SKILLS = [{"name": "drafting", "version": "1.2.0"},
          {"name": "checking", "version": "0.9.1"}]
GRANTS = [{"tool": "shelf.read", "scope_ceiling": "case evidence",
           "side_effect_class": "read", "bound": {"count": 10},
           "authority_trace": "commission brief, crew seat"}]
FULL = {"part": "part-A", "assignment": "Draft the A section",
        "verification_list": ["check the figures"]}

LIFECYCLE = ["ASSEMBLY_PROPOSED", "ONBOARDING", "ASSEMBLY_GENERATED",
             "ASSEMBLY_VERIFIED", "ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
             "ASSEMBLY_ISSUE_AUTHORISED", "INSTANCE_ACTIVATED"]


def identify():
    """The adapter's identify() shape (Piece 8, A5): two
    attributed claims, no verdict."""
    return {"declaration": DECL, "provider_model_id": PROVIDER_ID}


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
            "crew-2": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(FULL), "crew-2": dict(FULL)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def issue_case(d, office, tok, seat):
    """The Piece 5 route: office verification, the examiner's
    judgement, the orchestrator's authorisation."""
    r = office.issue_new(tok["orch-1"], seat)
    assert r["ok"], r
    d.act(tok["exam-1"], "CASE_JUDGED",
          {"case_id": f"case-{seat}", "version": 1},
          view_seq=d.store.head_seq())
    office.authorise(tok["orch-1"], f"case-{seat}", 1)


def refused(fn):
    """Run an act expected to be refused; return True when the
    doorway refused it (the refusal itself is asserted recorded
    by the callers that count events)."""
    try:
        fn()
    except DoorwayRefusal:
        return True
    return False


def lifecycle_events(store, assembly_id=None):
    evs = store.all_events()
    proposal_seq = None
    if assembly_id is not None:
        # A proposal carries no assembly id (ids are allocated
        # at generation); it belongs to the assembly whose
        # GENERATED record answers it, by proposal_seq.
        for ev in evs:
            if ev["type"] == "ASSEMBLY_GENERATED" and \
                    ev["payload"].get("assembly_id") == assembly_id:
                proposal_seq = ev["payload"].get("proposal_seq")
    out = []
    for ev in evs:
        if ev["type"] not in LIFECYCLE:
            continue
        if ev["type"] == "ONBOARDING" and \
                ev["payload"].get("subject") != "instance":
            continue
        if assembly_id is not None:
            if ev["type"] == "ASSEMBLY_PROPOSED":
                if ev["event_seq"] != proposal_seq:
                    continue
            elif ev["payload"].get("assembly_id") != assembly_id:
                continue
        out.append(ev)
    return out


def run_to_packed(store, d, gen, tok, seat="crew-1", grants=GRANTS):
    gen.propose(tok["orch-1"], seat, part="part-A",
                role_requirements="a careful drafting model")
    r = gen.generate(tok["orch-1"], seat, identify, skills=SKILLS,
                     grants=grants)
    assert r["ok"], r
    gen.verify(tok["orch-1"], r["assembly_id"])
    d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
          gen.judgement(r["assembly_id"]),
          view_seq=store.head_seq())
    packed = gen.pack(tok["orch-1"], r["assembly_id"])
    return r, packed


# -- T1: the happy path — sequence, attribution, hash chain of
# the judged/sealed object.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
gen.authorise(tok["orch-1"], r["assembly_id"])
gen.activate(tok["orch-1"], r["assembly_id"])
evs = lifecycle_events(store, r["assembly_id"])
check("T1 the eight acts land in the normative sequence",
      [e["type"] for e in evs] == LIFECYCLE,
      str([e["type"] for e in evs]))
actors = {e["type"]: e["actor"] for e in evs}
check("T1 attribution: office/orchestrator acts under orch-1, "
      "the judgement the examiner's own",
      actors["ASSEMBLY_PROPOSED"] == "orch-1"
      and actors["ONBOARDING"] == "orch-1"
      and actors["ASSEMBLY_GENERATED"] == "orch-1"
      and actors["ASSEMBLY_VERIFIED"] == "orch-1"
      and actors["ASSEMBLY_JUDGED"] == "exam-1"
      and actors["ASSEMBLY_PACKED"] == "orch-1"
      and actors["ASSEMBLY_ISSUE_AUTHORISED"] == "orch-1"
      and actors["INSTANCE_ACTIVATED"] == "orch-1")
entry = d.state()["assemblies"][r["assembly_id"]]
seqs = [entry[k] for k in ("generated_seq", "verified_seq",
                           "judged_seq", "packed_seq",
                           "authorised_seq", "activated_seq")]
check("T1 the fold's stage positions stand in order",
      all(s is not None for s in seqs) and seqs == sorted(seqs))
generated = next(e for e in evs if e["type"] == "ASSEMBLY_GENERATED")
judged = next(e for e in evs if e["type"] == "ASSEMBLY_JUDGED")
packed_ev = next(e for e in evs if e["type"] == "ASSEMBLY_PACKED")
check("T1 generation, judgement and pack name one object, by hash",
      r["record_hash"] == assembly_record_hash(generated["payload"])
      and judged["payload"]["record_hash"] == r["record_hash"]
      and packed_ev["payload"]["record_hash"] == r["record_hash"]
      and entry["judged_hash"] == entry["pack_hash"]
      == r["record_hash"])
check("T1 the generated record binds the exact onboarding event",
      generated["payload"]["onboarding_seq"]
      == r["onboarding_seq"]
      and generated["payload"]["proposal_seq"]
      == evs[0]["event_seq"])
check("T1 identity claims live only in the onboarding event",
      "declaration" not in generated["payload"]
      and "provider_model_id" not in generated["payload"])

# -- T2: the credential state machine, derived from the record.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r = gen.generate(tok["orch-1"], "crew-1", identify, skills=SKILLS,
                 grants=GRANTS)
check("T2 no credential before pack",
      d.instance_credential_state(r["instance_id"]) == "none")
gen.verify(tok["orch-1"], r["assembly_id"])
d.act(tok["exam-1"], "ASSEMBLY_JUDGED", gen.judgement(r["assembly_id"]),
      view_seq=store.head_seq())
packed = gen.pack(tok["orch-1"], r["assembly_id"])
check("T2 prepared at pack",
      d.instance_credential_state(r["instance_id"]) == "prepared")
gen.authorise(tok["orch-1"], r["assembly_id"])
check("T2 authorisation alone does not activate",
      d.instance_credential_state(r["instance_id"]) == "prepared")
gen.activate(tok["orch-1"], r["assembly_id"])
check("T2 active only at activation",
      d.instance_credential_state(r["instance_id"]) == "active")

# -- T3: a prepared credential is refused at authentication —
# recorded, on the credential invariant — and the same
# credential works after authorised activation.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
itok = packed["instance_token"]
before = len(store.all_events())
check("T3 the prepared credential does not authenticate",
      refused(lambda: d.act(
          itok, "COMMENT", {"on_job": True, "text": "early"},
          view_seq=store.head_seq())))
evs = store.all_events()
check("T3 the refusal is recorded, naming the slot and the ground",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION"
      and evs[-1]["payload"].get("seat") == "crew-1"
      and "prepared" in evs[-1]["payload"].get("ground", "")
      and "R39" in evs[-1]["payload"].get("ground", ""))
gen.authorise(tok["orch-1"], r["assembly_id"])
gen.activate(tok["orch-1"], r["assembly_id"])
ev = d.act(itok, "COMMENT", {"on_job": True, "text": "ready"},
           view_seq=store.head_seq())
check("T3 the same credential works after activation, as the "
      "slot's occupant", ev["actor"] == "crew-1")

# -- T4: out-of-order acts are refused, each refusal recorded,
# and the lifecycle still completes in order afterwards.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
check("T4 verify of an unknown assembly refused",
      refused(lambda: gen.verify(tok["orch-1"], "assembly-nope")))
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r = gen.generate(tok["orch-1"], "crew-1", identify, skills=SKILLS,
                 grants=GRANTS)
aid = r["assembly_id"]
head = store.head_seq()
check("T4 judgement before verification refused + recorded",
      refused(lambda: d.act(tok["exam-1"], "ASSEMBLY_JUDGED",
                            gen.judgement(aid),
                            view_seq=store.head_seq()))
      and len(store.all_events()) == head + 1
      and store.all_events()[-1]["type"] == "REJECTION")
check("T4 pack before judgement refused",
      refused(lambda: gen.pack(tok["orch-1"], aid)))
check("T4 authorisation before pack refused",
      refused(lambda: gen.authorise(tok["orch-1"], aid)))
gen.verify(tok["orch-1"], aid)
d.act(tok["exam-1"], "ASSEMBLY_JUDGED", gen.judgement(aid),
      view_seq=store.head_seq())
packed = gen.pack(tok["orch-1"], aid)
check("T4 activation before authorisation refused",
      refused(lambda: gen.activate(tok["orch-1"], aid)))
gen.authorise(tok["orch-1"], aid)
gen.activate(tok["orch-1"], aid)
check("T4 the lifecycle completes in order after the refusals",
      d.instance_credential_state(r["instance_id"]) == "active"
      and [e["type"] for e in lifecycle_events(store, aid)]
      == LIFECYCLE)

# -- T5: activation without authorisation fails closed, exactly:
# no activation event, no transition, one recorded refusal, the
# credential still prepared and unusable.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
before = len(store.all_events())
check("T5 activation without authorisation refused",
      refused(lambda: gen.activate(tok["orch-1"], r["assembly_id"])))
evs = store.all_events()
check("T5 exactly one REJECTION appended, no ACTIVATED event",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION"
      and not any(e["type"] == "INSTANCE_ACTIVATED" for e in evs))
check("T5 the credential remains prepared and unusable",
      d.instance_credential_state(r["instance_id"]) == "prepared"
      and refused(lambda: d.act(
          packed["instance_token"], "COMMENT", {"on_job": True},
          view_seq=store.head_seq())))

# -- T6: activation is refused where the record lacks a grants
# section — everything before it may stand.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok, grants=None)
entry = d.state()["assemblies"][r["assembly_id"]]
check("T6 a grants-less record generates, judges and packs",
      entry["grants_present"] is False
      and entry["packed_seq"] is not None)
gen.authorise(tok["orch-1"], r["assembly_id"])
before = len(store.all_events())
check("T6 activation refused without a grants section",
      refused(lambda: gen.activate(tok["orch-1"], r["assembly_id"])))
evs = store.all_events()
check("T6 refusal recorded on the grants ground; still prepared",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION"
      and "grants" in evs[-1]["payload"].get("ground", "")
      and d.instance_credential_state(r["instance_id"])
      == "prepared")

# -- T7: two instances, same slot, same model — fully distinct.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r1, packed1 = run_to_packed(store, d, gen, tok)
gen.authorise(tok["orch-1"], r1["assembly_id"])
gen.activate(tok["orch-1"], r1["assembly_id"])
r2, packed2 = run_to_packed(store, d, gen, tok)
check("T7 distinct assemblies and instances",
      r1["assembly_id"] != r2["assembly_id"]
      and r1["instance_id"] != r2["instance_id"])
check("T7 distinct onboarding records, both standing",
      ob.instance_onboarding_record(d, r1["instance_id"])[
          "onboarded_seq"]
      != ob.instance_onboarding_record(d, r2["instance_id"])[
          "onboarded_seq"])
check("T7 distinct credentials",
      packed1["instance_token"] != packed2["instance_token"])
check("T7 the second's preparation does not touch the first",
      d.instance_credential_state(r1["instance_id"]) == "active"
      and d.instance_credential_state(r2["instance_id"])
      == "prepared")
ev = d.act(packed1["instance_token"], "COMMENT",
           {"on_job": True, "text": "first still works"},
           view_seq=store.head_seq())
check("T7 the first instance's credential still authenticates",
      ev["actor"] == "crew-1")
check("T7 the second's prepared credential does not",
      refused(lambda: d.act(
          packed2["instance_token"], "COMMENT", {"on_job": True},
          view_seq=store.head_seq())))
gen.authorise(tok["orch-1"], r2["assembly_id"])
gen.activate(tok["orch-1"], r2["assembly_id"])
ev = d.act(packed2["instance_token"], "COMMENT",
           {"on_job": True, "text": "second now works"},
           view_seq=store.head_seq())
check("T7 the second activates on its own authorisation",
      ev["actor"] == "crew-1")

# -- T8: identity evidence kinds stay distinct; a provider id
# never raises status; the seat world is untouched.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
rec = ob.instance_onboarding_record(d, r["instance_id"])
check("T8 declaration verbatim in the instance record",
      rec["declaration"] == DECL)
check("T8 provider id recorded as its own claim, status declared",
      rec["provider_model_id"] == PROVIDER_ID
      and rec["identity_status"] == "declared")
check("T8 the instance record lives beside the seat state",
      "crew-1" not in d.state()["onboarding"]
      and rec["seat"] == "crew-1"
      and rec["assembly_id"] == r["assembly_id"])
check("T8 provider-confirmed without attestation refused "
      "on the instance path too",
      refused(lambda: ob.onboard_instance(
          d, tok["orch-1"], "crew-1", "inst-crew-1-99",
          "assembly-crew-1-99", DECL,
          identity_status="provider-confirmed")))

# -- T9: the second assembly for the slot runs the full
# sequence — no act skippable (slot refill, not continuation).
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r1, packed1 = run_to_packed(store, d, gen, tok)
gen.authorise(tok["orch-1"], r1["assembly_id"])
gen.activate(tok["orch-1"], r1["assembly_id"])
r2, packed2 = run_to_packed(store, d, gen, tok)
gen.authorise(tok["orch-1"], r2["assembly_id"])
gen.activate(tok["orch-1"], r2["assembly_id"])
e2 = d.state()["assemblies"][r2["assembly_id"]]
seqs2 = [e2[k] for k in ("generated_seq", "verified_seq",
                         "judged_seq", "packed_seq",
                         "authorised_seq", "activated_seq")]
check("T9 the refill assembly stands complete, in order",
      all(s is not None for s in seqs2) and seqs2 == sorted(seqs2)
      and [e["type"] for e in lifecycle_events(
          store, r2["assembly_id"])] == LIFECYCLE)
check("T9 both assemblies stand in the fold",
      len(d.state()["assemblies"]) == 2)

# -- T10: the judgement binds the sealed object — a wrong hash
# is refused at judgement and at pack; a changed assembly is a
# new assembly and inherits no judgement.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r = gen.generate(tok["orch-1"], "crew-1", identify, skills=SKILLS,
                 grants=GRANTS)
gen.verify(tok["orch-1"], r["assembly_id"])
bad = dict(gen.judgement(r["assembly_id"]))
bad["record_hash"] = "0" * 64
check("T10 a judgement naming the wrong object refused",
      refused(lambda: d.act(tok["exam-1"], "ASSEMBLY_JUDGED", bad,
                            view_seq=store.head_seq()))
      and not any(e["type"] == "ASSEMBLY_JUDGED"
                  for e in store.all_events()))
d.act(tok["exam-1"], "ASSEMBLY_JUDGED", gen.judgement(r["assembly_id"]),
      view_seq=store.head_seq())
entry = d.state()["assemblies"][r["assembly_id"]]
fp = instance_credential_fingerprint(
    r["instance_id"], DECL, entry["case_id"], entry["case_version"])
forged = {"assembly_id": r["assembly_id"],
          "instance_id": r["instance_id"],
          "record_hash": "0" * 64, "credential_fingerprint": fp}
check("T10 a pack naming a different object than the judgement "
      "refused (stale judgement seals nothing)",
      refused(lambda: d.act(tok["orch-1"], "ASSEMBLY_PACKED", forged,
                            view_seq=store.head_seq()))
      and d.instance_credential_state(r["instance_id"]) == "none")
packed = gen.pack(tok["orch-1"], r["assembly_id"])
check("T10 the true pack seals the judged object",
      d.state()["assemblies"][r["assembly_id"]]["pack_hash"]
      == r["record_hash"])
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r2 = gen.generate(tok["orch-1"], "crew-1", identify, skills=SKILLS,
                  grants=[{"tool": "shelf.write",
                           "scope_ceiling": "one artifact",
                           "side_effect_class": "write",
                           "bound": {"count": 1},
                           "authority_trace": "commission brief"}])
check("T10 the changed assembly is a new assembly, unjudged",
      r2["ok"] and r2["instance_id"] != r["instance_id"]
      and d.state()["assemblies"][r2["assembly_id"]]["judged_seq"]
      is None)
gen.verify(tok["orch-1"], r2["assembly_id"])
check("T10 the new assembly cannot pack on the old judgement",
      refused(lambda: gen.pack(tok["orch-1"], r2["assembly_id"])))

# -- T11: preflight completes before onboarding — a failed
# generation records nothing at all.
store, d, office, gen, tok = fresh()
gen.propose(tok["orch-1"], "crew-2", part="part-A",
            role_requirements="a careful drafting model")
head = store.head_seq()
r = gen.generate(tok["orch-1"], "crew-2", identify, skills=SKILLS,
                 grants=GRANTS)
check("T11 generation without an issued case fails preflight",
      r["ok"] is False and "case" in " ".join(r["problems"]))
check("T11 nothing recorded: no orphaned onboarding, no generation",
      store.head_seq() == head
      and d.state()["instance_onboarding"] == {}
      and d.state()["assemblies"] == {})
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
head = store.head_seq()
r = gen.generate(tok["orch-1"], "crew-1",
                 {"declaration": "", "provider_model_id": None},
                 skills=SKILLS, grants=GRANTS)
check("T11 an empty declaration fails preflight, nothing recorded",
      r["ok"] is False and store.head_seq() == head
      and d.state()["instance_onboarding"] == {})

# -- T12: the checker — the happy path verifies whole, and
# broken assembly histories are reported, never read as valid.
def quiesce(store):
    store._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def run_checker(store):
    quiesce(store)
    req = {"store_path": store.path, "run_id": "run-1",
           "snapshot": projection.snapshot(store)}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=SRC)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "checker"],
        input=json.dumps(req), capture_output=True, text=True,
        env=env, cwd=ROOT)
    return json.loads(proc.stdout)


store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
gen.authorise(tok["orch-1"], r["assembly_id"])
gen.activate(tok["orch-1"], r["assembly_id"])
verdict = run_checker(store)
c = verdict["checks"]
check("T12 the checker verifies the whole happy-path record",
      all(c[k]["result"] == "ok" for k in (
          "run_binding", "chain_hash", "chain_sequence", "replay",
          "projection_schema", "snapshot_schema", "replay_equality",
          "seal_correspondence", "assembly_correspondence")),
      json.dumps(c))

# (a) activation standing without its authorisation — an
# incomplete history, appended past the doorway.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
store.append("INSTANCE_ACTIVATED", "orch-1", [], {
    "assembly_id": r["assembly_id"],
    "instance_id": r["instance_id"]})
store.commit()
verdict = run_checker(store)
ac = verdict["checks"]["assembly_correspondence"]
check("T12 an activation without authorisation is reported",
      ac["result"] == "divergent"
      and any(p["kind"] == "assembly_stage_missing"
              for p in ac["problems"]), json.dumps(ac))

# (b) a generated record bound to no instance onboarding.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
r, packed = run_to_packed(store, d, gen, tok)
real = next(e for e in store.all_events()
            if e["type"] == "ASSEMBLY_GENERATED")
forged = dict(real["payload"])
forged["assembly_id"] = "assembly-crew-1-77"
forged["instance_id"] = "inst-crew-1-77"
forged["onboarding_seq"] = 1  # the commission, not an onboarding
store.append("ASSEMBLY_GENERATED", "orch-1", [], forged)
store.commit()
verdict = run_checker(store)
ac = verdict["checks"]["assembly_correspondence"]
check("T12 a generation bound to no onboarding is reported",
      ac["result"] == "divergent"
      and any(p["kind"] == "generated_onboarding_binding_broken"
              for p in ac["problems"]), json.dumps(ac))

# (c) a pack sealing a different object than the generated one.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
r = gen.generate(tok["orch-1"], "crew-1", identify, skills=SKILLS,
                 grants=GRANTS)
gen.verify(tok["orch-1"], r["assembly_id"])
d.act(tok["exam-1"], "ASSEMBLY_JUDGED", gen.judgement(r["assembly_id"]),
      view_seq=store.head_seq())
store.append("ASSEMBLY_PACKED", "orch-1", [], {
    "assembly_id": r["assembly_id"],
    "instance_id": r["instance_id"],
    "record_hash": "f" * 64, "credential_fingerprint": "0" * 64})
store.commit()
verdict = run_checker(store)
ac = verdict["checks"]["assembly_correspondence"]
check("T12 a pack sealing a different object is reported",
      ac["result"] == "divergent"
      and any(p["kind"] == "assembly_hash_mismatch"
              and p["type"] == "ASSEMBLY_PACKED"
              for p in ac["problems"]), json.dumps(ac))

# -- T13: correction round 1 (Vane's examination of the build)
# — the proposal discriminator and the case/part
# correspondence. ASSEMBLY_PROPOSED is a shared event kind: a
# §3.8 run-level proposal and an A1 instance proposal must
# never be mistaken for one another, in either fold, in the
# gate derivations, or at the doorway; and an assembly's part
# must be the part its bound case covers, at preflight and at
# the doorway alike.
CREW5 = [{"seat": s, "role": r} for s, r in (
    ("orch-1", "orchestrator"), ("exam-1", "examiner"),
    ("dir-1", "director"), ("crew-1", "crew"),
    ("crew-2", "crew"))]
GATES_A1 = {"assembly": "assembly", "completion": "completion",
            "part-B": "judgement"}


def run_proposal(d, store, tok):
    """A §3.8 run-level proposal, recorded as the orchestrator
    piece records it: the commission references and the full
    crew, no discriminator — absence is run-level."""
    cs = d.state()["commission_seq"]
    return d.act(tok["orch-1"], "ASSEMBLY_PROPOSED", {
        "commission_seq": cs, "tree_ref": cs, "gates_ref": cs,
        "crew": [dict(c) for c in CREW5]},
        view_seq=store.head_seq())


def run_record(d, store, tok, proposal_seq, gate_set):
    """The examiner's §3.8 assembly record, bound to a
    run-level proposal (no seat onboarding stands in these
    worlds, so every derived status is unverified)."""
    return d.act(tok["exam-1"], "ASSEMBLY_RECORD", {
        "proposal_seq": proposal_seq,
        "criteria_mapping": {"part-A": "criterion-part-A",
                             "part-B": "criterion-part-B"},
        "gate_set": dict(gate_set),
        "identity_weighed": {c["seat"]: "unverified"
                             for c in CREW5}},
        view_seq=store.head_seq())


def fresh_gated():
    """fresh()'s world with a declared gate set — the
    doorway's assembly-allow discipline binds only declared
    runs."""
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": ["part-B"], "part-B": []},
        "gates": dict(GATES_A1),
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "dir-1": {"role": "director",
                      "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
            "crew-2": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {"crew-1": dict(FULL), "crew-2": dict(FULL)},
    })
    store.commit()
    d = Doorway(store)
    office = Office(d)
    gen = Generator(d)
    tok = {s: d.issue_token(s) for s in
           ("orch-1", "exam-1", "dir-1", "crew-1", "crew-2")}
    return store, d, office, gen, tok


def forged_generated(proposal_seq, onboarding_seq, part):
    """An ASSEMBLY_GENERATED payload in the generator's own
    shape, hand-built so a test can vary exactly one binding."""
    return {
        "assembly_id": "assembly-crew-1-1",
        "instance_id": "inst-crew-1-1",
        "seat": "crew-1",
        "part": part,
        "case_id": "case-crew-1",
        "case_version": 1,
        "proposal_seq": proposal_seq,
        "onboarding_seq": onboarding_seq,
        "declaration_fingerprint": declaration_fingerprint(
            "inst-crew-1-1", DECL),
        "model_selection": {"basis": None, "requested": None},
        "skills": [dict(s) for s in SKILLS],
        "grants": copy.deepcopy(GRANTS),
    }


# (a) an instance proposal does not displace the operative
# gate declaration the run-level record established.
store, d, office, gen, tok = fresh()
prop = run_proposal(d, store, tok)
check("T13a before any record, the operative set is the "
      "commission's declaration (here, none)",
      _gates.operative_declaration(d.state()) == {})
run_record(d, store, tok, prop["event_seq"], GATES_A1)
check("T13a the record bound to the run proposal governs",
      _gates.operative_declaration(d.state()) == GATES_A1)
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
check("T13a the fold keeps the two proposals distinct",
      [p["proposal_kind"] for p in
       d.state()["assembly_proposals"]] == ["run", "instance"])
check("T13a the instance proposal does not displace the "
      "operative declaration",
      _gates.operative_declaration(d.state()) == GATES_A1)

# (b) a run-level assembly allow recorded after an instance
# proposal still validates against the run proposal's record.
store, d, office, gen, tok = fresh_gated()
prop = run_proposal(d, store, tok)
run_record(d, store, tok, prop["event_seq"], GATES_A1)
gen.propose(tok["orch-1"], "crew-1", part="part-A",
            role_requirements="a careful drafting model")
ev = d.act(tok["exam-1"], "GATE_OUTCOME",
           {"joint": "assembly", "outcome": "allow"},
           view_seq=store.head_seq())
check("T13b the assembly allow answers the run proposal, "
      "not the instance proposal standing after it",
      ev["type"] == "GATE_OUTCOME"
      and _gates.assembly_open(d.state()))

# (c) generation refuses to answer a run-level proposal — at
# preflight (nothing recorded) and at the doorway (a refusal
# recorded) alike.
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
prop = run_proposal(d, store, tok)
head = store.head_seq()
r = gen.generate(tok["orch-1"], "crew-1", identify,
                 skills=SKILLS, grants=GRANTS)
check("T13c generation does not answer a run-level proposal",
      r["ok"] is False and store.head_seq() == head
      and d.state()["instance_onboarding"] == {}
      and d.state()["assemblies"] == {})
ob_ev = ob.onboard_instance(
    d, tok["orch-1"], "crew-1", "inst-crew-1-1",
    "assembly-crew-1-1", DECL, provider_model_id=PROVIDER_ID)
before = len(store.all_events())
check("T13c a generation bound to the run proposal is "
      "refused at the doorway, the refusal recorded",
      refused(lambda: d.act(
          tok["orch-1"], "ASSEMBLY_GENERATED",
          forged_generated(prop["event_seq"],
                           ob_ev["event_seq"], "part-A"),
          view_seq=store.head_seq()))
      and len(store.all_events()) == before + 1
      and store.all_events()[-1]["type"] == "REJECTION"
      and "run-level" in store.all_events()[-1]["payload"].get(
          "ground", ""))

# (d) the part correspondence: a part the bound case does not
# cover fails generation preflight (nothing recorded) and is
# refused at the doorway (refusal recorded).
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
gen.propose(tok["orch-1"], "crew-1", part="part-B",
            role_requirements="a careful drafting model")
head = store.head_seq()
r = gen.generate(tok["orch-1"], "crew-1", identify,
                 skills=SKILLS, grants=GRANTS)
check("T13d a part the case does not cover fails preflight",
      r["ok"] is False and "part" in " ".join(r["problems"]))
check("T13d preflight recorded nothing",
      store.head_seq() == head
      and d.state()["instance_onboarding"] == {}
      and d.state()["assemblies"] == {})
store, d, office, gen, tok = fresh()
issue_case(d, office, tok, "crew-1")
prop_ev = gen.propose(tok["orch-1"], "crew-1", part="part-A",
                      role_requirements="a careful drafting "
                                        "model")
ob_ev = ob.onboard_instance(
    d, tok["orch-1"], "crew-1", "inst-crew-1-1",
    "assembly-crew-1-1", DECL, provider_model_id=PROVIDER_ID)
before = len(store.all_events())
check("T13d a record filling a part its case does not cover "
      "is refused at the doorway, the refusal recorded",
      refused(lambda: d.act(
          tok["orch-1"], "ASSEMBLY_GENERATED",
          forged_generated(prop_ev["event_seq"],
                           ob_ev["event_seq"], "part-B"),
          view_seq=store.head_seq()))
      and len(store.all_events()) == before + 1
      and store.all_events()[-1]["type"] == "REJECTION"
      and "part" in store.all_events()[-1]["payload"].get(
          "ground", ""))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES:", *FAILURES, sep="\n  ")
    sys.exit(1)
print("ALL PASS")
