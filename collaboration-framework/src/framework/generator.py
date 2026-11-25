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
    → ASSEMBLY_PROBED (office: the native-mode probe — only
      where the generated record declares the probe contract;
      its evidence binds to the exact generated record by hash)
    → ASSEMBLY_VERIFIED (office: construction verification;
      under a probe-governed assembly it names the probe
      evidence, so the verified assembly's integrity boundary
      covers it)
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
from . import probe as _probe
from . import tool_policy as _tool_policy
from .record import (assembly_record_hash, declaration_fingerprint,
                     effective_case, instance_credential_fingerprint)

# The A3-CAT catalogue contract's declaration (Piece A3-CAT,
# correction round): every assembly this generator produces
# declares, in its sealed generated record, that its loop
# iterations carry the tool catalogue commitment — the
# catalogue hash and the registry version on every
# LOOP_ITERATION. The declaration is the compatibility
# discriminator the checker reads: an assembly whose record
# carries it is governed by the contract and its iterations
# must carry both fields; an assembly generated before the
# contract existed carries no declaration, and its iterations
# are historical record, exempt identifiably rather than by
# inference from missing fields. The value is contract data,
# duplicated in the checker's own copy as its other contracts
# are.
CATALOGUE_CONTRACT = "a3-cat"

# The working-set contract (the run-3 correction, examiner's
# ruling 2026-11-24): an assembly generated for the combined
# configuration — the execution room AND retrieval grants,
# the configuration the ruling addresses — declares the
# contract (tool_policy.WORKING_SET_CONTRACT) in its sealed
# record beside the catalogue contract; its wake packages
# then present a working set (the successful retrieval
# material gathered so far, accumulated) and its iterations
# carry the working set's commitment hash. Assemblies under
# any other configuration declare nothing: the retrieval
# piece's examined carriage stands untouched for them, and
# historical records are exempt identifiably rather than by
# inference.

# The decision-recording note (INDEX 293): a probe-governed
# judgement binds the hash of the examiner's durable decision
# receipt, and the payload states plainly what the recording
# does and does not establish — the act is recorded by the
# harness from that receipt, under a token the harness issues;
# the token authenticates the recording act, never the
# examiner's identity. The provenance the record claims is the
# receipt and its hash, nothing more.
DECISION_RECORDING = (
    "harness-recorded from the examiner decision receipt; "
    "the examiner token authenticates the recording act, "
    "not the examiner's identity")

# The retrieval contract's declaration (RETRIEVAL-SCOPE
# Rev 5): an assembly generated for structured retrieval
# declares this value in the same field, in place of the
# A3-CAT value. It discriminates the whole retrieval regime
# — the v3 registry governs its dispatches and catalogue,
# the doorway enforces the two authority paths and the
# aggregate admission, and the loop carries each retrieval
# result exactly once. The value is the registry's own
# contract data (tool_policy.RETRIEVAL_CATALOGUE_CONTRACT),
# read from there so the generator, the doorway and the loop
# cannot drift apart on it; the checker holds its own copy,
# as its other contracts are held.


