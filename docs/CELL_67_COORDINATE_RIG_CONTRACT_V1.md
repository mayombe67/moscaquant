# CELL-67 Coordinate / Rig Contract v1

## Status

**Frozen public semantic contract.**

Contract ID: `CELL-67.COORDINATE-RIG.v1`

This document consolidates already-existing SITE-19B telemetry semantics before
the production MORTY rig becomes more detailed. It does **not** claim that
MoscaQuant has a validated biological neuromechanical controller.

## Canonical world frame

Frame: `CELL-67.WORLD.v1`

Units:

- distance: meter
- angle: degree
- force: newton
- velocity: meter/second

Axes:

- `+x` = subject right
- `+y` = forward from desk
- `+z` = up

Origin: `CELL-67 canonical desk-center floor projection`

The axis set is right-handed. No renderer may silently redefine this frame.
A renderer with different local axes must use an explicit presentation transform.

## Body orientation

- `body_pitch_deg` rotates about `+x`
- `body_roll_deg` rotates about `+y`
- `body_yaw_deg` rotates about `+z`
- positive rotation follows the right-hand rule
- `head_pitch_deg` uses local `+x`
- `head_yaw_deg` uses local `+z`

These definitions make the axis meaning explicit; they do not authorize the
frontend to invent pose values.

## Stable semantic rig IDs

```text
body.root
body.head
antenna.left
antenna.right
wing.left
wing.right
leg.front_left
leg.front_right
leg.mid_left
leg.mid_right
leg.hind_left
leg.hind_right
```

Renderer-specific names are implementation details. Internal aliases such as
`rear_left`, `middle_left`, mesh names, GLTF bone names, or Three.js object
names must not become competing scientific identifiers.

## Existing MotorStateV1 → semantic channels

The serialized `MotorStateV1` field names remain unchanged. v1 freezes this
alias layer:

```text
head_yaw_deg          -> body.head.yaw
head_pitch_deg        -> body.head.pitch
left_antenna_deg      -> antenna.left.angle
right_antenna_deg     -> antenna.right.angle
left_wing_deg         -> wing.left.angle
right_wing_deg        -> wing.right.angle
left_wing_velocity    -> wing.left.velocity
right_wing_velocity   -> wing.right.velocity
body_pitch_deg        -> body.root.pitch
body_roll_deg         -> body.root.roll
body_yaw_deg          -> body.root.yaw
locomotor_drive       -> drive.locomotor
grooming_drive        -> drive.grooming
courtship_drive       -> drive.courtship
escape_drive          -> drive.escape
left_foreleg          -> leg.front_left.joints
right_foreleg         -> leg.front_right.joints
left_midleg           -> leg.mid_left.joints
right_midleg          -> leg.mid_right.joints
left_hindleg          -> leg.hind_left.joints
right_hindleg         -> leg.hind_right.joints
```

This is a semantic alias layer, not a telemetry migration.

## Deliberately unfrozen semantics

All existing scalar `*_deg` angle fields are degrees. The six leg vectors are
angle vectors in degrees.

v1 deliberately does **not** assign anatomical joint names to leg-vector
indices. A placeholder renderer may map index `0` or `1` to a presentation
articulation, but that is not a validated coxa/femur/tibia mapping.

The existing wing-velocity fields are finite model values, but the public v1
sources do not freeze a physical unit for them. Do not relabel them as
degrees/second or radians/second without a later versioned contract.

Behavioral drive fields remain normalized `[0.0, 1.0]`.

## Environment IDs

- `CELL-67.v1`
- `CELL-67.BIRTHDAY.v1`

The birthday environment changes physical configuration explicitly; it does
not redefine `CELL-67.WORLD.v1`.

## Renderer boundary

Required architecture:

```text
CELL-67.WORLD.v1 telemetry
        ↓
explicit world → presentation transform
        ↓
renderer-local coordinates
        ↓
semantic-ID → renderer-node mapping
        ↓
mesh / rig interpolation
```

The transform belongs to the presentation implementation and must be explicit
and testable.

The private procedural Panopticon rig is a presentation implementation, not
the canonical rig. Its articulation choices and renderer-local names do not
define scientific joint identity.

Before production rig work proceeds, Panopticon should explicitly map the
canonical world axes, canonical front/mid/hind leg IDs, and authoritative
tether/root positions into renderer-local coordinates.

## Scientific boundary

This contract freezes representation and naming. It does not alter experimental
configuration, frozen results, neural dynamics, motor behavior, or scientific
authority.
