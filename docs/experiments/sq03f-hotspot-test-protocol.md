# SQ-03F — HOTSPOT TEST

## Dynamic Hotspot Network-Position Protocol

**Status:** FROZEN BEFORE ANALYSIS  
**Parent:** SQ-03E — STRUCTURE IS NOT DESTINY

## Question

SQ-03E showed that structural male/female edge-weight difference is a poor
general proxy for modeled dynamic consequence.

SQ-03F asks:

> Do the strongest dynamic hotspot edges occupy distinctive local network
> positions that simple structural difference misses?

## Frozen hotspot sets

Analyze separately:

1. **Primary:** top 1% of edges by maximum integrated total-effect magnitude `S`.
2. **Secondary:** top 1% of edges by maximum integrated context residual `C`.

For each set:

- `k = ceil(N * 0.01)`;
- ties are broken by ascending `edge_id`;
- exactly `k` edges are selected;
- ties never expand the set.

## Frozen graph

Use the same conservative matched graph:

`verdict_corr == "isomorphic" AND weight_m > 0 AND weight_f > 0`

Direction is `pre -> post`.

For weighted local topology:

`reference edge weight = (weight_m + weight_f) / 2`

## Primary network-position features

- source out-degree;
- target in-degree;
- source output fraction;
- target input fraction.

Where:

`source output fraction = mean edge weight / source mean-weight out-strength`

`target input fraction = mean edge weight / target mean-weight in-strength`

## Secondary features

- source out-strength;
- target in-strength;
- source-out-degree × target-in-degree;
- frozen SQ-03D context count.

No global-centrality feature is introduced after results are seen.

## Structurally matched controls

Each hotspot is paired with at most one non-hotspot control.

Controls must be in the exact same:

- total-weight decile; and
- absolute-weight-difference decile.

Selection is without replacement.

Hotspots are processed in frozen dynamic-score descending order, breaking ties
by ascending `edge_id`.

Among available controls in the exact same two-dimensional structural bin,
select the edge minimizing, in order:

1. absolute total-weight difference;
2. absolute absolute-weight-difference difference;
3. ascending `edge_id`.

If no unused control exists in the exact bin, record the hotspot as unmatched.
Do not widen the bin.

The `S` and `C` hotspot analyses are matched independently.

## Frozen comparisons

For every feature report:

- hotspot median;
- matched-control median;
- median paired difference;
- fraction of matched pairs where hotspot > control.

Also report the number and fraction of hotspots successfully matched.

No p-values, biological confidence intervals, or post-hoc significance
thresholds are generated.

## Negative-control check

Report absolute structural weight difference for hotspot/control pairs.

## Claim boundary

SQ-03F may describe network-position features associated with strong modeled
dynamic effects inside the frozen MoscaQuant matched-central-brain model.

It does not establish biological sex mechanisms, population-level biological
effects, organism behavior, intelligence differences, or financial usefulness.
