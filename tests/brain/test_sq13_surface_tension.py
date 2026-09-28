import numpy as np

from brain.sq13_surface_tension import (
    MASKS,
    analyze_canonical,
)


def empty_canonical(
    *,
    frames=4,
    baseline=0.2,
):
    voltage = {
        mask: np.full(
            (frames, 3),
            baseline,
            dtype=np.float32,
        )
        for mask in MASKS
    }

    fired = {
        mask: np.zeros(
            (frames, 3),
            dtype=np.uint8,
        )
        for mask in MASKS
    }

    spikes = {
        mask: np.zeros(
            (frames, 3),
            dtype=np.uint8,
        )
        for mask in MASKS
    }

    return {
        "responder_voltage_pre_threshold":
            voltage,
        "responder_fired":
            fired,
        "responder_spikes_post_commit":
            spikes,
    }


def test_positive_decision_margin():
    c = empty_canonical()

    #
    # Each BODY lesion changes only its
    # corresponding synthetic responder,
    # but all states remain below 1.0.
    #
    for mask in MASKS:
        if mask[0] == "1":
            c[
                "responder_voltage_pre_threshold"
            ][mask][:, 0] += np.float32(
                0.1
            )

        if mask[1] == "1":
            c[
                "responder_voltage_pre_threshold"
            ][mask][:, 1] += np.float32(
                0.2
            )

        if mask[2] == "1":
            c[
                "responder_voltage_pre_threshold"
            ][mask][:, 2] += np.float32(
                0.3
            )

    result = analyze_canonical(c)

    assert (
        result["classification"]
        == "GATE_CLOSED_WITH_"
        "POSITIVE_DECISION_MARGIN"
    )

    assert (
        result[
            "contradictory_contrast_count"
        ]
        == 0
    )

    assert (
        result[
            "total_p5_divergent_frames"
        ]
        > 0
    )

    assert (
        result[
            "primary_endpoint"
        ][
            "decision_boundary_distance"
        ]
        > 0.0
    )


def test_touching_boundary_with_same_firing():
    c = empty_canonical(
        baseline=1.1,
    )

    #
    # All synthetic states fire.
    # One lesioned state lands exactly at
    # threshold while the retained state is
    # above threshold, so firing remains equal.
    #
    c[
        "responder_voltage_pre_threshold"
    ]["100"][0, 0] = np.float32(
        1.0
    )

    for mask in MASKS:
        c[
            "responder_fired"
        ][mask][:] = 1

        c[
            "responder_spikes_post_commit"
        ][mask][:] = 1

    result = analyze_canonical(c)

    assert (
        result["classification"]
        == "GATE_TOUCHES_DECISION_BOUNDARY"
    )

    assert (
        result[
            "primary_endpoint"
        ][
            "decision_boundary_distance"
        ]
        == 0.0
    )


def test_firing_difference_is_contradiction():
    c = empty_canonical(
        baseline=0.9,
    )

    c[
        "responder_voltage_pre_threshold"
    ]["100"][0, 0] = np.float32(
        1.1
    )

    c[
        "responder_fired"
    ]["100"][0, 0] = 1

    c[
        "responder_spikes_post_commit"
    ]["100"][0, 0] = 1

    result = analyze_canonical(c)

    assert (
        result["classification"]
        == "TRANSMISSION_GATE_CONTRADICTION"
    )

    assert (
        result[
            "contradictory_contrast_count"
        ]
        >= 1
    )

    assert (
        result[
            "primary_endpoint"
        ]
        is None
    )


def test_no_p5_perturbation():
    c = empty_canonical()

    result = analyze_canonical(c)

    assert (
        result["classification"]
        == "NO_P5_PERTURBATION"
    )

    assert (
        result[
            "total_p5_divergent_frames"
        ]
        == 0
    )

    assert (
        result[
            "primary_endpoint"
        ]
        is None
    )
