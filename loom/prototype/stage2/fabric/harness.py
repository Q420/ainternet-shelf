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

Every Stage 2 event payload carries a plain-words "summary" of the
event, so the payload alone is enough to describe what happened (the
observer UI's only projection is the event history).
"""
import copy
import re
import uuid

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.validators import RefResolver

from .canonical import canonical, sha256_hex
from .engine import _apply_operations

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
    the submission merely rejected."""


class Harness:
    def __init__(self, engine):
        self._engine = engine
        self._tokens = {}          # token -> agent_id
        # Harness log: transport refusals, idles, breadth refusals —
        # the record of what never became an event (section 4).
        self.log = []
        # agent_id -> {region_id: {"openings", "last_version", "last_seq"}}
        self.read_record = {}
        # region_id -> contribution_id that last changed it (or None)
        self._last_changed_by = {}
        # (author, idempotency_id) -> {"content_hash", "outcome"}
        self._idempotency = {}
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
                for d_id, d in self._engine.state["dependencies"].items()}
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

    def _note_event(self, ev):
        if ev["type"] == "DISCOVERY":
            self._note_discovery(ev)
        elif ev["type"] == "CONTRIBUTION_ACCEPTED":
            self._note_accepted(ev)
        elif ev["type"] == "CONTRIBUTION_REJECTED":
            self._note_rejected(ev)

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

    # -- views (section 6: the pattern; no content, no breadth) -----
    def view_pattern(self, token) -> dict:
        """The pattern: exactly the closed section 6 enumeration —
        ids, titles, scope notes, edges, tension/claim/watch headers,
        versions, last-changed-by. Never content."""
        self._authenticate(token)
        st = self._engine.state
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
        ev = self._engine.commit_events([(
            "DISCOVERY", agent, [],
            {"path": "index", "region_id": None, "version": None,
             "summary": f"Agent {agent} consulted the index."})])[0]
        self._note_event(ev)
        st = self._engine.state
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
        st = self._engine.state
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
        """RB_i from the harness record (section 6)."""
        total = len(self._engine.state["regions"]) or 6
        return len(self.read_record.get(agent_id, {})) / total

    # -- the contribution protocol (section 4) -----------------------
    def submit(self, token, response) -> dict:
        """Run one agent response through the protocol. Returns the
        outcome dict. Raises TransportRefusal for a non-object
        submission and HardLineBreach for a read-record contradiction;
        both append no contribution event."""
        agent = self._authenticate(token)
        if not isinstance(response, dict):
            self.log.append({"kind": "transport_refusal", "agent": agent,
                             "detail": "submission was not a JSON object"})
            raise TransportRefusal(
                "submission is not a JSON object; refused at the "
                "interface, no event appended")
        action = response.get("action")
        if action == "idle":
            # A legitimate, recorded outcome (section 4) — recorded in
            # the harness log; the section 3 event enum has no idle
            # type. See the Stage 2 build notes.
            self.log.append({"kind": "idle", "agent": agent})
            return {"outcome": "idle", "event_seq": None}
        if action != "contribute":
            return self._reject(agent, None, {
                "outcome": "schema",
                "submitted": response,
                "errors": ["action must be 'contribute' or 'idle'"],
                "summary": "A submission was rejected: its action was "
                           "not a contribution or an idle."})
        contribution = response.get("contribution")

        # Step 1a — identity, rejected first and recorded (section 4).
        claimed = (contribution.get("author")
                   if isinstance(contribution, dict) else None)
        if not _is_uuid(claimed) or claimed != agent:
            return self._reject(agent, contribution, {
                "outcome": "identity_mismatch",
                "claimed_author": claimed,
                "summary": "A contribution was rejected: its author "
                           "did not match the identity its token "
                           "authenticates."})

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
                               "different content."})

        # Step 1c — schema: Annex B.1 plus cross-field rules (i)-(vi).
        errors = self._schema_errors(response, contribution, agent)
        if errors:
            return self._reject(agent, contribution, {
                "outcome": "schema",
                "errors": errors,
                "summary": "A contribution was rejected: it did not "
                           "match the required form."})

        # Hard line (sections 6, 9): declared reads vs the record.
        declared = set(contribution["read_set"])
        opened = set(self.read_record.get(agent, {}))
        if declared != opened:
            raise HardLineBreach(
                f"declared read set {sorted(declared)} does not match "
                f"the harness read record {sorted(opened)}: reads "
                f"claimed but not made {sorted(declared - opened)}, "
                f"reads made but omitted {sorted(opened - declared)}")

        # Step 2 — staleness, across the read set, with the diff.
        st = self._engine.state
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
                affected=[d["region_id"] for d in diff])

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
                affected=affected)

        # Step 4 — commit, atomic, per section 3.
        return self._commit(agent, contribution)

    def _reject(self, agent, contribution, detail, affected=()):
        payload = {"contribution": contribution}
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
        st = self._engine.state
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

    def _structural_violation(self, contribution):
        """Apply the operations hypothetically to current state and
        test S1, S2, S3 in the closed set's order (S4 is schema-level
        and was settled in step 1). Returns (invariant, records,
        affected) or None."""
        st = self._engine.state
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

    def _commit(self, agent, contribution):
        st = self._engine.state
        contribution_id = str(uuid.uuid4())
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
        events = self._engine.commit_events(specs)
        for ev in events:
            self._note_event(ev)
        return {"outcome": "accepted", "contribution_id": contribution_id,
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
