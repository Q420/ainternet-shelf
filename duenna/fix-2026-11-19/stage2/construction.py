"""Duenna Stage 2 — artefact construction and construction close.

Two operations, kept separate because they are different operations
(K5):

(a) ARTEFACT CONSTRUCTION — the artefact-producing path builds the
    artefact FROM canonical field-provenance entries held on the
    Stage 1 record (``PROVENANCE_ENTRY`` events). It does not build
    an independent dictionary and compare it afterwards. Each
    produced field resolves to exactly one provenance entry; a field
    with no entry cannot be produced, and there is no parameter,
    attribute or side path by which a literal value can be assigned
    into an artefact. This is the path DR-02's mechanism bypassed:
    ``artifact``/``evidence`` were set to None, filtered out of the
    ledgered insertion, then assigned as literal values, and
    ``fixtures_total`` was mapped to the name ``fixtures_executed``.

(b) CONSTRUCTION CLOSE (G2) — per artefact, the gate at the F5 edge.
    Inputs: the artefact, its provenance entries, the frozen schema.
    The close is a THREE-WAY exact comparison — names AND values —
    of the artefact's fields, the provenance entries, and the frozen
    schema's artefact section. The schema is a third party to every
    comparison, not a bystander: a schema-required field absent from
    BOTH the artefact and its provenance entries still fails the
    close, because equality between two incomplete representations
    is not schema completeness. Pass: the three field sets are
    exactly equal and every shared value agrees; construction
    closes and a ``CONSTRUCTION_CLOSED`` event is appended to the
    record. Fail: construction does not close; a
    ``CONSTRUCTION_REFUSED`` event carrying the differing field
    identities is appended, and :class:`ConstructionRefused` is
    raised. The LEDGER PROJECTION (K5(b)) — materialising record
    events into a ledger view — is a different operation; nothing
    here reads or proves anything about a projection.

THE CANONICAL PROVENANCE BOUNDARY (Gate 1 correction round,
2026-11-20). The first submission named a free function,
``append_provenance_entry``, "the canonical entry path" and had the
reader trust the ``PROVENANCE_ENTRY`` type string. But Stage 1's
``EventRecord.append`` accepts any event type and body, so a caller
could append a forged, complete, schema-matching
``PROVENANCE_ENTRY`` event directly through the generic record API
and the constructor would accept it: "canonical" was a description
of convention, not an enforced property (VANE-GATE1-VERDICT.md,
finding 3 — FAIL).

The correction makes the boundary a capability. :class:`ProvenanceLog`
is the canonical writer: the sole issuer of provenance entries. It
keeps a registry of exactly what it issued — per artefact, the
ordered (field, value) pairs together with the record event digests
returned at append time. The Stage 1 record is hash-chained, so
each digest binds its entry to the exact event (seq, predecessor,
type, body) the record accepted. :class:`ArtefactConstructor` takes
the writer, not the raw record — there is no construction path from
the record alone. Before building, the constructor verifies the
record against the registry:

- any ``PROVENANCE_ENTRY`` event on the record whose digest the
  writer did not issue — forged, malformed, or another writer's —
  refuses construction. A forgery poisons the close; it never
  sneaks in, and it is never merely compared after the fact: the
  refusal is about provenance authority, not content equality.
- any entry the writer issued for the artefact that is missing
  from, or altered on, the record refuses construction.

Only after verification are the artefact's entries taken from the
registry, built from, and closed by G2's three-way comparison —
whose semantics are exactly as examined in the first submission.

CORRECTION ROUND 2 (Gate 1, 2026-11-20 —
VANE-GATE1-VERDICT-CORRECTION-ROUND-2.md). The first correction
compared the record's STORED digests against the registry — but a
stored digest is itself only a claim. ``read_all`` does not verify
the chain, so an issued event whose body was edited in place, its
stored digest retained, still matched the registry while the
record itself was corrupted: the claimed binding to the exact
event currently on the record was not established. Now
:meth:`ProvenanceLog.verify` first recomputes the record's chain
over the events as they currently stand (Stage 1's
``verify_chain``, which recomputes every digest from seq, prev,
type and body). A retained-digest body edit fails recomputation;
construction refuses, naming the first bad seq, before any digest
is trusted. Only a verified chain's digests are compared against
the registry.

HONEST BOUNDARY: enforcement holds where the canonical writer is
the sole issuer within the construction process. A fresh writer
over a reloaded record has an empty registry and refuses
everything (fail-closed): continuity of the writer IS the
provenance authority in this harness. Wholesale replacement of the
record itself is outside this boundary — the same out-of-scope
class as Stage 1's C3 limitation (a coordinated record+anchor
rewrite is not defeated), which belongs to the external anchor,
not to this stage. Precisely: chain verification detects edits
and deletions of events; it does not, by itself, detect a
wholesale rewrite that re-chains from genesis (``verify_chain``'s
own stated limit — the external anchor's job). Within the
construction process, however, a content-changing re-chain still
fails the writer-registry comparison, because the registry is
held by the writer, not the record: the recomputed digests are
digests this writer never issued.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K5, G2),
PROCESS-TREE-AND-PLAN.md v2, Stage 2; DEFECT-REGISTER.md DR-02;
VANE-GATE1-VERDICT.md (Stage 2), finding 3 and required
resubmission.
"""

