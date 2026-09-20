from __future__ import annotations
from config.paths import data_path


import hashlib
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.market_replay import (
    ASSETS,
    FRAME_COUNT,
    OBSERVATIONS,
    SENSORY_GAIN,
    synthetic_series,
    market_window_at,
)
from brain.market_temporal import MarketVisionTemporalEncoder
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig
from market.features import compute_features
from market.normalization import CausalNormalizer


BASE = data_path('processed')

CONNECTOME = BASE / "connectome-baseline-v1.npz"
RETINA = BASE / "visual-r1-r6-map-v1.npz"
RELAY = BASE / "visual-relay-map-v1.npz"
TERRITORIES = BASE / "market-retinal-territories-v1.npz"
GRADED = BASE / "mq3-2-graded-visual-types-v1.npz"

INTERVENTION = (
    BASE
    / "mq3-2-first-onset-causal-edges-v1.json"
)

OUTPUT = data_path('experiments', 'mq3-2-causal-intervention-v1.json')

RELEASE_GAIN = 0.9981738484618123

TARGETS = (
    92,
    656,
    317,
    137122,
    126002,
    55,
    129,
    51,
    1273,
)

ORIGINAL_ONSETS = {
    92: 145,
    656: 145,
    317: 147,
    137122: 146,
    126002: 147,
    55: 146,
    129: 148,
    51: 149,
    1273: 147,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def load_target_edges():
    data = json.loads(
        INTERVENTION.read_text(
            encoding="utf-8"
        )
    )

    expected_hash = (
        "23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b"
    )

    actual_hash = sha256_file(
        INTERVENTION
    )

    if actual_hash != expected_hash:
        raise RuntimeError(
            "intervention artifact hash mismatch"
        )

    edges = [
        (
            int(edge["presynaptic"]),
            int(edge["postsynaptic"]),
            float(edge["weight"]),
        )
        for edge in data["edges"]
    ]

    if len(edges) != 13:
        raise RuntimeError(
            f"expected 13 targeted edges, got {len(edges)}"
        )

    return edges


def derive_sham_edges(
    connectome,
    targeted_edges,
):
    targeted_pairs = {
        (pre, post)
        for pre, post, _ in targeted_edges
    }

    target_nodes = set(
        TARGETS
    )

    used = set()
    sham = []

    for pre, targeted_post, targeted_weight in targeted_edges:

        column = connectome[
            :,
            pre
        ].tocoo()

        candidates = []

        for post, weight in zip(
            column.row,
            column.data,
        ):
            post = int(post)
            weight = float(weight)

            pair = (
                int(pre),
                post,
            )

            if weight <= 0:
                continue

            if pair in targeted_pairs:
                continue

            if pair in used:
                continue

            if post in target_nodes:
                continue

            distance = abs(
                weight
                - targeted_weight
            )

            candidates.append(
                (
                    distance,
                    post,
                    weight,
                )
            )

        if not candidates:
            raise RuntimeError(
                f"no sham edge available for presynaptic neuron {pre}"
            )

        candidates.sort(
            key=lambda item:
                (
                    item[0],
                    item[1],
                )
        )

        _, sham_post, sham_weight = (
            candidates[0]
        )

        pair = (
            int(pre),
            int(sham_post),
        )

        used.add(
            pair
        )

        sham.append(
            (
                int(pre),
                int(sham_post),
                float(sham_weight),
            )
        )

    if len(sham) != 13:
        raise RuntimeError(
            "sham edge count mismatch"
        )

    return sham


def zero_edges(
    connectome,
    edges,
):
    modified = connectome.tolil(
        copy=True
    )

    for pre, post, expected_weight in edges:

        current = float(
            modified[
                post,
                pre
            ]
        )

        if current <= 0:
            raise RuntimeError(
                f"edge missing or nonpositive: {pre}->{post}"
            )

        if not np.isclose(
            current,
            expected_weight,
            rtol=1e-6,
            atol=1e-12,
        ):
            raise RuntimeError(
                f"weight mismatch for {pre}->{post}: "
                f"{current} != {expected_weight}"
            )

        modified[
            post,
            pre
        ] = 0.0

    modified = modified.tocsr()
    modified.eliminate_zeros()

    return modified


def build_runtime(
    connectome,
    retinal_indices,
):
    return (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=connectome,
            retinal_indices=retinal_indices,
            relay_artifact=RELAY,
            graded_artifact=GRADED,
            config=VisualTransductionConfig(
                release_gain=RELEASE_GAIN,
            ),
        )
    )


