# MQ-7 — SC-03 BAD SYNAPSE Plasticity Mechanics Protocol

Status:

**PRE-REGISTERED / OUTCOMES NOT YET GENERATED**

## Purpose

Validate the mechanical and causal consequences of a bounded negative
synaptic-plasticity overlay before SC-03 is permitted to operate as an
adaptive live reinforcement condition.

This experiment tests plasticity mechanics only.

It does not define credit assignment for trading losses.

## Frozen pathway

The eligible validation pathway is:

`56393 → 68045 → 1273`

Frozen timing:

- `56393 → 68045` at frame 146
- `68045 → 1273` at frame 147

This pathway was preregistered and experimentally supported in MQ-5.4.

## Existing causal evidence

MQ-5.4 classified the following as SUPPORTED:

- upstream → intermediate dependence;
- upstream → downstream pathway propagation;
- intermediate → downstream dependence;
- dose-dependent pathway propagation.

Financial semantics remain NOT ASSIGNED.

## Plasticity intervention

SC-03 v1 mechanics use a multiplicative synaptic overlay.

For an eligible synapse:

`effective_weight = baseline_weight × 0.95`

Therefore:

- update magnitude: -5%
- baseline connectome artifact remains unchanged;
- structural connectome data are never rewritten;
- plasticity state is represented separately;
- overlay application must be deterministic and replayable.

## Validation interventions

The two frozen pathway edges are tested independently:

1. `56393 → 68045`
2. `68045 → 1273`

Each receives a -5% overlay independently.

No simultaneous dual-edge plasticity is tested in v1.

This avoids compounding two 5% changes into a larger pathway-level
perturbation.

## Primary measurements

For the upstream edge intervention measure:

1. change in 68045 response at F146;
2. change in 68045 effective activity at F147;
3. change in 1273 downstream response.

For the intermediate edge intervention measure:

1. change in 1273 response at F147;
2. integrated downstream change relative to baseline.

## Directional hypotheses

Reducing `56393 → 68045` by 5% is predicted to reduce the predefined
intermediate response and subsequently reduce the predefined downstream
response.

Reducing `68045 → 1273` by 5% is predicted to reduce the predefined
downstream response.

No minimum biological effect size is assumed.

A measurable zero or negligible effect remains a valid result.

## Required controls

- unchanged baseline;
- exact 1.00 multiplier sham;
- deterministic replay;
- frozen-artifact hash invariance;
- intervention telemetry verification;
- original connectome array equality before and after execution.

## Live SC-03 eligibility

Successful completion of this experiment validates only the mechanics of
bounded synaptic plasticity.

It does NOT activate SC-03 for live reinforcement.

Live SC-03 additionally requires a separately frozen credit-assignment
protocol defining how a recent pathway becomes eligible for negative
plasticity.

A financial loss by itself is insufficient evidence that any individual
synapse or pathway caused that loss.

Until credit assignment is frozen:

`plasticity_active = false`

If SC-03 is selected:

`NOT_APPLICABLE`

The result is not rerolled.

## Interpretation limits

A successful result supports causal effects of a bounded weight overlay
within the frozen MoscaQuant simulation.

It does not establish biological synaptic depression in living
Drosophila.

It does not establish learning.

It does not establish financial utility.

It does not establish that a pathway caused a profitable or losing trade.
