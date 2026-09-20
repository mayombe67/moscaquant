# SQ-03F.2 — THE CAPO TEST

**Status:** FROZEN BEFORE ANALYSIS  
**Parent:** SQ-03F.1 — NO FREE LOOKS  
**Class:** source-level hotspot decomposition

## Motivation

SQ-03F suggested that dynamic hotspot edges occupied busier network positions.
SQ-03F.1 then matched hotspot and control edges on represented context count as
well as the frozen structural bins. Most degree-based differences collapsed.

The clearest surviving association was larger **source out-strength** for
hotspot edges, while the hotspot edge itself represented a smaller fraction of
its source's total output.

That leaves a narrower question:

> Is the focal edge responsible for the source-strength result, or does the
> hotspot edge sit inside a source neuron with broadly larger outgoing weight?

Family Model translation:

> **Is the edge the boss, or does it work for a capo?**

## Frozen universe

Reuse the same conservative matched-central-brain graph, 114,825 candidate
edges, mean reference weight `(weight_m + weight_f) / 2`, and exact S/C hotspot
sets. No hotspot is added, removed, reranked, or redefined. No neural dynamics
are executed.

## Frozen matching

Deterministically reconstruct the SQ-03F.1 matched-control design. Controls must
match exactly on `context_count`, total-weight decile, and
absolute-weight-difference decile. Matching remains 1:1, without replacement,
and no widening is permitted.

The analyzer must reproduce the SQ-03F.1 source-out-strength summaries before
new decomposition results are accepted.

## Primary features

### 1. Leave-one-edge-out source strength

`LOO source strength = total source out-strength - focal mean_weight`

If parallel graph rows exist, remove only the focal row.

### 2. Leave-one-edge-out mean outgoing weight

`LOO mean outgoing weight = LOO source strength / number of other outgoing rows`

Null if the source has no other outgoing conservative edge row.

## Secondary source features

Report source outgoing edge-row count, source median outgoing mean-weight,
source maximum outgoing mean-weight, top-1 output share, top-5 output share,
outgoing-weight HHI, and focal-edge output-rank percentile within the source.

## Primary unit

The primary unit remains the matched hotspot-edge/control-edge pair. Because
multiple hotspot edges may share one source, also report unique hotspot-source
count, unique control-source count, fraction of hotspot edges sharing a source
with another hotspot edge, and a descriptive unique-source sensitivity summary.

## Reporting

For every feature and for both S and C hotspot sets report hotspot median,
matched-control median, median paired difference, and fraction hotspot > control.

No p-values. No new significance threshold.

## Frozen interpretation

If leave-one-edge-out source strength retains the SQ-03F.1 direction, the
association is broader than the focal edge itself.

If leave-one-edge-out mean outgoing weight and/or source median outgoing weight
are higher while outgoing edge count remains similar, the result is compatible
with generally heavier source outputs rather than merely more outputs.

If top-share and HHI measures are higher, a small number of dominant outgoing
edges may account for the source-strength association.

These outcomes are not mutually exclusive.

## Claim boundary

SQ-03F.2 describes graph properties inside the frozen MoscaQuant model. It does
not identify a biological neuron class, biological hierarchy, sex mechanism,
living-fly behavior, population effect, or financial utility.

Family Model language remains presentation-only.

**THE FAMILY EXPLAINS THE RACKET. IT DOES NOT CHANGE THE BOOKS.**
