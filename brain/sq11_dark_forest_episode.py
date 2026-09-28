from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)

from brain.visual_transduction import (
    VisualTransductionConfig,
)

from brain.sq10_sophon_episode import (
    BODY_RESPONDERS,
    BODY_SOURCES,
    FRAME_COUNT,
    GRADED,
    RELAY,
    RELEASE_GAIN,
    assert_frozen_stimulus,
    body_edge_weights,
    build_body_lesion,
    build_stimuli,
)

from brain.sq11_dark_forest_instrumentation import (
    DarkForestPhaseRecorder,
    build_body_row_geometry,
)

from brain.sq11_dark_forest_plan import (
    MASKS,
)

from brain.sq11_dark_forest_replay_v2 import (
    replay_csr_rows_float32,
)


ROOT = Path(__file__).resolve().parents[1]

INSTRUMENTATION = (
    ROOT
    / "brain"
    / "sq11_dark_forest_instrumentation.py"
)

REPLAY_V2 = (
    ROOT
    / "brain"
    / "sq11_dark_forest_replay_v2.py"
)

QUALIFICATION_V2 = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-replay-qualification-v2.json"
)

QUALIFICATION_SEAL_V2 = (
    ROOT
    / "config/controls/"
    "sq11-dark-forest-replay-qualification-seal-v2.json"
)

EXPECTED_INSTRUMENTATION_SHA256 = (
    "0051e2d240e6ca494b3bd766998ccb837"
    "4a0f678f8c723387e8891cec6aacc1f"
)

EXPECTED_REPLAY_V2_SHA256 = (
    "76245bfab248c0d4bf374da94ad79485"
    "f2e0e386d86707de9e52bad26ff772e5"
)

EXPECTED_QUALIFICATION_V2_SHA256 = (
    "a2b4256529ef5c7002fc32e9cd4c8779"
    "18d320fd736fa7961ba66f869d70e325"
)

EXPECTED_QUALIFICATION_SEAL_V2_SHA256 = (
    "19529383757e243f9881140edca30b13a"
    "ea10760b582dd2fb1cda09198f225ab"
)

BODY_PAIR_COUNT = 3
PRESYNAPTIC_UNION_COUNT = 4393
FLAT_ENTRY_COUNT = 4568

ROW_OFFSETS = np.asarray(
    [0, 2830, 3671, 4568],
    dtype=np.int64,
)

BODY_POSITIONS = np.asarray(
    [1908, 671, 767],
    dtype=np.int64,
)

BODY_FLAT_POSITIONS = np.asarray(
    [1908, 3501, 4438],
    dtype=np.int64,
)


class Refusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise Refusal(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                8 * 1024 * 1024
            ),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def verify_frozen_dependencies() -> None:
    expected = (
        (
            INSTRUMENTATION,
            EXPECTED_INSTRUMENTATION_SHA256,
        ),
        (
            REPLAY_V2,
            EXPECTED_REPLAY_V2_SHA256,
        ),
        (
            QUALIFICATION_V2,
            EXPECTED_QUALIFICATION_V2_SHA256,
        ),
        (
            QUALIFICATION_SEAL_V2,
            EXPECTED_QUALIFICATION_SEAL_V2_SHA256,
        ),
    )

    for path, wanted in expected:
        if not path.is_file():
            refuse(
                f"SQ-11 dependency missing: {path}"
            )

        actual = sha256_file(path)

        if actual != wanted:
            refuse(
                "SQ-11 dependency SHA drift: "
                f"{path}: {actual} != {wanted}"
            )


def condition_edge_zeroed(
    mask: str,
) -> np.ndarray:
    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-11 mask: {mask!r}"
        )

    return np.asarray(
        [int(bit) for bit in mask],
        dtype=np.uint8,
    )


