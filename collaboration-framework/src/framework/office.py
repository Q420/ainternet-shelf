"""The office — SPEC SHEET §3.5 (briefcases), Piece 5.

The orchestrator-side machinery that builds a briefcase from the
record and puts it through its issuance route: generate → verify →
(the examiner's act) → authorise, and correct. Every act goes
through the doorway under the orchestrator's token; the examiner's
acts (CASE_JUDGED / CASE_NOTIFIED) remain the examiner's own and
are never the office's to record.

- Generate (R14): a case is assembled from recorded sources only,
  never authored freehand (addendum 1 §B's source map): the tree
  copied verbatim from RUN_COMMISSIONED; part, assignment and
  verification list from the commission's recorded brief for the
  seat; the evidence boundary from the MATERIAL_SEALED records
  whose boundary includes the seat; the account from the
  commissioned seat itself; the authority from the §4 matrix
  defaults for the seat's role.
- Verify: preflight validation runs over the whole draft BEFORE
  anything is appended (addendum 2 §D). A field no record grounds,
  a part outside the tree, an incomplete R14 — preflight fails and
  no case event exists. Verification precedes every append.
- Content (addendum 1 §C): version 1's content rides on its
  CASE_VERIFIED, where the fold establishes it first-wins; a
  correction's content rides on its CASE_CORRECTED.
- Correct (R16/R17): the correction draft is the established
  content with named changes applied, preflighted whole, its
  classification computed by the classification diff (six semantic
  fields, compared as seven stored keys), and submitted as the
  atomic pair — CASE_CORRECTED + CASE_VERIFIED in one store
  transaction (addendum 3 §H). The doorway recomputes the
  classification independently and refuses a disagreement.
"""
import copy

from .doorway import (ACT_AUTHORITY, classify_case_change,
                      established_case_content,
                      loop_bounds_problem)
from .record import CASE_CONTENT_FIELDS


