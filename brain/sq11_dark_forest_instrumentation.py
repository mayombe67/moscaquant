from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq10_sophon_instrumentation import (
    SophonPhaseRecorder,
)


ROOT = Path(__file__).resolve().parents[1]

SOPHON_INSTRUMENTATION = (
    ROOT
    / "brain"
    / "sq10_sophon_instrumentation.py"
)

EXPECTED_SOPHON_INSTRUMENTATION_SHA256 = (
    "60ec01ef4c3dc04d40de84e592edfbde"
    "019a0014fe86bb34d59c8ae18a5ee426"
)


class DarkForestInstrumentationError(
    RuntimeError
):
    pass


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


def verify_sophon_instrumentation() -> str:
    actual = sha256_file(
        SOPHON_INSTRUMENTATION
    )

    if (
        actual
        != EXPECTED_SOPHON_INSTRUMENTATION_SHA256
    ):
        raise DarkForestInstrumentationError(
            "SQ-10 instrumentation SHA drift: "
            f"{actual} != "
            f"{EXPECTED_SOPHON_INSTRUMENTATION_SHA256}"
        )

    return actual


def _index_vector(
    name: str,
    value,
) -> np.ndarray:
    result = np.asarray(
        value,
        dtype=np.int64,
    )

    if result.ndim != 1:
        raise ValueError(
            f"{name} must be one-dimensional"
        )

    if len(result) == 0:
        raise ValueError(
            f"{name} must not be empty"
        )

    if (
        len(np.unique(result))
        != len(result)
    ):
        raise ValueError(
            f"{name} contains duplicates"
        )

    return result


def build_body_row_geometry(
    *,
    connectome: sparse.csr_matrix,
    responder_indices,
    source_indices,
) -> dict[str, np.ndarray]:
    """
    Freeze the three responder rows exactly as
    stored in CSR order.

    The flat row arrays preserve numerical
    accumulation order.

    presynaptic_union_indices is a deduplicated
    storage coordinate set.

    row_union_positions maps every flat CSR
    entry back into that union.
    """

    if not sparse.isspmatrix_csr(
        connectome
    ):
        raise TypeError(
            "DARK FOREST connectome must be CSR"
        )

    if (
        connectome.dtype
        != np.dtype(np.float32)
    ):
        raise TypeError(
            "DARK FOREST connectome "
            "must be float32"
        )

    responders = _index_vector(
        "responder_indices",
        responder_indices,
    )

    sources = _index_vector(
        "source_indices",
        source_indices,
    )

    if responders.shape != sources.shape:
        raise ValueError(
            "source/responder shape mismatch"
        )

    if len(responders) != 3:
        raise ValueError(
            "DARK FOREST requires "
            "exactly three BODY pairs"
        )

    population = int(
        connectome.shape[0]
    )

    if connectome.shape != (
        population,
        population,
    ):
        raise ValueError(
            "connectome must be square"
        )

    for name, values in (
        ("source", sources),
        ("responder", responders),
    ):
        if np.any(values < 0):
            raise ValueError(
                f"{name} index is negative"
            )

        if np.any(
            values >= population
        ):
            raise ValueError(
                f"{name} index outside "
                "connectome"
            )

    row_offsets = [0]
    row_indices = []
    row_weights = []
    body_positions = []

    for source, responder in zip(
        sources,
        responders,
    ):
        start = int(
            connectome.indptr[
                int(responder)
            ]
        )

        stop = int(
            connectome.indptr[
                int(responder) + 1
            ]
        )

        columns = np.asarray(
            connectome.indices[
                start:stop
            ],
            dtype=np.int64,
        ).copy()

        weights = np.asarray(
            connectome.data[
                start:stop
            ],
            dtype=np.float32,
        ).copy()

        if len(columns) == 0:
            raise DarkForestInstrumentationError(
                "BODY responder row is empty"
            )

        matches = np.flatnonzero(
            columns == int(source)
        )

        if len(matches) != 1:
            raise DarkForestInstrumentationError(
                "BODY edge occurrence drift: "
                f"{int(source)} -> "
                f"{int(responder)} "
                f"occurs {len(matches)} times"
            )

        body_positions.append(
            int(matches[0])
        )

        row_indices.append(
            columns
        )

        row_weights.append(
            weights
        )

        row_offsets.append(
            row_offsets[-1]
            + len(columns)
        )

    flat_indices = np.concatenate(
        row_indices
    ).astype(
        np.int64,
        copy=False,
    )

    flat_weights = np.concatenate(
        row_weights
    ).astype(
        np.float32,
        copy=False,
    )

    offsets = np.asarray(
        row_offsets,
        dtype=np.int64,
    )

    positions = np.asarray(
        body_positions,
        dtype=np.int64,
    )

    body_flat_positions = (
        offsets[:-1]
        + positions
    ).astype(
        np.int64,
        copy=False,
    )

    union = np.unique(
        flat_indices
    ).astype(
        np.int64,
        copy=False,
    )

    row_union_positions = (
        np.searchsorted(
            union,
            flat_indices,
        )
        .astype(
            np.int64,
            copy=False,
        )
    )

    if not np.array_equal(
        union[
            row_union_positions
        ],
        flat_indices,
    ):
        raise DarkForestInstrumentationError(
            "row-to-union mapping failure"
        )

    return {
        "row_offsets":
            offsets,

        "row_indices":
            flat_indices,

        "row_weights":
            flat_weights,

        "body_positions":
            positions,

        "body_flat_positions":
            body_flat_positions,

        "presynaptic_union_indices":
            union,

        "row_union_positions":
            row_union_positions,
    }


