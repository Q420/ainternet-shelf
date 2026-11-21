"""Stage 6 — K10 attribution: Test 6 case 1 (one failure,
one attribution record, referenced identically by closure,
ledger and adjudication), the pinned-authority gate, and
Test 6 case 3 (an attempted label-to-class conversion
refused).

Run: python3 -m unittest discover -s ~/workspace/duenna-fix/stage6/tests -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage1"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "stage3"))

from record import EventRecord  # noqa: E402
from authority import (  # noqa: E402
    AuthorityRefused, GovernanceAuthorityRecord,
    issue_authority, make_test_authority_record)
from attribution import (  # noqa: E402
    AttributionLedger, AttributionRefused, ConversionRefused,
    RecordIntegrityRefused, SYSTEM, MODEL,
    adjudication_view, closure_view, convert_local_label,
    ledger_view)
from stage6_support import fresh_record, issued_authority  # noqa: E402

FAILURE = "run-1:event-37"


class TestOneFailureOneRecord(unittest.TestCase):
    """Test 6, case 1: one failure, one attribution record,
    referenced identically by closure, ledger and
    adjudication."""

    def setUp(self):
        self.record, self.path = fresh_record(self)
        self.ledger = AttributionLedger(self.record,
                                        issued_authority())

    def test_three_surfaces_reference_the_same_record(self):
        minted = self.ledger.mint_attribution(
            FAILURE, SYSTEM, basis_refs=["finding:event-9"])
        views = [closure_view(self.record, FAILURE),
                 ledger_view(self.record, FAILURE),
                 adjudication_view(self.record, FAILURE)]
        # Identical reference, identical class, on all three.
        self.assertEqual(
            {v["attribution_event"] for v in views},
            {minted["digest"]})
        self.assertEqual({v["class"] for v in views}, {SYSTEM})
        self.assertEqual({v["surface"] for v in views},
                         {"closure", "ledger", "adjudication"})

    def test_views_read_the_fact_back_from_disk(self):
        self.ledger.mint_attribution(FAILURE, SYSTEM,
                                     basis_refs=["finding:event-9"])
        # A fresh record object over the same file: the views
        # show the fact because the RECORD holds it, not
        # because any live object remembers minting it.
        reopened = EventRecord(self.path)
        view = closure_view(reopened, FAILURE)
        self.assertEqual(view["class"], SYSTEM)
        readback = AttributionLedger(
            reopened, issued_authority()).attribution_for(FAILURE)
        self.assertEqual(view["attribution_event"],
                         readback["attribution_event"])
        self.assertEqual(readback["body"]["basis_refs"],
                         ["finding:event-9"])
        self.assertEqual(readback["body"]["attributor"],
                         "TEST-AUTHORITY-STAGE6")

    def test_second_mint_for_one_failure_refused(self):
        self.ledger.mint_attribution(FAILURE, SYSTEM,
                                     basis_refs=["finding:event-9"])
        with self.assertRaises(AttributionRefused):
            self.ledger.mint_attribution(
                FAILURE, MODEL, basis_refs=["finding:event-10"])
        # The one record still stands, unaltered.
        self.assertEqual(
            self.ledger.attribution_for(FAILURE)["body"]["class"],
            SYSTEM)

    def test_class_outside_vocabulary_refused(self):
        with self.assertRaises(AttributionRefused):
            self.ledger.mint_attribution(
                FAILURE, "SUBJECT", basis_refs=[])

    def test_no_attribution_yet_reads_as_none(self):
        self.assertIsNone(self.ledger.attribution_for(FAILURE))
        self.assertIsNone(
            closure_view(self.record, FAILURE)["attribution_event"])


class TestPinnedAuthority(unittest.TestCase):
    """K10: the adjudicator's authority must resolve to the
    pinned governance record; a component cannot self-appoint."""

    def test_genuine_record_issues(self):
        authority = issue_authority(make_test_authority_record())
        self.assertEqual(authority.authority_id,
                         "TEST-AUTHORITY-STAGE6")

    def test_self_appointed_record_refused(self):
        impostor = GovernanceAuthorityRecord(
            authority_id="COMPONENT-SELF-APPOINTED",
            holder="the-checker-itself",
            instrument="self-authored",
            rules="whatever the component prefers")
        with self.assertRaises(AuthorityRefused):
            issue_authority(impostor)

    def test_mutated_genuine_record_refused(self):
        genuine = make_test_authority_record()
        mutated = GovernanceAuthorityRecord(
            genuine.authority_id, "someone-else",
            genuine.instrument, genuine.rules)
        with self.assertRaises(AuthorityRefused):
            issue_authority(mutated)

    def test_ledger_requires_the_issued_capability(self):
        record, _ = fresh_record(self)
        with self.assertRaises(AttributionRefused):
            AttributionLedger(record, make_test_authority_record())
        with self.assertRaises(AttributionRefused):
            AttributionLedger(record, object())


class TestLabelConversionRefused(unittest.TestCase):
    """Test 6, case 3: an attempted label-to-class conversion
    is refused. The historical labels are preserved AS LOCAL;
    they are not attributions and cannot become any."""

    def setUp(self):
        self.record, self.path = fresh_record(self)
        self.ledger = AttributionLedger(self.record,
                                        issued_authority())

    def test_every_conversion_attempt_raises(self):
        for label in ("SUBJECT_FAILURE", "GOVERNANCE_FAILURE"):
            for target in (SYSTEM, MODEL, "INPUT", "UNKNOWN"):
                with self.assertRaises(ConversionRefused):
                    convert_local_label(label, target)

    def test_label_preserved_as_local_not_attribution(self):
        self.ledger.record_local_label(FAILURE, "SUBJECT_FAILURE")
        # Preserved, and explicitly local...
        events = self.record.read_all()
        labels = [e for e in events
                  if e["type"] == "LOCAL_LABEL_RECORDED"]
        self.assertEqual(len(labels), 1)
        self.assertIn("not an attribution",
                      labels[0]["body"]["status"])
        # ...and no attribution exists for the failure: the
        # label did not become one by being recorded.
        self.assertIsNone(self.ledger.attribution_for(FAILURE))


class TestRecordDiscipline(unittest.TestCase):
    """A mint onto a record whose chain no longer verifies
    raises and writes nothing (Stages 1–3 discipline)."""

    def test_tampered_record_refuses_and_stays_byte_identical(self):
        record, path = fresh_record(self)
        ledger = AttributionLedger(record, issued_authority())
        ledger.mint_attribution("run-1:event-1", SYSTEM,
                                basis_refs=[])
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        body = json.loads(lines[0])
        body["body"]["class"] = "MODEL"  # tamper, digest retained
        lines[0] = json.dumps(body, ensure_ascii=False) + "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        with open(path, "rb") as f:
            before = f.read()
        with self.assertRaises(RecordIntegrityRefused):
            ledger.mint_attribution(FAILURE, SYSTEM, basis_refs=[])
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)


if __name__ == "__main__":
    unittest.main()
