from __future__ import annotations
from config.paths import data_path

import hashlib
import json
from pathlib import Path


SOURCE = data_path('experiments', 'mq3-2-causal-path-decomposition-v1.json')

OUTPUT = data_path('processed', 'mq3-2-first-onset-causal-edges-v1.json')


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def main():
    data = json.loads(
        SOURCE.read_text(
            encoding="utf-8"
        )
    )

    edges = {}
    targets = []

    for target in data["targets"]:

        target_info = target["target"]

        first = next(
            frame
            for frame in target["frames"]
            if frame["label"]
            == "first_positive"
        )

        target_edges = set()

        for path in first["paths"]:
            for edge in path["edges"]:

                key = (
                    int(
                        edge[
                            "presynaptic"
                        ]
                    ),
                    int(
                        edge[
                            "postsynaptic"
                        ]
                    ),
                )

                target_edges.add(
                    key
                )

                if key not in edges:
                    edges[key] = {
                        "presynaptic":
                            key[0],

                        "postsynaptic":
                            key[1],

                        "weight":
                            float(
                                edge[
                                    "weight"
                                ]
                            ),

                        "observed_frames":
                            set(),

                        "targets":
                            set(),
                    }

                edges[
                    key
                ][
                    "observed_frames"
                ].add(
                    int(
                        edge[
                            "frame"
                        ]
                    )
                )

                edges[
                    key
                ][
                    "targets"
                ].add(
                    int(
                        target_info[
                            "model_index"
                        ]
                    )
                )

        targets.append(
            {
                "model_index":
                    int(
                        target_info[
                            "model_index"
                        ]
                    ),

                "body_id":
                    int(
                        target_info[
                            "body_id"
                        ]
                    ),

                "type":
                    target_info[
                        "type"
                    ],

                "instance":
                    target_info[
                        "instance"
                    ],

                "first_positive_frame":
                    int(
                        target[
                            "first_positive_frame"
                        ]
                    ),

                "candidate_path_count":
                    int(
                        first[
                            "path_count_reported"
                        ]
                    ),

                "intervention_edges":
                    [
                        {
                            "presynaptic":
                                pre,

                            "postsynaptic":
                                post,
                        }
                        for pre, post
                        in sorted(
                            target_edges
                        )
                    ],
            }
        )

    frozen_edges = []

    for key in sorted(edges):
        item = edges[key]

        frozen_edges.append(
            {
                "presynaptic":
                    item[
                        "presynaptic"
                    ],

                "postsynaptic":
                    item[
                        "postsynaptic"
                    ],

                "weight":
                    item[
                        "weight"
                    ],

                "observed_frames":
                    sorted(
                        item[
                            "observed_frames"
                        ]
                    ),

                "targets":
                    sorted(
                        item[
                            "targets"
                        ]
                    ),
            }
        )

    output = {
        "artifact":
            "mq3-2-first-onset-causal-edges-v1",

        "derived_from":
            str(SOURCE),

        "derived_from_sha256":
            sha256_file(
                SOURCE
            ),

        "selection_rule":
            (
                "union of all edges contained "
                "in activity-supported paths "
                "reported at each responder's "
                "first-positive frame"
            ),

        "market_condition_used":
            "A",

        "post_hoc":
            True,

        "purpose":
            "confirmatory in-model causal intervention",

        "edge_count":
            len(
                frozen_edges
            ),

        "edges":
            frozen_edges,

        "targets":
            targets,

        "financial_semantics_used":
            False,
    }

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print("=" * 80)
    print(
        "MQ-3.2 FIRST-ONSET "
        "CAUSAL INTERVENTION ARTIFACT"
    )
    print("=" * 80)

    print(
        "source sha256:",
        output[
            "derived_from_sha256"
        ],
    )

    print(
        "targets:",
        len(
            targets
        ),
    )

    print(
        "unique intervention edges:",
        len(
            frozen_edges
        ),
    )

    print()

    for target in targets:
        print(
            target[
                "model_index"
            ],
            target[
                "body_id"
            ],
            target[
                "type"
            ],
            target[
                "instance"
            ],
            "first=",
            target[
                "first_positive_frame"
            ],
            "paths=",
            target[
                "candidate_path_count"
            ],
            "edges=",
            len(
                target[
                    "intervention_edges"
                ]
            ),
        )

    print()
    print("FROZEN EDGE SET")

    for edge in frozen_edges:
        print(
            edge[
                "presynaptic"
            ],
            "->",
            edge[
                "postsynaptic"
            ],
            "w=",
            edge[
                "weight"
            ],
            "frames=",
            edge[
                "observed_frames"
            ],
            "targets=",
            edge[
                "targets"
            ],
        )

    print()
    print(
        "artifact:",
        OUTPUT,
    )

    print(
        "sha256:",
        sha256_file(
            OUTPUT
        ),
    )

    print()
    print(
        "FINANCIAL SEMANTICS USED: NO"
    )


if __name__ == "__main__":
    main()
