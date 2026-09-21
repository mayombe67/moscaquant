from brain.mq5_er1_detour_laptop_pilot import (
    MAX_BACKWARD_HOPS,
    execution_gate,
)


def valid_protocol(enabled=False):
    return {
        "experiment": {"authoritative": False},
        "scope": {"max_backward_hops": 2},
        "restrictions": {
            "may_amend_parent_protocol": False,
            "may_supply_roadblock_candidates": False,
            "may_tune_thresholds": False,
            "may_create_causal_claims": False,
        },
        "execution": {"result_execution_enabled": bool(enabled)},
    }


def test_pilot_is_hard_locked_to_two_hops():
    assert MAX_BACKWARD_HOPS == 2


def test_execution_gate_refuses_disabled_pilot():
    protocol = valid_protocol(enabled=False)
    try:
        execution_gate(protocol)
    except RuntimeError as exc:
        assert "result_execution_enabled is false" in str(exc)
    else:
        raise AssertionError("disabled pilot execution was not refused")


def test_execution_gate_refuses_authoritative_flag():
    protocol = valid_protocol(enabled=True)
    protocol["experiment"]["authoritative"] = True
    try:
        execution_gate(protocol)
    except RuntimeError as exc:
        assert "non-authoritative" in str(exc)
    else:
        raise AssertionError("authoritative pilot was not refused")


def test_execution_gate_refuses_roadblock_permission():
    protocol = valid_protocol(enabled=True)
    protocol["restrictions"]["may_supply_roadblock_candidates"] = True
    try:
        execution_gate(protocol)
    except RuntimeError as exc:
        assert "may_supply_roadblock_candidates" in str(exc)
    else:
        raise AssertionError("ROADBLOCK-enabled pilot was not refused")
