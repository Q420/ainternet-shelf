"""Watchdog Stage 2 — the ledger.

Built from the shelved Stage 1 contract v1.1 (Q420/ainternet-shelf,
branch pin 63d05299, sha256 5a83821c...; copy on main at
claude/WATCHDOG-STAGE1-CONTRACT-v1.1.md). Implements contract §2
(registry validation), §5 (packet shape, as stored), §6 (persisted
streak), §8 (ledger + acknowledgement). The detector, judge,
scheduler and wake are later stages and are NOT here: this module
never reads a page, never calls a model, never sends anything.

State lives in one JSON document written atomically (temp file,
fsync, rename) on every mutation (§8). Operational notes that are
not events — duplicate suppressions, judge errors, alerts raised —
go to an append-only ops log; stale-window alerts in particular
never enter the ledger (§9).
"""

import copy
import json
import os
import tempfile
import time

SCHEMA_VERSION = "1"
V1_SEATS = {"chatgpt", "this-seat"}

# Owner-tunable configuration (§11). These defaults are
# placeholders until the owner sets real values; every consumer
# takes them from config, never from a literal in logic.
DEFAULT_CONFIG = {
    "alert_age_s": 3600,        # unacked event older than this alerts
    "cooldown_default_s": 0,    # per-job cooldown after ack
    "cooldown_by_job": {},      # job_id -> seconds
    "stale_interval_s": 600,    # §9, consumed by the monitor stage
}


class RegistryError(Exception):
    """Registry load failure (§2): no job starts."""


class PacketError(Exception):
    """An event packet that does not meet §5 may not be recorded."""


# ----------------------------------------------------------------
# Registry (§2, §3)
# ----------------------------------------------------------------

JOB_FIELDS = {
    "job_id": str,
    "seat_id": str,
    "conversation_id": str,
    "task": str,
    "declared_precondition": str,
    "depends_on": list,
    "priority": int,
    "state": str,
}
JOB_STATES = {"active", "resolved", "retired"}


def _job_hash(job):
    """Hash of a job record EXCLUDING assigned_turn_index
    (owner ruling on verdict M3, 2026-11-15, for contract
    v1.2): the index is a set-once field — §2 fills it after
    activation, so it is pinned separately (see
    _pin_active_jobs) and the rest of the record is pinned
    whole."""
    import hashlib
    body = {k: v for k, v in job.items()
            if k != "assigned_turn_index"}
    canon = json.dumps(body, sort_keys=True).encode()
    return hashlib.sha256(canon).hexdigest()


