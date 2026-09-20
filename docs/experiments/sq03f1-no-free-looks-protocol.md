# SQ-03F.1 — NO FREE LOOKS

## Context-Count Matched Hotspot Verification

**Status:** FROZEN BEFORE ANALYSIS  
**Parent:** SQ-03F — HOTSPOT TEST

## Motivation

SQ-03F found that dynamic hotspot edges tend to sit in higher-throughput local
network neighborhoods. It also found that hotspots are represented in more
SQ-03D input/anchor contexts than their structurally matched controls.

Because SQ-03E/SQ-03F hotspot strength is defined as the **maximum** modeled
dynamic effect observed across an edge's represented contexts, an edge with
more contexts has more opportunities to produce a large maximum.

SQ-03F.1 controls that opportunity difference directly.

## Question

> Do the SQ-03F hotspot network-position differences persist when hotspot and
> control edges have the exact same represented context count?

## Frozen hotspot sets

Reuse the exact SQ-03F hotspot memberships.

- Primary: SQ-03F top 1% by max integrated `S`.
- Secondary: SQ-03F top 1% by max integrated `C`.

Do not rerank or redefine hotspots.

## Exact matching

Each hotspot may receive at most one control.

Controls must match the hotspot exactly on:

1. `context_count`;
2. total-weight decile;
3. absolute-weight-difference decile.

Selection is without replacement.

The `S` and `C` hotspot sets are matched independently.

Within the exact three-way stratum, choose the available control minimizing:

1. absolute total-weight difference;
2. absolute absolute-weight-difference difference;
3. ascending `edge_id`.

If no unused control exists in the exact stratum, mark the hotspot unmatched.

**Do not relax context count. Do not widen structural bins.**

## Network-position outcomes

Primary:

- source out-degree;
- target in-degree;
- source output fraction;
- target input fraction.

Secondary:

- source out-strength;
- target in-strength;
- endpoint degree product.

`context_count` is a matching variable only in SQ-03F.1 and is not evaluated as
an outcome.

## Frozen summaries

For each feature and hotspot set report:

- hotspot median;
- matched-control median;
- median paired difference;
- fraction of pairs where hotspot > control.

Also report:

- matched count;
- unmatched count;
- matched fraction;
- exact context-count matching audit;
- exact structural-bin matching audit.

No p-values or post-hoc significance thresholds are generated.

## Interpretation

SQ-03F.1 is a robustness check on the SQ-03F network-position result.

A pattern may be described as surviving context-count control only if its
direction remains the same after the exact matching design above.

Failure to preserve a pattern is a valid result and indicates that SQ-03F's
apparent topology association may have been partly driven by unequal
opportunity to produce large maxima.

## Claim boundary

SQ-03F.1 may describe whether SQ-03F local network-position differences remain
after exact matching on represented intervention context count and frozen
structural bins.

It does not establish biological sex mechanisms, biological population
differences, organism behavior, intelligence differences, or financial utility.
