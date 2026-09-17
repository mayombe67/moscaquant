from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from neuroscope.runtime_profile import (
    PROJECT_ROOT,
    load_runtime_profile,
)


SCHEMA = "mq5-neuroscope-intervention-replay-v1"
DOSES = ("25", "50", "75", "100")


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )


def trace(
    data: np.lib.npyio.NpzFile,
    key: str,
) -> list[float]:
    if key not in data.files:
        raise RuntimeError(
            f"required frozen trace missing: {key}"
        )

    arr = np.asarray(
        data[key],
        dtype=np.float32,
    )

    if arr.shape != (192,):
        raise RuntimeError(
            f"unexpected trace shape for {key}: "
            f"{arr.shape}"
        )

    return [
        float(x)
        for x in arr
    ]


def optional_trace(
    data: np.lib.npyio.NpzFile,
    key: str,
) -> list[float] | None:
    if key not in data.files:
        return None

    return trace(
        data,
        key,
    )


def viewer_lookup(
    replay: dict[str, Any],
) -> dict[int, int]:
    lookup = {}

    for local_index, node in enumerate(
        replay["nodes"]
    ):
        model_index = int(
            node["i"]
        )

        if model_index in lookup:
            raise RuntimeError(
                "duplicate Neuroscope model index: "
                f"{model_index}"
            )

        lookup[model_index] = local_index

    return lookup


def require_viewer_node(
    lookup: dict[int, int],
    model_index: int,
) -> int:
    model_index = int(
        model_index
    )

    if model_index not in lookup:
        raise RuntimeError(
            "MQ-5 node missing from existing "
            f"Neuroscope population: {model_index}"
        )

    return int(
        lookup[model_index]
    )


def generalized_payload(
    source_json: dict[str, Any],
    traces: np.lib.npyio.NpzFile,
    lookup: dict[int, int],
) -> list[dict[str, Any]]:
    output = []

    edges = source_json["edges"]

    if len(edges) != 13:
        raise RuntimeError(
            "expected 13 generalized MQ-5 edges, "
            f"found {len(edges)}"
        )

    for edge in edges:
        source = int(
            edge["source"]
        )
        target = int(
            edge["target"]
        )
        frame = int(
            edge["causal_frame"]
        )

        prefix = (
            f"{source}_to_{target}_F{frame}"
        )

        source_viewer = require_viewer_node(
            lookup,
            source,
        )

        target_viewer = require_viewer_node(
            lookup,
            target,
        )

        doses = {}

        for dose in DOSES:
            doses[dose] = {
                "metrics":
                    edge["doses"][dose],

                "sourceEffectiveTrace":
                    trace(
                        traces,
                        f"{prefix}_dose_{dose}_source",
                    ),

                "targetVoltageTrace":
                    trace(
                        traces,
                        f"{prefix}_dose_{dose}_voltage",
                    ),
            }

        matched = edge[
            "matched_control"
        ]

        matched_payload = {
            "available":
                bool(
                    matched["available"]
                ),

            "modelIndex":
                matched["model_index"],

            "viewerIndex":
                None,

            "baselineControlActivityAtCausalFrame":
                matched[
                    "baseline_control_activity_at_causal_frame"
                ],

            "metrics":
                matched["metrics"],

            "targetVoltageTrace":
                None,
        }

        if matched["available"]:
            control_model = int(
                matched["model_index"]
            )

            matched_payload[
                "viewerIndex"
            ] = require_viewer_node(
                lookup,
                control_model,
            )

            matched_payload[
                "targetVoltageTrace"
            ] = trace(
                traces,
                f"{prefix}_matched_voltage",
            )

        timing = edge[
            "timing_control"
        ]

        timing_payload = {
            "available":
                bool(
                    timing["available"]
                ),

            "frame":
                timing["frame"],

            "baselineSourceActivityAtControlFrame":
                timing[
                    "baseline_source_activity_at_control_frame"
                ],

            "metrics":
                timing["metrics"],

            "targetVoltageTrace":
                None,
        }

        if timing["available"]:
            timing_payload[
                "targetVoltageTrace"
            ] = trace(
                traces,
                f"{prefix}_timing_voltage",
            )

        output.append(
            {
                "id":
                    prefix,

                "source":
                    source,

                "sourceViewerIndex":
                    source_viewer,

                "target":
                    target,

                "targetViewerIndex":
                    target_viewer,

                "causalFrame":
                    frame,

                "observedFrames":
                    [
                        int(x)
                        for x
                        in edge[
                            "observed_frames"
                        ]
                    ],

                "frozenWeight":
                    float(
                        edge["frozen_weight"]
                    ),

                "baselineSourceEffectiveAtCausalFrame":
                    float(
                        edge[
                            "baseline_source_effective_at_causal_frame"
                        ]
                    ),

                "baselineMetrics":
                    edge["baseline"],

                "baselineSourceEffectiveTrace":
                    trace(
                        traces,
                        f"{prefix}_baseline_source",
                    ),

                "baselineTargetVoltageTrace":
                    trace(
                        traces,
                        f"{prefix}_baseline_voltage",
                    ),

                "shamMetrics":
                    edge["sham"],

                "shamTargetVoltageTrace":
                    trace(
                        traces,
                        f"{prefix}_sham_voltage",
                    ),

                "doses":
                    doses,

                "timingControl":
                    timing_payload,

                "matchedControl":
                    matched_payload,

                "validation":
                    edge["validation"],
            }
        )

    return output


