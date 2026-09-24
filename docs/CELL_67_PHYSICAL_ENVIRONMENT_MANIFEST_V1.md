# CELL-67 Physical Environment Manifest v1

## Status

**Frozen public provenance contract for the deterministic reference resolver.**

Schema ID:

`CELL-67.PHYSICAL-ENVIRONMENT-MANIFEST.v1`

Reference physics profile:

`CELL-67.REFERENCE-PHYSICS.v1`

This contract gives CELL-67 environment state a deterministic canonical payload
and SHA-256 identity.

It does **not** claim that production room geometry, production collision meshes,
or a biologically validated neuromechanical solver already exist.

## Why this exists

`environment_id = CELL-67.v1` identifies a configuration family, but an
environment ID alone is not enough to prove exactly which physical resolver
parameters produced an achieved pose.

The manifest therefore records the current reference-resolver inputs together
with declared physical-environment identity/state and gives that combined
provenance a stable hash.

Some declared physical props are not yet consumed by the deterministic reference
resolver. Their inclusion records environment identity; it does not imply that
the reference solver currently models their geometry or collisions.

## Canonical serialization

The canonical JSON representation uses:

- UTF-8;
- sorted object keys;
- no insignificant whitespace;
- JSON separators `,` and `:`;
- non-ASCII text preserved;
- NaN/infinity rejected.

The manifest SHA-256 is computed over that canonical JSON only.

The hash never includes itself.

## Scope

Version 1 has:

```text
physics_authority = deterministic_reference_resolver_only
production_geometry_frozen = false
```

That distinction is mandatory.

The manifest is exact provenance for the current public reference resolver. It
must not be presented as a frozen production-room collision model.

## Frozen reference physics parameters

The manifest captures the existing `ReferencePhysicsConfigV1` values:

```text
environment_id
tether_enabled
tether_anchor_m
tether_length_m
max_root_forward_m
forward_gain_m
tension_gain_n
pitch_gain_deg
bracing_threshold
```

No value is changed by this contract.

## Frozen resolver constants

The current reference resolver also contains constants outside
`ReferencePhysicsConfigV1`. They affect physical output and therefore belong in
the manifest:

```text
root x                       = 0.00 m
root z                       = 0.08 m

brace contact IDs            = reference.front-left-brace
                               reference.front-right-brace
brace body parts             = leg.front_left.tarsus
                               leg.front_right.tarsus
brace lateral x              = -0.02 m, +0.02 m
brace forward offset         = +0.05 m
brace z                      = 0.75 m
brace normal-force bias      = 0.05 N
brace surface                = desk.primary.surface
```

These remain plumbing/reference constants, not biological findings.

## Environment state

The manifest records:

```text
environment_id
base_environment_id
tether_enabled
room_roaming_enabled
temporary
exploratory_condition
restoration_environment_id
```

Only non-presentation-only props enter the physical manifest.

Presentation copy, monitor themes, banners, and other presentation-only metadata
do not change the physical hash.

## Physical prop identity

For each physical/non-presentation prop, v1 records:

```text
prop_id
kind
interactive
wearable
consumable
attractive
persistent_after_session
```

This deliberately excludes decorative metadata that does not participate in the
reference physical resolver.

## Surface IDs

The deterministic reference resolver currently exposes one physical contact
surface:

`desk.primary.surface`

Additional production surfaces require a later declared physical manifest.

## Deliberately unfrozen production geometry

The following remain explicitly outside v1:

```text
room_collision_geometry
prop_collision_shapes_and_world_poses
production_joint_contact_geometry
```

Their absence is not silently filled with renderer geometry.

When a production solver begins depending on them, they must enter a new
versioned physical manifest before scientific/replay provenance relies on them.

## Standard reference manifest

`CELL-67.v1` uses the existing tethered environment configuration and the
existing reference physics parameters.

Expected canonical SHA-256:

`302d57c4afba219964cfbe93b9de5ff093c8240ab6acec2a201b8943ef1ebbf8`

## Birthday reference manifest

`CELL-67.BIRTHDAY.v1` uses the existing temporary exploratory environment with
the tether disabled. Other reference physics parameters remain unchanged.

Expected canonical SHA-256:

`b161eb12500ebbcae42703474eeeadaa241d75b4a209eba46faa8caaab1f24c1`

## Telemetry event

`environment.manifest` may record the canonical payload and hash at run
provenance time.

Adding this event does not alter existing `motor.state`, `constraint.state`,
`contact.state`, or `physics.pose` payloads.

A later integration layer may bind a pose/replay segment directly to the
manifest hash. That linkage must be additive and must not rewrite historical
events.

## Scientific boundary

This contract freezes provenance representation for existing reference physics.

It does not:

- alter `CELL-67.WORLD.v1`;
- alter environment behavior;
- alter the reference resolver;
- invent production geometry;
- alter frozen experimental results;
- turn presentation geometry into science.
