# MQ-7.18 Pairwise Route Interaction / Compensation Protocol

## Research question

Do pairs of first-wave branches identified in MQ-7.15 and causally validated in MQ-7.16 exhibit interaction effects that are not explained by the two single-branch lesions acting independently on the residual DN-C1 effect?

## Motivation

MQ-7.17 established distributed, non-additive mediation across ten first-wave branches.

External technical feedback raised a specific follow-up question: can two routes partially compensate for, overlap with, or amplify one another such that single-route ablations understate or mischaracterize their joint role?

That external feedback is a research prompt only. It is not scientific evidence.

## Frozen parent experiment

MQ-7.18 directly reuses MQ-7.17 replay helpers so the following remain frozen:

- market condition B
- SHOCK target 56393
- intervention generation 32
- plasticized edge 56393 -> 68045
- plasticity multiplier 0.95
- SHOCK construction and seed semantics
- functional edge-ablation method
- DN-C1 measurement
- intact-effect attenuation calculation

Structural connectome modification remains prohibited.

## First-wave branches

The frozen ten-branch set is:

- 68045 -> 62598
- 68045 -> 69484
- 68045 -> 63192
- 68045 -> 79672
- 68045 -> 77298
- 68045 -> 66309
- 68045 -> 65046
- 68045 -> 73483
- 68045 -> 62142
- 68045 -> 61694

## Pairwise screen

All 45 unique unordered pairs are tested.

For each pair, both direct 68045 -> target contributions are functionally removed and the DN-C1 plasticity-expression effect is measured under the same frozen replay.

## Interaction null model

Simple addition of attenuation percentages is not permitted.

The preregistered null treats residual fractions as independent:

expected_pair_attenuation = 1 - (1 - A) * (1 - B)

where A and B are the measured single-lesion attenuations from the same MQ-7.18 run.

## Interaction excess

interaction_excess = observed_pair_attenuation - expected_pair_attenuation

Positive excess means the double lesion removes more effect than predicted by the independent-residual null.

Negative excess means it removes less.

A positive value alone must not be called biological compensation, synergy, or redundancy.

## Null-pair controls

The validated null edge 68045 -> 82348 is measured alone and paired separately with each of the ten first-wave branches.

The resulting interaction-excess values provide an empirical null reference.

No arbitrary significance threshold is preregistered.

## Higher-order combinations

Triples and larger combinations are out of scope until the complete 45-pair matrix and null controls are reviewed.

## Claims excluded

This experiment does not establish biological compensation in a living organism, biological learning, subjective experience, consciousness, generalization beyond the frozen replay, financial utility, or improved trading performance.

## Provenance note

The pairwise-compensation question was prompted by external community feedback on the public Neuroscope example.

Separately, professional-community moderation feedback emphasized rigorous analysis and theoretical grounding for quantitative-finance discussion. That feedback is treated as a standards/presentation prompt, not scientific evidence.

## Status

PROTOCOL FROZEN — AWAITING EXECUTION
