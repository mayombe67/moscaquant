# OVERWATCH Constraint, Contact & Physics Telemetry v1

## Purpose

Motor telemetry records what the model attempts to do.

Physics telemetry records what CELL-67 actually allows to happen.

These are intentionally separate.

```text
motor intent / motor state
        |
        v
CELL-67 constraints + contacts
        |
        v
achieved physical pose
        |
        v
Panopticon 3D
```

This distinction is essential while MQ-001 is physically constrained.

A high forward locomotor drive may produce:

- little or no root translation;
- increased tether tension;
- body pitch;
- leg bracing;
- slipping contacts;
- wing/head/antenna motion.

Panopticon should show that physical outcome rather than pretending either that the motor
command succeeded fully or that MQ-001 was motionless.

## Canonical coordinate frame

Version 1 freezes:

`CELL-67.WORLD.v1`

Units:

- distance: meter
- angle: degree
- force: newton
- velocity: meter/second

Axes:

- `+x` = subject right
- `+y` = forward from desk
- `+z` = up

Origin:

`CELL-67 canonical desk-center floor projection`

Future environment revisions may add transforms, but they must not silently redefine the
meaning of this frame.

## Event families

### `constraint.state`

Records:

- environment identity;
- tether enabled/disabled;
- tether anchor;
- tether length;
- instantaneous tether tension;
- root position;
- root displacement;
- whether the constraint is saturated;
- source motor event;
- sample index.

When the tether is disabled, reported tether tension must be zero.

This makes `CELL-67.BIRTHDAY.v1` mechanically distinguishable from normal containment.

### `contact.state`

Records zero or more physical contacts.

Each contact includes:

- stable contact ID;
- body-part/channel ID;
- environment surface ID;
- world-space position;
- normal force;
- tangential force;
- slipping state.

Examples include:

- foreleg contacting desk;
- hindleg bracing on floor;
- antenna contacting a prop;
- body contacting chair/restraint surface;
- party-hat/cake/balloon interaction when collision/contact logic exists.

### `physics.pose`

Records the achieved root/body pose after motor output has passed through physical
constraints and contacts.

Panopticon 3D should use this achieved pose as the physical root transform.

Detailed limb and wing channels may continue to come from `motor.state` or a future
validated joint/physics solver.

### `physics.transition`

Links:

```text
motor event
constraint event
contact event
pose event
```

This makes the complete movement path replayable.

The linkage is provenance. Scientific causality still requires an appropriate experimental
design.

## Stable channel naming

Panopticon, physics and model adapters should converge on stable semantic IDs rather than
renderer-specific bone names.

Examples:

```text
body.root
body.head
antenna.left
antenna.right
wing.left
wing.right

leg.front_left.*
leg.front_right.*
leg.mid_left.*
leg.mid_right.*
leg.hind_left.*
leg.hind_right.*
```

A renderer may map those IDs to Blender/Three.js/GLTF bones internally.

The telemetry contract should not depend on those renderer-specific names.

## CELL-67 tether

The normal chain/tether is modeled as a physical/environment constraint.

It is not an animation trigger.

Expected behavior:

```text
forward motor drive rises
        |
        v
root moves until allowed by physics
        |
        +--> contact forces may change
        |
        +--> tether tension may rise
        |
        +--> body pose may change
        |
        v
Panopticon displays achieved motion
```

The chain may therefore visibly pull taut because the physics state says it did.

The frontend must not animate chain tension solely because a punishment, market event or
other dramatic event occurred.

## Birthday exception

`CELL-67.BIRTHDAY.v1` explicitly disables the tether.

For that environment:

- tether tension must report zero;
- room roaming may be enabled;
- physical collisions and contacts still apply;
- interactive prop contacts remain observable;
- the normal tether returns only when the environment is restored.

## 3D rendering boundary

The preferred future render path is:

```text
motor.state
   +
constraint.state
   +
contact.state
        |
        v
physics.pose
        |
        v
Panopticon 3D
```

Interpolation for smooth rendering is allowed.

Inventing a biological/physical response that did not occur in telemetry is not.

## Sampling

Physics telemetry may be high-frequency.

The raw ordered stream may eventually be batched into immutable OVERWATCH segments.

Public Panopticon may receive a downsampled/interpolated projection, provided:

- source order is preserved;
- event identity/provenance remains available;
- downsampling does not alter the underlying scientific record;
- deterministic replay can use the authoritative stream.

## Future work

This contract intentionally precedes the actual neuromechanical solver.

Future adapters may map:

- descending-neuron activity;
- VNC/motor-controller outputs;
- NeuroMechFly-style joint targets;
- collision/contact solver state;
- GLTF/Three.js rig channels.

The adapter may improve.

The evidence boundaries should remain stable.
