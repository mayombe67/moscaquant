# SQ-03E — STRUCTURE IS NOT DESTINY

## Structural Difference vs Dynamic Consequence Protocol

**Status:** FROZEN BEFORE ANALYSIS  
**Class:** Deterministic structure-vs-dynamics census  
**Parents:** SQ-03B, SQ-03D, SQ-03D.1

## Question

The aligned MaleCNS/FlyWire edge table gives direct structural comparison
variables for matched edges, including male and female edge weights and
corrected structural-comparison statistics.

MoscaQuant now also has a complete counterfactual intervention census.

SQ-03E asks:

> Do the edges that look most structurally different also produce the largest
> modeled dynamic consequences?

The null is scientifically acceptable.

## Primary unit of analysis

The primary unit is **one matched edge**.

SQ-03B/SQ-03D contain repeated observations for an edge because the same edge
may occur under multiple inputs and output anchors. SQ-03E collapses those
repeated contexts to one edge-level record before the primary association
analysis.

This prevents edges with more candidate memberships from receiving more weight.

## Structural predictors

### Primary

`abs_weight_difference = |weight_m - weight_f|`

### Secondary

- `|t|`
- `p_corr`
- `verdict_corr`
- `total_weight = |weight_m| + |weight_f|`
- relative weight difference:

`|weight_m - weight_f| / (|weight_m| + |weight_f|)`

with exact zero when the denominator is zero.

## Dynamic outcomes

For each edge, aggregate across every frozen SQ-03D `(input, anchor)` context.

### Primary

Maximum integrated-positive-voltage total effect magnitude:

`max S_integrated`

where:

`S = |ΔM| + |ΔL|`

### Secondary

- maximum integrated context residual `C`;
- maximum peak total effect magnitude `S`;
- maximum peak context residual `C`;
- median integrated total effect magnitude `S`;
- number of represented input/anchor contexts.

`A`, the normalized asymmetry ratio, is excluded from SQ-03E acceptance and
primary interpretation because SQ-03D.1 demonstrated that it is numerically
ill-conditioned under scalar replay near zero.

## Rank-association analysis

Freeze descriptive Spearman rank correlations for:

1. `|weight_m - weight_f|` vs `max S_integrated`;
2. `|weight_m - weight_f|` vs `max C_integrated`;
3. `|t|` vs `max S_integrated`;
4. `|t|` vs `max C_integrated`.

No p-values are generated.

These are descriptive rank associations over the deterministic frozen model
census.

## Structural-difference deciles

Edges are sorted by absolute male/female weight difference and partitioned into
ten deterministic deciles.

For each decile report:

- edge count;
- structural-difference range;
- median dynamic `S`;
- maximum dynamic `S`;
- median dynamic `C`;
- maximum dynamic `C`.

This tests whether increasingly large structural differences produce an
ordered increase in dynamic consequences.

## Extreme-overlap analysis

Freeze a top-1% comparison.

Compare the top 1% of edges by structural absolute weight difference against:

- the top 1% by `max S_integrated`;
- the top 1% by `max C_integrated`.

Report:

- overlap count;
- Jaccard index.

No post-hoc top-k alternative may replace the frozen 1% analysis.

## Absolute-weight stratification

A structural edge difference may appear predictive merely because the edge
itself is large.

Therefore edges are also partitioned into ten bins by:

`total_weight = |weight_m| + |weight_f|`

Within each total-weight bin, report the frozen structure-dynamics rank
associations.

This is descriptive control for absolute edge magnitude, not a causal
adjustment model.

## SQ-03D.1 handling

SQ-03D.1 formally failed its frozen all-metric scalar acceptance rule because
normalized asymmetry `A` did not reproduce under the direct ratio comparison.

That failure remains preserved.

However, SQ-03D.1 also established:

- 64/64 primitive subject metrics agreed with SQ-03B;
- integrated `C` reproduced for 32/32 selected pairs;
- integrated `S` reproduced for 32/32 selected pairs;
- peak `C` reproduced for 32/32 selected pairs;
- peak `S` reproduced for 32/32 selected pairs.

SQ-03E therefore uses only raw `C` and `S` quantities. It does not rehabilitate
or reuse `A` as an acceptance metric.

## Statistical boundary

SQ-03E is a deterministic census.

Edges and simulation rows are not treated as independent biological animals.

No biological population p-value, confidence interval, or significance
threshold is generated.

## Possible outcomes

All of these are valid:

- strong structural-dynamic alignment;
- weak alignment;
- alignment only for large absolute-weight edges;
- isolated dynamical hotspots with modest structural differences;
- effectively no useful structural prediction.

The experiment does not assume the title is true.

## Claim boundary

SQ-03E may describe how well structural male/female edge differences align with
modeled dynamic counterfactual consequences inside the frozen MoscaQuant
matched-central-brain system.

It does not establish:

- a biological sex mechanism;
- organism-level behavior;
- general male/female behavioral differences;
- population-level statistical significance;
- sex superiority;
- intelligence differences;
- market skill;
- profitability;
- financial usefulness.
