"""Biologically annotated MQ-001 neuron populations."""

from pathlib import Path

import numpy as np
import pyarrow.feather as feather


def visual_r1_r6_indices(
    annotations_path: Path,
    neuron_ids: np.ndarray,
) -> np.ndarray:
    """Return MQ-001 indices corresponding to R1-R6 photoreceptors."""

    table = feather.read_table(
        annotations_path,
        columns=["bodyId", "superclass", "flywireType"],
        memory_map=True,
    )

    df = table.to_pandas()

    population = df[
        (df["superclass"] == "ol_sensory")
        & (df["flywireType"] == "R1-6")
    ]

    body_ids = np.sort(
        population["bodyId"].to_numpy(dtype=np.int64)
    )

    positions = np.searchsorted(neuron_ids, body_ids)

    valid = positions < len(neuron_ids)

    matched = np.zeros(len(body_ids), dtype=bool)
    matched[valid] = (
        neuron_ids[positions[valid]]
        == body_ids[valid]
    )

    if not matched.all():
        missing = int((~matched).sum())
        raise RuntimeError(
            f"{missing} R1-R6 neurons are absent from MQ-001"
        )

    return positions.astype(np.int32)
