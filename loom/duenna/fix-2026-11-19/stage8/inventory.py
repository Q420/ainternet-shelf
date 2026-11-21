"""Fixture inventory (Stage 8, K14).

Every test in stages 1-7, classified. A fixture's IDENTITY is
what it intends to test: the target mechanism path(s) it claims
to discriminate, stated here from a first-hand reading of the
suites (Stage 8 build, 2026-11-20). Its EXECUTION RECORD —
whether it actually discriminates that target — is a different
fact, produced by the sabotage matrix (matrix.py) from the
witness runner's outcomes, never from this file.

Kinds:
- guard:        claims the listed facet mechanism(s); the
                matrix verdict is per (fixture, mechanism).
- joint-guard:  claims a conjunction — it discriminates its
                targets only together (any one guard alone
                still refuses / still passes), so the matrix
                also runs the combined neutralisation.
- functional:   no guard target (behaviour, construction,
                API shape, freshness); collateral-monitored —
                it must stay green under every sabotage.
- control:      a healthy-path control; must stay green.
- boundary:     demonstrates a stated limitation; coverage-
                excluded BY KIND (Stage 1's s8), not a
                NOT-EXERCISED finding.
- exam:         a Stage 4 examination fixture: it applies its
                own sabotage to contract.py and asserts the
                exact failing set of the mechanism suites.
- exam-evidence: the DR-24 replay against the historical
                v2.3 artefact — evidence about the ancestor,
                not a Stage 4 guard fixture.
- reproduction: a Stage 6 reproduction of preserved attempt-3
                evidence (transcription / attribution of the
                historical record).
"""

