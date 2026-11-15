#!/usr/bin/env python3
"""CorpusSource — the pilot's single corpus interface (Harness §3.1).

Exactly one implementation: a reader over PILOT-CORPUS-SNAPSHOT-01
(the pinned snapshot, verified at Batch 0 and re-verified at the
Batch 0 re-run) plus the pilot-manifest data (the PILOT-DATA-*-01
files, Batch 1). The tools import this interface and nothing else:
no trial runner, no live index, no home-tree path. After Batch 0
the bridge index folder is out of the pilot's runtime path
entirely — constructing this object reads only the two directories
it is handed.

    get_section(source_ref)     -> {section_id, doc, heading_path,
                                    sha256, text} | NOT FOUND
    get_manifest_row(source_ref) -> {row fields} | NOT FOUND

Namespaces: a bare section id resolves against the corpus;
a `pilot-manifest:` prefix resolves against the pilot data files.
NOT FOUND is a returned value of the declared shape, never an
exception and never a fabricated record:
    {"verification": "NOT FOUND", "source_ref": ref,
     "failure_reason": str}
"""
import json, pathlib


class CorpusSource:
    def __init__(self, snapshot_dir, data_dir):
        snap = pathlib.Path(snapshot_dir)
        self._sections = {}
        for line in open(snap / "sections.jsonl"):
            s = json.loads(line)
            self._sections[s["section_id"]] = s
        self._manifest = json.loads((snap / "manifest.json").read_text())
        data = pathlib.Path(data_dir)
        self._data = {}
        for name in ("PILOT-DATA-PACKS-01", "PILOT-DATA-EXPECTED-01",
                     "PILOT-DATA-T09-01", "PILOT-DATA-FIXTURES-01"):
            self._data[name] = json.loads((data / f"{name}.json").read_text())

    @staticmethod
    def _not_found(ref, reason):
        return {"verification": "NOT FOUND", "source_ref": ref,
                "failure_reason": reason}

    def get_section(self, source_ref):
        if ":" in source_ref:
            return self._not_found(
                source_ref,
                "get_section takes a bare section id; "
                "pilot-manifest: refs resolve via get_manifest_row")
        s = self._sections.get(source_ref)
        if s is None:
            return self._not_found(source_ref,
                                   f"no such section: {source_ref}")
        return {"section_id": s["section_id"], "doc": s["doc"],
                "heading_path": s["heading_path"], "sha256": s["sha256"],
                "text": s["text"]}

    def get_manifest_row(self, source_ref):
        if source_ref.startswith("pilot-manifest:"):
            body = source_ref.split(":", 1)[1]
            if "#" not in body:
                doc = self._data.get(body)
                if doc is None:
                    return self._not_found(source_ref,
                                           f"no such data file: {body}")
                return {"ref": source_ref, "file": body, "value": doc}
            fname, key = body.split("#", 1)
            doc = self._data.get(fname)
            if doc is None:
                return self._not_found(source_ref,
                                       f"no such data file: {fname}")
            if key.startswith("receipt-"):
                r = doc.get("RECEIPTS", {}).get(key[len("receipt-"):])
                if r is None:
                    return self._not_found(source_ref,
                                           f"no such receipt: {key}")
                return {"ref": source_ref, "file": fname, "key": key,
                        "value": r}
            if key == "obligation-spec-text":
                return {"ref": source_ref, "file": fname, "key": key,
                        "value": doc["obligation_spec_text"]}
            if key == "t01-pack-manifest-reference":
                return {"ref": source_ref, "file": fname, "key": key,
                        "value": doc["t01_pack_manifest_reference"]}
            v = doc.get("fixtures", {}).get(key)
            if v is None:
                return self._not_found(source_ref,
                                       f"no such fixture: {key}")
            return {"ref": source_ref, "file": fname, "key": key,
                    "value": v}
        # a bare doc id resolves to its row in the corpus manifest
        for row in self._manifest.get("documents", []):
            if row.get("doc") == source_ref or \
                    row.get("id") == source_ref:
                return {"ref": source_ref, "value": row}
        return self._not_found(source_ref,
                               f"no manifest row for: {source_ref}")