class DarkForestPhaseRecorder(
    SophonPhaseRecorder
):
    """
    Passive SQ-11 extension of the frozen
    SQ-10 SOPHON recorder.

    Adds:

    - P2 effective activity for the complete
      BODY responder-row presynaptic union;
    - callback-time aggregate synaptic input
      for the three BODY responders.

    It delegates the modifier behavior itself
    to SophonPhaseRecorder and returns exactly
    whatever that already-qualified identity
    modifier returns.
    """

    def __init__(
        self,
        *,
        source_indices,
        responder_indices,
        presynaptic_union_indices,
    ):
        verify_sophon_instrumentation()

        super().__init__(
            source_indices=
                source_indices,
            responder_indices=
                responder_indices,
        )

        self.presynaptic_union_indices = (
            _index_vector(
                "presynaptic_union_indices",
                presynaptic_union_indices,
            )
        )

        self._dark_forest_frames = {
            "local_effective_activity_pre_synaptic":
                [],

            "responder_synaptic_p3":
                [],
        }

        self._pending_local_activity = None
        self._pending_responder_p3 = None

    def _validate_union_coordinates(
        self,
        activity: np.ndarray,
    ) -> None:
        if np.any(
            self.presynaptic_union_indices
            < 0
        ):
            raise (
                DarkForestInstrumentationError(
                    "presynaptic union "
                    "contains negative index"
                )
            )

        if np.any(
            self.presynaptic_union_indices
            >= activity.shape[0]
        ):
            raise (
                DarkForestInstrumentationError(
                    "presynaptic union index "
                    "outside activity vector"
                )
            )

    def __call__(
        self,
        effective_activity,
        synaptic,
    ):
        #
        # Let SOPHON perform its already-tested
        # validation/capture first.
        #
        returned = super().__call__(
            effective_activity,
            synaptic,
        )

        activity = np.asarray(
            effective_activity,
            dtype=np.float32,
        )

        synaptic_array = np.asarray(
            synaptic,
            dtype=np.float32,
        )

        self._validate_union_coordinates(
            activity
        )

        if synaptic_array.shape != (
            activity.shape
        ):
            raise (
                DarkForestInstrumentationError(
                    "synaptic/activity shape "
                    "mismatch"
                )
            )

        self._pending_local_activity = (
            np.asarray(
                activity[
                    self.presynaptic_union_indices
                ],
                dtype=np.float32,
            ).copy()
        )

        self._pending_responder_p3 = (
            np.asarray(
                synaptic_array[
                    self.responder_indices
                ],
                dtype=np.float32,
            ).copy()
        )

        #
        # Do not substitute our own array.
        # Preserve SOPHON's qualified identity
        # modifier result.
        #
        return returned

    def after_step(
        self,
        runtime,
    ) -> None:
        if (
            self._pending_local_activity
            is None
            or self._pending_responder_p3
            is None
        ):
            raise (
                DarkForestInstrumentationError(
                    "DARK FOREST callback "
                    "measurement missing"
                )
            )

        #
        # Only commit our frame after SOPHON
        # successfully closes the same frame.
        #
        super().after_step(
            runtime
        )

        self._dark_forest_frames[
            "local_effective_activity_pre_synaptic"
        ].append(
            self._pending_local_activity
        )

        self._dark_forest_frames[
            "responder_synaptic_p3"
        ].append(
            self._pending_responder_p3
        )

        self._pending_local_activity = None
        self._pending_responder_p3 = None

    def arrays(
        self,
    ) -> dict[str, np.ndarray]:
        result = super().arrays()

        frame_count = len(
            self._dark_forest_frames[
                "responder_synaptic_p3"
            ]
        )

        if frame_count == 0:
            raise (
                DarkForestInstrumentationError(
                    "DARK FOREST recorder "
                    "contains no closed frames"
                )
            )

        if len(
            self._dark_forest_frames[
                "local_effective_activity_pre_synaptic"
            ]
        ) != frame_count:
            raise (
                DarkForestInstrumentationError(
                    "DARK FOREST frame "
                    "count mismatch"
                )
            )

        result[
            "local_effective_activity_pre_synaptic"
        ] = np.stack(
            self._dark_forest_frames[
                "local_effective_activity_pre_synaptic"
            ]
        ).astype(
            np.float32,
            copy=False,
        )

        result[
            "responder_synaptic_p3"
        ] = np.stack(
            self._dark_forest_frames[
                "responder_synaptic_p3"
            ]
        ).astype(
            np.float32,
            copy=False,
        )

        return result
