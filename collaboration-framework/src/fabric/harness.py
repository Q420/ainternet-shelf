"""Harness — Loom spec v0.1 Rev 9, sections 4, 4A, 6, and Annex B.1.

The harness is the only agent-facing surface of the fabric. It holds
the store (through the engine), issues per-run tokens bound to agent
identities (section 4A), serves every content read itself and records
it at serve time as a DISCOVERY event (sections 4, 4A, 6), enforces
the cumulative read-breadth criterion (section 6: RB < 0.5 over six
regions — at most two regions' content per agent per run, ever), and
runs the contribution commit protocol in section 4's fixed order:

  1. identity, then schema (Annex B.1 + the cross-field rules,
     including discovery verification per Annex B rule (vi));
  2. staleness, against declared base versions, with the changed-read
     diff returned in the rejection event;
  3. structural, operations applied hypothetically to current state
     and tested against S1/S2/S3 (S4 is schema-level, step 1);
  4. commit, atomic, per section 3.

Idempotency (section 3) sits between identity and schema: the
assessment/examination ladder in section 3 fixes that position for the
other two action types (step 2, after identity, before schema), and
section 4's order does not name idempotency for contributions; the
ladder position is applied here and recorded as an interpretation in
the Stage 2 build notes, not silently.

A submission whose declared read set does not exactly match the
harness read record is not a rejection outcome: sections 6 and 9 name
it a hard-line breach (claiming reads not made, or omitting reads
made), which stops the run as failed. The harness raises
HardLineBreach and appends no contribution event — the rejection
outcome enum has no class for it.

Stage 2 corrections round (2026-11-21, Vane's examination findings
3A/3B): the run-failure itself is now durable. The harness is the
protocol library and still raises HardLineBreach appending nothing —
the examined Stage 2 semantics, which stage2_tests.py pins — but the
run's owner (the fabric service, fabric/service.py) catches the
breach and appends the system RUN_FAILED event atomically with the
transition to failed state; the engine fold derives that state from
the history, and this harness refuses every agent-facing operation
once the folded state is failed. Idle, likewise, is no longer an
in-memory log line: it appends a durable IDLE event (the between-run
amendment settled under Ben's delegation, 2026-11-21).

Every Stage 2 event payload carries a plain-words "summary" of the
event, so the payload alone is enough to describe what happened (the
observer UI's only projection is the event history).

Stage 3 extension (2026-11-21, built exactly to the settled Stage 3
design brief Rev 3): the noticing and judgment half of the fabric.
Three new agent operations — examine, assess, claim_completion —
run through ONE validation ladder (section 3's order: recordability,
identity, idempotency with its fixed sub-order of replay / key
conflict / global identity collision, schema, referential, authority
and scope, state), parameterised by action type, returning a
structured first failure the event writer consumes. Examinations
create or note semantic tensions under section 4's multi-match
duplicate rule, binding an immutable snapshot of the read versions
from this harness's own read record; assessments enter the record
under Annex B.3's discriminated union and move tensions through
section 4's transition table (transitions recorded as TENSION_STATUS
events, never silently folded); completion claims are recorded
under the settled claim contract (claim_id is both idempotency key
and global record identity; a claimant field is schema-invalid —
authorship is the token; evidence-invalid claims are RECORDED and
count as no claim, never refused) and facet statuses are derived
under section 5 with the settled precedence, recorded as
FACET_STATUS events on change. Every submission produces exactly
one primary outcome event; derived transitions ride in the same
atomic commit group, ordered deterministically.
"""

import copy
import json
import os
import re
import subprocess
import sys
import uuid

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.validators import RefResolver

from .canonical import canonical, sha256_hex
from .engine import (ReplayHalt, _apply_operations, apply_event,
                     empty_state, state_hash, verified_fold)
from .fixture import (CONSTITUTION_HASH, SEALED_REQUIRED_FACETS,
                      SYSTEM_ACTOR)
from .packpin import binding_is_stage4

# Section 6: RB_i < 0.5 strictly, over six regions, cumulative.
MAX_REGIONS_PER_AGENT = 2

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _is_uuid(value) -> bool:
    return isinstance(value, str) and _UUID_RE.match(value) is not None


_format_checker = FormatChecker()


@_format_checker.checks("uuid", raises=ValueError)
def _uuid_format(value):
    if not isinstance(value, str):
        return True  # format does not apply to non-strings
    if not _UUID_RE.match(value):
        raise ValueError("not a canonical UUID")
    return True


# Annex B.1 — the contribution schema, verbatim from Rev 9 (the
# mechanical instrument; draft 2020-12, format assertion required).
CONTRIBUTION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2020-12/vocab/core": True,
        "https://json-schema.org/draft/2020-12/vocab/applicator": True,
        "https://json-schema.org/draft/2020-12/vocab/validation": True,
        "https://json-schema.org/draft/2020-12/vocab/format-assertion": True,
    },
    "$id": "loom/contribution/3",
    "title": "Loom agent response",
    "type": "object",
    "additionalProperties": False,
    "required": ["action"],
    "properties": {
        "action": {"enum": ["contribute", "idle"]},
        "contribution": {
            "type": "object",
            "additionalProperties": False,
            "required": ["author", "idempotency_id", "base_versions",
                         "read_set", "write_set", "operations", "rationale",
                         "discovery_source", "discovery_ref"],
            "properties": {
                "author": {"type": "string", "format": "uuid"},
                "idempotency_id": {"type": "string", "format": "uuid"},
                "base_versions": {
                    "type": "object",
                    "minProperties": 1,
                    "additionalProperties": {"type": "integer", "minimum": 1},
                },
                "read_set": {
                    "type": "array", "minItems": 1, "uniqueItems": True,
                    "items": {"type": "string", "format": "uuid"},
                },
                "write_set": {
                    "type": "array", "uniqueItems": True,
                    "items": {"type": "string", "format": "uuid"},
                },
                "operations": {
                    "type": "array", "minItems": 1,
                    "items": {"$ref": "#/$defs/operation"},
                },
                "rationale": {"type": "string"},
                "discovery_source": {"enum": ["index", "watch", "fabric_read"]},
                "discovery_ref": {"type": "integer", "minimum": 1},
            },
        },
    },
    "allOf": [
        {
            "if": {"properties": {"action": {"const": "contribute"}}},
            "then": {"required": ["contribution"]},
            "else": {"not": {"required": ["contribution"]}},
        }
    ],
    "$defs": {
        "operation": {
            "oneOf": [
                {
                    "title": "replace_content",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["kind", "region_id", "new_content"],
                    "properties": {
                        "kind": {"const": "replace_content"},
                        "region_id": {"type": "string", "format": "uuid"},
                        "new_content": {"type": "string"},
                    },
                },
                {
                    "title": "append_content",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["kind", "region_id", "text"],
                    "properties": {
                        "kind": {"const": "append_content"},
                        "region_id": {"type": "string", "format": "uuid"},
                        "text": {"type": "string"},
                    },
                },
                {
                    "title": "add_dependency",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["kind", "dependency"],
                    "properties": {
                        "kind": {"const": "add_dependency"},
                        "dependency": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["source", "target", "kind"],
                            "properties": {
                                "source": {"type": "string", "format": "uuid"},
                                "target": {"type": "string", "format": "uuid"},
                                "kind": {"enum": ["uses", "constrains", "extends",
                                                  "contradicts-candidate"]},
                            },
                        },
                    },
                },
                {
                    "title": "remove_dependency",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["kind", "dependency_id"],
                    "properties": {
                        "kind": {"const": "remove_dependency"},
                        "dependency_id": {"type": "string", "format": "uuid"},
                    },
                },
                {
                    "title": "raise_tension (semantic only — agents hold no "
                             "structural-tension authority)",
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["kind", "tension"],
                    "properties": {
                        "kind": {"const": "raise_tension"},
                        "tension": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["type", "regions", "description"],
                            "properties": {
                                "type": {"const": "semantic"},
                                "regions": {
                                    "type": "array", "minItems": 1,
                                    "uniqueItems": True,
                                    "items": {"type": "string",
                                              "format": "uuid"},
                                },
                                "description": {"type": "string"},
                            },
                        },
                    },
                },
            ]
        }
    },
}

# The schema's $id ("loom/contribution/3") is a non-URL identifier;
# jsonschema 4.10's legacy resolver would try to fetch the schema's
# own document remotely when resolving the local "#/$defs/operation"
# ref. Serving the document from the resolver's local store under its
# own $id is exactly what the $id declares; no constraint changes.
_RESOLVER = RefResolver(base_uri="", referrer=CONTRIBUTION_SCHEMA,
                        store={"loom/contribution/3": CONTRIBUTION_SCHEMA})
_VALIDATOR = Draft202012Validator(CONTRIBUTION_SCHEMA, resolver=_RESOLVER,
                                  format_checker=_format_checker)

# Annex B.2 — the examination report schema, verbatim from Rev 9.
EXAMINATION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2020-12/vocab/core": True,
        "https://json-schema.org/draft/2020-12/vocab/applicator": True,
        "https://json-schema.org/draft/2020-12/vocab/validation": True,
        "https://json-schema.org/draft/2020-12/vocab/format-assertion": True,
    },
    "$id": "loom/examination/1",
    "title": "Loom examination report",
    "type": "object",
    "additionalProperties": False,
    "required": ["author", "examination_id", "idempotency_id", "regions",
                 "description", "discovery_source", "discovery_ref"],
    "properties": {
        "author": {"type": "string", "format": "uuid"},
        "examination_id": {"type": "string", "format": "uuid"},
        "idempotency_id": {"type": "string", "format": "uuid"},
        "regions": {
            "type": "array", "minItems": 1, "uniqueItems": True,
            "items": {"type": "string", "format": "uuid"},
        },
        "description": {"type": "string"},
        "related_tension": {"type": "string", "format": "uuid"},
        "discovery_source": {"enum": ["index", "watch", "fabric_read"]},
        "discovery_ref": {"type": "integer", "minimum": 1},
    },
}

