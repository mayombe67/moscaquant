# SQ-13 — SURFACE TENSION — Result

## Status

**SEALED / COMPLETED**

SQ-13 measured the decision-boundary margin surrounding the already-sealed
SQ-12 transmission-gate null.

No new neural execution was performed.

## Scientific question

SQ-12 RESONANCE CASCADE established that the known local BODY perturbations do
not become transmissible during the frozen 192-frame runtime.

SQ-13 asked:

> How much decision-boundary margin protected that closed gate?

The authoritative classification is:

`GATE_CLOSED_WITH_POSITIVE_DECISION_MARGIN`

## Frozen design

SQ-13 inherited the twelve single-edge matched contrasts from SQ-10 / SQ-11 and
used only already-sealed SQ-11 evidence.

Authoritative fields:

- P5 responder voltage before threshold;
- P6 firing decision;
- P7 committed spike state.

The frozen firing threshold remained:

`1.0`

P5 divergence was defined by exact stored float32 inequality.

No tolerance, fitted threshold, interpolation or post-result numerical floor was
introduced.

## Result

Across the twelve matched contrasts:

- matched contrasts: `12`;
- P5-divergent frame/contrast observations: `800`;
- firing-state contradictions: `0`;
- new neural executions: `0`.

All three BODY perturbations therefore produced measurable P5 differences while
preserving the already-sealed SQ-12 firing-state null.

## BODY summaries

### BODY A

P5-divergent observations:

`268`

Minimum observed decision-boundary distance:

`0.999994164324562`

Maximum absolute P5 difference:

`5.830753194491223e-06`

### BODY B

P5-divergent observations:

`272`

Minimum observed decision-boundary distance:

`0.9995643028523773`

Maximum absolute P5 difference:

`0.00010991192539222538`

### BODY C

P5-divergent observations:

`260`

Minimum observed decision-boundary distance:

`0.9999924379844742`

Maximum absolute P5 difference:

`2.9374905352597125e-07`

## Primary endpoint

The prospectively defined minimum decision-boundary distance occurred for:

- BODY: `B`;
- source: `128590`;
- responder: `317`;
- retained mask: `000`;
- lesioned mask: `010`;
- frame: `191`.

Observed P5 values:

- retained: `0.0004356971476227045`;
- lesioned: `0.0003257852222304791`.

Both states remained below threshold and both firing decisions were:

`0`

Absolute P5 difference:

`0.00010991192539222538`

Distance of the nearer observed state to the frozen threshold:

`0.9995643028523773`

Descriptive scale separation:

`9094.229759740716`

defined as:

`decision margin / observed P5 difference`

## Interpretation

The SQ-12 gate was not a numerically marginal binary null.

The BODY perturbations measurably changed local responder P5 state, but even the
closest observed state remained far below the frozen `1.0` firing threshold.

At the primary endpoint the remaining decision margin was approximately
`9,094.23` times the observed matched P5 difference.

That ratio is descriptive only.

It is not:

- the BODY-weight multiplier required to cause firing;
- a prediction under scaled intervention;
- evidence that the response is linear;
- authorization for a gain or weight sweep.

## Final-frame boundary

The primary endpoint occurs at frame:

`191`

which is the final stored frame of the frozen 192-frame episode.

This fact does not establish a trend toward eventual firing.

SQ-13 does not extrapolate beyond the observed window.

A longer-duration experiment would be a new causal question requiring separate
preregistration.

## Independent verification

A separately frozen verifier independently reconstructed the analysis using a
scalar frame-by-frame implementation and did not import the primary SQ-13
analyzer.

It reproduced:

- classification;
- all `800` P5-divergent observations;
- BODY-specific minimum margins;
- BODY-specific maximum P5 differences;
- the BODY B primary endpoint;
- frame `191`;
- decision-boundary distance;
- absolute P5 difference;
- scale separation.

Independent verification status:

`INDEPENDENT_VERIFICATION_PASS`

No new neural execution was performed.

## APOTHEOSIS #28 — Measure the Margin Before Moving the Goalposts

A nonzero perturbation does not imply a near-threshold system.

Before proposing a counterfactual intended to flip a binary outcome, measure the
observed distance to the decision boundary under the frozen model.

A measurable internal perturbation may coexist with a very large decision
margin.

Parameter escalation designed merely to manufacture a positive binary outcome
must not be substituted for understanding the frozen result.

## Provenance

SQ-13 analysis:

`artifacts/experiments/sq13-surface-tension/sq13-surface-tension-analysis-v1.json`

SHA-256:

`85cf6ec5d47c0571cacc435933e54b8cc6fcdf8bc54f6959731cd3052565b2d0`

Independent verification:

`artifacts/experiments/sq13-surface-tension/sq13-surface-tension-verification-v1.json`

SHA-256:

`67002ac7d88fff46c2e0688b3b684c6ff6f9c6cfc5ed76640d87c17e2bd499e0`

Canonical result seal:

`artifacts/experiments/sq13-surface-tension/sq13-surface-tension-result-seal-v1.json`

## Claim boundary

SQ-13 measures stored computational state in the frozen MoscaQuant model.

It does not establish:

- biological robustness;
- a biological firing margin;
- organism behavior;
- perception;
- cognition;
- consciousness;
- learning;
- market intelligence;
- prediction;
- profitability;
- financial usefulness.

## Canonical summary

Local P5 perturbation: **present**.

Firing-state change: **absent**.

Closest observed threshold margin: **positive and large**.

Primary BODY: **B**.

Primary frame: **191 / 191**.

New neural execution: **none**.

Classification:

`GATE_CLOSED_WITH_POSITIVE_DECISION_MARGIN`

Science first.

Lulz a very close second.