def baseline_geometry(
    baseline: sparse.csr_matrix,
) -> dict[str, np.ndarray]:
    if not sparse.isspmatrix_csr(
        baseline
    ):
        raise TypeError(
            "SQ-11 baseline must be CSR"
        )

    if baseline.dtype != np.dtype(
        np.float32
    ):
        raise TypeError(
            "SQ-11 baseline must be float32"
        )

    geometry = build_body_row_geometry(
        connectome=baseline,
        responder_indices=BODY_RESPONDERS,
        source_indices=BODY_SOURCES,
    )

    if not np.array_equal(
        geometry["row_offsets"],
        ROW_OFFSETS,
    ):
        refuse(
            "SQ-11 row-offset drift"
        )

    if not np.array_equal(
        geometry["body_positions"],
        BODY_POSITIONS,
    ):
        refuse(
            "SQ-11 BODY-position drift"
        )

    if not np.array_equal(
        geometry["body_flat_positions"],
        BODY_FLAT_POSITIONS,
    ):
        refuse(
            "SQ-11 BODY-flat-position drift"
        )

    if len(
        geometry["row_indices"]
    ) != FLAT_ENTRY_COUNT:
        refuse(
            "SQ-11 flat-entry count drift"
        )

    if len(
        geometry[
            "presynaptic_union_indices"
        ]
    ) != PRESYNAPTIC_UNION_COUNT:
        refuse(
            "SQ-11 presynaptic-union count drift"
        )

    observed_weights = (
        geometry["row_weights"][
            geometry[
                "body_flat_positions"
            ]
        ]
    )

    expected_weights = (
        body_edge_weights()
    )

    if not np.array_equal(
        observed_weights,
        expected_weights,
    ):
        refuse(
            "SQ-11 BODY edge-weight drift"
        )

    return geometry


DYNAMIC_KEYS = (
    "local_effective_activity_pre_synaptic",
    "source_voltage_pre_step",
    "source_spikes_pre_step",
    "source_effective_activity_pre_synaptic",
    "responder_synaptic_p3",
    "responder_voltage_pre_threshold",
    "responder_fired",
    "responder_voltage_post_reset",
    "responder_spikes_post_commit",
)

STATIC_KEYS = (
    "row_offsets",
    "row_indices",
    "row_weights",
    "body_positions",
    "body_flat_positions",
    "presynaptic_union_indices",
    "row_union_positions",
    "body_edge_weight",
)

RESULT_KEYS = (
    *DYNAMIC_KEYS,
    *STATIC_KEYS,
    "condition_edge_zeroed",
)


def expected_result_contract():
    frame3 = (
        FRAME_COUNT,
        BODY_PAIR_COUNT,
    )

    return {
        "local_effective_activity_pre_synaptic":
            (
                (
                    FRAME_COUNT,
                    PRESYNAPTIC_UNION_COUNT,
                ),
                np.dtype(np.float32),
            ),

        "source_voltage_pre_step":
            (
                frame3,
                np.dtype(np.float32),
            ),

        "source_spikes_pre_step":
            (
                frame3,
                np.dtype(np.uint8),
            ),

        "source_effective_activity_pre_synaptic":
            (
                frame3,
                np.dtype(np.float32),
            ),

        "responder_synaptic_p3":
            (
                frame3,
                np.dtype(np.float32),
            ),

        "responder_voltage_pre_threshold":
            (
                frame3,
                np.dtype(np.float32),
            ),

        "responder_fired":
            (
                frame3,
                np.dtype(np.uint8),
            ),

        "responder_voltage_post_reset":
            (
                frame3,
                np.dtype(np.float32),
            ),

        "responder_spikes_post_commit":
            (
                frame3,
                np.dtype(np.uint8),
            ),

        "row_offsets":
            (
                (4,),
                np.dtype(np.int64),
            ),

        "row_indices":
            (
                (FLAT_ENTRY_COUNT,),
                np.dtype(np.int64),
            ),

        "row_weights":
            (
                (FLAT_ENTRY_COUNT,),
                np.dtype(np.float32),
            ),

        "body_positions":
            (
                (BODY_PAIR_COUNT,),
                np.dtype(np.int64),
            ),

        "body_flat_positions":
            (
                (BODY_PAIR_COUNT,),
                np.dtype(np.int64),
            ),

        "presynaptic_union_indices":
            (
                (PRESYNAPTIC_UNION_COUNT,),
                np.dtype(np.int64),
            ),

        "row_union_positions":
            (
                (FLAT_ENTRY_COUNT,),
                np.dtype(np.int64),
            ),

        "body_edge_weight":
            (
                (BODY_PAIR_COUNT,),
                np.dtype(np.float32),
            ),

        "condition_edge_zeroed":
            (
                (BODY_PAIR_COUNT,),
                np.dtype(np.uint8),
            ),
    }


