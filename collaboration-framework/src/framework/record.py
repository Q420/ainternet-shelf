"""Framework record service — SPEC SHEET §3.1 (substrate, extended).

The single state of a run. Append-only; every act by every seat is an
event or does not exist for the framework (R1–R4).

Why this is new code beside the carried substrate, not an edit of it:
the carried `fabric/store.py` asserts its prototype event vocabulary
(module-level EVENT_TYPES) inside append(), so framework event types
cannot pass through it without editing a pinned file. SPEC SHEET §2
forbids silent substrate changes and §3.1 names this component
"substrate, extended" — so the extension lives here, recorded in
ADR-003, reusing the substrate's canonical hashing (`fabric.canonical`)
and its storage discipline (same schema shape, same append-only
triggers, same hash-chain rule). The carried files are untouched.

Every event carries: its run (run_id, in the event itself and so
under its hash), its acting seat (actor), a timestamp (ts), its
type, its payload, and the hash chain link (prev_hash/hash) — R1. A correction is a new event naming the
event it corrects (payload.corrects) — nothing is edited or deleted.
"""
import json
import sqlite3
import time
import uuid

from fabric.canonical import canonical, sha256_hex, event_hash

# The framework's constitution: the approved design pair and the pin.
# A run's genesis binds to this string's hash, so a record can always
# be checked against the design it was made under.
CONSTITUTION_TEXT = (
    "collaboration-framework constitution: COLLABORATION Rev 5 + "
    "SPEC SHEET Rev 5 (approved by Ben 2026-11-21) + ADR-002 substrate "
    "pin 87c9ec08 + ADR-003 record extension"
)
CONSTITUTION_HASH = sha256_hex(CONSTITUTION_TEXT.encode("utf-8"))

# R3: the record distinguishes these types. Lifecycle per SPEC §5.
EVENT_TYPES = {
    "RUN_COMMISSIONED", "SEAT_BOUND", "CONTRIBUTION", "COMMENT",
    "DISAGREEMENT", "DISAGREEMENT_SETTLED", "GATE_OUTCOME", "FINDING",
    "RULING", "DISPOSITION", "CERTIFICATION", "CASE_ISSUED",
    "CASE_CORRECTED", "CASE_VERIFIED", "CASE_JUDGED", "CASE_NOTIFIED",
    "CASE_ACKNOWLEDGED", "DRIVER_FAILURE",
    "ONBOARDING", "ESCALATION", "CLAIM_STATUS",
    "COMPLETION_CLAIMED", "MATERIAL_SEALED", "REJECTION", "RUN_CLOSED",
}

# R14: a case's content fields, over which a correction's
# classification is computed (Piece 5, addendum 1 §A: the diff runs
# over the case's contents, not only the three R16's gloss names;
# any change classifies the correction semantic). The scope counts
# six semantic fields — the tree and the highlighted part form one
# combined field — compared here as seven stored keys; the
# classification is the same either way, since a change to the
# tree, the part, or both is a change to that one field.
CASE_CONTENT_FIELDS = ("assignment", "tree", "part",
                       "evidence_boundary", "verification_list",
                       "account", "authority")

CLAIM_STATUSES = {"claimed", "evidenced", "verified", "disputed",
                  "stood_down"}

ROLES = {"crew", "orchestrator", "examiner", "director"}


