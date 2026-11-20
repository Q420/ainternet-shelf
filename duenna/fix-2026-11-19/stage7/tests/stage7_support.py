"""Stage 7 test support: a fresh record, package, issuer
store, issuer and pinned anchor per test, all under one
temporary directory. The issuer is built from the TEST
fixture constants (trust_anchor.py); the anchor is the
verifier's independent pin of the issuer the harness
recognises, obtained through the verifier's pinned-store
path (make_test_anchor) — since correction round 1 the
anchor constructor is restricted to that path, and the
harness verifier obtains its pin the same way the
mechanism requires. Attacker material is built in the
tests themselves from different keys/terms.
"""

import os
import tempfile

from record import EventRecord

from package import ResultPackage
from receipts import IssuerStore, ReceiptIssuer
from trust_anchor import TEST_ISSUER_ID, TEST_KEY, TEST_TERMS, \
    make_test_anchor


def fresh_setup(testcase):
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    record = EventRecord(os.path.join(tmp.name, "record.jsonl"))
    package = ResultPackage(os.path.join(tmp.name, "package"))
    store = IssuerStore(os.path.join(tmp.name, "issuer-store"))
    issuer = ReceiptIssuer(TEST_ISSUER_ID, TEST_KEY, TEST_TERMS)
    anchor = make_test_anchor()
    return record, package, store, issuer, anchor