def verify_runtime_replay(
    result: dict[str, np.ndarray],
) -> None:
    zeroed = np.repeat(
        result[
            "condition_edge_zeroed"
        ][None, :],
        FRAME_COUNT,
        axis=0,
    ).astype(
        np.uint8,
        copy=False,
    )

    replay = replay_csr_rows_float32(
        local_activity=
            result[
                "local_effective_activity_pre_synaptic"
            ],

        row_offsets=
            result["row_offsets"],

        row_weights=
            result["row_weights"],

        row_union_positions=
            result[
                "row_union_positions"
            ],

        body_flat_positions=
            result[
                "body_flat_positions"
            ],

        condition_edge_zeroed=
            zeroed,
    )

    observed = result[
        "responder_synaptic_p3"
    ]

    if np.array_equal(
        replay,
        observed,
    ):
        return

    mismatches = np.argwhere(
        replay != observed
    )

    frame = int(
        mismatches[0, 0]
    )

    body = int(
        mismatches[0, 1]
    )

    refuse(
        "SQ-11 exact P3 replay mismatch: "
        f"frame={frame}, body={body}, "
        f"replay={replay[frame, body]!r}, "
        f"runtime={observed[frame, body]!r}"
    )


def validate_result(
    result: dict,
    *,
    mask: str,
) -> None:
    if set(result) != set(
        RESULT_KEYS
    ):
        refuse(
            "SQ-11 episode result key-set drift"
        )

    for key, (
        expected_shape,
        expected_dtype,
    ) in expected_result_contract().items():
        value = result[key]

        if not isinstance(
            value,
            np.ndarray,
        ):
            refuse(
                f"SQ-11 result not ndarray: {key}"
            )

        if value.shape != expected_shape:
            refuse(
                f"SQ-11 shape drift {key}: "
                f"{value.shape} != "
                f"{expected_shape}"
            )

        if value.dtype != expected_dtype:
            refuse(
                f"SQ-11 dtype drift {key}: "
                f"{value.dtype} != "
                f"{expected_dtype}"
            )

        if (
            np.issubdtype(
                value.dtype,
                np.floating,
            )
            and not np.all(
                np.isfinite(value)
            )
        ):
            refuse(
                f"SQ-11 non-finite result: {key}"
            )

    if not np.array_equal(
        result["row_offsets"],
        ROW_OFFSETS,
    ):
        refuse(
            "SQ-11 stored row-offset drift"
        )

    if not np.array_equal(
        result["body_positions"],
        BODY_POSITIONS,
    ):
        refuse(
            "SQ-11 stored BODY-position drift"
        )

    if not np.array_equal(
        result["body_flat_positions"],
        BODY_FLAT_POSITIONS,
    ):
        refuse(
            "SQ-11 stored BODY-flat-position drift"
        )

    union = result[
        "presynaptic_union_indices"
    ]

    if np.any(
        union[1:] <= union[:-1]
    ):
        refuse(
            "SQ-11 presynaptic union "
            "must be strictly increasing"
        )

    mapping = result[
        "row_union_positions"
    ]

    if np.any(mapping < 0):
        refuse(
            "SQ-11 negative row-union position"
        )

    if np.any(
        mapping >= len(union)
    ):
        refuse(
            "SQ-11 row-union position "
            "outside union"
        )

    if not np.array_equal(
        union[mapping],
        result["row_indices"],
    ):
        refuse(
            "SQ-11 row/union round-trip failure"
        )

    if not np.array_equal(
        result["row_indices"][
            BODY_FLAT_POSITIONS
        ],
        BODY_SOURCES,
    ):
        refuse(
            "SQ-11 BODY source-location drift"
        )

    if not np.array_equal(
        result["row_weights"][
            BODY_FLAT_POSITIONS
        ],
        result["body_edge_weight"],
    ):
        refuse(
            "SQ-11 BODY weight-location drift"
        )

    expected_zeroed = (
        condition_edge_zeroed(mask)
    )

    if not np.array_equal(
        result[
            "condition_edge_zeroed"
        ],
        expected_zeroed,
    ):
        refuse(
            "SQ-11 lesion-mask drift"
        )

    for key in (
        "source_spikes_pre_step",
        "responder_fired",
        "responder_spikes_post_commit",
        "condition_edge_zeroed",
    ):
        value = result[key]

        if np.any(
            (value != 0)
            & (value != 1)
        ):
            refuse(
                f"SQ-11 non-binary field: {key}"
            )

    #
    # The compact BODY-source P2 readout and
    # the same coordinates inside the complete
    # local P2 union must agree exactly.
    #
    source_union_positions = np.searchsorted(
        union,
        BODY_SOURCES,
    )

    if not np.array_equal(
        union[source_union_positions],
        BODY_SOURCES,
    ):
        refuse(
            "SQ-11 BODY sources missing "
            "from presynaptic union"
        )

    if not np.array_equal(
        result[
            "local_effective_activity_pre_synaptic"
        ][
            :,
            source_union_positions,
        ],
        result[
            "source_effective_activity_pre_synaptic"
        ],
    ):
        refuse(
            "SQ-11 BODY-source P2 "
            "cross-readout mismatch"
        )

    #
    # Critical DARK FOREST gate:
    # the lesion-aware local replay must
    # reproduce runtime P3 exactly.
    #
    verify_runtime_replay(
        result
    )


