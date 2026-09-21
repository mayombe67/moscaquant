from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPT = Path("deploy/scripts/publish_reference_panopticon_sequence.py")


def load_module():
    spec = spec_from_file_location("reference_sequence", SCRIPT)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_reference_sequence_is_explicitly_non_authoritative():
    module = load_module()

    assert len(module.REFERENCE_SEQUENCE) == 7

    labels = [step["label"] for step in module.REFERENCE_SEQUENCE]
    assert labels == [
        "neutral",
        "orient",
        "foreleg-shift",
        "wing-articulation",
        "locomotor-request",
        "tether-response",
        "return-neutral",
    ]

    for index in range(len(module.REFERENCE_SEQUENCE)):
        frame = module.build_reference_frame(index)
        assert frame["feed_mode"] == "REFERENCE"
        assert frame["reference_playback"]["authoritative_subject_data"] is False
        assert frame["reference_playback"]["step_index"] == index
        assert frame["reference_playback"]["step_count"] == 7


def test_reference_sequence_exercises_semantic_motor_channels():
    module = load_module()

    frames = [module.build_reference_frame(i) for i in range(7)]
    motor_payloads = [
        next(
            event["payload"]["motor"]
            for event in frame["public_events"]
            if event["event_type"] == "motor.state"
        )
        for frame in frames
    ]

    assert any(payload["head_yaw_deg"] != 0.0 for payload in motor_payloads)
    assert any(payload["left_antenna_deg"] != 0.0 for payload in motor_payloads)
    assert any(payload["left_wing_deg"] != 0.0 for payload in motor_payloads)
    assert any(payload["left_foreleg"] for payload in motor_payloads)
    assert any(payload["locomotor_drive"] > 0.0 for payload in motor_payloads)
