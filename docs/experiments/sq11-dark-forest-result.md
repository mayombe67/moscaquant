# SQ-11 — DARK FOREST — Result

## Status

**SEALED / COMPLETED**

SQ-11 DARK FOREST resolved the numerical-mechanistic ambiguity left by
SQ-10 SOPHON.

The experiment asked whether the three sub-resolution BODY responder effects
could be reconstructed from the frozen local P2 presynaptic state and exact
float32 CSR row arithmetic, and whether any remaining difference required
source-state divergence, network interaction, or only the floating-point
accumulation path.

No new neural execution is authorized by this result document.

## Authoritative frozen state

Final analysis freeze commit:

`054a6c2b3fc06898f4d20cb31e6cd0ca9a9e6e26`

Authoritative execution evidence:

`artifacts/experiments/sq11-dark-forest/sq11-dark-forest-evidence-v2.npz`

SHA-256:

`cef49b5e581d6c9b2f21aafc701d06e8d53b0abc03f8453c9fe6c5d19ede9c37`

Authoritative publication receipt:

`artifacts/experiments/sq11-dark-forest/sq11-dark-forest-publication-receipt-v2.json`

SHA-256:

`2f0f7aeb6d0183d8dd918abd81563ac187eb70e2b3f6ea1559856625bf090eff`

Authoritative analysis:

`artifacts/experiments/sq11-dark-forest/sq11-dark-forest-analysis-v1.json`

SHA-256:

`b97a43514f9c3ec1f61675444fab284e61e5dd5341f926745e3390f5fe693779`

## Execution closure

The frozen execution completed all 16 authorized work units.

All eight deterministic replicate pairs reproduced exactly.

Independent verification passed before and after publication.

The analysis phase performed no neural execution.

The qualified replay-v2 implementation then reproduced all stored P3 responder
synaptic values using explicit float32 CSR accumulation with structural BODY-edge
omission:

- exact float32 replay comparisons: `9,216`
- replay mismatches: `0`
- tolerance: exact equality

## Primary result

All 12 preregistered matched one-edge contrasts produced a first P3 responder
divergence.

Classification counts:

- `DIRECT_TERM_EXACT_FLOAT32`: `4`
- `DIRECT_TERM_WITH_FLOAT32_ROUNDING_PATH`: `8`
- `SOURCE_STATE_DIVERGES_BEFORE_OR_AT_P3`: `0`
- `NO_P3_DIVERGENCE`: `0`

### BODY A

All four matched backgrounds produced the same result.

First P3 responder divergence:

`frame 125`

Observed runtime delta:

`1.2836295915086282e-10`

Isolated float32 direct BODY contribution:

`1.2836295915086282e-10`

Rounding-path residual:

`0.0`

Classification:

`DIRECT_TERM_EXACT_FLOAT32`

### BODY B

All four matched backgrounds produced the same result.

First P3 responder divergence:

`frame 124`

Observed runtime delta:

`5.276063053116786e-08`

Isolated float32 direct BODY contribution:

`5.276063319570312e-08`

Rounding-path residual:

`-2.6645352591003757e-15`

Classification:

`DIRECT_TERM_WITH_FLOAT32_ROUNDING_PATH`

### BODY C

All four matched backgrounds produced the same result.

First P3 responder divergence:

`frame 127`

Observed runtime delta:

`2.3104781976535094e-14`

Isolated float32 direct BODY contribution:

`2.3104451633685665e-14`

Rounding-path residual:

`3.3034284942917713e-19`

Classification:

`DIRECT_TERM_WITH_FLOAT32_ROUNDING_PATH`

## Source-state result

For every matched contrast, the BODY source state was exact through the first
P3 divergence.

The complete preserved P2 presynaptic state feeding the corresponding responder
row was also exact through that divergence.

No source-state divergence was observed.

## Background result

For each BODY edge, the first-divergence frame, classification, observed delta,
and residual were invariant across all four states of the other two BODY
lesions.

No background dependence was observed at the first P3 responder divergence.

## Interpretation

SQ-11 resolves the microscopic effects first isolated by SQ-10 SOPHON.

BODY A is exactly the isolated direct BODY contribution under the frozen
float32 arithmetic.

BODY B and BODY C are also local direct BODY effects, but structural removal of
their CSR entries changes the float32 accumulation path and produces tiny,
deterministic residuals.

The replay-v2 result demonstrates that these residuals are completely
reconstructed by the frozen local state and CSR arithmetic.

They therefore do not require an additional recurrent, cross-path, or
source-state contribution at this endpoint.

## Boundary

SQ-11 establishes a result only for the frozen MoscaQuant computational model
and measurement clock.

It does not establish:

- a biological mechanism in a living animal;
- cognition;
- consciousness;
- perception;
- intention;
- behavior;
- learning;
- market prediction;
- financial value.

In particular, the BODY B and BODY C residuals are computational floating-point
effects and must not be described as biological amplification or neural
interaction.

## Next scientific question

SQ-11 explains what enters the immediate BODY responder boundary.

The next question is what happens after that now-understood local perturbation
enters the downstream network.

That question is reserved for:

**SQ-12 — RESONANCE CASCADE**

SQ-12 requires its own preregistration and authorization before any new neural
execution.

Science first.

Lulz a very close second.
