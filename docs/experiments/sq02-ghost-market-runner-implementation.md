# SQ-02 — GHOST MARKET Runner Implementation Note

**Status:** PRE-RUN IMPLEMENTATION FREEZE  
**Protocol:** `config/experiments/sq02_ghost_market_v1.json`  
**Protocol commit:** `6a569b2`

This note fixes runner choices that the frozen SQ-02 protocol intentionally
described only at the experiment-class level.

No result-bearing SQ-02 execution should occur before this runner and its tests
are committed.

## Scientific runtime

The runner uses the frozen MQ-2.1 path already exercised by SQ-01:

`synthetic_series -> market_window_at -> compute_features -> CausalNormalizer
-> MarketVisionTemporalEncoder -> VisualTransductionRuntime`

Scientific neural time is fixed at:

- `frame_count = 16`
- `dt_ms = 1.0`
- `tau_ms = 20.0`
- `threshold = 1.0`
- `reset = 0.0`
- release gain loaded from the frozen visual-transduction configuration

The runner uses synthetic **Condition A**. SQ-02 is not an A/B discrimination
experiment.

## Stage A implementation

Malformed tensors are injected after causal normalization and before
`MarketVisionTemporalEncoder.encode_sequence()`.

The actual frozen encoder boundary is called directly.

If the encoder rejects the tensor, rejection type/message are recorded and
neural execution is not entered.

If the encoder accepts the malformed tensor, that fact is recorded and the
single observation is executed in an isolated fresh neural runtime. No state is
shared with another variant.

The mutated cell for NaN/+Inf/-Inf is `[asset row 0, feature column 0]`.

Shape mutations affect all six asset rows:

- short: `6 x 6`
- long: `6 x 8`

## Stage B implementation

A "feature frame" is operationalized as one normalized `6 x 7` observation
tensor before it enters the frozen 16-frame temporal encoder.

The deterministic mutation location is:

`OBSERVATIONS // 2`

The variants are implemented as:

- duplicate: insert a copy of the midpoint observation immediately before the
  original midpoint;
- drop: remove the midpoint observation;
- reversed: reverse the complete observation sequence;
- frozen: repeat the midpoint observation for the original sequence length.

This is intentionally not described as exchange-timestamp manipulation.

## Stage C implementation

The finite-extreme mutation is applied only at the midpoint observation.

The selected signed feature is:

- asset row: `0`
- feature column: `1`
- feature: `momentum`

`EXTREME_X10` and `EXTREME_X100` multiply only that cell.

`ZERO_VECTOR` replaces the complete midpoint `6 x 7` tensor with finite zeros.

The selection is fixed before execution because momentum is signed and is
explicitly consumed by the frozen temporal encoder.

## Determinism

Every variant is executed twice under identical scientific configuration.

The runner requires exact equality of recorded hashes, spike counts, first relay
time, encoded frame count, and final voltage hash.

A determinism failure aborts the run.

## Output

Result artifact:

`artifacts/sidequests/sq02-ghost-market-v1.json`

Interpretation/results documentation is created only after the complete artifact
has been inspected.

## Boundary

This runner does not invoke WARDEN-01, Sugar Cube Mode, ORACLE/D6, broker code,
financial execution, position sizing, or profitability analysis.