class Office:
    def __init__(self, doorway):
        self.doorway = doorway
        self.store = doorway.store

    # ------------------------------------------------------ sources
    def _commission(self):
        for ev in self.store.all_events():
            if ev["type"] == "RUN_COMMISSIONED":
                return ev["payload"]
        return {}

    def _sealed_for(self, seat_id):
        """Material ids the record seals with `seat_id` in their
        boundary (addendum 1 §B)."""
        found = set()
        for ev in self.store.all_events():
            if ev["type"] == "MATERIAL_SEALED":
                p = ev["payload"]
                if seat_id in (p.get("boundary") or []):
                    found.add(p.get("material_id"))
        return sorted(x for x in found if x is not None)

    @staticmethod
    def case_id_for(seat_id):
        return f"case-{seat_id}"

    # ----------------------------------------------------- generate
    def generate(self, seat_id):
        """The R14 draft for a seat, assembled from the record.
        Ungrounded fields come out as None and fail preflight —
        generation never invents a value to fill a gap."""
        commission = self._commission()
        seats = commission.get("seats") or {}
        info = seats.get(seat_id) or {}
        role = info.get("role")
        brief = (commission.get("briefs") or {}).get(seat_id) or {}
        authority = None
        if role is not None:
            authority = sorted(
                t for t, roles in ACT_AUTHORITY.items()
                if role in roles)
        content = {
            "case_id": self.case_id_for(seat_id),
            "version": 1,
            "seat": seat_id,
            "account": seat_id,
            "assignment": brief.get("assignment"),
            "part": brief.get("part"),
            "verification_list": brief.get("verification_list"),
            "tree": copy.deepcopy(commission.get("tree")),
            "evidence_boundary": self._sealed_for(seat_id),
            "authority": authority,
        }
        # Piece A3 (R49, correction round 1): the loop bounds
        # are case content like the rest — where the recorded
        # brief names them, the draft carries them, so they
        # reach the issued case through this route and no
        # other. A brief without bounds produces a case
        # without the field, exactly as before.
        if brief.get("loop_bounds") is not None:
            content["loop_bounds"] = copy.deepcopy(
                brief["loop_bounds"])
        return content

    # ---------------------------------------------------- preflight
    def preflight(self, content):
        """Validate a whole draft before any append (addendum 2
        §D). Returns the list of problems; empty means the draft
        may be submitted. Pure: reads the record, appends nothing.
        """
        problems = []
        commission = self._commission()
        seats = commission.get("seats") or {}
        seat_id = content.get("seat")
        if seat_id not in seats:
            problems.append(
                f"seat {seat_id} is not commissioned in the record")
        elif (seats[seat_id] or {}).get("role") != "crew":
            problems.append(
                f"cases are issued to crew seats; {seat_id} is "
                f"{(seats[seat_id] or {}).get('role')}")
        # loop_bounds is the one optional content field (Piece
        # A3): a case may lawfully carry none — no loop runs on
        # it — so it is not an R14 grounding requirement. When
        # present it must be well-formed; malformed bounds fail
        # preflight whole, never silently stripped.
        for field in ("case_id", "version", "seat") + tuple(
                f for f in CASE_CONTENT_FIELDS
                if f != "loop_bounds"):
            if content.get(field) is None:
                problems.append(f"R14 field {field} is ungrounded")
        if content.get("loop_bounds") is not None:
            problem = loop_bounds_problem(content["loop_bounds"])
            if problem is not None:
                problems.append(problem)
        tree = content.get("tree")
        part = content.get("part")
        if isinstance(tree, dict) and part is not None:
            known = set(tree)
            for downstream in tree.values():
                known.update(downstream or [])
            if part not in known:
                problems.append(
                    f"part {part} is not in the case's tree")
        if content.get("verification_list") is not None and \
                (not isinstance(content["verification_list"], list)
                 or not content["verification_list"]):
            problems.append(
                "the verification list names what needs verifying; "
                "it must be a non-empty list")
        if content.get("evidence_boundary") is not None and \
                not isinstance(content["evidence_boundary"], list):
            problems.append("the evidence boundary must be a list")
        if content.get("account") is not None and \
                content.get("account") != seat_id:
            problems.append(
                "the account is the commissioned seat itself")
        return problems

    # -------------------------------------------------------- issue
    def issue_new(self, token, seat_id):
        """Generate + preflight + record version 1's verification.
        On preflight failure nothing is appended."""
        content = self.generate(seat_id)
        problems = self.preflight(content)
        if problems:
            return {"ok": False, "problems": problems,
                    "case_id": content["case_id"]}
        head = self.doorway.state()["head_seq"]
        ev = self.doorway.act(token, "CASE_VERIFIED", content,
                              view_seq=head)
        return {"ok": True, "case_id": content["case_id"],
                "version": 1, "verified_seq": ev["event_seq"]}

    def authorise(self, token, case_id, version):
        """The orchestrator's authorisation (R15): CASE_ISSUED
        naming the case and version, through the doorway."""
        state = self.doorway.state()
        content, _ = established_case_content(state, case_id)
        seat = (content or {}).get("seat")
        ev = self.doorway.act(
            token, "CASE_ISSUED",
            {"case_id": case_id, "version": version, "seat": seat},
            view_seq=state["head_seq"])
        return ev

    # ------------------------------------------------------ correct
    def correct(self, token, case_id, changes):
        """Build and submit a correction (R16/R17): the established
        content with `changes` applied to its content fields,
        preflighted whole, classified by the six-field diff, and
        submitted as the atomic pair. On preflight failure nothing
        is appended; the pair itself is the doorway's (§H)."""
        state = self.doorway.state()
        current, current_version = established_case_content(
            state, case_id)
        if current is None:
            return {"ok": False,
                    "problems": [f"case {case_id} has no established "
                                 f"content to correct"]}
        unknown = [k for k in changes if k not in CASE_CONTENT_FIELDS]
        if unknown:
            return {"ok": False,
                    "problems": [f"changes name non-content fields: "
                                 f"{sorted(unknown)}"]}
        draft = {"case_id": case_id,
                 "version": current_version + 1,
                 "seat": current.get("seat")}
        for field in CASE_CONTENT_FIELDS:
            # loop_bounds rides forward only where it stands
            # or is being set: a correction of a case that
            # never carried bounds does not acquire a null
            # field it never had (Piece A3, correction
            # round 1).
            if field == "loop_bounds" and \
                    "loop_bounds" not in current and \
                    "loop_bounds" not in changes:
                continue
            draft[field] = copy.deepcopy(current.get(field))
        for field, value in changes.items():
            draft[field] = copy.deepcopy(value)
        problems = self.preflight(draft)
        if problems:
            return {"ok": False, "problems": problems,
                    "case_id": case_id}
        changed = classify_case_change(current, draft)
        draft["representational"] = not changed
        ev1, ev2 = self.doorway.submit_pair(
            token,
            [("CASE_CORRECTED", draft),
             ("CASE_VERIFIED", {"case_id": case_id,
                                "version": draft["version"]})],
            view_seq=state["head_seq"])
        return {"ok": True, "case_id": case_id,
                "version": draft["version"],
                "representational": draft["representational"],
                "changed": changed,
                "corrected_seq": ev1["event_seq"],
                "verified_seq": ev2["event_seq"]}