class FrameworkStore:
    """One run's append-only, hash-chained event history.

    Mirrors the substrate store's discipline (insert-only triggers,
    chain-linked hashes, caller-owned transactions) with the
    framework's vocabulary and a timestamp on every event (R1).
    """

    def __init__(self, path: str):
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS events (
                 event_seq INTEGER PRIMARY KEY,
                 event_id TEXT UNIQUE NOT NULL,
                 run_id TEXT NOT NULL,
                 type TEXT NOT NULL,
                 actor TEXT NOT NULL,
                 affected TEXT NOT NULL,
                 payload TEXT NOT NULL,
                 ts TEXT NOT NULL,
                 prev_hash TEXT NOT NULL,
                 hash TEXT NOT NULL
               )"""
        )
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_update
               BEFORE UPDATE ON events
               BEGIN SELECT RAISE(ABORT, 'events are append-only'); END"""
        )
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_delete
               BEFORE DELETE ON events
               BEGIN SELECT RAISE(ABORT, 'events are append-only'); END"""
        )
        self._conn.execute(
            """CREATE TRIGGER IF NOT EXISTS events_no_replace
               BEFORE INSERT ON events
               BEGIN
                 SELECT RAISE(ABORT, 'events are insert-only')
                 WHERE EXISTS (SELECT 1 FROM events
                               WHERE event_seq = NEW.event_seq
                                  OR event_id = NEW.event_id);
               END"""
        )
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                 run_id TEXT PRIMARY KEY,
                 constitution_hash TEXT NOT NULL,
                 status TEXT NOT NULL DEFAULT 'open'
               )"""
        )
        self._conn.commit()

    def insert_run(self, run_id: str, constitution_hash: str):
        self._conn.execute(
            "INSERT INTO runs (run_id, constitution_hash) VALUES (?,?)",
            (run_id, constitution_hash),
        )

    def get_run_id(self):
        row = self._conn.execute("SELECT run_id FROM runs LIMIT 1").fetchone()
        return row[0] if row else None

    def last(self):
        row = self._conn.execute(
            "SELECT event_seq, hash FROM events ORDER BY event_seq DESC"
            " LIMIT 1"
        ).fetchone()
        return row  # (seq, hash) or None

    def head_seq(self) -> int:
        last = self.last()
        return 0 if last is None else last[0]

    def append(self, type_: str, actor: str, affected: list,
               payload: dict) -> dict:
        assert type_ in EVENT_TYPES, f"unknown event type {type_}"
        # R1: every event carries its run — explicitly, in the event
        # itself (and so under the hash), not by store implication.
        run_id = self.get_run_id()
        assert run_id is not None, "no run inserted; events carry a run"
        # R1 (correction round 2): a commissioning payload that names
        # a different run than the event's own run is refused at the
        # door of the record — the two bindings can never disagree in
        # a recorded history.
        if type_ == "RUN_COMMISSIONED" and \
                payload.get("run_id") not in (None, run_id):
            raise AssertionError(
                f"RUN_COMMISSIONED payload run {payload.get('run_id')!r} "
                f"disagrees with the event's run {run_id!r} (R1)")
        last = self.last()
        seq = 1 if last is None else last[0] + 1
        prev_hash = "" if last is None else last[1]
        event = {
            "event_seq": seq,
            "event_id": str(uuid.uuid4()),
            "run_id": run_id,
            "type": type_,
            "actor": actor,
            "affected": list(affected),
            "payload": payload,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "prev_hash": prev_hash,
        }
        event["hash"] = event_hash(prev_hash, event)
        self._conn.execute(
            "INSERT INTO events (event_seq, event_id, run_id, type,"
            " actor, affected, payload, ts, prev_hash, hash)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (seq, event["event_id"], run_id, type_, actor,
             json.dumps(event["affected"]), json.dumps(event["payload"]),
             event["ts"], prev_hash, event["hash"]),
        )
        return event

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def all_events(self):
        rows = self._conn.execute(
            "SELECT event_seq, event_id, run_id, type, actor, affected,"
            " payload, ts, prev_hash, hash FROM events ORDER BY event_seq"
        ).fetchall()
        out = []
        for seq, eid, run_id, typ, actor, affected, payload, ts, prev, \
                h in rows:
            out.append({
                "event_seq": seq, "event_id": eid, "run_id": run_id,
                "type": typ, "actor": actor,
                "affected": json.loads(affected),
                "payload": json.loads(payload), "ts": ts,
                "prev_hash": prev, "hash": h,
            })
        return out


def verify_chain(events) -> bool:
    """Recompute every link with the substrate's canonical hashing."""
    prev = ""
    for ev in events:
        if ev["prev_hash"] != prev:
            return False
        body = {k: v for k, v in ev.items() if k != "hash"}
        if event_hash(prev, body) != ev["hash"]:
            return False
        prev = ev["hash"]
    return True


def verify_run_binding(events, run_id) -> bool:
    """R1, verifiable: every event carries this run's id."""
    return all(ev.get("run_id") == run_id for ev in events)


# ---------------------------------------------------------------- fold

