"""Duenna Stage 3 — the BINDER: run identity (K1), subject
verification (K2), and the configuration freeze gate (G1).

The BINDER mints the run identity (K1) at the moment a freeze
attempt begins, runs G1, and records its outputs through the
Stage 1 record. The run identity binds, by reference: one
configuration identity (K3, config.py), one verified subject
identity (K2), one frozen tree-set identity. ``RUN_STARTED`` is
appended only on a successful freeze. A REFUSED freeze is itself
recorded under the run identity as a governance record (freeze
attempted, refused, reason) — a run that never started still has
an identity and a record; it is never a scored subject outcome.

Subject verification (K2): a subject pin is an ASSERTION, not an
identity. The subject identity is minted by verification — a call
to the serving lane whose response is recorded (served model
string, endpoint) as a ``SUBJECT_VERIFICATION`` event, producing
the subject record {asserted pin, served identity, verification
event reference}. A pin/served mismatch refuses the run at G1.
In this harness the lane is a callable supplied by the caller —
``lane(pin) -> (served_identity, endpoint)`` — the harness's
stand-in for the serving lane, in the same fixture class as
Stage 1's TEST authority: the verification MECHANISM (the lane's
response is obtained and recorded, and identity binds to it,
never to the caller's assertion) is what this stage exercises;
no live lane is called and no transport is claimed.

G1's checks, in order:

0. RECORD INTEGRITY (prior to everything): the record's chain is
   recomputed over the events as they currently stand (Stage 1's
   ``verify_chain``), AND the verified chain's terminal state is
   bound to this record instance's in-memory length and head
   (:func:`verify_record_current`, the stage's shared check —
   Gate 1 correction round 4). If either fails, the freeze is
   refused by raised exception ONLY — nothing is appended,
   because a refusal must never mutate the record whose
   integrity just failed (Stage 2, correction round 3).
1. DRAFT STRUCTURE: the draft freezes as one configuration
   object (config.freeze_config). A structurally unusable draft
   is recorded as a refused freeze and raised.
2. SURFACE CONSISTENCY (DR-03): every subject surface in the
   draft, and the pin, must name the SAME subject. A
   contradiction is preserved as a ``SUBJECT_CONFLICT`` record
   AND refuses the freeze — refusal, not either/or.
3. SUBJECT VERIFICATION (K2/DR-20): the lane is called with the
   pin; its response is recorded; served != pin is a
   ``SUBJECT_CONFLICT`` AND refuses the freeze. "A listed model
   is not always a served model" — the pin cannot bind a run
   until the lane has served it.
4. DERIVED LIMITS POLICY (K3/DR-21): the policy check of
   config.derived_limit_problems runs and its result is recorded
   as a ``POLICY_CHECK`` event either way; any problem refuses
   the freeze.

On success the binder appends ``CONFIG_FROZEN`` (the three
bound digests) and ``RUN_STARTED``, and returns a
:class:`FrozenRun` — the capability the access path and the
gates require. There is no FrozenRun without a successful
freeze, so there is no governed execution of an unstarted run.

Attribution of a subject mismatch is a single class: UNKNOWN
(K2), recorded on every conflict record this stage mints. No
combined category, no guessed cause.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K1, K2, K3,
G1), PROCESS-TREE-AND-PLAN.md v2, Stage 3; DEFECT-REGISTER.md
DR-03, DR-20, DR-21.
"""

from __future__ import annotations

import hashlib
import json

from record import GENESIS, _canonical, verify_chain

from config import (ConfigError, FrozenConfig, derived_limit_problems,
                    freeze_config)

RUN_IDENTITY_MINTED = "RUN_IDENTITY_MINTED"
SUBJECT_VERIFICATION = "SUBJECT_VERIFICATION"
SUBJECT_CONFLICT = "SUBJECT_CONFLICT"
POLICY_CHECK = "POLICY_CHECK"
CONFIG_FROZEN = "CONFIG_FROZEN"
FREEZE_REFUSED = "FREEZE_REFUSED"
RUN_STARTED = "RUN_STARTED"
RUN_INVALIDATED = "RUN_INVALIDATED"

