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

The constructor reads provenance entries ONLY from the record, via
:func:`read_provenance_entries`. Entries reach the record ONLY via
:func:`append_provenance_entry`, the canonical entry path: an event
of any other type carrying field/value-shaped content is not a
provenance entry and is never read as one.

Design references: ID-SYSTEM-DESIGN-DRAFT-V3.md (K5, G2),
PROCESS-TREE-AND-PLAN.md v2, Stage 2; DEFECT-REGISTER.md DR-02.
"""

from __future__ import annotations

import hashlib
from typing import Any

from record import _canonical

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


# -- the canonical provenance-entry path -------------------------------


def append_provenance_entry(record, artefact_id: str, field: str,
                            value: Any) -> dict:
    """Append one field-provenance entry to the Stage 1 record.

    This is the ONLY way provenance enters the record. The entry
    body carries the artefact identity, the field name (the schema's
    name, by reference) and the field's value. Returns the recorded
    event dict.
    """
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
    return record.append(PROVENANCE_ENTRY, {
        "artefact_id": artefact_id,
        "field": field,
        "value": value,
    })


def read_provenance_entries(record, artefact_id: str) -> list[dict]:
    """Read the provenance entries for ``artefact_id`` from the
    record, in record order. Only ``PROVENANCE_ENTRY`` events are
    provenance; events of any other type are ignored, however their
    bodies are shaped. Returns a list of entry dicts with keys
    ``field`` and ``value`` (plus the source event's ``seq``)."""
    entries = []
    for ev in record.read_all():
        if ev.get("type") != PROVENANCE_ENTRY:
            continue
        body = ev.get("body")
        if not isinstance(body, dict):
            continue
        if body.get("artefact_id") != artefact_id:
            continue
        entries.append({
            "field": body.get("field"),
            "value": body.get("value"),
            "seq": ev.get("seq"),
        })
    return entries


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
    """Builds artefacts from a record's provenance entries and
    closes construction on them. The constructor is the whole
    canonical path: entries are read from the record (never
    supplied by the caller), the artefact is built from those
    entries (never assigned), and the close is G2's three-way
    comparison against the frozen schema."""

    def __init__(self, record, schema):
        self.record = record
        self.schema = schema

    def construct(self, artefact_id: str) -> dict:
        """Construct and close one artefact. On success appends a
        CONSTRUCTION_CLOSED event and returns the artefact dict.
        On any refusal appends a CONSTRUCTION_REFUSED event with
        the differing field identities and raises
        :class:`ConstructionRefused`."""
        entries = read_provenance_entries(self.record, artefact_id)
        try:
            artefact = build_from_entries(entries)
            evidence = construction_close(artefact, entries,
                                          self.schema)
        except ConstructionRefused as refused:
            details = refused.details
            self.record.append(CONSTRUCTION_REFUSED, {
                "artefact_id": artefact_id,
                "schema_digest": self.schema.digest,
                "differing": details,
            })
            raise ConstructionRefused(artefact_id, details) from None
        self.record.append(CONSTRUCTION_CLOSED, {
            "artefact_id": artefact_id,
            "schema_digest": evidence["schema_digest"],
            "fields": evidence["fields"],
            "values_digest": evidence["values_digest"],
        })
        return artefact


def construct_artefact(record, artefact_id: str, schema) -> dict:
    """Convenience: construct and close ``artefact_id`` on
    ``record`` under ``schema``."""
    return ArtefactConstructor(record, schema).construct(artefact_id)
