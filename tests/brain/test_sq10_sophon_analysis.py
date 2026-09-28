from __future__ import annotations

import numpy as np

from brain.sq10_sophon_analysis import (
    analyze,
    first_exact_divergence,
)


MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

TOLERANCE = 3.814697265625e-06


def base_arrays(
    *,
    weights=(
        0.001,
        0.001,
        0.001,
    ),
):
    ids = []
    masks = []
    replicates = []
    zeroed = []

    for mask in MASKS:
        for replicate in (1, 2):
            ids.append(
                f"sq10:{mask}:r{replicate}"
            )
            masks.append(mask)
            replicates.append(replicate)
            zeroed.append(
                [
                    int(bit)
                    for bit in mask
                ]
            )

    float_dynamic = np.zeros(
        (16, 192, 3),
        dtype=np.float32,
    )

    binary_dynamic = np.zeros(
        (16, 192, 3),
        dtype=np.uint8,
    )

    return {
        "condition_ordinal":
            np.arange(
                16,
                dtype=np.int32,
            ),

        "condition_id":
            np.asarray(
                ids,
                dtype="<U11",
            ),

        "condition_mask":
            np.asarray(
                masks,
                dtype="<U3",
            ),

        "condition_replicate":
            np.asarray(
                replicates,
                dtype=np.int8,
            ),

        "source_indices":
            np.asarray(
                [
                    65084,
                    128590,
                    135589,
                ],
                dtype=np.int64,
            ),

        "responder_indices":
            np.asarray(
                [
                    137122,
                    317,
                    126002,
                ],
                dtype=np.int64,
            ),

        "body_edge_weight":
            np.asarray(
                weights,
                dtype=np.float32,
            ),

        "condition_edge_zeroed":
            np.asarray(
                zeroed,
                dtype=np.uint8,
            ),

        "source_voltage_pre_step":
            float_dynamic.copy(),

        "source_spikes_pre_step":
            binary_dynamic.copy(),

        "source_effective_activity_pre_synaptic":
            float_dynamic.copy(),

        "responder_voltage_pre_threshold":
            float_dynamic.copy(),

        "responder_fired":
            binary_dynamic.copy(),

        "responder_voltage_post_reset":
            float_dynamic.copy(),

        "responder_spikes_post_commit":
            binary_dynamic.copy(),
    }


def rows_for_mask(
    mask: str,
) -> tuple[int, int]:
    position = MASKS.index(mask)

    return (
        position * 2,
        position * 2 + 1,
    )


def set_both_replicates(
    arrays,
    *,
    mask,
    field,
    frame,
    body_index,
    value,
):
    for row in rows_for_mask(mask):
        arrays[field][
            row,
            frame,
            body_index,
        ] = value


def set_all_frames_both_replicates(
    arrays,
    *,
    mask,
    field,
    body_index,
    value,
):
    for row in rows_for_mask(mask):
        arrays[field][
            row,
            :,
            body_index,
        ] = value


def test_first_exact_divergence():
    a = np.asarray(
        [0.0, 0.0, 1.0],
        dtype=np.float32,
    )

    b = np.asarray(
        [0.0, 0.0, 2.0],
        dtype=np.float32,
    )

    assert (
        first_exact_divergence(a, b)
        == 2
    )

    assert (
        first_exact_divergence(a, a)
        is None
    )


def test_all_12_contrasts_are_analyzed():
    arrays = base_arrays()

    result = analyze(arrays)

    assert result[
        "contrast_count"
    ] == 12

    assert len(
        result["contrasts"]
    ) == 12


def test_no_responder_divergence_class():
    arrays = base_arrays()

    result = analyze(arrays)

    assert result[
        "classification_counts"
    ] == {
        "NO_RESPONDER_DIVERGENCE":
            12
    }


def test_direct_local_at_first_divergence():
    arrays = base_arrays()

    #
    # A contrast 000 -> 100.
    #
    for mask in ("000", "100"):
        set_all_frames_both_replicates(
            arrays,
            mask=mask,
            field=(
                "source_effective_activity_"
                "pre_synaptic"
            ),
            body_index=0,
            value=np.float32(0.5),
        )

    predicted = np.float32(
        0.5 * arrays[
            "body_edge_weight"
        ][0]
    )

    set_both_replicates(
        arrays,
        mask="000",
        field=(
            "responder_voltage_"
            "pre_threshold"
        ),
        frame=10,
        body_index=0,
        value=predicted,
    )

    result = analyze(arrays)

    contrast = next(
        row
        for row in result["contrasts"]
        if (
            row["body"] == "A"
            and row["retained_mask"]
            == "000"
            and row["lesioned_mask"]
            == "100"
        )
    )

    assert (
        contrast["classification"]
        == "DIRECT_LOCAL_AT_FIRST_DIVERGENCE"
    )

    assert (
        contrast[
            "first_responder_divergence_frame"
        ]
        == 10
    )

    assert (
        contrast["absolute_residual"]
        <= TOLERANCE
    )

    assert (
        abs(
            contrast[
                "predicted_direct_delta"
            ]
        )
        > TOLERANCE
    )


