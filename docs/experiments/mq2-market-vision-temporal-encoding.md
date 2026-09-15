# MQ-2 Market Vision Temporal Encoding

## Purpose

Extend the frozen spatial Market Vision encoder into a deterministic
time-varying retinal stimulus.

This stage adds temporal organization only.

It does not contain trading semantics.

## Inputs

The temporal encoder consumes the same normalized six-asset feature matrix used
by the spatial encoder.

Feature values are in:

`[-1, 1]`

The spatial encoder remains frozen and is treated as the base frame.

## Temporal Features

### Momentum

Property:

`horizontal_motion_persistence`

Signed.

Momentum controls coherent horizontal motion through time.

Positive and negative momentum produce opposite motion directions.

Momentum sign must not alter integrated sensory energy.

### Realized Volatility

Property:

`temporal_pulse_rate`

Raw realized volatility is unsigned, but causal normalization represents
deviation from recent history in `[-1, 1]`.

Therefore:

- `-1` = unusually calm;
- `0` = near recent baseline;
- `+1` = unusually volatile.

The normalized value is mapped monotonically into pulse cadence.

### Return-Sign Entropy

Property:

`temporal_irregularity`

Raw return-sign entropy is unsigned, but causal normalization represents
deviation from recent history in `[-1, 1]`.

Therefore:

- `-1` = unusually orderly;
- `0` = near recent baseline;
- `+1` = unusually irregular.

Entropy changes pulse timing organization rather than average brightness.

## Energy Rule

For each ticker territory, temporal modulation is normalized over the complete
observation window.

Mean integrated territory energy must remain equal to the spatial encoder's
base energy.

Timing may change.

Direction may change.

Integrated energy over the observation window may not change solely because of
momentum sign, volatility level, or entropy level.

## Determinism

No runtime randomness is used.

Temporal irregularity is generated from a fixed deterministic phase sequence.

Identical feature matrices and frame counts must produce identical stimulus
sequences.

## Scientific Boundary

The temporal mapping is artificial and must be frozen before downstream
connectome responses are inspected.


## Validation Results

### Energy Conservation

A 16-frame zero-feature sequence produced mean integrated territory energies
of approximately 1.0 for all six retinal territories.

Result:

`TEMPORAL ENERGY CONSERVATION PASS`

### Momentum

Input:

`+0.9 / -0.9`

Measured T1 horizontal centroid trajectories:

- positive: `-0.0876377076 -> +0.0070314794`
- negative: `+0.0070314812 -> -0.0876377076`

Result:

`PASS`

Opposite momentum signs produced opposite horizontal motion through time.

### Initial Volatility Test Failure

The first volatility cadence test produced:

- calm direction changes: `22`
- volatile direction changes: `16`

This failed the expected ordering.

The encoder was not modified.

Investigation found that the otherwise-zero feature matrix left normalized
return-sign entropy at `0`.

For an unsigned raw feature represented by causal normalization, `0` means
near recent baseline rather than "disabled."

The entropy channel therefore introduced temporal irregularity into the
volatility-isolation experiment.

This was an experimental-control failure, not evidence of incorrect
volatility encoding.

### Isolated Volatility

The volatility experiment was repeated while explicitly fixing entropy to
`-1`, representing minimum temporal irregularity.

Measured direction changes over 64 frames:

- unusually calm: `2`
- unusually volatile: `8`

Mean territory energy:

- calm: `1.0000002384`
- volatile: `1.0`

Result:

`ISOLATED VOLATILITY CADENCE PASS`

### Isolated Return-Sign Entropy

Volatility was held constant at normalized baseline while entropy was varied.

Measured temporal irregularity:

- orderly: `0.0218281820`
- high entropy: `0.9831261039`

Mean territory energy:

- orderly: `1.0`
- irregular: `1.0000001192`

Result:

`ISOLATED ENTROPY IRREGULARITY PASS`

### Experimental Control Rule

For causal-normalized unsigned raw quantities:

- `-1` = unusually low relative to recent history;
- `0` = near recent baseline;
- `+1` = unusually high relative to recent history.

Therefore `0` must not be treated as equivalent to "feature disabled."

When isolating one temporal magnitude feature, other magnitude features must
be explicitly fixed to the intended control condition.

## Interpretation

The temporal encoder passed the intended independent mechanism tests without
parameter adjustment based on downstream neural response.

The initial failed volatility experiment is retained as part of the
experimental record.