def run_condition(
    connectome,
    retinal_indices,
    condition,
):
    runtime = build_runtime(
        connectome,
        retinal_indices,
    )

    encoder = MarketVisionTemporalEncoder(
        TERRITORIES
    )

    if condition != "neutral":
        normalizers = [
            CausalNormalizer(
                window_size=64,
                min_history=8,
            )
            for _ in ASSETS
        ]

        series = [
            synthetic_series(
                condition,
                i,
            )
            for i in range(6)
        ]

    target_voltage = {
        target: []
        for target in TARGETS
    }

    c1_score_sum = 0.0
    c1_frames = 0

    for observation in range(
        OBSERVATIONS
    ):
        if condition == "neutral":
            normalized = np.zeros(
                (6, 7),
                dtype=np.float32,
            )

        else:
            normalized = np.empty(
                (6, 7),
                dtype=np.float32,
            )

            for asset_index in range(6):
                window = market_window_at(
                    series[
                        asset_index
                    ],
                    observation,
                )

                features = compute_features(
                    window
                )

                normalized[
                    asset_index
                ] = normalizers[
                    asset_index
                ].transform(
                    features
                )

        frames = encoder.encode_sequence(
            normalized,
            frame_count=FRAME_COUNT,
        )

        for stimulus in frames:

            runtime.step(
                stimulus
                * SENSORY_GAIN
            )

            for target in TARGETS:
                target_voltage[
                    target
                ].append(
                    float(
                        runtime.voltage[
                            target
                        ]
                    )
                )

            #
            # Score only the frozen responder ensemble
            # here as a diagnostic, not as a replacement
            # for the official DN-C1 readout.
            #
            positive = np.maximum(
                runtime.voltage[
                    list(TARGETS)
                ],
                0.0,
            )

            c1_score_sum += float(
                positive.mean()
            )

            c1_frames += 1

    result = {
        "condition":
            condition,

        "responder_ensemble_score":
            float(
                c1_score_sum
                / c1_frames
            ),

        "targets": {},
    }

    for target in TARGETS:

        voltage = np.asarray(
            target_voltage[
                target
            ],
            dtype=np.float64,
        )

        positive_frames = np.flatnonzero(
            voltage > 0
        )

        first_positive = (
            int(
                positive_frames[0]
            )
            if len(
                positive_frames
            )
            else None
        )

        original_frame = (
            ORIGINAL_ONSETS[
                target
            ]
        )

        original_frame_voltage = float(
            voltage[
                original_frame
            ]
        )

        result[
            "targets"
        ][
            str(target)
        ] = {
            "original_onset_frame":
                original_frame,

            "voltage_at_original_onset":
                original_frame_voltage,

            "original_onset_removed_or_delayed":
                bool(
                    original_frame_voltage
                    <= 0.0
                ),

            "new_first_positive_frame":
                first_positive,

            "maximum_voltage":
                float(
                    voltage.max()
                ),

            "positive_frame_count":
                int(
                    np.count_nonzero(
                        voltage > 0
                    )
                ),

            "integrated_positive_voltage":
                float(
                    np.maximum(
                        voltage,
                        0.0,
                    ).sum()
                ),
        }

    return result


def print_target_table(
    label,
    result,
):
    print()
    print("=" * 88)
    print(label)
    print("=" * 88)

    print(
        "responder ensemble score:",
        result[
            "responder_ensemble_score"
        ],
    )

    for target in TARGETS:
        item = result[
            "targets"
        ][
            str(target)
        ]

        print(
            target,
            "original=",
            item[
                "original_onset_frame"
            ],
            "V@original=",
            item[
                "voltage_at_original_onset"
            ],
            "removed/delayed=",
            item[
                "original_onset_removed_or_delayed"
            ],
            "new_first=",
            item[
                "new_first_positive_frame"
            ],
            "maxV=",
            item[
                "maximum_voltage"
            ],
            "frames+=",
            item[
                "positive_frame_count"
            ],
        )


