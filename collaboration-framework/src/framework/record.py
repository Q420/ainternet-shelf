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
    "CASE_CORRECTED", "ONBOARDING", "ESCALATION", "CLAIM_STATUS",
    "COMPLETION_CLAIMED", "MATERIAL_SEALED", "REJECTION", "RUN_CLOSED",
}

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
        "seats": {},          # seat_id -> {role, identity_status}
        "claims": {},         # claim_id -> {author, status, subject}
        "disagreements": {},  # disagreement_id -> {status, claim_id, by}
        "contributions": {},  # contribution_id -> {author, tree_part}
        "cases": {},          # case_id -> {version, seat}
        "gates": {},          # joint -> {outcome, by, event_seq}
        "certifications": [],  # {by, coverage, event_seq}
        "findings": [], "rulings": [], "dispositions": [],
        "escalations": [], "rejections": [],
        "sealed": {},         # material_id -> [seat_id, ...] boundary
        "paused": {},         # tree_part -> {source_seq, downstream}
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
        state["run_id"] = p.get("run_id", state["run_id"])
        state["lifecycle"] = "commissioned"
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
    elif t == "CONTRIBUTION":
        cid = p.get("contribution_id", ev["event_id"])
        state["contributions"][cid] = {
            "author": actor, "tree_part": p.get("tree_part"),
        }
        if p.get("claim_id"):
            state["claims"][p["claim_id"]] = {
                "author": actor, "status": "claimed",
                "subject": cid,
            }
    elif t == "DISAGREEMENT":
        did = p.get("disagreement_id", ev["event_id"])
        state["disagreements"][did] = {
            "status": "open", "claim_id": p.get("claim_id"),
            "by": actor,
        }
        # R2: disputed follows a recorded disagreement naming the claim.
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim and claim["status"] in ("claimed", "evidenced"):
            claim["status"] = "disputed"
    elif t == "DISAGREEMENT_SETTLED":
        d = state["disagreements"].get(p.get("disagreement_id") or "")
        if d:
            d["status"] = "settled"
    elif t == "CLAIM_STATUS":
        claim = state["claims"].get(p.get("claim_id") or "")
        if claim:
            claim["status"] = p["to"]
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
        # an allow at the joint releases it.
        if p.get("outcome") == "escalate":
            for part in p.get("paused_set", []):
                state["paused"][part] = {
                    "source_seq": ev["event_seq"],
                    "downstream": p.get("downstream", {}).get(part, []),
                }
        elif p.get("outcome") == "allow":
            for part in p.get("paused_set", []) + \
                    p.get("released_set", []):
                state["paused"].pop(part, None)
    elif t == "ESCALATION":
        state["escalations"].append({
            "by": actor, "joint": p.get("joint"),
            "event_seq": ev["event_seq"],
        })
        for part in p.get("paused_set", []):
            state["paused"][part] = {
                "source_seq": ev["event_seq"],
                "downstream": p.get("downstream", {}).get(part, []),
            }
    elif t == "CASE_ISSUED" or t == "CASE_CORRECTED":
        state["cases"][p["case_id"]] = {
            "version": p["version"], "seat": p.get("seat"),
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
            state["lifecycle"] = "certified"
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
    elif t == "RUN_CLOSED":
        state["lifecycle"] = "closed"
    # COMMENT and ONBOARDING are recorded acts the fold carries in the
    # history without derived state of their own in this piece.
    return state


def fold(events, run_id=None) -> dict:
    state = empty_state(run_id)
    for ev in events:
        apply_event(state, ev)
    return state


def replay(store: FrameworkStore) -> dict:
    return fold(store.all_events(), store.get_run_id())


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
