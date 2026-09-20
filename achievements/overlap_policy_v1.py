from __future__ import annotations

CANONICAL_PREDICATE_BY_ID = {
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

COMEDIC_OVERLAP_GROUPS = {}

REVIEW_STATE_BY_ID = {
    achievement_id: "REVIEWED_DISTINCT"
    for achievement_id in CANONICAL_PREDICATE_BY_ID
}