def empty_state(run_id=None) -> dict:
    return {
        "run_id": run_id,
        "lifecycle": "unopened",
        "lifecycle_seq": None,
        "seats": {},          # seat_id -> {role, identity_status}
        "onboarding": {},     # seat_id -> {declaration, identity_status,
                              #   capability, limits, terms_acknowledged,
                              #   terms_ref, onboarded_seq, attestation}
                              #   (Piece 6, R18-R19: the first ONBOARDING
                              #   establishes the record; a later attested
                              #   ONBOARDING raises status only)
        "claims": {},         # claim_id -> {author, status, subject}
        "disagreements": {},  # disagreement_id -> {status, claim_id, by}
        "contributions": {},  # contribution_id -> {author, tree_part}
        "cases": {},          # case_id -> {version, seat}
        "gates": {},          # joint -> {outcome, by, event_seq}
        "certifications": [],  # {by, coverage, event_seq}
        "findings": [], "rulings": [], "dispositions": [],
        "escalations": [], "rejections": [],
        "sealed": {},         # material_id -> [seat_id, ...] boundary
        "stalled": {},        # seat_id -> {kind, part, event_seq} (R33)
        "tree": {},           # tree_part -> [downstream parts] (R30)
        "paused": {},         # tree_part -> {source_seq, source_joint,
                              #                 downstream}
        "head_seq": 0,
    }


def _subject_changed_parts(payload):
    part = payload.get("tree_part")
    return part


