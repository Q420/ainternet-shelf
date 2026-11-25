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
import hashlib

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


def _worked_example_problem(example, glossary,
                            presentation_declaration):
    """The worked example's preflight (round nine's
    correction pair, INDEX 548): the problem a supplied
    example stands under, or None where it may seal. The
    example seals only beside the presentation contract,
    names the pinned case's first glossary address
    exactly, and carries the listing performer's whole
    result, internally consistent — its hash and byte
    count its content's, its path the call's. Anything
    else would claim a demonstration the office never
    made, so the generation fails preflight whole."""
    if not presentation_declaration:
        return ("the worked example was asked to be "
                "sealed but this generation does not "
                "declare the staged-onboarding "
                "presentation contract, the only "
                "population the example stands for")
    if not isinstance(example, dict) or \
            set(example) != {"tool", "path", "result"}:
        return ("the worked example is not a call and "
                "its result (a mapping naming exactly "
                "tool, path and result)")
    if example.get("tool") != "sandbox.list":
        return ("the worked example's call is not "
                "sandbox.list, the demonstration call "
                "the files stage presents")
    path = example.get("path")
    first = None
    if isinstance(glossary, list):
        for entry in glossary:
            if isinstance(entry, dict) and \
                    isinstance(entry.get("address"), str):
                first = entry["address"]
                break
    if not isinstance(path, str) or not path or \
            first is None or path != first:
        return ("the worked example does not name the "
                "pinned case's first glossary address; "
                "the demonstration is of the first file "
                "the briefcase map names")
    result = example.get("result")
    if not isinstance(result, dict) or \
            set(result) != {"path", "content",
                            "content_bytes",
                            "content_sha256",
                            "authority_path", "size_bytes",
                            "line_count"}:
        return ("the worked example's result is not "
                "the listing performer's whole result")
    content = result.get("content")
    if result.get("path") != path or \
            not isinstance(content, str) or \
            result.get("content_bytes") != len(
                content.encode("utf-8")) or \
            result.get("content_sha256") != hashlib.sha256(
                content.encode("utf-8")).hexdigest() or \
            result.get("authority_path") not in (
                "source", "scratch") or \
            not isinstance(result.get("size_bytes"), int) \
            or isinstance(result.get("size_bytes"), bool) \
            or result.get("size_bytes") < 0 or \
            not isinstance(result.get("line_count"), int) \
            or isinstance(result.get("line_count"), bool) \
            or result.get("line_count") < 0:
        return ("the worked example's result is not "
                "internally consistent (its hash and "
                "byte count are its content's, its path "
                "the call's)")
    return None


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
                 freshness_suspended=False,
                 delivery_declaration=False,
                 delivery_evidence_declaration=False,
                 delivery_floor_declaration=False,
                 presentation_declaration=False,
                 worked_example=None):
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
        generation exactly as it always has.

        `presentation_declaration` (staged onboarding,
        INDEX 544): True seals the staged-onboarding
        contract; the pointer-rule successor's name
        (INDEX 568) seals that contract instead, under
        which a gathered entry's content is presented
        once and stands as a pointer after — any other
        string fails preflight whole. Where a generation
        is made for the combined configuration under
        Ben's direction, its sealed record declares the
        staged-onboarding presentation contract — the
        loop then onboards
        the worker in stages across his first wakes
        instead of presenting the whole case verbatim at
        every wake, and each iteration record carries
        the presentation hash the checker re-derives.
        The contract's whole population is the
        working-set population: the declaration seals
        only where the working-set contract seals (an
        exec-room generation carrying retrieval grants),
        and a generation asked to seal it anywhere else
        fails preflight whole — the loop would not
        honour it there, so the record must not claim
        it. The default declares nothing: every other
        generation's packages present exactly as they
        always have.

        `delivery_evidence_declaration` (round ten,
        INDEX 552): where the case declares the evidence
        a delivery must rest on — a `delivery_evidence`
        component naming the addresses whose whole
        content must stand in the worker's working set
        before a contribution is adjudicated as a
        delivery — sealing it binds that declaration to
        this assembly beside the delivery declaration,
        so the loop's door adjudicates against the
        case's own word. The declaration seals only
        where the delivery declaration seals with it
        (without the door there is nothing for the gate
        to guard) and only in the combined configuration
        (the working-set population — the declaration
        speaks of the worker's working set, a structure
        that stands declared only there). A generation
        asked to seal it anywhere else, or against a
        case carrying it missing or malformed, fails
        preflight whole. The default seals nothing:
        every other generation's contributions are
        adjudicated exactly as they always have been.

        `delivery_floor_declaration` (the third gate,
        INDEX 557): where the case declares the length
        a delivery must reach — a `delivery_floor`
        component naming the deliverable's minimum
        length in words — sealing it binds that
        declaration to this assembly beside the
        delivery declaration, so the loop's door
        adjudicates a contribution's sufficiency
        against the case's own word. The declaration
        seals only with the door (the delivery
        declaration sealed in the same generation):
        the floor is a property of the delivery, and
        its subject — the contributed text itself —
        stands wherever the door stands, so unlike the
        evidence declaration it does not require the
        combined configuration. A generation asked to
        seal it without the door, or against a case
        carrying it missing or malformed, fails
        preflight whole. The default seals nothing:
        every other generation's contributions are
        adjudicated exactly as they always have been.

        `worked_example` (round nine's correction pair,
        INDEX 548): the office's demonstration call for
        the staged files stage — a real sandbox.list call
        on the pinned case's first glossary file, made
        through the executor's governed performer while
        the briefcase was stocked, whose result the
        sealed record carries so the loop can present it
        and the checker can re-derive the presentation.
        The example seals only beside the presentation
        contract, names the case's first glossary address
        exactly, and carries its result whole and
        internally consistent (the result's hash and byte
        count are its content's) — a generation asked to
        seal anything else fails preflight whole. The
        default seals nothing: where the first glossary
        file cannot be listed, the office omits the
        example rather than present one that was never
        made, and the files stage presents none."""
        state = self.doorway.state()
        identity = identify() if callable(identify) else identify
        problems = self._generation_problems(
            state, seat_id, identity, skills, grants)
        if problems:
            return {"ok": False, "problems": problems,
                    "seat": seat_id}
        proposal = self._open_proposal(state, seat_id)
        eff = effective_case(state, seat_id)
        delivery = None
        if delivery_declaration:
            # The door scope (2026-11-24): the delivery
            # declaration stands in the pinned case's
            # content; sealing it is the generator's act —
            # the sealed generated record carries the exact
            # declaration the case stands under, bound to
            # this assembly, so the doorway, the loop and
            # the checker read one declaration, never a
            # mutable preference. A generation asked to
            # seal a declaration the case does not carry
            # (or carries malformed) fails preflight whole.
            content = eff.get("content") or {}
            delivery = content.get("delivery")
            if not isinstance(delivery, dict) or \
                    set(delivery) != {"destination",
                                      "route"} or \
                    any(not isinstance(
                            delivery.get(key), str)
                        or not delivery.get(key)
                        for key in ("destination",
                                    "route")):
                return {"ok": False,
                        "problems": [
                            "the delivery declaration was "
                            "asked to be sealed but the "
                            "pinned case carries no "
                            "well-formed delivery "
                            "declaration"],
                        "seat": seat_id}
        combined = exec_room and any(
            isinstance(g, dict)
            and g.get("tool")
            in _tool_policy.RETRIEVAL_TOOLS
            for g in grants or [])
        if isinstance(presentation_declaration, str) \
                and presentation_declaration not in (
                    _tool_policy.PRESENTATION_CONTRACT,
                    _tool_policy.PRESENTATION_CONTRACT_V2):
            # The pointer-rule successor (INDEX 568): the
            # declaration names one of the two contracts
            # the framework knows — v1, or v2 under which
            # a gathered entry's content is presented
            # once and stands as a pointer after. Any
            # other name is a contract nothing derives:
            # fail preflight whole rather than seal a
            # presentation no wake will ever make and no
            # checker will ever verify.
            return {"ok": False,
                    "problems": [
                        "the presentation declaration names "
                        f"{presentation_declaration!r}, "
                        "which is neither the staged-"
                        "onboarding contract nor its pointer-"
                        "rule successor; a generation seals "
                        "one of the two or neither"],
                    "seat": seat_id}
        if presentation_declaration and not combined:
            # The staged-onboarding contract's population
            # is the combined configuration alone (INDEX
            # 544): outside it the loop presents as it
            # always has, so a record claiming the staged
            # presentation there would claim a presentation
            # no wake will ever make. Fail preflight whole,
            # as the delivery declaration's preflight does.
            return {"ok": False,
                    "problems": [
                        "the staged-onboarding presentation "
                        "declaration was asked to be sealed "
                        "but this generation is not the "
                        "combined configuration (an exec-room "
                        "generation carrying retrieval "
                        "grants), the only population the "
                        "contract stands for"],
                    "seat": seat_id}
        if worked_example is not None:
            # Round nine's correction pair (INDEX 548):
            # the worked example seals only beside the
            # presentation contract, on the pinned case's
            # first glossary file, its result whole and
            # internally consistent — the loop presents
            # the seal and the checker re-derives it, so
            # a seal naming anything else would claim a
            # demonstration the office never made. Fail
            # preflight whole, as the declarations do.
            example_problem = _worked_example_problem(
                worked_example,
                (eff.get("content") or {}).get("glossary"),
                presentation_declaration)
            if example_problem is not None:
                return {"ok": False,
                        "problems": [example_problem],
                        "seat": seat_id}
        delivery_evidence = None
        if delivery_evidence_declaration:
            # Round ten (INDEX 552): the delivery-evidence
            # declaration stands in the pinned case's
            # content as its own component beside the
            # delivery declaration — the addresses whose
            # whole content must stand in the worker's
            # working set before his contribution is
            # adjudicated as a delivery. Sealing binds it
            # to this assembly exactly as the delivery
            # declaration is bound. It seals only with the
            # door (the delivery declaration sealed in the
            # same generation) and only in the combined
            # configuration, the working-set population —
            # anywhere else the record would claim a gate
            # that never stands. Fail preflight whole, as
            # the other declarations do.
            if not delivery_declaration:
                return {"ok": False,
                        "problems": [
                            "the delivery-evidence "
                            "declaration was asked to be "
                            "sealed but this generation does "
                            "not seal the delivery "
                            "declaration; without the door "
                            "there is nothing for the "
                            "evidence gate to guard"],
                        "seat": seat_id}
            if not combined:
                return {"ok": False,
                        "problems": [
                            "the delivery-evidence "
                            "declaration was asked to be "
                            "sealed but this generation is "
                            "not the combined configuration "
                            "(an exec-room generation "
                            "carrying retrieval grants), "
                            "the working-set population the "
                            "declaration speaks of"],
                        "seat": seat_id}
            content = eff.get("content") or {}
            evidence = content.get("delivery_evidence")
            if not isinstance(evidence, dict) or \
                    set(evidence) != {"addresses"} or \
                    not isinstance(
                        evidence.get("addresses"), list) or \
                    not evidence["addresses"] or \
                    any(not isinstance(address, str)
                        or not address
                        for address in
                        evidence["addresses"]):
                return {"ok": False,
                        "problems": [
                            "the delivery-evidence "
                            "declaration was asked to be "
                            "sealed but the pinned case "
                            "carries no well-formed "
                            "delivery-evidence declaration "
                            "(a mapping naming exactly "
                            "addresses: a non-empty list of "
                            "sandbox addresses)"],
                        "seat": seat_id}
            delivery_evidence = evidence
        delivery_floor = None
        if delivery_floor_declaration:
            # The third gate (INDEX 557): the
            # delivery-length declaration stands in the
            # pinned case's content as its own component
            # beside the delivery declaration — the
            # minimum word count a contribution must
            # reach before it is adjudicated as a
            # delivery. Sealing binds it to this assembly
            # exactly as the delivery declaration is
            # bound. It seals only with the door (the
            # delivery declaration sealed in the same
            # generation): the floor is a property of
            # the delivery itself, and its subject — the
            # contributed text — stands wherever the
            # door stands, so the combined configuration
            # is not required. Fail preflight whole, as
            # the other declarations do.
            if not delivery_declaration:
                return {"ok": False,
                        "problems": [
                            "the delivery-length "
                            "declaration was asked to be "
                            "sealed but this generation "
                            "does not seal the delivery "
                            "declaration; without the door "
                            "there is nothing for the "
                            "length gate to guard"],
                        "seat": seat_id}
            content = eff.get("content") or {}
            floor = content.get("delivery_floor")
            if not isinstance(floor, dict) or \
                    set(floor) != {"min_words"} or \
                    not isinstance(
                        floor.get("min_words"), int) or \
                    isinstance(
                        floor.get("min_words"), bool) or \
                    floor["min_words"] < 1:
                return {"ok": False,
                        "problems": [
                            "the delivery-length "
                            "declaration was asked to be "
                            "sealed but the pinned case "
                            "carries no well-formed "
                            "delivery-length declaration "
                            "(a mapping naming exactly "
                            "min_words: a positive whole "
                            "number of words)"],
                        "seat": seat_id}
            delivery_floor = floor
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
        if combined:
            # The combined configuration declares the
            # working-set contract (see the constant above):
            # the execution room plus retrieval grants is
            # the population whose wake packages carry the
            # gathered material forward.
            record["working_set_contract"] = \
                _tool_policy.WORKING_SET_CONTRACT
        if presentation_declaration:
            # Staged onboarding (INDEX 544), sealed beside
            # the working-set contract whose population it
            # shares — preflight above has already refused
            # the declaration anywhere else. True seals v1,
            # exactly as it always has; the v2 name seals
            # the pointer-rule successor (INDEX 568) under
            # its own name — v1's meaning under its name
            # does not change.
            record["presentation_contract"] = (
                _tool_policy.PRESENTATION_CONTRACT
                if presentation_declaration is True
                else presentation_declaration)
        if worked_example is not None:
            # Round nine's correction pair (INDEX 548),
            # sealed beside the presentation contract
            # whose files stage presents it — preflight
            # above has already refused the example
            # anywhere else, on any other file, or with
            # any other result.
            record["worked_example"] = copy.deepcopy(
                worked_example)
        if delivery_declaration:
            record["delivery"] = copy.deepcopy(delivery)
        if delivery_evidence_declaration:
            # Round ten (INDEX 552), sealed beside the
            # delivery declaration it guards — preflight
            # above has already refused it anywhere else
            # or against a case carrying it malformed.
            record["delivery_evidence"] = copy.deepcopy(
                delivery_evidence)
        if delivery_floor_declaration:
            # The third gate (INDEX 557), sealed beside
            # the delivery declaration it guards —
            # preflight above has already refused it
            # without the door or against a case carrying
            # it malformed.
            record["delivery_floor"] = copy.deepcopy(
                delivery_floor)
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
