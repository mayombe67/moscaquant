from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import sparse

import brain.mq5_er6r_the_warrant_selector_qualification as q


ROOT = Path(__file__).resolve().parents[1]


def test_qualification_binds_frozen_selector():
    assert (
        q.EXPECTED_SELECTOR_SHA256
        ==
        "010422a952297c5151743a8dc294dd9cb5a008cead5db4841e481ae3a901db1d"
    )

    assert (
        q.SELECTOR_FREEZE_GIT_SHA
        ==
        "8edcbd01e1aafa57ff3270c1cebf5d34de6f5ab1"
    )


def test_qualification_source_cannot_select():
    source = (
        ROOT
        / "brain/"
        "mq5_er6r_the_warrant_selector_qualification.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "selector.build_payload(" not in source
    assert "selector.rank_key(" not in source
    assert ".sort(" not in source


def test_qualification_source_does_not_emit_control_identity():
    source = (
        ROOT
        / "brain/"
        "mq5_er6r_the_warrant_selector_qualification.py"
    ).read_text(
        encoding="utf-8"
    )

    assert '"control_selected":\n            False' in source
    assert '"control_identity_exposed":\n            False' in source


def test_orientation_contract_minimal_graph():
    graph = sparse.csr_matrix(
        (
            np.asarray(
                [1.0, 1.0, 1.0],
                dtype=np.float32,
            ),
            (
                np.asarray(
                    [1, 2, 3],
                    dtype=np.int32,
                ),
                np.asarray(
                    [0, 1, 2],
                    dtype=np.int32,
                ),
            ),
        ),
        shape=(4, 4),
    )

    observed = q.selector.reverse_hop_array(
        graph,
        target=2,
        max_hops=3,
    )

    assert int(observed[1]) == 1
    assert int(observed[0]) == 2
    assert int(observed[3]) == -1


def test_expected_corrected_signature():
    observed = tuple(
        q.selector.EXPECTED_1952_HOPS[
            int(target)
        ]
        for target
        in q.selector.ALL_TARGETS
    )

    assert observed == (
        2,
        3,
        2,
        3,
        3,
        2,
        2,
        3,
        2,
    )



def test_v3_qualification_destination():
    assert (
        q.OUTPUT.name
        ==
        "mq5-er6r-the-warrant-selector-qualification-v3.json"
    )


def test_v3_schema_is_frozen():
    source = (
        ROOT
        / "brain/"
        "mq5_er6r_the_warrant_selector_qualification.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "selector-qualification/v3" in source


def test_requalification_binds_prior_aggregate_universe():
    source = (
        ROOT
        / "brain/"
        "mq5_er6r_the_warrant_selector_qualification.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "eligible_control_count != 149893" in source
    assert "exact_hop_signature_match_count != 1885" in source



def test_final_selector_expects_v3_qualification():
    assert (
        str(
            q.selector.SELECTOR_QUALIFICATION
        )
        ==
        "artifacts/qualification/"
        "mq5-er6r-the-warrant-selector-qualification-v3.json"
    )


def test_apotheosis_32_semantic_bindings():
    assert (
        q.EXPECTED_SELECTOR_SHA256
        ==
        "010422a952297c5151743a8dc294dd9cb5a008cead5db4841e481ae3a901db1d"
    )

    assert (
        q.SELECTOR_FREEZE_GIT_SHA
        ==
        "8edcbd01e1aafa57ff3270c1cebf5d34de6f5ab1"
    )

    assert (
        q.OUTPUT.name
        ==
        "mq5-er6r-the-warrant-selector-qualification-v3.json"
    )
