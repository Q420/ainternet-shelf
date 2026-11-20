"""Stage 2 — the plan's Test 2 sabotages, each exercised separately.

Every sabotage is presented to the REAL artefact path (the
constructor and the G2 close in construction.py — never a ledger
projection) and construction must REFUSE to close in every case.
Each test asserts not just refusal but that the refusal names the
differing field identities (G2's evidence requirement).

The sabotages, per PROCESS-TREE-AND-PLAN.md v2, Stage 2:
(a) direct assignment of artifact/evidence reintroduced;
(b) fixtures_total renamed;
(c) a ledger entry dropped while the field retained;
(d) an extra entry outside the schema;
(e) the canonical path bypassed;
(f) (v2 addition) a schema-required field absent from BOTH the
    artefact and its provenance entries.

Correction round (Gate 1, 2026-11-20 — VANE-GATE1-VERDICT.md,
finding 3): sabotage (e) tests a FOREIGN event type. It does not
test a forged event using the very type the provenance stream
trusts. Three cases are added, each reported separately:
(g) a complete, schema-matching PROVENANCE_ENTRY set appended
    directly through the generic record API, bypassing the
    canonical writer — the actual constructor must refuse it;
(mixed) genuine writer-issued entries plus ONE forged
    generic-append entry — the forgery poisons the close;
(malformed) malformed canonical-type bodies — recorded, controlled
    refusal, never an uncaught exception or accidental admission.

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage2/tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
from record import EventRecord  # noqa: E402
from schema import TEST_SCHEMA  # noqa: E402
from construction import (  # noqa: E402
    CONSTRUCTION_CLOSED,
    CONSTRUCTION_REFUSED,
    PROVENANCE_ENTRY,
    ConstructionRefused,
    ProvenanceLog,
    build_from_entries,
    construct_artefact,
    construction_close,
)
from test_construction import VALUES  # noqa: E402


class TestStage2Sabotages(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "record.jsonl")
        self.record = EventRecord(self.path)
        self.log = ProvenanceLog(self.record)

    def tearDown(self):
        self.tmp.cleanup()

    def _enter(self, artefact_id, fields):
        for field in fields:
            self.log.append_entry(artefact_id, field, VALUES[field])

    def _closed_events(self):
        return [ev for ev in self.record.read_all()
                if ev["type"] == CONSTRUCTION_CLOSED]

    def _refused_events(self):
        return [ev for ev in self.record.read_all()
                if ev["type"] == CONSTRUCTION_REFUSED]

    # (a) Direct assignment of artifact/evidence reintroduced.
    # The DR-02 mechanism: the artefact carries artifact/evidence as
    # literal values assigned outside the entry path; no provenance
    # entries exist for them. The close must refuse, naming exactly
    # those two fields as present in the artefact without an entry.
    def test_sabotage_a_direct_assignment_refused(self):
        entered = [f for f in VALUES
                   if f not in ("artifact", "evidence")]
        self._enter("ART-A", entered)
        entries = self.log.issued_entries("ART-A")
        # The sabotaged artefact: built from entries, then artifact
        # and evidence assigned directly as literals (the old
        # _construct path's exact move).
        artefact = build_from_entries(entries)
        artefact["artifact"] = "assigned-literal"
        artefact["evidence"] = "assigned-literal"
        with self.assertRaises(ConstructionRefused) as ctx:
            construction_close(artefact, entries, TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details[
                "fields_in_artefact_without_entry"],
            ["artifact", "evidence"])

    # (b) fixtures_total renamed (to fixtures_executed — DR-02's
    # exact failure). Artefact and entries agree with each other
    # perfectly; only the schema, as third party, can catch it:
    # fixtures_total is required and absent, fixtures_executed is
    # outside the schema. End-to-end through the constructor.
    def test_sabotage_b_fixtures_total_renamed_refused(self):
        for field, value in VALUES.items():
            name = ("fixtures_executed" if field == "fixtures_total"
                    else field)
            self.log.append_entry("ART-B", name, value)
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-B", TEST_SCHEMA)
        details = ctx.exception.details
        self.assertEqual(details["schema_fields_absent_from_both"],
                         ["fixtures_total"])
        self.assertEqual(details["entry_fields_outside_schema"],
                         ["fixtures_executed"])
        self.assertEqual(details["artefact_fields_outside_schema"],
                         ["fixtures_executed"])
        self.assertEqual(self._closed_events(), [])

    # (c) A ledger/provenance entry dropped while the field is
    # retained in the artefact. The artefact was faithfully built
    # from the full entry set; at close, one entry is missing. The
    # close must refuse, naming the retained field as having no
    # entry.
    def test_sabotage_c_dropped_entry_field_retained_refused(self):
        self._enter("ART-C", list(VALUES))
        entries = self.log.issued_entries("ART-C")
        artefact = build_from_entries(entries)
        dropped = [e for e in entries
                   if e["field"] != "fixtures_total"]
        self.assertEqual(len(dropped), len(entries) - 1)
        with self.assertRaises(ConstructionRefused) as ctx:
            construction_close(artefact, dropped, TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details[
                "fields_in_artefact_without_entry"],
            ["fixtures_total"])
        self.assertEqual(
            ctx.exception.details[
                "schema_fields_missing_from_entries"],
            ["fixtures_total"])

    # (d) An extra entry outside the schema. Artefact and entries
    # agree; the schema refuses the ninth field. End-to-end through
    # the constructor.
    def test_sabotage_d_extra_entry_outside_schema_refused(self):
        self._enter("ART-D", list(VALUES))
        self.log.append_entry("ART-D", "fixtures_executed", 8)
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-D", TEST_SCHEMA)
        details = ctx.exception.details
        self.assertEqual(details["entry_fields_outside_schema"],
                         ["fixtures_executed"])
        self.assertEqual(details["artefact_fields_outside_schema"],
                         ["fixtures_executed"])
        self.assertEqual(self._closed_events(), [])

    # (e) The canonical path bypassed. Provenance-shaped content is
    # placed on the record under a foreign event type, never via
    # the canonical writer. It is not provenance: the constructor
    # reads none of it and construction refuses to close — even
    # though a compare-after check against the fabricated content
    # would have found matching fields.
    def test_sabotage_e_canonical_path_bypassed_refused(self):
        for field, value in VALUES.items():
            self.record.append("LEDGER_ENTRY", {
                "artefact_id": "ART-E",
                "field": field,
                "value": value,
            })
        self.assertEqual(self.log.issued_entries("ART-E"), [])
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-E", TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["schema_fields_absent_from_both"],
            sorted(TEST_SCHEMA.artefact_fields))
        self.assertEqual(self._closed_events(), [])

    # (f) A schema-required field absent from BOTH the artefact and
    # its provenance entries (the plan's v2 addition). Artefact and
    # entries are exactly equal to each other — pairwise equality
    # holds — and construction must STILL refuse, because the frozen
    # schema is a third party to the comparison. End-to-end through
    # the constructor.
    def test_sabotage_f_field_absent_from_both_refused(self):
        entered = [f for f in VALUES if f != "fixtures_total"]
        self._enter("ART-F", entered)
        entries = self.log.issued_entries("ART-F")
        artefact = build_from_entries(entries)
        # Pairwise equality genuinely holds — that is the point of
        # this sabotage.
        self.assertEqual(set(artefact),
                         {e["field"] for e in entries})
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-F", TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["schema_fields_absent_from_both"],
            ["fixtures_total"])
        self.assertEqual(self._closed_events(), [])

    # Value-level companion: names agree everywhere, one value
    # differs between the artefact and its entry. Exact equality is
    # names AND values (G2), so the close refuses and names the
    # field.
    def test_value_mismatch_refused(self):
        self._enter("ART-V", list(VALUES))
        entries = self.log.issued_entries("ART-V")
        artefact = build_from_entries(entries)
        artefact["fixtures_passed"] = VALUES["fixtures_passed"] - 1
        with self.assertRaises(ConstructionRefused) as ctx:
            construction_close(artefact, entries, TEST_SCHEMA)
        self.assertEqual(ctx.exception.details["value_mismatches"],
                         ["fixtures_passed"])

    # (g) THE GATE 1 CASE: a forged canonical-type event set.
    # A complete, schema-matching set of PROVENANCE_ENTRY events is
    # appended directly through the generic record API
    # (record.append), bypassing the canonical writer entirely.
    # The bodies are exactly right — field for field, value for
    # value — so any check that merely compares contents would
    # admit them. The actual constructor must refuse: none of these
    # events was issued by the canonical writer, and provenance
    # authority, not content equality, is what the boundary
    # enforces. The refusal must be recorded on the record.
    def test_sabotage_g_forged_canonical_events_refused(self):
        for field, value in VALUES.items():
            self.record.append(PROVENANCE_ENTRY, {
                "artefact_id": "ART-G",
                "field": field,
                "value": value,
            })
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-G", TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["unissued_provenance_events"],
            list(range(1, len(VALUES) + 1)))
        self.assertEqual(len(self._refused_events()), 1)
        self.assertEqual(self._closed_events(), [])

    # (mixed) Genuine writer-issued entries plus ONE forged
    # generic-append entry. The genuine set alone would close; the
    # single forgery poisons the close — it never sneaks in beside
    # legitimate provenance.
    def test_mixed_genuine_and_forged_entries_refused(self):
        self._enter("ART-M", list(VALUES))
        forged = self.record.append(PROVENANCE_ENTRY, {
            "artefact_id": "ART-M",
            "field": "fixtures_total",
            "value": VALUES["fixtures_total"],
        })
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-M", TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["unissued_provenance_events"],
            [forged["seq"]])
        self.assertEqual(len(self._refused_events()), 1)
        self.assertEqual(self._closed_events(), [])

    # (malformed) Malformed canonical-type bodies, appended through
    # the generic record API: a body missing field/value, a field
    # that names nothing, an unhashable field, and bodies that are
    # not dicts at all. None was issued by the canonical writer.
    # Construction must produce a recorded, controlled refusal —
    # ConstructionRefused naming every offending event by seq —
    # never an uncaught exception and never accidental admission.
    def test_malformed_canonical_bodies_controlled_refusal(self):
        bodies = [
            {"artefact_id": "ART-X"},
            {"artefact_id": "ART-X", "field": None, "value": 1},
            {"artefact_id": "ART-X", "field": ["x"], "value": 1},
            {"field": "artifact", "value": "no-artefact-id"},
            "not-a-dict",
            None,
        ]
        seqs = [self.record.append(PROVENANCE_ENTRY, body)["seq"]
                for body in bodies]
        with self.assertRaises(ConstructionRefused) as ctx:
            construct_artefact(self.log, "ART-X", TEST_SCHEMA)
        self.assertEqual(
            ctx.exception.details["unissued_provenance_events"],
            seqs)
        self.assertEqual(len(self._refused_events()), 1)
        self.assertEqual(self._closed_events(), [])


if __name__ == "__main__":
    unittest.main()
