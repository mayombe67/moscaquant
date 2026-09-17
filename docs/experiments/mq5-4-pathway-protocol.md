# MQ-5.4 — Pathway Perturbation Protocol

Status:

**PRE-REGISTERED / OUTCOMES NOT YET GENERATED**

## Frozen pathway

`56393 → 68045 → 1273`

This is the only explicit two-hop path preserved in the frozen MQ-3 causal
graph.

Frozen timing:

- `56393 → 68045` at frame 146
- `68045 → 1273` at frame 147

## Research question

Does perturbing the predefined upstream node propagate through the
predefined intermediate node and subsequently alter the predefined
downstream target?

## Experiments

### Upstream perturbation

Perturb neuron 56393 at frame 146 using:

- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation

Measure:

1. activity removed from neuron 56393
2. resulting response of neuron 68045
3. effective activity subsequently emitted by neuron 68045
4. resulting response of neuron 1273

### Intermediate perturbation

Perturb neuron 68045 at frame 147 using the same attenuation series.

Measure the resulting response of neuron 1273.

The existing MQ-5.3 single-node result for `68045 → 1273` may be used as
supporting evidence but the MQ-5.4 runner must capture pathway telemetry
explicitly.

## Directional hypotheses

Upstream attenuation is predicted to reduce the response of neuron 68045.

Upstream attenuation is also predicted to reduce downstream response in
neuron 1273 through the predefined pathway.

Intermediate attenuation is predicted to reduce downstream response in
neuron 1273.

Increasing attenuation is expected to produce downstream change in the
predicted direction.

No assumption of equal effect magnitude between hops is made.

No synergy or linear-composition claim is pre-registered.

## Frame semantics

An intervention assigned to frame F modifies presynaptic effective
activity used during simulation step F.

The post-step neural state is recorded as frame F.

Therefore:

- intervention on 56393 occurs at F146
- the resulting 68045 state is observed at F146
- effective activity emitted by 68045 during F147 is then measured
- downstream state of 1273 is observed at F147 and afterward

## Controls

Required:

- unchanged baseline
- exact zero-effect sham
- intervention-telemetry verification
- deterministic full-silencing replicate
- frozen-artifact hash invariance

No new control may be selected after pathway outcomes are observed.

## Interpretation limits

Successful propagation supports simulated pathway dependence within the
frozen MoscaQuant model.

It does not establish equivalent pathway causality in living Drosophila.

It does not establish financial utility.

Financial semantics remain:

**NOT ASSIGNED**
