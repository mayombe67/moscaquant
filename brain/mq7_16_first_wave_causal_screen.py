from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain.mq3_2_anonymous_market_readout import run_replay
from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    csr_digest,
    load_inputs,
)
from oracle.d6_shock import (
    apply_shock_activity,
    build_shock,
    select_shock_target,
)
from oracle.plasticity_modifier import build_synaptic_modifier
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


MARKET = "B"

EXPERIMENT = "mq7-16-first-wave-causal-screen-v1"
SESSION = "mq7-16-shock-56393"

SHOCK_TARGET = 56393
INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

SOURCE = 68045

CANDIDATES = (
    62598,
    66309,
    69484,
    63192,
    77298,
    65046,
    79672,
    73483,
    62142,
    61694,
)

NULL_CONTROL = 82348

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-16-first-wave-causal-screen-v1.json"
)


def build_plasticity(connectome):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "validated plasticity edge missing"
        )

    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-16-preload",
        evidence_reference="mq7-16-sc03",
    )

    if not np.isclose(
        state.edges[0].multiplier,
        0.95,
    ):
        raise RuntimeError(
            "expected multiplier 0.95"
        )

    return state


def find_shock_seed():
    for seed in range(100000):
        _, target = select_shock_target(
            seed=seed,
            experiment_id=EXPERIMENT,
            session_id=SESSION,
        )

        if target == SHOCK_TARGET:
            return seed

    raise RuntimeError(
        "SHOCK seed not found"
    )


def build_shock_modifier():
    seed = find_shock_seed()

    intervention = build_shock(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=SESSION,
        current_generation=INTERVENTION_GENERATION,
    )

    if (
        intervention.target_model_index
        != SHOCK_TARGET
    ):
        raise RuntimeError(
            "SHOCK target mismatch"
        )

    def modifier(
        activity,
        generation,
    ):
        return apply_shock_activity(
            effective_activity=activity,
            intervention=intervention,
            generation=generation,
        )

    return seed, modifier


def edge_weight(
    connectome,
    pre,
    post,
):
    return float(
        connectome[
            post,
            pre,
        ]
    )


def ablation_modifier(
    *,
    presynaptic,
    postsynaptic,
    weight,
):
    def modifier(
        activity,
        synaptic,
    ):
        output = np.array(
            synaptic,
            copy=True,
        )

        output[postsynaptic] -= (
            weight
            * activity[presynaptic]
        )

        return output

    return modifier


def compose(
    *modifiers,
):
    active = [
        modifier
        for modifier in modifiers
        if modifier is not None
    ]

    def combined(
        activity,
        synaptic,
    ):
        output = synaptic

        for modifier in active:
            output = modifier(
                activity,
                output,
            )

        return output

    return combined


def replay(
    *,
    connectome,
    retinal_indices,
    channel_indices,
    release_gain,
    shock_modifier,
    synaptic_modifier=None,
):
    return run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        activity_modifier=shock_modifier,
        synaptic_modifier=synaptic_modifier,
    )


def difference(
    first,
    second,
):
    deltas = {
        channel:
            second["scores"][channel]
            - first["scores"][channel]
        for channel
        in first["scores"]
    }

    return {
        "voltage_identical":
            first[
                "voltage_trace_sha256"
            ]
            == second[
                "voltage_trace_sha256"
            ],
        "spikes_identical":
            first[
                "spike_trace_sha256"
            ]
            == second[
                "spike_trace_sha256"
            ],
        "scores_identical":
            first["scores"]
            == second["scores"],
        "decision_identical":
            first["decision"]
            == second["decision"],
        "score_deltas":
            deltas,
        "abs_dn_c1_delta":
            abs(
                float(
                    deltas["DN-C1"]
                )
            ),
    }


