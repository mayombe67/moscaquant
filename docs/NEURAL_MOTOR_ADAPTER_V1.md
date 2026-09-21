# Neural → Motor Adapter Contract v1

## Purpose

MoscaQuant now has public telemetry contracts for:

```text
neural/readout state
        ↓
motor.state
        ↓
constraint/contact physics
        ↓
physics.pose
        ↓
Panopticon
```

This document freezes the public boundary between neural/readout state and motor telemetry.

## Science-first rule

The adapter must not engineer desired behavior into MQ-001.

Its purpose is to expose whatever motor consequence follows from the modeled neural/readout
state under a declared mapping.

A disappointing motor result is still a result.

A visually interesting result is not automatically a scientifically meaningful one.

## Public interface

The public `NeuralMotorAdapterV1` contract requires:

- stable `adapter_id`;
- stable `adapter_version`;
- `map_state(...)`;
- output as `MotorStateV1`.

This allows alternative implementations to plug into the same OVERWATCH/Panopticon pipeline.

## Reference implementation

`ReferenceNeuralMotorAdapterV1` is intentionally boring.

It maps a small set of named scalar channels into normalized behavioral drives and wing
velocity fields.

It exists to demonstrate:

- interface compatibility;
- validation;
- provenance;
- end-to-end telemetry plumbing.

It is **not** the production MORTY mapping.

It must not be used to imply that the full connectome has already been translated into a
validated neuromechanical controller.

## Production implementation

A higher-fidelity implementation may remain private inside **THIS THING OF OURS** when it is
part of the product/experience layer.

However:

> If a published scientific claim materially depends on the proprietary mapping, enough of
> the mapping methodology must be disclosed for that claim to be independently evaluated.

This preserves the open-core rule:

> **Open the evidence. Protect the experience.**

## Provenance

Every adapter used for a meaningful run should identify:

- adapter ID;
- adapter version;
- methodology/document reference where applicable;
- implementation visibility (`public` or `private`);
- source neural-state reference;
- resulting motor-state event.

Future OVERWATCH integration may include these fields directly in a dedicated
`motor.mapping` event.

## No canned behavior

An adapter must not contain presentation rules such as:

```text
if punishment:
    shake wings dramatically
```

unless that behavior is itself part of a frozen experimental model.

Presentation layers may visualize state.

Motor mapping must remain model-derived.

## Future biological mapping

A future adapter may incorporate progressively stronger biological grounding, for example:

- descending-neuron activity;
- VNC/motor pathway outputs;
- motor-neuron populations;
- muscle activation proxies;
- joint target generation;
- NeuroMechFly-style controller interfaces;
- experimentally derived wing/leg mappings.

Those additions should be versioned rather than silently changing an established adapter.

## Failure is valid

The project does not tune the core fly merely to make Panopticon entertaining.

If MQ-001 produces:

- weak locomotor output;
- asymmetrical movement;
- unstable control;
- ineffective action;
- no useful trading behavior;

those outcomes remain observable scientific results.

The infrastructure should reveal the result, not manufacture success.
