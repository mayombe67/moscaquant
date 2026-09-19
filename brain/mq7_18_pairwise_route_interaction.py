from __future__ import annotations

import itertools
import json
from pathlib import Path

from brain import mq7_17_cumulative_first_wave_mediation as base

EXPERIMENT = "mq7-18-pairwise-route-interaction-v1"
OUTPUT = Path.home() / "moscaquant-data" / "experiments" / f"{EXPERIMENT}.json"


def attenuation(effect: float, intact_effect: float) -> float:
    return 1.0 - effect / intact_effect


def independent_residual_expectation(a: float, b: float) -> float:
    return 1.0 - ((1.0 - a) * (1.0 - b))


def run_condition(*, connectome, targets, plasticity_modifier, common, intact_effect):
    lesion, weights = base.ablation_modifier(connectome, list(targets))
    result = base.run_pair(
        lesion=lesion,
        plasticity_modifier=plasticity_modifier,
        common=common,
    )
    effect = result["abs_dn_c1_delta"]
    return {
        "targets": list(targets),
        "weights": weights,
        "result": result,
        "effect": effect,
        "attenuation": attenuation(effect, intact_effect),
    }


def main():
    connectome, retinal_indices, channel_indices, release_gain = base.load_inputs()
    digest_before = base.csr_digest(connectome)

    plasticity = base.build_plasticity(connectome)
    plasticity_modifier = base.build_synaptic_modifier(plasticity)
    seed, shock_modifier = base.build_shock_modifier()

    common = {
        "connectome": connectome,
        "retinal_indices": retinal_indices,
        "channel_indices": channel_indices,
        "release_gain": release_gain,
        "shock_modifier": shock_modifier,
    }

    print("=" * 72)
    print("MQ-7.18 PAIRWISE ROUTE INTERACTION / COMPENSATION SCREEN")
    print("=" * 72)
    print("reused MQ-7.17 SHOCK target:", base.SHOCK_TARGET)
    print("reused MQ-7.17 SHOCK seed:", seed)

    intact = base.run_pair(
        lesion=None,
        plasticity_modifier=plasticity_modifier,
        common=common,
    )
    intact_effect = intact["abs_dn_c1_delta"]
    print("intact |DN-C1|:", intact_effect)

    candidates = tuple(int(x) for x in base.CUMULATIVE_ORDER)
    if len(candidates) != 10:
        raise RuntimeError("expected exactly ten frozen first-wave branches")

    singles = {}
    for target in candidates:
        rec = run_condition(
            connectome=connectome,
            targets=(target,),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )
        singles[target] = rec
        print("single", f"{base.SOURCE}->{target}", "attenuation=", rec["attenuation"])

    null_single = run_condition(
        connectome=connectome,
        targets=(base.NULL_CONTROL,),
        plasticity_modifier=plasticity_modifier,
        common=common,
        intact_effect=intact_effect,
    )
    print("null single", f"{base.SOURCE}->{base.NULL_CONTROL}",
          "attenuation=", null_single["attenuation"])

    pair_records = []
    for first, second in itertools.combinations(candidates, 2):
        rec = run_condition(
            connectome=connectome,
            targets=(first, second),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )
        a = singles[first]["attenuation"]
        b = singles[second]["attenuation"]
        expected = independent_residual_expectation(a, b)
        rec.update({
            "single_attenuation_a": a,
            "single_attenuation_b": b,
            "independent_residual_expected_attenuation": expected,
            "interaction_excess": rec["attenuation"] - expected,
        })
        pair_records.append(rec)

    if len(pair_records) != 45:
        raise RuntimeError("expected 45 unique first-wave pairs")

    null_pair_controls = []
    for target in candidates:
        rec = run_condition(
            connectome=connectome,
            targets=(target, base.NULL_CONTROL),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )
        expected = independent_residual_expectation(
            singles[target]["attenuation"],
            null_single["attenuation"],
        )
        rec.update({
            "single_attenuation_a": singles[target]["attenuation"],
            "single_attenuation_b": null_single["attenuation"],
            "independent_residual_expected_attenuation": expected,
            "interaction_excess": rec["attenuation"] - expected,
        })
        null_pair_controls.append(rec)

    null_band = max(abs(x["interaction_excess"]) for x in null_pair_controls)

    ranked_positive = sorted(
        pair_records, key=lambda r: r["interaction_excess"], reverse=True
    )
    ranked_negative = sorted(
        pair_records, key=lambda r: r["interaction_excess"]
    )

    print("\nTOP POSITIVE INTERACTION EXCESS")
    for row in ranked_positive[:10]:
        a, b = row["targets"]
        print(
            f"{base.SOURCE}->{a} + {base.SOURCE}->{b}",
            "observed=", row["attenuation"],
            "expected=", row["independent_residual_expected_attenuation"],
            "excess=", row["interaction_excess"],
        )

    print("\nTOP NEGATIVE INTERACTION EXCESS")
    for row in ranked_negative[:10]:
        a, b = row["targets"]
        print(
            f"{base.SOURCE}->{a} + {base.SOURCE}->{b}",
            "observed=", row["attenuation"],
            "expected=", row["independent_residual_expected_attenuation"],
            "excess=", row["interaction_excess"],
        )

    print("\nmax |interaction excess| among null-edge controls:", null_band)

    if base.csr_digest(connectome) != digest_before:
        raise RuntimeError("structural connectome mutated")

    payload = {
        "schema_version": "mq7-pairwise-route-interaction/v1",
        "experiment": EXPERIMENT,
        "frozen_parent": base.EXPERIMENT,
        "shock_target": base.SHOCK_TARGET,
        "shock_seed": seed,
        "intact": intact,
        "intact_effect": intact_effect,
        "first_wave_targets": list(candidates),
        "null_control_target": base.NULL_CONTROL,
        "interaction_null_model": "1 - (1-a)*(1-b)",
        "singles": {str(k): v for k, v in singles.items()},
        "null_single": null_single,
        "pairs": pair_records,
        "null_pair_controls": null_pair_controls,
        "null_interaction_max_abs": null_band,
        "connectome_unchanged": True,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print("\nconnectome unchanged: True")
    print("results:", OUTPUT)
    print("MQ-7.18 EXECUTION COMPLETE")


if __name__ == "__main__":
    main()