# As in Stage 2: a refusal carrying this key is raised WITHOUT
# recording anything on the record.
CHAIN_VERIFICATION_FAILED = "record_chain_verification_failed"


def verify_record_current(record):
    """The stage's shared record-integrity check: run by every
    writer path (freeze, consumption issuance, capture
    admission, output admission) before it reads evidence from,
    or appends anything to, the record.

    Returns ``(events, failure)`` — the events as they currently
    stand on the record, and ``None`` iff the path may proceed.
    ``failure`` is the value the path carries under
    ``CHAIN_VERIFICATION_FAILED`` in its refusal details:

    - a chain that does not recompute: the first bad seq, as in
      every earlier round;
    - a chain that recomputes but whose TERMINAL state is not
      the state this record instance is about to extend: a
      ``{"terminal_mismatch": {...}}`` dict naming both
      terminals — the persisted chain's length and head digest,
      and the instance's in-memory ``length`` and
      ``head_digest``.

    The terminal binding is Gate 1 correction round 4.
    ``verify_chain`` alone proves the bytes read form A valid
    chain; it does not prove they form THE chain this
    ``EventRecord`` instance holds in memory — its length and
    head, loaded at open and advanced by its own appends. An
    empty event list verifies, so a record file deleted or
    truncated to empty after the freeze would pass the chain
    check while the instance still held its old head, and the
    next append would extend a chain that no longer exists in
    the file, under a sequence and predecessor that match
    nothing in it. Comparing the verified chain's terminal —
    event count, and the last event's digest (GENESIS when
    empty) — against the instance's length and head closes
    that gap: ANY desync between the persisted record and the
    writer's in-memory state (truncation to empty, tail
    truncation, deletion, extension by another writer) is an
    integrity failure of the same class as a chain break, and
    the path refuses without appending anything. A record
    genuinely at genesis — empty file, instance at (0,
    GENESIS) — passes, as it must: the binding compares two
    terminals, it does not require a non-empty chain."""
    events = record.read_all()
    chain_ok, first_bad_seq = verify_chain(events)
    if not chain_ok:
        return events, first_bad_seq
    persisted_head = events[-1]["digest"] if events else GENESIS
    if len(events) != record.length \
            or persisted_head != record.head_digest:
        return events, {"terminal_mismatch": {
            "persisted_length": len(events),
            "persisted_head_digest": persisted_head,
            "writer_length": record.length,
            "writer_head_digest": record.head_digest,
        }}
    return events, None

# K2: attribution of a mismatch is a single class, UNKNOWN, until
# evidence establishes the cause.
ATTRIBUTION_UNKNOWN = "UNKNOWN"


class FreezeRefused(Exception):
    """G1 refused the freeze. Carries the run identity (a refused
    freeze is still recorded under it) and the refusal evidence
    in ``details``."""

    def __init__(self, run_id: str, details: dict):
        self.run_id = run_id
        self.details = details
        super().__init__(
            f"freeze refused for run {run_id!r}: {details!r}")


