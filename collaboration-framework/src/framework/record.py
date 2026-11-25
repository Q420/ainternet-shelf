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
import hashlib
import json
import sqlite3
import threading
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
    "ONBOARDING", "ESCALATION", "CLAIM_STATUS", "HOLDER_UNAVAILABLE",
    "COMPLETION_CLAIMED", "MATERIAL_SEALED", "REJECTION", "RUN_CLOSED",
    # §3.8 (Piece 6, orchestrator functions): the assembly
    # proposal, the examiner's assembly record, and the
    # orchestrator's readiness declaration — three distinct acts
    # with three distinct meanings, none impersonating another.
    "ASSEMBLY_PROPOSED", "ASSEMBLY_RECORD", "RUN_READY_FOR_COMPLETION",
    # Agent layer (Piece A1, SPEC Rev 6 R37–R40): the assembly
    # lifecycle of a generated instance. ASSEMBLY_PROPOSED above
    # doubles as the lifecycle's proposal act — the same act,
    # its payload extended with the seat slot being filled —
    # and the instance's own ONBOARDING (subject "instance")
    # stands between the proposal and ASSEMBLY_GENERATED.
    "ASSEMBLY_GENERATED", "ASSEMBLY_PROBED", "ASSEMBLY_VERIFIED",
    "ASSEMBLY_JUDGED",
    "ASSEMBLY_PACKED", "ASSEMBLY_ISSUE_AUTHORISED",
    "INSTANCE_ACTIVATED",
    # Agent layer (Piece A2, SPEC Rev 6 R44–R48): the dispatch
    # sequence. A request is the instance's act; the dispatch
    # intent is the doorway's, recorded as mechanism on a passed
    # grant check; the start and the outcome are the executor's
    # reports under its own constrained identity; reconciliation
    # is the examiner's determination on an uncertain dispatch.
    "TOOL_REQUESTED", "TOOL_DISPATCHED", "TOOL_STARTED",
    "TOOL_OUTCOME", "TOOL_RECONCILED",
    # Agent layer (Piece A3, SPEC Rev 6 R49–R51): the bounded
    # loop's bookkeeping. An iteration is recorded by the loop
    # machinery under its own constrained identity before the
    # model call it accounts; a stall is the recorded stop a
    # bound produces — never a silent one (R50).
    "LOOP_ITERATION", "LOOP_STALLED",
    # Response-evidence piece (WORKER-RESPONSE-EVIDENCE-SCOPE
    # Rev 8): the call boundary, the iteration's response
    # disposition, and the evidence mechanism's own failure
    # terminal. CALL_ENTERED is the loop's durable crossing
    # of the call-entry boundary (R5-2/R6-2); RESPONSE_EVIDENCE
    # is the disposition every entered iteration owes exactly
    # one of (R3-1/R4-1); EVIDENCE_CAPTURE_FAILED records the
    # evidence mechanism's own failure — terminal for the
    # instance, and never a disposition (R8-2).
    "CALL_ENTERED", "RESPONSE_EVIDENCE", "EVIDENCE_CAPTURE_FAILED",
    # Native adapter piece (NATIVE-ADAPTER-SCOPE Rev 3, N32):
    # the translation record — the iteration's per-call
    # translation and refusal decisions, a distinct durable
    # event committed after the response-evidence disposition
    # and before the first dispatch of the iteration, bound to
    # the exact response-evidence artifact hash.
    "TRANSLATION_RECORDED",
}