from __future__ import annotations

import hashlib
from typing import Any

from record import _canonical, verify_chain

PROVENANCE_ENTRY = "PROVENANCE_ENTRY"
CONSTRUCTION_CLOSED = "CONSTRUCTION_CLOSED"
CONSTRUCTION_REFUSED = "CONSTRUCTION_REFUSED"


class ConstructionRefused(Exception):
    """Construction did not close. Carries the G2 evidence: the
    differing field identities, in ``details``."""

    def __init__(self, artefact_id: str, details: dict):
        self.artefact_id = artefact_id
        self.details = details
        super().__init__(
            f"construction refused for artefact {artefact_id!r}: "
            f"{details!r}")


# -- the canonical writer ------------------------------------------------


class ProvenanceLog:
    """The canonical writer — the SOLE issuer of provenance entries
    on a record, and the capability construction requires.

    ``append_entry`` is the only path by which provenance enters
    the record *as provenance*: it validates the entry, appends it
    through the record's generic append, and registers exactly what
    it issued — the artefact identity, the ordered (field, value)
    pair, and the appended event's seq and digest. Because the
    Stage 1 record is hash-chained, the digest binds the registry
    entry to the exact event on the record.

    The generic record API remains what Stage 1 made it — an
    unrestricted append. What changed is that construction no
    longer trusts it: :meth:`verify` first recomputes the record's
    chain over the events as they currently stand, then
    cross-checks the record's whole ``PROVENANCE_ENTRY`` stream
    against this registry, and :class:`ArtefactConstructor`
    refuses to operate without this writer. An event the writer
    did not issue is not provenance, whatever its type string or
    body claims.
    """

    def __init__(self, record):
        self.record = record
        # artefact_id -> [{"field", "value", "seq", "digest"}, ...]
        # in issue order.
        self._issued: dict[str, list[dict]] = {}
        # Every digest this writer has issued, across artefacts.
        self._issued_digests: set[str] = set()

    def append_entry(self, artefact_id: str, field: str,
                     value: Any) -> dict:
        """Issue one field-provenance entry: validate it, append it
        to the record, and register it as issued by this writer.
        Returns the recorded event dict."""
        if not isinstance(artefact_id, str) or not artefact_id.strip():
            raise ValueError(
                f"artefact_id must name something: {artefact_id!r}")
        if not isinstance(field, str) or not field.strip():
            raise ValueError(f"field must name something: {field!r}")
        try:
            _canonical(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"provenance value for field {field!r} is not "
                f"JSON-encodable: {exc}") from exc
        event = self.record.append(PROVENANCE_ENTRY, {
            "artefact_id": artefact_id,
            "field": field,
            "value": value,
        })
        self._issued.setdefault(artefact_id, []).append({
            "field": field,
            "value": value,
            "seq": event["seq"],
            "digest": event["digest"],
        })
        self._issued_digests.add(event["digest"])
        return event

    def issued_entries(self, artefact_id: str) -> list[dict]:
        """The entries this writer issued for ``artefact_id``, in
        issue order: dicts with keys ``field`` and ``value`` (plus
        the source event's ``seq``). This — not a scan of the raw
        record — is the provenance stream construction builds
        from, and :meth:`verify` establishes that the record's
        stream is exactly this one."""
        return [{
            "field": entry["field"],
            "value": entry["value"],
            "seq": entry["seq"],
        } for entry in self._issued.get(artefact_id, [])]

    def verify(self, artefact_id: str) -> dict:
        """Cross-check the record against this writer's registry.
        Returns a dict of boundary violations; empty iff the
        record's current chain verifies, its provenance stream is
        exactly what this writer issued, and this artefact's
        issued entries are all present on the record, unaltered,
        in issue order.

        The checks, in order. The first is prior to the other two:
        no digest is trusted until it passes.

        - CHAIN INTEGRITY (first): the record's chain is
          recomputed over the events as they currently stand
          (Stage 1's ``verify_chain``). A stored digest is a
          claim, not evidence — an issued event whose body was
          edited in place, its stored digest retained, fails
          recomputation, because the digest is recomputed from
          the CURRENT body. If the chain does not verify, the
          sole violation returned is
          ``record_chain_verification_failed`` naming the first
          bad seq, and no digest on the broken chain is compared
          against the registry at all.

        The remaining two checks are not content comparisons of a
        suspect event (the verdict's instruction: the issue is
        provenance authority, not equality of contents):

        - SOLE ISSUER (global): every ``PROVENANCE_ENTRY`` event on
          the record must carry a digest this writer issued. Any
          other such event — a forged canonical-type event, a
          malformed canonical-type body, another writer's entry —
          is foreign matter in the provenance stream and is named
          by seq under ``unissued_provenance_events``. Body shape
          is inspected only defensively (a non-dict body cannot
          crash the check); attribution is by digest, never by
          trusting the body's claims.
        - REGISTRY COMPLETENESS (per artefact): the digests of the
          record's ``PROVENANCE_ENTRY`` events for ``artefact_id``,
          in record order, must equal the registry's digests for
          that artefact, in issue order. Because each digest binds
          (seq, predecessor, type, body), equality of the digest
          sequence establishes that every issued entry is present
          with its exact field and value; any issued digest absent
          from the record is named under
          ``issued_entries_missing_or_altered``.
        """
        problems: dict = {}
        events = self.record.read_all()
        chain_ok, first_bad_seq = verify_chain(events)
        if not chain_ok:
            return {"record_chain_verification_failed": first_bad_seq}
        provenance_events = [
            ev for ev in events
            if ev.get("type") == PROVENANCE_ENTRY
        ]
        unissued = sorted(
            ev["seq"] for ev in provenance_events
            if ev.get("digest") not in self._issued_digests)
        if unissued:
            problems["unissued_provenance_events"] = unissued
        registry_digests = [
            entry["digest"]
            for entry in self._issued.get(artefact_id, [])
        ]
        record_digests = []
        for ev in provenance_events:
            body = ev.get("body")
            if isinstance(body, dict) \
                    and body.get("artefact_id") == artefact_id:
                record_digests.append(ev.get("digest"))
        if record_digests != registry_digests:
            missing = [d for d in registry_digests
                       if d not in record_digests]
            if missing:
                problems["issued_entries_missing_or_altered"] = \
                    missing
            else:
                problems["issued_entries_mismatch"] = {
                    "issued": registry_digests,
                    "on_record": record_digests,
                }
        return problems


