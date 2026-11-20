"""Duenna Stage 7 — the result package (K6's COLLECTED
boundary).

DR-04's failure happened at this boundary: issuance events
and SHA-256 values existed on the session record, but the
receipt contents were absent from the result package, so no
commitment could be independently verified. The package is
therefore a first-class artefact in this stage, not a
detail: a receipt is COLLECTED exactly when its content has
entered THIS package, and that fact is established by
reading the package back — never from a live object's memory
of having written it.

The package is a directory on disk:

    <root>/receipts/<receipt_id>.json     the receipt entry:
                                          the issuance facts as
                                          carried by the
                                          package, plus the
                                          issuer's
                                          authentication tag
    <root>/receipts/<receipt_id>.content  the collected
                                          content bytes,
                                          present only after
                                          collection

Every read goes back to disk. Removal is literal: deleting
a receipt's files removes it from the package, and the
lifecycle derivation (receipts.py) reports that state as
MISSING_FROM_PACKAGE — distinct from an entry that exists
but was never collected into.
"""

from __future__ import annotations

import json
import os


class ResultPackage:
    """A directory-backed result package. Holds no cached
    state: each method reads or writes the files as they
    stand, so what the package is at any moment is what its
    files say."""

    def __init__(self, root: str):
        self.root = root

    # -- paths ------------------------------------------------

    def _receipts_dir(self) -> str:
        return os.path.join(self.root, "receipts")

    def entry_path(self, receipt_id: str) -> str:
        return os.path.join(self._receipts_dir(),
                            receipt_id + ".json")

    def content_path(self, receipt_id: str) -> str:
        return os.path.join(self._receipts_dir(),
                            receipt_id + ".content")

    # -- writes ------------------------------------------------

    def _write_atomic(self, path: str, data: bytes) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def write_entry(self, receipt_id: str, entry: dict) -> None:
        """Write (or replace) a receipt's package entry."""
        self._write_atomic(
            self.entry_path(receipt_id),
            json.dumps(entry, ensure_ascii=False, sort_keys=True)
            .encode("utf-8"))

    def write_content(self, receipt_id: str,
                      content: bytes) -> None:
        """Place a receipt's content into the package — the
        act of collection at this boundary."""
        self._write_atomic(self.content_path(receipt_id),
                           bytes(content))

    def remove_receipt(self, receipt_id: str) -> None:
        """Remove a receipt from the package entirely (entry
        and content). A legitimate package operation — and
        the Test 7 removal case."""
        for path in (self.entry_path(receipt_id),
                     self.content_path(receipt_id)):
            if os.path.exists(path):
                os.remove(path)

    # -- reads (always from disk) ------------------------------

    def read_entry(self, receipt_id: str) -> dict | None:
        path = self.entry_path(receipt_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def read_content(self, receipt_id: str) -> bytes | None:
        path = self.content_path(receipt_id)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def has_entry(self, receipt_id: str) -> bool:
        return os.path.exists(self.entry_path(receipt_id))

    def has_content(self, receipt_id: str) -> bool:
        return os.path.exists(self.content_path(receipt_id))

    def entry_ids(self) -> list[str]:
        """The receipt identities the package currently
        carries entries for, read from the directory as it
        stands."""
        directory = self._receipts_dir()
        if not os.path.isdir(directory):
            return []
        return sorted(
            name[:-len(".json")]
            for name in os.listdir(directory)
            if name.endswith(".json"))
