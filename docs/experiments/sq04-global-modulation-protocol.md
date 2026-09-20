# SQ-04 — GLOBAL MODULATION SENSITIVITY

## Computational Parameter Sensitivity Protocol

**Status:** FROZEN BEFORE EXECUTION  
**Class:** Scientific side quest / computational sensitivity analysis  
**Parent baseline:** frozen MQ-2.1 visual-transduction runtime

## Why SQ-04

SQ-03 — CROSS-CONNECTOME STRUCTURED CONTROL was considered first.

The currently available local data contains the MaleCNS baseline plus existing
SHUFFLED MOSCA controls, but no second comparable whole-connectome substrate
suitable for a genuine cross-connectome experiment.

SQ-03 is therefore deferred rather than replaced with another randomized graph.

SQ-04 asks a different, narrower question:

> How sensitive is the frozen computational runtime to small global changes in
> spike threshold and membrane persistence while all sensory encoding,
> connectome structure, simulated time step, and release gain remain fixed?

## Important terminology boundary

"Global modulation" is a computational label only.

SQ-04 does not claim to model dopamine, serotonin, octopamine, hormones,
receptors, arousal, mood, reward chemistry, or any other biological
neuromodulatory system.

The manipulated variables are explicit model mechanics:

- spike threshold;
- membrane time constant `tau_ms`.

## Frozen baseline

The reference condition preserves:

- Condition A synthetic market input;
- frame count `16`;
- `dt_ms = 1.0`;
- `tau_ms = 20.0`;
- threshold `1.0`;
- reset `0.0`;
- frozen MaleCNS baseline connectome;
- frozen market feature/normalization/temporal encoding;
- frozen sensory gain;
- frozen visual-transduction release gain.

`dt_ms` may not change in SQ-04.

Wall-clock runtime remains non-scientific.

## Frozen variant matrix

| Variant | Threshold | tau_ms | Interpretation class |
|---|---:|---:|---|
| `REFERENCE` | 1.0 | 20.0 | Reference |
| `THRESHOLD_LOW_10` | 0.9 | 20.0 | Global excitability sensitivity |
| `THRESHOLD_HIGH_10` | 1.1 | 20.0 | Global excitability sensitivity |
| `TAU_FAST_25` | 1.0 | 15.0 | Membrane persistence sensitivity |
| `TAU_SLOW_25` | 1.0 | 25.0 | Membrane persistence sensitivity |

Only one parameter differs from REFERENCE in each non-reference arm.

## Measurements

For every variant record:

- exact A/A determinism;
- retinal, neural, relay, and wider-network hashes;
- retinal spike count;
- relay spike count;
- wider-network spike count;
- first relay spike time in simulated milliseconds;
- first wider-network spike time in simulated milliseconds;
- final voltage hash;
- final voltage maximum and minimum.

## Determinism gate

Each variant SHALL be executed at least twice with identical scientific
configuration.

If repeated runs differ on any frozen scientific output, that variant fails the
determinism gate and receives no higher-level interpretation.

## Interpretation rules

1. A deterministic difference from `REFERENCE` is computational parameter
   sensitivity.
2. No deterministic difference is a valid null result.
3. A larger numerical response is not automatically "better."
4. A smaller numerical response is not automatically "safer."
5. Asymmetry or non-monotonicity is reported descriptively unless a separate
   interaction or trend test is preregistered.
6. Wider-network spike emergence, if observed, is recorded but does not by
   itself validate biological propagation.
7. Results shall not be used to retune the frozen model and rerun SQ-04 until a
   preferred pattern appears.

## Explicit exclusions

SQ-04 performs no:

- biological neuromodulator assignment;
- plasticity or learning;
- ORACLE/D6 perturbation;
- WARDEN authorization;
- Sugar Cube transition;
- broker or execution-adapter interaction;
- financial-decision assignment;
- profitability evaluation.

## Claim boundary

SQ-04 measures deterministic sensitivity of the frozen MoscaQuant computational
runtime to small global changes in spike threshold and membrane time constant.
These parameters are model mechanics. The experiment does not identify or
simulate a biological neuromodulatory system, establish biological realism,
test learning, or demonstrate financial usefulness.

## Execution rule

Protocol/config/tests are committed before the first result-bearing execution.

Runner implementation choices are frozen in a separate pre-run implementation
record before execution.