def apply_event(state: dict, ev: dict) -> dict:
    """One fold step. Deterministic; replay reproduces state (R4).

    The fold applies what the record holds. Whether an act was
    *allowed* is the doorway's enforcement (§3.2); the fold never
    invents or drops a recorded act.
    """
    t = ev["type"]
    p = ev["payload"]
    actor = ev["actor"]
    state["head_seq"] = ev["event_seq"]

    if t == "RUN_COMMISSIONED":
        # R1 (correction round 2): the run the state reports is the
        # event's own run_id — the one under the hash — never a
        # payload value that could disagree with it.
        state["run_id"] = ev.get("run_id", state["run_id"])
        state["lifecycle"] = "commissioned"
        state["lifecycle_seq"] = ev["event_seq"]
        # R30: the commissioned tree (part -> downstream dependents)
        # is the record the doorway computes paused sets from.
        state["tree"] = dict(p.get("tree", {}))
        for seat_id, binding in p.get("seats", {}).items():
            state["seats"][seat_id] = {
                "role": binding["role"],
                "identity_status": binding.get("identity_status",
                                               "unverified"),
            }
    elif t == "SEAT_BOUND":
        state["seats"][p["seat_id"]] = {
            "role": p["role"],
            "identity_status": p.get("identity_status", "unverified"),
        }
    elif t == "ONBOARDING":
        # Piece 6 (R18-R19, scope F1 as settled): the FIRST onboarding
        # establishes the seat's record - declaration verbatim,
        # capability, limits, terms acknowledgement, initial status -
        # and is never replaced or rewritten. A LATER onboarding
        # carrying an attestation reference may raise the status only:
        # the attestation (event position + reference) is preserved as
        # the upgrade's provenance, and the original declaration and
        # details stand untouched. A later onboarding without an
        # attestation changes nothing the fold derives (the doorway
        # refuses status upgrades attempted without one; a same- or
        # lower-status restatement is history, not a new record).
        seat = p["seat_id"]
        rec = state["onboarding"].get(seat)
        if rec is None:
            state["onboarding"][seat] = {
                "declaration": p.get("declaration"),
                "identity_status": p.get("identity_status",
                                         "unverified"),
                "capability": p.get("capability"),
                "limits": p.get("limits"),
                "terms_acknowledged": p.get("terms_acknowledged"),
                "terms_ref": p.get("terms_ref"),
                "onboarded_seq": ev["event_seq"],
                "attestation": ({"event_seq": ev["event_seq"],
                                 "attestation_ref":
                                     p["attestation_ref"]}
                                if p.get("attestation_ref") else None),
            }
        elif p.get("attestation_ref"):
            # An attestation raises status only (examination
            # round 1): a same- or lower-status attested event
            # alters neither the status nor the attestation
            # provenance the record derives. The doorway refuses
            # such acts; the fold is safe on its own as well, so
            # replay of any history derives the same record.
            rank = {"unverified": 0, "declared": 1,
                    "provider-confirmed": 2}
            new = p.get("identity_status")
            if new in rank and rank[new] > rank.get(
                    rec["identity_status"], 0):
                rec["identity_status"] = new
                rec["attestation"] = {
                    "event_seq": ev["event_seq"],
                    "attestation_ref": p["attestation_ref"]}
    elif t == "CONTRIBUTION":
        cid = p.get("contribution_id", ev["event_id"])
        state["contributions"][cid] = {
            "author": actor, "tree_part": p.get("tree_part"),
        }
        if p.get("claim_id"):
            state["claims"][p["claim_id"]] = {
                "author": actor, "status": "claimed",
                "subject": cid, "status_seq": ev["event_seq"],
            }
    elif t == "DISAGREEMENT":
        did = p.get("disagreement_id", ev["event_id"])
        state["disagreements"][did] = {
            "status": "open", "claim_id": p.get("claim_id"),
            "by": actor, "status_seq": ev["event_seq"],
        }
        # R2: disputed follows a recorded disagreement naming the claim.
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim and claim["status"] in ("claimed", "evidenced"):
            claim["status"] = "disputed"
            claim["status_seq"] = ev["event_seq"]
    elif t == "DISAGREEMENT_SETTLED":
        d = state["disagreements"].get(p.get("disagreement_id") or "")
        if d:
            d["status"] = "settled"
            d["status_seq"] = ev["event_seq"]
    elif t == "CLAIM_STATUS":
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim:
            claim["status"] = p["to"]
            claim["status_seq"] = ev["event_seq"]
    elif t == "GATE_OUTCOME":
        joint = p.get("joint")
        # R22: the outcome vocabulary is exactly allow / correct /
        # escalate. The fold records who recorded the outcome —
        # later authority (R2's examiner-at-a-gate) is grounded in
        # this entry, never in a caller's assertion.
        state["gates"][joint] = {
            "outcome": p.get("outcome"), "by": actor,
            "event_seq": ev["event_seq"],
        }
        # R30: a gate "holding" work is not a fourth outcome — it is
        # the paused state an escalation records (work stops on the
        # part and its recorded downstream, awaiting ruling) until
        # an allow at the joint releases it. Every pause records the
        # joint it was set at (source_joint); an allow releases only
        # pauses that joint itself recorded — a release is bound to
        # the recorded pause, never to an arbitrary caller list
        # (correction round 3).
        if p.get("outcome") == "escalate":
            for part in p.get("paused_set", []):
                state["paused"][part] = {
                    "source_seq": ev["event_seq"],
                    "source_joint": joint,
                    "downstream": p.get("downstream", {}).get(part, []),
                }
        elif p.get("outcome") == "allow":
            for part in p.get("paused_set", []) + \
                    p.get("released_set", []):
                entry = state["paused"].get(part)
                if entry is not None and \
                        entry.get("source_joint") == joint:
                    state["paused"].pop(part, None)
    elif t == "ESCALATION":
        state["escalations"].append({
            "by": actor, "joint": p.get("joint"),
            "event_seq": ev["event_seq"],
        })
        for part in p.get("paused_set", []):
            state["paused"][part] = {
                "source_seq": ev["event_seq"],
                "source_joint": p.get("joint"),
                "downstream": p.get("downstream", {}).get(part, []),
            }
    elif t in ("CASE_ISSUED", "CASE_CORRECTED", "CASE_VERIFIED",
               "CASE_JUDGED", "CASE_NOTIFIED", "CASE_ACKNOWLEDGED"):
        # §3.5's acts, tracked per version (Piece 4 groundwork):
        # the fold records each act as it stands and never infers
        # one from another — whether a version stands issued is
        # decided by version_issued() over these entries.
        entry = state["cases"].setdefault(
            p["case_id"], {"version": 0, "seat": None, "versions": {}})
        if p.get("seat"):
            entry["seat"] = p["seat"]
        ver = entry["versions"].setdefault(str(p["version"]), {
            "verified": None, "judged": None, "notified": None,
            "issued": None, "content": None, "corrected": False,
            "corrected_seq": None,
            "representational": False, "acknowledged": {},
        })
        if t == "CASE_ISSUED":
            ver["issued"] = ev["event_seq"]
            # Authorisation does not replace content: a corrected
            # version's content stands on its CASE_CORRECTED event,
            # and the authorising CASE_ISSUED may name the version
            # only. Version 1's content rides on its CASE_ISSUED.
            if ver["content"] is None:
                ver["content"] = dict(p)
            entry["version"] = max(entry["version"], p["version"])
        elif t == "CASE_CORRECTED":
            # A version's correction is established once, by its
            # first CASE_CORRECTED (correction round 2): a second
            # correction event for the same version stands in the
            # history but never replaces the established content
            # or classification. Once issued, the version is
            # fixed; a change is a new version with its own route.
            if not ver["corrected"]:
                ver["corrected"] = True
                ver["corrected_seq"] = ev["event_seq"]
                ver["representational"] = bool(
                    p.get("representational"))
                ver["content"] = dict(p)
            entry["version"] = max(entry["version"], p["version"])
        elif t == "CASE_VERIFIED":
            # The first verification stands (Piece 5, addendum 2
            # §F/D): its position is the version's verification
            # position, immutably — a second verification of the
            # same version is history, never a replacement. And
            # where the verification carries the case's content —
            # version 1's issuance route under §3.5, where content
            # rides on the verification — that content is
            # established here, first-wins like the position.
            if ver["verified"] is None:
                ver["verified"] = ev["event_seq"]
            if ver["content"] is None and \
                    any(f in p for f in CASE_CONTENT_FIELDS):
                ver["content"] = dict(p)
        elif t == "CASE_JUDGED":
            ver["judged"] = ev["event_seq"]
        elif t == "CASE_NOTIFIED":
            ver["notified"] = ev["event_seq"]
        elif t == "CASE_ACKNOWLEDGED":
            ver["acknowledged"][actor] = ev["event_seq"]
    elif t == "DRIVER_FAILURE":
        # R13/R33: the seat is stalled. No pause is computed, no
        # state clears it in this piece — a stall stands until a
        # recorded event establishes otherwise.
        state["stalled"][p["seat"]] = {
            "kind": p.get("kind"), "part": p.get("part"),
            "event_seq": ev["event_seq"],
        }
    elif t == "CERTIFICATION":
        state["certifications"].append({
            "by": actor, "coverage": p.get("coverage"),
            "event_seq": ev["event_seq"],
        })
        # R3: a disagreement still open at close is open-at-close.
        if p.get("closes_run"):
            for d in state["disagreements"].values():
                if d["status"] == "open":
                    d["status"] = "open-at-close"
                    d["status_seq"] = ev["event_seq"]
            state["lifecycle"] = "certified"
            state["lifecycle_seq"] = ev["event_seq"]
    elif t == "FINDING":
        state["findings"].append({"by": actor,
                                   "event_seq": ev["event_seq"]})
    elif t == "RULING":
        state["rulings"].append({"by": actor,
                                  "event_seq": ev["event_seq"]})
    elif t == "DISPOSITION":
        state["dispositions"].append({"by": actor,
                                       "event_seq": ev["event_seq"]})
    elif t == "MATERIAL_SEALED":
        state["sealed"][p["material_id"]] = list(p.get("boundary", []))
    elif t == "REJECTION":
        state["rejections"].append({
            "seat": p.get("seat"), "attempted": p.get("attempted_type"),
            "ground": p.get("ground"), "event_seq": ev["event_seq"],
        })
    elif t == "COMPLETION_CLAIMED":
        state["lifecycle"] = "completion_claimed"
        state["lifecycle_seq"] = ev["event_seq"]
    elif t == "RUN_CLOSED":
        state["lifecycle"] = "closed"
        state["lifecycle_seq"] = ev["event_seq"]
    # COMMENT is a recorded act the fold carries in the history without
    # derived state of its own.
    return state


