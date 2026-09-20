# SQ-03D — THE SAME KNIFE CUTS DIFFERENTLY

## Paired Connectome-Background Reciprocity Protocol

**Status:** FROZEN BEFORE ANALYSIS  
**Class:** Paired deterministic connectome-background analysis  
**Parents:** SQ-03B FIND THE DIFFERENCE; SQ-03C CHECK THE RECEIPTS

## Question

SQ-03B changed one matched edge at a time in both network backgrounds:

- MORTY received the corresponding LILITH edge weight.
- LILITH received the corresponding MORTY edge weight.

SQ-03D asks a different question from simple structural difference:

> When the same matched edge-weight difference is reversed in the two
> connectome backgrounds, are the modeled consequences reciprocal, or does
> the surrounding network alter what that same edge difference does?

No new neural dynamics are required for the primary SQ-03D analysis.

## Source evidence

The complete SQ-03B checkpoint ledger is the authoritative source:

`artifacts/sidequests/sq03b-checkpoints-v1/results.ndjson`

Expected SHA-256:

`7b2632de5792973534177b697efdd7c3af0b82a836d9d2b597812dbc0dd1f725`

A hash mismatch stops the analysis.

SQ-03C is used only as an already-completed scalar-verification subset when
both subject counterfactuals for the same paired observation are available.

## Pairing rule

The atomic SQ-03D observation is:

`(input, edge_id, anchor)`

Each observation must contain exactly one MORTY counterfactual and exactly one
LILITH counterfactual from SQ-03B.

Unpaired observations are an error. They are not silently dropped.

## Reciprocity definition

For a metric `Y`:

`ΔM = Y(MORTY with LILITH edge weight) - Y(MORTY native)`

`ΔL = Y(LILITH with MORTY edge weight) - Y(LILITH native)`

A locally reciprocal response would satisfy approximately:

`ΔM ≈ -ΔL`

SQ-03D therefore freezes three complementary quantities.

### Context residual

`C = |ΔM + ΔL|`

This is the primary quantity.

`C = 0` means exact reciprocity for that metric.

Larger `C` means a larger departure from reciprocal behavior.

### Total effect magnitude

`S = |ΔM| + |ΔL|`

This is reported alongside `C` so that a large normalized ratio produced by
two numerically tiny effects cannot masquerade as an important result.

### Normalized asymmetry

If `ΔM = 0` and `ΔL = 0` exactly:

`A = 0`

Otherwise:

`A = |ΔM + ΔL| / (|ΔM| + |ΔL|)`

`A` is bounded from 0 to 1.

It is a descriptive shape metric, not a significance statistic.

### Sign relation

- `OPPOSITE`: `ΔM * ΔL < 0`
- `SAME`: `ΔM * ΔL > 0`
- `ZERO_INVOLVED`: otherwise

Reciprocity predicts opposite directions, but sign alone is not sufficient:
magnitude remains part of the result.

## Primary endpoint

The primary SQ-03D endpoint is:

**integrated-positive-voltage context residual**

`C_integrated = |ΔM_integrated + ΔL_integrated|`

Integrated positive voltage is primary because SQ-03B already used it as a
major effect measure and because the raw residual naturally suppresses the
problem of extremely small effects receiving dramatic normalized ratios.

## Secondary endpoints

SQ-03D also reports:

- integrated-positive-voltage normalized asymmetry;
- integrated-positive-voltage total effect magnitude;
- integrated-positive-voltage sign relation;
- peak-voltage context residual;
- peak-voltage normalized asymmetry;
- peak-voltage total effect magnitude;
- peak-voltage sign relation;
- first-positive-frame pair relation.

A null first-positive-frame result remains a valid null.

## Frozen strata

Results are summarized globally and by:

`(input, anchor)`

Inputs:

- `TmY14`
- `LPLC2`
- `AVLP234`
- `AVLP435`

Anchors:

- `DNc02`
- `DNp27`
- `DNp30`

Only combinations actually represented by the frozen SQ-03B candidate
membership are reported.

## Frozen descriptive summaries

For context residual and total effect magnitude:

- p50
- p90
- p99
- p99.9
- maximum

For normalized asymmetry:

- p50
- p90
- p99
- maximum

Sign-relation counts are reported directly.

The same summaries are also reported across magnitude deciles. This prevents
the interpretation from being dominated by high asymmetry among negligible
effects.

No p-value is generated from deterministic simulation rows.

## Candidate ranking for a future experiment

SQ-03D may produce a candidate ranking, but it does not execute those
candidates.

Ranking is frozen as:

1. integrated-positive-voltage context residual — descending;
2. peak-voltage context residual — descending;
3. integrated-positive-voltage total effect magnitude — descending;
4. edge ID — ascending.

This ranking exists only to support a separately frozen scalar follow-up.

## SQ-03C verification subset

For any `(input, edge_id, anchor)` where both subject counterfactuals were
independently scalar-verified in SQ-03C, SQ-03D reports the same reciprocity
metrics as a verification subset.

The subset does not replace the complete SQ-03B census.

## Statistical boundary

SQ-03D is a deterministic census of frozen model interventions.

Simulation rows are not treated as independent biological samples.

SQ-03D therefore does not manufacture:

- population p-values;
- confidence intervals pretending to represent flies;
- a formal biological significance threshold.

## Claim boundary

A nonzero reciprocity residual supports a model-level statement:

> The same matched male/female edge-weight difference can have different
> consequences when embedded in the two frozen matched network backgrounds.

SQ-03D does **not** establish:

- a biological sex mechanism in living flies;
- organism-level behavior;
- general male/female behavioral differences;
- sex superiority;
- intelligence differences;
- population-level statistical significance;
- market skill;
- profitability;
- financial usefulness.
