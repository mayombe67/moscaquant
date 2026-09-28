from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MEASUREMENT = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-measurement-contract-v2.json"
)

SCHEMA = (
    ROOT
    / "config/experiments/"
    "sq11-dark-forest-evidence-schema-v2.json"
)

QUAL_SHA = (
    "a2b4256529ef5c7002fc32e9cd4c8779"
    "18d320fd736fa7961ba66f869d70e325"
)

SEAL_SHA = (
    "19529383757e243f9881140edca30b13a"
    "ea10760b582dd2fb1cda09198f225ab"
)


def load(path: Path):
    return json.loads(
        path.read_text()
    )


def test_v2_contracts_are_pre_execution():
    m = load(MEASUREMENT)
    s = load(SCHEMA)

    assert (
        m["status"]
        == "FROZEN_PRE_EXECUTION"
    )

    assert (
        s["status"]
        == "FROZEN_PRE_EXECUTION"
    )


def test_v2_supersedes_v1_for_execution():
    m = load(MEASUREMENT)
    s = load(SCHEMA)

    assert (
        m["supersedes_for_execution"]
        == "moscaquant."
        "sq11-dark-forest-measurement-contract/v1"
    )

    assert (
        s["supersedes_for_execution"]
        == "moscaquant."
        "sq11-dark-forest-evidence-schema/v1"
    )


def test_v2_binds_authoritative_qualification():
    for d in (
        load(MEASUREMENT),
        load(SCHEMA),
    ):
        replay = d[
            "provenance"
        ][
            "execution_authoritative_replay"
        ]

        assert replay["version"] == 2

        assert (
            replay[
                "qualification_result"
            ]["sha256"]
            == QUAL_SHA
        )

        assert (
            replay[
                "qualification_seal"
            ]["sha256"]
            == SEAL_SHA
        )

        assert (
            replay[
                "qualification_comparisons"
            ]
            == 2304
        )

        assert (
            replay[
                "qualification_mismatches"
            ]
            == 0
        )


def test_structural_lesion_semantics_are_frozen():
    m = load(MEASUREMENT)[
        "replay_semantics"
    ]

    s = load(SCHEMA)[
        "replay_semantics"
    ]

    assert (
        m["authoritative_version"]
        == 2
    )

    assert (
        "structurally omitted"
        in m["lesioned_body_edge"]
    )

    assert (
        "must not be represented"
        in m["forbidden_substitution"]
    )

    assert (
        s["lesioned_body_entry_operation"]
        == "skip"
    )

    assert (
        s["zero_multiplication_equivalent"]
        is False
    )


def test_condition_edge_zeroed_has_operational_semantics():
    field = load(
        SCHEMA
    )["arrays"][
        "condition_edge_zeroed"
    ]

    assert field["dtype"] == "uint8"
    assert field["shape"] == [16, 3]

    assert (
        "structurally omits"
        in field["semantics"]
    )


def test_replay_remains_zero_tolerance():
    for d in (
        load(MEASUREMENT)[
            "replay_semantics"
        ],
        load(SCHEMA)[
            "replay_semantics"
        ],
    ):
        assert (
            d["absolute_tolerance"]
            == 0.0
        )

        assert (
            d["relative_tolerance"]
            == 0.0
        )


def test_v2_preserves_self_contained_geometry():
    arrays = load(
        SCHEMA
    )["arrays"]

    required = {
        "row_offsets",
        "row_indices",
        "row_weights",
        "body_positions",
        "body_flat_positions",
        "presynaptic_union_indices",
        "row_union_positions",
        "body_edge_weight",
        "condition_edge_zeroed",
        "local_effective_activity_pre_synaptic",
        "responder_synaptic_p3",
    }

    assert required.issubset(
        arrays
    )


def test_v2_dynamic_shapes_unchanged():
    arrays = load(
        SCHEMA
    )["arrays"]

    assert arrays[
        "local_effective_activity_pre_synaptic"
    ]["shape"] == [
        16,
        192,
        4393,
    ]

    assert arrays[
        "responder_synaptic_p3"
    ]["shape"] == [
        16,
        192,
        3,
    ]


def test_verifier_must_enforce_v2_semantics():
    v = load(
        SCHEMA
    )[
        "verification_requirements"
    ]

    assert (
        v[
            "execution_authoritative_replay_v2"
        ]
        is True
    )

    assert (
        v[
            "structural_lesion_semantics"
        ]
        is True
    )

    assert (
        v[
            "zero_multiplication_forbidden"
        ]
        is True
    )

    assert (
        v[
            "exact_runtime_p3_replay"
        ]
        is True
    )


def test_analysis_still_not_authorized():
    d = load(
        MEASUREMENT
    )[
        "analysis_boundary"
    ]

    assert (
        d["analysis_performed"]
        is False
    )

    assert (
        d["classification_performed"]
        is False
    )

    assert (
        d[
            "post_result_tolerance_allowed"
        ]
        is False
    )

    assert (
        d[
            "execution_authoritative_replay_version"
        ]
        == 2
    )
