"""The generator — the office's assembly subsystem (agent
layer, Piece A1; SPEC SHEET Rev 6, R37–R40).

Why its own module, not an extension of `office.py`: the office
builds briefcases for seats (Piece 5); the generator builds the
worker-and-case pair that fills a crew seat slot for one part.
The scope settles the generator as a distinct, inspectable
subsystem of the office — machinery with no authority of its
own — and a separate module keeps that boundary visible in the
code as it is in the design. Like the office, every act goes
through the doorway; the examiner's sufficiency judgement
remains the examiner's own and is never the generator's to
record (its payload is computed here for the examiner to use,
as the office computes a correction's classification).

The lifecycle, in the normative order (R40):

    ASSEMBLY_PROPOSED (orchestrator)
    → office preflight + instance id allocation — preparation,
      never recorded acts; preflight completes BEFORE any
      onboarding is recorded, so a failed generation leaves no
      orphaned instance onboarding
    → ONBOARDING (the instance's, subject "instance")
    → ASSEMBLY_GENERATED (office: the assembly record, binding
      to the exact onboarding event by position and by the
      declaration's fingerprint; identity claims live only in
      the onboarding event)
    → ASSEMBLY_VERIFIED (office: construction verification)
    → ASSEMBLY_JUDGED (examiner: sufficiency, naming the exact
      record by its canonical hash)
    → ASSEMBLY_PACKED (office: the record sealed by its hash;
      the credential prepared — and unusable)
    → ASSEMBLY_ISSUE_AUTHORISED (orchestrator)
    → INSTANCE_ACTIVATED (office, doorway-enforced)

Generation assembles from recorded sources only — the
commission, the standing proposal, the model's own identity
(declared through the adapter's `identify()` shape), the case
the record has issued to the seat — under the office's
never-invent-a-value rule: an ungrounded field fails preflight
and no act is recorded. A material change after judgement is
not an edit: it is a new assembly, with a new instance id and a
fresh onboarding, and the old assembly stands in history as it
was left.
"""
import copy

from . import onboarding as _onboarding
from .record import (assembly_record_hash, declaration_fingerprint,
                     effective_case, instance_credential_fingerprint)