# R14: a case's content fields, over which a correction's
# classification is computed (Piece 5, addendum 1 §A: the diff runs
# over the case's contents, not only the three R16's gloss names;
# any change classifies the correction semantic). The scope counts
# six semantic fields — the tree and the highlighted part form one
# combined field — compared here as seven stored keys; the
# classification is the same either way, since a change to the
# tree, the part, or both is a change to that one field.
# Piece A3 (correction round 1): loop_bounds joins the fields as
# an eighth stored key — the bounded loop's limits live in the
# issued case (R49), so the case-authority route (the office's
# generate/correct and the doorway's classification) must be able
# to carry them; a field the route strips is not a usable case
# requirement. Unlike the R14 fields it is OPTIONAL: a case may
# carry no bounds, and then no loop runs on it.
# The glossary joins the fields as a ninth stored key
# (2026-11-24, the combined configuration): Ben's briefcase
# design (2026-11-16) — the case carries the map of what the
# worker may pull from the shelf: each pullable item's address
# and what it is, and his scratch as his writing space, so his
# pull requests are made from knowledge inside his case (an
# agent cannot request what it cannot conceive of). OPTIONAL
# like loop_bounds, by the same reasoning: a field the route
# strips is not a usable case component.
# The journal joins the fields as a tenth stored key
# (2026-11-24, the orientation pass): Ben's ruling on the
# worker consultation — the case designates the worker's
# journal, a path under his scratch naming HIS notebook
# (where he was, what he noticed, what to do next), so
# each wake package can present it back to him as it
# stands. The notebook is his to write and rewrite —
# appending is his habit, not a mechanism: nothing
# enforces append-only, and he may replace it whole.
# It is orientation, disposable, not authoritative.
# The designation is the case's; the notebook's
# content is his, carried in the package, never in the
# record. OPTIONAL like the glossary, by the same reasoning.
CASE_CONTENT_FIELDS = ("assignment", "tree", "part",
                       "evidence_boundary", "verification_list",
                       "account", "authority", "loop_bounds",
                       "glossary", "journal")

# Piece A1 (R37–R40): the assembly record — the immutable object
# an ASSEMBLY_GENERATED establishes, the examiner judges, and
# ASSEMBLY_PACKED seals. Its canonical hash is computed over
# exactly these fields under a versioned canonicalisation tag, so
# the judged object, the sealed object and the generated object
# are provably the same object (the Piece 7 seal-correspondence
# pattern). Identity claims are NOT among the fields: the
# declaration and the provider-reported id live only in the
# instance's ONBOARDING event; the record binds to that event by
# position (onboarding_seq) and by the declaration's fingerprint.
ASSEMBLY_RECORD_FIELDS = ("assembly_id", "instance_id", "seat",
                          "part", "case_id", "case_version",
                          "proposal_seq", "onboarding_seq",
                          "declaration_fingerprint",
                          "model_selection", "skills", "grants")
ASSEMBLY_RECORD_HASH_VERSION = 1


def assembly_record_hash(record: dict) -> str:
    """The canonical hash of an assembly record (Piece A1):
    SHA-256 over the fabric canonical form of the record's fields
    under the version tag. The pack event itself is never an
    input — the hash names the generated object, not the act
    that seals it."""
    body = {k: record.get(k) for k in ASSEMBLY_RECORD_FIELDS}
    return sha256_hex(canonical({
        "assembly_record_v": ASSEMBLY_RECORD_HASH_VERSION,
        "record": body}))


def declaration_fingerprint(instance_id, declaration) -> str:
    """The fingerprint of an instance's established declaration
    (R38): binds the declaration to the instance it was taken
    from, in the doorway's seat-binding style. The fingerprint
    binds a claim; it does not prove it."""
    return hashlib.sha256(
        f"{instance_id}\x00{declaration}".encode()).hexdigest()


