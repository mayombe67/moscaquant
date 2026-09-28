from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.sq11_dark_forest_instrumentation import (
    EXPECTED_SOPHON_INSTRUMENTATION_SHA256,
    DarkForestPhaseRecorder,
    build_body_row_geometry,
    verify_sophon_instrumentation,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


POPULATION = 6000

SOURCES = np.asarray(
    [5000, 5001, 5002],
    dtype=np.int64,
)

RESPONDERS = np.asarray(
    [5500, 5501, 5502],
    dtype=np.int64,
)

EXTRA_SOURCES = np.asarray(
    [5100, 5101, 5102],
    dtype=np.int64,
)

RETINA = np.asarray(
    [5999],
    dtype=np.int32,
)


def make_artifacts(
    tmp_path: Path,
):
    relay = (
        tmp_path
        / "relay.npz"
    )

    graded = (
        tmp_path
        / "graded.npz"
    )

    relay_indices = np.arange(
        2430,
        dtype=np.int32,
    )

    np.savez(
        relay,
        neuron_index=
            relay_indices,
        body_id=
            relay_indices.astype(
                np.int64
            ),
        type=np.asarray(
            ["relay"] * 2430
        ),
    )

    graded_indices = np.arange(
        5490,
        dtype=np.int32,
    )

    graded_types = np.empty(
        5490,
        dtype="<U3",
    )

    graded_types[0::3] = "Tm2"
    graded_types[1::3] = "Tm3"
    graded_types[2::3] = "Tm4"

    np.savez(
        graded,
        neuron_index=
            graded_indices,
        type=
            graded_types,
    )

    return relay, graded


def make_connectome():
    matrix = sparse.lil_matrix(
        (
            POPULATION,
            POPULATION,
        ),
        dtype=np.float32,
    )

    #
    # Two presynaptic contributors per
    # BODY responder make the local-state
    # test nontrivial.
    #
    matrix[
        RESPONDERS[0],
        EXTRA_SOURCES[0],
    ] = np.float32(0.125)

    matrix[
        RESPONDERS[0],
        SOURCES[0],
    ] = np.float32(0.25)

    matrix[
        RESPONDERS[1],
        EXTRA_SOURCES[1],
    ] = np.float32(0.375)

    matrix[
        RESPONDERS[1],
        SOURCES[1],
    ] = np.float32(1.5)

    matrix[
        RESPONDERS[2],
        EXTRA_SOURCES[2],
    ] = np.float32(0.625)

    matrix[
        RESPONDERS[2],
        SOURCES[2],
    ] = np.float32(0.5)

    return matrix.tocsr()


def make_runtime(
    *,
    relay,
    graded,
    modifier=None,
):
    return (
        PhysiologyConstrainedVisualTransductionRuntime(
            connectome=
                make_connectome(),
            retinal_indices=
                RETINA,
            relay_artifact=
                relay,
            graded_artifact=
                graded,
            config=
                VisualTransductionConfig(),
            synaptic_modifier=
                modifier,
        )
    )


def initialize_state(
    runtime,
):
    runtime.voltage[
        SOURCES
    ] = np.asarray(
        [0.4, 0.8, 0.6],
        dtype=np.float32,
    )

    runtime.voltage[
        EXTRA_SOURCES
    ] = np.asarray(
        [0.2, 0.3, 0.7],
        dtype=np.float32,
    )

    runtime.voltage[
        RESPONDERS
    ] = np.asarray(
        [0.1, 0.2, 0.3],
        dtype=np.float32,
    )


def stimulus_for_frame(
    frame: int,
):
    stimulus = np.zeros(
        POPULATION,
        dtype=np.float32,
    )

    if frame == 3:
        stimulus[
            SOURCES[0]
        ] = np.float32(0.15)

    if frame == 7:
        stimulus[
            EXTRA_SOURCES[2]
        ] = np.float32(0.2)

    if frame == 11:
        stimulus[
            RESPONDERS[0]
        ] = np.float32(0.1)

    return stimulus


def geometry():
    return build_body_row_geometry(
        connectome=
            make_connectome(),
        responder_indices=
            RESPONDERS,
        source_indices=
            SOURCES,
    )


def test_sophon_instrumentation_dependency_is_exact():
    assert (
        verify_sophon_instrumentation()
        ==
        EXPECTED_SOPHON_INSTRUMENTATION_SHA256
    )


def test_body_geometry_preserves_csr_rows():
    matrix = make_connectome()

    g = geometry()

    assert (
        g["row_offsets"].tolist()
        == [0, 2, 4, 6]
    )

    for pair, responder in enumerate(
        RESPONDERS
    ):
        start = int(
            g["row_offsets"][pair]
        )

        stop = int(
            g["row_offsets"][
                pair + 1
            ]
        )

        csr_start = int(
            matrix.indptr[
                int(responder)
            ]
        )

        csr_stop = int(
            matrix.indptr[
                int(responder) + 1
            ]
        )

        np.testing.assert_array_equal(
            g["row_indices"][
                start:stop
            ],
            matrix.indices[
                csr_start:csr_stop
            ],
        )

        np.testing.assert_array_equal(
            g["row_weights"][
                start:stop
            ],
            matrix.data[
                csr_start:csr_stop
            ],
        )


def test_body_positions_point_to_sources():
    g = geometry()

    for pair, source in enumerate(
        SOURCES
    ):
        flat = int(
            g[
                "body_flat_positions"
            ][pair]
        )

        assert (
            g["row_indices"][flat]
            == source
        )


def test_union_mapping_round_trips():
    g = geometry()

    np.testing.assert_array_equal(
        g[
            "presynaptic_union_indices"
        ][
            g[
                "row_union_positions"
            ]
        ],
        g["row_indices"],
    )


def test_dark_forest_is_bit_identical(
    tmp_path,
):
    relay, graded = (
        make_artifacts(
            tmp_path
        )
    )

    g = geometry()

    recorder = (
        DarkForestPhaseRecorder(
            source_indices=
                SOURCES,
            responder_indices=
                RESPONDERS,
            presynaptic_union_indices=
                g[
                    "presynaptic_union_indices"
                ],
        )
    )

    baseline = make_runtime(
        relay=relay,
        graded=graded,
    )

    observed = make_runtime(
        relay=relay,
        graded=graded,
        modifier=recorder,
    )

    initialize_state(
        baseline
    )

    initialize_state(
        observed
    )

    for frame in range(32):
        stimulus = (
            stimulus_for_frame(
                frame
            )
        )

        recorder.before_step(
            observed,
            stimulus,
        )

        baseline_return = (
            baseline.step(
                stimulus
            )
        )

        observed_return = (
            observed.step(
                stimulus
            )
        )

        recorder.after_step(
            observed
        )

        np.testing.assert_array_equal(
            baseline_return,
            observed_return,
        )

        np.testing.assert_array_equal(
            baseline.voltage,
            observed.voltage,
        )

        np.testing.assert_array_equal(
            baseline.spikes,
            observed.spikes,
        )

        np.testing.assert_array_equal(
            baseline.relay_inhibition,
            observed.relay_inhibition,
        )

        np.testing.assert_array_equal(
            baseline.last_release,
            observed.last_release,
        )

    arrays = recorder.arrays()

    assert (
        arrays[
            "local_effective_activity_pre_synaptic"
        ].shape
        ==
        (
            32,
            len(
                g[
                    "presynaptic_union_indices"
                ]
            ),
        )
    )

    assert (
        arrays[
            "responder_synaptic_p3"
        ].shape
        == (32, 3)
    )


def test_first_frame_local_p2_and_p3_are_exact(
    tmp_path,
):
    relay, graded = (
        make_artifacts(
            tmp_path
        )
    )

    g = geometry()

    recorder = (
        DarkForestPhaseRecorder(
            source_indices=
                SOURCES,
            responder_indices=
                RESPONDERS,
            presynaptic_union_indices=
                g[
                    "presynaptic_union_indices"
                ],
        )
    )

    runtime = make_runtime(
        relay=relay,
        graded=graded,
        modifier=recorder,
    )

    initialize_state(
        runtime
    )

    stimulus = (
        stimulus_for_frame(0)
    )

    #
    # Capture the exact pre-step state so
    # we can independently derive P2/P3
    # for this synthetic frame.
    #
    expected_activity = (
        runtime.effective_activity()
    )

    expected_synaptic = (
        runtime.connectome
        @ expected_activity
    )

    expected_synaptic = np.asarray(
        expected_synaptic,
        dtype=np.float32,
    ).ravel()

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

    arrays = recorder.arrays()

    np.testing.assert_array_equal(
        arrays[
            "local_effective_activity_pre_synaptic"
        ][0],
        expected_activity[
            g[
                "presynaptic_union_indices"
            ]
        ],
    )

    np.testing.assert_array_equal(
        arrays[
            "responder_synaptic_p3"
        ][0],
        expected_synaptic[
            RESPONDERS
        ],
    )