class FrozenRun:
    """A run whose freeze succeeded: the run identity, the frozen
    configuration, and the verified subject record, bound by
    their digests. Minted only by :meth:`Binder.attempt_freeze`.

    Immutable as a capability (Gate 1 correction round 1):
    every attribute is set once at construction and assignment
    afterwards raises — as first built, ``run.config`` (and
    ``run_id``, ``subject_record``) were publicly writable, so
    the capability holding the frozen object could be rebound
    to a different configuration while the recorded
    ``RUN_STARTED`` event still bound the original.
    ``config_digest`` is the value CAPTURED at freeze — the
    digest the ``RUN_STARTED`` event binds — not a value
    recomputed from a replaceable attribute. The subject record
    is held as canonical JSON and handed out as a fresh dict,
    and its digest and served identity are likewise captured at
    construction.

    The one legitimate post-freeze transition is invalidation:
    ``invalidated`` is the run's subject-dependent execution
    state under the frozen run policy, set — through
    :meth:`_invalidate`, and only there — by the capture gate
    (admission.py) when a subject conflict invalidates the run,
    and read by the output gate. The invalidation is also
    recorded on the record as ``RUN_INVALIDATED``; the flag is
    this process's live copy of that recorded fact."""

    __slots__ = ("_record", "_run_id", "_config",
                 "_config_digest", "_subject_json",
                 "_subject_digest", "_verified_served_identity",
                 "_invalidated", "_invalidation_cause", "_frozen")

    def __init__(self, record, run_id: str, config: FrozenConfig,
                 subject_record: dict):
        object.__setattr__(self, "_frozen", False)
        object.__setattr__(self, "_record", record)
        object.__setattr__(self, "_run_id", run_id)
        object.__setattr__(self, "_config", config)
        object.__setattr__(self, "_config_digest", config.digest)
        object.__setattr__(
            self, "_subject_json",
            _canonical(subject_record).decode("utf-8"))
        object.__setattr__(
            self, "_subject_digest",
            subject_record["subject_digest"])
        object.__setattr__(
            self, "_verified_served_identity",
            subject_record["served_identity"])
        object.__setattr__(self, "_invalidated", False)
        object.__setattr__(self, "_invalidation_cause", None)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                "run is frozen: its identity, configuration and "
                "subject were bound at freeze and cannot be "
                "rebound")
        object.__setattr__(self, name, value)

    def _invalidate(self, cause_capture_id: str) -> None:
        """Mark the run invalidated under the frozen run policy.
        The ONLY post-freeze state transition, called by the
        capture gate when it records ``RUN_INVALIDATED``; the
        recorded event is the fact, this flag its live copy."""
        object.__setattr__(self, "_invalidated", True)
        object.__setattr__(self, "_invalidation_cause",
                           cause_capture_id)

    @property
    def record(self):
        return self._record

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def config(self) -> FrozenConfig:
        return self._config

    @property
    def subject_record(self) -> dict:
        """The verified subject record, as a fresh dict (the
        run's binding cannot be mutated through it)."""
        return json.loads(self._subject_json)

    @property
    def invalidated(self) -> bool:
        return self._invalidated

    @property
    def invalidation_cause(self):
        return self._invalidation_cause

    @property
    def config_digest(self) -> str:
        """The configuration digest captured at freeze — the
        digest bound in the ``RUN_STARTED`` event."""
        return self._config_digest

    @property
    def subject_digest(self) -> str:
        return self._subject_digest

    @property
    def verified_served_identity(self) -> str:
        """The served identity the run's subject claim rests on:
        the identity the lane returned for the preflight call,
        recorded at verification — never the pin's assertion
        alone (they are equal in a frozen run, because a mismatch
        refused the freeze; the claim cites the SERVED value)."""
        return self._verified_served_identity


