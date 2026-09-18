from __future__ import annotations

from pathlib import Path

from oracle.persistence import (
    load_state,
    write_state,
)
from oracle.plasticity_adapter import (
    get_plasticity_state,
    with_plasticity_state,
)
from oracle.plasticity_state import (
    apply_plasticity_update,
    build_empty_plasticity_state,
    complete_trading_session,
)
from oracle.state import initial_state


ARTIFACT = "connectome-baseline-v1.npz"


def build_plasticity():
    state = build_empty_plasticity_state()

    state = apply_plasticity_update(
        state,
        presynaptic=56393,
        postsynaptic=68045,
        baseline_artifact_id=ARTIFACT,
        baseline_weight=2.0,
        session_id="session-A",
        evidence_reference="credit-001",
    )

    state = complete_trading_session(
        state,
        session_id="session-A",
    )

    return state


def test_round_trip_inside_oracle_state():
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    plasticity = build_plasticity()

    updated = with_plasticity_state(
        oracle,
        plasticity,
    )

    restored = get_plasticity_state(
        updated
    )

    assert restored == plasticity
    assert updated.state_hash != oracle.state_hash


def test_state_json_restart_round_trip(
    tmp_path: Path,
):
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )


    plasticity = build_plasticity()

    updated = with_plasticity_state(
        oracle,
        plasticity,
    )

    path = tmp_path / "state.json"

    write_state(
        path,
        updated,
   )

    loaded = load_state(path)

    restored = get_plasticity_state(
        loaded
    )

    assert restored == plasticity
    assert loaded == updated


def test_multiplier_and_counter_survive_restart(
    tmp_path: Path,
):
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )


    plasticity = build_plasticity()

    for index in range(3):
        plasticity = complete_trading_session(
            plasticity,
            session_id=f"inactive-{index}",
        )

    updated = with_plasticity_state(
        oracle,
        plasticity,
    )

    path = tmp_path / "state.json"

    write_state(
       path,
       updated,
    )

    loaded = load_state(path)

    restored = get_plasticity_state(
        loaded
    )

    assert restored is not None

    edge = restored.edges[0]

    assert edge.multiplier == 0.95
    assert edge.inactive_completed_sessions == 3


def test_hash_chain_survives_restart(
    tmp_path: Path,
):
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )


    plasticity = build_plasticity()

    original_hash = plasticity.state_hash

    updated = with_plasticity_state(
        oracle,
        plasticity,
    )

    path = tmp_path / "state.json"

    write_state(
       path,
       updated,
    )

    loaded = load_state(path)

    restored = get_plasticity_state(
        loaded
    )

    assert restored is not None
    assert restored.state_hash == original_hash

    next_state = complete_trading_session(
        restored,
        session_id="session-B",
    )

    assert (
        next_state.previous_state_hash
        == original_hash
    )
def test_tampered_plasticity_state_is_rejected(
    tmp_path: Path,
):
    oracle = initial_state(
        oracle_version="oracle-test-v1",
    )

    plasticity = build_plasticity()

    updated = with_plasticity_state(
        oracle,
        plasticity,
    )

    path = tmp_path / "state.json"

    write_state(
        path,
        updated,
    )

    import json

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    adaptation = payload["adaptation_state"]

    for item in adaptation:
        if item[0] != "sc-03-plasticity-state":
            continue

        nested = dict(item[1])
        edges = nested["edges"]

        first_edge = dict(edges[0])

        #
        # Tamper with the persisted multiplier while
        # deliberately leaving the plasticity hash unchanged.
        #
        first_edge["multiplier"] = 0.81

        edges[0] = list(
            first_edge.items()
        )

        break

    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    loaded = load_state(path)

    import pytest

    with pytest.raises(
        ValueError,
        match="plasticity state hash mismatch",
    ):
        get_plasticity_state(
            loaded
        )