def instance_credential_fingerprint(instance_id, declaration,
                                    case_id, case_version) -> str:
    """The fingerprint an instance's credential binds to (R38):
    the established declaration, the instance, and the case
    binding (id + version). Two instances of the same model in
    the same role hold distinct credentials because their
    instance ids differ."""
    return hashlib.sha256(
        f"{instance_id}\x00{declaration}\x00{case_id}"
        f"\x00{case_version}".encode()).hexdigest()


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
        # One lock serializes every use of the connection
        # (Piece A2, correction round 2): the store holds it
        # inside each of its methods, so no two threads ever
        # drive the connection at the same time, whatever
        # callers do. It is re-entrant — append() reads the
        # run and the chain head through the same locked
        # paths — and a caller that must make a check and its
        # append atomic holds it across the whole sequence
        # via serialized() (the doorway's executor reports do
        # exactly that: their state check and their append
        # are one step, never separable by another thread's
        # append).
        self._lock = threading.RLock()
        # check_same_thread=False: the executor's worker
        # thread records its own TOOL_STARTED through the
        # doorway (Piece A2, correction round 1) — the start
        # report is the executing thread's first act, so the
        # connection cannot be bound to the thread that
        # opened the store. The flag is not load-bearing for
        # safety: the lock above is what serializes access.
        self._conn = sqlite3.connect(path, check_same_thread=False)
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

    def serialized(self):
        """The store's serialization lock, as a context
        manager: hold it across a sequence of store calls to
        make the sequence atomic against other threads. It is
        the same lock every store method holds internally,
        and re-entrant for the thread that holds it."""
        return self._lock

    def insert_run(self, run_id: str, constitution_hash: str):
        with self._lock:
            self._conn.execute(
                "INSERT INTO runs (run_id, constitution_hash)"
                " VALUES (?,?)",
                (run_id, constitution_hash),
            )

    def get_run_id(self):
        with self._lock:
            row = self._conn.execute(
                "SELECT run_id FROM runs LIMIT 1").fetchone()
            return row[0] if row else None

    def last(self):
        with self._lock:
            row = self._conn.execute(
                "SELECT event_seq, hash FROM events ORDER BY"
                " event_seq DESC LIMIT 1"
            ).fetchone()
            return row  # (seq, hash) or None

    def head_seq(self) -> int:
        last = self.last()
        return 0 if last is None else last[0]

    def append(self, type_: str, actor: str, affected: list,
               payload: dict) -> dict:
        # The whole append — the chain-head read, the sequence
        # computation and the insert — is one locked step: two
        # threads appending at once can never read the same
        # head and collide on the sequence.
        with self._lock:
            assert type_ in EVENT_TYPES, \
                f"unknown event type {type_}"
            # R1: every event carries its run — explicitly, in
            # the event itself (and so under the hash), not by
            # store implication.
            run_id = self.get_run_id()
            assert run_id is not None, \
                "no run inserted; events carry a run"
            # R1 (correction round 2): a commissioning payload
            # that names a different run than the event's own
            # run is refused at the door of the record — the
            # two bindings can never disagree in a recorded
            # history.
            if type_ == "RUN_COMMISSIONED" and \
                    payload.get("run_id") not in (None, run_id):
                raise AssertionError(
                    f"RUN_COMMISSIONED payload run "
                    f"{payload.get('run_id')!r} disagrees with "
                    f"the event's run {run_id!r} (R1)")
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
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                    time.gmtime()),
                "prev_hash": prev_hash,
            }
            event["hash"] = event_hash(prev_hash, event)
            self._conn.execute(
                "INSERT INTO events (event_seq, event_id, run_id,"
                " type, actor, affected, payload, ts, prev_hash,"
                " hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (seq, event["event_id"], run_id, type_, actor,
                 json.dumps(event["affected"]),
                 json.dumps(event["payload"]),
                 event["ts"], prev_hash, event["hash"]),
            )
            return event

    def commit(self):
        with self._lock:
            self._conn.commit()

    def rollback(self):
        with self._lock:
            self._conn.rollback()

    def all_events(self):
        with self._lock:
            rows = self._conn.execute(
                "SELECT event_seq, event_id, run_id, type, actor,"
                " affected, payload, ts, prev_hash, hash FROM"
                " events ORDER BY event_seq"
            ).fetchall()
            out = []
            for seq, eid, run_id, typ, actor, affected, payload, \
                    ts, prev, h in rows:
                out.append({
                    "event_seq": seq, "event_id": eid,
                    "run_id": run_id, "type": typ, "actor": actor,
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
        "instance_onboarding": {},  # instance_id -> the same
                              # record shape as a seat's, plus the
                              # seat slot and assembly it belongs
                              # to (Piece A1, R38: per-instance
                              # onboarding, kept beside the
                              # per-seat state; neither rewrites
                              # the other)
        "tool_requests": [],  # the instance tool requests, in
                              # record order (Piece A2, R47): each
                              # entry binds (instance_id,
                              # request_id) to the canonical
                              # fingerprint of its tool +
                              # parameters at first presentation,
                              # and names its dispatch once one
                              # stands. A retry folds to the
                              # standing entry; an identity never
                              # changes its meaning in the fold.
        "loop_activations": {},  # assembly_id -> the
                              # activation's loop standing (Piece
                              # A3, R49/R50): the binding ids, the
                              # recorded iterations in order (each
                              # with its governing bounds and the
                              # cursor range its package
                              # presented), and the stall where one
                              # stands — the first stall stands; a
                              # second is history for the checker
        "dispatches": {},     # dispatch_id -> the dispatch's
                              # standing (Piece A2, R45/R46): its
                              # request binding, the intent's
                              # position, the start's position
                              # where one stands, the standing
                              # outcome and its position, the
                              # position uncertainty was recorded
                              # where it was, and the
                              # reconciliation's position and
                              # established outcome where the
                              # examiner has reconciled it
        "assemblies": {},     # assembly_id -> the assembly's
                              # lifecycle standing (Piece A1, R40):
                              # the binding ids, each act's
                              # position (first-wins, like a case
                              # version's), the judged and sealed
                              # hashes, and the credential state
                              # the doorway derives — "none" before
                              # pack, "prepared" at pack, "active"
                              # only at INSTANCE_ACTIVATED (R39)
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
        "gate_declaration": {},  # joint -> kind, as commissioned
                              # (R21; Piece 6 gates — the derived
                              # gate_set and waiting states are
                              # computed over this fold by gates.py)
        "gates_present": False,  # whether the commission carried
                              # a gates field at all (G7, correction
                              # round 1: an explicitly empty
                              # declaration is a declaration — only
                              # a genuinely absent field takes the
                              # compatibility path)
        "completion_claim_seq": None,  # event_seq of the latest
                              # COMPLETION_CLAIMED (Piece 6 gates,
                              # §3.8's claim binding by position)
        "holder_unavailable": [],  # {joint, by, event_seq} —
                              # HOLDER_UNAVAILABLE declarations
                              # (R33; Piece 6 gates, §3.6)
        "commission_seq": None,  # the RUN_COMMISSIONED event's
                              # position (§3.8: a proposal answers
                              # an exact commission, by reference)
        "assembly_proposals": [],  # {event_seq, crew,
                              # proposal_kind} (R26; Piece A1
                              # correction round 1: the proposal
                              # discriminator — "instance" for a
                              # generated instance's proposal,
                              # "run" for the §3.8 gate proposal;
                              # a payload carrying no
                              # discriminator folds as "run", so
                              # pre-discriminator histories read
                              # exactly as they always did)
        "assembly_records": [],  # {event_seq, proposal_seq,
                              # gate_set} (R35)
        "run_ready_seq": None,  # the latest
                              # RUN_READY_FOR_COMPLETION position
                              # (§3.8: the declaration the
                              # completion gate answers)
        "completion_claims": [],  # {event_seq, by, tree_part} —
                              # every COMPLETION_CLAIMED (the
                              # readiness floor and the derived
                              # claims_by_part read these)
        "routing_notes": [],  # {disagreement_id, joint, event_seq,
                              # by} — validated routing notes;
                              # orchestrator.py derives the current
                              # route per disagreement (§3.8)
        "uncased": {},        # tree_part -> [contribution_id] —
                              # contributions recorded with no
                              # effective case standing for their
                              # seat and part AT their position
                              # (§3.8, S6: position-sensitive; a
                              # later case never recases them)
        "pre_ack": {},        # tree_part -> [contribution_id] —
                              # contributions recorded under a
                              # standing case not yet acknowledged
                              # by their seat (the R32 state) — a
                              # separate fact from uncased, never
                              # folded into it (§3.8, S6)
        "head_seq": 0,
    }


def _case_status_at(state, seat_id, part):
    """Whether an effective case stands for (seat, part) in the
    fold AS IT STANDS NOW — which, called from within a fold
    step, is the record as of the event being folded: the
    position-sensitive reading §3.8's uncased derivation needs.
    Returns (cased, acknowledged).

    The governing case is the seat's EFFECTIVE case at this
    position — selected by effective_case() itself, run over
    the fold as it stands at the contribution's own step
    (§3.8 correction rounds 1–3). One selection rule, shared
    by the fold and the driver by construction, so the
    record's account of which case governed a contribution
    cannot diverge from the case the seat was actually given:
    the highest issued version across all of the seat's case
    lineages (the earliest-standing lineage holding a version
    tie), judged for part coverage and acknowledgement as
    that version alone. A superseding version — whether a
    correction within a lineage or a higher version in
    another — retires what it supersedes entirely, including
    its coverage of its old part; an earlier version's
    acknowledgement never carries forward."""
    eff = effective_case(state, seat_id)
    if eff is None or not eff.get("content"):
        return False, False
    if eff["content"].get("part") != part:
        return False, False
    return True, bool(eff["acknowledged"])


def _subject_changed_parts(payload):
    part = payload.get("tree_part")
    return part


def _apply_instance_onboarding(state: dict, ev: dict):
    """One fold step for an instance-subject ONBOARDING (Piece
    A1, R38). The first onboarding establishes the instance's
    record — declaration verbatim, provider-reported id as its
    own claim, capability, limits, terms — and is never replaced
    or rewritten. A later onboarding carrying an attestation
    reference may raise the status only, exactly as a seat's
    attestation does; the original declaration stands untouched
    and the attestation is preserved as the upgrade's
    provenance."""
    p = ev["payload"]
    iid = p.get("instance_id")
    rec = state["instance_onboarding"].get(iid)
    if rec is None:
        state["instance_onboarding"][iid] = {
            "declaration": p.get("declaration"),
            "provider_model_id": p.get("provider_model_id"),
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
            "seat": p.get("seat_id"),
            "assembly_id": p.get("assembly_id"),
        }
    elif p.get("attestation_ref"):
        rank = {"unverified": 0, "declared": 1,
                "provider-confirmed": 2}
        new = p.get("identity_status")
        if new in rank and rank[new] > rank.get(
                rec["identity_status"], 0):
            rec["identity_status"] = new
            rec["attestation"] = {
                "event_seq": ev["event_seq"],
                "attestation_ref": p["attestation_ref"]}


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
        state["commission_seq"] = ev["event_seq"]
        # R30: the commissioned tree (part -> downstream dependents)
        # is the record the doorway computes paused sets from.
        state["tree"] = dict(p.get("tree", {}))
        # R21: the commissioned gate declaration (joint -> kind),
        # carried verbatim; gates.py derives its validity and the
        # waiting states over the fold (Piece 6 gates, §3.1).
        # Presence is preserved independently of contents (G7,
        # correction round 1): "gates": {} is an incomplete
        # declaration that enforces and fails closed; only a
        # commission with no gates field at all is undeclared.
        raw_gates = p.get("gates")
        state["gates_present"] = raw_gates is not None
        state["gate_declaration"] = dict(raw_gates) \
            if isinstance(raw_gates, dict) else {}
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
        if p.get("subject") == "instance":
            # Piece A1 (R38): an instance's onboarding, keyed by
            # instance — a separate state from the seats', with
            # the same first-wins establishment and attested
            # raise-only discipline.
            _apply_instance_onboarding(state, ev)
            return state
        seat = p["seat_id"]
        rec = state["onboarding"].get(seat)
        if rec is None:
            state["onboarding"][seat] = {
                "declaration": p.get("declaration"),
                "provider_model_id": p.get("provider_model_id"),
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
        # §3.8 (S6): case provenance is evaluated HERE, at the
        # contribution's own position, over the fold as it stands
        # at this step — a case issued later never recases this
        # contribution, and supersession later never uncases it.
        # Uncased and pre-acknowledgement are separate facts and
        # are derived separately, neither folded into the other.
        cased, acknowledged = _case_status_at(
            state, actor, p.get("tree_part"))
        key = p.get("tree_part") or "(job)"
        if not cased:
            state["uncased"].setdefault(key, []).append(cid)
        elif not acknowledged:
            state["pre_ack"].setdefault(key, []).append(cid)
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
        # Piece 6 gates (§3.4): a ruling names its gate and the
        # action it permits; the doorway's ruling mechanics and
        # the derived waiting states read both from the record.
        state["rulings"].append({"by": actor,
                                  "event_seq": ev["event_seq"],
                                  "joint": p.get("joint"),
                                  "action": p.get("action")})
    elif t == "DISPOSITION":
        state["dispositions"].append({"by": actor,
                                       "event_seq": ev["event_seq"]})
    elif t == "MATERIAL_SEALED":
        state["sealed"][p["material_id"]] = list(p.get("boundary", []))
    elif t == "REJECTION":
        state["rejections"].append({
            "seat": p.get("seat"), "attempted": p.get("attempted_type"),
            "ground": p.get("ground"), "event_seq": ev["event_seq"],
            "part": p.get("part"),
        })
    elif t == "HOLDER_UNAVAILABLE":
        # R33 (Piece 6 gates, §3.6): an orchestrator's declaration
        # that a gate's holder is unavailable. It pauses nothing
        # and requires no ruling; gates.py derives the waiting
        # state from these declarations, cleared by a recorded
        # GATE_OUTCOME at the joint.
        state["holder_unavailable"].append({
            "joint": p.get("joint"), "by": actor,
            "event_seq": ev["event_seq"],
        })
    elif t == "COMPLETION_CLAIMED":
        state["lifecycle"] = "completion_claimed"
        state["lifecycle_seq"] = ev["event_seq"]
        # Piece 6 gates (§3.8): the completion sequence binds by
        # position — only an outcome recorded after the latest
        # claim answers it.
        state["completion_claim_seq"] = ev["event_seq"]
        state["completion_claims"].append({
            "event_seq": ev["event_seq"], "by": actor,
            "tree_part": p.get("tree_part"),
        })
    elif t == "ASSEMBLY_PROPOSED":
        # R26: the orchestrator's proposal, a recorded act. The
        # fold carries the crew it proposed; the tree and gates it
        # adopts stand in the commission it references.
        # Piece A1 correction round 1: the event kind is shared —
        # a §3.8 run-level gate proposal and an A1 instance
        # proposal both record as ASSEMBLY_PROPOSED — so the fold
        # carries the payload's proposal discriminator,
        # normalised here: only an explicit "instance" marks an
        # instance proposal; absence (every pre-discriminator
        # history) is a run-level proposal.
        state["assembly_proposals"].append({
            "event_seq": ev["event_seq"],
            "crew": p.get("crew"),
            "proposal_kind": "instance"
            if p.get("proposal_kind") == "instance" else "run",
        })
    elif t == "ASSEMBLY_RECORD":
        # R35: the examiner's assembly record, bound to the exact
        # proposal it examines. gates.py derives the operative
        # gate set from the record bound to the latest proposal.
        state["assembly_records"].append({
            "event_seq": ev["event_seq"],
            "proposal_seq": p.get("proposal_seq"),
            "gate_set": dict(p.get("gate_set") or {}),
        })
    elif t == "ASSEMBLY_GENERATED":
        # Piece A1 (R37): the generated assembly — the fold
        # opens its lifecycle entry. The record's contents ride
        # on the event; the entry carries the binding ids and
        # the positions the later acts fill in, first-wins like
        # a case version's route positions: a second act of a
        # kind stands in the history but never replaces the
        # standing position. Whether the acts were *allowed* is
        # the doorway's enforcement; the checker verifies the
        # correspondence independently.
        state["assemblies"][p.get("assembly_id")] = {
            "instance_id": p.get("instance_id"),
            "seat": p.get("seat"),
            "part": p.get("part"),
            "case_id": p.get("case_id"),
            "case_version": p.get("case_version"),
            "proposal_seq": p.get("proposal_seq"),
            "onboarding_seq": p.get("onboarding_seq"),
            "generated_seq": ev["event_seq"],
            "probed_seq": None,
            "verified_seq": None, "judged_seq": None,
            "judged_hash": None,
            "packed_seq": None, "pack_hash": None,
            "authorised_seq": None, "activated_seq": None,
            "credential": "none",
            "grants_present": p.get("grants") is not None,
            # Piece A3-CAT, correction round: the generated
            # record's catalogue-contract declaration, carried
            # on the entry — "a3-cat" where the assembly is
            # governed by the contract, None on records that
            # predate it.
            "catalogue_contract": p.get("catalogue_contract"),
        }
    elif t in ("ASSEMBLY_PROBED", "ASSEMBLY_VERIFIED",
               "ASSEMBLY_JUDGED", "ASSEMBLY_PACKED",
               "ASSEMBLY_ISSUE_AUTHORISED", "INSTANCE_ACTIVATED"):
        # Piece A1 (R39/R40): the assembly's later acts, each
        # filling its own position on the generated entry. The
        # probe act (native-mode probe piece) fills probed_seq
        # the same way, between generation and verification.
        entry = state["assemblies"].get(p.get("assembly_id")
                                         or "")
        if entry is not None:
            if t == "ASSEMBLY_PROBED" and \
                    entry["probed_seq"] is None:
                entry["probed_seq"] = ev["event_seq"]
            elif t == "ASSEMBLY_VERIFIED" and \
                    entry["verified_seq"] is None:
                entry["verified_seq"] = ev["event_seq"]
            elif t == "ASSEMBLY_JUDGED" and \
                    entry["judged_seq"] is None:
                entry["judged_seq"] = ev["event_seq"]
                entry["judged_hash"] = p.get("record_hash")
            elif t == "ASSEMBLY_PACKED" and \
                    entry["packed_seq"] is None:
                entry["packed_seq"] = ev["event_seq"]
                entry["pack_hash"] = p.get("record_hash")
                entry["credential"] = "prepared"
            elif t == "ASSEMBLY_ISSUE_AUTHORISED" and \
                    entry["authorised_seq"] is None:
                entry["authorised_seq"] = ev["event_seq"]
            elif t == "INSTANCE_ACTIVATED" and \
                    entry["activated_seq"] is None:
                entry["activated_seq"] = ev["event_seq"]
                entry["credential"] = "active"
    elif t == "TOOL_REQUESTED":
        # Piece A2 (R47): the first presentation binds the
        # identity — (instance_id, request_id) — to the
        # fingerprint of its tool and parameters. A later
        # request event carrying the same identity folds to
        # the standing entry: the binding the record derives
        # never changes its meaning. (Whether a re-presentation
        # with different contents was refused is the doorway's
        # enforcement; that it must not stand as a second
        # meaning is the fold's, and the checker verifies the
        # events themselves.)
        key = (p.get("instance_id"), p.get("request_id"))
        if not any((r["instance_id"], r["request_id"]) == key
                   for r in state["tool_requests"]):
            state["tool_requests"].append({
                "instance_id": p.get("instance_id"),
                "request_id": p.get("request_id"),
                "fingerprint": p.get("fingerprint"),
                "tool": p.get("tool"),
                "requested_seq": ev["event_seq"],
                "dispatch_id": None,
            })
    elif t == "TOOL_DISPATCHED":
        # Piece A2 (R45): the doorway's recorded intent. The
        # entry opens in the `intent` state — the event means
        # the framework authorised and committed a dispatch,
        # never that execution began. The request it answers
        # names the dispatch (first dispatch wins the binding;
        # a second stands in the history for the checker to
        # report, and never displaces the first).
        entry = {
            "instance_id": p.get("instance_id"),
            "request_id": p.get("request_id"),
            "tool": p.get("tool"),
            "dispatch_seq": ev["event_seq"],
            "started_seq": None, "outcome": None,
            "outcome_seq": None, "uncertain_seq": None,
            "reconciled_seq": None, "reconciled_outcome": None,
        }
        state["dispatches"][p.get("dispatch_id")] = entry
        for req in state["tool_requests"]:
            if (req["instance_id"], req["request_id"]) == \
                    (p.get("instance_id"), p.get("request_id")) \
                    and req["dispatch_id"] is None:
                req["dispatch_id"] = p.get("dispatch_id")
    elif t == "TOOL_STARTED":
        # Piece A2: the executor's narrow report — execution
        # established as begun for this dispatch. First start
        # wins; a second stands in the history and replaces
        # nothing.
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None and entry["started_seq"] is None:
            entry["started_seq"] = ev["event_seq"]
    elif t == "TOOL_OUTCOME":
        # Piece A2 (R46): the executor's outcome report. The
        # first outcome stands — with one deliberate exception:
        # an `uncertain` outcome is not a settlement, so a
        # later attributable report of result or failure (the
        # delayed report, distinct from reconciliation) settles
        # the dispatch, the uncertainty's position preserved
        # beside it. A settled dispatch — result, failure, or
        # reconciled — takes no further outcome in the fold.
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None:
            outcome = p.get("outcome")
            if entry["outcome"] is None:
                entry["outcome"] = outcome
                entry["outcome_seq"] = ev["event_seq"]
                if outcome == "uncertain":
                    entry["uncertain_seq"] = ev["event_seq"]
            elif entry["outcome"] == "uncertain" and \
                    entry["reconciled_seq"] is None and \
                    outcome in ("result", "failure"):
                entry["outcome"] = outcome
                entry["outcome_seq"] = ev["event_seq"]
    elif t == "TOOL_RECONCILED":
        # Piece A2 (R46): the examiner's determination settles
        # an uncertain dispatch — only an uncertain one, and
        # only once; a settled dispatch reconciles no further
        # in the fold whatever stands in the history.
        entry = state["dispatches"].get(p.get("dispatch_id")
                                         or "")
        if entry is not None and \
                entry["outcome"] == "uncertain" and \
                entry["reconciled_seq"] is None:
            entry["reconciled_seq"] = ev["event_seq"]
            entry["reconciled_outcome"] = p.get("outcome")
    elif t == "LOOP_ITERATION":
        # Piece A3 (R49): the loop machinery's bookkeeping —
        # one event per model call, recorded before the call,
        # carrying the activation's binding, the governing
        # bounds as pinned, and the cursor range the iteration's
        # package presented — and, from Piece A3-CAT, the tool
        # catalogue's canonical hash and the registry version
        # it was derived under, where the event carries them.
        # The fold collects them per
        # activation, in record order; ordering, uniqueness and
        # the ceiling are the checker's correspondence, and the
        # doorway's route enforces them at record time.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        entry["iterations"].append({
            "iteration": p.get("iteration"),
            "event_seq": ev["event_seq"],
            "step_ceiling": p.get("step_ceiling"),
            "deadline_seconds": p.get("deadline_seconds"),
            "cursor_from": p.get("cursor_from"),
            "cursor_to": p.get("cursor_to"),
            "catalogue_hash": p.get("catalogue_hash"),
            "registry_version": p.get("registry_version"),
            "call_entered_seq": None,
            "disposition_seq": None,
            "disposition_outcome": None,
            "translation_seq": None,
        })
    elif t == "CALL_ENTERED":
        # Response-evidence piece (R5-2/R6-2): the call
        # boundary for one iteration. The fold marks the
        # iteration entry the payload names (by its
        # LOOP_ITERATION event seq); the first boundary
        # stands — a second is history for the checker.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["call_entered_seq"] is None:
                        it["call_entered_seq"] = ev["event_seq"]
                    break
    elif t == "RESPONSE_EVIDENCE":
        # Response-evidence piece (R3-1/R7-2): the
        # iteration's response disposition. The first
        # disposition stands in the fold; a second is
        # history for the checker to report, and replaces
        # nothing — a committed disposition is final.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["disposition_seq"] is None:
                        it["disposition_seq"] = ev["event_seq"]
                        it["disposition_outcome"] = \
                            p.get("outcome")
                    break
    elif t == "TRANSLATION_RECORDED":
        # Native adapter piece (N32): the iteration's
        # translation record. The fold marks the iteration
        # entry the payload names (by its LOOP_ITERATION
        # event seq); the first translation record stands —
        # a second is history for the checker, and replaces
        # nothing: the decision set, once committed, is the
        # set the iteration's dispatches answer to.
        entry = state["loop_activations"].get(
            p.get("assembly_id"))
        if entry is not None:
            for it in entry["iterations"]:
                if it["event_seq"] == p.get("iteration_seq"):
                    if it["translation_seq"] is None:
                        it["translation_seq"] = ev["event_seq"]
                    break
    elif t == "EVIDENCE_CAPTURE_FAILED":
        # Response-evidence piece (R8-2): the evidence
        # mechanism's own failure terminal. The first
        # stands; it discharges no disposition obligation
        # — the named iteration's entry keeps its missing
        # disposition, for the checker to report.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        if entry["evidence_failed"] is None:
            entry["evidence_failed"] = {
                "event_seq": ev["event_seq"],
                "iteration_seq": p.get("iteration_seq"),
                "operation": p.get("operation"),
            }
    elif t == "LOOP_STALLED":
        # Piece A3 (R50): the recorded stop. The first stall
        # stands in the fold; a second stands in the history
        # for the checker to report, and replaces nothing.
        entry = state["loop_activations"].setdefault(
            p.get("assembly_id"), {
                "instance_id": p.get("instance_id"),
                "activated_seq": p.get("activated_seq"),
                "case_id": p.get("case_id"),
                "case_version": p.get("case_version"),
                "iterations": [], "stalled": None,
                "evidence_failed": None})
        if entry["stalled"] is None:
            entry["stalled"] = {
                "ground": p.get("ground"),
                "event_seq": ev["event_seq"],
                "iterations": p.get("iterations"),
                "terminal_step": p.get("terminal_step"),
            }
    elif t == "RUN_READY_FOR_COMPLETION":
        # §3.8 (S5): the orchestrator's readiness declaration —
        # the act the completion gate answers. The crew's claims
        # stand separately, above; neither impersonates the other.
        state["run_ready_seq"] = ev["event_seq"]
    elif t == "COMMENT":
        # §3.8 (S4): a validated routing note. The fold carries
        # the note's referents; orchestrator.py derives the
        # current route per disagreement (latest valid route).
        if p.get("routes_disagreement") and p.get("to_gate"):
            state["routing_notes"].append({
                "disagreement_id": p.get("routes_disagreement"),
                "joint": p.get("to_gate"),
                "event_seq": ev["event_seq"], "by": actor,
            })
    elif t == "RUN_CLOSED":
        state["lifecycle"] = "closed"
        state["lifecycle_seq"] = ev["event_seq"]
    # A COMMENT with no routing referents is a recorded act the
    # fold carries in the history without derived state of its own.
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