class Generator:
    def __init__(self, doorway):
        self.doorway = doorway
        self.store = doorway.store

    # ------------------------------------------------------ sources
    def _entry(self, state, assembly_id):
        return state["assemblies"].get(assembly_id)

    def _open_proposal(self, state, seat_id):
        """The latest standing instance proposal naming this
        seat slot that no generated assembly has answered yet,
        or None. Only an instance proposal is an answerable
        referent (correction round 1): a run-level proposal
        shares the event kind but proposes the run's gate set,
        and a generation never answers one."""
        answered = {e.get("proposal_seq")
                    for e in state["assemblies"].values()}
        best = None
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_PROPOSED" and \
                    ev["payload"].get("proposal_kind") == \
                    "instance" and \
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
        exactly, as §3.8's discipline requires. The payload
        carries the proposal discriminator (correction round 1):
        "instance" — this proposal fills a seat slot and is
        never the run-level proposal the gate derivations read."""
        state = self.doorway.state()
        binding = state["seats"].get(seat_id) or {}
        payload = {
            "commission_seq": state["commission_seq"],
            "tree_ref": state["commission_seq"],
            "gates_ref": state["commission_seq"],
            "crew": [{"seat": seat_id,
                      "role": binding.get("role")}],
            "proposal_kind": "instance",
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
        proposal = self._open_proposal(state, seat_id)
        if proposal is None:
            problems.append(
                f"no unanswered proposal stands for seat "
                f"{seat_id}; a generation answers a proposal")
        declaration = (identity or {}).get("declaration")
        if not isinstance(declaration, str) or not declaration:
            problems.append(
                "the model declared no identity; an instance "
                "onboards on its own declaration (R38)")
        eff = effective_case(state, seat_id)
        if eff is None:
            problems.append(
                f"no issued case stands for seat {seat_id}; "
                f"an assembly binds to a case (R37)")
        elif proposal is not None:
            # Correction round 1: the part the proposal names
            # must be the part the bound case's established
            # content covers — each id grounded is not enough;
            # their pairing must correspond, here in preflight
            # (before any act) as at the doorway.
            part = proposal["payload"].get("part")
            case_part = (eff.get("content") or {}).get("part")
            if part != case_part:
                problems.append(
                    f"the proposal names part {part!r}; the "
                    f"case the assembly would bind covers part "
                    f"{case_part!r} — an assembly's part must "
                    f"be its case's part (R37)")
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
                 grants=None, model_requested=None,
                 retrieval=False, probe=False, exec_room=False,
                 freshness_suspended=False):
        """Assemble one instance for a seat slot (R37/R38).

        `identify` is a callable returning the adapter's
        identity claims — {"declaration": the model's words,
        verbatim, "provider_model_id": the provider's reported
        id, or None} — or such a mapping itself. On preflight
        failure nothing is recorded: no onboarding, no
        generation, no act of any kind. On success the
        instance's onboarding is recorded first (its normative
        place in the sequence), then the generated record that
        binds to it.

        `retrieval` (retrieval scope, Rev 5): where the
        assembly is generated for structured retrieval, its
        sealed record declares the retrieval catalogue
        contract in place of the A3-CAT value — the
        declaration that governs the assembly's whole
        retrieval regime. The default keeps every existing
        generation's declaration exactly as it stands.

        `probe` (native-mode probe scope, Rev 6): where the
        assembly is generated under the probe regime, its
        sealed record declares the probe contract — the
        declaration that makes the probe stage a required,
        binding step of this assembly's lifecycle. The
        declaration rides outside the record's canonical hash
        fields, like the catalogue contract's: the generated
        record is never rewritten by the probe, which binds to
        it by hash instead. The default declares nothing, and
        an assembly without the declaration is exempt,
        identifiably.

        `exec_room` (room-exec configuration, gate 4): where
        the assembly is generated for the room demonstration —
        its one grant the worker's own execution tool — its
        sealed record declares the exec catalogue contract,
        the declaration that governs the assembly's dispatch
        and catalogue versions (registry v4), exactly as the
        retrieval declaration governs its regime. The two
        configuration declarations are alternatives: a
        generation names at most one, and the exec declaration
        is the one recorded where both were somehow asked.

        The combined configuration (INDEX 476) is an exec
        generation whose grants ALSO carry the retrieval
        family (and the scratch write): the record still
        declares the one exec contract — no second
        declaration exists to name — and the retrieval
        regime applies to those grants under it, because
        registry v4 contains the v3 regime whole. The
        `retrieval` flag remains the declaration for a
        retrieval-only assembly; it is not set for the
        combined one.

        `freshness_suspended` (Ben's ruling, 2026-11-24:
        "Disable R31 until we need to worry about that"):
        where a generation is made under the ruling, its
        sealed record declares the freshness guard
        suspended — the declaration the doorway honours
        for that instance's acts and the checker reads
        from its own copy. The declaration rides outside
        the record's canonical hash fields, like the
        catalogue contract's. The default declares
        nothing: the guard stands for every other
        generation exactly as it always has."""
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
            "catalogue_contract":
                _tool_policy.EXEC_CATALOGUE_CONTRACT
                if exec_room else
                _tool_policy.RETRIEVAL_CATALOGUE_CONTRACT
                if retrieval else CATALOGUE_CONTRACT,
        }
        if probe:
            record["probe_contract"] = _probe.PROBE_CONTRACT
        if exec_room and any(
                isinstance(g, dict)
                and g.get("tool")
                in _tool_policy.RETRIEVAL_TOOLS
                for g in grants or []):
            # The combined configuration declares the
            # working-set contract (see the constant above):
            # the execution room plus retrieval grants is
            # the population whose wake packages carry the
            # gathered material forward.
            record["working_set_contract"] = \
                _tool_policy.WORKING_SET_CONTRACT
        if freshness_suspended:
            # Ben's R31 ruling (2026-11-24), sealed as a
            # declaration beside the contracts: the
            # doorway does not raise the freshness
            # rejection for this instance's answers. A
            # switch with a name and a ruling behind it —
            # the rule's code stands untouched, and a
            # generation made without the ruling declares
            # nothing.
            record["freshness_guard"] = \
                _tool_policy.FRESHNESS_GUARD_SUSPENDED
        ev = self.doorway.act(token, "ASSEMBLY_GENERATED", record,
                              view_seq=self.store.head_seq())
        return {"ok": True, "assembly_id": assembly_id,
                "instance_id": instance_id,
                "generated_seq": ev["event_seq"],
                "onboarding_seq": onboard_ev["event_seq"],
                "record_hash": assembly_record_hash(record)}

    # -------------------------------------------------------- probe
    def probe(self, token, assembly_id, raw_call, route=None,
              model=None):
        """The native-mode probe stage (probe scope §2): runs
        the versioned suite's bounded trials against the
        assembly's pinned model through the injected raw-call
        callable — capture below the adapter's interpretation —
        classifies each trial in two dimensions, retains the
        per-object evidence under the aggregate ceiling, and
        records ASSEMBLY_PROBED binding the evidence hash to
        the exact generated record by its hash. The generated
        record is never rewritten; nothing captured is
        dispatched or executed, and no tool results are sent
        back. The stage recommends at most a mode; the
        examiner's judgement decides."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        generated = self.doorway._generated_payload(assembly_id)
        # The route recorded here is the assembly's own:
        # the trials read it for the route's name
        # translation (the NVIDIA route's wire names,
        # Ben's ruling 2026-11-24) — the same value this
        # act records below and the fingerprint binds.
        trials = _probe.run_trials(raw_call, model, route=route)
        counts, settled, recommended = _probe.summarise(trials)
        payload = {
            "assembly_id": assembly_id,
            "instance_id": (entry or {}).get("instance_id"),
            "generated_record_hash": assembly_record_hash(
                generated or {}),
            "suite": _probe.SUITE_NAME,
            "suite_hash": _probe.SUITE_HASH,
            "route": route,
            "model": model,
            "fingerprint": _probe.configuration_fingerprint(
                route, model),
            "trials": trials,
            "counts": counts,
            "settled_count": settled,
            "recommended_mode": recommended,
        }
        payload["evidence_hash"] = _probe.evidence_hash(payload)
        ev = self.doorway.act(token, "ASSEMBLY_PROBED", payload,
                              view_seq=state["head_seq"])
        return {"ok": True, "assembly_id": assembly_id,
                "probed_seq": ev["event_seq"],
                "evidence_hash": payload["evidence_hash"],
                "recommended_mode": recommended,
                "counts": counts, "settled_count": settled}

    # ------------------------------------------------------- verify
    def verify(self, token, assembly_id):
        """Construction verification (office, R40): the
        assembly matches its record and is technically
        complete. The doorway checks the sequence; whether the
        construction is *sufficient* is the examiner's judgement
        that follows, never this act's. Under a probe-governed
        assembly the act names the standing probe evidence
        hash, so the verified assembly's integrity boundary
        covers the probe evidence (probe scope §4, INDEX 285):
        a verification that left the evidence outside the
        boundary it verifies would let the evidence be
        substituted after verification."""
        state = self.doorway.state()
        entry = self._entry(state, assembly_id)
        payload = {"assembly_id": assembly_id,
                   "instance_id": (entry or {}).get("instance_id")}
        if self.doorway._probe_governed(
                self.doorway._generated_payload(assembly_id)):
            probed = self.doorway._probed_payload(assembly_id)
            payload["probe_evidence_hash"] = \
                (probed or {}).get("evidence_hash")
        return self.doorway.act(
            token, "ASSEMBLY_VERIFIED", payload,
            view_seq=state["head_seq"])

    # ------------------------------------------------------ judging
    def judgement(self, assembly_id, adapter_mode=None,
                  mode_grounds=None, decision_receipt_hash=None,
                  decision_examiner=None):
        """The payload of the examiner's sufficiency judgement
        (R40), computed from the record: it names the assembly,
        its instance, and the exact object judged — by the
        generated record's canonical hash. The act itself is
        the examiner's to record, through the doorway, under
        the examiner's token.

        Under a probe-governed assembly the payload also
        identifies the exact probe event and its evidence hash
        and carries the examiner's mode decision: `adapter_mode`
        and `mode_grounds` are the examiner's inputs, supplied
        by the caller — the probe's recommendation is evidence
        for that decision, never the decision itself, and an
        override of an inconclusive probe stands only as this
        act, with its grounds (probe scope §5). The decision's
        provenance binds with it (INDEX 293): the payload
        carries the hash of the examiner's durable decision
        receipt — the document that identifies this exact
        assembly, its generated record, its probe event and
        evidence, and the mode and grounds decided — and the
        receipt's examiner label, under the standing note
        (DECISION_RECORDING) that the recording token
        authenticates the recording act, not the examiner's
        identity."""
        generated = None
        for ev in self.store.all_events():
            if ev["type"] == "ASSEMBLY_GENERATED" and \
                    ev["payload"].get("assembly_id") == assembly_id:
                generated = ev["payload"]
                break
        if generated is None:
            return None
        payload = {"assembly_id": assembly_id,
                   "instance_id": generated.get("instance_id"),
                   "record_hash": assembly_record_hash(generated)}
        if self.doorway._probe_governed(generated):
            state = self.doorway.state()
            entry = self._entry(state, assembly_id)
            probed = self.doorway._probed_payload(assembly_id)
            payload["probe_seq"] = (entry or {}).get(
                "probed_seq")
            payload["probe_evidence_hash"] = \
                (probed or {}).get("evidence_hash")
            payload["adapter_mode"] = adapter_mode
            payload["mode_grounds"] = mode_grounds
            payload["decision_receipt_hash"] = \
                decision_receipt_hash
            payload["decision_examiner"] = decision_examiner
            payload["decision_recording"] = DECISION_RECORDING
        return payload

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
        if self.doorway._probe_governed(
                self.doorway._generated_payload(assembly_id)):
            # Probe scope §4: the pack seals the probe bindings
            # alongside the record's — the evidence hash and the
            # mode exactly as judged, copied from the standing
            # acts, so the sealed package the adapter reads is
            # the package the examiner judged.
            probed = self.doorway._probed_payload(assembly_id)
            judged = self.doorway._event_at(
                (entry or {}).get("judged_seq"))
            payload["probe_evidence_hash"] = \
                (probed or {}).get("evidence_hash")
            payload["adapter_mode"] = (judged or {}).get(
                "payload", {}).get("adapter_mode")
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
