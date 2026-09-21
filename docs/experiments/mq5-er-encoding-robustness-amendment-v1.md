# MQ-5.ER Protocol Amendment v1

**Status:** PRE-RESULT CORRECTION / NO MQ-5.ER OUTCOMES GENERATED

## Why this amendment exists

Implementation-level review of the frozen encoder exposed one terminology error
and clarified the separability of the proposed encoding manipulations.

No MQ-5.ER result-bearing execution occurred before this amendment.

## Correction to Arm D

The preregistered scaffold described Arm D as a feature-to-retinal-territory
remap.

That description was incorrect.

The frozen spatial encoder accepts a `(6, 7)` matrix in which each row is one
asset/ticker and each column is one feature. Row 0 maps to retinal territory T1,
row 1 to T2, through row 5 to T6.

Therefore Arm D is corrected to:

**asset/ticker-to-retinal-territory remapping**

The seven within-row feature semantics remain unchanged.

## Arm D mapping family

Rather than selecting one arbitrary remap, MQ-5.ER reuses the already existing
balanced deterministic ticker/territory design:

- six cyclic rotations of the identity order;
- six cyclic rotations of the reversed order;
- twelve mappings total;
- identity is the reference member;
- eleven non-identity remaps are confirmatory alternatives;
- across the complete twelve-mapping design, every asset appears in every
  territory exactly twice.

No mapping is selected or removed based on MQ-5.ER neural outcomes.

Arm D is reported as a mapping-family robustness test.

`ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS` requires all eleven
non-identity mappings to satisfy the frozen preservation criteria.

Any mixture of preserved and non-preserved remaps is reported as:

`MIXED ASSET-TERRITORY DEPENDENCE`

If none of the eleven non-identity mappings preserve the accepted response,
report:

`ASSET-TERRITORY ASSIGNMENT DEPENDENCE SUPPORTED`

These labels apply only to the frozen tested mapping family.

## Arm B feasibility and freeze

The code-level audit confirms that volatility controls temporal cadence through:

`cycles = 1.0 + 3.0 * volatility_mag`

where normalized volatility is mapped from `[-1, 1]` into `[0, 1]`.

Arm B is therefore separable from entropy jitter.

The fixed Arm B cadence is frozen prospectively at the midpoint of the existing
cadence domain:

`cycles = 2.5`

This corresponds to the frozen encoder's neutral normalized volatility value
of `0.0`.

Arm B changes cadence selection only. It does not alter:

- the normalized volatility feature stored in the feature matrix;
- entropy;
- momentum;
- retinal territory assignment;
- spatial feature geometry;
- sensory gain;
- neural dynamics.

## Arm C feasibility and freeze

The code-level audit confirms that entropy contributes only the phase
irregularity term:

`entropy_mag * pi * jitter`

after the regular cadence phase is constructed.

Arm C is therefore separable from volatility cadence.

Arm C freezes the jitter contribution multiplier to exactly:

`0.0`

The normalized entropy feature itself remains present and unchanged in the
input matrix; only its temporal-irregularity encoding effect is disabled.

This distinction avoids replacing the normalized entropy value with `-1`,
which would change the input data rather than isolate the encoding rule.

## Arm E correction and freeze

The original scaffold proposed an unspecified alternative motion rule.

The code-level audit shows that momentum-dependent motion is implemented as a
multiplicative horizontal reweighting:

`1 + 0.25 * momentum * motion_phase * geometry.x`

followed by per-frame energy renormalization.

To avoid inventing an arbitrary new motion algorithm, Arm E is now defined as:

**NO MOMENTUM-DEPENDENT TEMPORAL MOTION**

Arm E sets the motion-weight multiplier to unity for every neuron and frame:

`motion_weight = 1.0`

while preserving:

- the original base spatial pattern;
- normalized momentum values in the feature matrix;
- volatility-dependent cadence;
- entropy-dependent jitter;
- retinal territories;
- all other spatial feature effects;
- per-frame spatial energy normalization;
- mean territory energy;
- sensory gain;
- neural substrate.

This tests whether the accepted response requires the hand-designed temporal
translation of momentum into coherent horizontal motion.

It does not test every possible alternative motion encoding.

## Energy-conservation requirement

The frozen encoder normalizes:

1. each motion-modified frame to `base_energy` before pulse modulation; and
2. the complete territory sequence so mean territory energy equals
   `base_energy`.

MQ-5.ER implementations must preserve those fairness rules for Arms B, C, D,
and E.

## Result authorization

Result execution remains disabled.

Before any result-bearing execution, the implementation must:

- prove Arm A duplicate replay;
- prove B changes only cadence selection;
- prove C changes only entropy-jitter contribution;
- prove each D mapping is a valid asset-row permutation and preserves the
  twelve-mapping balance design;
- prove E changes only momentum-dependent temporal motion;
- verify energy-conservation invariants;
- freeze numeric preservation tolerances;
- commit code and configuration.

This amendment corrects protocol semantics before outcome inspection.

Financial semantics remain:

**NOT ASSIGNED**
