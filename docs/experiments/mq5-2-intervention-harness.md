# MQ-5.2 — Intervention Harness Validation

Status: SUPPORTED INTERVENTION EFFECT

## Experiment

Pre-registered showcase:

`43417 → 656`

Frozen causal frame:

`145`

Intervention mechanism:

runtime attenuation of presynaptic effective activity at frame 145.

The structural connectome was not modified.

## Validation

All MQ-5.2 harness validation gates passed.

- baseline and zero-effect sham target-voltage traces were exactly equal
- baseline and zero-effect sham source-activity traces were exactly equal
- source neuron 43417 was active at frame 145
- requested dose application was verified from intervention telemetry
- deterministic 100% attenuation replication was exactly reproducible
- frozen source artifacts were unchanged by hash comparison

Baseline source effective activity at frame 145:

`0.37755101919174194`

Frozen edge weight:

`0.0006644517998211086`

Predicted direct contribution:

`0.00025086445422624684`

Observed neuron-656 voltage at frame 145:

`0.00025086445384658873`

Residual:

`-3.7965811050533205e-13`

Within numerical precision, the positive voltage recorded for neuron 656
at frame 145 is accounted for by the frozen `43417 → 656` contribution
under this experimental condition.

## Dose response

| Attenuation | Source activity F145 | Target V F145 | Integrated positive V | Peak V | First positive | Peak frame |
|---:|---:|---:|---:|---:|---:|---:|
| 0% baseline | 0.3775510192 | 0.000250864454 | 0.07467284449 | 0.001978947548 | 145 | 165 |
| 0% sham | 0.3775510192 | 0.000250864454 | 0.07467284449 | 0.001978947548 | 145 | 165 |
| 25% | 0.2831632495 | 0.000188148333 | 0.07350943417 | 0.001955874730 | 145 | 165 |
| 50% | 0.1887755096 | 0.000125432227 | 0.07234602432 | 0.001932802028 | 145 | 165 |
| 75% | 0.0943877548 | 0.000062716113 | 0.07118262081 | 0.001909729559 | 145 | 165 |
| 100% | 0.0000000000 | 0.000000000000 | 0.07001921117 | 0.001887654071 | 146 | 166 |

Relative to baseline, integrated positive voltage decreased by
approximately:

- 1.56% at 25% attenuation
- 3.12% at 50% attenuation
- 4.67% at 75% attenuation
- 6.23% at 100% attenuation

Peak voltage decreased by approximately:

- 1.17% at 25% attenuation
- 2.33% at 50% attenuation
- 3.50% at 75% attenuation
- 4.61% at 100% attenuation

The downstream response therefore changed monotonically with increasing
attenuation.

At complete silencing:

- frame-145 target voltage fell to zero
- first positive response shifted from frame 145 to frame 146
- peak response shifted from frame 165 to frame 166
- positive-frame count decreased from 47 to 46

## Interpretation

This experiment supports the pre-registered directional hypothesis for
the `43417 → 656` intervention within the frozen MoscaQuant model.

Reducing effective activity of neuron 43417 during the causal frame
produced progressively reduced downstream activity in neuron 656.

The result demonstrates simulated dynamical causality within the frozen
MoscaQuant model.

It does not establish biological causality in living Drosophila.

The nearly exact frame-145 proportionality is expected from the direct
weighted contribution and is therefore not, by itself, sufficient
evidence of broader network causality.

The persistence of dose-dependent changes in integrated response and peak
response, together with the latency and peak-frame shift under complete
silencing, demonstrates a downstream dynamical consequence beyond the
instantaneous multiplication at frame 145.

## Result classification

**Supported intervention effect**

Scope:

**causal perturbation within the frozen MoscaQuant model**

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**

## Artifacts

- `mq5-intervention-43417-to-656-v1.json`
- `mq5-intervention-43417-to-656-v1.npz`

Generated experiment artifacts remain immutable.

Interpretation is recorded separately in this document.

## Next

Proceed to the remaining MQ-5.2 validation requirements:

1. timing-shift control
2. matched non-causal control
3. generalized intervention harness across the frozen causal set

No MQ-5.1 hypothesis or threshold was changed after observing this result.
