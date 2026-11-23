"""Piece 6 tests — onboarding (SPEC SHEET §3.6, R18-R20),
against the nine acceptance tests of src/PIECE6-SCOPE-2026-11-22.md
§6 as settled on examination (addendum): F1 attestation as a later
ONBOARDING carrying its reference, the fold keeping the original
record unrewritten; F2 conditional token binding with the
end-to-end run onboarding before binding; F3's corrected test 8
(onboarding leaves the §4 matrix untouched — no claim of a
general effective-case check, which does not exist).

Run: PYTHONPATH=src python3 tests/unit/test_piece6_onboarding.py
Exits 0 when every check passes.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..",
                                "src"))

from framework.record import FrameworkStore, CONSTITUTION_HASH
from framework.doorway import Doorway, DoorwayRefusal
from framework import onboarding as ob

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + "  " + detail)
    if not cond:
        FAILURES.append(name)


def fresh():
    path = os.path.join(tempfile.mkdtemp(), "run.db")
    store = FrameworkStore(path)
    store.insert_run("run-1", CONSTITUTION_HASH)
    store.append("RUN_COMMISSIONED", "dir-1", [], {
        "run_id": "run-1",
        "tree": {"part-A": []},
        "seats": {
            "orch-1": {"role": "orchestrator",
                       "identity_status": "declared"},
            "exam-1": {"role": "examiner",
                       "identity_status": "declared"},
            "crew-1": {"role": "crew",
                       "identity_status": "unverified"},
        },
        "briefs": {},
    })
    store.commit()
    return store, Doorway(store)


# -- T1: the declaration is recorded verbatim, status declared.
store, d = fresh()
orch = d.issue_token("orch-1")
DECL = "I am ExampleModel 4.2, served by Provider P, build 9917."
ob.onboard(d, orch, "crew-1", DECL, capability="writes code",
           limits="no browsing", terms_acknowledged=True,
           terms_ref="COLLABORATION Rev 5")
rec = ob.onboarding_record(d, "crew-1")
check("T1 declaration verbatim (byte-equal) in the fold",
      rec["declaration"] == DECL)
check("T1 status declared", rec["identity_status"] == "declared")

# -- T2: all three statuses handled.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl-u", identity_status="unverified")
ob.onboard(d, orch, "exam-1", "decl-d", identity_status="declared")
ob.onboard(d, orch, "orch-1", "decl-p",
           identity_status="provider-confirmed",
           attestation_ref="provider-attestation/2026-11-22/7")
st = d.state()["onboarding"]
check("T2 unverified recorded",
      st["crew-1"]["identity_status"] == "unverified")
check("T2 declared recorded",
      st["exam-1"]["identity_status"] == "declared")
check("T2 provider-confirmed with reference recorded",
      st["orch-1"]["identity_status"] == "provider-confirmed"
      and st["orch-1"]["attestation"]["attestation_ref"]
      == "provider-attestation/2026-11-22/7")

# -- T3: provider-confirmed without a reference is refused and the
# refusal recorded.
store, d = fresh()
orch = d.issue_token("orch-1")
before = len(store.all_events())
try:
    ob.onboard(d, orch, "crew-1", "decl",
               identity_status="provider-confirmed")
    check("T3 unreferenced provider-confirmed refused", False)
except DoorwayRefusal:
    check("T3 unreferenced provider-confirmed refused", True)
evs = store.all_events()
check("T3 refusal recorded as REJECTION, nothing else appended",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION")

# -- T4: upgrades need a recorded attestation (§7's item).
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "original declaration",
           identity_status="unverified")
try:
    ob.attest(d, orch, "crew-1", "declared", attestation_ref=None)
    check("T4 upgrade without attestation refused", False)
except DoorwayRefusal:
    check("T4 upgrade without attestation refused", True)
ob.attest(d, orch, "crew-1", "provider-confirmed",
          attestation_ref="att/42")
rec = ob.onboarding_record(d, "crew-1")
check("T4 attested upgrade rises",
      rec["identity_status"] == "provider-confirmed")
check("T4 original declaration stands untouched",
      rec["declaration"] == "original declaration")
check("T4 attestation preserved as provenance",
      rec["attestation"]["attestation_ref"] == "att/42"
      and rec["attestation"]["event_seq"] > rec["onboarded_seq"])

# -- T5: capability, limits, terms acknowledgement recorded (R19).
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl", capability="code + tests",
           limits="context 200k; no tools beyond the doorway",
           terms_acknowledged=True, terms_ref="COLLABORATION Rev 5")
rec = ob.onboarding_record(d, "crew-1")
check("T5 capability and limits in the record",
      rec["capability"] == "code + tests"
      and "context 200k" in rec["limits"])
check("T5 terms acknowledgement recorded",
      rec["terms_acknowledged"] is True
      and rec["terms_ref"] == "COLLABORATION Rev 5")

# -- T6: a second onboarding does not replace the first record.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "first declaration",
           capability="first capability", identity_status="declared")
ob.onboard(d, orch, "crew-1", "second declaration",
           capability="second capability", identity_status="declared")
rec = ob.onboarding_record(d, "crew-1")
check("T6 first record stands (declaration + capability)",
      rec["declaration"] == "first declaration"
      and rec["capability"] == "first capability")

# -- T7: token bound at onboarding authenticates (F2); the
# commission path remains where no onboarding stands.
store, d = fresh()
orch = d.issue_token("orch-1")
check("T7 pre-onboarding binding basis is commission",
      d.binding_basis(orch) == "commission")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
crew = d.issue_token("crew-1")
check("T7 post-onboarding binding basis is onboarding",
      d.binding_basis(crew) == "onboarding")
ev = d.act(crew, "COMMENT", {"on_job": True, "text": "ready"},
           view_seq=store.head_seq())
check("T7 the onboarded seat's token authenticates its acts",
      ev["actor"] == "crew-1")
try:
    d.act("not-a-token", "COMMENT", {"on_job": True},
          view_seq=store.head_seq())
    check("T7 a mismatched token is refused", False)
except DoorwayRefusal:
    check("T7 a mismatched token is refused", True)

# -- T8 (corrected): onboarding confers no authority — the §4
# matrix is untouched by it, and onboarding records no case.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
crew = d.issue_token("crew-1")
try:
    d.act(crew, "FINDING", {"text": "not mine to record"},
          view_seq=store.head_seq())
    check("T8 out-of-role act refused exactly as before", False)
except DoorwayRefusal:
    check("T8 out-of-role act refused exactly as before", True)
check("T8 onboarding records no case", d.state()["cases"] == {})

# -- Round 1 (examination): an attestation raises status ONLY.
# T9: an attested downgrade is refused and recorded; the status
# and the attestation provenance stand unchanged.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl",
           identity_status="provider-confirmed",
           attestation_ref="att/original")
before = len(store.all_events())
try:
    ob.attest(d, orch, "crew-1", "unverified",
              attestation_ref="att/downgrade")
    check("T9 attested downgrade refused", False)
except DoorwayRefusal:
    check("T9 attested downgrade refused", True)
rec = ob.onboarding_record(d, "crew-1")
check("T9 status and provenance unchanged after the attempt",
      rec["identity_status"] == "provider-confirmed"
      and rec["attestation"]["attestation_ref"] == "att/original")
evs = store.all_events()
check("T9 the refusal is recorded (one REJECTION appended)",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION")

# T10: an attested same-status act is refused; it may not replace
# the recorded attestation provenance while raising nothing.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
ob.attest(d, orch, "crew-1", "provider-confirmed",
          attestation_ref="att/first")
try:
    ob.attest(d, orch, "crew-1", "provider-confirmed",
              attestation_ref="att/second")
    check("T10 attested same-status act refused", False)
except DoorwayRefusal:
    check("T10 attested same-status act refused", True)
rec = ob.onboarding_record(d, "crew-1")
check("T10 original attestation provenance stands",
      rec["attestation"]["attestation_ref"] == "att/first")

# T11: the fold itself derives no change from a non-raising
# attested event, even in a history that bypassed the doorway
# (direct store append) — replay safety, not a doorway claim.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl",
           identity_status="provider-confirmed",
           attestation_ref="att/original")
store.append("ONBOARDING", "orch-1", [], {
    "seat_id": "crew-1", "identity_status": "unverified",
    "attestation_ref": "att/forged"})
store.commit()
rec = ob.onboarding_record(d, "crew-1")
check("T11 fold ignores a non-raising attested event on replay",
      rec["identity_status"] == "provider-confirmed"
      and rec["attestation"]["attestation_ref"] == "att/original")

# -- Round 1: token binding as enforcement, not a label.
# T12: a token bound at onboarding authenticates only against the
# identity it bound to. The same doorway, over a record where the
# seat's established declaration differs, does not authenticate
# it. (The store is rebound on the doorway to stand for a record
# the token was never issued against.)
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "declaration A",
           identity_status="declared")
crew = d.issue_token("crew-1")
ev = d.act(crew, "COMMENT", {"on_job": True, "text": "ok"},
           view_seq=store.head_seq())
check("T12 token authenticates against its own onboarding record",
      ev["actor"] == "crew-1")
store2, d2 = fresh()
orch2 = d2.issue_token("orch-1")
ob.onboard(d2, orch2, "crew-1", "declaration B",
           identity_status="declared")
d.store = store2  # the same doorway over the other record
try:
    d.act(crew, "COMMENT", {"on_job": True, "text": "ok"},
          view_seq=store2.head_seq())
    check("T12 token refused against a different established "
          "identity", False)
except DoorwayRefusal:
    check("T12 token refused against a different established "
          "identity", True)
d.store = store

# T13: an attested status upgrade does not invalidate the seat's
# token — the upgrade changes the status, never the identity.
store, d = fresh()
orch = d.issue_token("orch-1")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
crew = d.issue_token("crew-1")
ob.attest(d, orch, "crew-1", "provider-confirmed",
          attestation_ref="att/up")
ev = d.act(crew, "COMMENT", {"on_job": True, "text": "still me"},
           view_seq=store.head_seq())
check("T13 token survives an attested status upgrade",
      ev["actor"] == "crew-1")

# -- Round 2 (examination): the route transition.
# T14: a pre-onboarding commission token remains valid only
# while no onboarding record stands. Once the seat is onboarded,
# the old token no longer authenticates; a newly issued token
# binds to the onboarding identity and works.
store, d = fresh()
orch = d.issue_token("orch-1")
crew_old = d.issue_token("crew-1")
ev = d.act(crew_old, "COMMENT", {"on_job": True, "text": "before"},
           view_seq=store.head_seq())
check("T14 commission token works before onboarding",
      ev["actor"] == "crew-1")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
try:
    d.act(crew_old, "COMMENT", {"on_job": True, "text": "after"},
          view_seq=store.head_seq())
    check("T14 old token refused once onboarding stands", False)
except DoorwayRefusal:
    check("T14 old token refused once onboarding stands", True)
crew_new = d.issue_token("crew-1")
check("T14 the new token's basis is onboarding",
      d.binding_basis(crew_new) == "onboarding")
ev = d.act(crew_new, "COMMENT", {"on_job": True, "text": "after"},
           view_seq=store.head_seq())
check("T14 the newly issued token authenticates normally",
      ev["actor"] == "crew-1")

# T15: the orchestrator's own transition — its commission token
# performs the onboarding act (no record stands for it yet at
# authentication time), then dies; a fresh token issued against
# the established record carries the work on.
store, d = fresh()
orch_old = d.issue_token("orch-1")
ob.onboard(d, orch_old, "orch-1", "orchestrator declaration",
           identity_status="declared")
try:
    ob.onboard(d, orch_old, "exam-1", "examiner declaration",
               identity_status="declared")
    check("T15 orchestrator's old token refused after its own "
          "onboarding", False)
except DoorwayRefusal:
    check("T15 orchestrator's old token refused after its own "
          "onboarding", True)
orch_new = d.issue_token("orch-1")
check("T15 the fresh orchestrator token binds at onboarding",
      d.binding_basis(orch_new) == "onboarding")
ob.onboard(d, orch_new, "exam-1", "examiner declaration",
           identity_status="declared")
check("T15 the fresh token carries the work on",
      ob.onboarding_record(d, "exam-1")["declaration"]
      == "examiner declaration")

# -- Owed regression (Vane's non-blocking note on the onboarding
# pass): the expired commission token's refusal is itself
# recorded as a REJECTION.
store, d = fresh()
orch = d.issue_token("orch-1")
crew_old = d.issue_token("crew-1")
ob.onboard(d, orch, "crew-1", "decl", identity_status="declared")
before = len(store.all_events())
try:
    d.act(crew_old, "COMMENT", {"on_job": True, "text": "after"},
          view_seq=store.head_seq())
    check("T16 expired token refused", False)
except DoorwayRefusal:
    check("T16 expired token refused", True)
evs = store.all_events()
check("T16 the refusal is recorded as a REJECTION naming the seat",
      len(evs) == before + 1 and evs[-1]["type"] == "REJECTION"
      and evs[-1]["payload"].get("seat") == "crew-1")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURES:", *FAILURES, sep="\n  ")
    sys.exit(1)
print("ALL PASS")
