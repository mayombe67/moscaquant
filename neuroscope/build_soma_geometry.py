from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from neuroscope.runtime_profile import (
    PROJECT_ROOT,
    load_runtime_profile,
)


SCHEMA_VERSION = (
    "mq4-neuroscope-soma-geometry-v1"
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        while True:
            block = handle.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def valid_xyz(
    value,
) -> bool:
    if value is None:
        return False

    if not isinstance(
        value,
        (
            list,
            tuple,
            np.ndarray,
        ),
    ):
        return False

    if len(value) != 3:
        return False

    try:
        xyz = np.asarray(
            value,
            dtype=np.float64,
        )
    except Exception:
        return False

    return bool(
        np.all(
            np.isfinite(
                xyz
            )
        )
    )


def main():
    profile = (
        load_runtime_profile()
    )

    annotations_path = (
        profile.data_dir
        / "raw"
        / (
            "body-annotations-male-cns-v1.0-"
            "minconf-0.5.feather"
        )
    )

    replay_path = (
        PROJECT_ROOT
        / "neuroscope"
        / "web"
        / "data"
        / "replay-A-v1.json"
    )

    output_dir = (
        profile.data_dir
        / "neuroscope"
    )

    output_path = (
        output_dir
        / "mq4-soma-geometry-v1.json"
    )

    if not annotations_path.exists():
        raise RuntimeError(
            "annotations missing: "
            f"{annotations_path}"
        )

    if not replay_path.exists():
        raise RuntimeError(
            "web replay missing: "
            f"{replay_path}"
        )

    replay = json.loads(
        replay_path.read_text(
            encoding="utf-8"
        )
    )

    annotations = (
        pd.read_feather(
            annotations_path
        )
        .set_index(
            "bodyId"
        )
    )

    records = []

    real_xyz = []

    role_counts = {
        "real": {},
        "fallback": {},
    }

    for node in replay[
        "nodes"
    ]:
        model_index = int(
            node[
                "i"
            ]
        )

        body_id = int(
            node[
                "body"
            ]
        )

        roles = int(
            node[
                "roles"
            ]
        )

        soma = None
        soma_side = None
        soma_neuromere = None

        if body_id in annotations.index:
            row = annotations.loc[
                body_id
            ]

            soma = row.get(
                "somaLocation"
            )

            soma_side = row.get(
                "somaSide"
            )

            soma_neuromere = row.get(
                "somaNeuromere"
            )

        if valid_xyz(
            soma
        ):
            xyz = np.asarray(
                soma,
                dtype=np.float64,
            )

            source = (
                "somaLocation"
            )

            real_xyz.append(
                xyz
            )

            bucket = "real"

        else:
            xyz = None
            source = (
                "topologyFallback"
            )

            bucket = "fallback"

        role_key = str(
            roles
        )

        role_counts[
            bucket
        ][
            role_key
        ] = (
            role_counts[
                bucket
            ].get(
                role_key,
                0,
            )
            + 1
        )

        records.append(
            {
                "modelIndex":
                    model_index,

                "bodyId":
                    body_id,

                "roles":
                    roles,

                "positionSource":
                    source,

                "xyz":
                    (
                        [
                            float(x)
                            for x in xyz
                        ]
                        if xyz
                        is not None
                        else None
                    ),

                "somaSide":
                    (
                        None
                        if pd.isna(
                            soma_side
                        )
                        else str(
                            soma_side
                        )
                    ),

                "somaNeuromere":
                    (
                        None
                        if pd.isna(
                            soma_neuromere
                        )
                        else str(
                            soma_neuromere
                        )
                    ),
            }
        )

    xyz_array = np.asarray(
        real_xyz,
        dtype=np.float64,
    )

    if not len(
        xyz_array
    ):
        raise RuntimeError(
            "no soma coordinates found"
        )

    minimum = xyz_array.min(
        axis=0
    )

    maximum = xyz_array.max(
        axis=0
    )

    median = np.median(
        xyz_array,
        axis=0,
    )

    center = (
        minimum
        + maximum
    ) / 2.0

    span = (
        maximum
        - minimum
    )

    scale = float(
        span.max()
    )

    real_count = int(
        sum(
            item[
                "positionSource"
            ]
            == "somaLocation"
            for item
            in records
        )
    )

    fallback_count = (
        len(
            records
        )
        - real_count
    )

    responder_records = [
        item
        for item
        in records
        if (
            item[
                "roles"
            ]
            & 16
        )
        != 0
    ]

    if (
        len(
            responder_records
        )
        != 9
    ):
        raise RuntimeError(
            "expected exactly nine "
            "MQ-3 responder nodes"
        )

    if not all(
        item[
            "positionSource"
        ]
        == "somaLocation"
        for item
        in responder_records
    ):
        raise RuntimeError(
            "all nine MQ-3 responders "
            "must have real somaLocation"
        )

    payload = {
        "schema":
            SCHEMA_VERSION,

        "runtimeProfile":
            profile.name,

        "sourceReplay":
            str(
                replay_path
            ),

        "sourceReplaySha256":
            sha256_file(
                replay_path
            ),

        "sourceAnnotations":
            str(
                annotations_path
            ),

        "sourceAnnotationsSha256":
            sha256_file(
                annotations_path
            ),

        "coordinateSystem": {
            "source":
                "MaleCNS somaLocation",

            "units":
                "source dataset units",

            "axisInterpretation":
                "preserved from source",

            "transformed":
                False,

            "center":
                [
                    float(x)
                    for x in center
                ],

            "minimum":
                [
                    float(x)
                    for x in minimum
                ],

            "maximum":
                [
                    float(x)
                    for x in maximum
                ],

            "median":
                [
                    float(x)
                    for x in median
                ],

            "span":
                [
                    float(x)
                    for x in span
                ],

            "uniformScaleDenominator":
                scale,
        },

        "coverage": {
            "viewerNodes":
                len(
                    records
                ),

            "realSoma":
                real_count,

            "fallback":
                fallback_count,

            "fractionReal":
                (
                    real_count
                    / len(
                        records
                    )
                ),

            "roleBitmaskCounts":
                role_counts,
        },

        "responders": [
            {
                "modelIndex":
                    item[
                        "modelIndex"
                    ],

                "bodyId":
                    item[
                        "bodyId"
                    ],

                "xyz":
                    item[
                        "xyz"
                    ],

                "somaSide":
                    item[
                        "somaSide"
                    ],
            }
            for item
            in responder_records
        ],

        "nodes":
            records,

        "interpretation": {
            "realCoordinatesAreAnatomical":
                True,

            "fallbackCoordinatesAreAnatomical":
                False,

            "tosomaLocationUsed":
                False,

            "inventedAnatomicalCoordinates":
                False,

            "simulationFeedback":
                False,

            "financialSemanticsUsed":
                False,
        },
    }

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=" * 80)
    print(
        "MQ-4.4 SOMA GEOMETRY BUILD"
    )
    print("=" * 80)

    print(
        "runtime profile:",
        profile.name,
    )

    print(
        "viewer nodes:",
        len(
            records
        ),
    )

    print(
        "real soma:",
        real_count,
    )

    print(
        "fallback:",
        fallback_count,
    )

    print(
        "coverage:",
        real_count
        / len(
            records
        ),
    )

    print()
    print(
        "minimum:",
        minimum.tolist(),
    )

    print(
        "maximum:",
        maximum.tolist(),
    )

    print(
        "center:",
        center.tolist(),
    )

    print(
        "span:",
        span.tolist(),
    )

    print()
    print(
        "responders with real soma:",
        len(
            responder_records
        ),
        "/ 9",
    )

    print()
    print(
        "artifact:",
        output_path,
    )

    print(
        "sha256:",
        sha256_file(
            output_path
        ),
    )

    print()
    print(
        "TOSOMA FALLBACK USED: NO"
    )

    print(
        "INVENTED ANATOMICAL "
        "COORDINATES: NO"
    )

    print(
        "SIMULATION FEEDBACK: NO"
    )

    print()
    print(
        "MQ-4.4 SOMA GEOMETRY "
        "BUILD COMPLETE"
    )


if __name__ == "__main__":
    main()
