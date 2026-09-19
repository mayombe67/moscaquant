from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain import mq7_18_pairwise_route_interaction as mq718
from brain import mq7_17_cumulative_first_wave_mediation as base


EXPERIMENT = "mq7-19-conditional-pairwise-contribution-v1"

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / f"{EXPERIMENT}.json"
)

PAIRS = (
    (62598, 77298),
    (62598, 79672),
    (79672, 77298),
)

UNIQUE_TARGETS = tuple(
    sorted({target for pair in PAIRS for target in pair})
)


def conditional_fraction(
    *,
    pair_attenuation: float,
    conditioning_attenuation: float,
) -> float:
    residual = 1.0 - conditioning_attenuation

    if residual <= 0.0:
        raise RuntimeError(
            "conditioning lesion leaves no measurable residual"
        )

    return (
        pair_attenuation
        - conditioning_attenuation
    ) / residual


def run_condition(
    *,
    connectome,
    targets,
    plasticity_modifier,
    common,
    intact_effect,
):
    return mq718.run_condition(
        connectome=connectome,
        targets=targets,
        plasticity_modifier=plasticity_modifier,
        common=common,
        intact_effect=intact_effect,
    )


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = base.load_inputs()

    digest_before = base.csr_digest(connectome)

    plasticity = base.build_plasticity(
        connectome
    )
    plasticity_modifier = (
        base.build_synaptic_modifier(
            plasticity
        )
    )

    seed, shock_modifier = (
        base.build_shock_modifier()
    )

    common = {
        "connectome": connectome,
        "retinal_indices": retinal_indices,
        "channel_indices": channel_indices,
        "release_gain": release_gain,
        "shock_modifier": shock_modifier,
    }

    print("=" * 72)
    print(
        "MQ-7.19 CONDITIONAL PAIRWISE CONTRIBUTION"
    )
    print("=" * 72)
    print(
        "reused SHOCK target:",
        base.SHOCK_TARGET,
    )
    print(
        "reused SHOCK seed:",
        seed,
    )

    intact = base.run_pair(
        lesion=None,
        plasticity_modifier=plasticity_modifier,
        common=common,
    )
    intact_effect = (
        intact["abs_dn_c1_delta"]
    )

    print(
        "intact |DN-C1|:",
        intact_effect,
    )

    singles = {}

    for target in UNIQUE_TARGETS:
        singles[target] = run_condition(
            connectome=connectome,
            targets=(target,),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )

    records = []

    for first, second in PAIRS:
        pair = run_condition(
            connectome=connectome,
            targets=(first, second),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )

        a = singles[first]["attenuation"]
        b = singles[second]["attenuation"]
        ab = pair["attenuation"]

        second_given_first = conditional_fraction(
            pair_attenuation=ab,
            conditioning_attenuation=a,
        )

        first_given_second = conditional_fraction(
            pair_attenuation=ab,
            conditioning_attenuation=b,
        )

        gain_second_given_first = (
            second_given_first - b
        )

        gain_first_given_second = (
            first_given_second - a
        )

        record = {
            "targets": [first, second],
            "single_a": singles[first],
            "single_b": singles[second],
            "pair": pair,
            "conditional_b_given_a":
                second_given_first,
            "conditional_a_given_b":
                first_given_second,
            "conditional_gain_b_given_a":
                gain_second_given_first,
            "conditional_gain_a_given_b":
                gain_first_given_second,
        }

        records.append(record)

        print()
        print(
            f"PAIR {base.SOURCE}->{first} + "
            f"{base.SOURCE}->{second}"
        )
        print(
            "A attenuation:",
            a,
        )
        print(
            "B attenuation:",
            b,
        )
        print(
            "AB attenuation:",
            ab,
        )
        print(
            "B given A:",
            second_given_first,
            "gain:",
            gain_second_given_first,
        )
        print(
            "A given B:",
            first_given_second,
            "gain:",
            gain_first_given_second,
        )

    #
    # Null controls for every unique branch in the frozen pair set.
    #
    null_single = run_condition(
        connectome=connectome,
        targets=(base.NULL_CONTROL,),
        plasticity_modifier=plasticity_modifier,
        common=common,
        intact_effect=intact_effect,
    )

    null_records = []

    for target in UNIQUE_TARGETS:
        pair = run_condition(
            connectome=connectome,
            targets=(target, base.NULL_CONTROL),
            plasticity_modifier=plasticity_modifier,
            common=common,
            intact_effect=intact_effect,
        )

        target_att = singles[target]["attenuation"]
        null_att = null_single["attenuation"]
        pair_att = pair["attenuation"]

        null_given_target = conditional_fraction(
            pair_attenuation=pair_att,
            conditioning_attenuation=target_att,
        )

        target_given_null = conditional_fraction(
            pair_attenuation=pair_att,
            conditioning_attenuation=null_att,
        )

        null_records.append({
            "target": target,
            "pair": pair,
            "null_given_target":
                null_given_target,
            "null_gain_given_target":
                null_given_target - null_att,
            "target_given_null":
                target_given_null,
            "target_gain_given_null":
                target_given_null - target_att,
        })

    max_abs_null_gain = max(
        max(
            abs(row["null_gain_given_target"]),
            abs(row["target_gain_given_null"]),
        )
        for row in null_records
    )

    print()
    print(
        "max |conditional gain| among null controls:",
        max_abs_null_gain,
    )

    if (
        base.csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    payload = {
        "schema_version":
            "mq7-conditional-pairwise-contribution/v1",
        "experiment":
            EXPERIMENT,
        "frozen_parent":
            mq718.EXPERIMENT,
        "shock_target":
            base.SHOCK_TARGET,
        "shock_seed":
            seed,
        "intact":
            intact,
        "intact_effect":
            intact_effect,
        "frozen_pairs":
            [list(pair) for pair in PAIRS],
        "singles":
            {
                str(target): record
                for target, record
                in singles.items()
            },
        "pairs":
            records,
        "null_single":
            null_single,
        "null_controls":
            null_records,
        "max_abs_null_conditional_gain":
            max_abs_null_gain,
        "connectome_unchanged":
            True,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print(
        "connectome unchanged: True"
    )
    print(
        "results:",
        OUTPUT,
    )
    print(
        "MQ-7.19 EXECUTION COMPLETE"
    )


if __name__ == "__main__":
    main()