class Binder:
    """Mints run identities and runs G1 against a Stage 1
    record. One Binder per record is the harness's shape."""

    def __init__(self, record):
        self.record = record

    @staticmethod
    def _mint_run_id(events) -> str:
        """The next run identity, from the record as it stands:
        one past the count of identities already minted on it.
        Deterministic in the record's contents."""
        prior = sum(
            1 for ev in events
            if ev.get("type") == RUN_IDENTITY_MINTED)
        return f"RUN-{prior + 1:04d}"

    def _record_refusal(self, run_id: str, details: dict):
        """Append the FREEZE_REFUSED governance record.
        PRECONDITION: the record's chain has verified (checked
        first in attempt_freeze). Recording extends the chain,
        which is only sound on a valid chain."""
        self.record.append(FREEZE_REFUSED, {
            "run_id": run_id,
            "details": details,
        })

    def attempt_freeze(self, draft: dict, lane) -> FrozenRun:
        """Run G1 on a draft configuration. ``lane`` is the
        serving-lane callable: ``lane(pin) -> (served_identity,
        endpoint)``. On success returns the FrozenRun; on any
        refusal raises :class:`FreezeRefused`, with the refusal
        recorded under the minted run identity (except a
        chain-integrity failure, which records nothing)."""
        events, integrity_failure = verify_record_current(
            self.record)
        run_id = self._mint_run_id(events)
        if integrity_failure is not None:
            raise FreezeRefused(run_id, {
                CHAIN_VERIFICATION_FAILED: integrity_failure})

        self.record.append(RUN_IDENTITY_MINTED, {"run_id": run_id})

        # 1. Draft structure.
        try:
            config = freeze_config(draft)
        except ConfigError as exc:
            details = {"stage": "draft_structure",
                       "error": str(exc)}
            self._record_refusal(run_id, details)
            raise FreezeRefused(run_id, details) from None

        # 2. Surface consistency (DR-03): the pin and every
        # surface must name the same subject.
        named = set(config.subject_surfaces.values())
        named.add(config.subject_pin)
        if len(named) != 1:
            conflict = {
                "run_id": run_id,
                "kind": "configuration_surfaces",
                "subject_pin": config.subject_pin,
                "subject_surfaces": config.subject_surfaces,
                "attribution": ATTRIBUTION_UNKNOWN,
            }
            self.record.append(SUBJECT_CONFLICT, conflict)
            details = {"stage": "surface_consistency",
                       "conflict": conflict}
            self._record_refusal(run_id, details)
            raise FreezeRefused(run_id, details)

        # 3. Subject verification (K2): the lane's response is
        # obtained and recorded; identity binds to it.
        served_identity, endpoint = lane(config.subject_pin)
        verification = self.record.append(SUBJECT_VERIFICATION, {
            "run_id": run_id,
            "asserted_pin": config.subject_pin,
            "served_identity": served_identity,
            "endpoint": endpoint,
        })
        if served_identity != config.subject_pin:
            conflict = {
                "run_id": run_id,
                "kind": "pin_served_mismatch",
                "asserted_pin": config.subject_pin,
                "served_identity": served_identity,
                "attribution": ATTRIBUTION_UNKNOWN,
            }
            self.record.append(SUBJECT_CONFLICT, conflict)
            details = {"stage": "subject_verification",
                       "conflict": conflict}
            self._record_refusal(run_id, details)
            raise FreezeRefused(run_id, details)
        subject_digest = hashlib.sha256(_canonical({
            "asserted_pin": config.subject_pin,
            "served_identity": served_identity,
            "endpoint": endpoint,
            "verification_event_digest": verification["digest"],
        })).hexdigest()
        subject_record = {
            "asserted_pin": config.subject_pin,
            "served_identity": served_identity,
            "endpoint": endpoint,
            "verification_event_digest": verification["digest"],
            "subject_digest": subject_digest,
        }

        # 4. Derived limits policy (K3): recorded either way;
        # any problem refuses.
        problems = derived_limit_problems(config)
        self.record.append(POLICY_CHECK, {
            "run_id": run_id,
            "config_digest": config.digest,
            "derived_limit_problems": problems,
            "passed": not problems,
        })
        if problems:
            details = {"stage": "derived_limits_policy",
                       "problems": problems}
            self._record_refusal(run_id, details)
            raise FreezeRefused(run_id, details)

        # Success: bind the three identities and start the run.
        self.record.append(CONFIG_FROZEN, {
            "run_id": run_id,
            "config_digest": config.digest,
            "subject_digest": subject_digest,
            "tree_set_digest": config.tree_set_digest,
            "schema_digest": config.schema_digest,
        })
        self.record.append(RUN_STARTED, {
            "run_id": run_id,
            "config_digest": config.digest,
            "subject_digest": subject_digest,
            "tree_set_digest": config.tree_set_digest,
        })
        return FrozenRun(self.record, run_id, config,
                         subject_record)
