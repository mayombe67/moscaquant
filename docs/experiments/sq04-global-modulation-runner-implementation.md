# SQ-04 — GLOBAL MODULATION SENSITIVITY Runner Implementation

**Status:** PRE-RUN IMPLEMENTATION FREEZE  
**Protocol:** `config/experiments/sq04_global_modulation_v1.json`  
**Protocol commit:** `c1f758a`

No result-bearing SQ-04 execution should occur before this runner and its tests
are committed.

## Runtime path

SQ-04 reuses the frozen MQ-2.1 / SQ-01 scientific path:

`synthetic_series -> market_window_at -> compute_features -> CausalNormalizer
-> MarketVisionTemporalEncoder -> VisualTransductionRuntime`

The experiment uses synthetic Condition A only.

It is not an A/B discrimination experiment.

## Fixed scientific state

The runner fixes:

- frame count: `16`;
- `dt_ms = 1.0`;
- reset: `0.0`;
- frozen MaleCNS connectome;
- frozen market encoding;
- frozen causal normalization;
- frozen sensory gain;
- frozen visual-transduction release gain.

Only `threshold` or `tau_ms` differs by variant.

## Variant implementation

The runner consumes the variant matrix directly from the frozen SQ-04 JSON
protocol.

No additional parameter variants are generated at runtime.

## Repeated-run determinism

Every frozen variant is run twice.

Exact equality is required for:

- retinal hash;
- neural hash;
- relay hash;
- wider-network hash;
- retinal spike count;
- relay spike count;
- wider-network spike count;
- first relay spike time;
- first wider-network spike time;
- final voltage hash;
- final voltage minimum;
- final voltage maximum.

A determinism failure aborts the experiment.

## Reference comparison

After all repeated-run checks pass, each variant is compared against
`REFERENCE`.

The result artifact records a per-field boolean difference map.

This does not label higher or lower activity as beneficial.

## Output

`artifacts/sidequests/sq04-global-modulation-v1.json`

Results interpretation is written only after the complete artifact has been
reviewed.

## Boundary

This runner implements computational sensitivity only.

It does not simulate or identify dopamine, serotonin, octopamine, hormones,
receptors, or any biological neuromodulatory system.

It performs no ORACLE/D6, WARDEN, Sugar Cube, broker, financial, plasticity, or
profitability operation.
