# MQ-5.6 — Replication and Stability Results

Status:

**SUPPORTED — INDEPENDENT FULL-NETWORK REPLICATION**

Scope:

**Frozen MoscaQuant simulation model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Purpose

MQ-5.6 tested whether selected accepted MQ-5 findings depended on the
production MoscaQuant neural runtime implementation.

A separate full-network reference runtime was implemented before outcome
generation.

The reference implementation did not:

- inherit from the production visual-transduction runtime
- call the production runtime `step()` method
- call the production runtime `effective_activity()` method
- call the MQ-5 intervention runtime
- modify frozen connectome artifacts

The reference runtime independently implemented the frozen scientific
equations and intervention semantics.

## Frozen replication set

### Direct edge

`43417 → 656 @ F145`

### Two-hop pathway

`56393 → 68045 @ F146`

`68045 → 1273 @ F147`

### Convergence system

`44274 + 55925 → 55 @ F146`

## Predefined numerical tolerance

Before outcomes were generated:

- absolute tolerance: `1e-12`
- relative tolerance: `1e-6`
- small-value threshold: `1e-12`

No tolerance was changed after outcome inspection.

## Independent-runtime result

The MQ-5.6 reference execution completed successfully.

Validation:

- frozen artifacts unchanged: `True`
- direct numeric replication: `True`
- pathway numeric replication: `True`
- convergence numeric replication: `True`
- convergence combined-dose monotonicity: `True`
- convergence combined effect exceeded either single input: `True`

Runtime:

approximately:

`2m40.846s`

## Direct-edge replication

The independent runtime reproduced the selected direct causal intervention:

`43417 → 656`

including the preregistered attenuation series and numerical outcome
comparisons within the predefined tolerance.

Result:

**REPLICATED**

## Pathway replication

The independent runtime reproduced the selected frozen two-hop pathway:

`56393 → 68045 → 1273`

including:

- upstream attenuation
- intermediate attenuation
- frame-specific intermediate state
- downstream state
- integrated response metrics

Result:

**REPLICATED**

## Convergence replication

The independent runtime reproduced the frozen convergence system:

`44274 + 55925 → 55`

For all tested attenuation levels:

- A-only effects reproduced
- B-only effects reproduced
- combined effects reproduced
- combined effect exceeded either single input
- combined dose series remained monotonic

Result:

**REPLICATED**

## Interpretation

MQ-5.6 provides evidence that the selected MQ-5 causal findings do not
depend solely on the original production neural-runtime implementation.

The findings survived execution through an independently implemented
full-network reference runtime while preserving the frozen scientific
configuration.

This strengthens confidence in the simulated causal results and reduces
concern about implementation-specific behavior.

## Limits

This result does not establish:

- biological causality in living Drosophila
- population-wide generalization to all descending neurons
- robustness to all sensory encodings
- topology specificity against all null-model families
- financial usefulness
- predictive trading value

Independent implementation replication is stronger than deterministic
rerunning of identical code, but it remains replication within the same
frozen mathematical model and data.

## Classification

Selected MQ-5 causal findings:

**REPLICATED UNDER INDEPENDENT FULL-NETWORK IMPLEMENTATION**

Runtime implementation dependence:

**SUBSTANTIALLY MITIGATED FOR THE SELECTED REPLICATION SET**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**
