# MQ-5.3 — Single-Node Perturbation

Status:

**COMPLETE**

MQ-5.3 required controlled interventions against the selected frozen causal
nodes with comparison against predefined controls and measurement of
downstream response, latency, and persistence.

These experiments were executed during generalized validation of the
MQ-5.2 intervention harness rather than repeated in a separate runner.

No additional experiment was performed solely to satisfy the phase label.

## Frozen intervention set

The complete 13-edge MQ-3 causal set was tested.

Each causal source received:

- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation
- zero-effect sham
- prospectively selected timing control
- matched non-causal control where scientifically feasible

## Results

Validation:

- 13 / 13 experiments completed
- 13 / 13 shams exactly matched baseline
- 13 / 13 dose applications verified
- 13 / 13 deterministic full-silencing replicates reproduced exactly
- frozen artifacts remained unchanged

Primary intervention result:

- 13 / 13 causal edges exhibited monotonic reduction in integrated
  downstream response with increasing source attenuation

Matched-control result:

- 12 / 12 causal interventions produced a larger downstream effect than
  the prospectively selected matched non-causal control
- 1 / 13 had no scientifically valid matched control available and was
  prospectively documented as infeasible

Latency:

- complete source silencing delayed first positive downstream response in
  7 / 13 cases

Timing:

- causal-frame intervention exceeded the nearby timing-control effect in
  3 / 13 cases
- nearby timing intervention was equal or larger in 10 / 13 cases

The timing result does not support single-frame temporal exclusivity as a
general property.

Instead, the evidence-defined causal frame frequently lies within a
broader active causal window.

## Result classification

Single-node causal intervention:

**SUPPORTED — 13 / 13 MONOTONIC DOSE RESPONSE**

Source specificity where matched control exists:

**SUPPORTED — 12 / 12**

Single-frame temporal exclusivity:

**NOT SUPPORTED AS A GENERAL PROPERTY**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Source artifacts

- `mq5-generalized-intervention-matrix-v1.json`
- `mq5-generalized-intervention-matrix-v1.npz`

Primary interpretation:

- `docs/experiments/mq5-2-generalized-results.md`

MQ-5.3 introduces no replacement or modified experimental artifact.

The MQ-5.2 artifacts remain immutable.

## Next

Proceed to:

**MQ-5.4 — Pathway Perturbation**

Primary frozen path:

`56393 → 68045 → 1273`
