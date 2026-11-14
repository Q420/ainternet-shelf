#!/usr/bin/env python3
"""Correction 6 driver patch: T02 §3.1 construction per the
approved plan Revs 2-4. Anchored; each anchor asserted once."""
import pathlib

p = pathlib.Path.home() / "workspace/ssh-door/batch3-correction2" / \
    "pilot_driver.py"
s = p.read_text()

def rep(old, new, name):
    global s
    assert s.count(old) == 1, f"anchor: {name} ({s.count(old)})"
    s = s.replace(old, new)
    print("OK", name)

old_ws = '''    def op_t02_build_worksheet(self, key, step, state):
        rows = []
        for ref, cls in (("d3-v010-change-record#007", "implementer"),
                         ("claude-verification-report-v010#001a",
                          "examiner"),
                         (ADJ_V010, "adjudicator")):
            _, sec = self.tools.shelf_lookup(ref)
            text = sec.get("text", "")
            quote = next((ln for ln in text.splitlines()
                          if "R60" in ln and ln.strip()), "")
            if cls == "adjudicator":
                res = self._extract(key, step["step_id"], ADJ_R60,
                                    "correction_b")
                state["t02_adjudication"] = res.get("value")
                state["t02_adjudication_extraction"] = res
            rows.append({"source": ref, "class": cls, "claim": quote,
                         "verbatim": quote in text})
        state["t02_rows"] = rows
        ok = all(r["verbatim"] and r["claim"] for r in rows)
        return {"progress": [{"worksheet_row": r} for r in rows],
                "outputs": {"worksheet": rows},
                "check": {"compared": {"rows": len(rows),
                                       "all_verbatim": ok},
                          "passed": ok}}
'''
new_ws = '''    @staticmethod
    def _t02_span(cls, text):
        """Amendment Draft 02 §3.1 span + boundary-derived
        standing for one T02 source (Correction Plan Revs
        2-4). Returns (span, standing), or (None, reason)
        on any boundary failure — fail-closed, no fallback,
        no claim-text interpretation."""
        if cls == "implementer":
            cands = [ln for ln in text.splitlines()
                     if re.search(r"\\d+ fixtures executed,", ln)]
            if len(cands) != 1:
                return None, "IMPLEMENTER_CANDIDATES"
            if not re.search(
                    r"\\*\\*(\\d+) fixtures executed, \\1 PASS, "
                    r"0 FAIL\\*\\*", cands[0]):
                return None, "IMPLEMENTER_MALFORMED"
            return cands[0], "CLOSED"
        if cls == "examiner":
            phrase = "R60 fails as a whole"
            if text.count(phrase) != 1:
                return None, "EXAMINER_PHRASE"
            i = text.index(phrase)
            return text[i:text.index(".", i) + 1], "OPEN"
        if cls == "adjudicator":
            cands = [ln for ln in text.splitlines()
                     if ln.startswith("- **R60 — ")]
            if len(cands) != 1:
                return None, "ADJUDICATOR_CANDIDATES"
            if not re.match(r"- \\*\\*R60 — (PASS|FAIL)\\.\\*\\*",
                            cands[0]):
                return None, "ADJUDICATOR_MALFORMED"
            j = text.index(cands[0])
            nxt = text.find("\\n- **", j + 1)
            span = text[j:] if nxt == -1 else text[j:nxt]
            m = re.findall(r"\\*\\*R60 — (PASS|FAIL)", span)
            if len(m) != 1:
                return None, "ADJUDICATOR_DERIVATION"
            return span, ("OPEN" if m[0] == "FAIL" else "CLOSED")
        return None, "UNKNOWN_CLASS"

    def op_t02_build_worksheet(self, key, step, state):
        # References from the pinned pack in pack order;
        # classes parsed from the loaded T02-STEP-01 text;
        # both verified before any pairing (Plan Rev 2 §C).
        refs = [e["section"]
                for e in self.packs["trees"]["T02"]["pack"]]
        step01 = next(s for s in self.trees["T02"]["steps"]
                      if s["step_id"] == "T02-STEP-01")
        text01 = step01["text"]
        stems = (("implementer", "implementer"),
                 ("examiner", "examiner"),
                 ("adjudicat", "adjudicator"))
        found = sorted((text01.index(stem), cls)
                       for stem, cls in stems if stem in text01)
        classes = [cls for _, cls in found]
        state["t02_classes"] = classes
        if len(refs) != 3 or classes != ["implementer",
                                         "examiner",
                                         "adjudicator"]:
            state["t02_rows"] = []
            state["t02_standings"] = []
            return {"progress": [], "outputs": {},
                    "check": {"compared": {"refs": len(refs),
                                           "classes": classes},
                              "passed": False}}
        rows = []
        standings = []
        failure = None
        for ref, cls in zip(refs, classes):
            _, sec = self.tools.shelf_lookup(ref)
            text = sec.get("text", "")
            span, standing = self._t02_span(cls, text)
            if span is None:
                failure = {"class": cls, "source": ref,
                           "reason": standing}
                break
            if cls == "adjudicator":
                res = self._extract(key, step["step_id"], ADJ_R60,
                                    "correction_b")
                state["t02_adjudication"] = res.get("value")
                state["t02_adjudication_extraction"] = res
            rows.append({"source": ref, "class": cls,
                         "claim": span,
                         "verbatim": span in text})
            standings.append(standing)
        if failure is not None:
            state["t02_rows"] = []
            state["t02_standings"] = []
            return {"progress": [], "outputs": {},
                    "check": {"compared": {"boundary_failure":
                                           failure},
                              "passed": False}}
        state["t02_rows"] = rows
        state["t02_standings"] = standings
        ok = all(r["verbatim"] and r["claim"] for r in rows)
        return {"progress": [{"worksheet_row": r} for r in rows],
                "outputs": {"worksheet": rows},
                "check": {"compared": {"rows": len(rows),
                                       "all_verbatim": ok},
                          "passed": ok}}
'''
rep(old_ws, new_ws, "worksheet")

old_cmp = '''    def op_t02_compare(self, key, step, state):
        def implied(row):
            c = row["claim"].upper()
            if "NOT APPROVED" in c or "FAIL" in c or "OPEN" in c:
                return "OPEN"
            return "CLOSED"
        rows = state["t02_rows"]
        conflicts = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if implied(rows[i]) != implied(rows[j]):
                    conflicts.append(
                        {"pair": [rows[i]["class"], rows[j]["class"]],
                         "values": [implied(rows[i]),
                                    implied(rows[j])]})
        state["t02_conflicts"] = conflicts
'''
new_cmp = '''    def op_t02_compare(self, key, step, state):
        # Consumes the standings stored by the worksheet
        # operation; claim text is never reinterpreted here
        # (Plan Rev 2 §B — the old implied() is deleted).
        rows = state["t02_rows"]
        standings = state["t02_standings"]
        conflicts = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if standings[i] != standings[j]:
                    conflicts.append(
                        {"pair": [rows[i]["class"], rows[j]["class"]],
                         "values": [standings[i], standings[j]]})
        state["t02_conflicts"] = conflicts
'''
rep(old_cmp, new_cmp, "compare")

rep('''        if attempt > 1:
            artefacts["adjudication_row"] = state["t02_rows"][2]
''', '''        if attempt > 1:
            adj_i = state["t02_classes"].index("adjudicator")
            artefacts["adjudication_row"] = \\
                state["t02_rows"][adj_i]
''', "adj-row")

p.write_text(s)
print("driver patch done")