def run_pair(
    *,
    lesion,
    plasticity_modifier,
    common,
):
    baseline = replay(
        **common,
        synaptic_modifier=lesion,
    )

    adaptive = replay(
        **common,
        synaptic_modifier=(
            compose(
                lesion,
                plasticity_modifier,
            )
        ),
    )

    return difference(
        baseline,
        adaptive,
    )


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    digest_before = csr_digest(
        connectome
    )

    plasticity = build_plasticity(
        connectome
    )

    plasticity_modifier = (
        build_synaptic_modifier(
            plasticity
        )
    )

    seed, shock_modifier = (
        build_shock_modifier()
    )

    common = {
        "connectome":
            connectome,
        "retinal_indices":
            retinal_indices,
        "channel_indices":
            channel_indices,
        "release_gain":
            release_gain,
        "shock_modifier":
            shock_modifier,
    }

    print("=" * 72)
    print(
        "MQ-7.16 FIRST-WAVE CAUSAL SCREEN"
    )
    print("=" * 72)

    print(
        "SHOCK target:",
        SHOCK_TARGET,
    )

    print(
        "SHOCK seed:",
        seed,
    )

    intact = run_pair(
        lesion=None,
        plasticity_modifier=(
            plasticity_modifier
        ),
        common=common,
    )

    intact_effect = (
        intact["abs_dn_c1_delta"]
    )

    print()
    print(
        "intact |DN-C1|:",
        intact_effect,
    )

    records = []

    for target in (
        *CANDIDATES,
        NULL_CONTROL,
    ):
        print()
        print("-" * 72)

        print(
            "target:",
            target,
        )

        weight = edge_weight(
            connectome,
            SOURCE,
            target,
        )

        if weight == 0.0:
            print(
                "status: NO_DIRECT_EDGE"
            )

            records.append({
                "target":
                    target,
                "status":
                    "NO_DIRECT_EDGE",
                "weight":
                    0.0,
            })

            continue

        lesion = ablation_modifier(
            presynaptic=SOURCE,
            postsynaptic=target,
            weight=weight,
        )

        result = run_pair(
            lesion=lesion,
            plasticity_modifier=(
                plasticity_modifier
            ),
            common=common,
        )

        effect = (
            result[
                "abs_dn_c1_delta"
            ]
        )

        attenuation = (
            1.0
            - effect
            / intact_effect
        )

        print(
            "weight:",
            weight,
        )

        print(
            "voltage identical:",
            result[
                "voltage_identical"
            ],
        )

        print(
            "spikes identical:",
            result[
                "spikes_identical"
            ],
        )

        print(
            "scores identical:",
            result[
                "scores_identical"
            ],
        )

        print(
            "decision identical:",
            result[
                "decision_identical"
            ],
        )

        print(
            "DN-C1 delta:",
            result[
                "score_deltas"
            ][
                "DN-C1"
            ],
        )

        print(
            "|DN-C1|:",
            effect,
        )

        print(
            "attenuation:",
            attenuation,
        )

        records.append({
            "target":
                target,
            "status":
                "TESTED",
            "weight":
                weight,
            "result":
                result,
            "attenuation":
                attenuation,
            "is_null_control":
                target == NULL_CONTROL,
        })

    tested = [
        record
        for record in records
        if record["status"]
        == "TESTED"
    ]

    ranked = sorted(
        tested,
        key=lambda record: (
            -record[
                "attenuation"
            ],
            record["target"],
        ),
    )

    print()
    print("=" * 72)
    print("CAUSAL SCREEN RANKING")
    print("=" * 72)

    for rank, record in enumerate(
        ranked,
        start=1,
    ):
        print(
            rank,
            "target=",
            record["target"],
            "attenuation=",
            record[
                "attenuation"
            ],
            "control=",
            record[
                "is_null_control"
            ],
        )

    if (
        csr_digest(connectome)
        != digest_before
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    payload = {
        "schema_version":
            "mq7-first-wave-causal-screen/v1",
        "shock_target":
            SHOCK_TARGET,
        "shock_seed":
            seed,
        "source":
            SOURCE,
        "intact":
            intact,
        "records":
            records,
        "ranked_tested":
            ranked,
        "null_control":
            NULL_CONTROL,
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
        "MQ-7.16 COMPLETE"
    )


if __name__ == "__main__":
    main()
