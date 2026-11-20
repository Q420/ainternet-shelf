"""Sabotage target mechanisms (Stage 8).

Each mechanism names ONE guard in stages 1-7: the file(s) it
lives in, the exact source anchor(s) the matrix replaces in a
SCRATCH copy to neutralise it, and the suites to re-run. The
real trees are never patched — the matrix copies the tree,
applies the replacement there, and the witness runner observes
the outcomes.

A patch is (path relative to the duenna-fix root, anchor,
replacement, expected_count). The anchor must occur exactly
expected_count times in the real file; the matrix refuses to
run a mechanism whose anchor does not verify, and records the
refusal rather than guessing.
"""

NEUT = "  # STAGE8-NEUTRALISED"


def _p(path, anchor, replacement, count=1):
    return {"path": path, "anchor": anchor,
            "replacement": replacement, "count": count}


MECHANISMS = {
    # ---------------- Stage 1 ----------------
    "s1.verify_chain": {
        "description": "record.verify_chain recomputes every "
                       "event digest and link (stage1/record.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/record.py",
            "def verify_chain(events: list[dict]) -> tuple[bool, int | None]:",
            "def verify_chain(events: list[dict]) -> tuple[bool, int | None]:\n"
            "    return (True, None)" + NEUT)],
    },
    "s1.structural_validity": {
        "description": "validator._is_structurally_valid_event "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/record.py",
            "def _is_structurally_valid_event(ev) -> bool:",
            "def _is_structurally_valid_event(ev) -> bool:\n"
            "    return True" + NEUT)],
    },
    "s1.terminal_check": {
        "description": "validator._check_terminal_record: exactly "
                       "one CLOSURE, in last place "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "def _check_terminal_record(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:",
            "def _check_terminal_record(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:\n"
            "    return (\"PASS\", {})" + NEUT)],
    },
    "s1.account_whole": {
        "description": "validator._check_account_completeness as "
                       "a whole (stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "def _check_account_completeness(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:",
            "def _check_account_completeness(events: list[dict], parse_error: str | None = None) -> tuple[str, dict]:\n"
            "    return (\"PASS\", {})" + NEUT)],
    },
    "s1.account_reconciliation": {
        "description": "account completeness reconciliation "
                       "FAIL branches: duplicate_record / "
                       "duplicate_account / omitted / extra / "
                       "altered (stage1/validator.py)",
        "suites": [1],
        "patches": [
            _p("stage1/validator.py",
               "    if duplicate_record:",
               "    if False:" + NEUT),
            _p("stage1/validator.py",
               "    if duplicate_account:",
               "    if False:" + NEUT),
            _p("stage1/validator.py",
               "    if omitted:",
               "    if False:" + NEUT),
            _p("stage1/validator.py",
               "    if extra:",
               "    if False:" + NEUT),
            _p("stage1/validator.py",
               "    if altered:",
               "    if False:" + NEUT),
        ],
    },
    "s1.account_schema": {
        "description": "account schema facet: malformed account "
                       "entries fail validation "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "    if schema_invalid:",
            "    if False:" + NEUT)],
    },
    "s1.account_complete_unknowns": {
        "description": "COMPLETE declared with unknowns stands "
                       "is refused (stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "    if status == \"COMPLETE\" and unknowns:",
            "    if False:" + NEUT)],
    },
    "s1.account_status_incomplete": {
        "description": "INCOMPLETE closure status is reported "
                       "INCOMPLETE, not PASS "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "    if status == \"INCOMPLETE\":",
            "    if False:" + NEUT)],
    },
    "s1.whitespace": {
        "description": "validator._has_content: whitespace-only "
                       "strings name nothing (stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "def _has_content(value) -> bool:",
            "def _has_content(value) -> bool:\n"
            "    return isinstance(value, str) and len(value) > 0"
            + NEUT)],
    },
    "s1.anchor_comparison": {
        "description": "validator chain validity: record head "
                       "compared with the anchor's head/length "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "    if head[\"head_digest\"] != anchor[\"head_digest\"] or \\\n"
            "            head[\"length\"] != anchor[\"length\"]:",
            "    if False:" + NEUT)],
    },
    "s1.anchor_absence": {
        "description": "missing/unreadable anchor yields "
                       "NOT_VERIFIED, never PASS "
                       "(stage1/validator.py)",
        "suites": [1],
        "patches": [_p(
            "stage1/validator.py",
            "    if anchor is None:\n        return NOT_VERIFIED, {",
            "    if anchor is None:\n        return \"PASS\", {"
            + NEUT)],
    },
    # ---------------- Stage 2 ----------------
    "s2.verify_all": {
        "description": "ProvenanceLog.verify as a whole "
                       "(stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "        problems: dict = {}\n        events = self.record.read_all()",
            "        return {}" + NEUT + "\n"
            "        problems: dict = {}\n        events = self.record.read_all()")],
    },
    "s2.sole_issuer": {
        "description": "verify(): provenance events whose "
                       "digests the writer never issued are "
                       "refused (stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "        unissued = sorted(\n"
            "            ev[\"seq\"] for ev in provenance_events\n"
            "            if ev.get(\"digest\") not in self._issued_digests)",
            "        unissued = []" + NEUT)],
    },
    "s2.registry_completeness": {
        "description": "verify(): record provenance digests "
                       "must equal the writer's issued registry "
                       "(stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "        if record_digests != registry_digests:",
            "        if False:" + NEUT)],
    },
    "s2.chain_in_verify": {
        "description": "verify() recomputes the record chain "
                       "before trusting any digest on it "
                       "(stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "        if not chain_ok:\n"
            "            return {CHAIN_VERIFICATION_FAILED: first_bad_seq}",
            "        if False:" + NEUT + "\n"
            "            return {CHAIN_VERIFICATION_FAILED: first_bad_seq}")],
    },
    "s2.close_schema": {
        "description": "construction_close schema facets: "
                       "fields absent from both / outside the "
                       "schema (stage2/construction.py, "
                       "_differing, indent 4)",
        "suites": [2],
        "patches": [
            _p("stage2/construction.py",
               "    if missing:\n"
               "        differing[\"schema_fields_absent_from_both\"] = missing",
               "    if False:" + NEUT + "\n"
               "        differing[\"schema_fields_absent_from_both\"] = missing"),
            _p("stage2/construction.py",
               "    if not_schema_a:\n"
               "        differing[\"artefact_fields_outside_schema\"] = not_schema_a",
               "    if False:" + NEUT + "\n"
               "        differing[\"artefact_fields_outside_schema\"] = not_schema_a"),
            _p("stage2/construction.py",
               "    if not_schema_e:\n"
               "        differing[\"entry_fields_outside_schema\"] = not_schema_e",
               "    if False:" + NEUT + "\n"
               "        differing[\"entry_fields_outside_schema\"] = not_schema_e"),
        ],
    },
    "s2.close_fieldset": {
        "description": "construction_close field-set facets: "
                       "artefact/entry field disagreement "
                       "(stage2/construction.py, _differing, "
                       "indent 4)",
        "suites": [2],
        "patches": [
            _p("stage2/construction.py",
               "    if only_artefact:\n"
               "        differing[\"fields_in_artefact_without_entry\"] = only_artefact",
               "    if False:" + NEUT + "\n"
               "        differing[\"fields_in_artefact_without_entry\"] = only_artefact"),
            _p("stage2/construction.py",
               "    if only_entries:\n"
               "        differing[\"fields_in_entries_not_in_artefact\"] = only_entries",
               "    if False:" + NEUT + "\n"
               "        differing[\"fields_in_entries_not_in_artefact\"] = only_entries"),
            _p("stage2/construction.py",
               "    if missing_a:\n"
               "        differing[\"schema_fields_missing_from_artefact\"] = missing_a",
               "    if False:" + NEUT + "\n"
               "        differing[\"schema_fields_missing_from_artefact\"] = missing_a"),
            _p("stage2/construction.py",
               "    if missing_e:\n"
               "        differing[\"schema_fields_missing_from_entries\"] = missing_e",
               "    if False:" + NEUT + "\n"
               "        differing[\"schema_fields_missing_from_entries\"] = missing_e"),
        ],
    },
    "s2.close_value": {
        "description": "construction_close value facet: closed "
                       "values must equal entry values "
                       "(stage2/construction.py, _differing, "
                       "indent 4)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "    if value_mismatches:\n"
            "        differing[\"value_mismatches\"] = value_mismatches",
            "    if False:" + NEUT + "\n"
            "        differing[\"value_mismatches\"] = value_mismatches")],
    },
    "s2.build_duplicates": {
        "description": "build_from_entries duplicate-entry "
                       "refusal (stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "    if duplicates:",
            "    if False:" + NEUT)],
    },
    "s2.close_duplicates": {
        "description": "construction_close duplicate-entry "
                       "facet (stage2/construction.py, _differing, "
                       "indent 4)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "    if duplicate_entries:\n"
            "        differing[\"duplicate_entries\"] = sorted(set(duplicate_entries))",
            "    if False:" + NEUT + "\n"
            "        differing[\"duplicate_entries\"] = sorted(set(duplicate_entries))")],
    },
    "s2.entry_validation": {
        "description": "append_entry canonical-encodability "
                       "check (stage2/construction.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/construction.py",
            "            _canonical(value)",
            "            pass" + NEUT)],
    },
    "s2.schema_freeze": {
        "description": "FrozenSchema seal (stage2/schema.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/schema.py",
            "    def __setattr__(self, name, value):\n"
            "        if getattr(self, \"_frozen\", False):",
            "    def __setattr__(self, name, value):\n"
            "        if False:" + NEUT)],
    },
    "s2.schema_validation": {
        "description": "schema section validation: duplicate "
                       "and nameless fields refused "
                       "(stage2/schema.py)",
        "suites": [2],
        "patches": [
            _p("stage2/schema.py",
               "    if len(set(names)) != len(names):",
               "    if False:" + NEUT),
            _p("stage2/schema.py",
               "        if not _has_content(name):",
               "        if False:" + NEUT),
        ],
    },
    "s2.schema_tuples": {
        "description": "schema sections stored as immutable "
                       "tuples (stage2/schema.py)",
        "suites": [2],
        "patches": [_p(
            "stage2/schema.py",
            "    names = tuple(fields)",
            "    names = list(fields)" + NEUT)],
    },
    # ---------------- Stage 3 ----------------
    "s3.chain_facet": {
        "description": "verify_record_current chain facet: the "
                       "persisted record's chain is recomputed "
                       "before any writer trusts it "
                       "(stage3/binder.py; shared by stages "
                       "3, 5, 6, 7)",
        "suites": [3, 5, 6, 7],
        "patches": [_p(
            "stage3/binder.py",
            "    chain_ok, first_bad_seq = verify_chain(events)\n"
            "    if not chain_ok:",
            "    chain_ok, first_bad_seq = verify_chain(events)\n"
            "    if False:" + NEUT)],
    },
    "s3.terminal_facet": {
        "description": "verify_record_current terminal facet: "
                       "persisted length/head must equal the "
                       "writer's in-memory length/head "
                       "(stage3/binder.py; shared by stages "
                       "3, 5, 7)",
        "suites": [3, 5, 7],
        "patches": [_p(
            "stage3/binder.py",
            "    if len(events) != record.length \\\n"
            "            or persisted_head != record.head_digest:",
            "    if False:" + NEUT)],
    },
    "s3.freeze_surface": {
        "description": "freeze surface consistency: pin and "
                       "every surface name one subject "
                       "(stage3/binder.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/binder.py",
            "        if len(named) != 1:",
            "        if False:" + NEUT)],
    },
    "s3.freeze_served_pin": {
        "description": "freeze served-identity vs pin "
                       "comparison (stage3/binder.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/binder.py",
            "        if served_identity != config.subject_pin:",
            "        if False:" + NEUT)],
    },
    "s3.capture_subject": {
        "description": "capture gate served-identity vs "
                       "expected comparison (stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "        if served_identity != expected:",
            "        if False:" + NEUT)],
    },
    "s3.receipt_record_presence": {
        "description": "output gate: a receipt with no "
                       "CONSUMPTION_RECEIPT event on the record "
                       "is refused (stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "            if recorded is None:",
            "            if False:" + NEUT)],
    },
    "s3.receipt_facts": {
        "description": "output gate: recorded receipt fields "
                       "must agree with the live receipt object "
                       "(stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "                    if recorded.get(field) != object_value:",
            "                    if False:" + NEUT)],
    },
    "s3.receipt_binding": {
        "description": "output gate: recorded receipt "
                       "component/invocation must match the "
                       "output's (stage3/admission.py)",
        "suites": [3],
        "patches": [
            _p("stage3/admission.py",
               "                if recorded.get(\"component\") \\\n"
               "                        != output.get(\"component\"):",
               "                if False:" + NEUT),
            _p("stage3/admission.py",
               "                if recorded.get(\"invocation\") \\\n"
               "                        != output.get(\"invocation\"):",
               "                if False:" + NEUT),
        ],
    },
    "s3.receipt_coverage": {
        "description": "output gate: every value used must be "
                       "covered by the recorded receipt "
                       "(stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "            uncovered = sorted(\n"
            "                name for name in values_used\n"
            "                if name not in recorded_values)",
            "            uncovered = []" + NEUT)],
    },
    "s3.output_not_frozen": {
        "description": "output gate: values never frozen are "
                       "refused (stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "        if not_frozen:\n"
            "            problems[\"values_not_in_frozen_config\"] = not_frozen",
            "        if False:" + NEUT + "\n"
            "            problems[\"values_not_in_frozen_config\"] = not_frozen")],
    },
    "s3.output_differing": {
        "description": "output gate: values differing from "
                       "the frozen object are refused "
                       "(stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "        if differing:\n"
            "            problems[\"values_differ_from_frozen_config\"] = [",
            "        if False:" + NEUT + "\n"
            "            problems[\"values_differ_from_frozen_config\"] = [")],
    },
    "s3.output_digest": {
        "description": "output gate: the output's quoted "
                       "config digest is checked against the "
                       "frozen object (stage3/admission.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/admission.py",
            "        if output.get(\"config_digest\") != self.run.config_digest:",
            "        if False:" + NEUT)],
    },
    "s3.frozenrun_seal": {
        "description": "FrozenRun seal (stage3/binder.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/binder.py",
            "    def __setattr__(self, name, value):\n"
            "        if getattr(self, \"_frozen\", False):",
            "    def __setattr__(self, name, value):\n"
            "        if False:" + NEUT)],
    },
    "s3.policy_recompute": {
        "description": "derived-limit policy recompute "
                       "(stage3/config.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/config.py",
            "def derived_limit_problems(config: FrozenConfig) -> dict:",
            "def derived_limit_problems(config: FrozenConfig) -> dict:\n"
            "    return {}" + NEUT)],
    },
    "s3.consume_unknown": {
        "description": "consume(): governed values outside "
                       "the frozen configuration are refused "
                       "(stage3/access.py)",
        "suites": [3],
        "patches": [_p(
            "stage3/access.py",
            "        if unknown:",
            "        if False:" + NEUT)],
    },
    # ---------------- Stage 4 ----------------
    "s4.identity_check": {
        "description": "validate_verdict K7 object-identity "
                       "lookup: the verdict object must be the "
                       "one this contract issued "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "and candidate[\"verdict\"] is verdict:",
            "and True:" + NEUT)],
    },
    "s4.contract_identity": {
        "description": "validate_verdict K7 lookup, contract "
                       "conjunct: the issuance entry must be an "
                       "entry issued by THIS contract "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            if candidate[\"contract\"] is contract \\",
            "            if True \\")],
    },
    "s4.fingerprint_check": {
        "description": "validate_verdict issuance fingerprint "
                       "comparison (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "        if fingerprint(verdict) != entry[\"fingerprint\"]:",
            "        if False:" + NEUT)],
    },
    "s4.pinned_hash": {
        "description": "validate_verdict pinned implementation "
                       "hash comparison (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "        if verdict[\"implementation_hash\"] != pinned_hashes.get(verdict.get(\"procedure\")):",
            "        if False:" + NEUT)],
    },
    "s4.field_checks": {
        "description": "validate_verdict field presence and "
                       "match checks: procedure, version, hash, "
                       "input identity, verdict shape "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [
            _p("stage4/contract.py",
               "        if not isinstance(verdict, dict):",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if verdict.get(\"procedure\") != contract.procedure:",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if \"version\" not in verdict:",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if verdict[\"version\"] != contract.version:",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if \"implementation_hash\" not in verdict:",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if \"input\" not in verdict:",
               "        if False:" + NEUT),
            _p("stage4/contract.py",
               "        if verdict[\"input\"] != contract.input_id:",
               "        if False:" + NEUT),
        ],
    },
    "s4.seal": {
        "description": "CheckerContract seal: procedure "
                       "binding write-once (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            if getattr(self, \"_sealed\", False):",
            "            if False:" + NEUT, count=2)],
    },
    "s4.construction_binding": {
        "description": "CheckerContract binds the procedure "
                       "callable at construction; later module "
                       "registry rebinding does not redirect "
                       "dispatch (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            self._procedure_fn = registry[procedure]",
            "            self._procedure_fn = lambda payload, sha: "
            "PROCEDURE_REGISTRY[PROCEDURE_IDENTITY](payload, sha)"
            + NEUT)],
    },
    "s4.registry_immutable": {
        "description": "the procedure registry is a "
                       "MappingProxyType: remapping is refused "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "    registry = MappingProxyType({PROCEDURE_IDENTITY: preservation_check})",
            "    registry = {PROCEDURE_IDENTITY: preservation_check}"
            + NEUT)],
    },
    "s4.construction_validation": {
        "description": "CheckerContract construction refuses "
                       "a procedure the registry does not hold "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            if procedure not in registry:",
            "            if False:" + NEUT)],
    },
    "s4.run_pin": {
        "description": "run() refuses an unpinned contract "
                       "(stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            if not self.pinned:",
            "            if False:" + NEUT)],
    },
    "s4.run_input_identity": {
        "description": "run() refuses an artefact that is not "
                       "the defined input (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "            if artefact.get(\"id\") != self.input_id:",
            "            if False:" + NEUT)],
    },
    "s4.digest_comparison": {
        "description": "preservation_check recomputes the "
                       "payload digest and compares it with "
                       "the pinned digest — regardless of any "
                       "corrupt flag (stage4/contract.py)",
        "suites": [4],
        "patches": [_p(
            "stage4/contract.py",
            "    return digest if digest == expected_sha else None",
            "    return digest" + NEUT)],
    },
    # ---------------- Stage 5 ----------------
    "s5.event_recognition": {
        "description": "receiver._operation_events: operation "
                       "state recognised from the record's "
                       "INSERTION_APPLIED / OPERATION_CONSUMED "
                       "events (stage5/receiver.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/receiver.py",
            "    def _operation_events(events, operation_id: str):",
            "    def _operation_events(events, operation_id: str):\n"
            "        return (None, None)" + NEUT)],
    },
    "s5.payload_binding": {
        "description": "present(): a recorded payload digest "
                       "binds the identity; a different "
                       "payload under it is refused "
                       "(stage5/receiver.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/receiver.py",
            "        if recorded_digest is not None \\\n"
            "                and recorded_digest != operation.payload_digest:",
            "        if False:" + NEUT)],
    },
    "s5.completed_state": {
        "description": "present() consumed fast path: the "
                       "consumption's applied reference must "
                       "resolve to this operation's applied "
                       "event AND the effect must still exist "
                       "(stage5/receiver.py)",
        "suites": [5],
        "patches": [
            _p("stage5/receiver.py",
               "            if applied_ev is None \\\n"
               "                    or cited_applied_digest != applied_ev[\"digest\"]:",
               "            if False:" + NEUT),
            _p("stage5/receiver.py",
               "            if effect is None:\n"
               "                raise InsertionDivergence(op_id, {\n"
               "                    EFFECT_MISSING: {\n"
               "                        \"applied_event_seq\": applied_ev[\"seq\"],\n"
               "                        \"consumed_event_seq\": consumed_ev[\"seq\"],",
               "            if False:" + NEUT + "\n"
               "                raise InsertionDivergence(op_id, {\n"
               "                    EFFECT_MISSING: {\n"
               "                        \"applied_event_seq\": applied_ev[\"seq\"],\n"
               "                        \"consumed_event_seq\": consumed_ev[\"seq\"],"),
        ],
    },
    "s5.applied_effect_divergence": {
        "description": "present(): a recorded insertion whose "
                       "effect is absent is surfaced, never "
                       "repaired (stage5/receiver.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/receiver.py",
            "        if applied_ev is not None and effect is None:",
            "        if False:" + NEUT)],
    },
    "s5.effect_recognition": {
        "description": "present(): a landed effect with the "
                       "record behind it is recognised as the "
                       "single application, not re-applied "
                       "(stage5/receiver.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/receiver.py",
            "        if effect is not None:\n"
            "            # The insertion landed; the record is behind reality",
            "        if False:" + NEUT + "\n"
            "            # The insertion landed; the record is behind reality")],
    },
    "s5.operation_seal": {
        "description": "Operation immutability: the custom "
                       "_sealed __setattr__ guard "
                       "(stage5/operations.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/operations.py",
            "    def __setattr__(self, name, value):\n"
            "        if getattr(self, \"_sealed\", False):",
            "    def __setattr__(self, name, value):\n"
            "        if False:" + NEUT)],
    },
    "s5.payload_copy": {
        "description": "Operation.payload hands out a fresh "
                       "decoded copy on every access; the "
                       "sabotage caches and re-hands the same "
                       "object, so a caller's mutation persists "
                       "(stage5/operations.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/operations.py",
            "        return json.loads(self._payload_canonical)",
            "        _cached = getattr(self, \"_payload_cache\", None)\n"
            "        if _cached is None:\n"
            "            _cached = json.loads(self._payload_canonical)\n"
            "            object.__setattr__(self, \"_payload_cache\", _cached)\n"
            "        return _cached" + NEUT)],
    },
    "s5.identity_function": {
        "description": "operation identity is a function of "
                       "(run, step, slot) — every part binds; "
                       "the sabotage drops slot from the "
                       "mint_operation_id hash input "
                       "(stage5/operations.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/operations.py",
            "        {\"run\": run_id, \"step\": step_id, \"slot\": slot})).hexdigest()",
            "        {\"run\": run_id, \"step\": step_id})).hexdigest()"
            + NEUT)],
    },
    "s5.identity_payload": {
        "description": "operation identity excludes the payload; "
                       "the sabotage variant folds a payload "
                       "digest into the operation identity at "
                       "construction (stage5/operations.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/operations.py",
            "        self.operation_id = mint_operation_id(run_id, step_id, slot)",
            "        self.operation_id = mint_operation_id(run_id, step_id, slot) "
            "+ payload_digest(payload)[:16]" + NEUT)],
    },
    "s5.identity_determinism": {
        "description": "operation identity is deterministic — "
                       "the same triple mints the same identity "
                       "on every call; the sabotage variant "
                       "mixes a per-call object hash into the "
                       "minted identity (stage5/operations.py)",
        "suites": [5],
        "patches": [_p(
            "stage5/operations.py",
            "    return f\"op-{digest}\"",
            "    mint_operation_id._sabotage_counter = "
            "getattr(mint_operation_id, \"_sabotage_counter\", 0) + 1\n"
            "    return f\"op-{digest}-{mint_operation_id._sabotage_counter}\""
            + NEUT)],
    },
    # ---------------- Stage 6 ----------------
    "s6.issuance_token": {
        "description": "GoverningAuthority construction is "
                       "token-gated to the issuance path "
                       "(stage6/authority.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/authority.py",
            "        if _token is not _ISSUANCE_TOKEN:",
            "        if False:" + NEUT)],
    },
    "s6.point_of_use": {
        "description": "capability_is_issued point-of-use "
                       "verification (stage6/authority.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/authority.py",
            "def capability_is_issued(authority) -> bool:",
            "def capability_is_issued(authority) -> bool:\n"
            "    return True" + NEUT)],
    },
    "s6.issuance_record_check": {
        "description": "issue_authority: the presented record "
                       "must digest to the independently held "
                       "pin (stage6/authority.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/authority.py",
            "    if presented.digest != PINNED_AUTHORITY_DIGEST:",
            "    if False:" + NEUT)],
    },
    "s6.resolve_attribution": {
        "description": "discrepancy citations must resolve to "
                       "a real ATTRIBUTION_RECORDED event on "
                       "the verified snapshot "
                       "(stage6/discrepancy.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/discrepancy.py",
            "def _resolve_attribution(events, attribution_event):",
            "def _resolve_attribution(events, attribution_event):\n"
            "    return attribution_event" + NEUT)],
    },
    "s6.label_conversion": {
        "description": "convert_local_label always refuses: "
                       "no local label converts to an "
                       "attribution class (stage6/attribution.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/attribution.py",
            "    raise ConversionRefused(label, target_class)",
            "    return target_class" + NEUT)],
    },
    "s6.vocabulary": {
        "description": "mint_attribution refuses classes "
                       "outside the attribution vocabulary "
                       "(stage6/attribution.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/attribution.py",
            "        if cls not in ATTRIBUTION_CLASSES:",
            "        if False:" + NEUT)],
    },
    "s6.one_record": {
        "description": "one attribution record per failure: a "
                       "second mint is refused "
                       "(stage6/attribution.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/attribution.py",
            "        if existing is not None:",
            "        if False:" + NEUT)],
    },
    "s6.format_prescribed": {
        "description": "ResponseContract.format_prescribed: "
                       "was the demanded format actually "
                       "prescribed in the delivered instruction "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "    def format_prescribed(self, instruction_text: str) -> bool:",
            "    def format_prescribed(self, instruction_text: str) -> bool:\n"
            "        return True" + NEUT)],
    },
    "s6.format_prescribed_false": {
        "description": "ResponseContract.format_prescribed, "
                       "opposite-direction sabotage: the "
                       "demanded format is reported NEVER "
                       "prescribed, whatever the preserved "
                       "instruction says "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "    def format_prescribed(self, instruction_text: str) -> bool:",
            "    def format_prescribed(self, instruction_text: str) -> bool:\n"
            "        return False" + NEUT)],
    },
    "s6.extraction": {
        "description": "ResponseContract.extract, regex path: "
                       "the checker's extraction returns None "
                       "for every response, whatever it states "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "            m = re.search(self.pattern, response)",
            "            m = None" + NEUT)],
    },
    "s6.input_defect_branch": {
        "description": "examine(): the input-defect branch — "
                       "a defect in what was supplied TO the "
                       "agent is attributed INPUT before any "
                       "extraction fact is read "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "    if input_defect is not None:",
            "    if False:" + NEUT)],
    },
    "s6.response_matching": {
        "description": "ResponseContract required-lines "
                       "matching: the response must carry the "
                       "contract's required lines "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "            if line not in response:",
            "            if False:" + NEUT)],
    },
    "s6.schema_binding": {
        "description": "examine(): the presented schema / "
                       "checker binding must resolve to the "
                       "independently held pin "
                       "(stage6/schema_contract.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/schema_contract.py",
            "    if moved:\n        finding.update({",
            "    if False:" + NEUT + "\n        finding.update({")],
    },
    "s6.schema_seal": {
        "description": "the _Sealed base: schema, contract, "
                       "instruction and checker objects are "
                       "sealed (stage6/authority.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/authority.py",
            "    def __setattr__(self, name, value):\n"
            "        if getattr(self, \"_sealed\", False):",
            "    def __setattr__(self, name, value):\n"
            "        if False:" + NEUT)],
    },
    "s6.g6_contradiction": {
        "description": "resolve_report: a literal location "
                       "contradicting the rendered resolution "
                       "is flagged, never corrected "
                       "(stage6/examiner.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/examiner.py",
            "        if ref[\"literal_location\"] != rendered:",
            "        if False:" + NEUT)],
    },
    "s6.g6_resolution": {
        "description": "resolve_report: an unresolvable "
                       "reference is an error, not a flag "
                       "(stage6/examiner.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/examiner.py",
            "        ev = by_seq.get(seq)",
            "        ev = by_seq.get(seq) or {\"seq\": seq, "
            "\"event_sha256\": None, \"type\": \"UNKNOWN\", "
            "\"body\": {}}" + NEUT)],
    },
    "s6.one_resolution": {
        "description": "a discrepancy already resolved cannot "
                       "be resolved again: the follow check in "
                       "_append_resolution (stage6/discrepancy.py)",
        "suites": [6],
        "patches": [_p(
            "stage6/discrepancy.py",
            "    if follow:",
            "    if False:" + NEUT)],
    },
    # ---------------- Stage 7 ----------------
    "s7.pin_constructor": {
        "description": "TrustAnchor construction is "
                       "token-gated to the pinned store "
                       "(stage7/trust_anchor.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/trust_anchor.py",
            "        if _token is not _PIN_TOKEN:",
            "        if False:" + NEUT)],
    },
    "s7.pin_point_of_use": {
        "description": "_require_pinned_anchor: every entry "
                       "point validates the anchor against the "
                       "pin (stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "def _require_pinned_anchor(anchor, receipt_id):",
            "def _require_pinned_anchor(anchor, receipt_id):\n"
            "    return None" + NEUT)],
    },
    "s7.authentication": {
        "description": "_state_from: the presented tag must "
                       "authenticate under the pinned anchor "
                       "(stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    if not anchor.authenticates(",
            "    if False and not anchor.authenticates(" + NEUT)],
    },
    "s7.digest_comparison": {
        "description": "_state_from: collected content's "
                       "digest must equal the issuance body's "
                       "content digest (stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    if _sha256(content) != body[\"content_digest\"]:",
            "    if False:" + NEUT)],
    },
    "s7.issuance_lookup": {
        "description": "_issuance_event: a receipt id with no "
                       "RECEIPT_ISSUED event is not a lifecycle "
                       "receipt (stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "def _issuance_event(events, receipt_id: str):",
            "def _issuance_event(events, receipt_id: str):\n"
            "    return {\"type\": \"RECEIPT_ISSUED\", \"body\": "
            "{\"receipt_id\": receipt_id, \"issuer_id\": "
            "\"stage8-synthetic\", \"commitment_id\": "
            "\"stage8-synthetic\", \"terms_digest\": "
            "\"stage8-synthetic\", \"content_digest\": \"0\" * 64}}"
            + NEUT)],
    },
    "s7.package_lookup": {
        "description": "package read-back: an entry removed "
                       "from the package reads as absent, and "
                       "uncollected content reads as no content; "
                       "the sabotage falsifies ONLY the "
                       "missing-file return points inside "
                       "read_entry/read_content, so genuine "
                       "entries still read back honestly "
                       "(stage7/package.py)",
        "suites": [7],
        "patches": [
            _p("stage7/package.py",
               "        if not os.path.exists(path):\n"
               "            return None\n"
               "        with open(path, \"r\", encoding=\"utf-8\") as f:",
               "        if not os.path.exists(path):\n"
               "            return {\"auth_tag\": None}" + NEUT + "\n"
               "        with open(path, \"r\", encoding=\"utf-8\") as f:"),
            _p("stage7/package.py",
               "        if not os.path.exists(path):\n"
               "            return None\n"
               "        with open(path, \"rb\") as f:",
               "        if not os.path.exists(path):\n"
               "            return b\"stage8-synthetic-content\"" + NEUT + "\n"
               "        with open(path, \"rb\") as f:"),
        ],
    },
    "s7.issue_once": {
        "description": "issue_receipt: one commitment has "
                       "exactly one receipt "
                       "(stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    if _issuance_event(events, receipt_id) is not None:",
            "    if False:" + NEUT)],
    },
    "s7.collect_issuance": {
        "description": "collect_receipt: collection requires "
                       "a standing issuance (stage7/receipts.py; "
                       "the long anchor, through the refusal "
                       "reason, distinguishes collect_receipt "
                       "from _state_from's identical first two "
                       "lines)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    issuance = _issuance_event(events, receipt_id)\n"
            "    if issuance is None:\n"
            "        raise ReceiptRefused(receipt_id, {\n"
            "            \"reason\": \"no issuance for this receipt stands on \"",
            "    issuance = _issuance_event(events, receipt_id)\n"
            "    if False:" + NEUT + "\n"
            "        raise ReceiptRefused(receipt_id, {\n"
            "            \"reason\": \"no issuance for this receipt stands on \"")],
    },
    "s7.collect_once": {
        "description": "collect_receipt: content already "
                       "collected cannot be collected again "
                       "(stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    if package.has_content(receipt_id):",
            "    if False:" + NEUT)],
    },
    "s7.unrecorded_accounting": {
        "description": "receipt_account: package entries with "
                       "no issuance are named as unrecorded "
                       "(stage7/receipts.py)",
        "suites": [7],
        "patches": [_p(
            "stage7/receipts.py",
            "    unrecorded = sorted(set(package.entry_ids())\n"
            "                        - set(issued_ids))",
            "    unrecorded = []" + NEUT)],
    },
}


def verify_anchors(root: str) -> dict:
    """Check every patch anchor against the real tree.
    Returns {mechanism_id: [problems]} — empty dict means
    every anchor verified at its expected count."""
    import os
    problems = {}
    for mech_id, mech in MECHANISMS.items():
        for patch in mech["patches"]:
            path = os.path.join(root, patch["path"])
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            found = text.count(patch["anchor"])
            if found != patch["count"]:
                problems.setdefault(mech_id, []).append(
                    f"{patch['path']}: anchor found {found}x, "
                    f"expected {patch['count']}x: "
                    f"{patch['anchor'][:60]!r}")
    return problems