def _atomic_write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path),
                               prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, indent=1, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp, path)
        _fsync_dir(os.path.dirname(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _fsync_dir(dirpath):
    """Fsync a directory so a rename inside it is durable
    (verdict S3)."""
    try:
        dfd = os.open(dirpath or ".", os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except OSError:
        pass


def load_registry(path, state_dir):
    """Load and validate the registry. Any §2 failure raises
    RegistryError and nothing starts: unknown depends_on target,
    dependency cycle, duplicate job_id, seat outside the v1 set.
    Returns {job_id: job record}.

    assigned_turn_index is NOT required at load (verdict S5):
    §2 fills it on assignment confirmation, so a job may be
    registered before that; when present it must be an int.

    gate_terms (§3 as amended by v1.3) is likewise optional
    at load: absent means no keyword gate. When present it
    must be a list of strings; it is normalized into the
    loaded record and pinned with it (see below).

    state_dir is required (resubmission-2 verdict M5 — the
    pin must never be skippable, the same class of gap as M4):
    immutability is enforced across
    loads (verdict S2): each active job's record hash is pinned
    on first sight, and a later load whose active record hashes
    differently fails — an active record is never edited (§2);
    a change is a new job_id."""
    with open(path) as f:
        raw = json.load(f)
    jobs = raw.get("jobs") if isinstance(raw, dict) else raw
    if not isinstance(jobs, list):
        raise RegistryError("registry must be a list of jobs "
                            "(or an object with a 'jobs' list)")
    out = {}
    for job in jobs:
        if not isinstance(job, dict):
            raise RegistryError("job record is not an object")
        for field, typ in JOB_FIELDS.items():
            if field not in job:
                raise RegistryError(
                    f"job missing field {field!r}: {job!r}")
            if not isinstance(job[field], typ) or (
                    typ is int and isinstance(job[field], bool)):
                raise RegistryError(
                    f"job {job.get('job_id')!r}: field {field!r} "
                    f"must be {typ.__name__}")
        ati = job.get("assigned_turn_index")
        if ati is not None and (not isinstance(ati, int)
                                or isinstance(ati, bool)):
            raise RegistryError(
                f"job {job.get('job_id')!r}: field "
                f"'assigned_turn_index' must be int")
        # gate_terms (§3 as amended by v1.3): the keyword
        # gate's terms, an OPTIONAL field — a record without
        # it predates v1.3 and still loads, treated as no
        # gate. When present it must be a list of strings.
        # It is normalized here (absent/null -> []) BEFORE
        # the §2 pin is computed in _pin_active_jobs, and
        # _job_hash covers the whole record, so the terms
        # are pinned with the record exactly like every
        # other field — NOT a set-once side field: changing
        # them on an active job fails the pin, and the
        # change is a new job_id.
        gt = job.get("gate_terms")
        if gt is None:
            job["gate_terms"] = []
        elif not isinstance(gt, list) or not all(
                isinstance(t, str) for t in gt):
            raise RegistryError(
                f"job {job.get('job_id')!r}: field "
                f"'gate_terms' must be a list of strings")
        elif any(not t.strip() for t in gt):
            # an empty or whitespace-only term matches every
            # turn, so the gate would silently pass everything
            # while looking like a gate (Stage 3 gate-rebuild
            # review should-fix)
            raise RegistryError(
                f"job {job.get('job_id')!r}: field "
                f"'gate_terms' must not contain empty or "
                f"whitespace-only terms")
        else:
            job["gate_terms"] = list(gt)
        jid = job["job_id"]
        if jid in out:
            raise RegistryError(f"duplicate job_id: {jid!r}")
        if job["seat_id"] not in V1_SEATS:
            raise RegistryError(
                f"job {jid!r}: seat {job['seat_id']!r} not in "
                f"the v1 seat set")
        if job["state"] not in JOB_STATES:
            raise RegistryError(
                f"job {jid!r}: unknown state {job['state']!r}")
        out[jid] = job
    for jid, job in out.items():
        for dep in job["depends_on"]:
            if dep not in out:
                raise RegistryError(
                    f"job {jid!r} depends on unknown job {dep!r}")
    _reject_cycles(out)
    _pin_active_jobs(out, state_dir)
    return out


def _pin_active_jobs(jobs, state_dir):
    os.makedirs(state_dir, exist_ok=True)
    pin_path = os.path.join(state_dir, "registry-pins.json")
    pins = {}
    if os.path.exists(pin_path):
        with open(pin_path) as f:
            pins = json.load(f)
    changed = False
    for jid, job in jobs.items():
        if job["state"] != "active":
            continue
        h = _job_hash(job)
        ati = job.get("assigned_turn_index")
        pin = pins.get(jid)
        if isinstance(pin, str):  # pre-v1.2 pin format
            pin = {"record": pin, "ati": None}
        if pin is not None:
            if pin["record"] != h:
                raise RegistryError(
                    f"active job {jid!r} record changed since "
                    f"it was pinned — active records are "
                    f"immutable (§2); a change is a new job_id")
            if pin.get("ati") is not None and ati != pin["ati"]:
                raise RegistryError(
                    f"active job {jid!r}: assigned_turn_index "
                    f"is set-once — pinned at {pin['ati']}, "
                    f"registry now says {ati}")
            if pin.get("ati") is None and ati is not None:
                pin = {"record": h, "ati": ati}
                pins[jid] = pin
                changed = True
        else:
            pins[jid] = {"record": h, "ati": ati}
            changed = True
    if changed:
        _atomic_write_json(pin_path, pins)


def _reject_cycles(jobs):
    """Depth-first cycle check over depends_on (§2b: rejected,
    not warned)."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {jid: WHITE for jid in jobs}

    def visit(jid, trail):
        colour[jid] = GREY
        for dep in jobs[jid]["depends_on"]:
            if colour[dep] == GREY:
                raise RegistryError(
                    "dependency cycle: "
                    + " -> ".join(trail + [jid, dep]))
            if colour[dep] == WHITE:
                visit(dep, trail + [jid])
        colour[jid] = BLACK

    for jid in jobs:
        if colour[jid] == WHITE:
            visit(jid, [])


# ----------------------------------------------------------------
# Event packet (§5) — validation on write
# ----------------------------------------------------------------

PACKET_FIELDS = (
    "schema_version", "event_id", "ledger_key", "job_id",
    "seat_id", "window_id", "declared_precondition",
    "trigger_reason", "candidate_turn_ids", "turn_index_range",
    "judge_results", "judge_model", "judge_prompt_hash",
    "buffer_window_bounds", "relevant_buffer_slice",
    "dependency_state", "detected_at", "priority",
)


def ledger_key_for(job_id, seat_id, conversation_id, turn_key):
    """§5: job_id + '|' + seat_id + '|' + conversation_id + '|'
    + turn_key, where turn_key is the structural identity of the
    FIRST qualifying turn."""
    return "|".join([job_id, seat_id, conversation_id, turn_key])


def validate_packet(packet):
    if not isinstance(packet, dict):
        raise PacketError("packet is not an object")
    for field in PACKET_FIELDS:
        if field not in packet:
            raise PacketError(f"packet missing field {field!r}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise PacketError(
            f"schema_version must be {SCHEMA_VERSION!r}")
    if packet["trigger_reason"] != "two_consecutive_yes":
        raise PacketError("trigger_reason must be "
                          "'two_consecutive_yes'")
    results = packet["judge_results"]
    if not isinstance(results, list) or len(results) != 2:
        raise PacketError("judge_results must hold exactly the "
                          "two qualifying turns")
    for r in results:
        # §7: errors never appear here as a result.
        if r not in ("YES", "NO"):
            raise PacketError(
                f"judge_results entry is not YES/NO: {r!r}")
    if results != ["YES", "YES"]:
        raise PacketError("a recorded event requires two "
                          "consecutive YES results")
    cands = packet["candidate_turn_ids"]
    if not isinstance(cands, list) or len(cands) != 2:
        raise PacketError("candidate_turn_ids must hold the two "
                          "qualifying turns")
    return True


# ----------------------------------------------------------------
# The ledger (§8) + persisted streak (§6)
# ----------------------------------------------------------------

class Ledger:
    def __init__(self, state_dir, config=None, registry=None):
        # The registry is REQUIRED (verdict M4): the M2 packet
        # check must never be skippable on a production path,
        # so a ledger cannot be constructed without the loaded
        # registry it checks against.
        if registry is None:
            raise ValueError(
                "Ledger requires the loaded registry — the "
                "packet-vs-registry check (M2) is not optional")
        self.dir = state_dir
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, "ledger.json")
        self.ops_path = os.path.join(self.dir, "ops-log.jsonl")
        self.config = dict(DEFAULT_CONFIG)
        if config:
            self.config.update(config)
        self.registry = registry
        self.state = self._load()

    # -- persistence: one document, atomic writes (§8) ---------

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                state = json.load(f)
            state.setdefault("events", {})
            state.setdefault("streaks", {})
            state.setdefault("cooldown_until", {})
            state.setdefault("alerts_raised", {})
            return state
        return {"events": {}, "streaks": {},
                "cooldown_until": {}, "alerts_raised": {}}

    def _save(self):
        fd, tmp = tempfile.mkstemp(dir=self.dir,
                                   prefix="ledger-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(self.state, f, indent=1,
                          sort_keys=True)
                f.flush()
                os.fsync(f.fileno())
            os.rename(tmp, self.path)
            _fsync_dir(self.dir)  # the rename itself durable (S3)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def _ops(self, kind, **fields):
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "kind": kind}
        rec.update(fields)
        with open(self.ops_path, "a") as f:
            f.write(json.dumps(rec) + "\n")

    # -- restart (§8): re-offer, never re-create ----------------

    def unacknowledged(self):
        """Events in state 'unacknowledged', oldest first. On
        restart these are re-offered to the orchestrator; no
        event is ever re-created."""
        evs = [copy.deepcopy(e)
               for e in self.state["events"].values()
               if e["state"] == "unacknowledged"]
        return sorted(evs, key=lambda e: e["detected_at"])

    # -- read accessors (Stage 4 review S-S4-2) ----------------
    # Public reads over the ledger's state, so consumers (the
    # scheduler, the detector) never touch self.state and are
    # not coupled to the storage layout. Returned events are
    # deep copies, as everywhere in this class.

    def events_for_job(self, job_id):
        """Every event recorded for the job, oldest first."""
        evs = [copy.deepcopy(e)
               for e in self.state["events"].values()
               if e["job_id"] == job_id]
        return sorted(evs, key=lambda e: e["detected_at"])

    def unacknowledged_for_job(self, job_id):
        """The job's unacknowledged event — the §8 ack lock's
        blocker — or None when the job has none."""
        for e in self.state["events"].values():
            if (e["job_id"] == job_id
                    and e["state"] == "unacknowledged"):
                return copy.deepcopy(e)
        return None

    def has_acknowledged_event(self, job_id):
        """True when any event for the job has ever been
        acknowledged — the §10 dependency-resolution test:
        resolution is "any acknowledged event ever", so a
        later unacknowledged event does not un-resolve it."""
        return any(
            e["job_id"] == job_id
            and e["state"] == "acknowledged"
            for e in self.state["events"].values())

    def cooldown_until(self, job_id):
        """When the job's post-acknowledgement cooldown ends
        (epoch seconds), or 0 when none is standing."""
        return self.state["cooldown_until"].get(job_id, 0)

    # -- events (§8) ---------------------------------------------

    def record_event(self, packet):
        """Record a detection. Returns (outcome, event) where
        outcome is 'recorded', 'duplicate' (same ledger_key —
        suppressed and logged, §8) or 'locked' (the job already
        has an unacknowledged event — no new event may be
        created). A recorded event consumes the job's streak:
        the qualifying pair is spent into the event, so the
        next fire needs a fresh pair."""
        validate_packet(packet)
        # M2 (verdict): the packet must match the registry —
        # the job exists, is active, and seat/window are as
        # registered (§5: "as registry"). The registry is a
        # required constructor argument (M4), so this check
        # always runs.
        job = self.registry.get(packet["job_id"])
        if job is None:
            raise PacketError(
                f"unknown job_id: {packet['job_id']!r}")
        if job["state"] != "active":
            raise PacketError(
                f"job {packet['job_id']!r} is not active")
        if packet["seat_id"] != job["seat_id"]:
            raise PacketError(
                "packet seat_id does not match the registry")
        if packet["window_id"] != job["conversation_id"]:
            raise PacketError(
                "packet window_id does not match the registry")
        # M1 (verdict): the ledger_key is never taken on
        # faith — it is derived from the packet's own fields
        # (§5 formula, turn_key = first candidate's id) and
        # any mismatch is rejected.
        expected = ledger_key_for(
            packet["job_id"], packet["seat_id"],
            packet["window_id"], packet["candidate_turn_ids"][0])
        if packet["ledger_key"] != expected:
            raise PacketError(
                f"ledger_key mismatch: packet carries "
                f"{packet['ledger_key']!r}, derived {expected!r}")
        key = packet["ledger_key"]
        if key in self.state["events"]:
            self._ops("duplicate_suppressed", ledger_key=key,
                      job_id=packet["job_id"])
            return "duplicate", copy.deepcopy(
                self.state["events"][key])
        # M1, second half: the same candidate pair under any
        # key is the same detection — suppressed, so one pair
        # of turns can never produce two events.
        for e in self.state["events"].values():
            if (e["job_id"] == packet["job_id"]
                    and sorted(e["candidate_turn_ids"])
                    == sorted(packet["candidate_turn_ids"])):
                self._ops("duplicate_suppressed",
                          ledger_key=key,
                          job_id=packet["job_id"],
                          reason="candidate_pair",
                          existing_key=e["ledger_key"])
                return "duplicate", copy.deepcopy(e)
        for e in self.state["events"].values():
            if (e["job_id"] == packet["job_id"]
                    and e["state"] == "unacknowledged"):
                self._ops("event_locked", ledger_key=key,
                          job_id=packet["job_id"],
                          blocking_key=e["ledger_key"])
                return "locked", copy.deepcopy(e)
        event = copy.deepcopy(packet)
        event["state"] = "unacknowledged"
        self.state["events"][key] = event
        self._reset_streak(packet["job_id"])
        self._save()
        return "recorded", copy.deepcopy(event)

    def acknowledge(self, ledger_key, at=None):
        """Mark an event acknowledged. Cooldown starts HERE,
        at acknowledgement, not at detection (§8). Idempotent:
        acknowledging an already-acknowledged event returns it
        unchanged."""
        event = self.state["events"].get(ledger_key)
        if event is None:
            raise KeyError(f"unknown ledger_key: {ledger_key}")
        if event["state"] == "acknowledged":
            return copy.deepcopy(event)
        at = time.time() if at is None else at
        event["state"] = "acknowledged"
        event["acknowledged_at"] = at
        cooldown = self.config["cooldown_by_job"].get(
            event["job_id"], self.config["cooldown_default_s"])
        self.state["cooldown_until"][event["job_id"]] = (
            at + cooldown)
        self._save()
        return copy.deepcopy(event)

    def may_detect(self, job_id, now=None):
        """Detection gate (§8): closed while the job has an
        unacknowledged event, and during the post-acknowledgement
        cooldown. Dependencies (§10) are the scheduler's gate,
        not this one."""
        now = time.time() if now is None else now
        for e in self.state["events"].values():
            if (e["job_id"] == job_id
                    and e["state"] == "unacknowledged"):
                return False
        return now >= self.state["cooldown_until"].get(job_id, 0)

    def due_alerts(self, now=None):
        """Unacknowledged events older than alert_age (§8),
        by their packet's detected_at. Pure read."""
        from datetime import datetime
        now = time.time() if now is None else now
        age = self.config["alert_age_s"]
        out = []
        for e in self.unacknowledged():
            try:
                det = datetime.fromisoformat(
                    e["detected_at"].replace(
                        "Z", "+00:00")).timestamp()
            except Exception:
                continue
            if now - det > age:
                out.append(e)
        return out

    def raise_alerts(self, now=None):
        """Raise the due alerts (§8): each is written to the
        ops log as an operational alert, at most once per
        ledger_key per alert interval (verdict S4 — the
        interval is alert_age). The events themselves stay
        unacknowledged — an alert never drops one."""
        now = time.time() if now is None else now
        due = self.due_alerts(now)
        raised = []
        for e in due:
            key = e["ledger_key"]
            last = self.state["alerts_raised"].get(key, 0)
            if now - last < self.config["alert_age_s"]:
                continue
            self.state["alerts_raised"][key] = now
            self._ops("alert_due", ledger_key=key,
                      job_id=e["job_id"])
            raised.append(e)
        if raised:
            self._save()
        return raised

    # -- streak (§6): persisted, survives restart ----------------

    def streak(self, job_id):
        s = self.state["streaks"].get(job_id)
        return {"count": 0, "last_turn_key": None,
                "reset_cause": None} if s is None else dict(s)

    def apply_judgement(self, job_id, turn_key, result):
        """One judged turn (§6). CALLER'S RESPONSIBILITY
        (reviewer note, verdict 2026-11-15): only completed
        turns that reached the pool may be passed here — this
        function does not and cannot check pool membership.
        YES counts, NO resets, ERROR holds (and is logged,
        §7 — an error is never recorded as a NO). The same
        turn judged twice does not count twice: turn identity
        is structural. Returns the streak after the
        judgement."""
        if result not in ("YES", "NO", "ERROR"):
            raise ValueError(f"unknown judgement: {result!r}")
        s = self.streak(job_id)
        if result == "ERROR":
            self._ops("judge_error", job_id=job_id,
                      turn_key=turn_key)
            return s
        if s["last_turn_key"] == turn_key:
            return s
        if result == "YES":
            s = {"count": s["count"] + 1,
                 "last_turn_key": turn_key,
                 "reset_cause": s.get("reset_cause")}
        else:
            s = {"count": 0, "last_turn_key": turn_key,
                 "reset_cause": "judged_no"}
        self.state["streaks"][job_id] = s
        self._save()
        return dict(s)

    def reset_streak_gate(self, job_id, turn_key):
        """Reset the streak for a GATED-OUT completed seat
        turn (§6 as amended by the v1.3 draft; Stage 3 review
        ruling D2 / must-fix M-S3-1). The keyword gate excluded
        this turn before the judge, so NO judge call was made
        and this is never recorded as a judged NO: the reset
        is recorded distinctly, as reset_cause "gate_reset" in
        the streak record and a "gate_reset" entry in the ops
        log. last_turn_key advances to the gated turn so the
        detector resumes after it and never reprocesses it.
        Returns the streak after the reset."""
        s = self.streak(job_id)
        if (s["count"] == 0
                and s["last_turn_key"] == turn_key
                and s.get("reset_cause") == "gate_reset"):
            return s
        s = {"count": 0, "last_turn_key": turn_key,
             "reset_cause": "gate_reset"}
        self.state["streaks"][job_id] = s
        self._ops("gate_reset", job_id=job_id,
                  turn_key=turn_key)
        self._save()
        return dict(s)

    def _reset_streak(self, job_id):
        self.state["streaks"][job_id] = {
            "count": 0,
            "last_turn_key":
                self.streak(job_id)["last_turn_key"],
            "reset_cause": "event_recorded"}
