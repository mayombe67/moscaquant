# MQ-7.18 Pairwise Route Interaction / Compensation Results

## Status

PAIRWISE SUPRA-INDEPENDENT INTERACTION: SUPPORTED

## Research question

Do pairs of first-wave branches exhibit joint effects that depart from the
preregistered independent-residual null?

## Frozen parent

MQ-7.18 directly reused the frozen MQ-7.17 replay mechanics:

- market condition B
- SHOCK target 56393
- SHOCK seed 5
- intervention generation 32
- plasticized edge 56393 -> 68045
- plasticity multiplier 0.95
- functional edge-ablation method
- DN-C1 effect measurement
- attenuation relative to the intact replay

Structural connectome modification:

None

## Intact reference

Absolute DN-C1 effect:

1.1174368270910759e-08

## Single-branch attenuation

- 68045 -> 62598: 33.63841423709857%
- 68045 -> 69484: 26.47211095789420%
- 68045 -> 63192: 21.23091068478895%
- 68045 -> 79672: 17.63615287879791%
- 68045 -> 77298: 17.25879292644743%
- 68045 -> 66309: 13.49910387950026%
- 68045 -> 65046: 10.13471441760241%
- 68045 -> 73483: 9.83937480671824%
- 68045 -> 62142: 4.32011277664687%
- 68045 -> 61694: 3.69977660274357%

Validated null edge:

68045 -> 82348

Observed attenuation:

0.0%

## Interaction null model

The preregistered null treated residual fractions as independent:

expected_pair_attenuation =
    1 - (1 - A) * (1 - B)

where A and B are the single-lesion attenuations measured in the same run.

Interaction excess:

observed_pair_attenuation
-
expected_pair_attenuation

No simple addition of attenuation percentages was permitted.

## Strongest positive interactions

### 1. 62598 + 77298

Observed pair attenuation:

47.05361328003301%

Independent-residual expectation:

45.09162290662455%

Interaction excess:

+1.961990373408462 percentage points

### 2. 62598 + 79672

Observed pair attenuation:

47.13626147635609%

Independent-residual expectation:

45.34204495503845%

Interaction excess:

+1.794216521317638 percentage points

### 3. 79672 + 77298

Observed pair attenuation:

33.63076955557142%

Independent-residual expectation:

31.85115869970191%

Interaction excess:

+1.779610855869507 percentage points

### 4. 69484 + 77298

Observed pair attenuation:

40.86261586455237%

Independent-residual expectation:

39.16213707085927%

Interaction excess:

+1.700478793693094 percentage points

### 5. 63192 + 77298

Observed pair attenuation:

36.37592416342670%

Independent-residual expectation:

34.82550469974965%

Interaction excess:

+1.550419463677044 percentage points

## Most negative interaction

Pair:

66309 + 61694

Observed pair attenuation:

16.62416635853200%

Independent-residual expectation:

16.69944379533003%

Interaction excess:

-0.075277436798027 percentage points

The strongest departures from the null were therefore predominantly positive.

## Null-pair controls

The validated zero-attenuation edge:

68045 -> 82348

was paired separately with each of the ten first-wave branches.

Maximum absolute interaction excess across all ten null-pair controls:

0.0

This provides an empirical control showing that merely adding a second lesion
did not itself produce interaction excess under the frozen replay.

## Interpretation

The first-wave subnetwork contains structured pairwise interactions.

Several branch pairs removed more of the DN-C1 effect than predicted by the
independent-residual null.

The strongest pair:

68045 -> 62598
+
68045 -> 77298

exceeded its expected attenuation by approximately 1.96 percentage points.

The null-edge pair controls produced no interaction excess.

These results support supra-independent pairwise interaction under the frozen
replay.

## What this does not establish

Positive interaction excess is not by itself evidence of biological
compensation, redundancy, synergy, learning, or adaptation in a living fly.

Possible explanations within the model include:

- conditional route dependence
- recurrent network effects
- threshold effects
- nonlinear propagation
- overlap not captured by the independent-residual null

MQ-7.19 is therefore limited to testing conditional contribution among the
strongest preregistered pairs.

## Frozen MQ-7.19 candidates

The three strongest positive-interaction pairs are frozen as:

1. 68045 -> 62598 + 68045 -> 77298
2. 68045 -> 62598 + 68045 -> 79672
3. 68045 -> 79672 + 68045 -> 77298

No other pair may be substituted into the initial MQ-7.19 test based on later
inspection.

## Provenance

The pairwise-compensation question was prompted by external technical feedback
on the public Neuroscope example asking whether partially redundant downstream
routes could make single-route ablations misleading.

That feedback motivated the question only. It did not determine the pair set,
null model, controls, or result.

Separately, moderation feedback from a professional quantitative-finance
community emphasized rigorous analysis and theoretical grounding. That feedback
is retained as a standards/presentation prompt only and is not scientific
evidence.

Internal nickname for the latter:

the r/quant neckbeards problem

## Claims excluded

These results do not establish:

- biological compensation in a living organism
- biological learning
- subjective memory, pain, fear, trauma, or reward
- consciousness
- exclusive biological pathway usage
- generalization beyond the frozen replay
- financial utility
- improved trading performance
- institutional quantitative-finance relevance

## Final classification

MQ-7.18 PAIRWISE SUPRA-INDEPENDENT INTERACTION: SUPPORTED