# test_id -> (targets, kind, note)
ENTRIES = {
    # ---------------- Stage 1 ----------------
    "test_anchor.TestAnchor.test_commit_record_head_uses_current_head_values":
        ([], "functional", "anchor file carries the record's current head values"),
    "test_anchor.TestAnchor.test_deleted_anchor_after_closure_yields_not_verified":
        (["s1.anchor_absence"], "guard", ""),
    "test_anchor.TestAnchor.test_missing_anchor_yields_not_verified":
        (["s1.anchor_absence"], "guard", ""),
    "test_anchor.TestAnchor.test_normal_closed_record_verifies":
        ([], "control", "healthy closed record verifies end to end"),
    "test_anchor.TestAnchor.test_unreadable_anchor_yields_not_verified":
        (["s1.anchor_absence"], "guard", ""),
    "test_anchor.TestAnchor.test_wholesale_rechained_rewrite_caught_by_anchor_mismatch":
        (["s1.anchor_comparison"], "guard",
         "the re-chained chain recomputes cleanly; only the anchor comparison catches it"),
    "test_anchor.TestAnchor.test_write_anchor_takes_only_head_state_values":
        ([], "functional", "anchor writing takes head state only"),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_complete_missing_unknowns":
        (["s1.account_schema"], "guard", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_complete_unknowns_wrong_type":
        (["s1.account_schema"], "guard", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_incomplete_empty_unknowns":
        (["s1.account_schema"], "guard", "INCOMPLETE without unknowns is schema-invalid"),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_incomplete_missing_unknowns":
        (["s1.account_schema"], "guard", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_missing_account_authority":
        (["s1.account_schema"], "guard", "authority naming nothing is schema-invalid"),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_missing_failure_entry_authority":
        (["s1.account_whole"], "joint-guard",
         "the account_invalid branch has no facet mechanism in the matrix; "
         "this fixture discriminates _check_account_completeness only as a whole"),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_unknowns_empty_string_entry":
        (["s1.account_schema"], "guard", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_unknowns_non_string_entry":
        (["s1.account_schema"], "guard", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_wellformed_complete_still_passes":
        ([], "control", ""),
    "test_c6_account_schema.TestC6AccountSchema.test_c6_wellformed_incomplete_still_incomplete":
        (["s1.account_status_incomplete"], "guard", ""),
    "test_closure.TestClosureRunner.test_clean_path_account_complete_with_empty_failures":
        ([], "functional", "ClosureWriter behaviour; no validator facet claimed"),
    "test_closure.TestClosureRunner.test_closure_states_three_endings_separately":
        ([], "functional", "ClosureWriter behaviour"),
    "test_closure.TestClosureRunner.test_each_path_yields_exactly_one_closure_as_last_event":
        ([], "functional", "ClosureWriter behaviour"),
    "test_closure.TestClosureRunner.test_early_stop_account_incomplete_with_unknowns_named":
        ([], "functional", "ClosureWriter behaviour"),
    "test_closure.TestClosureRunner.test_exception_path_still_closes":
        ([], "functional", "ClosureWriter behaviour"),
    "test_closure.TestClosureRunner.test_known_failure_account_lists_failure_with_attribution":
        ([], "functional", "ClosureWriter behaviour"),
    "test_closure.TestClosureRunner.test_known_failure_also_appended_as_failure_event_before_closure":
        ([], "functional", "ClosureWriter behaviour"),
    "test_record.TestEventRecord.test_append_assigns_sequence_and_chains":
        ([], "functional", "EventRecord append mechanics"),
    "test_record.TestEventRecord.test_clean_record_verifies":
        ([], "control", "healthy chain verifies; a verify_chain that always "
         "answers True also passes it — it is a control, not a guard fixture"),
    "test_record.TestEventRecord.test_deleted_event_detected":
        (["s1.verify_chain"], "guard", ""),
    "test_record.TestEventRecord.test_empty_record_verifies":
        ([], "control", ""),
    "test_record.TestEventRecord.test_record_file_is_append_only_jsonl":
        ([], "functional", "record file format"),
    "test_record.TestEventRecord.test_reopen_continues_from_head":
        ([], "functional", "reopen/head mechanics"),
    "test_record.TestEventRecord.test_rewritten_middle_event_detected":
        (["s1.verify_chain"], "guard", ""),
    "test_stage1_cases.TestStage1Cases.test_case1_normal_completion":
        ([], "control", ""),
    "test_stage1_cases.TestStage1Cases.test_case2_known_failure_accounted_with_attribution":
        ([], "functional", "closure account of a known failure"),
    "test_stage1_cases.TestStage1Cases.test_case3_early_stop_closes_with_known_unknown_stated":
        ([], "functional", "closure states the known unknown"),
    "test_stage1_cases.TestStage1Cases.test_case4_exception_path_appends_closure":
        ([], "functional", "exception path closure"),
    "test_stage1_cases.TestStage1Cases.test_case5_missing_failure_account":
        (["s1.account_whole"], "joint-guard",
         "the closure body has no account section at all; the refusal "
         "lands on the account-presence branch, which has no facet "
         "mechanism — this fixture discriminates the account function "
         "only as a whole (classification corrected on the matrix's "
         "evidence: it does not touch the reconciliation facets)"),
    "test_stage1_cases.TestStage1Cases.test_case6_missing_attribution_recorded_as_unknown":
        ([], "functional", "ClosureWriter records UNKNOWN attribution"),
    "test_stage1_cases.TestStage1Cases.test_case7_rewritten_chain_detected_by_anchor":
        (["s1.anchor_comparison"], "guard", ""),
    "test_stage1_cases.TestStage1Cases.test_case8_anchor_unavailable_not_verified_never_passed":
        (["s1.anchor_absence"], "guard", ""),
    "test_stage1_cases.TestStage1Cases.test_case9_omitted_known_failure_fails_account_completeness":
        (["s1.account_reconciliation"], "guard", "omitted facet"),
    "test_validator.TestValidator.test_clean_run_passes_all_three":
        ([], "control", ""),
    "test_validator.TestValidator.test_complete_declared_with_unknowns_fails_account":
        (["s1.account_complete_unknowns"], "guard", ""),
    "test_validator.TestValidator.test_early_stop_account_reported_incomplete_not_pass":
        (["s1.account_status_incomplete"], "guard", ""),
    "test_validator.TestValidator.test_edited_middle_event_body_fails_chain_validity":
        (["s1.verify_chain"], "guard", ""),
    "test_validator.TestValidator.test_known_failure_run_passes_all_three":
        ([], "control", ""),
    "test_validator.TestValidator.test_omitted_failure_fails_account_completeness":
        (["s1.account_reconciliation"], "guard", "omitted facet"),
    "test_validator.TestValidator.test_record_with_no_closure_fails_terminal_record":
        (["s1.terminal_check"], "guard", ""),
    "test_validator.TestValidator.test_validator_reads_fresh_from_disk":
        ([], "functional", "freshness: the validator re-reads from disk; "
         "no sabotage in the matrix targets read caching"),
    "test_vane_hardening.TestVaneHardening.test_authority_match_passes":
        ([], "control", ""),
    "test_vane_hardening.TestVaneHardening.test_authority_mismatch_is_altered":
        (["s1.account_reconciliation"], "guard", "altered facet (authority field)"),
    "test_vane_hardening.TestVaneHardening.test_padded_content_accepted_and_preserved":
        ([], "control", "whitespace semantics control: padded content names "
         "something under both the settled term and a plain length check"),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_account_authority_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_account_description_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_account_failure_id_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_description_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_entry_authority_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_failure_id_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_hardening.TestVaneHardening.test_whitespace_only_unknown_rejected":
        (["s1.whitespace"], "guard", ""),
    "test_vane_sabotage.TestVaneSabotage.test_s1_duplicate_terminal_closure":
        (["s1.terminal_check"], "guard", ""),
    "test_vane_sabotage.TestVaneSabotage.test_s1b_two_closures_with_event_afterward":
        (["s1.terminal_check"], "guard", ""),
    "test_vane_sabotage.TestVaneSabotage.test_s1c_closure_followed_by_continuation":
        (["s1.terminal_check"], "guard", ""),
    "test_vane_sabotage.TestVaneSabotage.test_s2_duplicate_failure_id_in_record":
        (["s1.account_reconciliation"], "guard", "duplicate_record facet"),
    "test_vane_sabotage.TestVaneSabotage.test_s3_duplicate_account_failure_id":
        (["s1.account_reconciliation"], "guard", "duplicate_account facet"),
    "test_vane_sabotage.TestVaneSabotage.test_s4_extra_fabricated_account_failure":
        (["s1.account_reconciliation"], "guard", "extra facet"),
    "test_vane_sabotage.TestVaneSabotage.test_s5_altered_failure_description_or_attribution":
        (["s1.account_reconciliation"], "guard", "altered facet"),
    "test_vane_sabotage.TestVaneSabotage.test_s6_structurally_malformed_event":
        (["s1.structural_validity"], "guard", ""),
    "test_vane_sabotage.TestVaneSabotage.test_s7_corrupted_record_reopened_for_append":
        (["s1.verify_chain", "s1.structural_validity"], "joint-guard",
         "reopen verifies the chain; the corruption is a body edit, so the "
         "chain facet is the expected discriminator and structural validity "
         "the joint claim"),
    "test_vane_sabotage.TestVaneSabotage.test_s8_record_and_anchor_both_rewritten_demonstrates_boundary":
        ([], "boundary",
         "asserts the C3 limitation (a coordinated record+anchor rewrite is "
         "not defeated); no guard target; coverage-excluded by kind"),
    # ---------------- Stage 2 ----------------
    "test_construction.TestConstruction.test_duplicate_entry_for_one_field_refuses":
        (["s2.build_duplicates", "s2.close_duplicates"], "joint-guard",
         "either duplicate guard alone still refuses with the same "
         "duplicate_entries detail; only the conjunction discriminates"),
    "test_construction.TestConstruction.test_entries_for_other_artefacts_are_not_read":
        ([], "functional", "issued_entries is per-artefact; no facet claimed"),
    "test_construction.TestConstruction.test_faithful_artefact_passes_field_for_field":
        ([], "control", ""),
    "test_construction.TestConstruction.test_fresh_writer_over_existing_record_refuses":
        (["s2.sole_issuer"], "guard",
         "asserts the unissued_provenance_events detail exactly; cited in "
         "Stage 2 as whole-verify evidence — for the REGISTRY facet it is "
         "not a discriminator (see the registry-completeness finding)"),
    "test_construction.TestConstruction.test_no_entries_at_all_refuses_and_records_refusal":
        (["s2.close_schema"], "guard", "missing facet (absent from both)"),
    "test_construction.TestConstruction.test_record_chain_still_verifies_after_construction":
        ([], "functional", "post-construction chain health (Stage 1 verify_chain)"),
    "test_construction.TestConstruction.test_unencodable_provenance_value_refused_at_entry":
        (["s2.entry_validation"], "guard", ""),
    "test_construction.TestConstruction.test_well_formed_artefact_closes":
        ([], "control", ""),
    "test_schema.TestFrozenSchema.test_digest_is_deterministic":
        ([], "functional", "schema digest determinism"),
    "test_schema.TestFrozenSchema.test_duplicate_field_names_refused":
        (["s2.schema_validation"], "guard", ""),
    "test_schema.TestFrozenSchema.test_either_section_change_changes_the_one_identity":
        ([], "functional", "schema identity binds both sections"),
    "test_schema.TestFrozenSchema.test_nameless_field_or_version_refused":
        (["s2.schema_validation"], "guard", ""),
    "test_schema.TestFrozenSchema.test_schema_is_frozen_after_construction":
        (["s2.schema_freeze"], "guard", ""),
    "test_schema.TestFrozenSchema.test_sections_are_immutable_tuples":
        (["s2.schema_tuples"], "guard", ""),
    "test_schema.TestFrozenSchema.test_sections_carry_the_contracts":
        ([], "functional", "schema content"),
    "test_stage2_sabotage.TestStage2Sabotages.test_malformed_canonical_bodies_controlled_refusal":
        (["s2.sole_issuer"], "guard", "asserts the unissued detail exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_mixed_genuine_and_forged_entries_refused":
        (["s2.sole_issuer"], "guard", "asserts the unissued detail exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_a_direct_assignment_refused":
        (["s2.close_fieldset"], "guard", "only_artefact facet"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_b_fixtures_total_renamed_refused":
        (["s2.close_schema"], "guard", "missing + not_schema facets, asserted exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_c_dropped_entry_field_retained_refused":
        (["s2.close_fieldset"], "guard", "only_artefact + missing_e facets"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_d_extra_entry_outside_schema_refused":
        (["s2.close_schema"], "guard", "not_schema facets"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_e_canonical_path_bypassed_refused":
        (["s2.close_schema"], "guard",
         "foreign-type entries are not provenance; refusal lands on the "
         "absent-from-both facet"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_f_field_absent_from_both_refused":
        (["s2.close_schema"], "guard", "missing facet"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_g_forged_canonical_events_refused":
        (["s2.sole_issuer"], "guard", "asserts the unissued detail exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_h_companion_deleted_middle_event_refused":
        (["s2.chain_in_verify"], "guard", "asserts the chain-failure detail exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_sabotage_h_tampered_body_retained_digest_refused":
        (["s2.chain_in_verify"], "guard", "asserts the chain-failure detail exactly"),
    "test_stage2_sabotage.TestStage2Sabotages.test_value_mismatch_refused":
        (["s2.close_value"], "guard", ""),
    # ---------------- Stage 3 ----------------
    "test_access_admission.TestAccessAdmission.test_capture_admitted_and_output_may_depend_on_it":
        ([], "control", ""),
    "test_access_admission.TestAccessAdmission.test_consume_issues_receipt_with_frozen_values":
        ([], "functional", "consume happy path"),
    "test_access_admission.TestAccessAdmission.test_consume_unknown_governed_value_refused":
        (["s3.consume_unknown"], "guard", ""),
    "test_access_admission.TestAccessAdmission.test_output_admitted_on_positive_consumption_proof":
        ([], "control", ""),
    "test_access_admission.TestAccessAdmission.test_output_with_fabricated_receipt_refused":
        (["s3.receipt_record_presence", "s3.receipt_facts"], "joint-guard",
         "a fabricated receipt is refused at the recorded-event lookup; "
         "presence is the first gate, facts the joint claim"),
    "test_access_admission.TestAccessAdmission.test_output_without_any_receipt_refused":
        (["s3.receipt_record_presence"], "guard", ""),
    "test_access_admission.TestAccessAdmission.test_quoted_digest_checked_against_the_frozen_object":
        (["s3.output_digest"], "guard", ""),
    "test_access_admission.TestAccessAdmission.test_receipt_for_another_invocation_does_not_admit":
        (["s3.receipt_binding"], "guard", "invocation facet"),
    "test_access_admission.TestAccessAdmission.test_receipt_must_cover_every_value_used":
        (["s3.receipt_coverage"], "guard", ""),
    "test_freeze.TestFreeze.test_derivation_that_does_not_recompute_refused":
        (["s3.policy_recompute"], "guard", ""),
    "test_freeze.TestFreeze.test_derived_limit_below_requirement_refused":
        (["s3.policy_recompute"], "guard", ""),
    "test_freeze.TestFreeze.test_derived_limit_without_derivation_refused":
        (["s3.policy_recompute"], "guard", ""),
    "test_freeze.TestFreeze.test_freeze_on_corrupted_record_writes_nothing":
        (["s3.chain_facet"], "guard", ""),
    "test_freeze.TestFreeze.test_recorded_constant_limit_passes_policy_check":
        ([], "control", "a recorded constant satisfies the policy without recompute"),
    "test_freeze.TestFreeze.test_refused_freeze_is_a_governance_record_not_a_start":
        ([], "functional", "refused freeze is recorded as governance, not a start"),
    "test_freeze.TestFreeze.test_successful_freeze_binds_the_three_identities":
        ([], "functional", "freeze binds config, subject and tree identities"),
    "test_stage3_sabotage.TestSabotageA.test_contradictory_driver_adapter_configurations":
        (["s3.freeze_surface"], "guard", ""),
    "test_stage3_sabotage.TestSabotageB.test_fabricated_receipt_quoting_canonical_hash":
        (["s3.receipt_record_presence", "s3.receipt_facts"], "joint-guard",
         "asserts the receipt_not_issued detail; presence is the first gate"),
    "test_stage3_sabotage.TestSabotageB.test_quoting_canonical_hash_while_using_private_value":
        (["s3.output_differing"], "guard", "the quote is correct; the used value differs"),
    "test_stage3_sabotage.TestSabotageC.test_capture_gate_has_no_identity_to_borrow":
        ([], "functional", "API-shape fixture: admit_capture's signature "
         "carries no identity parameter"),
    "test_stage3_sabotage.TestSabotageC.test_capture_routed_to_another_model_invalidates_run":
        (["s3.capture_subject"], "guard", ""),
    "test_stage3_sabotage.TestSabotageC.test_refuse_capture_policy_scopes_the_refusal":
        (["s3.capture_subject"], "guard", "the subject check under the REFUSE_CAPTURE policy"),
    "test_stage3_sabotage.TestSabotageD.test_served_identity_differing_from_the_pin":
        (["s3.freeze_served_pin"], "guard", ""),
    "test_stage3_sabotage.TestSabotageE.test_gate_honours_recorded_event_not_the_live_object":
        (["s3.receipt_facts"], "guard", ""),
    "test_stage3_sabotage.TestSabotageE.test_post_issuance_receipt_mutation_gains_no_coverage":
        (["s3.receipt_facts", "s3.receipt_coverage"], "joint-guard",
         "the mutated live object is judged against the recorded event: "
         "its facts and its coverage"),
    "test_stage3_sabotage.TestSabotageF.test_frozen_run_cannot_be_rebound":
        (["s3.frozenrun_seal"], "guard", ""),
    "test_stage3_sabotage.TestSabotageG.test_capture_gate_on_body_edited_record_writes_nothing":
        (["s3.chain_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageG.test_output_admission_on_body_edited_record_writes_nothing":
        (["s3.chain_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageG.test_output_admission_on_deleted_event_record_writes_nothing":
        (["s3.chain_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageH.test_consume_on_body_edited_record_issues_nothing":
        (["s3.chain_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_capture_gate_on_emptied_record_refuses_before_lane_call":
        (["s3.terminal_facet"], "guard", "an emptied record's chain recomputes; "
         "the terminal binding is the discriminator"),
    "test_stage3_sabotage.TestSabotageI.test_capture_gate_on_tail_truncated_record_refuses_before_lane_call":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_consume_on_emptied_record_issues_nothing":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_consume_on_tail_truncated_record_issues_nothing":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_freeze_on_emptied_record_refuses_and_writes_nothing":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_freeze_on_tail_truncated_record_refuses_and_writes_nothing":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_output_admission_on_emptied_record_writes_nothing":
        (["s3.terminal_facet"], "guard", ""),
    "test_stage3_sabotage.TestSabotageI.test_output_admission_on_tail_truncated_record_writes_nothing":
        (["s3.terminal_facet"], "guard", ""),
    # ---------------- Stage 4 ----------------
    "test_dispatch.TestProcedureBinding.test_declared_identity_is_the_executed_callable":
        (["s4.construction_binding"], "guard", ""),
    "test_dispatch.TestProcedureBinding.test_fictitious_procedure_identity_rejected_at_construction":
        (["s4.construction_validation"], "guard", ""),
    "test_dispatch.TestProcedureBinding.test_reproducible_result":
        ([], "functional", "run reproducibility"),
    "test_dispatch.TestRegistryAttacks.test_module_registry_rebinding_does_not_redirect_dispatch":
        (["s4.construction_binding"], "guard", "FX-R60i's fixture"),
    "test_dispatch.TestRegistryAttacks.test_registry_remapping_refused_and_dispatch_unchanged":
        (["s4.registry_immutable"], "guard", "FX-R60h's fixture"),
    "test_dispatch.TestRunPaths.test_corrupt_artefact_takes_failure_path":
        (["s4.digest_comparison"], "guard",
         "Stage 4 presents this as a preservation-comparison "
         "fixture; the matrix records whether the comparison is "
         "actually reached (the corrupt flag is checked before "
         "the comparison in preservation_check)"),
    "test_dispatch.TestRunPaths.test_missing_artefact_takes_failure_path":
        ([], "functional", "missing artefact handling in the procedure"),
    "test_dispatch.TestRunPaths.test_unpinned_contract_refuses_to_run":
        (["s4.run_pin"], "guard", ""),
    "test_dispatch.TestRunPaths.test_verdict_records_the_pinned_version":
        ([], "functional", "verdict carries the pinned version"),
    "test_dispatch.TestRunPaths.test_wrong_digest_no_corrupt_flag_takes_failure_path":
        (["s4.digest_comparison"], "guard",
         "the DR-08 successor fixture (FX-R60f's shape): wrong digest, no "
         "corrupt flag, through run() — the comparison itself is reached"),
    "test_dispatch.TestRunPaths.test_wrong_input_artefact_refused":
        (["s4.run_input_identity"], "guard", ""),
    "test_exam_dr24_replay.TestDR24OriginalReplayExecuted.test_cross_contract_replay_accepted_by_v23":
        ([], "exam-evidence",
         "executes the historical v2.3 artefact and demonstrates DR-24 "
         "reproduces; evidence about the ancestor, not a Stage 4 guard"),
    "test_exam_dr24_replay.TestV23EvidencePin.test_evidence_file_matches_the_pinned_v23_digest":
        ([], "functional", "the recovered v2.3 evidence file matches its pin"),
    "test_exam_fx_r60i_restored_global_dispatch.TestFXR60iRestoredGlobalDispatchSabotage.test_restoring_global_dispatch_fails_fx_r60i":
        (["s4.construction_binding", "s4.pinned_hash"], "exam",
         "its own sabotage restores global dispatch (construction binding) "
         "and self-referential validation (pinned hash) together"),
    "test_exam_fx_r60k_identity_sabotage.TestFXR60kIdentitySabotage.test_removing_object_identity_fails_fx_r60k":
        (["s4.identity_check"], "exam",
         "its own sabotage replaces the identity check with content matching"),
    "test_exam_fx_r60l_reconfirmation.TestFXR60lReconfirmation.test_removing_fingerprint_check_fails_fx_r60l_alone":
        (["s4.fingerprint_check"], "exam",
         "its own sabotage removes the fingerprint comparison"),
    "test_instance_binding.TestSealedInstanceBinding.test_healthy_control_canonical_execution_and_validation":
        ([], "control", ""),
    "test_instance_binding.TestSealedInstanceBinding.test_rebinding_instance_procedure_refused":
        (["s4.seal"], "guard", ""),
    "test_verdict_issuance.TestCrossContractReplay.test_a_verdict_rejected_by_b_different_digests":
        (["s4.contract_identity"], "guard",
         "the matrix's verdict, after two classification attempts: "
         "the verdict object IS A's issued object (the verdict "
         "conjunct passes trivially), its contents fingerprint-match "
         "A's entry, its input IDENTITY matches B (only the payload "
         "digest differs, and no field check compares that), and "
         "the pinned hash is genuine for both — the sole load-"
         "bearing check is the K7 lookup's CONTRACT conjunct: no "
         "issuance entry issued BY B matches. Stage 4 presented "
         "this fixture under identity/pinned-hash; the contract "
         "conjunct is the facet that discriminates it"),
    "test_verdict_issuance.TestCrossContractReplay.test_a_verdict_rejected_by_b_identical_contents":
        (["s4.identity_check", "s4.contract_identity"], "guard",
         "FX-R60k's fixture: contents identical. It fails under "
         "EITHER conjunct's neutralisation, by different routes — "
         "verdict conjunct off: the lookup finds B's own entry and "
         "the identical contents fingerprint-match it; contract "
         "conjunct off: the lookup finds A's entry, whose "
         "fingerprint also matches"),
    "test_verdict_issuance.TestCrossContractReplay.test_byte_identical_copy_rejected":
        (["s4.identity_check"], "guard", "FX-R60k's fixture"),
    "test_verdict_issuance.TestCrossContractReplay.test_same_contract_control_accepted":
        ([], "control", ""),
    "test_verdict_issuance.TestFieldChecks.test_altered_implementation_hash_rejected":
        (["s4.pinned_hash"], "guard", "the hash VALUE comparison is the pinned-hash facet"),
    "test_verdict_issuance.TestFieldChecks.test_input_identity_mismatch_rejected":
        (["s4.field_checks"], "guard", "input facet"),
    "test_verdict_issuance.TestFieldChecks.test_missing_implementation_hash_rejected":
        (["s4.field_checks"], "guard", "hash presence facet"),
    "test_verdict_issuance.TestFieldChecks.test_missing_input_identity_rejected":
        (["s4.field_checks"], "guard", "input presence facet"),
    "test_verdict_issuance.TestFieldChecks.test_missing_version_rejected":
        (["s4.field_checks"], "guard", "version presence facet"),
    "test_verdict_issuance.TestFieldChecks.test_not_a_verdict_rejected":
        (["s4.field_checks"], "guard", "shape facet"),
    "test_verdict_issuance.TestFieldChecks.test_procedure_mismatch_rejected":
        (["s4.field_checks"], "guard", "procedure facet"),
    "test_verdict_issuance.TestFieldChecks.test_version_mismatch_rejected":
        (["s4.field_checks"], "guard", "version facet"),
    "test_verdict_issuance.TestGenuineAndForged.test_forged_verdict_with_genuine_pinned_hash_rejected":
        (["s4.identity_check"], "guard",
         "the forgery carries the genuine pinned hash; only issuance "
         "identity rejects it"),
    "test_verdict_issuance.TestGenuineAndForged.test_forgery_offered_against_failure_path_artefact_rejected":
        (["s4.identity_check"], "guard", ""),
    "test_verdict_issuance.TestGenuineAndForged.test_genuine_verdict_accepted_by_its_issuer":
        ([], "control", ""),
    "test_verdict_issuance.TestIssuanceIntegrity.test_mutated_issued_object_rejected":
        (["s4.fingerprint_check"], "guard", "FX-R60l's fixture: the object "
         "is the issued one; its changed fingerprint rejects it"),
    "test_verdict_issuance.TestIssuanceIntegrity.test_mutated_issued_object_rejection_reason":
        (["s4.fingerprint_check"], "guard", "FX-R60l's reason fixture"),
    "test_verdict_issuance.TestIssuanceIntegrity.test_mutated_then_restored_exactly_accepted":
        ([], "control", "restored exactly, the fingerprint matches again"),
    # ---------------- Stage 5 ----------------
    "test_insertion.TestApplication.test_fresh_presentation_applies_once":
        ([], "functional", "first presentation applies the effect once"),
    "test_insertion.TestApplication.test_unconsumed_operation_is_not_falsely_refused":
        ([], "functional", "an unconsumed operation is not refused"),
    "test_insertion.TestDivergence.test_consumed_event_citing_another_operations_applied":
        (["s5.completed_state"], "guard", "cited-applied facet"),
    "test_insertion.TestDivergence.test_consumed_event_without_applied_event_is_not_accepted":
        (["s5.completed_state"], "guard", "cited-applied facet"),
    "test_insertion.TestDivergence.test_consumed_operation_with_missing_effect_is_surfaced":
        (["s5.completed_state"], "guard", "effect-still-present facet"),
    "test_insertion.TestDivergence.test_recorded_insertion_with_missing_effect_is_surfaced":
        (["s5.applied_effect_divergence"], "guard", ""),
    "test_insertion.TestPayloadBinding.test_changed_payload_in_the_crash_window_is_refused":
        (["s5.payload_binding"], "guard", ""),
    "test_insertion.TestPayloadBinding.test_changed_payload_under_consumed_identity_is_refused":
        (["s5.payload_binding"], "guard", ""),
    "test_insertion.TestRePresentation.test_consumed_operation_is_already_satisfied":
        (["s5.event_recognition"], "guard",
         "asserts the recorded consumption event is cited — recognition "
         "from the record, not the effect path"),
    "test_insertion.TestRePresentation.test_recognition_is_per_identity":
        (["s5.identity_function"], "guard",
         "the un-presented operation must read UNCONSUMED: what "
         "separates the two operations is their identities. (The "
         "(None, None) event-recognition neutralisation cannot "
         "move it — the expected state is the null state either "
         "way; the slot-dropping identity sabotage does move it, "
         "as the matrix's collateral record first showed)"),
    "test_insertion.TestRePresentation.test_reconstructed_operation_is_recognised_not_new":
        ([], "functional",
         "DR-01's end-to-end demonstration; its discriminating sabotage "
         "would be a non-canonical identity mint, which no matrix "
         "mechanism performs — named as a sabotage-shape gap"),
    "test_insertion.TestRecordDiscipline.test_emptied_record_refuses_by_terminal_binding":
        (["s3.terminal_facet"], "guard", "shared Stage 3 binder facet"),
    "test_insertion.TestRecordDiscipline.test_tampered_record_refuses_and_writes_nothing":
        (["s3.chain_facet"], "guard", "shared Stage 3 binder facet"),
    "test_operations.TestCanonicalIdentity.test_identity_does_not_depend_on_payload":
        (["s5.identity_payload"], "guard",
         "discriminated by the payload-included sabotage variant, not by "
         "the slot-dropped variant of the identity function"),
    "test_operations.TestCanonicalIdentity.test_identity_is_a_function_of_the_triple":
        (["s5.identity_determinism"], "guard",
         "determinism half of the identity function; discriminated by "
         "the non-deterministic sabotage variant"),
    "test_operations.TestCanonicalIdentity.test_identity_parts_all_bind":
        (["s5.identity_function"], "guard", "each triple part varied in turn"),
    "test_operations.TestOperationImmutability.test_attributes_cannot_be_rebound":
        (["s5.operation_seal"], "guard", ""),
    "test_operations.TestOperationImmutability.test_payload_cannot_be_mutated_through_the_copy":
        (["s5.payload_copy"], "guard", ""),
    "test_operations.TestOperationImmutability.test_payload_digest_is_canonical":
        ([], "functional", "payload digest canonicality"),
    "test_operations.TestPureConstruction.test_build_touches_no_state":
        ([], "functional", "purity: build reads/writes no state"),
    "test_operations.TestPureConstruction.test_reconstruction_after_consumption_is_the_same_operation":
        ([], "functional", "reconstruction equality (identity + payload)"),
    "test_operations.TestPureConstruction.test_repeated_builds_are_equal":
        ([], "functional", "purity: repeated builds equal"),
    "test_recovery.TestInterruptionBetweenInsertionAndRecording.test_crash_after_applied_event_before_consumption":
        (["s5.effect_recognition"], "guard", ""),
    "test_recovery.TestInterruptionBetweenInsertionAndRecording.test_crash_after_effect_before_any_recording":
        (["s5.effect_recognition"], "guard", ""),
    "test_recovery.TestPartialInsertion.test_interruption_mid_insertion_then_retry":
        ([], "functional",
         "the crash lands DURING the effect write: the insertion "
         "never landed (orphan temp only), so the retry is a fresh "
         "application — the effect-recognition branch is not what "
         "this fixture exercises (classification corrected on a "
         "first-hand reading)"),
    "test_recovery.TestRestartRecognition.test_consumed_missing_effect_diverges_after_restart":
        (["s5.completed_state"], "guard", "after an actual process restart"),
    "test_recovery.TestRestartRecognition.test_consumed_operation_recognised_after_restart":
        (["s5.event_recognition"], "guard",
         "recognition rebuilt from the record alone in a new process"),
    "test_recovery.TestRestartRecognition.test_partial_insertion_recovered_by_new_process":
        ([], "functional",
         "the same never-landed shape, recovered by a new process: "
         "a fresh application, not an effect recognition"),
    "test_recovery.TestRestartRecognition.test_retry_after_crash_and_restart":
        (["s5.effect_recognition"], "guard", ""),
    "test_recovery.TestRestartRecognition.test_unconsumed_operation_applies_after_restart":
        ([], "functional", "an unconsumed operation still applies after restart"),
    # ---------------- Stage 6 ----------------
    "test_attribution.TestLabelConversionRefused.test_every_conversion_attempt_raises":
        (["s6.label_conversion"], "guard", ""),
    "test_attribution.TestLabelConversionRefused.test_label_preserved_as_local_not_attribution":
        (["s6.label_conversion"], "guard", ""),
    "test_attribution.TestOneFailureOneRecord.test_class_outside_vocabulary_refused":
        (["s6.vocabulary"], "guard", ""),
    "test_attribution.TestOneFailureOneRecord.test_no_attribution_yet_reads_as_none":
        ([], "functional", "absence reads as None"),
    "test_attribution.TestOneFailureOneRecord.test_second_mint_for_one_failure_refused":
        (["s6.one_record"], "guard", ""),
    "test_attribution.TestOneFailureOneRecord.test_three_surfaces_reference_the_same_record":
        ([], "functional", "closure/ledger/adjudication views reference one record"),
    "test_attribution.TestOneFailureOneRecord.test_views_read_the_fact_back_from_disk":
        ([], "functional", "views re-read from disk"),
    "test_attribution.TestPinnedAuthority.test_genuine_record_issues":
        ([], "control", ""),
    "test_attribution.TestPinnedAuthority.test_ledger_requires_the_issued_capability":
        (["s6.point_of_use"], "guard", ""),
    "test_attribution.TestPinnedAuthority.test_mutated_genuine_record_refused":
        (["s6.issuance_record_check"], "guard", ""),
    "test_attribution.TestPinnedAuthority.test_self_appointed_record_refused":
        (["s6.issuance_record_check"], "guard", ""),
    "test_attribution.TestRecordDiscipline.test_tampered_record_refuses_and_stays_byte_identical":
        (["s3.chain_facet"], "guard", "shared Stage 3 binder facet"),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_capability_swapped_onto_ledger_cannot_mint":
        (["s6.point_of_use"], "guard", ""),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_direct_construction_from_genuine_record_refused":
        (["s6.issuance_token"], "guard", ""),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_direct_construction_from_impostor_record_refused":
        (["s6.issuance_token"], "guard", ""),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_cannot_mint_attribution":
        (["s6.issuance_token", "s6.point_of_use"], "joint-guard",
         "a forged capability is stopped at construction or at point of "
         "use, whichever it reaches"),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_cannot_resolve_discrepancy":
        (["s6.issuance_token", "s6.point_of_use"], "joint-guard", ""),
    "test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_carrying_the_pinned_digest_cannot_mint":
        (["s6.issuance_token", "s6.point_of_use"], "joint-guard", ""),
    "test_correction_round_1.TestDiscrepancyLinkMustResolve.test_healthy_link_still_mints_and_reads_back":
        ([], "control", ""),
    "test_correction_round_1.TestDiscrepancyLinkMustResolve.test_nonexistent_attribution_digest_refused":
        (["s6.resolve_attribution"], "guard", ""),
    "test_correction_round_1.TestDiscrepancyLinkMustResolve.test_readback_refuses_an_unresolvable_link":
        (["s6.resolve_attribution"], "guard", ""),
    "test_correction_round_1.TestDiscrepancyLinkMustResolve.test_wrong_type_attribution_digest_refused":
        (["s6.resolve_attribution"], "guard", ""),
    "test_discrepancy.TestAuthorisedResolution.test_authorised_resolution_records_decision_and_authority":
        ([], "functional", "resolution happy path"),
    "test_discrepancy.TestAuthorisedResolution.test_resolution_without_authority_refused":
        (["s6.point_of_use"], "guard", ""),
    "test_discrepancy.TestAuthorisedResolution.test_second_resolution_refused":
        (["s6.one_resolution"], "guard", ""),
    "test_discrepancy.TestBothPositionsPreserved.test_positions_verbatim_and_state_unresolved":
        ([], "functional", "both positions preserved verbatim"),
    "test_discrepancy.TestBothPositionsPreserved.test_the_original_attribution_is_not_changed":
        ([], "functional", "resolution does not rewrite the attribution"),
    "test_discrepancy.TestIndeterminate.test_indeterminate_is_terminal_for_the_disagreement_only":
        ([], "functional", "indeterminate terminality, attribution untouched"),
    "test_examiner_g6.TestReportResolution.test_conflict_becomes_a_discrepancy_preserving_both":
        ([], "functional", "report conflict becomes a discrepancy"),
    "test_examiner_g6.TestReportResolution.test_contradictory_literals_flagged_by_name":
        (["s6.g6_contradiction"], "guard", ""),
    "test_examiner_g6.TestReportResolution.test_correct_literals_pass":
        ([], "control", ""),
    "test_examiner_g6.TestReportResolution.test_flagged_not_corrected":
        ([], "functional",
         "asserts the resolved entry preserves the literal and "
         "carries the rendered location — resolution-entry "
         "construction; the flag facet itself is discriminated "
         "by its sibling, test_contradictory_literals_flagged_by_name"),
    "test_examiner_g6.TestReportResolution.test_unresolvable_reference_is_an_error_not_a_flag":
        (["s6.g6_resolution"], "guard", ""),
    "test_reproductions.TestEvidencePins.test_executed_stack_matches_the_records_own_pins":
        ([], "functional", "the executed stack matches the preserved record's pins"),
    "test_reproductions.TestFindingsBecomeAttributions.test_t02_finding_recorded_and_attributed":
        (["s6.format_prescribed"], "reproduction",
         "T02's finding becomes a SYSTEM attribution on the "
         "format-not-prescribed fact"),
    "test_reproductions.TestT02.test_attribution":
        (["s6.format_prescribed"], "reproduction", ""),
    "test_reproductions.TestT02.test_transcription_reproduces_the_record":
        ([], "reproduction", "transcription of preserved attempt-3 evidence"),
    "test_reproductions.TestT07.test_attribution":
        (["s6.format_prescribed"], "reproduction", ""),
    "test_reproductions.TestT07.test_transcription_reproduces_the_record":
        ([], "reproduction", "transcription of preserved attempt-3 evidence"),
    "test_reproductions.TestT09.test_attributions":
        (["s6.format_prescribed"], "reproduction", ""),
    "test_reproductions.TestT09.test_transcriptions_reproduce_the_record":
        ([], "reproduction", "transcription of preserved attempt-3 evidence"),
    "test_schema_contract.TestCausalTableControls.test_agreement":
        (["s6.extraction"], "guard",
         "the agreement branch returns on extraction equality BEFORE "
         "format_prescribed or any lines matching is consulted; the "
         "regex extraction is its mechanism"),
    "test_schema_contract.TestCausalTableControls.test_checker_defect_on_compliant_response":
        (["s6.format_prescribed_false"], "guard",
         "prescribed is genuinely True here, so only the "
         "opposite-direction sabotage (reported never prescribed) "
         "can move this branch"),
    "test_schema_contract.TestCausalTableControls.test_input_branch":
        (["s6.input_defect_branch"], "guard",
         "examine()'s input-defect branch returns before any "
         "extraction fact is read"),
    "test_schema_contract.TestCausalTableControls.test_model_branch":
        (["s6.format_prescribed_false"], "guard",
         "the branch is VALUE_NOT_STATED_AS_PRESCRIBED: extraction "
         "yields nothing, the value is not stated, and prescribed is "
         "genuinely True — only the opposite-direction sabotage "
         "moves it (the lines-matching facet never executes for "
         "this regex contract)"),
    "test_schema_contract.TestCausalTableControls.test_unknown_branch":
        (["s6.format_prescribed"], "guard",
         "prescribed is genuinely False; forcing it True moves the "
         "branch to MODEL — the single-direction sabotage suffices"),
    "test_schema_contract.TestChangedUnderUnchanged.test_checker_changed_schema_unchanged":
        (["s6.schema_binding"], "guard", ""),
    "test_schema_contract.TestChangedUnderUnchanged.test_checker_rebound_to_another_schema":
        (["s6.schema_binding"], "guard", ""),
    "test_schema_contract.TestChangedUnderUnchanged.test_schema_changed_checker_unchanged":
        (["s6.schema_binding"], "guard", ""),
    "test_schema_contract.TestFindingIsRecorded.test_finding_event_on_the_record":
        ([], "functional", "the finding is recorded as an event"),
    "test_schema_contract.TestPinnedSchemaArtefact.test_checker_binding_comes_from_the_frozen_object":
        (["s6.schema_binding"], "guard", ""),
    "test_schema_contract.TestPinnedSchemaArtefact.test_delivered_instruction_is_preserved_in_full":
        ([], "functional", "instruction preservation"),
    "test_schema_contract.TestPinnedSchemaArtefact.test_one_identity_over_both_sections":
        ([], "functional", "one identity over schema + contract sections"),
    "test_schema_contract.TestPinnedSchemaArtefact.test_schema_and_contract_are_sealed":
        (["s6.schema_seal"], "guard", ""),
    # ---------------- Stage 7 ----------------
    "test_anchor_provenance.TestDirectConstructionRefused.test_direct_construction_from_attacker_values_refused":
        (["s7.pin_constructor"], "guard", ""),
    "test_anchor_provenance.TestDirectConstructionRefused.test_direct_construction_from_genuine_values_refused":
        (["s7.pin_constructor"], "guard", "the path is verified, not the values"),
    "test_anchor_provenance.TestHealthyControl.test_genuine_anchor_verifies_and_closes_complete":
        ([], "control", ""),
    "test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_gap_survives_under_the_genuine_pin":
        ([], "functional", "after refused substitutions, genuine accounting "
         "keeps the exact gap"),
    "test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_append_and_writes_nothing":
        (["s7.pin_point_of_use"], "guard", ""),
    "test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_closure_and_writes_nothing":
        (["s7.pin_point_of_use"], "guard", ""),
    "test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_receipt_account":
        (["s7.pin_point_of_use"], "guard", ""),
    "test_anchor_provenance.TestSubstitutionAtLifecycle.test_attack_is_coherent_under_attacker_anchor":
        ([], "functional", "attack-coherence precondition: the forged "
         "anchor genuinely authenticates the attacker tag, shown before "
         "any refusal is asserted"),
    "test_anchor_provenance.TestSubstitutionAtLifecycle.test_substituted_anchor_refused_at_lifecycle_state":
        (["s7.pin_point_of_use"], "guard", ""),
    "test_anchor_provenance.TestSubstitutionAtLifecycle.test_true_state_under_the_genuine_pin":
        (["s7.authentication"], "guard",
         "the same receipt under the genuine pin lands COLLECTED_UNAUTHENTICATED"),
    "test_anchor_provenance.TestSubstitutionAtLifecycle.test_value_identical_forgery_refused":
        (["s7.pin_point_of_use"], "guard", "values copy the pin; the token does not"),
    "test_closure_account.TestClosureStatesGapsExactly.test_closure_complete_when_every_receipt_verified":
        ([], "control", ""),
    "test_closure_account.TestClosureStatesGapsExactly.test_each_deficient_state_named_as_its_exact_gap":
        (["s7.authentication", "s7.digest_comparison", "s7.package_lookup"],
         "joint-guard",
         "one receipt per deficient state; each state's guard must hold "
         "for its gap line to be the exact one"),
    "test_closure_account.TestDR04Shape.test_dr04_receipts_stated_as_not_collected":
        (["s7.package_lookup"], "guard", "DR-04's shape: issued, content "
         "never collected — the read_content absence point"),
    "test_closure_account.TestUnrecordedEntries.test_unrecorded_package_entry_named_as_a_gap":
        (["s7.unrecorded_accounting"], "guard", ""),
    "test_lifecycle.TestDigestMismatch.test_content_mismatching_digest":
        (["s7.digest_comparison"], "guard", ""),
    "test_lifecycle.TestFullLifecycle.test_full_lifecycle_verified":
        ([], "control", ""),
    "test_lifecycle.TestFullLifecycle.test_issuance_never_satisfies_collection_or_verification":
        (["s7.package_lookup"], "guard", "issuance alone reads as not collected"),
    "test_lifecycle.TestIssuanceAndCollectionRules.test_collect_unissued_refused":
        (["s7.collect_issuance"], "guard", ""),
    "test_lifecycle.TestIssuanceAndCollectionRules.test_reissue_same_commitment_refused":
        (["s7.issue_once"], "guard", ""),
    "test_lifecycle.TestIssuanceAndCollectionRules.test_second_collection_refused":
        (["s7.collect_once"], "guard", ""),
    "test_lifecycle.TestIssuanceAndCollectionRules.test_unrecorded_package_entry_is_not_a_lifecycle_state":
        (["s7.issuance_lookup"], "guard", ""),
    "test_lifecycle.TestIssuedWithoutContent.test_issued_without_content":
        (["s7.package_lookup"], "guard", ""),
    "test_lifecycle.TestRemovedFromPackage.test_removed_after_collection":
        (["s7.package_lookup"], "guard", "the read_entry absence point"),
    "test_lifecycle.TestRemovedFromPackage.test_removed_after_issuance":
        (["s7.package_lookup"], "guard", "the read_entry absence point"),
    "test_lifecycle.TestStatesDistinct.test_all_five_states_are_distinct":
        (["s7.authentication", "s7.digest_comparison", "s7.package_lookup"],
         "joint-guard", "the five states told apart in one run"),
    "test_lifecycle.TestUnauthenticated.test_issued_under_other_terms_does_not_authenticate":
        (["s7.authentication"], "guard", ""),
    "test_lifecycle.TestUnauthenticated.test_package_supplied_anchor_is_not_trusted":
        (["s7.authentication"], "guard",
         "verification proceeds under the genuine pin; the package's "
         "anchor is not consulted"),
    "test_lifecycle.TestUnauthenticated.test_tag_absent":
        (["s7.authentication"], "guard", ""),
    "test_lifecycle.TestUnauthenticated.test_tag_forged_under_attacker_key":
        (["s7.authentication"], "guard", ""),
    "test_record_discipline.TestEmptiedRecord.test_collection_refused_on_emptied_record":
        (["s3.terminal_facet"], "guard", "shared Stage 3 binder facet"),
    "test_record_discipline.TestTamperedRecord.test_account_refused_on_body_edited_record":
        (["s3.chain_facet"], "guard", "shared Stage 3 binder facet"),
    "test_record_discipline.TestTamperedRecord.test_collection_refused_on_body_edited_record":
        (["s3.chain_facet"], "guard", "shared Stage 3 binder facet"),
    "test_record_discipline.TestTamperedRecord.test_issuance_refused_on_body_edited_record":
        (["s3.chain_facet"], "guard", "shared Stage 3 binder facet"),
}


def fixtures():
    """The inventory as a list of fixture records."""
    return [{"fixture_id": test_id, "targets": list(targets),
             "kind": kind, "note": note}
            for test_id, (targets, kind, note)
            in sorted(ENTRIES.items())]


def discover_stage_ids(root: str, stage: int):
    """Test ids discovered in one stage's real tree, via the
    witness runner (the matrix's own witness — discovery and
    matrix outcomes come from the same instrument)."""
    import json
    import os
    import subprocess
    import sys
    runner = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "witness_run.py")
    proc = subprocess.run(
        [sys.executable, runner, os.path.join(root, f"stage{stage}")],
        capture_output=True, text=True, timeout=300)
    ids = []
    for line in proc.stdout.splitlines():
        row = json.loads(line)
        if "test_id" in row:
            ids.append(row["test_id"])
    return ids


def completeness(root: str):
    """(discovered_not_in_inventory, in_inventory_not_discovered,
    stage_by_id). Exact set equality is the completeness claim;
    anything in either difference is a defect of the inventory,
    named, not smoothed."""
    stage_by_id = {}
    for stage in range(1, 8):
        for tid in discover_stage_ids(root, stage):
            stage_by_id[tid] = stage
    discovered = set(stage_by_id)
    inventoried = set(ENTRIES)
    return (sorted(discovered - inventoried),
            sorted(inventoried - discovered),
            stage_by_id)
