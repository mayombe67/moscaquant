# CONF-004A — Robust Normalization Results

Status:

**ROBUST TO TESTED NORMALIZATION ALTERNATIVE**

Scope:

**Frozen MoscaQuant model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Purpose

CONF-004A tested whether the principal MQ-5 causal findings depended on the
original causal rolling mean / standard-deviation normalization rule.

Encoder B replaced only that normalization stage with:

- rolling median
- rolling median absolute deviation
- MAD consistency factor 1.4826
- bounded `tanh` transform

The following remained fixed:

- market observations
- market features
- retinal territories
- temporal encoder
- sensory gain
- connectome
- physiology
- causal nodes
- causal frames
- matched-control identities
- intervention mechanics
- outcome metrics

## Encoder difference audit

Encoder B materially changed the sensory representation.

Observed differences included:

- 4 / 12 normalized observations changed
- 165 normalized feature values changed
- 64 / 192 retinal stimulus frames changed
- 207,424 retinal stimulus values changed
- total retinal L1 difference approximately 286.09
- neural effective activity changed on 60 frames
- maximum neural effective-activity difference reached 1.0

Therefore Encoder B was not equivalent to Encoder A.

## Frozen causal engagement

All 13 frozen causal sources remained engaged at their original frozen
causal frames.

Result:

**13 / 13 ENGAGED**

No causal frame or causal node was reselected.

## Frozen matched-control engagement

All 12 previously frozen matched non-causal controls remained engaged at
their original comparison frames.

Result:

**12 / 12 ENGAGED**

No matched-control identity was replaced.

## Generalized single-node robustness

Under Encoder B:

- 13 / 13 causal edges retained monotonic dose response
- 12 / 12 causal-source interventions exceeded their frozen matched
  non-causal controls
- 3 / 13 causal-frame interventions exceeded the nearby timing-control
  effect
- 10 / 13 timing-control interventions were equal or larger in magnitude
- 7 / 13 full causal-source silencing interventions delayed first response

These categorical results exactly matched Encoder A.

## Effect-magnitude comparison

For most causal edges, full-silencing intervention magnitude under Encoder B
was extremely close to Encoder A.

Median Encoder-B / Encoder-A absolute 100% effect ratio:

approximately:

`1.00007`

Most measurable edges were close to unity.

The apparent largest ratio occurred for `55548 -> 51`, whose absolute effect
lies near `10^-15`.

That ratio is therefore dominated by the previously documented tiny-response
numerical-scale limitation and must not be interpreted as a large practical
effect change.

Several responders showed substantial changes in baseline integrated
activity while retaining nearly unchanged causal intervention magnitude.

Examples included:

- `64717 -> 92`
- `128590 -> 317`

This indicates that the tested causal intervention effects were more stable
than the surrounding baseline trajectory under the normalization change.

## Pathway robustness

Frozen pathway:

`56393 → 68045 → 1273`

The complete pathway retained dose-dependent propagation under Encoder B.

Upstream attenuation continued to produce:

1. reduced 68045 state at F146
2. reduced 68045 effective activity at F147
3. reduced 1273 response at F147
4. monotonic reduction in downstream integrated response

Complete upstream silencing produced downstream integrated change of
approximately:

`-1.593874503e-07`

Complete intermediate silencing produced approximately:

`-2.282887457e-08`

These values were very close to Encoder-A pathway effects.

Result:

**PATHWAY PROPAGATION ROBUST TO CONF-004A**

## Convergence robustness

All three frozen convergence systems retained their qualitative structure:

`44274 + 55925 → 55`

`55548 + 87441 → 51`

`92657 + 93484 → 129`

For all three systems:

- combined perturbation exceeded either individual perturbation at every
  tested attenuation level
- combined dose response remained monotonic

Result:

**12 / 12 combined-versus-single comparisons retained**

and:

**3 / 3 combined dose series retained monotonicity**

No statistical synergy, antagonism, subadditivity, or superadditivity
classification is assigned.

Responder 51 remains subject to the previously documented extremely-small
absolute response limitation.

## Overall interpretation

CONF-004A supports robustness of the principal MQ-5 causal findings to the
specific tested normalization alternative.

The findings survived replacement of the original rolling mean / standard
deviation normalizer with a causal median / MAD normalizer despite material
changes to the sensory stream and neural baseline state.

Supported robustness includes:

- generalized single-node causal intervention
- matched-control specificity
- timing-pattern replication
- onset-delay pattern
- complete two-hop pathway propagation
- convergent-input contribution

This result reduces concern that the MQ-5 findings are solely artifacts of
the original normalization rule.

## Limitation

CONF-004A does not establish invariance to all possible sensory encodings.

The following remain unchanged and therefore untested by this experiment:

- retinal territory assignment
- temporal motion encoding
- volatility-dependent cadence
- entropy-dependent temporal jitter
- sensory gain

A more structurally distinct encoding may be tested separately as
CONF-004B.

## Result classification

Normalization dependence:

**NOT SUPPORTED FOR THE PRINCIPAL MQ-5 FINDINGS UNDER THE TESTED ALTERNATIVE**

Robustness to causal median/MAD normalization:

**SUPPORTED**

General encoding independence:

**NOT ESTABLISHED**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**
