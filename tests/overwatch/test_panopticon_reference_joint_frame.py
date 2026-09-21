from pathlib import Path

PUBLISHER = Path("deploy/scripts/publish_initial_panopticon_frame.py")

def test_initial_panopticon_reference_frame_uses_canonical_motor_fields():
    text = PUBLISHER.read_text(encoding="utf-8")

    for field in (
        "head_yaw_deg",
        "head_pitch_deg",
        "left_antenna_deg",
        "right_antenna_deg",
        "left_wing_deg",
        "right_wing_deg",
        "left_foreleg",
        "right_foreleg",
        "left_midleg",
        "right_midleg",
        "left_hindleg",
        "right_hindleg",
    ):
        assert f'"{field}"' in text

    assert '"feed_mode"] = "REFERENCE"' in text
    assert "deployment_reference" in text
