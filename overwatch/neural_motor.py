from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from .motor import MotorStateV1


class NeuralMotorAdapterV1(Protocol):
    """Public contract for converting neural/readout state into MotorStateV1.

    Implementations may be public or private. Published claims that depend on a
    specific implementation must disclose enough methodology to evaluate them.
    """

    adapter_id: str
    adapter_version: str

    def map_state(
        self,
        neural_state: Mapping[str, float],
        *,
        sample_index: int | None = None,
    ) -> MotorStateV1:
        ...


@dataclass(frozen=True)
class AdapterProvenanceV1:
    adapter_id: str
    adapter_version: str
    methodology_ref: str | None = None
    implementation_visibility: str = "public"

    def __post_init__(self) -> None:
        if self.implementation_visibility not in {"public", "private"}:
            raise ValueError(
                "implementation_visibility must be public or private"
            )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "methodology_ref": self.methodology_ref,
            "implementation_visibility": self.implementation_visibility,
        }


class ReferenceNeuralMotorAdapterV1:
    """Deliberately simple public reference adapter.

    This proves the interface and telemetry path. It is not the production
    MoscaQuant neural-to-rig mapping and should not be presented as one.
    """

    adapter_id = "reference.linear-neural-motor"
    adapter_version = "v1"

    _ALIASES = {
        "locomotor": "locomotor_drive",
        "grooming": "grooming_drive",
        "courtship": "courtship_drive",
        "escape": "escape_drive",
        "left_wing": "left_wing_velocity",
        "right_wing": "right_wing_velocity",
    }

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def map_state(
        self,
        neural_state: Mapping[str, float],
        *,
        sample_index: int | None = None,
    ) -> MotorStateV1:
        values = {
            target: float(neural_state.get(source, 0.0))
            for source, target in self._ALIASES.items()
        }

        return MotorStateV1(
            locomotor_drive=self._clamp01(values["locomotor_drive"]),
            grooming_drive=self._clamp01(values["grooming_drive"]),
            courtship_drive=self._clamp01(values["courtship_drive"]),
            escape_drive=self._clamp01(values["escape_drive"]),
            left_wing_velocity=values["left_wing_velocity"],
            right_wing_velocity=values["right_wing_velocity"],
        )


def reference_adapter_provenance() -> AdapterProvenanceV1:
    return AdapterProvenanceV1(
        adapter_id=ReferenceNeuralMotorAdapterV1.adapter_id,
        adapter_version=ReferenceNeuralMotorAdapterV1.adapter_version,
        methodology_ref="docs/NEURAL_MOTOR_ADAPTER_V1.md",
        implementation_visibility="public",
    )
