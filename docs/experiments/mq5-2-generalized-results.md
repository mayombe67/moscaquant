# MQ-5.2 — Generalized Intervention Results

Status:

**SUPPORTED INTERVENTION EFFECT**

Scope:

**Frozen MoscaQuant model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Experiment

MQ-5.2 generalized the frozen MQ-3 causal set across all 13 causal edges.

The experimental design, matched-control assignments, timing-control
assignments, dose levels, and intervention mechanics were frozen before
generalized intervention outcomes were inspected.

Interventions modified presynaptic effective activity at runtime.

Structural connectome weights were not modified.

## Validation

All generalized harness validation gates passed.

- 13 / 13 causal edges completed
- 13 / 13 zero-effect shams exactly matched baseline
- 13 / 13 dose-series intervention telemetry verified
- 13 / 13 deterministic full-silencing replicates reproduced exactly
- frozen artifacts remained unchanged
- timing controls were available for 13 / 13 edges
- matched non-causal controls were available for 12 / 13 edges

The sole matched-control infeasibility was:

`43417 -> 656 @ frame 145`

That infeasibility was identified and documented prospectively before
generalized intervention outcomes were generated.

## Dose-response result

All 13 causal edges exhibited a monotonic decrease in integrated positive
target response as source attenuation increased through:

- 25%
- 50%
- 75%
- 100%

Result:

**13 / 13 monotonic dose responses**

This supports the preregistered directional intervention hypothesis
within the frozen MoscaQuant model.

## Matched non-causal controls

For all 12 causal edges where a scientifically valid matched non-causal
control existed, full causal-source silencing produced a larger
integrated target-response reduction than matched-control silencing.

Result:

**12 / 12 causal interventions exceeded their matched non-causal controls**

The thirteenth edge had no valid matched control and is not counted as a
matched-control success or failure.

This result supports source specificity within the tested frozen model.

## Timing controls

Timing-shift controls were available for all 13 edges.

Comparison of full causal-frame silencing with the prospectively selected
nearby timing control showed:

- causal-frame effect larger: 3 / 13
- timing-shift effect equal or larger: 10 / 13

Therefore MQ-5.2 does not support a general claim of single-frame temporal
exclusivity.

The frozen MQ-3 causal frames remain valid evidence/onset frames, but the
MQ-5.2 interventions show that causal influence often persists into
subsequent active frames.

Interpretation:

**causal influence is frequently temporally extended rather than confined
to one discrete frame**

Timing controls were not activity matched and must not be interpreted as
equal-activity comparisons.

## Response onset

Under complete causal-source silencing:

**7 / 13**

targets showed a delayed first positive response.

The remaining targets retained their original first-positive frame despite
showing dose-dependent reductions in downstream response.

## Generalized interpretation

MQ-5.2 supports a generalized model-level causal effect across the frozen
13-edge set.

The strongest findings are:

1. consistent dose dependence across all 13 causal edges
2. causal-source effects exceeding matched non-causal controls in all 12
   cases where a valid match existed
3. measurable onset delays in 7 of 13 complete-silencing experiments
4. deterministic reproducibility and frozen-artifact invariance

The timing-control result modifies the temporal interpretation.

The evidence does not support describing the frozen causal frame as the
unique effective instant for most edges.

Instead, the causal frame should be understood as an evidence-defined
point within a frequently broader active causal window.

## Result classification

General intervention result:

**SUPPORTED INTERVENTION EFFECT**

Node/source specificity:

**SUPPORTED WHERE MATCHED CONTROL AVAILABLE — 12 / 12**

Monotonic dose dependence:

**SUPPORTED — 13 / 13**

Single-frame temporal exclusivity:

**NOT SUPPORTED AS A GENERAL PROPERTY — 3 / 13**

Full-silencing onset delay:

**OBSERVED — 7 / 13**

## Artifacts

Generated experimental artifacts:

- `mq5-generalized-intervention-matrix-v1.json`
- `mq5-generalized-intervention-matrix-v1.npz`

Frozen control definitions:

- `mq5-2-generalized-control-map-v1.json`
- `mq5-2-generalized-timing-map-v1.json`

Generated experimental artifacts remain immutable.

Interpretation is maintained separately in version-controlled
documentation.

## Scientific limitation

These findings establish causal behavior within the frozen MoscaQuant
simulation.

They do not establish equivalent biological causality in living
Drosophila.

They do not establish market prediction or financial utility.

Financial semantics remain:

**NOT ASSIGNED**
