# OVERWATCH Motor Telemetry v1

## Purpose

Motor telemetry is the bridge between MoscaQuant's modeled neural/motor output and
Panopticon's eventual real-time 3D MORTY.

The core rule is:

> When model-derived motor state exists, Panopticon 3D renders that state rather than
> substituting canned action animations.

## Event families

### `motor.state`

Continuous pose/kinematic state.

Version 1 supports:

- head yaw / pitch;
- left/right antenna angles;
- left/right wing angles;
- left/right wing velocities;
- body pitch / roll / yaw;
- locomotor drive;
- grooming drive;
- courtship drive;
- escape drive;
- optional joint-angle vectors for six legs;
- neural-state provenance reference;
- source event linkage;
- sample index.

Angles are represented in degrees.

Drive values use `[0.0, 1.0]`.

The exact biomechanical mapping may become richer in later versions without changing the
principle that movement is telemetry-driven.

### `motor.activity`

Normalized channel activity for motor/readout pathways.

This is useful before a full pose solver exists. Panopticon may display activity directly,
but it must not pretend channel activity is a validated limb angle unless a frozen mapping
establishes that relationship.

### `motor.transition`

Links meaningful changes between motor states and the event that preceded them.

This supports questions such as:

- what changed after a market stimulus;
- what changed after an Oracle/Warden decision;
- what changed after reinforcement;
- whether a D6 event caused a transient or persistent motor-state change.

The event linkage is provenance. Scientific causality still requires an appropriate protocol.

## 2D versus 3D contract

The 2D portrait is an expressive interpretation layer.

It may map telemetry into a readable face/status representation.

The 3D model is different.

```text
neural / motor model
        |
        v
   motor.state
        |
        v
 Panopticon 3D rig
```

The 3D renderer should interpolate measured/model-derived pose values over time.

It should not implement rules such as:

```text
if shock:
    play canned shake animation
```

when actual motor-state telemetry is available.

## D6

A D6 reinforcement event may precede a motor-state change:

```text
reinforcement.applied
        |
        v
neural / internal-state change
        |
        v
motor.state
        |
        v
actual visible limb / wing / body response
```

The frontend should therefore show the model's resulting response rather than a punishment
animation invented by the UI.

## Trading / experiment analysis

The same rule applies while MoscaQuant processes market or experimental inputs.

If analysis changes modeled motor output, the 3D fly may visibly move its wings, legs,
antennae, head or body in real time.

This movement is not evidence of consciousness or subjective intent. It is a visualization
of the model-derived motor state.

## Sampling

Motor telemetry may become high-frequency.

OVERWATCH should preserve:

- source neural-state identity;
- monotonic sample/order identity;
- timestamps;
- run identity;
- experiment identity where applicable.

Cloud storage may batch samples into immutable segments without changing their order or
meaning.

## SAVE STATE

A checkpoint may eventually preserve a motor baseline alongside:

- neural state;
- plasticity;
- mood/internal state;
- reinforcement scars/persistent effects;
- lineage.

Restoring a checkpoint must not invent a default pose when a scientifically relevant motor
baseline is part of the saved state.

## Panopticon ownership

OVERWATCH owns the motor telemetry contract.

Panopticon owns:

- rigging;
- mesh;
- interpolation;
- rendering;
- camera;
- lighting;
- low-poly aesthetic;
- visualization of continuous movement.

Private ops owns transport, infrastructure and secrets.
