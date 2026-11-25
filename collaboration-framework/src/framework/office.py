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
        # The glossary (Ben's briefcase design, 2026-11-16;
        # carried 2026-11-24): where the recorded brief names
        # the case's glossary — the map of what the worker may
        # pull from the shelf, each item's address and what it
        # is — the draft carries it, by the same route as the
        # bounds, so it stands in the issued case as its own
        # component and reaches the worker's package inside
        # the case. A brief without a glossary produces a
        # case without the field, exactly as before.
        if brief.get("glossary") is not None:
            content["glossary"] = copy.deepcopy(
                brief["glossary"])
        # The journal designation (the orientation pass,
        # 2026-11-24): where the recorded brief names the
        # worker's journal — the path under his scratch of
        # his own notebook (his to write and rewrite;
        # appending is his convention, not an enforced
        # mechanism) — the draft carries
        # it, by the same route as the glossary, so the
        # designation stands in the issued case and the
        # loop can present the notebook back to him at
        # each wake. A brief without a journal produces a
        # case without the field, exactly as before.
        if brief.get("journal") is not None:
            content["journal"] = copy.deepcopy(
                brief["journal"])
        # The onboarding (the run-6 package, 2026-11-24;
        # Ben's ruling: "his first prompt should be his
        # onboarding file with specific instructions on
        # how to navigate his briefcase"): where the
        # recorded brief names the case's onboarding —
        # the job's headline, the deliverable's statement
        # and the onboarding text itself — the draft
        # carries it, by the same route as the journal, so
        # it stands in the issued case as its own
        # component and the loop can present it at the
        # head of the worker's first wake package. A brief
        # without an onboarding produces a case without
        # the field, exactly as before.
        if brief.get("onboarding") is not None:
            content["onboarding"] = copy.deepcopy(
                brief["onboarding"])
        # The door scope's components (2026-11-24): where
        # the recorded brief names the case's delivery
        # declaration, its role-memory snapshot, or its
        # opening record, the draft carries each unchanged
        # as its own component, by the same route.
        for _field in ("delivery", "role_memory", "opening"):
            if brief.get(_field) is not None:
                content[_field] = copy.deepcopy(
                    brief[_field])
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
        # loop_bounds, glossary, journal and onboarding are
        # the optional content fields (Piece A3; the
        # combined configuration; the orientation pass; the
        # run-6 package): a case may lawfully carry none of
        # them — no loop runs on a boundless case, a
        # glossary-less case simply carries no map, a
        # journal-less case designates no notebook, and an
        # onboarding-less case opens with no guide — so none
        # is an R14 grounding requirement. When present each
        # must be well-formed; malformed optional content
        # fails preflight whole, never silently stripped.
        for field in ("case_id", "version", "seat") + tuple(
                f for f in CASE_CONTENT_FIELDS
                if f not in ("loop_bounds", "glossary",
                             "journal", "onboarding",
                             "delivery", "role_memory",
                             "opening")):
            if content.get(field) is None:
                problems.append(f"R14 field {field} is ungrounded")
        if content.get("loop_bounds") is not None:
            problem = loop_bounds_problem(content["loop_bounds"])
            if problem is not None:
                problems.append(problem)
        if content.get("glossary") is not None:
            glossary = content["glossary"]
            if not isinstance(glossary, list) or not glossary \
                    or any(
                        not isinstance(entry, dict)
                        or not isinstance(
                            entry.get("address"), str)
                        or not entry.get("address")
                        or not isinstance(
                            entry.get("description"), str)
                        or not entry.get("description")
                        for entry in glossary):
                problems.append(
                    "the glossary must be a non-empty list of "
                    "entries, each carrying a non-empty address "
                    "and a non-empty description")
        if content.get("journal") is not None:
            journal = content["journal"]
            if not isinstance(journal, str) or \
                    not journal.startswith("scratch/") or \
                    ".." in journal.split("/"):
                problems.append(
                    "the journal must name a path under "
                    "scratch/ — the worker's notebook stands "
                    "in his own writing space")
        if content.get("onboarding") is not None:
            onboarding = content["onboarding"]
            if not isinstance(onboarding, dict) or \
                    set(onboarding) != {"headline",
                                        "deliverable",
                                        "text"} or \
                    any(not isinstance(
                            onboarding.get(key), str)
                        or not onboarding.get(key)
                        for key in ("headline", "deliverable",
                                    "text")):
                problems.append(
                    "the onboarding must be an object of "
                    "exactly three non-empty strings: the "
                    "job's headline, the deliverable's "
                    "statement, and the onboarding text")
        if content.get("delivery") is not None:
            delivery = content["delivery"]
            if not isinstance(delivery, dict) or \
                    set(delivery) != {"destination",
                                      "route"} or \
                    any(not isinstance(
                            delivery.get(key), str)
                        or not delivery.get(key)
                        for key in ("destination", "route")):
                problems.append(
                    "the delivery declaration must be an "
                    "object of exactly two non-empty "
                    "strings: the destination and the "
                    "route")
        if content.get("role_memory") is not None:
            role_memory = content["role_memory"]
            if not isinstance(role_memory, list) or any(
                    not isinstance(item, dict)
                    or set(item) != {"observation", "basis",
                                     "conditions"}
                    or any(not isinstance(
                               item.get(key), str)
                           or not item.get(key)
                           for key in ("observation",
                                       "conditions"))
                    or item.get("basis") not in (
                        "demonstrated", "worker_reported",
                        "inference")
                    for item in role_memory):
                problems.append(
                    "the role memory must be a list of "
                    "items, each an object of exactly an "
                    "observation, a basis (demonstrated, "
                    "worker_reported or inference) and "
                    "conditions, all non-empty strings")
        if content.get("opening") is not None:
            opening = content["opening"]
            if not isinstance(opening, dict) or \
                    set(opening) != {
                        "worker_statements", "office_answers",
                        "settled", "unresolved"} or \
                    any(not isinstance(
                            opening.get(key), list)
                        or any(not isinstance(x, str)
                               for x in opening.get(key)
                               or [])
                        for key in (
                            "worker_statements",
                            "office_answers", "settled",
                            "unresolved")):
                problems.append(
                    "the opening record must be an object "
                    "of exactly four lists of strings: "
                    "worker_statements, office_answers, "
                    "settled and unresolved")
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
            # The optional fields (loop_bounds, glossary,
            # journal, onboarding) ride forward only where
            # they stand or are being set: a correction of
            # a case that never carried one does not
            # acquire a null field it never had (Piece A3,
            # correction round 1).
            if field in ("loop_bounds", "glossary",
                         "journal", "onboarding",
                         "delivery", "role_memory",
                         "opening") and \
                    field not in current and \
                    field not in changes:
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
