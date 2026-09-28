from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.sq10_sophon_instrumentation import (
    EXPECTED_FROZEN_RUNTIME_SHA256,
    SophonPhaseRecorder,
    verify_frozen_runtime_source,
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

RETINA = np.asarray(
    [5999],
    dtype=np.int32,
)


def make_artifacts(
    tmp_path: Path,
):
    relay = tmp_path / "relay.npz"
    graded = tmp_path / "graded.npz"

    relay_indices = np.arange(
        2430,
        dtype=np.int32,
    )

    np.savez(
        relay,
        neuron_index=relay_indices,
        body_id=relay_indices.astype(
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
        neuron_index=graded_indices,
        type=graded_types,
    )

    return relay, graded


def make_connectome():
    matrix = sparse.lil_matrix(
        (POPULATION, POPULATION),
        dtype=np.float32,
    )

    matrix[
        RESPONDERS[0],
        SOURCES[0],
    ] = np.float32(0.25)

    matrix[
        RESPONDERS[1],
        SOURCES[1],
    ] = np.float32(1.5)

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
            connectome=make_connectome(),
            retinal_indices=RETINA,
            relay_artifact=relay,
            graded_artifact=graded,
            config=VisualTransductionConfig(),
            synaptic_modifier=modifier,
        )
    )


def initialize_state(runtime):
    runtime.voltage[
        SOURCES
    ] = np.asarray(
        [0.4, 0.8, 0.6],
        dtype=np.float32,
    )

    runtime.voltage[
        RESPONDERS
    ] = np.asarray(
        [0.1, 0.2, 0.3],
        dtype=np.float32,
    )


def stimulus_for_frame(frame: int):
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
            SOURCES[2]
        ] = np.float32(0.2)

    if frame == 11:
        stimulus[
            RESPONDERS[0]
        ] = np.float32(0.1)

    return stimulus


def test_frozen_runtime_hash_is_exact():
    assert (
        verify_frozen_runtime_source()
        == EXPECTED_FROZEN_RUNTIME_SHA256
    )


def test_sophon_recorder_is_bit_identical_to_frozen_runtime(
    tmp_path,
):
    relay, graded = make_artifacts(
        tmp_path
    )

    recorder = SophonPhaseRecorder(
        source_indices=SOURCES,
        responder_indices=RESPONDERS,
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

    initialize_state(baseline)
    initialize_state(observed)

    for frame in range(32):
        stimulus = stimulus_for_frame(
            frame
        )

        recorder.before_step(
            observed,
            stimulus,
        )

        baseline_return = baseline.step(
            stimulus
        )

        observed_return = observed.step(
            stimulus
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

    expected_shapes = {
        "source_voltage_pre_step":
            (32, 3),
        "source_spikes_pre_step":
            (32, 3),
        "source_effective_activity_pre_synaptic":
            (32, 3),
        "responder_voltage_pre_threshold":
            (32, 3),
        "responder_fired":
            (32, 3),
        "responder_voltage_post_reset":
            (32, 3),
        "responder_spikes_post_commit":
            (32, 3),
    }

    assert {
        key: value.shape
        for key, value
        in arrays.items()
    } == expected_shapes


def test_first_frame_effective_activity_is_exact(
    tmp_path,
):
    relay, graded = make_artifacts(
        tmp_path
    )

    recorder = SophonPhaseRecorder(
        source_indices=SOURCES,
        responder_indices=RESPONDERS,
    )

    runtime = make_runtime(
        relay=relay,
        graded=graded,
        modifier=recorder,
    )

    initialize_state(runtime)

    stimulus = stimulus_for_frame(0)

    recorder.before_step(
        runtime,
        stimulus,
    )

    runtime.step(stimulus)

    recorder.after_step(runtime)

    arrays = recorder.arrays()

    np.testing.assert_array_equal(
        arrays[
            "source_effective_activity_pre_synaptic"
        ][0],
        np.asarray(
            [0.4, 0.8, 0.6],
            dtype=np.float32,
        ),
    )


def test_p5_and_p6_capture_pre_reset_state(
    tmp_path,
):
    relay, graded = make_artifacts(
        tmp_path
    )

    recorder = SophonPhaseRecorder(
        source_indices=SOURCES,
        responder_indices=RESPONDERS,
    )

    runtime = make_runtime(
        relay=relay,
        graded=graded,
        modifier=recorder,
    )

    initialize_state(runtime)

    stimulus = stimulus_for_frame(0)

    recorder.before_step(
        runtime,
        stimulus,
    )

    runtime.step(stimulus)

    recorder.after_step(runtime)

    arrays = recorder.arrays()

    pre_threshold = arrays[
        "responder_voltage_pre_threshold"
    ][0]

    fired = arrays[
        "responder_fired"
    ][0]

    post_reset = arrays[
        "responder_voltage_post_reset"
    ][0]

    assert pre_threshold[1] >= 1.0
    assert fired[1] == 1
    assert post_reset[1] == 0.0