def pathway_payload(
    source_json: dict[str, Any],
    traces: np.lib.npyio.NpzFile,
    lookup: dict[int, int],
) -> dict[str, Any]:
    path = source_json["path"]

    upstream = int(
        path["upstream"]
    )
    intermediate = int(
        path["intermediate"]
    )
    downstream = int(
        path["downstream"]
    )

    upstream_frame = int(
        path["upstream_causal_frame"]
    )
    intermediate_frame = int(
        path["intermediate_causal_frame"]
    )

    upstream_doses = {}
    intermediate_doses = {}

    for dose in DOSES:
        upstream_doses[dose] = {
            "metrics":
                source_json[
                    "upstream_interventions"
                ][dose],

            "upstreamEffectiveTrace":
                trace(
                    traces,
                    f"upstream_{dose}_upstream_effective",
                ),

            "intermediateVoltageTrace":
                trace(
                    traces,
                    f"upstream_{dose}_intermediate_voltage",
                ),

            "intermediateEffectiveTrace":
                trace(
                    traces,
                    f"upstream_{dose}_intermediate_effective",
                ),

            "downstreamVoltageTrace":
                trace(
                    traces,
                    f"upstream_{dose}_downstream_voltage",
                ),
        }

        intermediate_doses[dose] = {
            "metrics":
                source_json[
                    "intermediate_interventions"
                ][dose],

            "intermediateEffectiveTrace":
                trace(
                    traces,
                    f"intermediate_{dose}_intermediate_effective",
                ),

            "downstreamVoltageTrace":
                trace(
                    traces,
                    f"intermediate_{dose}_downstream_voltage",
                ),

            # Not recorded in frozen artifact.
            "intermediateVoltageTrace":
                None,
        }

    return {
        "id":
            "56393_to_68045_to_1273",

        "upstream":
            upstream,

        "upstreamViewerIndex":
            require_viewer_node(
                lookup,
                upstream,
            ),

        "intermediate":
            intermediate,

        "intermediateViewerIndex":
            require_viewer_node(
                lookup,
                intermediate,
            ),

        "downstream":
            downstream,

        "downstreamViewerIndex":
            require_viewer_node(
                lookup,
                downstream,
            ),

        "upstreamCausalFrame":
            upstream_frame,

        "intermediateCausalFrame":
            intermediate_frame,

        "baseline":
            source_json["baseline"],

        "baselineTraces": {
            "upstreamEffective":
                trace(
                    traces,
                    "baseline_upstream_effective",
                ),

            "intermediateVoltage":
                trace(
                    traces,
                    "baseline_intermediate_voltage",
                ),

            "intermediateEffective":
                trace(
                    traces,
                    "baseline_intermediate_effective",
                ),

            "downstreamVoltage":
                trace(
                    traces,
                    "baseline_downstream_voltage",
                ),
        },

        "upstreamInterventions":
            upstream_doses,

        "intermediateInterventions":
            intermediate_doses,

        "validation":
            source_json["validation"],
    }


