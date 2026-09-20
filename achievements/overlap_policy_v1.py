from __future__ import annotations

CANONICAL_PREDICATE_BY_ID = {
    "ACH-021": "science.matched_heavier_source_at_comparable_opportunity",
    "ACH-057": "containment.unsupported_exemption_request_rejected",
    "ACH-097": "lore.salads_car_flip_followup",
    "ACH-001": "science.preregistered_null_constrains_next_question",
    "ACH-008": "science.persistent_state_silent_at_baseline_exposed_by_perturbation",
    "ACH-012": "science.preregistered_control_constrains_causal_interpretation",
    "ACH-019": "science.latent_state_requires_second_matched_perturbation",
    "ACH-035": "oracle.measurable_positive_modulation",
    "ACH-036": "oracle.measurable_propagation_change",
    "ACH-040": "oracle.valid_nonzero_effect_below_practical_relevance_threshold",
    "ACH-066": "behavior.single_adverse_threshold_held_without_reversal",
    "ACH-074": "behavior.progressive_adverse_worsening_while_exposure_persists",
    "ACH-129": "science.expected_lookup_target_missing",
    "ACH-130": "science.provenance_unresolved_or_conflicting",
    "ACH-131": "containment.fly_proximity_presentation_event",
    "ACH-132": "behavior.predefined_adverse_or_absurd_outcome",
    "ACH-133": "behavior.positive_reinforcement_eligible",
    "ACH-134": "behavior.expected_reward_withheld_or_ineligible",
    "ACH-135": "oracle.interpretation_or_classification_mismatch",
    "ACH-136": "science.frozen_hypothesis_rejected",
    "ACH-137": "oracle.prediction_hindsight_discrepancy",
    "ACH-138": "lore.control_supported_status_demotion",
    "ACH-139": "lore.manual_project_or_experiment_closure",
    "ACH-140": "oddity.unresolved_anomalous_event",
    "ACH-141": "containment.workload_within_resource_ceiling",
    "ACH-142": "lore.validated_result_celebration",
    "ACH-143": "science.adequate_opportunity_minimum_effect_failure",
    "ACH-144": "science.versioned_metric_new_canonical_maximum",
    "ACH-145": "containment.preanalysis_validator_blocks_execution",
    "ACH-146": "science.raw_effect_deflates_under_required_control",
    "ACH-147": "science.predefined_pair_coverage_asymmetry",
    "ACH-148": "science.predefined_subgroups_opposite_directions",
    "ACH-149": "lore.repeatable_achievement_stack_milestone",
    "ACH-150": "oracle.interpretation_arithmetic_or_unit_correction",
    "ACH-151": "observance.cadence_convention_exceeded_without_invariant_failure",
    "ACH-152": "oddity.declared_surrogate_synthetic_or_inferred_input",
}

COMEDIC_OVERLAP_GROUPS = {
    "SALADS_CAR_FLIP": ("ACH-021", "ACH-097"),
}

REVIEW_STATE_BY_ID = {
    achievement_id: "REVIEWED_DISTINCT"
    for achievement_id in CANONICAL_PREDICATE_BY_ID
}

LEGACY_ADJUDICATION_V1 = {
    "ACH-001": "REVIEWED_DISTINCT",
    "ACH-008": "REVIEWED_DISTINCT",
    "ACH-012": "REVIEWED_DISTINCT",
    "ACH-019": "REVIEWED_DISTINCT",
    "ACH-035": "REVIEWED_DISTINCT",
    "ACH-036": "REVIEWED_DISTINCT",
    "ACH-040": "REPLACED_RETARGETED",
    "ACH-066": "REVIEWED_DISTINCT",
    "ACH-074": "REVIEWED_DISTINCT",
}

REVIEW_STATE_BY_ID.update(LEGACY_ADJUDICATION_V1)

SOPRANOS_PACK_REVIEW_V1 = {
    "ACH-021": "REVIEWED_DISTINCT",
    "ACH-057": "REVIEWED_DISTINCT",
    "ACH-097": "INTENTIONAL_COMEDIC_OVERLAP",
}

REVIEW_STATE_BY_ID.update(SOPRANOS_PACK_REVIEW_V1)
