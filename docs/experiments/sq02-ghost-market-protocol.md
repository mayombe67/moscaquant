# SQ-02 — GHOST MARKET

## Adversarial Input Robustness Protocol

**Status:** FROZEN BEFORE EXECUTION  
**Class:** Scientific side quest / diagnostic robustness characterization  
**Parent scientific baseline:** frozen MQ-2.1 market-to-visual pipeline

## Question

How does the frozen MoscaQuant market-to-neural pipeline behave when its input
boundary receives malformed feature tensors, temporally adversarial but
structurally valid feature sequences, or finite extreme values?

This is a characterization experiment. It is not a search for a desirable
downstream response.

## Why this experiment exists

SQ-01 established that simulated neural time and wall-clock execution rate must
remain separate. SQ-02 therefore holds scientific time fixed and perturbs only
the input representation presented to the frozen market-to-neural pipeline.

The Charter requires timestamps and identifiers for event records, defines
stale-data detection as a WARDEN responsibility, and requires ambiguous
financial state to fail closed. SQ-02 does **not** test those operational
WARDEN controls. It tests the scientific input pipeline upstream of financial
authority.

## Frozen clock rule

`dt_ms` and all other scientific neural-time parameters remain unchanged.

Machine speed, process scheduling, runtime latency, and wall-clock duration are
not scientific variables in SQ-02.

## Stage A — FEATURE_INTERFACE

Stage A asks whether the existing feature boundary explicitly rejects malformed
feature tensors before neural execution.

Frozen variants:

- `BASELINE_VALID`
- `FEATURE_NAN`
- `FEATURE_POS_INF`
- `FEATURE_NEG_INF`
- `FEATURE_SHORT_ROW`
- `FEATURE_LONG_ROW`

The experiment records acceptance/rejection and exception type.

A malformed input that is explicitly rejected does not proceed to neural
execution.

A malformed non-finite or shape-invalid input that reaches neural execution
without explicit rejection is recorded as an input-boundary weakness.

## Stage B — TEMPORAL_SEQUENCE

Stage B uses structurally valid feature frames and alters sequence structure
without changing simulated neural time.

Frozen variants:

- `SEQUENCE_BASELINE`
- `SEQUENCE_DUPLICATE_FRAME`
- `SEQUENCE_DROP_FRAME`
- `SEQUENCE_REVERSED`
- `SEQUENCE_FROZEN`

These are not labeled "bad" merely because neural output changes. A deterministic
difference is evidence of temporal-input sensitivity.

This stage does not claim that feature-frame ordering is equivalent to exchange
timestamps. Raw-feed timestamp validation is a separate future interface test
unless the existing replay API exposes that contract directly.

## Stage C — FINITE_EXTREMES

Frozen variants:

- `EXTREME_X10`
- `EXTREME_X100`
- `ZERO_VECTOR`

Only finite values are used in this stage.

The purpose is to characterize whether unusually large but finite feature
magnitudes cause bounded, saturated, qualitatively altered, or unchanged
responses under the frozen pipeline.

## Required measurements

For every variant where neural execution is possible, record:

- accepted / rejected;
- exception type if rejected;
- deterministic A/A replay result;
- encoded frame count;
- retinal stimulus summary;
- relay spike count;
- wider-network spike count;
- first relay spike time in simulated milliseconds when present.

## Determinism gate

Each accepted variant SHALL be replayed at least twice under identical
scientific configuration.

A variant is deterministic only if the recorded scientific outputs match across
the repeated run.

Failure of determinism is itself a result and stops interpretive escalation for
that variant.

## Interpretation rules

1. Rejection of malformed input is reported as rejection, not robustness of the
   connectome.
2. Acceptance of malformed non-finite or shape-invalid input into neural
   execution is an input-boundary weakness.
3. Temporal mutation changing neural output is temporal-input sensitivity, not
   automatically failure.
4. Finite extreme sensitivity is not evidence of financial usefulness.
5. No effect is a valid result.
6. Results SHALL NOT be used to retune the frozen pipeline and rerun SQ-02 until
   a preferred pattern appears.
7. Any later mitigation or validator introduced because of SQ-02 must be a
   separately versioned engineering/scientific change and tested independently.

## Explicit exclusions

SQ-02 performs no:

- broker interaction;
- execution-adapter interaction;
- WARDEN authorization;
- Sugar Cube state transition;
- D6 / ORACLE perturbation;
- position sizing;
- financial decision assignment;
- profitability evaluation;
- live-data claim.

The Charter's stale-feed → Sugar Cube / WARDEN behavior remains an operational
containment concern and is not simulated here.

## Claim boundary

SQ-02 is a deterministic adversarial-input sensitivity analysis of the frozen
MoscaQuant market-to-neural computational pipeline. It characterizes input
rejection and neural response under malformed or temporally perturbed inputs.
It does not establish biological robustness, financial usefulness,
profitability, live-trading safety, or WARDEN containment performance.

## Execution rule

Protocol/config/tests are committed before the first result-bearing execution.

Post-run interpretation is recorded separately from this frozen protocol.
