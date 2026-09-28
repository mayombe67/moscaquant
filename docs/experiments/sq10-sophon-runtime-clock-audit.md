# SQ-10 — SOPHON Runtime Clock Audit

## Status

PRE-PREREGISTRATION IMPLEMENTATION AUDIT

No neural execution is authorized by this document.

## Purpose

SQ-10 requires source-side state at the phase where each Tm4 source actually
contributes to synaptic propagation.

SQ-08 preserved responder state only after completion of `runtime.step()` and
therefore did not preserve the source-side transmission state required for this
mechanistic question.

## Frozen runtime sequence

The inspected runtime is:

`brain/physiology_constrained_visual_transduction.py`

Within each frame the relevant sequence is:

### P0 — committed pre-step state

At entry to `step()`:

- `self.voltage` contains the state surviving the preceding frame;
- `self.spikes` contains the preceding committed spike state.

The runtime binds:

`prior_spikes = self.spikes`

before later spike replacement.

### P1 — raw effective activity

`effective_activity()` begins from a copy of the committed spikes.

For the frozen graded Tm2/Tm3/Tm4 population:

    graded_voltage =
        clip(voltage, 0, threshold)

    graded_activity =
        graded_voltage / threshold

    activity[graded] =
        maximum(spikes[graded], graded_activity)

This is the raw effective graded source state.

### P2 — transmission activity

The raw effective activity may pass through `activity_modifier`.

The vector remaining after that optional modifier is the actual activity vector
consumed by the connectome.

SQ-10 therefore defines:

`source_effective_activity_pre_synaptic`

as the source coordinate from the activity vector that is actually supplied to
the connectome matrix multiplication.

This definition remains correct even if an activity modifier exists.

### P3 — synaptic multiplication

The runtime computes:

    synaptic =
        connectome @ effective_activity

For a BODY source `s` and responder `r`, the direct edge contribution prior to
later network-state divergence is:

    effective_activity[s] * connectome[r, s]

SQ-10 must preserve the effective activity and frozen edge weight required to
reproduce this scalar contribution exactly, or preserve the scalar directly.

### P4 — decay

After synaptic construction:

    voltage *= decay

### P5 — integration / pre-threshold voltage

The runtime then adds:

- synaptic input;
- external stimulus;
- relay release contribution where applicable.

The resulting voltage immediately before threshold evaluation is the
scientifically relevant responder pre-threshold state.

SQ-10 defines:

`responder_voltage_pre_threshold`

at this phase.

### P6 — firing decision

The runtime evaluates:

    fired =
        voltage >= threshold

SQ-10 defines:

`responder_fired`

from this decision before reset.

### P7 — committed post-step state

The runtime:

- clears the old spike array;
- commits `1.0` for fired neurons;
- resets voltage for fired neurons.

This produces:

- post-commit spikes;
- post-reset voltage.

These are the states historically preserved by the SQ-08 mechanistic readout.

## SQ-08 relationship

SQ-08 performed:

    runtime.step(stimulus)

before capturing:

- primary DN voltage;
- primary DN spikes;
- BODY responder voltage;
- BODY responder spikes;
- frontier voltage;
- frontier spikes.

Therefore SQ-08 BODY voltage is a P7 post-step/post-reset measurement.

It is not a preserved P0/P1/P2 source-state measurement and it is not a
preserved P5 pre-threshold responder measurement.

## SOPHON required phase-resolved measurements

For each source A/B/C and every frame:

### Source

- `source_voltage_pre_step`
- `source_spikes_pre_step`
- `source_effective_activity_pre_synaptic`

For each corresponding responder and every frame:

### Responder

- `responder_voltage_pre_threshold`
- `responder_fired`
- `responder_voltage_post_reset`
- `responder_spikes_post_commit`

For each BODY edge and every frame:

### Edge

Either preserve directly or permit exact deterministic derivation of:

- `direct_edge_contribution`

defined from:

    source_effective_activity_pre_synaptic * frozen_edge_weight

## Mechanistic comparison

The simplest direct-transmission model predicts that, before recurrent
divergence alters other state, the retained-versus-lesioned responder
difference should be attributable to removal of the corresponding direct edge
contribution.

SQ-10 must not assume this equality.

It is a prospective hypothesis to test.

Later-frame deviations from the direct contribution may indicate recurrent
feedback, altered parallel inputs, cross-path coupling, threshold effects, or
other state divergence.

## Measurement principle

The experiment must distinguish:

1. the state that enters the synaptic calculation;
2. the responder voltage before threshold/reset;
3. the state remaining after spike commit/reset.

No generic unqualified `source_voltage[t]` or `responder_voltage[t]` field is
sufficient.

## Authorization boundary

This audit resolves timing terminology only.

It does not:

- freeze the final evidence schema;
- preregister SQ-10;
- authorize neural execution.
