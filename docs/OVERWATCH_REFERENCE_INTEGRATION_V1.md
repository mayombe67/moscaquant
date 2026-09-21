# OVERWATCH Reference Neural → Motor → Physics Integration v1

## Purpose

This is the first public end-to-end reference path for SITE-19B:

```text
synthetic/reference neural state
        ↓
NeuralMotorAdapterV1
        ↓
motor.state
        ↓
CELL-67 reference constraint/contact resolution
        ↓
constraint.state
contact.state
        ↓
physics.pose
        ↓
physics.transition
```

Its job is to prove that the contracts compose and that provenance survives the complete path.

It is intentionally **not** the production MORTY neuromechanical implementation.

## Science-first boundary

The reference integration must not be confused with evidence that MQ-001 already possesses a
validated fly neuromechanical controller.

It uses a deliberately simple deterministic resolver.

The production system may later replace both:

- the neural → motor mapping;
- the motor → physics resolver.

The event contracts and provenance requirements should remain stable.

## Motor intent versus achieved motion

A core reason for this integration layer is to preserve the distinction between what the
model attempted and what CELL-67 allowed.

Example reference behavior:

```text
locomotor drive = 1.0
        ↓
requested forward displacement = 0.10 m
        ↓
CELL-67 tether allows 0.03 m
        ↓
root stops at 0.03 m
tether tension rises
forelegs brace
body pitch increases
```

The numbers in the reference resolver are plumbing constants, not biological findings.

They exist only to exercise the interfaces.

## Birthday behavior

The same reference path supports an untethered environment config.

For `CELL-67.BIRTHDAY.v1`:

```text
tether_enabled = false
```

Therefore the reference resolver:

- reports zero tether tension;
- does not impose the normal forward tether limit;
- still emits physics/contact/pose events.

This proves that the environment configuration can change physical outcome without changing
the neural/motor adapter.

## Provenance

A single reference integration step emits, in order:

1. `motor.state`
2. `constraint.state`
3. `contact.state`
4. `physics.pose`
5. `physics.transition`

The chain preserves:

- source neural-state reference;
- motor event ID;
- constraint event ID;
- contact event ID;
- achieved pose event ID;
- sample index;
- run/experiment/subject identity where provided.

This makes the step reconstructable for later deterministic replay.

## Determinism

Given the same:

- neural input;
- adapter version;
- reference physics config;
- sample ordering;

the computed motor/physics values are deterministic.

Event UUIDs and timestamps may differ between executions, but the scientific/reference payload
values should not.

A later replay layer should compare payload/state hashes rather than expecting regenerated
event IDs to match.

## Public/private boundary

Public `moscaquant` contains this intentionally simple integration path so researchers can
exercise and validate the interfaces.

**THIS THING OF OURS** may replace the reference mapping/resolver with:

- higher-fidelity neural readouts;
- descending/VNC mappings;
- biomechanical solvers;
- production MORTY rig mappings;
- real-time CELL-67 physics;
- high-fidelity rendering.

If a scientific claim materially depends on a private implementation, the relevant
methodology must be disclosed sufficiently to evaluate that claim.

## Next step

The next public infrastructure layer should focus on:

- deterministic state/payload hashing;
- replay frames;
- ordered high-frequency sampling;
- safe downsampling for Panopticon;
- detecting divergence between recorded and replayed state.

That will turn this event chain into a reproducible historical stream rather than merely a
live sequence.