def convergence_payload(
    source_json: dict[str, Any],
    traces: np.lib.npyio.NpzFile,
    lookup: dict[int, int],
) -> list[dict[str, Any]]:
    systems = source_json["systems"]

    if len(systems) != 3:
        raise RuntimeError(
            "expected 3 convergence systems, "
            f"found {len(systems)}"
        )

    output = []

    for system in systems:
        target = int(
            system["target"]
        )
        a = int(
            system["input_a"]
        )
        b = int(
            system["input_b"]
        )

        doses = {}

        for dose in DOSES:
            dose_data = system[
                "doses"
            ][dose]

            doses[dose] = {
                # Frozen completed result object.
                "result":
                    dose_data,

                "aOnlyTargetVoltageTrace":
                    trace(
                        traces,
                        f"target_{target}_dose_{dose}_a_voltage",
                    ),

                "bOnlyTargetVoltageTrace":
                    trace(
                        traces,
                        f"target_{target}_dose_{dose}_b_voltage",
                    ),

                "combinedTargetVoltageTrace":
                    trace(
                        traces,
                        f"target_{target}_dose_{dose}_ab_voltage",
                    ),
            }

        output.append(
            {
                "id":
                    f"{a}_plus_{b}_to_{target}",

                "inputA":
                    a,

                "inputAViewerIndex":
                    require_viewer_node(
                        lookup,
                        a,
                    ),

                "inputB":
                    b,

                "inputBViewerIndex":
                    require_viewer_node(
                        lookup,
                        b,
                    ),

                "target":
                    target,

                "targetViewerIndex":
                    require_viewer_node(
                        lookup,
                        target,
                    ),

                "causalFrameA":
                    int(
                        system[
                            "causal_frame_a"
                        ]
                    ),

                "causalFrameB":
                    int(
                        system[
                            "causal_frame_b"
                        ]
                    ),

                "baseline":
                    system["baseline"],

                "baselineTraces": {
                    "inputAEffective":
                        trace(
                            traces,
                            f"target_{target}_baseline_a_effective",
                        ),

                    "inputBEffective":
                        trace(
                            traces,
                            f"target_{target}_baseline_b_effective",
                        ),

                    "targetVoltage":
                        trace(
                            traces,
                            f"target_{target}_baseline_voltage",
                        ),
                },

                "doses":
                    doses,

                "combinedDoseMonotonic":
                    bool(
                        system[
                            "combined_dose_monotonic"
                        ]
                    ),

                "validation":
                    system["validation"],

                "numericalScaleWarning":
                    (
                        "Responder 51 effects are at "
                        "extremely small numerical scale; "
                        "interpret magnitude cautiously."
                        if target == 51
                        else None
                    ),

                "interactionClaim":
                    (
                        "No statistical synergy, antagonism, "
                        "subadditivity, or superadditivity "
                        "classification assigned."
                    ),
            }
        )

    return output


