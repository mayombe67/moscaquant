"""MQ-8.5A public achievement semantics overlay.

This module enriches the frozen v1 achievement definitions without changing
the core achievement model or trigger engine.

Scientific semantics live here; runtime occurrence state does not.
"""

from __future__ import annotations


DEFAULT_SEMANTICS = {
    "claim_boundary": "",
    "family": "UNCLASSIFIED",
    "tags": [],
    "related_achievement_ids": [],
    "provenance_class": "FUTURE_EVENT",
    "social_eligible": False,
    "syndication_class": "NOISE",
    "dossier_priority": "NORMAL",
}


SEMANTICS_BY_ID = {
    # ---------------------------------------------------------------------
    # Historical MQ-7 science achievements
    # ---------------------------------------------------------------------
    "ACH-001": {
        "claim_boundary": (
            "Supports the value of the frozen null result in MQ-7.14 for "
            "constraining subsequent hypotheses. Does not establish that all "
            "null results are informative or generalize beyond the tested replay."
        ),
        "family": "NULL_RESULTS",
        "tags": ["MQ-7.14", "null-result", "residual-branch", "hypothesis-test"],
        "related_achievement_ids": ["ACH-005", "ACH-006"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "NOTABLE",
        "dossier_priority": "HIGH",
    },
    "ACH-002": {
        "claim_boundary": (
            "Supports causal dependence on the tested 56393→68045 edge in the "
            "frozen MQ-7.11 replay because the validated-edge ablation removed "
            "the measured effect while the matched control lesion did not. "
            "Does not establish a general biological pathway or mechanism."
        ),
        "family": "CAUSAL_PATHWAY",
        "tags": ["MQ-7.11", "ablation", "causal-route", "validated-edge"],
        "related_achievement_ids": ["ACH-003", "ACH-006", "ACH-020"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "HIGH",
    },
    "ACH-003": {
        "claim_boundary": (
            "Supported only for the frozen MQ-7.17 replay and measured "
            "downstream effect. Does not establish a general network "
            "decomposition, biological pathway, biological learning, or "
            "transfer to other replay conditions without replication."
        ),
        "family": "CAUSAL_PATHWAY",
        "tags": ["MQ-7.17", "mediation", "first-wave", "causal-pathway"],
        "related_achievement_ids": ["ACH-002", "ACH-005", "ACH-006", "ACH-020"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "CRITICAL",
    },
    "ACH-004": {
        "claim_boundary": (
            "Describes the frozen MQ-7.9 target-specificity screen in which ten "
            "tested SC-01 targets exposed the latent modeled plasticity state. "
            "It does not imply that all nearby targets, all perturbations, or "
            "biological neurons would behave similarly."
        ),
        "family": "INTERVENTION",
        "tags": ["MQ-7.9", "SC-01", "target-specificity", "shock"],
        "related_achievement_ids": ["ACH-008", "ACH-009", "ACH-019"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "NOTABLE",
        "dossier_priority": "HIGH",
    },
    "ACH-005": {
        "claim_boundary": (
            "Supports the specific MQ-7.16 observation that large differential "
            "activity can coexist with zero measured lesion attenuation for the "
            "tested control branch. It does not imply that large activity is "
            "generally non-causal."
        ),
        "family": "NULL_RESULTS",
        "tags": ["MQ-7.16", "causal-screen", "control", "dynamic-trace"],
        "related_achievement_ids": ["ACH-001", "ACH-003", "ACH-006", "ACH-007"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "NOTABLE",
        "dossier_priority": "HIGH",
    },
    "ACH-006": {
        "claim_boundary": (
            "Summarizes the MQ-7.13 through MQ-7.16 finding that static "
            "structural ranking was not sufficient to identify the useful "
            "causal branches in the frozen replay, while dynamic divergence "
            "tracing produced productive candidates. This does not establish "
            "dynamic tracing as universally superior."
        ),
        "family": "CAUSAL_PATHWAY",
        "tags": ["MQ-7.13", "MQ-7.14", "MQ-7.15", "MQ-7.16", "topology", "dynamic-trace"],
        "related_achievement_ids": ["ACH-002", "ACH-003", "ACH-005", "ACH-007"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "NOTABLE",
        "dossier_priority": "HIGH",
    },
    "ACH-007": {
        "claim_boundary": (
            "Describes recurrent divergence returning to the original "
            "perturbation node in the frozen MQ-7.15 differential trace. "
            "It is a model/replay observation and does not establish a "
            "biological recurrent mechanism."
        ),
        "family": "DYNAMIC_TRACE",
        "tags": ["MQ-7.15", "recurrence", "differential-trace", "56393"],
        "related_achievement_ids": ["ACH-005", "ACH-006"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "NOTABLE",
        "dossier_priority": "NORMAL",
    },
    "ACH-008": {
        "claim_boundary": (
            "Supports perturbation-dependent expression of persistent modeled "
            "plasticity under the frozen MQ-7.8 replay. Plasticity alone was "
            "silent at baseline. This does not establish biological learning, "
            "consciousness, or financial utility."
        ),
        "family": "PLASTICITY",
        "tags": ["MQ-7.8", "SC-03", "plasticity", "latent-state", "shock"],
        "related_achievement_ids": ["ACH-004", "ACH-009", "ACH-019"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "CRITICAL",
    },
    "ACH-009": {
        "claim_boundary": (
            "The frozen MQ-7.8 replay showed an acute intervention reaching the "
            "modeled decision layer. The large decision effect belongs to the "
            "SHOCK intervention; the persistent plasticity state only subtly "
            "modified the matched trajectory and must not be credited with the "
            "entire decision change."
        ),
        "family": "INTERVENTION",
        "tags": ["MQ-7.8", "decision-layer", "SC-01", "shock", "plasticity-interaction"],
        "related_achievement_ids": ["ACH-004", "ACH-008", "ACH-019"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "CRITICAL",
    },
    "ACH-019": {
        "claim_boundary": (
            "Supports an interaction in the frozen MQ-7.8 replay where a "
            "persistent modeled state became measurable under a second matched "
            "perturbation. It does not establish biological synergy, biological "
            "learning, consciousness, or generalization beyond the tested replay."
        ),
        "family": "PLASTICITY",
        "tags": ["MQ-7.8", "interaction", "latent-state", "SC-03", "SC-01"],
        "related_achievement_ids": ["ACH-004", "ACH-008", "ACH-009"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "CRITICAL",
    },
    "ACH-020": {
        "claim_boundary": (
            "Within the frozen MQ-7.17 replay, cumulative tested first-wave "
            "branches plus the tested downstream 68045→1273 edge reduced the "
            "residual measured effect below 0.001% of intact magnitude at the "
            "current numerical resolution. This is not a claim of universal "
            "network completeness or biological pathway completeness."
        ),
        "family": "CAUSAL_PATHWAY",
        "tags": ["MQ-7.17", "cumulative-mediation", "residual-effect", "causal-pathway"],
        "related_achievement_ids": ["ACH-002", "ACH-003", "ACH-006"],
        "provenance_class": "HISTORICAL_REPLAY",
        "social_eligible": True,
        "syndication_class": "MAJOR",
        "dossier_priority": "CRITICAL",
    },
}


CATEGORY_DEFAULT_FAMILY = {
    "SCIENCE": "SCIENCE",
    "ORACLE": "INTERVENTION",
    "CONTAINMENT": "CONTAINMENT",
    "BEHAVIOR": "BEHAVIOR",
    "LORE": "LORE",
    "ANOMALOUS_OBSERVANCE": "ANOMALOUS_OBSERVANCE",
    "SECRET_ODDITY": "SECRET_ODDITY",
}


def semantics_for(achievement_id: str, category: str) -> dict:
    """Return a complete public semantics record for an achievement."""
    merged = dict(DEFAULT_SEMANTICS)
    merged["family"] = CATEGORY_DEFAULT_FAMILY.get(category, "UNCLASSIFIED")
    merged.update(SEMANTICS_BY_ID.get(achievement_id, {}))

    # Return fresh containers so callers cannot mutate shared module constants.
    merged["tags"] = list(merged.get("tags", []))
    merged["related_achievement_ids"] = list(
        merged.get("related_achievement_ids", [])
    )
    return merged


SEMANTICS_BY_ID.update({
    "ACH-129": {"family": "PROVENANCE", "related_achievement_ids": ["ACH-130"]},
    "ACH-130": {"family": "PROVENANCE", "related_achievement_ids": ["ACH-129", "ACH-140"]},
    "ACH-131": {"family": "CONTAINMENT", "related_achievement_ids": []},
    "ACH-132": {"family": "BEHAVIOR", "related_achievement_ids": ["ACH-134"]},
    "ACH-133": {"family": "REWARD", "related_achievement_ids": ["ACH-134"]},
    "ACH-134": {"family": "REWARD", "related_achievement_ids": ["ACH-133"]},
    "ACH-135": {"family": "INTERPRETATION", "related_achievement_ids": ["ACH-137"]},
    "ACH-136": {"family": "NULL_RESULTS", "related_achievement_ids": []},
    "ACH-137": {"family": "INTERPRETATION", "related_achievement_ids": ["ACH-135"]},
    "ACH-138": {"family": "FAMILY_MODEL", "related_achievement_ids": []},
    "ACH-139": {"family": "LORE", "related_achievement_ids": []},
    "ACH-140": {"family": "SECRET_ODDITY", "related_achievement_ids": ["ACH-130"]},
})


# Canonical 152-slot namespace extension — gym / bro-science presentation pack.
SEMANTICS_BY_ID.update({
    "ACH-141": {"family": "CONTAINMENT", "related_achievement_ids": ["ACH-145"]},
    "ACH-142": {"family": "LORE", "related_achievement_ids": ["ACH-149"]},
    "ACH-143": {"family": "NULL_RESULTS", "related_achievement_ids": ["ACH-136"]},
    "ACH-144": {"family": "RECORDS", "related_achievement_ids": []},
    "ACH-145": {"family": "CONTAINMENT", "related_achievement_ids": ["ACH-141"]},
    "ACH-146": {"family": "CONTROLS", "related_achievement_ids": ["ACH-138"]},
    "ACH-147": {"family": "COVERAGE", "related_achievement_ids": ["ACH-129"]},
    "ACH-148": {"family": "CONTRASTS", "related_achievement_ids": []},
    "ACH-149": {"family": "LORE", "related_achievement_ids": ["ACH-142"]},
    "ACH-150": {"family": "INTERPRETATION", "related_achievement_ids": ["ACH-135"]},
    "ACH-151": {"family": "ANOMALOUS_OBSERVANCE", "related_achievement_ids": []},
    "ACH-152": {"family": "PROVENANCE", "related_achievement_ids": ["ACH-130", "ACH-140"]},
})


SEMANTICS_BY_ID.update({
    "ACH-021": {"family": "MATCHED_COMPARISON", "related_achievement_ids": ["ACH-097"]},
    "ACH-057": {"family": "CONTAINMENT", "related_achievement_ids": ["ACH-049", "ACH-052", "ACH-053"]},
    "ACH-097": {"family": "FAMILY_MODEL", "related_achievement_ids": ["ACH-021"]},
})
