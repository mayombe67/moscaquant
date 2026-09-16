from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


FEATURE_NAMES = (
    "return",
    "momentum",
    "volume_deviation",
    "realized_volatility",
    "spread",
    "order_book_imbalance",
    "return_sign_entropy",
)

RETURN = 0
VOLUME_DEVIATION = 2
SPREAD = 4
ORDER_BOOK_IMBALANCE = 5


@dataclass(frozen=True)
class TerritoryGeometry:
    receptor_rows: np.ndarray
    neuron_index: np.ndarray
    x: np.ndarray
    y: np.ndarray


class MarketVisionSpatialEncoder:
    """
    Deterministic spatial market-to-retina encoder.

    No trade semantics are present here.

    Signed spatial features move or skew a stimulus while integrated
    sensory energy is conserved within each territory.
    """

    def __init__(
        self,
        territory_artifact: Path,
        population_size: int = 166_700,
        base_energy: float = 1.0,
    ):
        self.territory_artifact = Path(
            territory_artifact
        )

        self.population_size = int(
            population_size
        )

        self.base_energy = float(
            base_energy
        )

        if self.population_size <= 0:
            raise ValueError(
                "population_size must be positive"
            )

        if self.base_energy <= 0:
            raise ValueError(
                "base_energy must be positive"
            )

        data = np.load(
            self.territory_artifact
        )

        required = {
            "neuron_index",
            "eye",
            "h1",
            "h2",
            "territory",
        }

        missing = required - set(data.files)

        if missing:
            raise ValueError(
                "territory artifact missing arrays: "
                + ", ".join(sorted(missing))
            )

        self.neuron_index = data[
            "neuron_index"
        ].astype(
            np.int32,
            copy=False,
        )

        self.eye = data[
            "eye"
        ].astype(
            np.int8,
            copy=False,
        )

        self.h1 = data[
            "h1"
        ].astype(
            np.float32,
            copy=False,
        )

        self.h2 = data[
            "h2"
        ].astype(
            np.float32,
            copy=False,
        )

        self.territory = data[
            "territory"
        ].astype(
            np.int8,
            copy=False,
        )

        if (
            self.neuron_index.min() < 0
            or self.neuron_index.max()
            >= self.population_size
        ):
            raise ValueError(
                "territory neuron index outside "
                "population_size"
            )

        self.geometries = {
            territory: self._build_geometry(
                territory
            )
            for territory in range(1, 7)
        }

    @staticmethod
    def _normalize_axis(
        values: np.ndarray,
    ) -> np.ndarray:
        lo = float(values.min())
        hi = float(values.max())

        if hi == lo:
            return np.zeros_like(
                values,
                dtype=np.float32,
            )

        scaled = (
            2.0
            * (values - lo)
            / (hi - lo)
            - 1.0
        )

        return scaled.astype(
            np.float32,
            copy=False,
        )

    def _build_geometry(
        self,
        territory: int,
    ) -> TerritoryGeometry:
        rows = np.flatnonzero(
            self.territory == territory
        )

        if len(rows) == 0:
            raise ValueError(
                f"empty territory T{territory}"
            )

        # Preserve eye separation in geometry.
        #
        # h1/h2 are normalized within each eye's portion of the
        # territory rather than collapsing both eyes into one plane.
        x = np.empty(
            len(rows),
            dtype=np.float32,
        )

        y = np.empty(
            len(rows),
            dtype=np.float32,
        )

        territory_eye = self.eye[rows]

        for eye_value in (0, 1):
            local = np.flatnonzero(
                territory_eye == eye_value
            )

            if len(local) == 0:
                continue

            source_rows = rows[local]

            x[local] = self._normalize_axis(
                self.h1[source_rows]
            )

            y[local] = self._normalize_axis(
                self.h2[source_rows]
            )

        return TerritoryGeometry(
            receptor_rows=rows,
            neuron_index=self.neuron_index[
                rows
            ],
            x=x,
            y=y,
        )

    @staticmethod
    def _validate_features(
        features: np.ndarray,
    ) -> np.ndarray:
        values = np.asarray(
            features,
            dtype=np.float32,
        )

        if values.shape != (6, 7):
            raise ValueError(
                "features must have shape (6, 7)"
            )

        if not np.all(
            np.isfinite(values)
        ):
            raise ValueError(
                "features contain non-finite values"
            )

        if np.any(values < -1.0) or np.any(
            values > 1.0
        ):
            raise ValueError(
                "normalized features must be "
                "within [-1, 1]"
            )

        return values

    @staticmethod
    def _territory_pattern(
        geometry: TerritoryGeometry,
        feature_row: np.ndarray,
    ) -> np.ndarray:
        """
        Build one energy-normalized spatial pattern.

        The parameter constants below are encoding geometry,
        not learned/tuned neural parameters.
        """

        return_value = float(
            feature_row[RETURN]
        )

        volume_value = float(
            feature_row[VOLUME_DEVIATION]
        )

        # Unsigned raw feature represented as a causal
        # deviation in [-1, 1]:
        #
        # -1 = unusually low
        #  0 = near recent baseline
        # +1 = unusually high
        #
        # Convert monotonically to [0, 1] rather than using abs(),
        # which would collapse low and high deviations together.
        spread_value = (
            float(feature_row[SPREAD]) + 1.0
        ) / 2.0

        imbalance_value = float(
            feature_row[
                ORDER_BOOK_IMBALANCE
            ]
        )

        # Signed center movement.
        center_x = 0.35 * return_value
        center_y = 0.35 * volume_value

        # Width ranges from 0.32 to 0.62 in normalized
        # territory coordinates.
        sigma = (
            0.32
            + 0.30 * spread_value
        )

        dx = geometry.x - center_x
        dy = geometry.y - center_y

        distance2 = (
            dx * dx
            + dy * dy
        )

        pattern = np.exp(
            -distance2
            / (2.0 * sigma * sigma)
        ).astype(
            np.float32
        )

        # Signed local left/right skew.
        #
        # Opposite signs produce opposite spatial bias.
        # Clip guarantees non-negative sensory intensity.
        skew = (
            1.0
            + 0.35
            * imbalance_value
            * geometry.x
        )

        pattern *= np.clip(
            skew,
            0.0,
            None,
        ).astype(
            np.float32
        )

        total = float(pattern.sum())

        if total <= 0.0:
            raise RuntimeError(
                "territory pattern has zero energy"
            )

        # Critical fairness rule:
        # spatial encoding redistributes energy but does not
        # change integrated energy.
        pattern /= total

        return pattern

    def encode(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        """
        Encode six ticker feature rows into a full MQ-001
        stimulus vector.

        Row 0 maps to T1, row 1 to T2, ... row 5 to T6.

        Ticker names are deliberately not known by this class.
        """

        values = self._validate_features(
            features
        )

        stimulus = np.zeros(
            self.population_size,
            dtype=np.float32,
        )

        for row_index, territory in enumerate(
            range(1, 7)
        ):
            geometry = self.geometries[
                territory
            ]

            pattern = self._territory_pattern(
                geometry,
                values[row_index],
            )

            stimulus[
                geometry.neuron_index
            ] = (
                self.base_energy
                * pattern
            )

        return stimulus