class Generator:
    def __init__(self, doorway):
        self.doorway = doorway
        self.store = doorway.store

    # ------------------------------------------------------ sources
    def _entry(self, state, assembly_id):
        return state["assemblies"].get(assembly_id)

    def _open_proposal(self, state, seat_id):
        """The latest standing proposal naming this seat slot
        that no generated assembly has answered yet, or None."""
        answered = {e.get("proposal_seq")
                    for e in state["assemblies"].values()}
        best = None
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_PROPOSED" and \
                    ev["payload"].get("seat") == seat_id and \
                    ev["event_seq"] not in answered:
                best = ev
        return best

    def _next_number(self, state):
        """The next instance number for a seat slot, derived
        from the record: one past the highest number any
        instance id in the record already carries. Ids are
        allocated from the record itself, so they are unique
        per assembly and never reused — a number burned by a
        failed generation is simply skipped, never reissued."""
        highest = 0
        ids = list(state["instance_onboarding"])
        ids += [e.get("instance_id")
                for e in state["assemblies"].values()]
        for iid in ids:
            if isinstance(iid, str) and "-" in iid:
                suffix = iid.rsplit("-", 1)[-1]
                if suffix.isdigit():
                    highest = max(highest, int(suffix))
        return highest + 1

    # ------------------------------------------------------ propose
    def propose(self, token, seat_id, part=None,
                role_requirements=None):
        """The orchestrator's proposal (R40): the §3.8 assembly
        proposal, extended with the seat slot it fills, the part,
        and the role requirements the generation answers. The
        commission references name the standing commission
        exactly, as §3.8's discipline requires."""
        state = self.doorway.state()
        binding = state["seats"].get(seat_id) or {}
        payload = {
            "commission_seq": state["commission_seq"],
            "tree_ref": state["commission_seq"],
            "gates_ref": state["commission_seq"],
            "crew": [{"seat": seat_id,
                      "role": binding.get("role")}],
            "seat": seat_id,
            "part": part,
            "role_requirements": role_requirements,
        }
        return self.doorway.act(token, "ASSEMBLY_PROPOSED",
                                payload, view_seq=state["head_seq"])

    # ----------------------------------------------------- generate
    def _generation_problems(self, state, seat_id, identity,
                             skills, grants):
        """The generation preflight, whole and before any act
        (the office's addendum-2 §D discipline, carried to the
        generator): every field of the assembly record must be
        grounded in a recorded source or in the identity the
        model itself declared. Returns the problems; empty
        means generation may proceed to record."""
        problems = []
        binding = state["seats"].get(seat_id)
        if binding is None:
            problems.append(
                f"seat {seat_id} is not commissioned in the "
                f"record")
        elif binding.get("role") != "crew":
            problems.append(
                f"assemblies fill crew seat slots; {seat_id} "
                f"is {binding.get('role')}")
        if self._open_proposal(state, seat_id) is None:
            problems.append(
                f"no unanswered proposal stands for seat "
                f"{seat_id}; a generation answers a proposal")
        declaration = (identity or {}).get("declaration")
        if not isinstance(declaration, str) or not declaration:
            problems.append(
                "the model declared no identity; an instance "
                "onboards on its own declaration (R38)")
        if effective_case(state, seat_id) is None:
            problems.append(
                f"no issued case stands for seat {seat_id}; "
                f"an assembly binds to a case (R37)")
        if not isinstance(skills, (list, tuple)) or any(
                not isinstance(s, dict) or not s.get("name")
                or not s.get("version") for s in skills):
            problems.append(
                "skills are pinned by name and version (R37)")
        if grants is not None and (
                not isinstance(grants, list) or any(
                    not isinstance(g, dict) or not g.get("tool")
                    for g in grants)):
            problems.append(
                "grants, when present, are a list of grant "
                "objects naming their tool (R44's shape, as "
                "data)")
        return problems

    def generate(self, token, seat_id, identify, skills=(),
                 grants=None, model_requested=None):
        """Assemble one instance for a seat slot (R37/R38).

        `identify` is a callable returning the adapter's
        identity claims — {"declaration": the model's words,
        verbatim, "provider_model_id": the provider's reported
        id, or None} — or such a mapping itself. On preflight
        failure nothing is recorded: no onboarding, no
        generation, no act of any kind. On success the
        instance's onboarding is recorded first (its normative
        place in the sequence), then the generated record that
        binds to it."""
        state = self.doorway.state()
        identity = identify() if callable(identify) else identify
        problems = self._generation_problems(
            state, seat_id, identity, skills, grants)
        if problems:
            return {"ok": False, "problems": problems,
                    "seat": seat_id}
        proposal = self._open_proposal(state, seat_id)
        eff = effective_case(state, seat_id)
        n = self._next_number(state)
        instance_id = f"inst-{seat_id}-{n}"
        assembly_id = f"assembly-{seat_id}-{n}"
        declaration = identity["declaration"]
        onboard_ev = _onboarding.onboard_instance(
            self.doorway, token, seat_id, instance_id,
            assembly_id, declaration,
            provider_model_id=identity.get("provider_model_id"),
            view_seq=self.store.head_seq())
        record = {
            "assembly_id": assembly_id,
            "instance_id": instance_id,
            "seat": seat_id,
            "part": proposal["payload"].get("part"),
            "case_id": eff["case_id"],
            "case_version": eff["version"],
            "proposal_seq": proposal["event_seq"],
            "onboarding_seq": onboard_ev["event_seq"],
            "declaration_fingerprint": declaration_fingerprint(
                instance_id, declaration),
            "model_selection": {
                "basis": proposal["payload"].get(
                    "role_requirements"),
                "requested": model_requested,
            },
            "skills": [{"name": s["name"],
                        "version": s["version"]} for s in skills],
            "grants": copy.deepcopy(grants),
        }
        ev = self.doorway.act(token, "ASSEMBLY_GENERATED", record,
                              view_seq=self.store.head_seq())
        return {"ok": True, "assembly_id": assembly_id,
                "instance_id": instance_id,
                "generated_seq": ev["event_seq"],
                "onboarding_seq": onboard_ev["event_seq"],
                "record_hash": assembly_record_hash(record)}

    # ------------------------------------------------------- verify
    def verify(self, token, assembly_id):
        """Construction verification (office, R40): the
        assembly matches its record and is technically
        complete. The doorway checks the sequence; whether the
        construction is *sufficient* is the examiner's judgement
        that follows, never this act's."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        return self.doorway.act(
            token, "ASSEMBLY_VERIFIED",
            {"assembly_id": assembly_id,
             "instance_id": (entry or {}).get("instance_id")},
            view_seq=state["head_seq"])

    # ------------------------------------------------------ judging
    def judgement(self, assembly_id):
        """The payload of the examiner's sufficiency judgement
        (R40), computed from the record: it names the assembly,
        its instance, and the exact object judged — by the
        generated record's canonical hash. The act itself is
        the examiner's to record, through the doorway, under
        the examiner's token."""
        generated = None
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_GENERATED" and \
                    ev["payload"].get("assembly_id") == assembly_id:
                generated = ev["payload"]
                break
        if generated is None:
            return None
        return {"assembly_id": assembly_id,
                "instance_id": generated.get("instance_id"),
                "record_hash": assembly_record_hash(generated)}

    # --------------------------------------------------------- pack
    def pack(self, token, assembly_id):
        """Pack (office, R39/R40): seals the judged record —
        the act carries the record's canonical hash and the
        credential fingerprint — and the doorway issues the
        instance's credential in its prepared state. The token
        is returned here, to the office that hands it on; it
        authenticates nothing until activation stands in the
        record."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        instance_id = (entry or {}).get("instance_id")
        record = self.doorway.state()["instance_onboarding"].get(
            instance_id) or {}
        payload = {
            "assembly_id": assembly_id,
            "instance_id": instance_id,
            "record_hash": (entry or {}).get("judged_hash"),
            "credential_fingerprint":
                instance_credential_fingerprint(
                    instance_id, record.get("declaration"),
                    (entry or {}).get("case_id"),
                    (entry or {}).get("case_version")),
        }
        ev = self.doorway.act(token, "ASSEMBLY_PACKED", payload,
                              view_seq=state["head_seq"])
        instance_token = self.doorway.issue_instance_token(
            instance_id)
        return {"ok": True, "assembly_id": assembly_id,
                "instance_id": instance_id,
                "packed_seq": ev["event_seq"],
                "instance_token": instance_token}

    # ---------------------------------------------------- authorise
    def authorise(self, token, assembly_id):
        """The orchestrator's issue authorisation (R40): the
        packed assembly may go live. Authorisation activates
        nothing by itself — activation is the separate act that
        follows, doorway-enforced."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        return self.doorway.act(
            token, "ASSEMBLY_ISSUE_AUTHORISED",
            {"assembly_id": assembly_id,
             "instance_id": (entry or {}).get("instance_id")},
            view_seq=state["head_seq"])

    # ----------------------------------------------------- activate
    def activate(self, token, assembly_id):
        """Activation (office, doorway-enforced, R39): the
        recorded act that makes the instance's credential
        usable. The doorway refuses it — recording the refusal —
        unless the issue authorisation stands and the record
        carries its grants section; the credential's state is
        derived from this event standing in the record, so the
        act and the transition are one thing, atomic by
        construction: no event, no transition."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        return self.doorway.act(
            token, "INSTANCE_ACTIVATED",
            {"assembly_id": assembly_id,
             "instance_id": (entry or {}).get("instance_id")},
            view_seq=state["head_seq"])
