from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

FROZEN_RUNTIME_SOURCE = (
    ROOT
    / "brain"
    / "physiology_constrained_visual_transduction.py"
)

EXPECTED_FROZEN_RUNTIME_SHA256 = (
    "bf754a29155ade789349fbdfc3c579f1"
    "b2c8dbea3c63804f2cf3d858d0a2f605"
)


class SophonInstrumentationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def verify_frozen_runtime_source() -> str:
    actual = sha256_file(
        FROZEN_RUNTIME_SOURCE
    )

    if actual != EXPECTED_FROZEN_RUNTIME_SHA256:
        raise SophonInstrumentationError(
            "frozen physiology runtime SHA mismatch: "
            f"{actual} != "
            f"{EXPECTED_FROZEN_RUNTIME_SHA256}"
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

    if len(np.unique(result)) != len(result):
        raise ValueError(
            f"{name} contains duplicates"
        )

    return result


class SophonPhaseRecorder:
    """
    Passive phase recorder for SQ-10 SOPHON.

    The recorder is installed as the frozen runtime's
    identity synaptic_modifier.

    It MUST return the incoming synaptic vector unchanged.

    P0 is captured immediately before runtime.step().
    P2 is observed inside the frozen synaptic_modifier hook.
    P5/P6 are reconstructed from the exact operands consumed
    by the frozen runtime.
    P7 is captured immediately after runtime.step().

    The frozen runtime itself is never modified.
    """

    def __init__(
        self,
        *,
        source_indices,
        responder_indices,
    ):
        verify_frozen_runtime_source()

        self.source_indices = _index_vector(
            "source_indices",
            source_indices,
        )

        self.responder_indices = _index_vector(
            "responder_indices",
            responder_indices,
        )

        if (
            self.source_indices.shape
            != self.responder_indices.shape
        ):
            raise ValueError(
                "source/responder coordinate "
                "shape mismatch"
            )

        self.body_pair_count = len(
            self.source_indices
        )

        self._frame_open = False
        self._callback_seen = False
        self._relay_positions = None

        self._frames = {
            "source_voltage_pre_step": [],
            "source_spikes_pre_step": [],
            "source_effective_activity_pre_synaptic": [],
            "responder_voltage_pre_threshold": [],
            "responder_fired": [],
            "responder_voltage_post_reset": [],
            "responder_spikes_post_commit": [],
        }

    def _bind_runtime_coordinates(
        self,
        runtime,
    ) -> None:
        if self._relay_positions is not None:
            return

        population_size = int(
            runtime.population_size
        )

        for name, indices in (
            ("source", self.source_indices),
            ("responder", self.responder_indices),
        ):
            if np.any(indices < 0):
                raise SophonInstrumentationError(
                    f"{name} index is negative"
                )

            if np.any(indices >= population_size):
                raise SophonInstrumentationError(
                    f"{name} index outside runtime population"
                )

        relay_lookup = {
            int(index): int(position)
            for position, index
            in enumerate(
                np.asarray(
                    runtime.relay_indices,
                    dtype=np.int64,
                )
            )
        }

        self._relay_positions = np.asarray(
            [
                relay_lookup.get(
                    int(index),
                    -1,
                )
                for index
                in self.responder_indices
            ],
            dtype=np.int64,
        )

    def before_step(
        self,
        runtime,
        stimulus,
    ) -> None:
        if self._frame_open:
            raise SophonInstrumentationError(
                "previous SOPHON frame was not closed"
            )

        self._bind_runtime_coordinates(
            runtime
        )

        stimulus = np.asarray(
            stimulus,
            dtype=np.float32,
        )

        if stimulus.shape != (
            runtime.population_size,
        ):
            raise SophonInstrumentationError(
                "stimulus shape mismatch"
            )

        self._p0_source_voltage = np.asarray(
            runtime.voltage[
                self.source_indices
            ],
            dtype=np.float32,
        ).copy()

        self._p0_source_spikes = np.asarray(
            runtime.spikes[
                self.source_indices
            ] > 0,
            dtype=np.uint8,
        ).copy()

        self._p0_responder_voltage = np.asarray(
            runtime.voltage[
                self.responder_indices
            ],
            dtype=np.float32,
        ).copy()

        self._stimulus_responder = np.asarray(
            stimulus[
                self.responder_indices
            ],
            dtype=np.float32,
        ).copy()

        retinal_spikes = np.asarray(
            runtime.spikes[
                runtime.retinal_indices
            ],
            dtype=np.float32,
        )

        direct_retinal_current = (
            runtime.relay_from_retina
            @ retinal_spikes
        )

        direct_retinal_current = np.asarray(
            direct_retinal_current,
            dtype=np.float32,
        ).ravel()

        inhibition = np.maximum(
            -direct_retinal_current,
            0.0,
        )

        release = np.maximum(
            np.asarray(
                runtime.relay_inhibition,
                dtype=np.float32,
            )
            - inhibition,
            0.0,
        )

        self._responder_retinal_current = (
            np.zeros(
                self.body_pair_count,
                dtype=np.float32,
            )
        )

        self._responder_release = (
            np.zeros(
                self.body_pair_count,
                dtype=np.float32,
            )
        )

        for i, relay_position in enumerate(
            self._relay_positions
        ):
            if relay_position < 0:
                continue

            self._responder_retinal_current[
                i
            ] = direct_retinal_current[
                relay_position
            ]

            self._responder_release[
                i
            ] = release[
                relay_position
            ]

        self._decay = runtime.decay
        self._threshold = (
            runtime.config.threshold
        )
        self._reset = runtime.config.reset
        self._release_gain = (
            runtime.config.release_gain
        )

        self._frame_open = True
        self._callback_seen = False

    def __call__(
        self,
        effective_activity,
        synaptic,
    ):
        if not self._frame_open:
            raise SophonInstrumentationError(
                "synaptic callback occurred "
                "outside an open SOPHON frame"
            )

        if self._callback_seen:
            raise SophonInstrumentationError(
                "multiple synaptic callbacks "
                "within one SOPHON frame"
            )

        activity = np.asarray(
            effective_activity,
            dtype=np.float32,
        )

        synaptic_array = np.asarray(
            synaptic,
            dtype=np.float32,
        )

        self._p2_source_activity = np.asarray(
            activity[
                self.source_indices
            ],
            dtype=np.float32,
        ).copy()

        responder_synaptic = np.asarray(
            synaptic_array[
                self.responder_indices
            ],
            dtype=np.float32,
        ).copy()

        #
        # Mirror the frozen runtime's retinal
        # double-count subtraction for any responder
        # that happens to belong to the relay population.
        #
        responder_synaptic -= (
            self._responder_retinal_current
        )

        #
        # Reconstruct P5 using the same float32
        # in-place operation order as the runtime:
        #
        #   voltage *= decay
        #   voltage += synaptic
        #   voltage += stimulus
        #   relay voltage += release * gain
        #
        p5 = self._p0_responder_voltage.copy()

        p5 *= self._decay
        p5 += responder_synaptic
        p5 += self._stimulus_responder

        relay_addition = np.asarray(
            self._responder_release
            * self._release_gain,
            dtype=np.float32,
        )

        p5 += relay_addition

        self._p5_responder_voltage = p5

        self._p6_responder_fired = np.asarray(
            p5 >= self._threshold,
            dtype=np.uint8,
        )

        self._callback_seen = True

        #
        # Critical containment rule:
        # return the runtime-owned synaptic vector
        # unchanged.
        #
        return synaptic

    def after_step(
        self,
        runtime,
    ) -> None:
        if not self._frame_open:
            raise SophonInstrumentationError(
                "no open SOPHON frame"
            )

        if not self._callback_seen:
            raise SophonInstrumentationError(
                "SOPHON synaptic callback "
                "was not observed"
            )

        p7_voltage = np.asarray(
            runtime.voltage[
                self.responder_indices
            ],
            dtype=np.float32,
        ).copy()

        p7_spikes = np.asarray(
            runtime.spikes[
                self.responder_indices
            ] > 0,
            dtype=np.uint8,
        ).copy()

        #
        # Independently derive the P7 responder
        # voltage expected from reconstructed P5.
        #
        expected_p7 = (
            self._p5_responder_voltage.copy()
        )

        expected_p7[
            self._p6_responder_fired > 0
        ] = self._reset

        if not np.array_equal(
            expected_p7,
            p7_voltage,
        ):
            raise SophonInstrumentationError(
                "P5/P7 voltage reconstruction drift"
            )

        if not np.array_equal(
            self._p6_responder_fired,
            p7_spikes,
        ):
            raise SophonInstrumentationError(
                "P6/P7 spike reconstruction drift"
            )

        self._frames[
            "source_voltage_pre_step"
        ].append(
            self._p0_source_voltage
        )

        self._frames[
            "source_spikes_pre_step"
        ].append(
            self._p0_source_spikes
        )

        self._frames[
            "source_effective_activity_pre_synaptic"
        ].append(
            self._p2_source_activity
        )

        self._frames[
            "responder_voltage_pre_threshold"
        ].append(
            self._p5_responder_voltage.copy()
        )

        self._frames[
            "responder_fired"
        ].append(
            self._p6_responder_fired.copy()
        )

        self._frames[
            "responder_voltage_post_reset"
        ].append(
            p7_voltage
        )

        self._frames[
            "responder_spikes_post_commit"
        ].append(
            p7_spikes
        )

        self._frame_open = False
        self._callback_seen = False

    def arrays(self) -> dict[str, np.ndarray]:
        if self._frame_open:
            raise SophonInstrumentationError(
                "cannot materialize arrays "
                "with an open SOPHON frame"
            )

        if not self._frames[
            "source_voltage_pre_step"
        ]:
            raise SophonInstrumentationError(
                "no SOPHON frames captured"
            )

        return {
            "source_voltage_pre_step":
                np.stack(
                    self._frames[
                        "source_voltage_pre_step"
                    ]
                ).astype(
                    np.float32,
                    copy=False,
                ),

            "source_spikes_pre_step":
                np.stack(
                    self._frames[
                        "source_spikes_pre_step"
                    ]
                ).astype(
                    np.uint8,
                    copy=False,
                ),

            "source_effective_activity_pre_synaptic":
                np.stack(
                    self._frames[
                        "source_effective_activity_pre_synaptic"
                    ]
                ).astype(
                    np.float32,
                    copy=False,
                ),

            "responder_voltage_pre_threshold":
                np.stack(
                    self._frames[
                        "responder_voltage_pre_threshold"
                    ]
                ).astype(
                    np.float32,
                    copy=False,
                ),

            "responder_fired":
                np.stack(
                    self._frames[
                        "responder_fired"
                    ]
                ).astype(
                    np.uint8,
                    copy=False,
                ),

            "responder_voltage_post_reset":
                np.stack(
                    self._frames[
                        "responder_voltage_post_reset"
                    ]
                ).astype(
                    np.float32,
                    copy=False,
                ),

            "responder_spikes_post_commit":
                np.stack(
                    self._frames[
                        "responder_spikes_post_commit"
                    ]
                ).astype(
                    np.uint8,
                    copy=False,
                ),
        }