def test_below_calibrated_resolution_class():
    arrays = base_arrays(
        weights=(
            1.0e-6,
            0.001,
            0.001,
        )
    )

    for mask in ("000", "100"):
        set_all_frames_both_replicates(
            arrays,
            mask=mask,
            field=(
                "source_effective_activity_"
                "pre_synaptic"
            ),
            body_index=0,
            value=np.float32(1.0),
        )

    set_both_replicates(
        arrays,
        mask="000",
        field=(
            "responder_voltage_"
            "pre_threshold"
        ),
        frame=8,
        body_index=0,
        value=np.float32(1.0e-6),
    )

    result = analyze(arrays)

    contrast = next(
        row
        for row in result["contrasts"]
        if (
            row["body"] == "A"
            and row["retained_mask"]
            == "000"
            and row["lesioned_mask"]
            == "100"
        )
    )

    assert (
        contrast["classification"]
        == "DIRECT_EFFECT_BELOW_"
        "CALIBRATED_RESOLUTION"
    )


def test_source_divergence_takes_priority():
    arrays = base_arrays()

    for mask in ("000", "100"):
        set_all_frames_both_replicates(
            arrays,
            mask=mask,
            field=(
                "source_effective_activity_"
                "pre_synaptic"
            ),
            body_index=0,
            value=np.float32(0.5),
        )

    set_both_replicates(
        arrays,
        mask="100",
        field=(
            "source_effective_activity_"
            "pre_synaptic"
        ),
        frame=9,
        body_index=0,
        value=np.float32(0.4),
    )

    set_both_replicates(
        arrays,
        mask="000",
        field=(
            "responder_voltage_"
            "pre_threshold"
        ),
        frame=10,
        body_index=0,
        value=np.float32(0.0005),
    )

    result = analyze(arrays)

    contrast = next(
        row
        for row in result["contrasts"]
        if (
            row["body"] == "A"
            and row["retained_mask"]
            == "000"
            and row["lesioned_mask"]
            == "100"
        )
    )

    assert (
        contrast["classification"]
        == "SOURCE_STATE_DIVERGES_"
        "BEFORE_OR_AT_RESPONDER"
    )

    assert (
        contrast[
            "target_source_first_divergence_frame"
        ]
        == 9
    )


def test_residual_exceeds_tolerance_class():
    arrays = base_arrays()

    for mask in ("000", "100"):
        set_all_frames_both_replicates(
            arrays,
            mask=mask,
            field=(
                "source_effective_activity_"
                "pre_synaptic"
            ),
            body_index=0,
            value=np.float32(0.5),
        )

    set_both_replicates(
        arrays,
        mask="000",
        field=(
            "responder_voltage_"
            "pre_threshold"
        ),
        frame=12,
        body_index=0,
        value=np.float32(0.001),
    )

    result = analyze(arrays)

    contrast = next(
        row
        for row in result["contrasts"]
        if (
            row["body"] == "A"
            and row["retained_mask"]
            == "000"
            and row["lesioned_mask"]
            == "100"
        )
    )

    assert (
        contrast["classification"]
        == "DIRECT_PREDICTION_RESIDUAL_"
        "EXCEEDS_TOLERANCE"
    )

    assert (
        contrast["absolute_residual"]
        > TOLERANCE
    )


def test_off_target_divergence_is_reported():
    arrays = base_arrays()

    #
    # A comparison 000 -> 100, but B source
    # and C responder diverge later.
    #
    set_both_replicates(
        arrays,
        mask="100",
        field=(
            "source_effective_activity_"
            "pre_synaptic"
        ),
        frame=20,
        body_index=1,
        value=np.float32(0.25),
    )

    set_both_replicates(
        arrays,
        mask="100",
        field=(
            "responder_voltage_"
            "pre_threshold"
        ),
        frame=25,
        body_index=2,
        value=np.float32(0.5),
    )

    result = analyze(arrays)

    contrast = next(
        row
        for row in result["contrasts"]
        if (
            row["body"] == "A"
            and row["retained_mask"]
            == "000"
            and row["lesioned_mask"]
            == "100"
        )
    )

    assert (
        contrast[
            "off_target_source_first_divergence_frames"
        ]["B"]
        == 20
    )

    assert (
        contrast[
            "off_target_responder_first_divergence_frames"
        ]["C"]
        == 25
    )
