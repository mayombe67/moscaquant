# MQ-7.19 Conditional Pairwise Contribution Results

## Status

CONDITIONAL COMPENSATION-LIKE DEPENDENCE: SUPPORTED

## Research question

For the three strongest supra-independent pairs identified in MQ-7.18, does
either route account for a larger fraction of the remaining DN-C1 effect when
its partner route is already absent?

## Frozen parent

MQ-7.19 reused the frozen MQ-7.18 / MQ-7.17 replay machinery:

- market condition B
- SHOCK target 56393
- SHOCK seed 5
- intervention generation 32
- plasticized edge 56393 -> 68045
- plasticity multiplier 0.95
- functional edge-ablation method
- DN-C1 effect metric

Structural connectome modification:

None

## Intact reference

Absolute DN-C1 effect:

1.1174368270910759e-08

## Frozen pair set

The three strongest positive-interaction pairs from MQ-7.18 were frozen before
execution:

1. 68045 -> 62598 + 68045 -> 77298
2. 68045 -> 62598 + 68045 -> 79672
3. 68045 -> 79672 + 68045 -> 77298

No pair substitution occurred.

## Conditional metric

For pair A/B:

B_given_A =
    (attenuation_AB - attenuation_A)
    /
    (1 - attenuation_A)

A_given_B =
    (attenuation_AB - attenuation_B)
    /
    (1 - attenuation_B)

Conditional gain is the conditional fraction minus the corresponding standalone
attenuation.

A positive conditional gain means the route accounts for a larger fraction of
the remaining effect when its partner route is absent.

## Pair 1: 62598 + 77298

62598 standalone attenuation:

33.63841423709857%

77298 standalone attenuation:

17.25879292644743%

Pair attenuation:

47.05361328003301%

77298 given 62598 absent:

20.21530813152153%

Conditional gain:

+2.956515205074095 percentage points

62598 given 77298 absent:

36.00965154774641%

Conditional gain:

+2.371237310647839 percentage points

## Pair 2: 62598 + 79672

62598 standalone attenuation:

33.63841423709857%

79672 standalone attenuation:

17.63615287879791%

Pair attenuation:

47.13626147635609%

79672 given 62598 absent:

20.33985035783053%

Conditional gain:

+2.703697479032624 percentage points

62598 given 79672 absent:

35.81681724282190%

Conditional gain:

+2.178403005723334 percentage points

## Pair 3: 79672 + 77298

79672 standalone attenuation:

17.63615287879791%

77298 standalone attenuation:

17.25879292644743%

Pair attenuation:

33.63076955557142%

77298 given 79672 absent:

19.41946282965233%

Conditional gain:

+2.160669903204898 percentage points

79672 given 77298 absent:

19.78696855917289%

Conditional gain:

+2.150815680374987 percentage points

## Null controls

The validated null edge:

68045 -> 82348

was paired with every unique branch in the frozen MQ-7.19 pair set.

Maximum absolute conditional gain among null controls:

0.0

This confirms that the conditional-gain calculation does not produce a
non-zero effect merely because a second lesion is present under the frozen
replay.

## Interpretation

All three preregistered pairs showed positive conditional gain in both
directions.

Within the frozen model, each tested branch therefore accounted for a larger
fraction of the remaining DN-C1 effect when its paired branch was absent than
it did in the intact context.

This strengthens the MQ-7.18 result from generic supra-independent pairwise
interaction to bidirectional conditional dependence among the strongest tested
pairs.

The result is compatible with compensation-like behavior within the model.

## Claim boundary

The result must not be described as biological compensation in a living fly.

The experiment did not demonstrate:

- adaptive rerouting after injury
- dynamic rewiring
- biological homeostasis
- biological learning
- subjective state
- generalization beyond the frozen replay

The supported claim is limited to conditional dependence in the modeled
network under the frozen MQ-7 replay.

## Scientific sequence

The causal-pathway sequence now ends with:

1. MQ-7.17: distributed causal mediation supported
2. MQ-7.18: pairwise supra-independent interaction supported
3. MQ-7.19: bidirectional conditional compensation-like dependence supported

Together these results show that the measured replay-level effect is distributed
and contains structured nonlinear dependence among selected downstream
branches.

## Why the rabbit hole stops here

MQ-7.19 answers the specific external technical question that reopened the
causal-pathway subphase.

A blind triple/higher-order combinatorial search is not justified by the
current question and would substantially expand the search space without a
new preregistered hypothesis.

Higher-order combinations remain permissible only if a future independently
motivated question requires them.

## Provenance

MQ-7.18 and MQ-7.19 were prompted by external technical feedback asking whether
partially redundant routes could make single-edge ablations misleading.

The external comment supplied the question, not the result.

A separate quantitative-finance moderation event is retained only as a
standards/presentation prompt.

Internal nickname:

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

MQ-7.19 CONDITIONAL COMPENSATION-LIKE DEPENDENCE: SUPPORTED