def run_dark_forest_episode(
    *,
    connectome: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    stimuli: tuple[np.ndarray, ...],
    mask: str,
    geometry: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    verify_frozen_dependencies()

    if mask not in MASKS:
        raise ValueError(
            f"invalid SQ-11 mask: {mask!r}"
        )

    if len(stimuli) != FRAME_COUNT:
        raise ValueError(
            "SQ-11 episode must contain "
            "exactly 192 frames"
        )

    if not sparse.isspmatrix_csr(
        connectome
    ):
        raise TypeError(
            "SQ-11 candidate connectome must be CSR"
        )

    if connectome.dtype != np.dtype(
        np.float32
    ):
        raise TypeError(
            "SQ-11 candidate connectome "
            "must be float32"
        )

    zeroed = (
        condition_edge_zeroed(mask)
    )

    recorder = DarkForestPhaseRecorder(
        source_indices=
            BODY_SOURCES,

        responder_indices=
            BODY_RESPONDERS,

        presynaptic_union_indices=
            geometry[
                "presynaptic_union_indices"
            ],
    )

    runtime = (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=
                connectome.tocsr(
                    copy=False
                ),

            retinal_indices=
                np.asarray(
                    retinal_indices,
                    dtype=np.int32,
                ),

            relay_artifact=
                RELAY,

            graded_artifact=
                GRADED,

            config=
                VisualTransductionConfig(
                    release_gain=
                        RELEASE_GAIN
                ),

            synaptic_modifier=
                recorder,
        )
    )

    for stimulus in stimuli:
        recorder.before_step(
            runtime,
            stimulus,
        )

        runtime.step(
            stimulus
        )

        recorder.after_step(
            runtime
        )

    result = recorder.arrays()

    for key in (
        "row_offsets",
        "row_indices",
        "row_weights",
        "body_positions",
        "body_flat_positions",
        "presynaptic_union_indices",
        "row_union_positions",
    ):
        result[key] = (
            geometry[key].copy()
        )

    result[
        "body_edge_weight"
    ] = np.asarray(
        geometry[
            "row_weights"
        ][
            geometry[
                "body_flat_positions"
            ]
        ],
        dtype=np.float32,
    ).copy()

    result[
        "condition_edge_zeroed"
    ] = zeroed.copy()

    validate_result(
        result,
        mask=mask,
    )

    return result


def execute_condition(
    *,
    baseline: sparse.csr_matrix,
    retinal_indices: np.ndarray,
    condition: dict,
) -> dict:
    #
    # Dependency closure is checked before
    # touching the neural runtime.
    #
    verify_frozen_dependencies()

    from brain.sq11_dark_forest_plan import (
        validate_condition,
    )

    canonical = validate_condition(
        condition
    )

    geometry = baseline_geometry(
        baseline
    )

    candidate, topology_provenance = (
        build_body_lesion(
            baseline,
            canonical["mask"],
        )
    )

    #
    # DARK FOREST inherits exactly the same
    # frozen RL stimulus used by SQ-10/SQ-08.
    #
    stimuli = build_stimuli(
        "RL"
    )

    assert_frozen_stimulus()

    result = run_dark_forest_episode(
        connectome=candidate,
        retinal_indices=
            retinal_indices,
        stimuli=stimuli,
        mask=canonical["mask"],
        geometry=geometry,
    )

    return {
        "condition":
            canonical,

        "topology_provenance":
            topology_provenance,

        "result":
            result,

        #
        # This adapter does not grant authority.
        #
        "execution_authorized_here":
            False,
    }


def duplicate_pair_exact(
    first: dict,
    second: dict,
) -> bool:
    from brain.sq11_dark_forest_plan import (
        validate_condition,
    )

    a = validate_condition(
        first["condition"]
    )

    b = validate_condition(
        second["condition"]
    )

    if a["mask"] != b["mask"]:
        return False

    if {
        a["replicate"],
        b["replicate"],
    } != {1, 2}:
        return False

    if (
        first.get(
            "execution_authorized_here"
        )
        is not False
    ):
        return False

    if (
        second.get(
            "execution_authorized_here"
        )
        is not False
    ):
        return False

    validate_result(
        first["result"],
        mask=a["mask"],
    )

    validate_result(
        second["result"],
        mask=b["mask"],
    )

    return all(
        np.array_equal(
            first["result"][key],
            second["result"][key],
        )
        for key in RESULT_KEYS
    )
