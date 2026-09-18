from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from brain.mq3_2_anonymous_market_readout import (
    run_replay,
)
from brain.mq7_o1_o2_activation import (
    ARTIFACT_ID,
    csr_digest,
    load_inputs,
)
from oracle.d6_shock import (
    SHOCK_TARGET_POOL,
    apply_shock_activity,
    build_shock,
    select_shock_target,
)
from oracle.plasticity_modifier import (
    build_synaptic_modifier,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
)


MARKET = "B"

EXPERIMENT = (
    "mq7-9-shock-target-specificity-v1"
)

INTERVENTION_GENERATION = 32

PLASTICITY_PRE = 56393
PLASTICITY_POST = 68045

OUTPUT = (
    Path.home()
    / "moscaquant-data"
    / "experiments"
    / "mq7-9-shock-target-specificity-v1.json"
)


def build_plasticity(
    connectome,
):
    weight = float(
        connectome[
            PLASTICITY_POST,
            PLASTICITY_PRE,
        ]
    )

    if weight == 0.0:
        raise RuntimeError(
            "validated SC-03 edge missing"
        )

    state = build_empty_plasticity_state()

    return apply_plasticity_update(
        state,
        presynaptic=PLASTICITY_PRE,
        postsynaptic=PLASTICITY_POST,
        baseline_artifact_id=ARTIFACT_ID,
        baseline_weight=weight,
        session_id="mq7-9-preload",
        evidence_reference=(
            "mq7-9-validated-sc03-edge"
        ),
    )


def find_seed_for_target(
    target: int,
) -> tuple[int, str]:
    session_id = (
        f"mq7-9-target-{target}"
    )

    for seed in range(100000):
        _, selected = (
            select_shock_target(
                seed=seed,
                experiment_id=EXPERIMENT,
                session_id=session_id,
            )
        )

        if selected == target:
            return seed, session_id

    raise RuntimeError(
        f"seed not found for target {target}"
    )


def build_shock_modifier(
    *,
    target: int,
):
    seed, session_id = (
        find_seed_for_target(
            target
        )
    )

    intervention = build_shock(
        seed=seed,
        experiment_id=EXPERIMENT,
        session_id=session_id,
        current_generation=(
            INTERVENTION_GENERATION
        ),
    )

    if (
        intervention.target_model_index
        != target
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

    return (
        seed,
        session_id,
        intervention,
        modifier,
    )


def difference(
    first,
    second,
):
    return {
        "voltage_identical": (
            first["voltage_trace_sha256"]
            == second["voltage_trace_sha256"]
        ),
        "spikes_identical": (
            first["spike_trace_sha256"]
            == second["spike_trace_sha256"]
        ),
        "scores_identical": (
            first["scores"]
            == second["scores"]
        ),
        "decision_identical": (
            first["decision"]
            == second["decision"]
        ),
        "score_deltas": {
            channel: (
                second["scores"][channel]
                - first["scores"][channel]
            )
            for channel
            in first["scores"]
        },
    }


def main():
    (
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    ) = load_inputs()

    before_digest = csr_digest(
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

    print("=" * 72)
    print(
        "MQ-7.9 SHOCK TARGET "
        "SPECIFICITY"
    )
    print("=" * 72)

    print("market:", MARKET)
    print(
        "plasticized edge:",
        f"{PLASTICITY_PRE}"
        f"->{PLASTICITY_POST}",
    )
    print(
        "multiplier:",
        plasticity.edges[0].multiplier,
    )
    print(
        "targets:",
        len(SHOCK_TARGET_POOL),
    )

    #
    # Verify plasticity-alone null again.
    #
    print()
    print("running B0 baseline...")

    b0 = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
    )

    print(
        "running BP plasticity only..."
    )

    bp = run_replay(
        MARKET,
        connectome,
        retinal_indices,
        channel_indices,
        release_gain,
        synaptic_modifier=(
            plasticity_modifier
        ),
    )

    baseline_plasticity = difference(
        b0,
        bp,
    )

    print(
        "plasticity-alone voltage identical:",
        baseline_plasticity[
            "voltage_identical"
        ],
    )

    print(
        "plasticity-alone scores identical:",
        baseline_plasticity[
            "scores_identical"
        ],
    )

    records = []

    exposed_targets = []
    spike_targets = []
    decision_targets = []

    for target in SHOCK_TARGET_POOL:
        (
            seed,
            session_id,
            intervention,
            shock_modifier,
        ) = build_shock_modifier(
            target=target
        )

        print()
        print("-" * 72)
        print("target:", target)
        print("seed:", seed)

        bs = run_replay(
            MARKET,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            activity_modifier=(
                shock_modifier
            ),
        )

        bps = run_replay(
            MARKET,
            connectome,
            retinal_indices,
            channel_indices,
            release_gain,
            activity_modifier=(
                shock_modifier
            ),
            synaptic_modifier=(
                plasticity_modifier
            ),
        )

        result = difference(
            bs,
            bps,
        )

        exposed = (
            not result[
                "voltage_identical"
            ]
            or not result[
                "scores_identical"
            ]
        )

        if exposed:
            exposed_targets.append(
                target
            )

        if not result[
            "spikes_identical"
        ]:
            spike_targets.append(
                target
            )

        if not result[
            "decision_identical"
        ]:
            decision_targets.append(
                target
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
            "score deltas:",
            result[
                "score_deltas"
            ],
        )

        records.append({
            "target": target,
            "seed": seed,
            "session_id":
                session_id,
            "shock_generation":
                INTERVENTION_GENERATION,
            "difference":
                result,
        })

    if (
        csr_digest(connectome)
        != before_digest
    ):
        raise RuntimeError(
            "structural connectome mutated"
        )

    print()
    print("=" * 72)
    print("TARGET-SPECIFICITY SUMMARY")
    print("=" * 72)

    print(
        "plasticity alone silent:",
        (
            baseline_plasticity[
                "voltage_identical"
            ]
            and baseline_plasticity[
                "scores_identical"
            ]
        ),
    )

    print(
        "targets exposing plasticity:",
        exposed_targets,
    )

    print(
        "exposing target count:",
        len(exposed_targets),
    )

    print(
        "spike-divergence targets:",
        spike_targets,
    )

    print(
        "decision-divergence targets:",
        decision_targets,
    )

    print(
        "68045 exposed:",
        68045 in exposed_targets,
    )

    print(
        "connectome unchanged: True"
    )

    result_payload = {
        "schema_version":
            "mq7-9-shock-target-specificity/v1",
        "market_condition":
            MARKET,
        "intervention_generation":
            INTERVENTION_GENERATION,
        "plasticized_edge": {
            "presynaptic":
                PLASTICITY_PRE,
            "postsynaptic":
                PLASTICITY_POST,
            "multiplier":
                plasticity.edges[0].multiplier,
        },
        "plasticity_alone":
            baseline_plasticity,
        "target_pool":
            list(SHOCK_TARGET_POOL),
        "targets_exposing_plasticity":
            exposed_targets,
        "spike_divergence_targets":
            spike_targets,
        "decision_divergence_targets":
            decision_targets,
        "connectome_unchanged":
            True,
        "targets":
            records,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            result_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        "results:",
        OUTPUT,
    )

    print(
        "MQ-7.9 COMPLETE"
    )


if __name__ == "__main__":
    main()
