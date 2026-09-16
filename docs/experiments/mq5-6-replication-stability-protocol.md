# MQ-5.6 — Replication and Stability Protocol

Status:

**PRE-REGISTERED / REPLICATION NOT YET EXECUTED**

## Purpose

MQ-5.6 distinguishes:

1. implementation reproducibility,
2. scientific robustness across an independent implementation.

Exact reruns of the existing MoscaQuant runtime have already established
deterministic software reproducibility.

MQ-5.6 therefore focuses on an independently implemented reduced-circuit
reference model for selected, previously accepted causal findings.

## Selected replication set

The replication set is frozen before independent-runtime outcomes are
generated.

### Direct-edge showcase

`43417 → 656`

Frozen causal frame:

`F145`

Reason for inclusion:

- strongest direct showcase
- clear causal onset
- prospectively documented matched-control infeasibility
- substantial measurable effect

### Multi-hop showcase

`56393 → 68045 → 1273`

Frozen causal frames:

- `56393 → 68045 @ F146`
- `68045 → 1273 @ F147`

Reason for inclusion:

- only explicit two-hop path in the frozen causal graph
- tests propagation through an intermediate node
- previously supported in MQ-5.4 and CONF-004A

### Convergence showcase

`44274 + 55925 → 55`

Frozen causal frame:

`F146`

Reason for inclusion:

- cleanest convergent-input system
- measurable effect magnitude
- combined perturbation previously exceeded either single input
- avoids the extreme numerical-scale limitation of responder 51

## Independent implementation requirement

The MQ-5.6 reference implementation must not:

- subclass the current physiology runtime
- call the current runtime `step()` implementation
- call the current runtime `effective_activity()` implementation
- reuse the MQ-5 intervention runtime's attenuation machinery
- mutate frozen artifacts

It may reuse:

- frozen connectome artifacts
- frozen model-index identities
- frozen physiological constants
- frozen market observations
- frozen sensory input artifacts or equivalent frozen stimulus arrays
- scientific configuration values

The purpose is to reproduce the scientific calculation through a separate
implementation path.

## Reduced-circuit scope

The reference implementation may simulate only the neurons and incoming
terms necessary to reproduce the selected causal relationships.

Any reduced-circuit simplification must be explicit.

The reference calculation must preserve the relevant scientific equations,
weights, decay behavior, release behavior, intervention magnitude, and
frame semantics.

## Intervention conditions

For each selected finding, test:

- baseline
- zero-effect sham
- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation

For the convergence system additionally test:

- input A only
- input B only
- combined A+B

## Primary replication questions

### Direct edge

Does attenuation of 43417 at F145 produce the same directional and
dose-ordered change in 656 under the independent implementation?

### Multi-hop path

Does attenuation of 56393 at F146:

1. reduce 68045 at F146,
2. reduce 68045 effective activity at F147,
3. reduce 1273 downstream?

Does independent attenuation of 68045 at F147 reduce 1273?

### Convergence

Do both 44274 and 55925 independently contribute to 55?

Does combined attenuation exceed either individual perturbation?

Does combined attenuation remain dose ordered?

## Numerical comparison

For each replicated measurable quantity, report:

- existing-runtime value
- reference-runtime value
- absolute difference
- relative difference where numerically meaningful

No numerical tolerance will be invented after results are inspected.

Before execution, the implementation must declare its comparison tolerance.

Very small values near numerical precision must be reported separately and
must not dominate aggregate conclusions.

## Stability classifications

Each tested finding may be reported as:

- `REPLICATED`
- `DIRECTIONALLY_REPLICATED_WITH_MAGNITUDE_DIFFERENCE`
- `NOT_REPLICATED`
- `NUMERICALLY_INCONCLUSIVE`

These labels apply only to the frozen simulation model.

## Randomness

The current experiment is deterministic.

No multi-seed test is required because no stochastic component is present.

If stochastic behavior is introduced in a later experiment, seeds must be
predefined before outcome generation.

## Scope limits

Independent reduced-circuit replication can reduce concern about dependence
on the current MoscaQuant runtime implementation.

It does not establish biological causality.

It does not establish financial usefulness.

Financial semantics remain:

**NOT ASSIGNED**
