#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from overwatch.events import TelemetryEventV1
from overwatch.streaming import StreamSampleV1, build_render_frame
from overwatch.public_feed import write_latest_render_frame


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: publish_initial_panopticon_frame.py "
            "/path/to/latest-render-frame.json"
        )

    destination = Path(sys.argv[1])

    events = (
        TelemetryEventV1(
            event_type="motor.state",
            run_id="site19b-initial",
            component="motor",
            subject_id="MQ-001",
            payload={
                "motor": {
                    # Explicit MotorStateV1 field names.
                    # This is a deployment reference pose used only to prove the
                    # public RenderFrameV1 -> Panopticon semantic-rig path.
                    "head_yaw_deg": 6.0,
                    "head_pitch_deg": -3.0,
                    "left_antenna_deg": 10.0,
                    "right_antenna_deg": -8.0,
                    "left_wing_deg": 22.0,
                    "right_wing_deg": -18.0,
                    "left_wing_velocity": 0.0,
                    "right_wing_velocity": 0.0,
                    "body_pitch_deg": 0.0,
                    "body_roll_deg": 0.0,
                    "body_yaw_deg": 0.0,
                    "locomotor_drive": 0.0,
                    "grooming_drive": 0.0,
                    "courtship_drive": 0.0,
                    "escape_drive": 0.0,
                    "left_foreleg": [14.0],
                    "right_foreleg": [-12.0],
                    "left_midleg": [-8.0],
                    "right_midleg": [9.0],
                    "left_hindleg": [7.0],
                    "right_hindleg": [-6.0],
                },
                "source": "deployment_reference",
            },
            lore_surface="HUD",
        ),
        TelemetryEventV1(
            event_type="constraint.state",
            run_id="site19b-initial",
            component="physics",
            subject_id="MQ-001",
            payload={
                "constraint": {
                    "environment_id": "CELL-67.v1",
                    "tether_enabled": True,
                    "tether_tension_n": 0.0,
                    "root_position": {"x": 0.0, "y": 0.0, "z": 0.08},
                },
                "source": "deployment_reference",
            },
            lore_surface="HUD",
        ),
        TelemetryEventV1(
            event_type="physics.pose",
            run_id="site19b-initial",
            component="physics",
            subject_id="MQ-001",
            payload={
                "pose": {
                    "root_position": {"x": 0.0, "y": 0.0, "z": 0.08},
                    "body_pitch_deg": 0.0,
                    "body_roll_deg": 0.0,
                    "body_yaw_deg": 0.0,
                },
                "source": "deployment_reference",
            },
            lore_surface="HUD",
        ),
    )

    samples = tuple(
        StreamSampleV1(sequence=i, event=event)
        for i, event in enumerate(events)
    )

    frame = build_render_frame(samples, frame_index=0).to_dict()
    frame["feed_mode"] = "REFERENCE"
    frame["status_text"] = "SITE-19B PUBLIC FEED INITIALIZED"

    write_latest_render_frame(frame, destination)

    print(json.dumps(frame, indent=2))
    print(f"\npublished: {destination}")


if __name__ == "__main__":
    main()