def fold(events, run_id=None) -> dict:
    state = empty_state(run_id)
    for ev in events:
        apply_event(state, ev)
    return state


def replay(store: FrameworkStore) -> dict:
    return fold(store.all_events(), store.get_run_id())


def version_issued(ver, version) -> bool:
    """Whether one recorded case version completed its issuance
    route (R15/R16): office verification and authorisation always;
    the examiner's act is the sufficiency judgement — or, for a
    correction recorded as purely representational, the examiner
    notification. The route follows the version's recorded
    classification, never whichever events happen to be present.
    The prerequisites must PRECEDE the authorisation: an early
    CASE_ISSUED is not made valid by acts recorded after it
    (correction round 1, point 2). And a version above the initial
    version stands on its CASE_CORRECTED — no correction event, no
    correction (point 3). The order within the route is exact:
    correction < verification < the examiner's act < authorisation
    (Piece 5, addendum 2 §F)."""
    if not ver or ver.get("verified") is None or \
            ver.get("issued") is None:
        return False
    if version > 1 and not ver.get("corrected"):
        return False
    if not ver["verified"] < ver["issued"]:
        return False
    if ver.get("corrected"):
        # The correction precedes the whole route (round 2): the
        # acts that issue a version act on the content its
        # correction established.
        cseq = ver.get("corrected_seq")
        if cseq is None or not cseq < ver["verified"]:
            return False
        # The issuance order is exact (Piece 5, addendum 2 §F):
        # correction < verification < the examiner's act <
        # authorisation. An examiner act recorded before the
        # verification it answers does not complete the route,
        # however complete the set of acts looks.
        if ver.get("representational"):
            return ver.get("notified") is not None and \
                ver["verified"] < ver["notified"] < ver["issued"]
        return ver.get("judged") is not None and \
            ver["verified"] < ver["judged"] < ver["issued"]
    return ver.get("judged") is not None and \
        ver["verified"] < ver["judged"] < ver["issued"]


