from brain.sq12_resonance_cascade_gate_verify import (
    verify_runtime_semantics,
)


def test_non_graded_runtime_is_spike_only():
    assert (
        verify_runtime_semantics()
        is True
    )
