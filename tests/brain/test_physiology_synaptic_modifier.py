from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


DATA = (
    Path.home()
    / "moscaquant-data"
    / "processed"
)

CONNECTOME = (
    DATA
    / "connectome-baseline-v1.npz"
)

RETINA = (
    DATA
    / "visual-r1-r6-map-v1.npz"
)

RELAY = (
    DATA
    / "visual-relay-map-v1.npz"
)

GRADED = (
    DATA
    / "mq3-2-graded-visual-types-v1.npz"
)


def build_runtime(
    *,
    modifier=None,
):
    connectome = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    retina = np.load(
        RETINA
    )

    retinal_indices = np.asarray(
        retina["neuron_index"],
        dtype=np.int32,
    )

    return PhysiologyConstrainedVisualTransductionRuntime(
        connectome=connectome,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(),
        synaptic_modifier=modifier,
    )


def test_no_modifier_preserves_baseline_behavior():
    first = build_runtime()
    second = build_runtime(
        modifier=None,
    )

    stimulus = np.zeros(
        first.population_size,
        dtype=np.float32,
    )

    first_result = first.step(
        stimulus
    )

    second_result = second.step(
        stimulus
    )

    np.testing.assert_array_equal(
        first_result,
        second_result,
    )

    np.testing.assert_array_equal(
        first.voltage,
        second.voltage,
    )


def test_identity_modifier_preserves_behavior():
    baseline = build_runtime()

    modified = build_runtime(
        modifier=lambda activity, synaptic: synaptic
    )

    stimulus = np.zeros(
        baseline.population_size,
        dtype=np.float32,
    )

    baseline.step(
        stimulus
    )

    modified.step(
        stimulus
    )

    np.testing.assert_array_equal(
        baseline.voltage,
        modified.voltage,
    )

    np.testing.assert_array_equal(
        baseline.spikes,
        modified.spikes,
    )


def test_modifier_can_change_synaptic_vector():
    baseline = build_runtime()

    modified = build_runtime(
        modifier=lambda activity, synaptic: (
            synaptic * 0.5
        )
    )

    #
    # Give both runtimes identical internal activity
    # so there is actual synaptic propagation.
    #
    baseline.spikes[56393] = 1.0
    modified.spikes[56393] = 1.0

    stimulus = np.zeros(
        baseline.population_size,
        dtype=np.float32,
    )

    baseline.step(
        stimulus
    )

    modified.step(
        stimulus
    )

    assert not np.array_equal(
        baseline.voltage,
        modified.voltage,
    )


def test_modifier_shape_mismatch_is_rejected():
    runtime = build_runtime(
        modifier=lambda activity, synaptic: (
            np.zeros(
                len(synaptic) - 1,
                dtype=np.float32,
            )
        )
    )

    stimulus = np.zeros(
        runtime.population_size,
        dtype=np.float32,
    )

    with pytest.raises(
        ValueError,
        match="shape mismatch",
    ):
        runtime.step(
            stimulus
        )


def test_modifier_nonfinite_output_is_rejected():
    def bad_modifier(
        activity,
        synaptic,
    ):
        result = synaptic.copy()
        result[0] = np.nan
        return result

    runtime = build_runtime(
        modifier=bad_modifier
    )

    stimulus = np.zeros(
        runtime.population_size,
        dtype=np.float32,
    )

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        runtime.step(
            stimulus
        )