# -- construction from entries (K5(a)) -----------------------------------


def build_from_entries(entries: list[dict]) -> dict:
    """Build the artefact FROM provenance entries — the only
    construction. Each field resolves to exactly one entry: a field
    with two entries cannot be produced (ConstructionRefused), and
    a field with no entry is simply not in the artefact — the close
    (G2), not the builder, judges whether that is acceptable."""
    artefact: dict = {}
    duplicates = []
    for entry in entries:
        field = entry.get("field")
        if field in artefact:
            duplicates.append(field)
        else:
            artefact[field] = entry.get("value")
    if duplicates:
        raise ConstructionRefused(
            "<build>", {"duplicate_entries": sorted(set(duplicates))})
    return artefact


# -- construction close (G2) ---------------------------------------------


def _differing(artefact: dict, entries: list[dict],
               schema) -> dict:
    """The three-way comparison. Returns a dict of differing field
    identities; empty iff the three parties agree exactly (names
    and values). Every key names one way the parties can differ,
    so a refusal records WHICH fields differ, never just that
    something did."""
    entry_fields: dict = {}
    duplicate_entries = []
    for entry in entries:
        field = entry.get("field")
        if field in entry_fields:
            duplicate_entries.append(field)
        else:
            entry_fields[field] = entry.get("value")

    artefact_set = set(artefact)
    entry_set = set(entry_fields)
    schema_set = set(schema.artefact_fields)

    differing: dict = {}
    if duplicate_entries:
        differing["duplicate_entries"] = sorted(set(duplicate_entries))
    # The schema as third party: required fields missing from BOTH
    # representations are caught here — artefact_set == entry_set
    # does not save them.
    missing = sorted(schema_set - artefact_set - entry_set)
    if missing:
        differing["schema_fields_absent_from_both"] = missing
    only_artefact = sorted(artefact_set - entry_set)
    if only_artefact:
        differing["fields_in_artefact_without_entry"] = only_artefact
    only_entries = sorted(entry_set - artefact_set)
    if only_entries:
        differing["fields_in_entries_not_in_artefact"] = only_entries
    not_schema_a = sorted(artefact_set - schema_set)
    if not_schema_a:
        differing["artefact_fields_outside_schema"] = not_schema_a
    not_schema_e = sorted(entry_set - schema_set)
    if not_schema_e:
        differing["entry_fields_outside_schema"] = not_schema_e
    missing_a = sorted((schema_set & entry_set) - artefact_set)
    if missing_a:
        differing["schema_fields_missing_from_artefact"] = missing_a
    missing_e = sorted((schema_set & artefact_set) - entry_set)
    if missing_e:
        differing["schema_fields_missing_from_entries"] = missing_e
    value_mismatches = sorted(
        field for field in (artefact_set & entry_set)
        if artefact[field] != entry_fields[field])
    if value_mismatches:
        differing["value_mismatches"] = value_mismatches
    return differing


