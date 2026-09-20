# SQ-03F.3 — MADE MEN

**Status:** FROZEN BEFORE ANALYSIS  
**Parent:** SQ-03F.2 — THE CAPO TEST  
**Class:** source-hotspot recurrence randomization test

## Motivation

SQ-03F.2 showed that hotspot-associated edges tend to come from sources with
greater aggregate outgoing capacity. Its preregistered unique-source sensitivity
preserved the source-strength difference while weakening the earlier
concentration story.

Hotspot edges are nevertheless highly source-recurrent:

- roughly 80% of S hotspot edges share a source with another S hotspot edge;
- roughly 82% of C hotspot edges share a source with another C hotspot edge.

That observation is not sufficient by itself. Large or highly represented
sources may simply have more opportunities to appear among hotspot edges.

SQ-03F.3 freezes an opportunity-aware randomization reference before inspecting
that question.

Family Model translation:

> **Do the same capos keep showing up in different jobs, or do big crews just get
> more chances to make the books?**

## Frozen hotspot sets

Reuse the exact SQ-03F hotspot memberships:

- S: top 1% by max integrated `S`;
- C: top 1% by max integrated `C`.

No hotspot is reranked, added, removed, or redefined.

No neural dynamics are executed.

## Source identity

A source is the conservative matched-graph `pre` neuron label.

Parallel conservative edge rows remain separate edge opportunities.

## Context identity

A context signature is the ordered pair:

`(input, anchor)`

from the SQ-03D/SQ-03B candidate membership.

## Primary observed metrics

For S and C independently:

1. unique hotspot-source count;
2. fraction of hotspot edges whose source contributes at least two hotspot
   edges;
3. maximum hotspot-edge count contributed by one source;
4. HHI of hotspot-edge counts across hotspot-producing sources.

## Secondary metrics

Also report:

- median hotspot-edge count per hotspot-producing source;
- top-1 source share of hotspot edges;
- top-5 source share of hotspot edges;
- number of sources represented by hotspot edges in at least two distinct
  input-anchor context signatures;
- maximum number of distinct hotspot context signatures represented by one
  source.

## Opportunity audit

For every candidate source calculate:

- candidate edge count;
- sum of candidate-edge `context_count`;
- distinct candidate `(input, anchor)` context signatures.

These quantities are descriptive and remain fixed during randomization.

## Frozen null model

### STRATIFIED HOTSPOT-LABEL RANDOMIZATION

Run **10,000** iterations with seed **314159**.

S and C are randomized independently.

Strata are defined by the exact tuple:

1. `context_count`;
2. total-weight decile;
3. absolute-weight-difference decile.

Within every stratum:

- preserve the exact observed number of hotspot labels;
- randomly assign those labels to candidate edges without replacement;
- leave source identity fixed;
- leave edge context memberships fixed.

Therefore every iteration preserves the hotspot-set size and its
context-count/structural-stratum composition.

It does **not** preserve source hotspot counts. That is the quantity under test.

## Reporting

For each primary and secondary recurrence metric report:

- observed value;
- randomization median;
- randomization 5th percentile;
- randomization 95th percentile;
- observed/null-median ratio when defined;
- descriptive null percentile rank.

No p-values.

No post-hoc significance threshold.

The percentile rank is a model-internal randomization reference, not a
biological population probability.

## Frozen interpretation

If observed hotspots occupy fewer sources, show a larger repeated-source edge
fraction, or have greater source-count HHI than the stratified null reference,
the result is compatible with source recurrence beyond edge opportunity alone.

If observed values are compatible with the stratified reference, the apparent
recurrence is compatible with opportunity and the frozen edge-level strata.

Cross-context source reuse is descriptive only.

## Claim boundary

SQ-03F.3 is a graph-level randomization analysis inside the frozen MoscaQuant
matched-central-brain model.

It does not establish biological neuron classes, biological sex mechanisms,
living-fly behavior, population effects, or financial utility.

**THE FAMILY EXPLAINS THE RACKET. IT DOES NOT CHANGE THE BOOKS.**