# Annex B.3 — the assessment schema (the discriminated union),
# verbatim from Rev 9.
ASSESSMENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2020-12/vocab/core": True,
        "https://json-schema.org/draft/2020-12/vocab/applicator": True,
        "https://json-schema.org/draft/2020-12/vocab/validation": True,
        "https://json-schema.org/draft/2020-12/vocab/format-assertion": True,
    },
    "$id": "loom/assessment/1",
    "title": "Loom assessment",
    "oneOf": [
        {
            "title": "TensionAssessment",
            "type": "object",
            "additionalProperties": False,
            "required": ["assessment_id", "author", "target_kind",
                         "target_id", "position", "reasoning"],
            "not": {"required": ["version_reviewed"]},
            "properties": {
                "assessment_id": {"type": "string", "format": "uuid"},
                "author": {"type": "string", "format": "uuid"},
                "target_kind": {"const": "tension"},
                "target_id": {"type": "string", "format": "uuid"},
                "position": {"enum": ["addressed", "remains", "clarifies"]},
                "reasoning": {"type": "string"},
                "supersedes": {"type": "string", "format": "uuid"},
            },
        },
        {
            "title": "FacetAssessment",
            "type": "object",
            "additionalProperties": False,
            "required": ["assessment_id", "author", "target_kind",
                         "target_id", "position", "reasoning",
                         "version_reviewed"],
            "properties": {
                "assessment_id": {"type": "string", "format": "uuid"},
                "author": {"type": "string", "format": "uuid"},
                "target_kind": {"const": "facet"},
                "target_id": {"type": "string", "format": "uuid"},
                "position": {"enum": ["examined", "disputed"]},
                "reasoning": {"type": "string"},
                "supersedes": {"type": "string", "format": "uuid"},
                "version_reviewed": {"type": "integer", "minimum": 1},
            },
        },
    ],
}

# The CompletionClaim schema (Stage 3 claim contract, settled
# 2026-11-21): exactly the Rev 9 section 3 record fields MINUS
# claimant — the schema does not accept a claimant field, so one
# present is schema_invalid (additionalProperties is false and no
# claimant property exists). Authorship is the token identity,
# bound by the harness, never read from the submission.
CLAIM_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "loom/completion-claim/1",
    "title": "Loom completion claim",
    "type": "object",
    "additionalProperties": False,
    "required": ["claim_id", "facet", "facet_version",
                 "supporting_contributions", "rationale"],
    "properties": {
        "claim_id": {"type": "string", "format": "uuid"},
        "facet": {"type": "string", "format": "uuid"},
        "facet_version": {"type": "integer", "minimum": 1},
        "supporting_contributions": {
            "type": "array", "minItems": 1,
            "items": {"type": "string", "format": "uuid"},
        },
        "rationale": {"type": "string"},
    },
}

_EXAMINATION_VALIDATOR = Draft202012Validator(
    EXAMINATION_SCHEMA, format_checker=_format_checker)
_ASSESSMENT_VALIDATOR = Draft202012Validator(
    ASSESSMENT_SCHEMA, format_checker=_format_checker)
_CLAIM_VALIDATOR = Draft202012Validator(
    CLAIM_SCHEMA, format_checker=_format_checker)

# The section 3 validation ladder, parameterised by action type
# (Stage 3 brief section 3): for each action, the idempotency-key
# field, the global record-identity field, the key-conflict reason,
# and the payload field the submitted document travels under.
_LADDER_KEYS = {
    "assessment": {"key": "assessment_id", "record": "assessment_id",
                   "conflict": "id_conflict",
                   "doc_field": "assessment"},
    "examination": {"key": "idempotency_id", "record": "examination_id",
                    "conflict": "idempotency_conflict",
                    "doc_field": "report"},
    "claim": {"key": "claim_id", "record": "claim_id",
              "conflict": "id_conflict", "doc_field": "claim"},
}

# S3 ranges over these dependency kinds (section 4).
_PATTERN_KINDS = ("uses", "constrains", "extends")


class HarnessRefusal(Exception):
    """An interface refusal: the call is refused and no event is
    appended (unauthenticated token, unknown region, breadth limit).
    Refusals of calls that never reached the record belong to the
    harness log, not the history."""


class TransportRefusal(HarnessRefusal):
    """A submission that is not a JSON object: refused at the
    interface as a transport error, counted in the harness log only
    (section 4 — no faithful payload exists to record)."""


class HardLineBreach(Exception):
    """A section 9 hard line: the submission's declared reads
    contradict the harness read record (reads claimed that were not
    made, or reads made that were omitted). The run is failed, not
    the submission merely rejected. Carries the evidence — the
    declared read set and the recorded read set — so the run's owner
    can record it verbatim in the RUN_FAILED event."""

    def __init__(self, message, declared=(), recorded=()):
        super().__init__(message)
        self.declared_read_set = sorted(declared)
        self.recorded_read_set = sorted(recorded)


class CheckerFailure(Exception):
    """Stage 4: the independent checker could not produce a verdict
    for a seal attempt — its process failed, timed out, answered
    unparseably, or returned a halt/refusal for a staged group the
    commit path itself produced. That is machinery failure
    (validation pack VP-36): the atomic group does not commit, and
    the run's owner records the failure under the run-failure
    contract. It is never a silent retry and never a partial
    group."""


