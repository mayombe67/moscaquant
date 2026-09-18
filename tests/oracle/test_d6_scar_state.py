from __future__ import annotations

from oracle.d6_scar import (
    ScarPhase,
    advance_scar,
    build_scar,
)
from oracle.d6_scar_state import (
    get_scar_state,
    with_scar_state,
)
from oracle.persistence import (
    load_state,
    write_state,
)
from oracle.state import initial_state


def test_scar_round_trip_through_oracle_state():
    base = initial_state(
        oracle_version="glados-test",
    )

    scar = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    state = with_scar_state(
        oracle_state=base,
        scar=scar,
    )

    loaded = get_scar_state(state)

    assert loaded == scar
    assert state.state_hash != base.state_hash


def test_scar_persists_through_state_json(
    tmp_path,
):
    base = initial_state(
        oracle_version="glados-test",
    )

    scar = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    state = with_scar_state(
        oracle_state=base,
        scar=scar,
    )

    path = tmp_path / "state.json"

    write_state(
        path,
        state,
    )

    reloaded = load_state(path)

    assert reloaded == state
    assert get_scar_state(reloaded) == scar


def test_scar_cross_session_progression_persists(
    tmp_path,
):
    path = tmp_path / "state.json"

    oracle_state = initial_state(
        oracle_version="glados-test",
    )

    scar = build_scar(
        session_id="session-A",
        current_generation=42,
    )

    state_a = with_scar_state(
        oracle_state=oracle_state,
        scar=scar,
    )

    write_state(path, state_a)

    loaded_a = load_state(path)
    scar_a = get_scar_state(loaded_a)

    assert scar_a is not None
    assert (
        scar_a.phase
        is ScarPhase.CURRENT_SESSION
    )

    scar_b = advance_scar(
        state=scar_a,
        session_id="session-B",
    )

    state_b = with_scar_state(
        oracle_state=loaded_a,
        scar=scar_b,
    )

    write_state(path, state_b)

    loaded_b = load_state(path)
    scar_b_loaded = get_scar_state(
        loaded_b
    )

    assert scar_b_loaded is not None
    assert (
        scar_b_loaded.phase
        is ScarPhase.FOLLOWING_SESSION
    )

    scar_c = advance_scar(
        state=scar_b_loaded,
        session_id="session-C",
    )

    state_c = with_scar_state(
        oracle_state=loaded_b,
        scar=scar_c,
    )

    write_state(path, state_c)

    loaded_c = load_state(path)
    scar_c_loaded = get_scar_state(
        loaded_c
    )

    assert scar_c_loaded is not None
    assert (
        scar_c_loaded.phase
        is ScarPhase.RECOVERED
    )

    assert scar_c_loaded.active is False

    assert (
        state_a.state_hash
        != state_b.state_hash
    )

    assert (
        state_b.state_hash
        != state_c.state_hash
    )


def test_no_scar_returns_none():
    state = initial_state(
        oracle_version="glados-test",
    )

    assert get_scar_state(state) is None
