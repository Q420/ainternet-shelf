# Duenna Stage 8 — Fixture Inventory (K14)

Every test in Stages 1–7: its fixture identity (the target mechanism path it claims, from a first-hand reading of the suites) and its execution record (the sabotage matrix's verdict, from the witness runner's outcomes — never from the fixture's own account of itself).

Fixtures: 287. Claimed (fixture, mechanism) pairs: 217.

## Stage 1 — 68 fixtures

### `test_anchor.TestAnchor.test_commit_record_head_uses_current_head_values`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: anchor file carries the record's current head values

### `test_anchor.TestAnchor.test_deleted_anchor_after_closure_yields_not_verified`
- kind: guard
- targets: s1.anchor_absence
- execution (s1.anchor_absence): EXERCISED

### `test_anchor.TestAnchor.test_missing_anchor_yields_not_verified`
- kind: guard
- targets: s1.anchor_absence
- execution (s1.anchor_absence): EXERCISED

### `test_anchor.TestAnchor.test_normal_closed_record_verifies`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: healthy closed record verifies end to end

### `test_anchor.TestAnchor.test_unreadable_anchor_yields_not_verified`
- kind: guard
- targets: s1.anchor_absence
- execution (s1.anchor_absence): EXERCISED

### `test_anchor.TestAnchor.test_wholesale_rechained_rewrite_caught_by_anchor_mismatch`
- kind: guard
- targets: s1.anchor_comparison
- execution (s1.anchor_comparison): EXERCISED
- note: the re-chained chain recomputes cleanly; only the anchor comparison catches it

### `test_anchor.TestAnchor.test_write_anchor_takes_only_head_state_values`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: anchor writing takes head state only

### `test_c6_account_schema.TestC6AccountSchema.test_c6_complete_missing_unknowns`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED

### `test_c6_account_schema.TestC6AccountSchema.test_c6_complete_unknowns_wrong_type`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): NOT-EXERCISED

### `test_c6_account_schema.TestC6AccountSchema.test_c6_incomplete_empty_unknowns`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED
- note: INCOMPLETE without unknowns is schema-invalid

### `test_c6_account_schema.TestC6AccountSchema.test_c6_incomplete_missing_unknowns`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED

### `test_c6_account_schema.TestC6AccountSchema.test_c6_missing_account_authority`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED
- note: authority naming nothing is schema-invalid

### `test_c6_account_schema.TestC6AccountSchema.test_c6_missing_failure_entry_authority`
- kind: joint-guard
- targets: s1.account_whole
- execution (s1.account_whole): EXERCISED
- note: the account_invalid branch has no facet mechanism in the matrix; this fixture discriminates _check_account_completeness only as a whole

### `test_c6_account_schema.TestC6AccountSchema.test_c6_unknowns_empty_string_entry`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED

### `test_c6_account_schema.TestC6AccountSchema.test_c6_unknowns_non_string_entry`
- kind: guard
- targets: s1.account_schema
- execution (s1.account_schema): EXERCISED

### `test_c6_account_schema.TestC6AccountSchema.test_c6_wellformed_complete_still_passes`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_c6_account_schema.TestC6AccountSchema.test_c6_wellformed_incomplete_still_incomplete`
- kind: guard
- targets: s1.account_status_incomplete
- execution (s1.account_status_incomplete): EXERCISED

### `test_closure.TestClosureRunner.test_clean_path_account_complete_with_empty_failures`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour; no validator facet claimed

### `test_closure.TestClosureRunner.test_closure_states_three_endings_separately`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_closure.TestClosureRunner.test_each_path_yields_exactly_one_closure_as_last_event`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_closure.TestClosureRunner.test_early_stop_account_incomplete_with_unknowns_named`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_closure.TestClosureRunner.test_exception_path_still_closes`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_closure.TestClosureRunner.test_known_failure_account_lists_failure_with_attribution`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_closure.TestClosureRunner.test_known_failure_also_appended_as_failure_event_before_closure`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter behaviour

### `test_record.TestEventRecord.test_append_assigns_sequence_and_chains`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: EventRecord append mechanics

### `test_record.TestEventRecord.test_clean_record_verifies`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: healthy chain verifies; a verify_chain that always answers True also passes it — it is a control, not a guard fixture

### `test_record.TestEventRecord.test_deleted_event_detected`
- kind: guard
- targets: s1.verify_chain
- execution (s1.verify_chain): EXERCISED

### `test_record.TestEventRecord.test_empty_record_verifies`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_record.TestEventRecord.test_record_file_is_append_only_jsonl`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: record file format

### `test_record.TestEventRecord.test_reopen_continues_from_head`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: reopen/head mechanics

### `test_record.TestEventRecord.test_rewritten_middle_event_detected`
- kind: guard
- targets: s1.verify_chain
- execution (s1.verify_chain): EXERCISED

### `test_stage1_cases.TestStage1Cases.test_case1_normal_completion`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_stage1_cases.TestStage1Cases.test_case2_known_failure_accounted_with_attribution`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: closure account of a known failure

### `test_stage1_cases.TestStage1Cases.test_case3_early_stop_closes_with_known_unknown_stated`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: closure states the known unknown

### `test_stage1_cases.TestStage1Cases.test_case4_exception_path_appends_closure`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: exception path closure

### `test_stage1_cases.TestStage1Cases.test_case5_missing_failure_account`
- kind: joint-guard
- targets: s1.account_whole
- execution (s1.account_whole): EXERCISED
- note: the closure body has no account section at all; the refusal lands on the account-presence branch, which has no facet mechanism — this fixture discriminates the account function only as a whole (classification corrected on the matrix's evidence: it does not touch the reconciliation facets)

### `test_stage1_cases.TestStage1Cases.test_case6_missing_attribution_recorded_as_unknown`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: ClosureWriter records UNKNOWN attribution

### `test_stage1_cases.TestStage1Cases.test_case7_rewritten_chain_detected_by_anchor`
- kind: guard
- targets: s1.anchor_comparison
- execution (s1.anchor_comparison): EXERCISED

### `test_stage1_cases.TestStage1Cases.test_case8_anchor_unavailable_not_verified_never_passed`
- kind: guard
- targets: s1.anchor_absence
- execution (s1.anchor_absence): EXERCISED

### `test_stage1_cases.TestStage1Cases.test_case9_omitted_known_failure_fails_account_completeness`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: omitted facet

### `test_validator.TestValidator.test_clean_run_passes_all_three`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_validator.TestValidator.test_complete_declared_with_unknowns_fails_account`
- kind: guard
- targets: s1.account_complete_unknowns
- execution (s1.account_complete_unknowns): EXERCISED

### `test_validator.TestValidator.test_early_stop_account_reported_incomplete_not_pass`
- kind: guard
- targets: s1.account_status_incomplete
- execution (s1.account_status_incomplete): EXERCISED

### `test_validator.TestValidator.test_edited_middle_event_body_fails_chain_validity`
- kind: guard
- targets: s1.verify_chain
- execution (s1.verify_chain): EXERCISED

### `test_validator.TestValidator.test_known_failure_run_passes_all_three`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_validator.TestValidator.test_omitted_failure_fails_account_completeness`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: omitted facet

### `test_validator.TestValidator.test_record_with_no_closure_fails_terminal_record`
- kind: guard
- targets: s1.terminal_check
- execution (s1.terminal_check): EXERCISED

### `test_validator.TestValidator.test_validator_reads_fresh_from_disk`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: freshness: the validator re-reads from disk; no sabotage in the matrix targets read caching

### `test_vane_hardening.TestVaneHardening.test_authority_match_passes`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_vane_hardening.TestVaneHardening.test_authority_mismatch_is_altered`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: altered facet (authority field)

### `test_vane_hardening.TestVaneHardening.test_padded_content_accepted_and_preserved`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: whitespace semantics control: padded content names something under both the settled term and a plain length check

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_account_authority_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_account_description_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_account_failure_id_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_description_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_entry_authority_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_failure_id_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_hardening.TestVaneHardening.test_whitespace_only_unknown_rejected`
- kind: guard
- targets: s1.whitespace
- execution (s1.whitespace): EXERCISED

### `test_vane_sabotage.TestVaneSabotage.test_s1_duplicate_terminal_closure`
- kind: guard
- targets: s1.terminal_check
- execution (s1.terminal_check): EXERCISED

### `test_vane_sabotage.TestVaneSabotage.test_s1b_two_closures_with_event_afterward`
- kind: guard
- targets: s1.terminal_check
- execution (s1.terminal_check): EXERCISED

### `test_vane_sabotage.TestVaneSabotage.test_s1c_closure_followed_by_continuation`
- kind: guard
- targets: s1.terminal_check
- execution (s1.terminal_check): EXERCISED

### `test_vane_sabotage.TestVaneSabotage.test_s2_duplicate_failure_id_in_record`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: duplicate_record facet

### `test_vane_sabotage.TestVaneSabotage.test_s3_duplicate_account_failure_id`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: duplicate_account facet

### `test_vane_sabotage.TestVaneSabotage.test_s4_extra_fabricated_account_failure`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: extra facet

### `test_vane_sabotage.TestVaneSabotage.test_s5_altered_failure_description_or_attribution`
- kind: guard
- targets: s1.account_reconciliation
- execution (s1.account_reconciliation): EXERCISED
- note: altered facet

### `test_vane_sabotage.TestVaneSabotage.test_s6_structurally_malformed_event`
- kind: guard
- targets: s1.structural_validity
- execution (s1.structural_validity): EXERCISED

### `test_vane_sabotage.TestVaneSabotage.test_s7_corrupted_record_reopened_for_append`
- kind: joint-guard
- targets: s1.verify_chain, s1.structural_validity
- execution (s1.structural_validity): JOINT-ONLY
- execution (s1.verify_chain): EXERCISED
- execution (combined): EXERCISED-JOINT
- note: reopen verifies the chain; the corruption is a body edit, so the chain facet is the expected discriminator and structural validity the joint claim

### `test_vane_sabotage.TestVaneSabotage.test_s8_record_and_anchor_both_rewritten_demonstrates_boundary`
- kind: boundary
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: asserts the C3 limitation (a coordinated record+anchor rewrite is not defeated); no guard target; coverage-excluded by kind

## Stage 2 — 27 fixtures

### `test_construction.TestConstruction.test_duplicate_entry_for_one_field_refuses`
- kind: joint-guard
- targets: s2.build_duplicates, s2.close_duplicates
- execution (s2.build_duplicates): JOINT-ONLY
- execution (s2.close_duplicates): JOINT-ONLY
- execution (combined): EXERCISED-JOINT
- note: either duplicate guard alone still refuses with the same duplicate_entries detail; only the conjunction discriminates

### `test_construction.TestConstruction.test_entries_for_other_artefacts_are_not_read`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: issued_entries is per-artefact; no facet claimed

### `test_construction.TestConstruction.test_faithful_artefact_passes_field_for_field`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_construction.TestConstruction.test_fresh_writer_over_existing_record_refuses`
- kind: guard
- targets: s2.sole_issuer
- execution (s2.sole_issuer): EXERCISED
- note: asserts the unissued_provenance_events detail exactly; cited in Stage 2 as whole-verify evidence — for the REGISTRY facet it is not a discriminator (see the registry-completeness finding)

### `test_construction.TestConstruction.test_no_entries_at_all_refuses_and_records_refusal`
- kind: guard
- targets: s2.close_schema
- execution (s2.close_schema): EXERCISED
- note: missing facet (absent from both)

### `test_construction.TestConstruction.test_record_chain_still_verifies_after_construction`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: post-construction chain health (Stage 1 verify_chain)

### `test_construction.TestConstruction.test_unencodable_provenance_value_refused_at_entry`
- kind: guard
- targets: s2.entry_validation
- execution (s2.entry_validation): EXERCISED

### `test_construction.TestConstruction.test_well_formed_artefact_closes`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_schema.TestFrozenSchema.test_digest_is_deterministic`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: schema digest determinism

### `test_schema.TestFrozenSchema.test_duplicate_field_names_refused`
- kind: guard
- targets: s2.schema_validation
- execution (s2.schema_validation): EXERCISED

### `test_schema.TestFrozenSchema.test_either_section_change_changes_the_one_identity`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: schema identity binds both sections

### `test_schema.TestFrozenSchema.test_nameless_field_or_version_refused`
- kind: guard
- targets: s2.schema_validation
- execution (s2.schema_validation): EXERCISED

### `test_schema.TestFrozenSchema.test_schema_is_frozen_after_construction`
- kind: guard
- targets: s2.schema_freeze
- execution (s2.schema_freeze): NOT-EXERCISED

### `test_schema.TestFrozenSchema.test_sections_are_immutable_tuples`
- kind: guard
- targets: s2.schema_tuples
- execution (s2.schema_tuples): EXERCISED

### `test_schema.TestFrozenSchema.test_sections_carry_the_contracts`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: schema content

### `test_stage2_sabotage.TestStage2Sabotages.test_malformed_canonical_bodies_controlled_refusal`
- kind: guard
- targets: s2.sole_issuer
- execution (s2.sole_issuer): EXERCISED
- note: asserts the unissued detail exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_mixed_genuine_and_forged_entries_refused`
- kind: guard
- targets: s2.sole_issuer
- execution (s2.sole_issuer): EXERCISED
- note: asserts the unissued detail exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_a_direct_assignment_refused`
- kind: guard
- targets: s2.close_fieldset
- execution (s2.close_fieldset): EXERCISED
- note: only_artefact facet

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_b_fixtures_total_renamed_refused`
- kind: guard
- targets: s2.close_schema
- execution (s2.close_schema): EXERCISED
- note: missing + not_schema facets, asserted exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_c_dropped_entry_field_retained_refused`
- kind: guard
- targets: s2.close_fieldset
- execution (s2.close_fieldset): EXERCISED
- note: only_artefact + missing_e facets

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_d_extra_entry_outside_schema_refused`
- kind: guard
- targets: s2.close_schema
- execution (s2.close_schema): EXERCISED
- note: not_schema facets

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_e_canonical_path_bypassed_refused`
- kind: guard
- targets: s2.close_schema
- execution (s2.close_schema): EXERCISED
- note: foreign-type entries are not provenance; refusal lands on the absent-from-both facet

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_f_field_absent_from_both_refused`
- kind: guard
- targets: s2.close_schema
- execution (s2.close_schema): EXERCISED
- note: missing facet

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_g_forged_canonical_events_refused`
- kind: guard
- targets: s2.sole_issuer
- execution (s2.sole_issuer): EXERCISED
- note: asserts the unissued detail exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_h_companion_deleted_middle_event_refused`
- kind: guard
- targets: s2.chain_in_verify
- execution (s2.chain_in_verify): EXERCISED
- note: asserts the chain-failure detail exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_sabotage_h_tampered_body_retained_digest_refused`
- kind: guard
- targets: s2.chain_in_verify
- execution (s2.chain_in_verify): EXERCISED
- note: asserts the chain-failure detail exactly

### `test_stage2_sabotage.TestStage2Sabotages.test_value_mismatch_refused`
- kind: guard
- targets: s2.close_value
- execution (s2.close_value): EXERCISED

## Stage 3 — 38 fixtures

### `test_access_admission.TestAccessAdmission.test_capture_admitted_and_output_may_depend_on_it`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_access_admission.TestAccessAdmission.test_consume_issues_receipt_with_frozen_values`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: consume happy path

### `test_access_admission.TestAccessAdmission.test_consume_unknown_governed_value_refused`
- kind: guard
- targets: s3.consume_unknown
- execution (s3.consume_unknown): EXERCISED

### `test_access_admission.TestAccessAdmission.test_output_admitted_on_positive_consumption_proof`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_access_admission.TestAccessAdmission.test_output_with_fabricated_receipt_refused`
- kind: joint-guard
- targets: s3.receipt_record_presence, s3.receipt_facts
- execution (s3.receipt_facts): NOT-EXERCISED
- execution (s3.receipt_record_presence): NOT-EXERCISED
- execution (combined): NOT-EXERCISED
- note: a fabricated receipt is refused at the recorded-event lookup; presence is the first gate, facts the joint claim

### `test_access_admission.TestAccessAdmission.test_output_without_any_receipt_refused`
- kind: guard
- targets: s3.receipt_record_presence
- execution (s3.receipt_record_presence): NOT-EXERCISED

### `test_access_admission.TestAccessAdmission.test_quoted_digest_checked_against_the_frozen_object`
- kind: guard
- targets: s3.output_digest
- execution (s3.output_digest): EXERCISED

### `test_access_admission.TestAccessAdmission.test_receipt_for_another_invocation_does_not_admit`
- kind: guard
- targets: s3.receipt_binding
- execution (s3.receipt_binding): EXERCISED
- note: invocation facet

### `test_access_admission.TestAccessAdmission.test_receipt_must_cover_every_value_used`
- kind: guard
- targets: s3.receipt_coverage
- execution (s3.receipt_coverage): EXERCISED

### `test_freeze.TestFreeze.test_derivation_that_does_not_recompute_refused`
- kind: guard
- targets: s3.policy_recompute
- execution (s3.policy_recompute): EXERCISED

### `test_freeze.TestFreeze.test_derived_limit_below_requirement_refused`
- kind: guard
- targets: s3.policy_recompute
- execution (s3.policy_recompute): EXERCISED

### `test_freeze.TestFreeze.test_derived_limit_without_derivation_refused`
- kind: guard
- targets: s3.policy_recompute
- execution (s3.policy_recompute): EXERCISED

### `test_freeze.TestFreeze.test_freeze_on_corrupted_record_writes_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED

### `test_freeze.TestFreeze.test_recorded_constant_limit_passes_policy_check`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: a recorded constant satisfies the policy without recompute

### `test_freeze.TestFreeze.test_refused_freeze_is_a_governance_record_not_a_start`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: refused freeze is recorded as governance, not a start

### `test_freeze.TestFreeze.test_successful_freeze_binds_the_three_identities`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: freeze binds config, subject and tree identities

### `test_stage3_sabotage.TestSabotageA.test_contradictory_driver_adapter_configurations`
- kind: guard
- targets: s3.freeze_surface
- execution (s3.freeze_surface): EXERCISED

### `test_stage3_sabotage.TestSabotageB.test_fabricated_receipt_quoting_canonical_hash`
- kind: joint-guard
- targets: s3.receipt_record_presence, s3.receipt_facts
- execution (s3.receipt_facts): NOT-EXERCISED
- execution (s3.receipt_record_presence): NOT-EXERCISED
- execution (combined): NOT-EXERCISED
- note: asserts the receipt_not_issued detail; presence is the first gate

### `test_stage3_sabotage.TestSabotageB.test_quoting_canonical_hash_while_using_private_value`
- kind: guard
- targets: s3.output_differing
- execution (s3.output_differing): EXERCISED
- note: the quote is correct; the used value differs

### `test_stage3_sabotage.TestSabotageC.test_capture_gate_has_no_identity_to_borrow`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: API-shape fixture: admit_capture's signature carries no identity parameter

### `test_stage3_sabotage.TestSabotageC.test_capture_routed_to_another_model_invalidates_run`
- kind: guard
- targets: s3.capture_subject
- execution (s3.capture_subject): EXERCISED

### `test_stage3_sabotage.TestSabotageC.test_refuse_capture_policy_scopes_the_refusal`
- kind: guard
- targets: s3.capture_subject
- execution (s3.capture_subject): EXERCISED
- note: the subject check under the REFUSE_CAPTURE policy

### `test_stage3_sabotage.TestSabotageD.test_served_identity_differing_from_the_pin`
- kind: guard
- targets: s3.freeze_served_pin
- execution (s3.freeze_served_pin): EXERCISED

### `test_stage3_sabotage.TestSabotageE.test_gate_honours_recorded_event_not_the_live_object`
- kind: guard
- targets: s3.receipt_facts
- execution (s3.receipt_facts): EXERCISED

### `test_stage3_sabotage.TestSabotageE.test_post_issuance_receipt_mutation_gains_no_coverage`
- kind: joint-guard
- targets: s3.receipt_facts, s3.receipt_coverage
- execution (s3.receipt_coverage): EXERCISED
- execution (s3.receipt_facts): JOINT-ONLY
- execution (combined): EXERCISED-JOINT
- note: the mutated live object is judged against the recorded event: its facts and its coverage

### `test_stage3_sabotage.TestSabotageF.test_frozen_run_cannot_be_rebound`
- kind: guard
- targets: s3.frozenrun_seal
- execution (s3.frozenrun_seal): NOT-EXERCISED

### `test_stage3_sabotage.TestSabotageG.test_capture_gate_on_body_edited_record_writes_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageG.test_output_admission_on_body_edited_record_writes_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageG.test_output_admission_on_deleted_event_record_writes_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageH.test_consume_on_body_edited_record_issues_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_capture_gate_on_emptied_record_refuses_before_lane_call`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED
- note: an emptied record's chain recomputes; the terminal binding is the discriminator

### `test_stage3_sabotage.TestSabotageI.test_capture_gate_on_tail_truncated_record_refuses_before_lane_call`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_consume_on_emptied_record_issues_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_consume_on_tail_truncated_record_issues_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_freeze_on_emptied_record_refuses_and_writes_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_freeze_on_tail_truncated_record_refuses_and_writes_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_output_admission_on_emptied_record_writes_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

### `test_stage3_sabotage.TestSabotageI.test_output_admission_on_tail_truncated_record_writes_nothing`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED

## Stage 4 — 36 fixtures

### `test_dispatch.TestProcedureBinding.test_declared_identity_is_the_executed_callable`
- kind: guard
- targets: s4.construction_binding
- execution (s4.construction_binding): EXERCISED

### `test_dispatch.TestProcedureBinding.test_fictitious_procedure_identity_rejected_at_construction`
- kind: guard
- targets: s4.construction_validation
- execution (s4.construction_validation): EXERCISED

### `test_dispatch.TestProcedureBinding.test_reproducible_result`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: run reproducibility

### `test_dispatch.TestRegistryAttacks.test_module_registry_rebinding_does_not_redirect_dispatch`
- kind: guard
- targets: s4.construction_binding
- execution (s4.construction_binding): EXERCISED
- note: FX-R60i's fixture

### `test_dispatch.TestRegistryAttacks.test_registry_remapping_refused_and_dispatch_unchanged`
- kind: guard
- targets: s4.registry_immutable
- execution (s4.registry_immutable): EXERCISED
- note: FX-R60h's fixture

### `test_dispatch.TestRunPaths.test_corrupt_artefact_takes_failure_path`
- kind: guard
- targets: s4.digest_comparison
- execution (s4.digest_comparison): NOT-EXERCISED
- note: Stage 4 presents this as a preservation-comparison fixture; the matrix records whether the comparison is actually reached (the corrupt flag is checked before the comparison in preservation_check)

### `test_dispatch.TestRunPaths.test_missing_artefact_takes_failure_path`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: missing artefact handling in the procedure

### `test_dispatch.TestRunPaths.test_unpinned_contract_refuses_to_run`
- kind: guard
- targets: s4.run_pin
- execution (s4.run_pin): EXERCISED

### `test_dispatch.TestRunPaths.test_verdict_records_the_pinned_version`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: verdict carries the pinned version

### `test_dispatch.TestRunPaths.test_wrong_digest_no_corrupt_flag_takes_failure_path`
- kind: guard
- targets: s4.digest_comparison
- execution (s4.digest_comparison): EXERCISED
- note: the DR-08 successor fixture (FX-R60f's shape): wrong digest, no corrupt flag, through run() — the comparison itself is reached

### `test_dispatch.TestRunPaths.test_wrong_input_artefact_refused`
- kind: guard
- targets: s4.run_input_identity
- execution (s4.run_input_identity): EXERCISED

### `test_exam_dr24_replay.TestDR24OriginalReplayExecuted.test_cross_contract_replay_accepted_by_v23`
- kind: exam-evidence
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: executes the historical v2.3 artefact and demonstrates DR-24 reproduces; evidence about the ancestor, not a Stage 4 guard

### `test_exam_dr24_replay.TestV23EvidencePin.test_evidence_file_matches_the_pinned_v23_digest`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: the recovered v2.3 evidence file matches its pin

### `test_exam_fx_r60i_restored_global_dispatch.TestFXR60iRestoredGlobalDispatchSabotage.test_restoring_global_dispatch_fails_fx_r60i`
- kind: exam
- targets: s4.construction_binding, s4.pinned_hash
- execution (s4.construction_binding): SELF-WITNESSED
- execution (s4.pinned_hash): SELF-WITNESSED
- note: its own sabotage restores global dispatch (construction binding) and self-referential validation (pinned hash) together

### `test_exam_fx_r60k_identity_sabotage.TestFXR60kIdentitySabotage.test_removing_object_identity_fails_fx_r60k`
- kind: exam
- targets: s4.identity_check
- execution (s4.identity_check): SELF-WITNESSED
- note: its own sabotage replaces the identity check with content matching

### `test_exam_fx_r60l_reconfirmation.TestFXR60lReconfirmation.test_removing_fingerprint_check_fails_fx_r60l_alone`
- kind: exam
- targets: s4.fingerprint_check
- execution (s4.fingerprint_check): SELF-WITNESSED
- note: its own sabotage removes the fingerprint comparison

### `test_instance_binding.TestSealedInstanceBinding.test_healthy_control_canonical_execution_and_validation`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_instance_binding.TestSealedInstanceBinding.test_rebinding_instance_procedure_refused`
- kind: guard
- targets: s4.seal
- execution (s4.seal): EXERCISED

### `test_verdict_issuance.TestCrossContractReplay.test_a_verdict_rejected_by_b_different_digests`
- kind: guard
- targets: s4.contract_identity
- execution (s4.contract_identity): EXERCISED
- note: the matrix's verdict, after two classification attempts: the verdict object IS A's issued object (the verdict conjunct passes trivially), its contents fingerprint-match A's entry, its input IDENTITY matches B (only the payload digest differs, and no field check compares that), and the pinned hash is genuine for both — the sole load-bearing check is the K7 lookup's CONTRACT conjunct: no issuance entry issued BY B matches. Stage 4 presented this fixture under identity/pinned-hash; the contract conjunct is the facet that discriminates it

### `test_verdict_issuance.TestCrossContractReplay.test_a_verdict_rejected_by_b_identical_contents`
- kind: guard
- targets: s4.identity_check, s4.contract_identity
- execution (s4.contract_identity): EXERCISED
- execution (s4.identity_check): EXERCISED
- note: FX-R60k's fixture: contents identical. It fails under EITHER conjunct's neutralisation, by different routes — verdict conjunct off: the lookup finds B's own entry and the identical contents fingerprint-match it; contract conjunct off: the lookup finds A's entry, whose fingerprint also matches

### `test_verdict_issuance.TestCrossContractReplay.test_byte_identical_copy_rejected`
- kind: guard
- targets: s4.identity_check
- execution (s4.identity_check): EXERCISED
- note: FX-R60k's fixture

### `test_verdict_issuance.TestCrossContractReplay.test_same_contract_control_accepted`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_verdict_issuance.TestFieldChecks.test_altered_implementation_hash_rejected`
- kind: guard
- targets: s4.pinned_hash
- execution (s4.pinned_hash): EXERCISED
- note: the hash VALUE comparison is the pinned-hash facet

### `test_verdict_issuance.TestFieldChecks.test_input_identity_mismatch_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: input facet

### `test_verdict_issuance.TestFieldChecks.test_missing_implementation_hash_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: hash presence facet

### `test_verdict_issuance.TestFieldChecks.test_missing_input_identity_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: input presence facet

### `test_verdict_issuance.TestFieldChecks.test_missing_version_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: version presence facet

### `test_verdict_issuance.TestFieldChecks.test_not_a_verdict_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: shape facet

### `test_verdict_issuance.TestFieldChecks.test_procedure_mismatch_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: procedure facet

### `test_verdict_issuance.TestFieldChecks.test_version_mismatch_rejected`
- kind: guard
- targets: s4.field_checks
- execution (s4.field_checks): EXERCISED
- note: version facet

### `test_verdict_issuance.TestGenuineAndForged.test_forged_verdict_with_genuine_pinned_hash_rejected`
- kind: guard
- targets: s4.identity_check
- execution (s4.identity_check): EXERCISED
- note: the forgery carries the genuine pinned hash; only issuance identity rejects it

### `test_verdict_issuance.TestGenuineAndForged.test_forgery_offered_against_failure_path_artefact_rejected`
- kind: guard
- targets: s4.identity_check
- execution (s4.identity_check): EXERCISED

### `test_verdict_issuance.TestGenuineAndForged.test_genuine_verdict_accepted_by_its_issuer`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_verdict_issuance.TestIssuanceIntegrity.test_mutated_issued_object_rejected`
- kind: guard
- targets: s4.fingerprint_check
- execution (s4.fingerprint_check): EXERCISED
- note: FX-R60l's fixture: the object is the issued one; its changed fingerprint rejects it

### `test_verdict_issuance.TestIssuanceIntegrity.test_mutated_issued_object_rejection_reason`
- kind: guard
- targets: s4.fingerprint_check
- execution (s4.fingerprint_check): EXERCISED
- note: FX-R60l's reason fixture

### `test_verdict_issuance.TestIssuanceIntegrity.test_mutated_then_restored_exactly_accepted`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: restored exactly, the fingerprint matches again

## Stage 5 — 30 fixtures

### `test_insertion.TestApplication.test_fresh_presentation_applies_once`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: first presentation applies the effect once

### `test_insertion.TestApplication.test_unconsumed_operation_is_not_falsely_refused`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: an unconsumed operation is not refused

### `test_insertion.TestDivergence.test_consumed_event_citing_another_operations_applied`
- kind: guard
- targets: s5.completed_state
- execution (s5.completed_state): EXERCISED
- note: cited-applied facet

### `test_insertion.TestDivergence.test_consumed_event_without_applied_event_is_not_accepted`
- kind: guard
- targets: s5.completed_state
- execution (s5.completed_state): EXERCISED
- note: cited-applied facet

### `test_insertion.TestDivergence.test_consumed_operation_with_missing_effect_is_surfaced`
- kind: guard
- targets: s5.completed_state
- execution (s5.completed_state): EXERCISED
- note: effect-still-present facet

### `test_insertion.TestDivergence.test_recorded_insertion_with_missing_effect_is_surfaced`
- kind: guard
- targets: s5.applied_effect_divergence
- execution (s5.applied_effect_divergence): EXERCISED

### `test_insertion.TestPayloadBinding.test_changed_payload_in_the_crash_window_is_refused`
- kind: guard
- targets: s5.payload_binding
- execution (s5.payload_binding): EXERCISED

### `test_insertion.TestPayloadBinding.test_changed_payload_under_consumed_identity_is_refused`
- kind: guard
- targets: s5.payload_binding
- execution (s5.payload_binding): EXERCISED

### `test_insertion.TestRePresentation.test_consumed_operation_is_already_satisfied`
- kind: guard
- targets: s5.event_recognition
- execution (s5.event_recognition): EXERCISED
- note: asserts the recorded consumption event is cited — recognition from the record, not the effect path

### `test_insertion.TestRePresentation.test_recognition_is_per_identity`
- kind: guard
- targets: s5.identity_function
- execution (s5.identity_function): EXERCISED
- note: the un-presented operation must read UNCONSUMED: what separates the two operations is their identities. (The (None, None) event-recognition neutralisation cannot move it — the expected state is the null state either way; the slot-dropping identity sabotage does move it, as the matrix's collateral record first showed)

### `test_insertion.TestRePresentation.test_reconstructed_operation_is_recognised_not_new`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: DR-01's end-to-end demonstration; its discriminating sabotage would be a non-canonical identity mint, which no matrix mechanism performs — named as a sabotage-shape gap

### `test_insertion.TestRecordDiscipline.test_emptied_record_refuses_by_terminal_binding`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_insertion.TestRecordDiscipline.test_tampered_record_refuses_and_writes_nothing`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_operations.TestCanonicalIdentity.test_identity_does_not_depend_on_payload`
- kind: guard
- targets: s5.identity_payload
- execution (s5.identity_payload): EXERCISED
- note: discriminated by the payload-included sabotage variant, not by the slot-dropped variant of the identity function

### `test_operations.TestCanonicalIdentity.test_identity_is_a_function_of_the_triple`
- kind: guard
- targets: s5.identity_determinism
- execution (s5.identity_determinism): EXERCISED
- note: determinism half of the identity function; discriminated by the non-deterministic sabotage variant

### `test_operations.TestCanonicalIdentity.test_identity_parts_all_bind`
- kind: guard
- targets: s5.identity_function
- execution (s5.identity_function): EXERCISED
- note: each triple part varied in turn

### `test_operations.TestOperationImmutability.test_attributes_cannot_be_rebound`
- kind: guard
- targets: s5.operation_seal
- execution (s5.operation_seal): EXERCISED

### `test_operations.TestOperationImmutability.test_payload_cannot_be_mutated_through_the_copy`
- kind: guard
- targets: s5.payload_copy
- execution (s5.payload_copy): EXERCISED

### `test_operations.TestOperationImmutability.test_payload_digest_is_canonical`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: payload digest canonicality

### `test_operations.TestPureConstruction.test_build_touches_no_state`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: purity: build reads/writes no state

### `test_operations.TestPureConstruction.test_reconstruction_after_consumption_is_the_same_operation`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: reconstruction equality (identity + payload)

### `test_operations.TestPureConstruction.test_repeated_builds_are_equal`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: purity: repeated builds equal

### `test_recovery.TestInterruptionBetweenInsertionAndRecording.test_crash_after_applied_event_before_consumption`
- kind: guard
- targets: s5.effect_recognition
- execution (s5.effect_recognition): EXERCISED

### `test_recovery.TestInterruptionBetweenInsertionAndRecording.test_crash_after_effect_before_any_recording`
- kind: guard
- targets: s5.effect_recognition
- execution (s5.effect_recognition): EXERCISED

### `test_recovery.TestPartialInsertion.test_interruption_mid_insertion_then_retry`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: the crash lands DURING the effect write: the insertion never landed (orphan temp only), so the retry is a fresh application — the effect-recognition branch is not what this fixture exercises (classification corrected on a first-hand reading)

### `test_recovery.TestRestartRecognition.test_consumed_missing_effect_diverges_after_restart`
- kind: guard
- targets: s5.completed_state
- execution (s5.completed_state): EXERCISED
- note: after an actual process restart

### `test_recovery.TestRestartRecognition.test_consumed_operation_recognised_after_restart`
- kind: guard
- targets: s5.event_recognition
- execution (s5.event_recognition): EXERCISED
- note: recognition rebuilt from the record alone in a new process

### `test_recovery.TestRestartRecognition.test_partial_insertion_recovered_by_new_process`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: the same never-landed shape, recovered by a new process: a fresh application, not an effect recognition

### `test_recovery.TestRestartRecognition.test_retry_after_crash_and_restart`
- kind: guard
- targets: s5.effect_recognition
- execution (s5.effect_recognition): EXERCISED

### `test_recovery.TestRestartRecognition.test_unconsumed_operation_applies_after_restart`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: an unconsumed operation still applies after restart

## Stage 6 — 54 fixtures

### `test_attribution.TestLabelConversionRefused.test_every_conversion_attempt_raises`
- kind: guard
- targets: s6.label_conversion
- execution (s6.label_conversion): EXERCISED

### `test_attribution.TestLabelConversionRefused.test_label_preserved_as_local_not_attribution`
- kind: guard
- targets: s6.label_conversion
- execution (s6.label_conversion): NOT-EXERCISED

### `test_attribution.TestOneFailureOneRecord.test_class_outside_vocabulary_refused`
- kind: guard
- targets: s6.vocabulary
- execution (s6.vocabulary): EXERCISED

### `test_attribution.TestOneFailureOneRecord.test_no_attribution_yet_reads_as_none`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: absence reads as None

### `test_attribution.TestOneFailureOneRecord.test_second_mint_for_one_failure_refused`
- kind: guard
- targets: s6.one_record
- execution (s6.one_record): EXERCISED

### `test_attribution.TestOneFailureOneRecord.test_three_surfaces_reference_the_same_record`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: closure/ledger/adjudication views reference one record

### `test_attribution.TestOneFailureOneRecord.test_views_read_the_fact_back_from_disk`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: views re-read from disk

### `test_attribution.TestPinnedAuthority.test_genuine_record_issues`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_attribution.TestPinnedAuthority.test_ledger_requires_the_issued_capability`
- kind: guard
- targets: s6.point_of_use
- execution (s6.point_of_use): NOT-EXERCISED

### `test_attribution.TestPinnedAuthority.test_mutated_genuine_record_refused`
- kind: guard
- targets: s6.issuance_record_check
- execution (s6.issuance_record_check): EXERCISED

### `test_attribution.TestPinnedAuthority.test_self_appointed_record_refused`
- kind: guard
- targets: s6.issuance_record_check
- execution (s6.issuance_record_check): EXERCISED

### `test_attribution.TestRecordDiscipline.test_tampered_record_refuses_and_stays_byte_identical`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_capability_swapped_onto_ledger_cannot_mint`
- kind: guard
- targets: s6.point_of_use
- execution (s6.point_of_use): EXERCISED

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_direct_construction_from_genuine_record_refused`
- kind: guard
- targets: s6.issuance_token
- execution (s6.issuance_token): EXERCISED

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_direct_construction_from_impostor_record_refused`
- kind: guard
- targets: s6.issuance_token
- execution (s6.issuance_token): EXERCISED

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_cannot_mint_attribution`
- kind: joint-guard
- targets: s6.issuance_token, s6.point_of_use
- execution (s6.issuance_token): JOINT-ONLY
- execution (s6.point_of_use): EXERCISED
- execution (combined): EXERCISED-JOINT
- note: a forged capability is stopped at construction or at point of use, whichever it reaches

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_cannot_resolve_discrepancy`
- kind: joint-guard
- targets: s6.issuance_token, s6.point_of_use
- execution (s6.issuance_token): JOINT-ONLY
- execution (s6.point_of_use): EXERCISED
- execution (combined): EXERCISED-JOINT

### `test_correction_round_1.TestCapabilityCannotBeSelfIssued.test_forged_capability_carrying_the_pinned_digest_cannot_mint`
- kind: joint-guard
- targets: s6.issuance_token, s6.point_of_use
- execution (s6.issuance_token): JOINT-ONLY
- execution (s6.point_of_use): EXERCISED
- execution (combined): EXERCISED-JOINT

### `test_correction_round_1.TestDiscrepancyLinkMustResolve.test_healthy_link_still_mints_and_reads_back`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_correction_round_1.TestDiscrepancyLinkMustResolve.test_nonexistent_attribution_digest_refused`
- kind: guard
- targets: s6.resolve_attribution
- execution (s6.resolve_attribution): EXERCISED

### `test_correction_round_1.TestDiscrepancyLinkMustResolve.test_readback_refuses_an_unresolvable_link`
- kind: guard
- targets: s6.resolve_attribution
- execution (s6.resolve_attribution): EXERCISED

### `test_correction_round_1.TestDiscrepancyLinkMustResolve.test_wrong_type_attribution_digest_refused`
- kind: guard
- targets: s6.resolve_attribution
- execution (s6.resolve_attribution): EXERCISED

### `test_discrepancy.TestAuthorisedResolution.test_authorised_resolution_records_decision_and_authority`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: resolution happy path

### `test_discrepancy.TestAuthorisedResolution.test_resolution_without_authority_refused`
- kind: guard
- targets: s6.point_of_use
- execution (s6.point_of_use): NOT-EXERCISED

### `test_discrepancy.TestAuthorisedResolution.test_second_resolution_refused`
- kind: guard
- targets: s6.one_resolution
- execution (s6.one_resolution): EXERCISED

### `test_discrepancy.TestBothPositionsPreserved.test_positions_verbatim_and_state_unresolved`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: both positions preserved verbatim

### `test_discrepancy.TestBothPositionsPreserved.test_the_original_attribution_is_not_changed`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: resolution does not rewrite the attribution

### `test_discrepancy.TestIndeterminate.test_indeterminate_is_terminal_for_the_disagreement_only`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: indeterminate terminality, attribution untouched

### `test_examiner_g6.TestReportResolution.test_conflict_becomes_a_discrepancy_preserving_both`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: report conflict becomes a discrepancy

### `test_examiner_g6.TestReportResolution.test_contradictory_literals_flagged_by_name`
- kind: guard
- targets: s6.g6_contradiction
- execution (s6.g6_contradiction): EXERCISED

### `test_examiner_g6.TestReportResolution.test_correct_literals_pass`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_examiner_g6.TestReportResolution.test_flagged_not_corrected`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: asserts the resolved entry preserves the literal and carries the rendered location — resolution-entry construction; the flag facet itself is discriminated by its sibling, test_contradictory_literals_flagged_by_name

### `test_examiner_g6.TestReportResolution.test_unresolvable_reference_is_an_error_not_a_flag`
- kind: guard
- targets: s6.g6_resolution
- execution (s6.g6_resolution): NOT-EXERCISED

### `test_reproductions.TestEvidencePins.test_executed_stack_matches_the_records_own_pins`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: the executed stack matches the preserved record's pins

### `test_reproductions.TestFindingsBecomeAttributions.test_t02_finding_recorded_and_attributed`
- kind: reproduction
- targets: s6.format_prescribed
- execution (s6.format_prescribed): NOT-EXERCISED
- note: T02's finding becomes a SYSTEM attribution on the format-not-prescribed fact

### `test_reproductions.TestT02.test_attribution`
- kind: reproduction
- targets: s6.format_prescribed
- execution (s6.format_prescribed): EXERCISED

### `test_reproductions.TestT02.test_transcription_reproduces_the_record`
- kind: reproduction
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: transcription of preserved attempt-3 evidence

### `test_reproductions.TestT07.test_attribution`
- kind: reproduction
- targets: s6.format_prescribed
- execution (s6.format_prescribed): EXERCISED

### `test_reproductions.TestT07.test_transcription_reproduces_the_record`
- kind: reproduction
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: transcription of preserved attempt-3 evidence

### `test_reproductions.TestT09.test_attributions`
- kind: reproduction
- targets: s6.format_prescribed
- execution (s6.format_prescribed): EXERCISED

### `test_reproductions.TestT09.test_transcriptions_reproduce_the_record`
- kind: reproduction
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: transcription of preserved attempt-3 evidence

### `test_schema_contract.TestCausalTableControls.test_agreement`
- kind: guard
- targets: s6.extraction
- execution (s6.extraction): EXERCISED
- note: the agreement branch returns on extraction equality BEFORE format_prescribed or any lines matching is consulted; the regex extraction is its mechanism

### `test_schema_contract.TestCausalTableControls.test_checker_defect_on_compliant_response`
- kind: guard
- targets: s6.format_prescribed_false
- execution (s6.format_prescribed_false): EXERCISED
- note: prescribed is genuinely True here, so only the opposite-direction sabotage (reported never prescribed) can move this branch

### `test_schema_contract.TestCausalTableControls.test_input_branch`
- kind: guard
- targets: s6.input_defect_branch
- execution (s6.input_defect_branch): EXERCISED
- note: examine()'s input-defect branch returns before any extraction fact is read

### `test_schema_contract.TestCausalTableControls.test_model_branch`
- kind: guard
- targets: s6.format_prescribed_false
- execution (s6.format_prescribed_false): EXERCISED
- note: the branch is VALUE_NOT_STATED_AS_PRESCRIBED: extraction yields nothing, the value is not stated, and prescribed is genuinely True — only the opposite-direction sabotage moves it (the lines-matching facet never executes for this regex contract)

### `test_schema_contract.TestCausalTableControls.test_unknown_branch`
- kind: guard
- targets: s6.format_prescribed
- execution (s6.format_prescribed): EXERCISED
- note: prescribed is genuinely False; forcing it True moves the branch to MODEL — the single-direction sabotage suffices

### `test_schema_contract.TestChangedUnderUnchanged.test_checker_changed_schema_unchanged`
- kind: guard
- targets: s6.schema_binding
- execution (s6.schema_binding): EXERCISED

### `test_schema_contract.TestChangedUnderUnchanged.test_checker_rebound_to_another_schema`
- kind: guard
- targets: s6.schema_binding
- execution (s6.schema_binding): EXERCISED

### `test_schema_contract.TestChangedUnderUnchanged.test_schema_changed_checker_unchanged`
- kind: guard
- targets: s6.schema_binding
- execution (s6.schema_binding): EXERCISED

### `test_schema_contract.TestFindingIsRecorded.test_finding_event_on_the_record`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: the finding is recorded as an event

### `test_schema_contract.TestPinnedSchemaArtefact.test_checker_binding_comes_from_the_frozen_object`
- kind: guard
- targets: s6.schema_binding
- execution (s6.schema_binding): NOT-EXERCISED

### `test_schema_contract.TestPinnedSchemaArtefact.test_delivered_instruction_is_preserved_in_full`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: instruction preservation

### `test_schema_contract.TestPinnedSchemaArtefact.test_one_identity_over_both_sections`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: one identity over schema + contract sections

### `test_schema_contract.TestPinnedSchemaArtefact.test_schema_and_contract_are_sealed`
- kind: guard
- targets: s6.schema_seal
- execution (s6.schema_seal): EXERCISED

## Stage 7 — 34 fixtures

### `test_anchor_provenance.TestDirectConstructionRefused.test_direct_construction_from_attacker_values_refused`
- kind: guard
- targets: s7.pin_constructor
- execution (s7.pin_constructor): EXERCISED

### `test_anchor_provenance.TestDirectConstructionRefused.test_direct_construction_from_genuine_values_refused`
- kind: guard
- targets: s7.pin_constructor
- execution (s7.pin_constructor): EXERCISED
- note: the path is verified, not the values

### `test_anchor_provenance.TestHealthyControl.test_genuine_anchor_verifies_and_closes_complete`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_gap_survives_under_the_genuine_pin`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: after refused substitutions, genuine accounting keeps the exact gap

### `test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_append_and_writes_nothing`
- kind: guard
- targets: s7.pin_point_of_use
- execution (s7.pin_point_of_use): EXERCISED

### `test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_closure_and_writes_nothing`
- kind: guard
- targets: s7.pin_point_of_use
- execution (s7.pin_point_of_use): EXERCISED

### `test_anchor_provenance.TestSubstitutionAtAccountAndClosure.test_substitution_refused_at_receipt_account`
- kind: guard
- targets: s7.pin_point_of_use
- execution (s7.pin_point_of_use): EXERCISED

### `test_anchor_provenance.TestSubstitutionAtLifecycle.test_attack_is_coherent_under_attacker_anchor`
- kind: functional
- targets: none claimed
- execution: no claimed pair — collateral-monitored only
- note: attack-coherence precondition: the forged anchor genuinely authenticates the attacker tag, shown before any refusal is asserted

### `test_anchor_provenance.TestSubstitutionAtLifecycle.test_substituted_anchor_refused_at_lifecycle_state`
- kind: guard
- targets: s7.pin_point_of_use
- execution (s7.pin_point_of_use): EXERCISED

### `test_anchor_provenance.TestSubstitutionAtLifecycle.test_true_state_under_the_genuine_pin`
- kind: guard
- targets: s7.authentication
- execution (s7.authentication): EXERCISED
- note: the same receipt under the genuine pin lands COLLECTED_UNAUTHENTICATED

### `test_anchor_provenance.TestSubstitutionAtLifecycle.test_value_identical_forgery_refused`
- kind: guard
- targets: s7.pin_point_of_use
- execution (s7.pin_point_of_use): EXERCISED
- note: values copy the pin; the token does not

### `test_closure_account.TestClosureStatesGapsExactly.test_closure_complete_when_every_receipt_verified`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_closure_account.TestClosureStatesGapsExactly.test_each_deficient_state_named_as_its_exact_gap`
- kind: joint-guard
- targets: s7.authentication, s7.digest_comparison, s7.package_lookup
- execution (s7.authentication): EXERCISED
- execution (s7.digest_comparison): EXERCISED
- execution (s7.package_lookup): EXERCISED
- execution (combined): EXERCISED-JOINT
- note: one receipt per deficient state; each state's guard must hold for its gap line to be the exact one

### `test_closure_account.TestDR04Shape.test_dr04_receipts_stated_as_not_collected`
- kind: guard
- targets: s7.package_lookup
- execution (s7.package_lookup): EXERCISED
- note: DR-04's shape: issued, content never collected — the read_content absence point

### `test_closure_account.TestUnrecordedEntries.test_unrecorded_package_entry_named_as_a_gap`
- kind: guard
- targets: s7.unrecorded_accounting
- execution (s7.unrecorded_accounting): EXERCISED

### `test_lifecycle.TestDigestMismatch.test_content_mismatching_digest`
- kind: guard
- targets: s7.digest_comparison
- execution (s7.digest_comparison): EXERCISED

### `test_lifecycle.TestFullLifecycle.test_full_lifecycle_verified`
- kind: control
- targets: none claimed
- execution: no claimed pair — collateral-monitored only

### `test_lifecycle.TestFullLifecycle.test_issuance_never_satisfies_collection_or_verification`
- kind: guard
- targets: s7.package_lookup
- execution (s7.package_lookup): NOT-EXERCISED
- note: issuance alone reads as not collected

### `test_lifecycle.TestIssuanceAndCollectionRules.test_collect_unissued_refused`
- kind: guard
- targets: s7.collect_issuance
- execution (s7.collect_issuance): NOT-EXERCISED

### `test_lifecycle.TestIssuanceAndCollectionRules.test_reissue_same_commitment_refused`
- kind: guard
- targets: s7.issue_once
- execution (s7.issue_once): EXERCISED

### `test_lifecycle.TestIssuanceAndCollectionRules.test_second_collection_refused`
- kind: guard
- targets: s7.collect_once
- execution (s7.collect_once): EXERCISED

### `test_lifecycle.TestIssuanceAndCollectionRules.test_unrecorded_package_entry_is_not_a_lifecycle_state`
- kind: guard
- targets: s7.issuance_lookup
- execution (s7.issuance_lookup): EXERCISED

### `test_lifecycle.TestIssuedWithoutContent.test_issued_without_content`
- kind: guard
- targets: s7.package_lookup
- execution (s7.package_lookup): EXERCISED

### `test_lifecycle.TestRemovedFromPackage.test_removed_after_collection`
- kind: guard
- targets: s7.package_lookup
- execution (s7.package_lookup): EXERCISED
- note: the read_entry absence point

### `test_lifecycle.TestRemovedFromPackage.test_removed_after_issuance`
- kind: guard
- targets: s7.package_lookup
- execution (s7.package_lookup): EXERCISED
- note: the read_entry absence point

### `test_lifecycle.TestStatesDistinct.test_all_five_states_are_distinct`
- kind: joint-guard
- targets: s7.authentication, s7.digest_comparison, s7.package_lookup
- execution (s7.authentication): EXERCISED
- execution (s7.digest_comparison): EXERCISED
- execution (s7.package_lookup): EXERCISED
- execution (combined): EXERCISED-JOINT
- note: the five states told apart in one run

### `test_lifecycle.TestUnauthenticated.test_issued_under_other_terms_does_not_authenticate`
- kind: guard
- targets: s7.authentication
- execution (s7.authentication): EXERCISED

### `test_lifecycle.TestUnauthenticated.test_package_supplied_anchor_is_not_trusted`
- kind: guard
- targets: s7.authentication
- execution (s7.authentication): EXERCISED
- note: verification proceeds under the genuine pin; the package's anchor is not consulted

### `test_lifecycle.TestUnauthenticated.test_tag_absent`
- kind: guard
- targets: s7.authentication
- execution (s7.authentication): EXERCISED

### `test_lifecycle.TestUnauthenticated.test_tag_forged_under_attacker_key`
- kind: guard
- targets: s7.authentication
- execution (s7.authentication): EXERCISED

### `test_record_discipline.TestEmptiedRecord.test_collection_refused_on_emptied_record`
- kind: guard
- targets: s3.terminal_facet
- execution (s3.terminal_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_record_discipline.TestTamperedRecord.test_account_refused_on_body_edited_record`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_record_discipline.TestTamperedRecord.test_collection_refused_on_body_edited_record`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED
- note: shared Stage 3 binder facet

### `test_record_discipline.TestTamperedRecord.test_issuance_refused_on_body_edited_record`
- kind: guard
- targets: s3.chain_facet
- execution (s3.chain_facet): EXERCISED
- note: shared Stage 3 binder facet