def main():
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina[
            "neuron_index"
        ],
        dtype=np.int32,
    )

    targeted_edges = (
        load_target_edges()
    )

    sham_edges = derive_sham_edges(
        connectome,
        targeted_edges,
    )

    print("=" * 88)
    print(
        "MQ-3.2 CAUSAL INTERVENTION"
    )
    print("=" * 88)

    print(
        "targeted edge count:",
        len(
            targeted_edges
        ),
    )

    print(
        "sham edge count:",
        len(
            sham_edges
        ),
    )

    print()
    print("TARGETED EDGES")

    for edge in targeted_edges:
        print(
            edge[0],
            "->",
            edge[1],
            "w=",
            edge[2],
        )

    print()
    print("SHAM EDGES")

    for edge in sham_edges:
        print(
            edge[0],
            "->",
            edge[1],
            "w=",
            edge[2],
        )

    targeted_connectome = zero_edges(
        connectome,
        targeted_edges,
    )

    sham_connectome = zero_edges(
        connectome,
        sham_edges,
    )

    print()
    print(
        "running baseline A..."
    )

    baseline_a = run_condition(
        connectome,
        retinal_indices,
        "A",
    )

    print(
        "running targeted A..."
    )

    targeted_a = run_condition(
        targeted_connectome,
        retinal_indices,
        "A",
    )

    print(
        "running sham A..."
    )

    sham_a = run_condition(
        sham_connectome,
        retinal_indices,
        "A",
    )

    print(
        "running targeted neutral..."
    )

    targeted_neutral = run_condition(
        targeted_connectome,
        retinal_indices,
        "neutral",
    )

    print(
        "running targeted B..."
    )

    targeted_b = run_condition(
        targeted_connectome,
        retinal_indices,
        "B",
    )

    print_target_table(
        "BASELINE A",
        baseline_a,
    )

    print_target_table(
        "TARGETED A",
        targeted_a,
    )

    print_target_table(
        "SHAM A",
        sham_a,
    )

    print_target_table(
        "TARGETED NEUTRAL",
        targeted_neutral,
    )

    print_target_table(
        "TARGETED B",
        targeted_b,
    )

    targeted_removed = sum(
        bool(
            targeted_a[
                "targets"
            ][
                str(target)
            ][
                "original_onset_removed_or_delayed"
            ]
        )
        for target in TARGETS
    )

    sham_removed = sum(
        bool(
            sham_a[
                "targets"
            ][
                str(target)
            ][
                "original_onset_removed_or_delayed"
            ]
        )
        for target in TARGETS
    )

    baseline_reproduced = all(
        baseline_a[
            "targets"
        ][
            str(target)
        ][
            "new_first_positive_frame"
        ]
        == ORIGINAL_ONSETS[
            target
        ]
        for target in TARGETS
    )

    neutral_clean = all(
        targeted_neutral[
            "targets"
        ][
            str(target)
        ][
            "new_first_positive_frame"
        ]
        is None
        for target in TARGETS
    )

    b_clean = all(
        targeted_b[
            "targets"
        ][
            str(target)
        ][
            "new_first_positive_frame"
        ]
        is None
        for target in TARGETS
    )

    if (
        targeted_removed == 9
        and sham_removed == 0
    ):
        verdict = (
            "STRONG_CONFIRMATION"
        )

    elif targeted_removed >= 1:
        verdict = (
            "PARTIAL_CONFIRMATION"
        )

    else:
        verdict = (
            "FAILURE"
        )

    output = {
        "experiment":
            "mq3-2-causal-intervention-v1",

        "targeted_edge_artifact":
            str(
                INTERVENTION
            ),

        "targeted_edge_artifact_sha256":
            sha256_file(
                INTERVENTION
            ),

        "targeted_edges": [
            {
                "presynaptic":
                    pre,
                "postsynaptic":
                    post,
                "weight":
                    weight,
            }
            for pre, post, weight
            in targeted_edges
        ],

        "sham_edges": [
            {
                "presynaptic":
                    pre,
                "postsynaptic":
                    post,
                "weight":
                    weight,
            }
            for pre, post, weight
            in sham_edges
        ],

        "runs": {
            "baseline_A":
                baseline_a,

            "targeted_A":
                targeted_a,

            "sham_A":
                sham_a,

            "targeted_neutral":
                targeted_neutral,

            "targeted_B":
                targeted_b,
        },

        "summary": {
            "baseline_reproduced":
                baseline_reproduced,

            "targeted_onsets_removed_or_delayed":
                targeted_removed,

            "sham_onsets_removed_or_delayed":
                sham_removed,

            "targeted_neutral_clean":
                neutral_clean,

            "targeted_B_clean":
                b_clean,

            "verdict":
                verdict,
        },

        "claim_scope":
            (
                "causal necessity within "
                "the frozen MoscaQuant model"
            ),

        "biological_causality_claim":
            False,

        "financial_semantics_used":
            False,
    }

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 88)
    print("INTERVENTION SUMMARY")
    print("=" * 88)

    print(
        "baseline reproduced:",
        baseline_reproduced,
    )

    print(
        "targeted onsets removed/delayed:",
        targeted_removed,
        "/ 9",
    )

    print(
        "sham onsets removed/delayed:",
        sham_removed,
        "/ 9",
    )

    print(
        "targeted neutral clean:",
        neutral_clean,
    )

    print(
        "targeted B clean:",
        b_clean,
    )

    print(
        "verdict:",
        verdict,
    )

    print()
    print(
        "results:",
        OUTPUT,
    )

    print(
        "sha256:",
        sha256_file(
            OUTPUT
        ),
    )

    print()
    print(
        "FINANCIAL SEMANTICS USED: NO"
    )

    print(
        "BIOLOGICAL CAUSALITY CLAIM: NO"
    )

    print(
        "MODEL-LEVEL CAUSAL "
        "INTERVENTION COMPLETE"
    )


if __name__ == "__main__":
    main()