class Harness:
    def __init__(self, engine):
        self._engine = engine
        # Stage 4: the command that runs the independent checker
        # process (None = the standard module invocation). Tests
        # replace it with a failing process to exercise VP-36; the
        # fabric service replaces it when the checker_failure fault
        # is injected.
        self.checker_command = None
        self._bound_cache = None   # Stage 4 binding, once read
        # Stage 4 correction round (C-B4): an optional observer the
        # pack harness installs to capture each seal attempt's
        # exact inputs (committed history, staged batch, snapshot,
        # authenticated actor) at the moment the checker is
        # invoked, so the same (H, B, L) can be replayed through
        # both evaluators. Behaviour-neutral when unset (None).
        self.attempt_observer = None
        # Correction round (C-B2): memo for the authoritative
        # history-derived fold, keyed by the history's head hash.
        self._auth_state_cache = None
        self._tokens = {}          # token -> agent_id
        # Harness log: transport refusals and breadth refusals — the
        # record of calls refused at the interface, which append no
        # event (section 4). (Idle left this log in the corrections
        # round: it is a durable IDLE event now.)
        self.log = []
        # agent_id -> {region_id: {"openings", "last_version", "last_seq"}}
        self.read_record = {}
        # region_id -> contribution_id that last changed it (or None)
        self._last_changed_by = {}
        # (author, idempotency_id) -> {"content_hash", "outcome"}
        self._idempotency = {}
        # -- Stage 3 records (all rebuilt from the history) --------
        # (action, author, key) -> {"content_hash", "outcome"}: the
        # idempotency index for examine / assess / claim_completion.
        self._action_index = {}
        # (action, record_id) -> author: the global record-identity
        # registry (successfully recorded submissions only).
        self._record_identities = {}
        # contribution_id -> registry entry for EVERY recordable
        # contribution submission (accepted or rejected), with a
        # version simulation for the accepted ones: the claim
        # contract's referential stage and section 5's evidence
        # binding read from here. (Rev 9 section 3 gives every
        # Contribution record a contribution_id; Stage 2 assigned
        # one only at commit — Stage 3 assigns one to every
        # recordable submission and records it in the outcome
        # event's payload, so a claim can cite any contribution,
        # and the evidence predicate can refuse to count an
        # unaccepted one.)
        self._contribution_registry = {}
        self._sim_versions = {}      # region_id -> version (simulated)
        self._sim_deps = {}          # dependency_id -> (source, target)
        self._assessment_seq = {}    # assessment_id -> event_seq
        self._tension_raised_seq = {}  # tension_id -> event_seq
        self._rebuild_records()

    # -- record reconstruction -------------------------------------
    def _rebuild_records(self):
        dep_endpoints = {}
        for ev in self._engine.store.all_events():
            if ev["type"] == "RUN_OPENED":
                for d in ev["payload"]["dependencies"]:
                    dep_endpoints[d["dependency_id"]] = (d["source"],
                                                          d["target"])
                for r in ev["payload"]["regions"]:
                    self._last_changed_by[r["region_id"]] = None
            elif ev["type"] == "DISCOVERY":
                self._note_discovery(ev)
            elif ev["type"] == "CONTRIBUTION_ACCEPTED":
                self._note_accepted(ev, dep_endpoints)
            elif ev["type"] == "CONTRIBUTION_REJECTED":
                self._note_rejected(ev)
            self._note_stage3_event(ev)

    def _note_discovery(self, ev):
        rid = ev["payload"].get("region_id")
        if not rid:
            return
        slot = self.read_record.setdefault(ev["actor"], {}).setdefault(
            rid, {"openings": 0, "last_version": None, "last_seq": None})
        slot["openings"] += 1
        slot["last_version"] = ev["payload"].get("version")
        slot["last_seq"] = ev["event_seq"]

    def _note_accepted(self, ev, dep_endpoints=None):
        payload = ev["payload"]
        contribution = payload["contribution"]
        if dep_endpoints is None:
            dep_endpoints = {
                d_id: (d["source"], d["target"])
                for d_id, d in
                self._authoritative_state()["dependencies"].items()}
        touched = set()
        for i, op in enumerate(contribution["operations"]):
            kind = op["kind"]
            if kind in ("replace_content", "append_content"):
                touched.add(op["region_id"])
            elif kind == "add_dependency":
                dep_id = payload["assigned_dependency_ids"][str(i)]
                dep_endpoints[dep_id] = (op["dependency"]["source"],
                                         op["dependency"]["target"])
                touched.update(dep_endpoints[dep_id])
            elif kind == "remove_dependency":
                endpoints = dep_endpoints.get(op["dependency_id"])
                if endpoints:
                    touched.update(endpoints)
        for rid in touched:
            self._last_changed_by[rid] = payload["contribution_id"]
        key = (contribution["author"], contribution["idempotency_id"])
        self._idempotency[key] = {
            "content_hash": sha256_hex(canonical(contribution)),
            "outcome": {"outcome": "accepted",
                        "contribution_id": payload["contribution_id"],
                        "event_seq": ev["event_seq"]},
        }

    def _note_rejected(self, ev):
        payload = ev["payload"]
        if payload.get("outcome") == "idempotency_conflict":
            return  # a conflict is not the original submission
        contribution = payload.get("contribution")
        if not isinstance(contribution, dict):
            return
        author = contribution.get("author")
        idem = contribution.get("idempotency_id")
        if not (_is_uuid(author) and _is_uuid(idem)):
            return
        if author != ev["actor"]:
            return  # identity-mismatch records index nothing under a claim
        key = (author, idem)
        if key not in self._idempotency:
            self._idempotency[key] = {
                "content_hash": sha256_hex(canonical(contribution)),
                "outcome": {"outcome": payload["outcome"],
                            "event_seq": ev["event_seq"]},
            }

    # -- Stage 3 record reconstruction ------------------------------
    def _note_stage3_event(self, ev):
        """Maintain the Stage 3 registries from one event. Called
        for every event at rebuild (in sequence order) and for every
        newly committed event, so the registries are a deterministic
        function of the history."""
        t = ev["type"]
        if t == "RUN_OPENED":
            for r in ev["payload"]["regions"]:
                self._sim_versions[r["region_id"]] = r["version"]
            for d in ev["payload"]["dependencies"]:
                self._sim_deps[d["dependency_id"]] = (d["source"],
                                                       d["target"])
        elif t in ("CONTRIBUTION_ACCEPTED", "CONTRIBUTION_REJECTED"):
            self._note_contribution_outcome(ev)
        elif t in ("ASSESSMENT_RECORDED", "EXAMINATION_RECORDED",
                   "COMPLETION_CLAIMED"):
            self._note_action_outcome(ev)
        elif t == "TENSION_RAISED":
            self._tension_raised_seq[ev["payload"]["tension_id"]] = \
                ev["event_seq"]

    def _contribution_entry(self, actor, event_seq, payload,
                            sim_versions, sim_deps):
        """Simulate one accepted contribution's version effects over
        the given simulation state (mutated in place) and return its
        registry entry. Shared by the history rebuild (the real
        simulation) and by commit planning (a scratch simulation),
        so both derive the same entry from the same payload."""
        contribution = payload["contribution"]
        content_modified = set()
        for i, op in enumerate(contribution["operations"]):
            kind = op["kind"]
            if kind in ("replace_content", "append_content"):
                sim_versions[op["region_id"]] += 1
                content_modified.add(op["region_id"])
            elif kind == "add_dependency":
                dep_id = payload["assigned_dependency_ids"][str(i)]
                sim_deps[dep_id] = (op["dependency"]["source"],
                                    op["dependency"]["target"])
                sim_versions[op["dependency"]["source"]] += 1
                sim_versions[op["dependency"]["target"]] += 1
            elif kind == "remove_dependency":
                endpoints = sim_deps.get(op["dependency_id"])
                if endpoints:
                    sim_versions[endpoints[0]] += 1
                    sim_versions[endpoints[1]] += 1
        return {
            "contribution_id": payload["contribution_id"],
            "author": actor, "accepted": True, "event_seq": event_seq,
            "write_set": list(contribution["write_set"]),
            "content_modified": sorted(content_modified),
            "version_after": {rid: sim_versions[rid]
                              for rid in contribution["write_set"]},
        }

    def _note_contribution_outcome(self, ev):
        payload = ev["payload"]
        cid = payload.get("contribution_id")
        if not isinstance(cid, str):
            return  # a pre-Stage-3 rejection carried no id to cite
        if ev["type"] == "CONTRIBUTION_ACCEPTED":
            self._contribution_registry[cid] = self._contribution_entry(
                ev["actor"], ev["event_seq"], payload,
                self._sim_versions, self._sim_deps)
        else:
            self._contribution_registry[cid] = {
                "contribution_id": cid, "author": ev["actor"],
                "accepted": False, "event_seq": ev["event_seq"],
                "write_set": [], "content_modified": [],
                "version_after": {},
            }

    def _note_action_outcome(self, ev):
        kind = {"ASSESSMENT_RECORDED": "assessment",
                "EXAMINATION_RECORDED": "examination",
                "COMPLETION_CLAIMED": "claim"}[ev["type"]]
        cfg = _LADDER_KEYS[kind]
        payload = ev["payload"]
        document = payload[cfg["doc_field"]]
        outcome = {"outcome": payload["outcome"],
                   "event_seq": ev["event_seq"]}
        if payload["outcome"] == "rejected":
            outcome["reason"] = payload["reason"]
        if kind == "examination" and payload["outcome"] == "created":
            outcome["tension_id"] = payload["tension_id"]
        if kind == "examination" \
                and payload["outcome"] == "noted_existing":
            outcome["matched_tensions"] = list(
                payload["matched_tensions"])
        # The global identity registry holds successfully recorded
        # submissions only: a rejected submission creates no record
        # (section 3, B3), so it does not claim its identity.
        if payload["outcome"] in ("recorded", "created",
                                  "noted_existing") \
                and isinstance(document, dict):
            record_id = document.get(cfg["record"])
            if _is_uuid(record_id):
                self._record_identities[(kind, record_id)] = ev["actor"]
        # The idempotency index holds every outcome event EXCEPT a
        # key-conflict rejection (a conflict is not the original
        # submission — the contribution rule of _note_rejected) and
        # an identity-mismatch rejection (its key is not the
        # authenticated author's to index).
        if payload["outcome"] == "rejected" and payload.get("reason") \
                in (cfg["conflict"], "identity_mismatch"):
            return
        if isinstance(document, dict):
            key = document.get(cfg["key"])
            if _is_uuid(key):
                self._action_index[(kind, ev["actor"], key)] = {
                    "content_hash": sha256_hex(canonical(document)),
                    "outcome": outcome,
                }
        if kind == "assessment" and payload["outcome"] == "recorded":
            self._assessment_seq[document["assessment_id"]] = \
                ev["event_seq"]

    def _note_event(self, ev):
        if ev["type"] == "DISCOVERY":
            self._note_discovery(ev)
        elif ev["type"] == "CONTRIBUTION_ACCEPTED":
            self._note_accepted(ev)
        elif ev["type"] == "CONTRIBUTION_REJECTED":
            self._note_rejected(ev)
        self._note_stage3_event(ev)

    # -- identity (section 4A) --------------------------------------
    def issue_token(self, agent_id: str) -> str:
        """Issue the per-run token for an agent identity. The token —
        never the claimed author field — is what authenticates."""
        if not _is_uuid(agent_id):
            raise HarnessRefusal("agent identity must be a UUID")
        token = str(uuid.uuid4())
        self._tokens[token] = agent_id
        return token

    def _authenticate(self, token) -> str:
        agent = self._tokens.get(token)
        if agent is None:
            raise HarnessRefusal("unrecognised token")
        return agent

    # -- run lifecycle (corrections round) ---------------------------
    @property
    def run_failed(self) -> bool:
        """True once the folded state carries a RUN_FAILED. The
        failed state is derived from the history, so a harness built
        over a failed run's store is born refusing. Correction
        round 2 (C2-B2): the status is read from the authoritative
        fold, like every other non-snapshot consumer — never from
        the operational live view the fault hook corrupts."""
        return self._authoritative_state().get("run_status") == "failed"

    def _require_open(self):
        """Terminal enforcement: a failed run admits no further
        agent-facing operation of any kind (Vane's correction
        conditions, section 3)."""
        if self.run_failed:
            raise HarnessRefusal(
                "the run has failed (RUN_FAILED is in its history); "
                "no further agent activity is admitted")

    # -- views (section 6: the pattern; no content, no breadth) -----
    def view_pattern(self, token) -> dict:
        """The pattern: exactly the closed section 6 enumeration —
        ids, titles, scope notes, edges, tension/claim/watch headers,
        versions, last-changed-by. Never content."""
        self._authenticate(token)
        self._require_open()
        st = self._authoritative_state()
        return {
            "regions": [
                {"region_id": rid,
                 "title": r["title"],
                 "scope_note": r["scope_note"],
                 "version": r["version"],
                 "last_changed_by": self._last_changed_by.get(rid)}
                for rid, r in st["regions"].items()],
            "dependencies": [dict(d) for d in st["dependencies"].values()],
            "tensions": [
                {"tension_id": t["tension_id"], "type": t["type"],
                 "regions": list(t["regions"]), "status": t["status"]}
                for t in st["tensions"].values()],
            "claims": [dict(c) for c in st["claims"].values()],
            "watches": [dict(w) for w in st["watches"].values()],
            "facet_status": dict(st["facet_status"]),
        }

    def consult_index(self, token) -> dict:
        """Consult the derived index (open tensions, claims, recent
        events — headers only, never payloads: a payload can carry
        content, and content is served only by open_region). Recorded
        as a DISCOVERY event naming the index path (section 4)."""
        agent = self._authenticate(token)
        self._require_open()
        ev = self._engine.commit_events([(
            "DISCOVERY", agent, [],
            {"path": "index", "region_id": None, "version": None,
             "summary": f"Agent {agent} consulted the index."})])[0]
        self._note_event(ev)
        st = self._authoritative_state()
        recent = self._engine.store.all_events()[-10:]
        return {
            "open_tensions": [
                {"tension_id": t["tension_id"], "type": t["type"],
                 "regions": list(t["regions"]), "status": t["status"]}
                for t in st["tensions"].values() if t["status"] == "open"],
            "claims": [dict(c) for c in st["claims"].values()],
            "recent_events": [
                {"event_seq": e["event_seq"], "type": e["type"],
                 "actor": e["actor"], "affected": e["affected"]}
                for e in recent],
        }

    # -- content reads (sections 4A, 6) ------------------------------
    def open_region(self, token, region_id) -> dict:
        """Serve one region's content, recorded at serve time as a
        DISCOVERY event. The breadth cap is enforced BEFORE serving:
        a refused opening serves nothing and records no read."""
        agent = self._authenticate(token)
        self._require_open()
        st = self._authoritative_state()
        if region_id not in st["regions"]:
            raise HarnessRefusal(f"no such region: {region_id}")
        read = self.read_record.setdefault(agent, {})
        if region_id not in read and len(read) >= MAX_REGIONS_PER_AGENT:
            self.log.append({"kind": "breadth_refusal", "agent": agent,
                             "region_id": region_id})
            raise HarnessRefusal(
                "read-breadth limit: at most two regions' content per "
                "agent per run (section 6)")
        region = st["regions"][region_id]
        ev = self._engine.commit_events([(
            "DISCOVERY", agent, [region_id],
            {"path": "fabric_read", "region_id": region_id,
             "version": region["version"],
             "summary": f"Agent {agent} opened {region['title']} "
                        f"(version {region['version']}) by reading the "
                        f"fabric directly."})])[0]
        self._note_event(ev)
        # A fresh dict of immutable strings: the handle an agent holds
        # can never reach back into fabric state.
        return {"region_id": region_id, "title": region["title"],
                "scope_note": region["scope_note"],
                "content": region["content"], "version": region["version"]}

    def read_breadth(self, agent_id: str) -> float:
        """RB_i from the harness record (section 6). Correction
        round 2 (C2-B2): the region total is the authoritative
        fold's — a fault that drops a region from the live view
        does not shrink the fabric an agent's breadth is measured
        against."""
        self._require_open()
        total = len(self._authoritative_state()["regions"]) or 6
        return len(self.read_record.get(agent_id, {})) / total

    # -- the contribution protocol (section 4) -----------------------
    def submit(self, token, response) -> dict:
        """Run one agent response through the protocol. Returns the
        outcome dict. Raises TransportRefusal for a non-object
        submission and HardLineBreach for a read-record contradiction;
        both append no contribution event."""
        agent = self._authenticate(token)
        self._require_open()
        if not isinstance(response, dict):
            self.log.append({"kind": "transport_refusal", "agent": agent,
                             "detail": "submission was not a JSON object"})
            raise TransportRefusal(
                "submission is not a JSON object; refused at the "
                "interface, no event appended")
        action = response.get("action")
        if action == "idle":
            # A legitimate, recorded outcome (section 4). Since the
            # corrections round it is recorded durably, as its own
            # IDLE event — the between-run amendment settled by Remmy
            # and Vane under Ben's delegation (2026-11-21): idle is
            # event-sourced like everything else the observer may
            # project, never an in-memory log line.
            ev = self._engine.commit_events([(
                "IDLE", agent, [],
                {"summary": f"Agent {agent} chose to idle: it took "
                            f"no action this turn."})])[0]
            return {"outcome": "idle", "event_seq": ev["event_seq"]}
        if action != "contribute":
            return self._reject(agent, None, {
                "outcome": "schema",
                "submitted": response,
                "errors": ["action must be 'contribute' or 'idle'"],
                "summary": "A submission was rejected: its action was "
                           "not a contribution or an idle."})
        contribution = response.get("contribution")
        # Stage 3: every recordable contribution submission is
        # assigned its contribution_id here, before any check, and
        # the id is recorded in whichever outcome event the
        # submission produces — so the completion-claim contract
        # can cite any contribution, accepted or not (section 3
        # gives every Contribution record an id; the claim
        # evidence predicate then refuses to count unaccepted ones).
        contribution_id = str(uuid.uuid4())

        # Step 1a — identity, rejected first and recorded (section 4).
        claimed = (contribution.get("author")
                   if isinstance(contribution, dict) else None)
        if not _is_uuid(claimed) or claimed != agent:
            return self._reject(agent, contribution, {
                "outcome": "identity_mismatch",
                "claimed_author": claimed,
                "summary": "A contribution was rejected: its author "
                           "did not match the identity its token "
                           "authenticates."}, contribution_id)

        # Step 1b — idempotency (section 3; ladder position, step 2).
        idem = contribution.get("idempotency_id")
        if _is_uuid(idem):
            prior = self._idempotency.get((agent, idem))
            if prior is not None:
                if prior["content_hash"] == sha256_hex(
                        canonical(contribution)):
                    return {**prior["outcome"], "idempotent_replay": True}
                return self._reject(agent, contribution, {
                    "outcome": "idempotency_conflict",
                    "summary": "A contribution was rejected: its "
                               "idempotency key was already used for "
                               "different content."}, contribution_id)

        # Step 1c — schema: Annex B.1 plus cross-field rules (i)-(vi).
        errors = self._schema_errors(response, contribution, agent)
        if errors:
            return self._reject(agent, contribution, {
                "outcome": "schema",
                "errors": errors,
                "summary": "A contribution was rejected: it did not "
                           "match the required form."}, contribution_id)

        # Hard line (sections 6, 9): declared reads vs the record.
        declared = set(contribution["read_set"])
        opened = set(self.read_record.get(agent, {}))
        if declared != opened:
            raise HardLineBreach(
                f"declared read set {sorted(declared)} does not match "
                f"the harness read record {sorted(opened)}: reads "
                f"claimed but not made {sorted(declared - opened)}, "
                f"reads made but omitted {sorted(opened - declared)}",
                declared=declared, recorded=opened)

        # Step 2 — staleness, across the read set, with the diff.
        # Correction round (C-B2): staleness reads the
        # authoritative fold, never the possibly corrupted live
        # view; the changed-by record is history-derived as well.
        st = self._authoritative_state()
        diff = []
        for rid in contribution["read_set"]:
            expected = contribution["base_versions"][rid]
            current = st["regions"][rid]["version"]
            if expected != current:
                diff.append({"region_id": rid,
                             "expected_version": expected,
                             "current_version": current,
                             "changed_by": self._last_changed_by.get(rid)})
        if diff:
            names = ", ".join(
                st["regions"][d["region_id"]]["title"] for d in diff)
            return self._reject(agent, contribution, {
                "outcome": "stale",
                "diff": diff,
                "summary": f"A contribution was rejected as stale: "
                           f"{names} had moved past the versions it "
                           f"was based on."},
                affected=[d["region_id"] for d in diff],
                contribution_id=contribution_id)

        # Step 3 — structural, against the closed invariant set.
        violation = self._structural_violation(contribution)
        if violation is not None:
            invariant, records, affected = violation
            return self._reject(agent, contribution, {
                "outcome": "structural",
                "invariant": invariant,
                "records": records,
                "summary": f"A contribution was rejected as "
                           f"structural: it violated invariant "
                           f"{invariant}."},
                affected=affected, contribution_id=contribution_id)

        # Step 4 — commit, atomic, per section 3.
        return self._commit(agent, contribution, contribution_id)

    def _reject(self, agent, contribution, detail, affected=(),
                contribution_id=None):
        payload = {"contribution": contribution}
        if contribution_id is not None:
            payload["contribution_id"] = contribution_id
        payload.update(detail)
        ev = self._engine.commit_events([(
            "CONTRIBUTION_REJECTED", agent, list(affected), payload)])[0]
        self._note_event(ev)
        return {"outcome": detail["outcome"], "event_seq": ev["event_seq"]}

    def _schema_errors(self, response, contribution, agent):
        """Annex B.1 envelope validation, then cross-field rules
        (i)-(vi) in Annex B's order. Returns a list of error strings;
        empty means schema-valid."""
        errors = [e.message for e in
                  sorted(_VALIDATOR.iter_errors(response),
                         key=lambda e: list(e.absolute_path))]
        if errors:
            return errors
        # Envelope is valid; contribution is a dict with typed fields.
        # Correction round (C-B2): the cross-field rules are part
        # of admission — the frozen region set and the dependency
        # records they read come from the authoritative fold, so a
        # contribution may lawfully mention a region the live view
        # has lost to a fault (the round-1 notes' I-5 observation
        # described the pre-correction behaviour).
        st = self._authoritative_state()
        frozen = set(st["regions"])
        read_set = contribution["read_set"]
        write_set = contribution["write_set"]
        read_s, write_s = set(read_set), set(write_set)
        # (i) write_set subset of read_set
        if not write_s <= read_s:
            errors.append(
                f"write_set is not a subset of read_set: "
                f"{sorted(write_s - read_s)}")
        # (ii) base_versions keys are exactly the read set
        if set(contribution["base_versions"]) != read_s:
            errors.append(
                "base_versions keys do not equal the read_set exactly")
        # (iv) every region id appearing anywhere is in the frozen set
        anywhere = set(read_set) | set(write_set) \
            | set(contribution["base_versions"])
        for op in contribution["operations"]:
            if op["kind"] in ("replace_content", "append_content"):
                anywhere.add(op["region_id"])
            elif op["kind"] == "add_dependency":
                anywhere.add(op["dependency"]["source"])
                anywhere.add(op["dependency"]["target"])
            elif op["kind"] == "raise_tension":
                anywhere.update(op["tension"]["regions"])
        unknown = anywhere - frozen
        if unknown:
            errors.append(
                f"region ids outside the frozen set: {sorted(unknown)}")
        # (iii) per-class scope rules and duplicate targets
        content_targets = []
        added = []
        removed = []
        for op in contribution["operations"]:
            kind = op["kind"]
            if kind in ("replace_content", "append_content"):
                if op["region_id"] not in write_s:
                    errors.append(
                        f"content operation targets "
                        f"{op['region_id']}, which is not in write_set")
                content_targets.append(op["region_id"])
            elif kind == "add_dependency":
                dep = op["dependency"]
                endpoints = {dep["source"], dep["target"]}
                if not endpoints <= (read_s & write_s):
                    errors.append(
                        "add_dependency endpoints must both be in "
                        "read_set and write_set")
                triple = (dep["source"], dep["target"], dep["kind"])
                if triple in added:
                    errors.append(
                        f"duplicate add_dependency target in one "
                        f"contribution: {triple}")
                added.append(triple)
                for existing in st["dependencies"].values():
                    if (existing["status"] == "active"
                            and (existing["source"], existing["target"],
                                 existing["kind"]) == triple):
                        errors.append(
                            "add_dependency duplicates an active "
                            "dependency (same source, target, kind)")
            elif kind == "remove_dependency":
                dep_id = op["dependency_id"]
                if dep_id in removed:
                    errors.append(
                        f"duplicate remove_dependency target in one "
                        f"contribution: {dep_id}")
                removed.append(dep_id)
                dep = st["dependencies"].get(dep_id)
                if dep is None:
                    errors.append(
                        f"remove_dependency names an unknown "
                        f"dependency: {dep_id}")
                elif not {dep["source"], dep["target"]} <= (read_s & write_s):
                    errors.append(
                        "remove_dependency endpoints must both be in "
                        "read_set and write_set")
            elif kind == "raise_tension":
                if not set(op["tension"]["regions"]) <= read_s:
                    errors.append(
                        "raise_tension regions must all be in read_set")
        if len(content_targets) != len(set(content_targets)):
            errors.append(
                "more than one content operation targets the same "
                "region in one contribution")
        # (vi) discovery verification (section 4): the referenced
        # DISCOVERY event exists, names this agent, and precedes the
        # submission (it is already in the history).
        ref = contribution["discovery_ref"]
        target = None
        for ev in self._engine.store.all_events():
            if ev["event_seq"] == ref:
                target = ev
                break
        if target is None or target["type"] != "DISCOVERY" \
                or target["actor"] != agent:
            errors.append(
                f"discovery_ref {ref} does not verify: no DISCOVERY "
                f"event with that sequence naming this agent")
        return errors

    def _authoritative_state(self):
        """The authoritative state: the verified fold of the
        committed history, and nothing else (Stage 4 correction
        round, C-B2). Admission validation — the schema's frozen
        region set, staleness, and the structural check — reads
        THIS state, never the engine's operational live state.
        The two coincide on every unfaulted run; they part only
        when a fault has corrupted the live derived state (the
        TV-1 injection), and in that case the fold is the state
        the history actually establishes, while the corrupted
        live state is exactly the snapshot L the seal regime
        judges. Memoised on the history's head hash: any commit
        moves the head and the fold is recomputed."""
        events = self._engine.store.all_events()
        if not events:
            return empty_state()
        head = events[-1]["hash"]
        cache = self._auth_state_cache
        if cache is not None and cache[0] == head:
            return cache[1]
        state = verified_fold(events, CONSTITUTION_HASH)
        self._auth_state_cache = (head, state)
        return state

    def _structural_violation(self, contribution):
        """Apply the operations hypothetically to current state and
        test S1, S2, S3 in the closed set's order (S4 is schema-level
        and was settled in step 1). Returns (invariant, records,
        affected) or None.

        Stage 4 correction round (C-B2): the whole-state scans of
        the accepted Stage 2 implementation (artifact dbdf1769)
        are RESTORED — the hypothetical post-contribution state is
        checked whole for S1 and S3, with no introduced-only
        narrowing. The Stage 4 build round's attribution narrowing
        (recorded as a deviation in the round-1 build notes) was
        rejected at examination: Rev 9 section 4 tests the
        hypothetical state whole, and a contribution may not be
        accepted into a state that still violates S1 or S3. The
        TV-1 problem the narrowing solved is solved instead by
        the choice of state: the check runs against the
        AUTHORITATIVE, history-derived fold (see
        _authoritative_state), which the TV-1 fault — a corruption
        of the live snapshot view only — never touches. A
        violation standing in the authoritative state itself
        (e.g. asserted at genesis) blocks every non-fixing
        contribution and admits the one that fixes it."""
        st = self._authoritative_state()
        # S1 premise: retiring a dependency that is not active.
        for op in contribution["operations"]:
            if op["kind"] == "remove_dependency":
                dep = st["dependencies"].get(op["dependency_id"])
                if dep is not None and dep["status"] != "active":
                    return ("S1",
                            {"dependency_id": op["dependency_id"],
                             "status": dep["status"]},
                            [op["dependency_id"]])
        hypo = copy.deepcopy(st)
        dummy = {"assigned_dependency_ids": {
            str(i): str(uuid.uuid4())
            for i, op in enumerate(contribution["operations"])
            if op["kind"] == "add_dependency"}}
        _apply_operations(hypo, contribution, dummy)
        # S1 — dependency integrity.
        for dep in hypo["dependencies"].values():
            if dep["status"] == "active" and (
                    dep["source"] not in hypo["regions"]
                    or dep["target"] not in hypo["regions"]):
                return ("S1",
                        {"dependency_id": dep["dependency_id"]},
                        [dep["dependency_id"], dep["source"],
                         dep["target"]])
        # S2 — version monotonicity.
        for rid, region in hypo["regions"].items():
            if region["version"] < st["regions"][rid]["version"]:
                return ("S2", {"region_id": rid}, [rid])
        # S3 — pattern acyclicity over uses/constrains/extends.
        graph = {}
        for dep in hypo["dependencies"].values():
            if dep["status"] == "active" and dep["kind"] in _PATTERN_KINDS:
                graph.setdefault(dep["source"], []).append(dep["target"])
        cycle = _find_cycle(graph)
        if cycle:
            proposed = [op["dependency"]
                        for op in contribution["operations"]
                        if op["kind"] == "add_dependency"]
            affected = []
            for rid in cycle:
                if rid not in affected:
                    affected.append(rid)
            return ("S3",
                    {"cycle": cycle, "proposed_dependencies": proposed},
                    affected)
        return None

    def _commit(self, agent, contribution, contribution_id):
        # Correction round 2 (C2-B2): the acceptance summary's
        # titles and the planning entry's sequence come from the
        # authoritative fold, not the live view.
        st = self._authoritative_state()
        assigned_deps = {}
        tension_specs = []
        for i, op in enumerate(contribution["operations"]):
            if op["kind"] == "add_dependency":
                assigned_deps[str(i)] = str(uuid.uuid4())
            elif op["kind"] == "raise_tension":
                tension_specs.append((str(uuid.uuid4()), op["tension"]))
        changed_titles = []
        for rid in contribution["write_set"]:
            title = st["regions"][rid]["title"]
            if title not in changed_titles:
                changed_titles.append(title)
        payload = {
            "contribution_id": contribution_id,
            "contribution": contribution,
            "assigned_dependency_ids": assigned_deps,
            "summary": f"A contribution by agent {agent} was accepted "
                       f"and committed"
                       + (f", changing {', '.join(changed_titles)}."
                          if changed_titles else "."),
        }
        affected = list(contribution["write_set"])
        for _, tension in tension_specs:
            for rid in tension["regions"]:
                if rid not in affected:
                    affected.append(rid)
        specs = [("CONTRIBUTION_ACCEPTED", agent, affected, payload)]
        for tension_id, tension in tension_specs:
            names = ", ".join(st["regions"][r]["title"]
                              for r in tension["regions"])
            specs.append((
                "TENSION_RAISED", agent, list(tension["regions"]),
                {"tension_id": tension_id, "type": "semantic",
                 "regions": list(tension["regions"]),
                 "origin": "contribution", "origin_ref": contribution_id,
                 "description": tension["description"], "status": "open",
                 "summary": f"A semantic tension was raised over "
                            f"{names} by a contribution."}))
        # Stage 3: the accepted contribution is also a trigger for
        # the derived protocols — a contribution can complete a
        # tension's resolution conditions, and it changes the facet
        # accounting of everything it writes. The planning entry is
        # this contribution's registry entry, simulated on a scratch
        # copy of the version simulation so the derived evaluation
        # sees the record as it will stand once the group commits.
        entry = self._contribution_entry(
            agent, st["last_seq"] + 1, payload,
            dict(self._sim_versions), dict(self._sim_deps))
        trigger = {"kind": "contribution", "contribution": contribution,
                   "contribution_entry": entry}
        # Stage 4: on a run bound to the Stage 4 authority set, the
        # accepted commit's group carries a seal attempt (section
        # 7; build notes I-1, I-2).
        events = self._commit_group(
            specs, trigger, seal=self._stage4_bound(),
            seal_actor=agent)
        return {"outcome": "accepted", "contribution_id": contribution_id,
                "event_seq": events[0]["event_seq"]}

    # -- Stage 3: atomic groups and derived transitions --------------
    def _commit_group(self, primary_specs, trigger, seal=False,
                      seal_actor=None):
        """Commit one submission's whole event group atomically:
        the primary outcome event(s), then the derived transitions
        the protocols warrant, evaluated against the state the
        primary events produce. Planning runs against a deep copy
        of the authoritative fold (correction round 2, C2-B2 —
        the round-1 form planned against the live state; the
        paragraph below states the two-hypothetical split); the
        real commit is a single engine transaction, so no partially
        recorded action can survive. Derived transitions are
        emitted deterministically: tension transitions by tension
        id, then facet statuses by region id.

        Stage 4 (seal=True, contribution commits on a Stage-4-bound
        run): after the derived transitions, the group carries one
        seal attempt in the B3 order — SEAL_ATTEMPTED, then the
        structural events the attempt causes. The attempt is
        evaluated by the independent checker process over the
        staged group BEFORE anything commits (Brief Rev 2, B3);
        its verdict decides the recorded outcome. A checker
        failure raises CheckerFailure and nothing commits.

        Correction round 2 (C2-B2): TWO hypotheticals are carried.
        The PLANNING hypothetical — the state the derived
        evaluation runs against — is a deep copy of the
        authoritative fold: commit planning never consumes the
        possibly corrupted live view. The LIVE hypothetical —
        the operational live state with the same staged specs
        applied — is the snapshot source, the one consumer the
        live view still feeds: the seal attempt judges L, fault
        and all. A spec the corrupted live view cannot fold
        (an operation touching the dropped region) leaves the
        live hypothetical at its pre-spec value for that spec;
        on an unfaulted run the guard never fires and the live
        hypothetical is exactly the post-batch live state."""
        hypo = copy.deepcopy(self._authoritative_state())
        live = copy.deepcopy(self._engine.state)
        seq = hypo["last_seq"]
        trigger = dict(trigger)
        trigger["pending_seq"] = seq + 1
        staged = []

        def apply_hypo(spec):
            nonlocal seq, live
            seq += 1
            type_, actor, affected, payload = spec[:4]
            # A spec may carry a pre-minted event_id (closing
            # correction round, CC-1): the staged/planned records
            # then carry the id the committed event will bear.
            minted = spec[4] if len(spec) > 4 else None
            staged.append({"event_seq": seq,
                           "event_id": minted or "staged",
                           "type": type_, "actor": actor,
                           "affected": list(affected),
                           "payload": payload})
            event = {"event_seq": seq,
                     "event_id": minted or "planned",
                     "type": type_, "actor": actor,
                     "affected": list(affected),
                     "payload": payload, "prev_hash": "",
                     "hash": ""}
            apply_event(hypo, event)
            try:
                candidate = copy.deepcopy(live)
                apply_event(candidate, event)
                live = candidate
            except ReplayHalt:
                # The corrupted live view cannot fold this spec
                # (it names state the fault dropped). The snapshot
                # keeps the pre-spec live view for this spec: the
                # divergence the checker must judge is preserved,
                # never papered over by the planning state.
                pass

        for spec in primary_specs:
            apply_hypo(spec)
        derived = []

        def emit(spec):
            derived.append(spec)
            apply_hypo(spec)

        self._evaluate_derived(hypo, trigger, emit)
        specs = list(primary_specs) + derived
        if seal:
            attempt_specs = self._seal_step(
                list(staged), copy.deepcopy(live), seq + 1,
                seal_actor)
            for spec in attempt_specs:
                apply_hypo(spec)
            specs = specs + attempt_specs
        events = self._engine.commit_events(specs)
        for ev in events:
            self._note_event(ev)
        return events

    # -- Stage 4: seal attempts --------------------------------------
    def _stage4_bound(self):
        """True when this run's RUN_OPENED binds the pinned Stage 4
        pack — the seal regime's activation condition (build notes
        I-1). Read once and cached: a run cannot change its
        authority set mid-run (VP-15)."""
        if self._bound_cache is None:
            events = self._engine.store.all_events()
            self._bound_cache = bool(
                events and events[0]["type"] == "RUN_OPENED"
                and binding_is_stage4(events[0]["payload"]))
        return self._bound_cache

    def _invoke_checker(self, staged, snapshot, authenticated_actor):
        """Run the independent checker process for one attempt and
        return its verdict. The committed history reaches the
        checker by store path when the store is file-backed — the
        checker opens the database read-only itself (build notes
        I-8) — and as inline data otherwise. Any process failure
        is CheckerFailure: machinery failure, never a retry."""
        request = {"mode": "evaluate",
                   "constitution_hash": CONSTITUTION_HASH,
                   "staged_batch": staged,
                   "snapshot": snapshot}
        if authenticated_actor is not None:
            request["authenticated_actor"] = authenticated_actor
        store_path = getattr(self._engine.store, "path", None)
        if store_path and store_path != ":memory:" \
                and os.path.exists(store_path):
            request["store_path"] = store_path
        else:
            request["history"] = self._engine.store.all_events()
        command = self.checker_command or [
            sys.executable, "-m", "fabric.checker"]
        package_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        env = dict(os.environ)
        env["PYTHONPATH"] = package_root + os.pathsep \
            + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            proc = subprocess.run(
                command, input=json.dumps(request),
                capture_output=True, text=True, timeout=60, env=env,
                cwd=package_root)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CheckerFailure(
                f"the independent checker could not be run: "
                f"{type(exc).__name__}: {exc}")
        if proc.returncode != 0:
            raise CheckerFailure(
                f"the independent checker process failed "
                f"(rc={proc.returncode}): "
                f"{proc.stderr.strip()[-500:]}")
        try:
            verdict = json.loads(proc.stdout)
        except ValueError:
            raise CheckerFailure(
                "the independent checker answered unparseably: "
                f"{proc.stdout.strip()[-200:]}")
        if not isinstance(verdict, dict) \
                or verdict.get("outcome") not in (
                    "pass", "fail", "mismatch"):
            raise CheckerFailure(
                f"the independent checker returned no usable "
                f"verdict for a staged commit group: {verdict!r}")
        return verdict

    def _seal_step(self, staged, snapshot, attempt_seq,
                   authenticated_actor):
        """Evaluate one seal attempt against the staged group and
        build the group's seal specs: SEAL_ATTEMPTED, then the
        structural TENSION_RAISED / TENSION_STATUS events the
        attempt causes (B3 order). The checker's verdict decides
        the recorded outcome."""
        if self.attempt_observer is not None:
            # Correction round (C-B4): capture the attempt's exact
            # inputs — the committed history as it stands before
            # this group, the staged batch, the snapshot, and the
            # authenticated actor — before the checker is invoked,
            # so the pack harness can replay the identical
            # (H, B, L) through both evaluators.
            self.attempt_observer({
                "history": copy.deepcopy(
                    self._engine.store.all_events()),
                "staged": copy.deepcopy(staged),
                "snapshot": copy.deepcopy(snapshot),
                "authenticated_actor": authenticated_actor,
                "attempt_seq": attempt_seq})
        verdict = self._invoke_checker(staged, snapshot,
                                       authenticated_actor)
        outcome = verdict["outcome"]
        failed = verdict["failed_checks"]
        if outcome == "pass":
            summary = ("A weave seal was attempted after the "
                       "accepted commit and passed: every "
                       "structural check succeeded on the current "
                       "state, and a seal stands at this position. "
                       "The seal certifies structure only; it "
                       "grants no semantic clearance.")
        elif outcome == "fail":
            names = ", ".join(f["check"] for f in failed)
            summary = ("A weave seal was attempted after the "
                       "accepted commit and failed: structural "
                       f"check(s) {names} did not pass on the "
                       "current state. No seal was issued.")
        else:
            summary = ("A weave seal was attempted after the "
                       "accepted commit and could not certify: "
                       "the live derived state diverges from the "
                       "state the event history derives, and no "
                       "structural check explains the divergence. "
                       "No seal was issued.")
        payload = {
            "outcome": outcome,
            "checks_performed": ["S1", "S2", "S3", "event_schema",
                                 "hash_chain"],
            "failed_checks": failed,
            "summary": summary,
        }
        if verdict["divergence"]:
            payload["divergence"] = verdict["divergence"]
        if verdict["attachments"]:
            payload["findings_attached"] = list(
                verdict["attachments"])
        if outcome == "pass":
            seal = dict(verdict["seal"])
            seal["position"] = attempt_seq
            payload["seal"] = seal
        affected = []
        for finding in failed:
            for member in finding["affected"]:
                if member not in affected:
                    affected.append(member)
        # Closing correction round (CC-1/CC-2): the attempt's
        # event_id is minted NOW, before the group commits, and
        # carried into the store as the SEAL_ATTEMPTED event's
        # actual id — so the structural events the attempt causes
        # in the same atomic group can cite the attempt by its id:
        # a raised tension's origin_ref (an id field, section 3)
        # and a resolution's evidence both bind the UUID, never a
        # sequence label.
        attempt_event_id = str(uuid.uuid4())
        specs = [("SEAL_ATTEMPTED", SYSTEM_ACTOR, affected, payload,
                  attempt_event_id)]
        for raise_ in verdict["raises"]:
            names = ", ".join(raise_["affected"])
            specs.append((
                "TENSION_RAISED", SYSTEM_ACTOR,
                list(raise_["regions"]),
                {"tension_id": str(uuid.uuid4()),
                 "type": "structural",
                 "regions": list(raise_["regions"]),
                 "origin": "checker",
                 "origin_ref": attempt_event_id,
                 "description":
                     f"Structural inconsistency found by the "
                     f"independent checker's {raise_['check']} "
                     f"check; affected records: {names}.",
                 "status": "open",
                 "check": raise_["check"],
                 "affected": list(raise_["affected"]),
                 "summary":
                     f"A structural tension was raised by the "
                     f"checker ({raise_['check']}): the records "
                     f"it names are inconsistent in the current "
                     f"state."}))
        for resolution in verdict["resolutions"]:
            specs.append((
                "TENSION_STATUS", SYSTEM_ACTOR,
                [resolution["tension_id"]],
                {"tension_id": resolution["tension_id"],
                 "from": "open", "to": "resolved",
                 "evidence": {
                     "seal_attempt_event_id": attempt_event_id,
                     "seal_attempt_seq": attempt_seq,
                     "check": resolution["check"],
                     "affected": list(resolution["affected"])},
                 "summary":
                     f"A structural tension was resolved: the "
                     f"{resolution['check']} check, re-run against "
                     f"the tension's original affected records by "
                     f"the passing seal attempt at sequence "
                     f"{attempt_seq}, found the inconsistency "
                     f"gone."}))
        return specs

    def close_run(self) -> dict:
        """Close the run (Stage 4): on a Stage-4-bound run, one
        unconditional close-time seal attempt first if the last
        accepted commit was not already followed by an attempt
        (section 7; VP-37/VP-38); then RUN_CLOSED, recording the
        final state hash and the chain head (Brief Rev 2, B7 —
        the anchoring language lives in the build notes, not in
        the record's claims)."""
        self._require_open()
        appended = []
        if self._stage4_bound():
            events = self._engine.store.all_events()
            last_accept = 0
            last_attempt = 0
            for ev in events:
                if ev["type"] == "CONTRIBUTION_ACCEPTED":
                    last_accept = ev["event_seq"]
                elif ev["type"] == "SEAL_ATTEMPTED":
                    last_attempt = ev["event_seq"]
            if last_accept > last_attempt:
                # The close attempt's snapshot is the live view —
                # the one consumer it feeds (correction round 2,
                # C2-B2 boundary statement). Its position and the
                # recorded final hash come from the authoritative
                # fold.
                snapshot = copy.deepcopy(self._engine.state)
                specs = self._seal_step(
                    [], snapshot,
                    self._authoritative_state()["last_seq"] + 1,
                    None)
                appended = self._engine.commit_events(specs)
                for ev in appended:
                    self._note_event(ev)
        head = self._engine.store.last()
        payload = {
            "final_state_hash": state_hash(self._authoritative_state()),
            "chain_head": head[1] if head else None,
            "summary": "The run was closed. Its final state hash "
                       "and chain head stand in this record; what "
                       "an external anchor does and does not "
                       "establish for them is stated in the Stage "
                       "4 build notes (B7), not claimed here.",
        }
        ev = self._engine.commit_events(
            [("RUN_CLOSED", SYSTEM_ACTOR, [], payload)])[0]
        return {"outcome": "closed", "event_seq": ev["event_seq"],
                "close_attempt_events": len(appended)}

    def _evaluation_registry(self, trigger):
        """The contribution registry as the derived evaluation must
        see it: the committed registry plus, for a contribution
        trigger, that contribution's own planning entry."""
        registry = self._contribution_registry
        entry = trigger.get("contribution_entry")
        if entry is not None:
            registry = dict(registry)
            registry[entry["contribution_id"]] = entry
        return registry

    def _evaluate_derived(self, hypo, trigger, emit):
        """Evaluate the tension transition table and the facet
        accounting against the post-primary hypothetical state,
        emitting TENSION_STATUS and FACET_STATUS events for actual
        changes only."""
        registry = self._evaluation_registry(trigger)
        tension_ids = []
        if trigger["kind"] == "assessment" \
                and trigger["assessment"]["target_kind"] == "tension":
            tension_ids = [trigger["assessment"]["target_id"]]
        elif trigger["kind"] == "contribution":
            tension_ids = sorted(
                tid for tid, t in hypo["tensions"].items()
                if t["type"] == "semantic"
                and t["status"] in ("open", "examined"))
        transitioned_regions = []
        for tid in tension_ids:
            regions = hypo["tensions"][tid]["regions"]
            moved = False
            while True:
                spec = self._next_tension_transition(
                    hypo, tid, trigger, registry)
                if spec is None:
                    break
                emit(spec)
                moved = True
            if moved:
                transitioned_regions.extend(regions)
        facets = set(transitioned_regions)
        if trigger["kind"] == "contribution":
            facets.update(trigger["contribution"]["write_set"])
        elif trigger["kind"] == "assessment" \
                and trigger["assessment"]["target_kind"] == "facet":
            facets.add(trigger["assessment"]["target_id"])
        elif trigger["kind"] == "claim":
            facets.add(trigger["claim"]["facet"])
        for rid in sorted(facets):
            new_status, evidence = self._facet_status(
                hypo, rid, registry, trigger)
            old_status = hypo["facet_status"].get(rid, "open")
            if new_status != old_status:
                title = hypo["regions"][rid]["title"]
                emit(("FACET_STATUS", SYSTEM_ACTOR, [rid], {
                    "region_id": rid, "from": old_status,
                    "to": new_status, "evidence": evidence,
                    "summary": f"The facet {title} is now "
                               f"{new_status} (it was {old_status}), "
                               f"on the evidence the record holds."}))

    def _assessment_seqs(self, trigger):
        """assessment_id -> event_seq, including the triggering
        assessment itself at its planned sequence."""
        seqs = dict(self._assessment_seq)
        if trigger["kind"] == "assessment":
            seqs[trigger["assessment"]["assessment_id"]] = \
                trigger["pending_seq"]
        return seqs

    def _next_tension_transition(self, hypo, tension_id, trigger,
                                 registry):
        """The next transition section 4's table warrants for one
        semantic tension, evaluated purely from the record — or
        None. The engine counts recorded positions and checks
        protocol conditions; it judges no meaning."""
        tension = hypo["tensions"].get(tension_id)
        if tension is None or tension["type"] != "semantic":
            return None
        status = tension["status"]
        if status not in ("open", "examined"):
            return None  # resolved and standing are terminal
        seqs = self._assessment_seqs(trigger)
        on_tension = [a for a in hypo["assessments"].values()
                      if a["target_kind"] == "tension"
                      and a["target_id"] == tension_id]
        title = ", ".join(hypo["regions"][r]["title"]
                          for r in tension["regions"])
        if status == "open":
            if not on_tension:
                return None
            first = min(on_tension,
                        key=lambda a: seqs[a["assessment_id"]])
            return ("TENSION_STATUS", SYSTEM_ACTOR, [tension_id], {
                "tension_id": tension_id, "from": "open",
                "to": "examined",
                "evidence": {"assessment_id": first["assessment_id"]},
                "summary": f"The tension over {title} was examined: "
                           f"its first assessment is on record."})
        # status == "examined": resolved is evaluated before
        # standing, in the table's order.
        raised_seq = self._tension_raised_seq.get(tension_id)
        anchor = None
        if raised_seq is not None:
            modifying = [e for e in registry.values()
                         if e["accepted"]
                         and e["event_seq"] > raised_seq
                         and set(e["content_modified"])
                         & set(tension["regions"])]
            if modifying:
                anchor = max(modifying, key=lambda e: e["event_seq"])
        if anchor is not None:
            window = [a for a in on_tension
                      if seqs[a["assessment_id"]] > anchor["event_seq"]]
            latest = {}
            for a in sorted(window,
                            key=lambda a: seqs[a["assessment_id"]]):
                latest[a["author"]] = a
            qualifying = [a for author, a in latest.items()
                          if a["position"] == "addressed"
                          and author != anchor["author"]]
            blocked = any(a["position"] == "remains"
                          for a in latest.values())
            if len(qualifying) >= 2 and not blocked:
                return ("TENSION_STATUS", SYSTEM_ACTOR, [tension_id], {
                    "tension_id": tension_id, "from": "examined",
                    "to": "resolved",
                    "evidence": {
                        "modifying_contribution_id":
                            anchor["contribution_id"],
                        "assessment_ids": sorted(
                            a["assessment_id"] for a in qualifying)},
                    "summary": f"The tension over {title} was "
                               f"resolved under the protocol: its "
                               f"regions were modified and two "
                               f"assessments recorded the work as "
                               f"addressed, with no objection "
                               f"standing."})
        latest_all = {}
        for a in sorted(on_tension,
                        key=lambda a: seqs[a["assessment_id"]]):
            latest_all[a["author"]] = a
        remains = [a for a in latest_all.values()
                   if a["position"] == "remains"]
        if len({a["author"] for a in remains}) >= 2 and not any(
                a["position"] == "addressed"
                for a in latest_all.values()):
            return ("TENSION_STATUS", SYSTEM_ACTOR, [tension_id], {
                "tension_id": tension_id, "from": "examined",
                "to": "standing",
                "evidence": {"assessment_ids": sorted(
                    a["assessment_id"] for a in remains)},
                "summary": f"The tension over {title} was left "
                           f"standing: two or more agents recorded "
                           f"that it remains, and none recorded it "
                           f"as addressed."})
        return None

    def _claim_evidence_valid(self, claim, registry):
        """Section 5's evidence binding, as a fold-computed counting
        predicate — all three conditions (the PIN of Vane's
        examination of brief Rev 3): (1) every cited contribution
        is ACCEPTED — a rejected contribution never supports a
        claim; (2) every cited contribution touched the claimed
        facet (the facet is in its write set, counting dependency
        endpoints per section 4 — endpoints are write-set members
        by the scope rules); (3) the claim's facet_version equals
        the version the latest cited contribution (by event
        sequence) left the facet at."""
        cited = []
        for cid in claim["supporting_contributions"]:
            entry = registry.get(cid)
            if entry is None or not entry["accepted"]:
                return False
            if claim["facet"] not in entry["write_set"]:
                return False
            cited.append(entry)
        latest = max(cited, key=lambda e: e["event_seq"])
        return claim["facet_version"] == \
            latest["version_after"][claim["facet"]]

    def _facet_status(self, hypo, region_id, registry, trigger):
        """Section 5's derived facet status, with the settled
        precedence (complete > stood_down > disputed > claimed >
        unexamined > open), and the evidence that determined it.
        Computed from the record alone; a status is an evidence
        state, never a judgment of adequacy."""
        current = hypo["regions"][region_id]["version"]
        facet_assessments = [a for a in hypo["assessments"].values()
                             if a["target_kind"] == "facet"
                             and a["target_id"] == region_id]
        seqs = self._assessment_seqs(trigger)
        latest = {}
        for a in sorted(facet_assessments,
                        key=lambda a: seqs[a["assessment_id"]]):
            latest[a["author"]] = a
        disputed = [a for a in latest.values()
                    if a["position"] == "disputed"
                    and a["version_reviewed"] == current]
        valid_claims = [
            c for c in hypo["completion_claims"].values()
            if c["facet"] == region_id
            and c["facet_version"] == current
            and self._claim_evidence_valid(c, registry)]
        # 1. complete
        for claim in valid_claims:
            review = next(
                (a for a in facet_assessments
                 if a["position"] == "examined"
                 and a["version_reviewed"] == current
                 and a["author"] != claim["claimant"]), None)
            if review is not None and not disputed:
                return "complete", {
                    "claim_id": claim["claim_id"],
                    "assessment_id": review["assessment_id"]}
        # 2. stood_down — the mapping rule, exactly: required, not
        # complete, and named by a standing semantic tension.
        standing = [t for t in hypo["tensions"].values()
                    if t["type"] == "semantic"
                    and t["status"] == "standing"
                    and region_id in t["regions"]]
        if region_id in SEALED_REQUIRED_FACETS and standing:
            return "stood_down", {
                "tension_ids": sorted(t["tension_id"]
                                      for t in standing)}
        # 3. disputed
        if disputed:
            return "disputed", {
                "assessment_id": disputed[0]["assessment_id"]}
        # 4. claimed
        if valid_claims:
            return "claimed", {"claim_id": valid_claims[0]["claim_id"]}
        # 5. unexamined
        if any(e["accepted"] and region_id in e["write_set"]
               for e in registry.values()):
            return "unexamined", {}
        # 6. open
        return "open", {}

    # -- the section 3 validation ladder (Stage 3) -------------------
    def _run_ladder(self, kind, agent, document):
        """The ONE validation ladder for examine / assess /
        claim_completion, parameterised by action type (brief
        section 3). The checks are evaluated in Rev 9 section 3's
        order; the first failing check determines the recorded
        reason, and later checks are not evaluated. Returns
        ("replay", outcome) for an identical resubmission,
        ("failure", {"stage", "reason", "ctx"}) for the first
        failure, or ("pass", ctx). The event writers consume the
        structured result; they never choose a reason themselves.
        Recordability (step 0) is the caller's: a submission that
        is not a JSON object never reaches the ladder."""
        cfg = _LADDER_KEYS[kind]
        ctx = {}
        # Step 1 — Identity. (Claims carry no author assertion:
        # the authenticated token is the claimant, and the claim
        # schema admits no claimant field to check — the claim
        # settlement, item 1.)
        if kind != "claim":
            claimed = document.get("author") \
                if isinstance(document, dict) else None
            if not _is_uuid(claimed) or claimed != agent:
                return ("failure", {"stage": "identity",
                                    "reason": "identity_mismatch",
                                    "ctx": ctx})
        # Step 2 — Idempotency, in its fixed sub-order: identical
        # replay, then key conflict, then the global record
        # identity. A malformed or absent key can neither match
        # nor replay anything: the step produces no outcome and
        # the submission proceeds to Schema.
        key = document.get(cfg["key"]) \
            if isinstance(document, dict) else None
        if _is_uuid(key):
            prior = self._action_index.get((kind, agent, key))
            if prior is not None:
                if prior["content_hash"] == sha256_hex(
                        canonical(document)):
                    return ("replay", prior["outcome"])
                return ("failure", {"stage": "idempotency",
                                    "reason": cfg["conflict"],
                                    "ctx": ctx})
            record_id = document.get(cfg["record"])
            if _is_uuid(record_id) \
                    and (kind, record_id) in self._record_identities:
                return ("failure", {"stage": "idempotency",
                                    "reason": "identity_collision",
                                    "ctx": ctx})
        # Step 3 — Schema.
        errors = self._ladder_schema_errors(kind, document)
        if errors:
            ctx["schema_errors"] = errors
            return ("failure", {"stage": "schema",
                                "reason": "schema_invalid", "ctx": ctx})
        # Step 4 — Referential.
        reason = self._ladder_referential(kind, document, ctx)
        if reason is not None:
            return ("failure", {"stage": "referential",
                                "reason": reason, "ctx": ctx})
        # Step 5 — Authority and scope.
        reason = self._ladder_authority(kind, agent, document, ctx)
        if reason is not None:
            return ("failure", {"stage": "authority",
                                "reason": reason, "ctx": ctx})
        # Step 6 — State.
        reason = self._ladder_state(kind, agent, document, ctx)
        if reason is not None:
            return ("failure", {"stage": "state",
                                "reason": reason, "ctx": ctx})
        return ("pass", ctx)

    def _ladder_schema_errors(self, kind, document):
        if kind == "claim" and not isinstance(document, dict):
            # The claim settlement's recordability distinction: the
            # top-level submission was a JSON object, but its claim
            # field is missing, malformed, or not an object — that
            # is recordable, and fails here at Schema.
            return ["the claim field is missing or is not a "
                    "JSON object"]
        validator = {"assessment": _ASSESSMENT_VALIDATOR,
                     "examination": _EXAMINATION_VALIDATOR,
                     "claim": _CLAIM_VALIDATOR}[kind]
        return [e.message for e in
                sorted(validator.iter_errors(document),
                       key=lambda e: list(e.absolute_path))]

    def _ladder_referential(self, kind, document, ctx):
        # Correction round 2 (C2-B2): the Stage 3 ladder's
        # referential reads consume the authoritative fold, never
        # the live view — a target the fault dropped from the live
        # view still resolves, because the history still holds it.
        st = self._authoritative_state()
        if kind == "assessment":
            if document["target_kind"] == "tension":
                target = st["tensions"].get(document["target_id"])
            else:
                target = st["regions"].get(document["target_id"])
            if target is None:
                return "target_unresolved"
            ctx["target"] = target
            return None
        if kind == "examination":
            frozen = set(st["regions"])
            if any(r not in frozen for r in document["regions"]):
                return "unknown_region"
            related = document.get("related_tension")
            if related is not None \
                    and related not in st["tensions"]:
                return "related_tension_unresolved"
            return None
        # claim: the facet first, then each supporting contribution
        # (the claim settlement, item 4).
        if document["facet"] not in st["regions"]:
            return "target_unresolved"
        for cid in document["supporting_contributions"]:
            if cid not in self._contribution_registry:
                return "contribution_unresolved"
        return None

    def _ladder_authority(self, kind, agent, document, ctx):
        if kind == "assessment":
            # A schema-valid assessment targeting a structural
            # tension is refused here: structural tensions are
            # outside the assessment system entirely (section 3).
            if document["target_kind"] == "tension" \
                    and ctx["target"]["type"] == "structural":
                return "structural_target"
            return None
        if kind == "examination":
            # Every reported region must appear in the
            # authenticated agent's own read record — and the
            # versions it binds are captured from that record, at
            # the agent's latest opening of each region (brief
            # section 6: an immutable snapshot, stored in the
            # event payload, never a pointer to the mutable record).
            read = self.read_record.get(agent, {})
            if any(r not in read for r in document["regions"]):
                return "region_not_in_read_record"
            ctx["read_versions"] = {
                r: read[r]["last_version"] for r in document["regions"]}
            return None
        return None  # claims: no authority check beyond the token

    def _ladder_state(self, kind, agent, document, ctx):
        # Correction round 2 (C2-B2): the ladder's state reads
        # (facet versions, superseded assessments) likewise read
        # the authoritative fold.
        st = self._authoritative_state()
        if kind == "assessment":
            if document["target_kind"] == "facet" \
                    and document["version_reviewed"] \
                    > st["regions"][document["target_id"]]["version"]:
                return "version_never_existed"
            supersedes = document.get("supersedes")
            if supersedes is not None:
                prior = st["assessments"].get(supersedes)
                if prior is None or prior["author"] != agent \
                        or prior["target_id"] != document["target_id"] \
                        or prior["target_kind"] \
                        != document["target_kind"]:
                    return "supersedes_invalid"
            return None
        if kind == "examination":
            if not self._discovery_verifies(agent,
                                             document["discovery_ref"]):
                return "discovery_unverifiable"
            return None
        # claim: a facet_version beyond the facet's current version
        # names a version that has never existed; a historical
        # version is legitimate and simply fails to count if the
        # evidence binding is not met (claim settlement, item 4).
        if document["facet_version"] \
                > st["regions"][document["facet"]]["version"]:
            return "version_never_existed"
        return None

    def _discovery_verifies(self, agent, ref):
        """Section 4's discovery verification, as the contribution
        protocol applies it: the referenced DISCOVERY event exists,
        names this agent, and precedes the submission (it is
        already in the history)."""
        for ev in self._engine.store.all_events():
            if ev["event_seq"] == ref:
                return ev["type"] == "DISCOVERY" \
                    and ev["actor"] == agent
        return False

    # -- Stage 3 action: examination reports (section 4) -------------
    def examine(self, token, report) -> dict:
        """File an ExaminationReport through the ladder. Returns
        the outcome dict. Raises TransportRefusal for a submission
        that is not a JSON object (no faithful payload exists to
        record — section 4's edge (ii))."""
        agent = self._authenticate(token)
        self._require_open()
        if not isinstance(report, dict):
            self.log.append({"kind": "transport_refusal",
                             "agent": agent,
                             "detail": "examination submission was "
                                       "not a JSON object"})
            raise TransportRefusal(
                "examination submission is not a JSON object; "
                "refused at the interface, no event appended")
        status, result = self._run_ladder("examination", agent, report)
        if status == "replay":
            return {**result, "idempotent_replay": True}
        affected = report["regions"] \
            if isinstance(report.get("regions"), list) and all(
                isinstance(r, str) for r in report["regions"]) else []
        if status == "failure":
            payload = {
                "report": report, "outcome": "rejected",
                "reason": result["reason"], "stage": result["stage"],
                "read_versions": result["ctx"].get(
                    "read_versions", {}),
                "summary": "An examination report was rejected: "
                           f"{result['reason']}."}
            ev = self._engine.commit_events([(
                "EXAMINATION_RECORDED", agent, list(affected),
                payload)])[0]
            self._note_event(ev)
            return {"outcome": "rejected", "reason": result["reason"],
                    "event_seq": ev["event_seq"]}
        ctx = result
        snapshot = ctx["read_versions"]
        st = self._authoritative_state()
        region_set = set(report["regions"])
        # The multi-match duplicate rule (section 4): an identical
        # region set against one or more NON-TERMINAL semantic
        # tensions notes the report against all of them and
        # creates nothing; if only terminal tensions match, the
        # report creates — the recurrence path.
        matches = [t for t in st["tensions"].values()
                   if t["type"] == "semantic"
                   and t["status"] in ("open", "examined")
                   and set(t["regions"]) == region_set]
        names = ", ".join(st["regions"][r]["title"]
                          for r in report["regions"])
        if matches:
            matched_ids = [t["tension_id"] for t in matches]
            payload = {
                "report": report, "outcome": "noted_existing",
                "read_versions": snapshot,
                "matched_tensions": matched_ids,
                "summary": f"An examination of {names} was noted "
                           f"against {len(matched_ids)} existing "
                           f"tension(s) over the same regions; no "
                           f"new tension was created."}
            ev = self._engine.commit_events([(
                "EXAMINATION_RECORDED", agent, list(affected),
                payload)])[0]
            self._note_event(ev)
            return {"outcome": "noted_existing",
                    "matched_tensions": matched_ids,
                    "event_seq": ev["event_seq"]}
        tension_id = str(uuid.uuid4())
        payload = {
            "report": report, "outcome": "created",
            "read_versions": snapshot, "tension_id": tension_id,
            "summary": f"An examination of {names} was recorded "
                       f"and raised a new semantic tension."}
        specs = [
            ("EXAMINATION_RECORDED", agent, list(affected), payload),
            ("TENSION_RAISED", agent, list(report["regions"]), {
                "tension_id": tension_id, "type": "semantic",
                "regions": list(report["regions"]),
                "origin": "examination",
                "origin_ref": report["examination_id"],
                "description": report["description"],
                "status": "open",
                "summary": f"A semantic tension was raised over "
                           f"{names} by an examination report."}),
        ]
        events = self._engine.commit_events(specs)
        for ev in events:
            self._note_event(ev)
        return {"outcome": "created", "tension_id": tension_id,
                "event_seq": events[0]["event_seq"]}

    # -- Stage 3 action: assessments (section 3) ----------------------
    def assess(self, token, assessment) -> dict:
        """Record an Assessment through the ladder. Exactly one
        ASSESSMENT_RECORDED event per recordable submission;
        derived tension/facet transitions ride in the same atomic
        group."""
        agent = self._authenticate(token)
        self._require_open()
        if not isinstance(assessment, dict):
            self.log.append({"kind": "transport_refusal",
                             "agent": agent,
                             "detail": "assessment submission was "
                                       "not a JSON object"})
            raise TransportRefusal(
                "assessment submission is not a JSON object; "
                "refused at the interface, no event appended")
        status, result = self._run_ladder("assessment", agent,
                                          assessment)
        if status == "replay":
            return {**result, "idempotent_replay": True}
        if status == "failure":
            payload = {
                "assessment": assessment, "outcome": "rejected",
                "reason": result["reason"], "stage": result["stage"],
                "summary": "An assessment was rejected: "
                           f"{result['reason']}."}
            affected = [assessment["target_id"]] \
                if isinstance(assessment.get("target_id"), str) else []
            ev = self._engine.commit_events([(
                "ASSESSMENT_RECORDED", agent, affected, payload)])[0]
            self._note_event(ev)
            return {"outcome": "rejected", "reason": result["reason"],
                    "event_seq": ev["event_seq"]}
        payload = {
            "assessment": assessment, "outcome": "recorded",
            "summary": f"An assessment of a "
                       f"{assessment['target_kind']} was recorded, "
                       f"position {assessment['position']}."}
        specs = [("ASSESSMENT_RECORDED", agent,
                  [assessment["target_id"]], payload)]
        events = self._commit_group(
            specs, {"kind": "assessment", "assessment": assessment})
        return {"outcome": "recorded",
                "event_seq": events[0]["event_seq"]}

    # -- Stage 3 action: completion claims (the claim contract) -------
    def claim_completion(self, token, envelope) -> dict:
        """File a CompletionClaim. `envelope` is the top-level
        submission (the data-socket request): a top-level value
        that is not a JSON object is a transport refusal; a JSON
        object whose claim field is missing, malformed, or not an
        object is recordable and fails at Schema, with the raw
        claim value preserved in the rejection event (the claim
        settlement, item 2)."""
        agent = self._authenticate(token)
        self._require_open()
        if not isinstance(envelope, dict):
            self.log.append({"kind": "transport_refusal",
                             "agent": agent,
                             "detail": "claim submission was not a "
                                       "JSON object"})
            raise TransportRefusal(
                "claim submission is not a JSON object; refused at "
                "the interface, no event appended")
        document = envelope.get("claim")
        status, result = self._run_ladder("claim", agent, document)
        if status == "replay":
            return {**result, "idempotent_replay": True}
        affected = [document["facet"]] \
            if isinstance(document, dict) \
            and isinstance(document.get("facet"), str) else []
        if status == "failure":
            payload = {
                "claim": document, "claimant": agent,
                "outcome": "rejected", "reason": result["reason"],
                "stage": result["stage"],
                "summary": "A completion claim was rejected: "
                           f"{result['reason']}."}
            ev = self._engine.commit_events([(
                "COMPLETION_CLAIMED", agent, affected, payload)])[0]
            self._note_event(ev)
            return {"outcome": "rejected", "reason": result["reason"],
                    "event_seq": ev["event_seq"]}
        payload = {
            "claim": document, "claimant": agent,
            "outcome": "recorded",
            "summary": "A completion claim was recorded; whether "
                       "it counts is a matter of the evidence "
                       "binding, computed from the record."}
        specs = [("COMPLETION_CLAIMED", agent, affected, payload)]
        events = self._commit_group(
            specs, {"kind": "claim", "claim": document})
        return {"outcome": "recorded",
                "event_seq": events[0]["event_seq"]}


def _find_cycle(graph):
    """Return one cycle as a list of nodes (start repeated at the
    end), or None. Deterministic: nodes visited in sorted order."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {node: WHITE for node in graph}
    stack = []

    def visit(node):
        colour[node] = GREY
        stack.append(node)
        for nxt in sorted(graph.get(node, [])):
            if nxt not in colour:
                colour[nxt] = WHITE
            if colour[nxt] == GREY:
                return stack[stack.index(nxt):] + [nxt]
            if colour[nxt] == WHITE:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        colour[node] = BLACK
        return None

    for node in sorted(graph):
        if colour[node] == WHITE:
            found = visit(node)
            if found:
                return found
    return None
