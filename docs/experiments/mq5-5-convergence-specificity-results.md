# MQ-5.5 — Convergence and Specificity Results

Status:

**SUPPORTED CONVERGENT-INPUT EFFECT**

Scope:

**Frozen MoscaQuant model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Frozen convergence systems

MQ-5.5 tested the three convergent responder systems predefined in MQ-5.1:

### Responder 55

`44274 → 55`

`55925 → 55`

at frame 146.

### Responder 51

`55548 → 51`

`87441 → 51`

at frame 149.

### Responder 129

`92657 → 129`

`93484 → 129`

at frame 148.

No convergence system was selected after intervention outcomes were observed.

## Validation

All MQ-5.5 validation gates passed.

- 3 / 3 convergence systems completed
- all combined zero-effect shams exactly matched baseline
- all intervention telemetry verified
- all deterministic full combined-silencing replicates reproduced exactly
- frozen artifacts remained unchanged

## Combined-input result

For every system and every attenuation level, combined perturbation produced
a larger integrated target-response reduction than either single-input
perturbation alone.

Result:

**12 / 12 dose-level comparisons**

satisfied:

`E_AB > max(E_A, E_B)`

where:

- `E_A` is the integrated-response reduction after perturbing input A
- `E_B` is the integrated-response reduction after perturbing input B
- `E_AB` is the integrated-response reduction after perturbing both

This supports the predefined combined-input hypothesis within the frozen
MoscaQuant model.

## Combined dose response

All three responder systems exhibited monotonic combined-input dose response
across:

- 25%
- 50%
- 75%
- 100%

Result:

**3 / 3 monotonic combined dose series**

Increasing attenuation of both preserved inputs produced increasing
downstream reduction.

## Responder 55

Inputs:

`44274 + 55925 → 55`

At complete silencing:

- `E_A = 3.480854e-07`
- `E_B = 5.419379e-07`
- `E_AB = 8.898869e-07`
- descriptive additive reference:
  `E_A + E_B = 8.900233e-07`
- combined minus additive reference:
  approximately `-1.36e-10`

Combined intervention exceeded either single intervention at all four dose
levels.

The combined effect was also numerically close to the descriptive additive
reference.

No statistical additivity, synergy, antagonism, subadditivity, or
superadditivity claim is assigned.

## Responder 51

Inputs:

`55548 + 87441 → 51`

Combined intervention exceeded either single intervention at all four dose
levels.

At complete silencing:

- `E_A = 1.308002e-15`
- `E_B = 5.378601e-16`
- `E_AB = 2.009875e-15`
- descriptive additive reference:
  `1.845862e-15`

The absolute response magnitude is extremely small.

Therefore this result is retained as a deterministic model-level effect but
must not be described as having the same practical magnitude or numerical
robustness as the larger responder effects without additional precision or
stability analysis.

The direction and ordering are retained exactly as observed.

## Responder 129

Inputs:

`92657 + 93484 → 129`

Combined intervention exceeded either single intervention at all four dose
levels.

At complete silencing:

- `E_A = 6.680546e-12`
- `E_B = 1.041600e-12`
- `E_AB = 7.698888e-12`
- descriptive additive reference:
  `7.722146e-12`
- combined minus additive reference:
  approximately `-2.33e-14`

The combined response was close to the descriptive additive reference.

No statistical interaction classification is assigned.

## Interpretation

MQ-5.5 supports convergent causal influence within the frozen MoscaQuant
model.

For all three predefined responder systems:

1. perturbing input A changed the responder
2. perturbing input B changed the responder
3. perturbing both inputs produced a larger effect than either input alone
4. the combined effect increased monotonically with attenuation

The observed combined effects were generally close to the descriptive sum
of the individual effects.

Because no statistical interaction null model or equivalence tolerance was
pre-registered, these comparisons remain descriptive.

The experiment therefore does not assign labels such as:

- synergistic
- antagonistic
- subadditive
- superadditive

## Result classification

Combined perturbation exceeds either single input:

**SUPPORTED — 12 / 12 DOSE-LEVEL COMPARISONS**

Combined dose dependence:

**SUPPORTED — 3 / 3 SYSTEMS**

Convergent-input contribution:

**SUPPORTED WITHIN THE FROZEN MODEL**

Statistical interaction class:

**NOT ASSIGNED**

Single-frame temporal exclusivity:

**NOT TESTED**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Numerical-scale limitation

The three systems span very different response magnitudes.

In particular, responder 51 produced effects on the order of `10^-15`.

Such effects are retained because they arise deterministically under the
frozen runtime and preserve the preregistered directional ordering.

However, extremely small absolute effects must be distinguished from larger
effects when assessing practical magnitude and numerical stability.

MQ-5.6 replication and stability work should preserve this distinction.

## Artifacts

Generated immutable experimental artifacts:

- `mq5-5-convergence-specificity-v1.json`
- `mq5-5-convergence-specificity-v1.npz`

Protocol:

- `docs/experiments/mq5-5-convergence-specificity-protocol.md`

Configuration:

- `config/controls/mq5-5-convergence-specificity-v1.toml`

## Next methodological checkpoint

Before treating the intervention findings as broadly stable, the project
should address the already-registered encoding-dependence confound.

A prospective encoding-robustness experiment should test whether the major
MQ-5 findings survive an independently justified alternative
market-to-sensory encoding.

This must be treated as a new experiment rather than as reinterpretation of
the current results.

Financial semantics remain:

**NOT ASSIGNED**