def effective_case(state: dict, seat_id: str):
    """The seat's current effective case (Piece 4): the highest
    version that completed its issuance route, with its content as
    recorded — or None when no version stands issued. A newer
    incomplete version never displaces a standing one."""
    best = None
    for case_id, entry in state["cases"].items():
        if entry.get("seat") != seat_id:
            continue
        for vstr, ver in entry["versions"].items():
            v = int(vstr)
            if version_issued(ver, v):
                # R32: an acknowledgement counts only when the
                # assigned seat recorded it after this version's
                # authorisation (correction round 1, point 4).
                ack_seq = ver.get("acknowledged", {}).get(seat_id)
                acknowledged = ack_seq is not None and \
                    ver.get("issued") is not None and \
                    ack_seq > ver["issued"]
                if best is None or v > best["version"]:
                    best = {
                        "case_id": case_id, "version": v,
                        "content": ver.get("content"),
                        "issued_seq": ver.get("issued"),
                        "corrected": ver.get("corrected", False),
                        "acknowledged": acknowledged,
                    }
    return best


def state_hash(state: dict) -> str:
    return sha256_hex(canonical(state))


# ------------------------------------------------------- claim status

GATE_OUTCOMES = ("allow", "correct", "escalate")  # R22


def validate_status_transition(state, actor, role, claim_id, to,
                               evidence=None, gate_joint=None):
    """R2's authority rules for claim-status transitions.

    Returns (ok, ground). The doorway enforces this before recording;
    a refused transition is recorded as a REJECTION (R6).
    """
    claim = state["claims"].get(claim_id)
    if claim is None:
        return False, f"unknown claim {claim_id}"
    if to not in CLAIM_STATUSES:
        return False, f"unknown claim status {to}"
    if to == "claimed":
        return False, "claimed is a claim's initial status, not a transition"
    if to == "disputed":
        return False, ("disputed follows a recorded disagreement naming "
                       "the claim (R2); it is not recorded directly")
    if to == "evidenced":
        # §4: attaching evidence is crew's act alone.
        if role != "crew":
            return False, ("evidence is attached by crew (authority "
                           f"matrix, §4); {role} may not record it")
        if not evidence:
            return False, "evidenced requires the evidence being attached"
        if claim["status"] in ("verified", "stood_down"):
            return False, f"a {claim['status']} claim takes no new evidence"
        return True, ""
    if to == "verified":
        if role != "examiner":
            return False, "verified is recorded by the examiner alone (R2)"
        if claim["status"] != "evidenced":
            return False, ("verified is recorded on evidence (R2); the "
                           f"claim stands {claim['status']}")
        return True, ""
    if to == "stood_down":
        if actor == claim["author"]:
            return True, ""
        if role == "examiner" and gate_joint is not None:
            # "At a gate" is grounded in the record: the fold must
            # show a gate outcome for that joint recorded by this
            # examiner — never a caller-supplied flag.
            gate = state["gates"].get(gate_joint)
            if gate is not None and gate.get("by") == actor:
                return True, ""
            return False, (f"no gate outcome for joint {gate_joint} "
                           "recorded by this examiner stands in the "
                           "record (R2)")
        return False, ("stood_down is recorded by the claim's author, or "
                       "by the examiner at a gate (R2)")
    return False, f"unhandled transition to {to}"
