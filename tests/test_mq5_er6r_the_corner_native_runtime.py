"""Native-runtime contracts on synthetic data; never a C13 scientific run."""
import numpy as np
import pytest
from scipy import sparse

from brain import mq5_er6r_the_corner as corner
from brain import mq5_er6r_the_corner_runner as runner


@pytest.fixture
def native_fixture(tmp_path, monkeypatch):
    # Preserve the native constructors' population contracts without real data.
    n = 12000
    relay = tmp_path / "relay.npz"
    graded = tmp_path / "graded.npz"
    np.savez(relay, neuron_index=np.arange(4000, 6430),
             body_id=np.arange(2430), type=np.full(2430, "L1"))
    np.savez(graded, neuron_index=np.arange(6500, 11990),
             type=np.resize(np.array(["Tm2", "Tm3", "Tm4"]), 5490))
    monkeypatch.setattr(runner, "RELAY", relay)
    monkeypatch.setattr(runner, "GRADED", graded)
    # Independent symmetric routes plus a graded route and retinal relay input.
    graph = sparse.csr_matrix(
        ([0.4, 0.4, 0.2, -0.1], ([55, 92, 656, 4000], [1952, 3056, 6500, 0])),
        shape=(n, n), dtype=np.float32,
    )
    return graph, np.array([0], dtype=np.int32)


def make_runtime(fixture, modifier=None):
    graph, retina = fixture
    return runner.PhysiologyConstrainedVisualTransductionRuntime(
        connectome=graph, retinal_indices=retina, relay_artifact=runner.RELAY,
        graded_artifact=runner.GRADED,
        config=runner.VisualTransductionConfig(release_gain=runner.RELEASE_GAIN),
        activity_modifier=modifier,
    )


def test_runner_p0_equals_native_runtime_for_entire_window(native_fixture):
    graph, retina = native_fixture
    stimuli = []
    for frame in range(192):
        stimulus = np.zeros(graph.shape[0], dtype=np.float32)
        stimulus[[1952, 3056, 6500, 0]] = 1.1 if frame % 7 == 0 else 0.07
        stimuli.append(stimulus)
    targets = (55, 92, 656, 1952, 3056, 6500, 4000)
    native = make_runtime(native_fixture)
    voltage, spikes = [], []
    for frame, stimulus in enumerate(stimuli):
        native.step(stimulus, generation=frame)
        voltage.append(native.voltage[list(targets)].copy())
        spikes.append(native.spikes[list(targets)].copy())
    actual = runner.run_arm("P0", graph, retina, targets, stimuli)
    np.testing.assert_array_equal(actual["responder_voltage"], voltage)
    np.testing.assert_array_equal(actual["responder_spikes"], spikes)
    assert actual["native_target_activity_before_silencing"] == []


@pytest.mark.parametrize("arm,target,downstream", [("P1952", 1952, 55), ("PCONTROL", 3056, 92)])
def test_native_hook_silences_only_output_preserving_internal_state(native_fixture, arm, target, downstream):
    observed = []
    silencer = corner.arm_modifier(arm, population_size=native_fixture[0].shape[0])
    native = make_runtime(native_fixture)

    def inspect(activity, frame):
        before_voltage, before_spikes = treated.voltage.copy(), treated.spikes.copy()
        result = silencer(activity, frame)
        np.testing.assert_array_equal(treated.voltage, before_voltage)
        np.testing.assert_array_equal(treated.spikes, before_spikes)
        assert np.flatnonzero(result != activity).tolist() == [target]
        assert activity[target] == 1.0
        assert result[6500] == activity[6500] == np.float32(0.5)
        observed.append(frame)
        return result

    treated = make_runtime(native_fixture, inspect)
    for runtime in (native, treated):
        runtime.spikes[[1952, 3056, 0]] = 1.0
        runtime.voltage[[1952, 3056]] = 0.3
        runtime.voltage[6500] = 0.5
    stimulus = np.zeros(native_fixture[0].shape[0], dtype=np.float32)
    native.step(stimulus, generation=0)
    treated.step(stimulus, generation=0)
    assert observed == [0]
    assert np.flatnonzero(native.voltage != treated.voltage).tolist() == [downstream]
    assert native.voltage[downstream] > treated.voltage[downstream]
    assert native.voltage[target] == treated.voltage[target] > 0
    np.testing.assert_array_equal(native.spikes, treated.spikes)