def construction_close(artefact: dict, entries: list[dict],
                       schema) -> dict:
    """G2 construction close: the three-way exact comparison of
    artefact, provenance entries and frozen schema (names AND
    values). Returns the close evidence dict on success; raises
    :class:`ConstructionRefused` carrying the differing field
    identities on any mismatch."""
    differing = _differing(artefact, entries, schema)
    if differing:
        raise ConstructionRefused("<close>", differing)
    return {
        "fields": sorted(artefact),
        "schema_digest": schema.digest,
        "values_digest": hashlib.sha256(
            _canonical(artefact)).hexdigest(),
    }


# -- the artefact-producing path -----------------------------------------


class ArtefactConstructor:
    """Builds artefacts from provenance entries issued by a
    :class:`ProvenanceLog` and closes construction on them.

    The constructor takes the canonical writer as a capability —
    there is no construction path from the raw record alone. The
    whole path is: verify the record's current chain, then verify
    the record against the writer's registry (the canonical
    provenance boundary), take the artefact's entries from the
    registry, build the artefact from those entries (never
    assigned), and close by G2's three-way comparison against the
    frozen schema."""

    def __init__(self, log: ProvenanceLog, schema):
        self.log = log
        self.record = log.record
        self.schema = schema

    def _record_refusal(self, artefact_id: str, details: dict):
        self.record.append(CONSTRUCTION_REFUSED, {
            "artefact_id": artefact_id,
            "schema_digest": self.schema.digest,
            "differing": details,
        })

    def construct(self, artefact_id: str) -> dict:
        """Construct and close one artefact. On success appends a
        CONSTRUCTION_CLOSED event and returns the artefact dict.
        On any refusal — a boundary violation at verification, or
        a differing three-way comparison at the close — appends a
        CONSTRUCTION_REFUSED event carrying the evidence and raises
        :class:`ConstructionRefused`."""
        problems = self.log.verify(artefact_id)
        if problems:
            self._record_refusal(artefact_id, problems)
            raise ConstructionRefused(artefact_id, problems)
        entries = self.log.issued_entries(artefact_id)
        try:
            artefact = build_from_entries(entries)
            evidence = construction_close(artefact, entries,
                                          self.schema)
        except ConstructionRefused as refused:
            details = refused.details
            self._record_refusal(artefact_id, details)
            raise ConstructionRefused(artefact_id, details) from None
        self.record.append(CONSTRUCTION_CLOSED, {
            "artefact_id": artefact_id,
            "schema_digest": evidence["schema_digest"],
            "fields": evidence["fields"],
            "values_digest": evidence["values_digest"],
        })
        return artefact


def construct_artefact(log: ProvenanceLog, artefact_id: str,
                       schema) -> dict:
    """Convenience: construct and close ``artefact_id`` under
    ``schema``, from the provenance issued by the canonical writer
    ``log``."""
    return ArtefactConstructor(log, schema).construct(artefact_id)