def main() -> None:
    profile = load_runtime_profile()

    experiments = (
        profile.data_dir
        / "experiments"
    )

    base_replay_path = (
        PROJECT_ROOT
        / "neuroscope"
        / "web"
        / "data"
        / "replay-A-v1.json"
    )

    generalized_json_path = (
        experiments
        / "mq5-generalized-intervention-matrix-v1.json"
    )

    generalized_npz_path = (
        experiments
        / "mq5-generalized-intervention-matrix-v1.npz"
    )

    pathway_json_path = (
        experiments
        / "mq5-4-pathway-56393-68045-1273-v1.json"
    )

    pathway_npz_path = (
        experiments
        / "mq5-4-pathway-56393-68045-1273-v1.npz"
    )

    convergence_json_path = (
        experiments
        / "mq5-5-convergence-specificity-v1.json"
    )

    convergence_npz_path = (
        experiments
        / "mq5-5-convergence-specificity-v1.npz"
    )

    robustness_path = (
        experiments
        / "conf-004a-generalized-intervention-matrix-v1.json"
    )

    replication_path = (
        experiments
        / "mq5-6-replication-stability-v1.json"
    )

    protocol_path = (
        PROJECT_ROOT
        / "docs"
        / "experiments"
        / "mq5-7-neuroscope-intervention-replay-protocol.md"
    )

    config_path = (
        PROJECT_ROOT
        / "config"
        / "controls"
        / "mq5-7-neuroscope-intervention-replay-v1.toml"
    )

    output_path = (
        PROJECT_ROOT
        / "neuroscope"
        / "web"
        / "data"
        / "mq5-interventions-v1.json"
    )

    source_paths = [
        base_replay_path,
        generalized_json_path,
        generalized_npz_path,
        pathway_json_path,
        pathway_npz_path,
        convergence_json_path,
        convergence_npz_path,
        robustness_path,
        replication_path,
        protocol_path,
        config_path,
    ]

    for path in source_paths:
        if not path.exists():
            raise RuntimeError(
                f"required source artifact missing: {path}"
            )

    hashes_before = {
        str(path):
            sha256(path)
        for path
        in source_paths
    }

    base_replay = load_json(
        base_replay_path
    )

    lookup = viewer_lookup(
        base_replay
    )

    generalized_json = load_json(
        generalized_json_path
    )

    pathway_json = load_json(
        pathway_json_path
    )

    convergence_json = load_json(
        convergence_json_path
    )

    robustness_json = load_json(
        robustness_path
    )

    replication_json = load_json(
        replication_path
    )

    with (
        np.load(
            generalized_npz_path,
            allow_pickle=False,
        ) as generalized_npz,

        np.load(
            pathway_npz_path,
            allow_pickle=False,
        ) as pathway_npz,

        np.load(
            convergence_npz_path,
            allow_pickle=False,
        ) as convergence_npz,
    ):
        generalized = generalized_payload(
            generalized_json,
            generalized_npz,
            lookup,
        )

        pathway = pathway_payload(
            pathway_json,
            pathway_npz,
            lookup,
        )

        convergence = convergence_payload(
            convergence_json,
            convergence_npz,
            lookup,
        )

    payload = {
        "schema":
            SCHEMA,

        "phase":
            "MQ-5.7",

        "classification":
            "visualization-replay",

        "readOnly":
            True,

        "simulationFeedback":
            False,

        "generatesScientificOutcomes":
            False,

        "frameCount":
            int(
                base_replay["frameCount"]
            ),

        "baseReplay": {
            "artifact":
                base_replay_path.name,

            "schema":
                base_replay["schema"],

            "populationCount":
                int(
                    base_replay[
                        "populationCount"
                    ]
                ),

            "geometry":
                base_replay[
                    "geometry"
                ],
        },

        "sourceArtifacts": {
            str(path):
                hashes_before[
                    str(path)
                ]
            for path
            in source_paths
        },

        "generalized": {
            "artifactClassification":
                generalized_json[
                    "classification"
                ],

            "interpretationStatus":
                generalized_json[
                    "interpretation_status"
                ],

            "softwareCommit":
                generalized_json[
                    "software_commit"
                ],

            "attenuationLevels":
                generalized_json[
                    "attenuation_levels"
                ],

            "validation":
                generalized_json[
                    "validation"
                ],

            "edges":
                generalized,
        },

        "pathway": {
            "artifactClassification":
                pathway_json[
                    "classification"
                ],

            "interpretationStatus":
                pathway_json[
                    "interpretation_status"
                ],

            "softwareCommit":
                pathway_json[
                    "software_commit"
                ],

            "replay":
                pathway,
        },

        "convergence": {
            "artifactClassification":
                convergence_json[
                    "classification"
                ],

            "interpretation":
                convergence_json[
                    "interpretation"
                ],

            "softwareCommit":
                convergence_json[
                    "software_commit"
                ],

            "attenuationLevels":
                convergence_json[
                    "attenuation_levels"
                ],

            "validation":
                convergence_json[
                    "validation"
                ],

            "systems":
                convergence,
        },

        "robustness": {
            "conf004a": {
                "experimentId":
                    robustness_json[
                        "experiment_id"
                    ],

                "classification":
                    robustness_json[
                        "classification"
                    ],

                "softwareCommit":
                    robustness_json[
                        "software_commit"
                    ],

                "encoder":
                    robustness_json[
                        "encoder"
                    ],

                "test":
                    robustness_json[
                        "robustness_test"
                    ],

                "validation":
                    robustness_json[
                        "validation"
                    ],

                "biologicalCausalityClaim":
                    bool(
                        robustness_json[
                            "biological_causality_claim"
                        ]
                    ),

                "financialSemanticsUsed":
                    bool(
                        robustness_json[
                            "financial_semantics_used"
                        ]
                    ),
            },

            "mq56IndependentReplication": {
                "experimentId":
                    replication_json[
                        "experiment_id"
                    ],

                "classification":
                    replication_json[
                        "classification"
                    ],

                "softwareCommit":
                    replication_json[
                        "software_commit"
                    ],

                "implementation":
                    replication_json[
                        "implementation"
                    ],

                "tolerance":
                    replication_json[
                        "tolerance"
                    ],

                "validation":
                    replication_json[
                        "validation"
                    ],

                "biologicalCausalityClaim":
                    bool(
                        replication_json[
                            "biological_causality_claim"
                        ]
                    ),

                "financialSemanticsUsed":
                    bool(
                        replication_json[
                            "financial_semantics_used"
                        ]
                    ),
            },
        },

        "claimBoundary": {
            "biologicalCausalityClaim":
                False,

            "financialSemantics":
                "NOT ASSIGNED",

            "viewerAddsEvidence":
                False,

            "statement":
                (
                    "Neuroscope displays completed frozen "
                    "MQ-5 evidence. Visualization does not "
                    "create additional causal evidence."
                ),
        },
    }

    hashes_after = {
        str(path):
            sha256(path)
        for path
        in source_paths
    }

    if hashes_before != hashes_after:
        raise RuntimeError(
            "source artifact changed during MQ-5.7 export"
        )

    encoded = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path.exists():
        existing = output_path.read_text(
            encoding="utf-8",
        )

        if existing != encoded:
            raise RuntimeError(
                "MQ-5.7 output already exists with "
                "different contents; refusing overwrite"
            )

        print(
            "MQ-5.7 artifact already current:"
        )
        print(
            output_path
        )

    else:
        output_path.write_text(
            encoded,
            encoding="utf-8",
        )

        print(
            "MQ-5.7 artifact written:"
        )
        print(
            output_path
        )

    print()
    print(
        "generalized edges:",
        len(
            payload[
                "generalized"
            ]["edges"]
        ),
    )

    print(
        "pathway:",
        (
            f"{pathway['upstream']} -> "
            f"{pathway['intermediate']} -> "
            f"{pathway['downstream']}"
        ),
    )

    print(
        "convergence systems:",
        len(
            payload[
                "convergence"
            ]["systems"]
        ),
    )

    print(
        "readOnly:",
        payload["readOnly"],
    )

    print(
        "simulationFeedback:",
        payload[
            "simulationFeedback"
        ],
    )

    print(
        "source artifacts unchanged:",
        hashes_before == hashes_after,
    )


if __name__ == "__main__":
    main()
