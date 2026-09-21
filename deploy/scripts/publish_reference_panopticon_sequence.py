#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from overwatch.events import TelemetryEventV1
from overwatch.motor import MotorStateV1
from overwatch.public_feed import write_latest_render_frame
from overwatch.streaming import StreamSampleV1, build_render_frame

RUN_ID = "site19b-reference-playback"
SUBJECT_ID = "MQ-001"
ENVIRONMENT_ID = "CELL-67.v1"

REFERENCE_SEQUENCE = (
    {
        "label": "neutral",
        "motor": MotorStateV1(),
        "root_y": 0.0,
        "tension": 0.0,
        "pitch": 0.0,
    },
    {
        "label": "orient",
        "motor": MotorStateV1(
            head_yaw_deg=10.0,
            head_pitch_deg=-4.0,
            left_antenna_deg=16.0,
            right_antenna_deg=-11.0,
        ),
        "root_y": 0.0,
        "tension": 0.0,
        "pitch": 0.0,
    },
    {
        "label": "foreleg-shift",
        "motor": MotorStateV1(
            head_yaw_deg=7.0,
            left_antenna_deg=12.0,
            right_antenna_deg=-7.0,
            left_foreleg=(18.0,),
            right_foreleg=(-15.0,),
            left_midleg=(-6.0,),
            right_midleg=(7.0,),
        ),
        "root_y": 0.0,
        "tension": 0.0,
        "pitch": 0.0,
    },
    {
        "label": "wing-articulation",
        "motor": MotorStateV1(
            left_wing_deg=30.0,
            right_wing_deg=-26.0,
            left_wing_velocity=0.30,
            right_wing_velocity=0.26,
            left_foreleg=(10.0,),
            right_foreleg=(-9.0,),
            left_hindleg=(6.0,),
            right_hindleg=(-5.0,),
        ),
        "root_y": 0.0,
        "tension": 0.0,
        "pitch": 0.0,
    },
    {
        "label": "locomotor-request",
        "motor": MotorStateV1(
            locomotor_drive=0.65,
            head_pitch_deg=-6.0,
            left_foreleg=(20.0,),
            right_foreleg=(-18.0,),
            left_midleg=(-12.0,),
            right_midleg=(13.0,),
            left_hindleg=(9.0,),
            right_hindleg=(-8.0,),
        ),
        "root_y": 0.032,
        "tension": 0.0,
        "pitch": 5.0,
    },
    {
        "label": "tether-response",
        "motor": MotorStateV1(
            locomotor_drive=0.90,
            head_pitch_deg=-8.0,
            left_foreleg=(24.0,),
            right_foreleg=(-22.0,),
            left_midleg=(-15.0,),
            right_midleg=(16.0,),
            left_hindleg=(11.0,),
            right_hindleg=(-10.0,),
        ),
        "root_y": 0.040,
        "tension": 0.18,
        "pitch": 8.0,
    },
    {
        "label": "return-neutral",
        "motor": MotorStateV1(
            head_yaw_deg=2.0,
            left_antenna_deg=4.0,
            right_antenna_deg=-3.0,
            left_wing_deg=6.0,
            right_wing_deg=-5.0,
            left_foreleg=(4.0,),
            right_foreleg=(-3.0,),
        ),
        "root_y": 0.010,
        "tension": 0.02,
        "pitch": 1.5,
    },
)


def build_reference_frame(step_index: int) -> dict:
    step = REFERENCE_SEQUENCE[step_index]
    motor = step["motor"]

    events = (
        TelemetryEventV1(
            event_type="motor.state",
            run_id=RUN_ID,
            component="motor",
            subject_id=SUBJECT_ID,
            payload={
                "motor": motor.to_dict(),
                "source": "deployment_reference_sequence",
                "reference_step": step_index,
                "reference_label": step["label"],
                "interpretation_boundary": (
                    "deterministic deployment reference playback; "
                    "not production MORTY behavior"
                ),
            },
            lore_surface="HUD",
        ),
        TelemetryEventV1(
            event_type="constraint.state",
            run_id=RUN_ID,
            component="physics",
            subject_id=SUBJECT_ID,
            payload={
                "constraint": {
                    "environment_id": ENVIRONMENT_ID,
                    "tether_enabled": True,
                    "tether_tension_n": step["tension"],
                    "root_position": {"x": 0.0, "y": step["root_y"], "z": 0.08},
                },
                "source": "deployment_reference_sequence",
                "reference_step": step_index,
                "reference_label": step["label"],
            },
            lore_surface="HUD",
        ),
        TelemetryEventV1(
            event_type="physics.pose",
            run_id=RUN_ID,
            component="physics",
            subject_id=SUBJECT_ID,
            payload={
                "pose": {
                    "root_position": {"x": 0.0, "y": step["root_y"], "z": 0.08},
                    "body_pitch_deg": step["pitch"],
                    "body_roll_deg": 0.0,
                    "body_yaw_deg": 0.0,
                },
                "source": "deployment_reference_sequence",
                "reference_step": step_index,
                "reference_label": step["label"],
            },
            lore_surface="HUD",
        ),
    )

    samples = tuple(
        StreamSampleV1(sequence=i, event=event)
        for i, event in enumerate(events)
    )

    frame = build_render_frame(samples, frame_index=step_index).to_dict()
    frame["feed_mode"] = "REFERENCE"
    frame["status_text"] = (
        f"SITE-19B REFERENCE PLAYBACK // "
        f"{step_index + 1}/{len(REFERENCE_SEQUENCE)} // {step['label'].upper()}"
    )
    frame["reference_playback"] = {
        "sequence_id": "cell67.semantic-rig.v1",
        "step_index": step_index,
        "step_count": len(REFERENCE_SEQUENCE),
        "label": step["label"],
        "authoritative_subject_data": False,
    }
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Publish deterministic SITE-19B REFERENCE frames."
    )
    parser.add_argument("destination", type=Path)
    parser.add_argument("--interval", type=float, default=1.5)
    parser.add_argument("--loops", type=int, default=1)
    parser.add_argument(
        "--hold-last",
        action="store_true",
        help="Leave final sequence frame published instead of restoring neutral.",
    )
    args = parser.parse_args()

    if args.interval < 0.1:
        raise SystemExit("--interval must be at least 0.1 seconds")
    if args.loops < 1:
        raise SystemExit("--loops must be >= 1")

    for loop_index in range(args.loops):
        for step_index in range(len(REFERENCE_SEQUENCE)):
            frame = build_reference_frame(step_index)
            write_latest_render_frame(frame, args.destination)
            print(
                json.dumps(
                    {
                        "loop": loop_index + 1,
                        "step": step_index,
                        "label": REFERENCE_SEQUENCE[step_index]["label"],
                        "frame_sha256": frame["frame_sha256"],
                    }
                )
            )
            time.sleep(args.interval)

    if not args.hold_last:
        neutral = build_reference_frame(0)
        neutral["status_text"] = "SITE-19B REFERENCE PLAYBACK COMPLETE // NEUTRAL"
        write_latest_render_frame(neutral, args.destination)
        print(json.dumps({"complete": True, "restored": "neutral"}))


if __name__ == "__main__":
    main()
