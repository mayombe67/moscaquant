# SQ-03F.4 — THE SIT-DOWN

**Status:** FROZEN BEFORE ANALYSIS  
**Parent:** SQ-03F.3 — MADE MEN  
**Class:** source-level matched recurrence phenotype test

## Motivation

SQ-03F.3 showed that hotspot edges are substantially more concentrated into a
small set of recurring source neurons than expected under a stratified
hotspot-label randomization that preserves edge-level opportunity.

That result establishes recurrence inside the frozen model.

It does not yet tell us what source-level graph properties distinguish the most
recurrent sources.

SQ-03F.4 moves the unit of analysis from edges to sources.

Family Model translation:

> **Put a made source across the table from somebody with the same number of jobs
> and ask what is actually different about the operation.**

## Candidate source universe

Use every unique `pre` source represented by the frozen 114,825 candidate edges.

Reuse the exact S and C hotspot memberships from SQ-03F.

No hotspot is redefined.

No neural dynamics are executed.

## MADE source definition

For S and C separately:

1. count hotspot edges contributed by each candidate source;
2. rank sources by hotspot-edge count descending;
3. break ties by source label ascending;
4. select exactly the top 1% of candidate sources:
   `k = ceil(candidate_source_count * 0.01)`;
5. require at least one hotspot edge.

No tie expansion.

S and C made-source sets remain separate analyses.

## Opportunity matching

Each made source receives at most one control source.

Controls are selected without replacement from candidate sources outside the
current made-source set.

Controls must match exactly on equal-count deciles of:

1. candidate edge count;
2. sum of candidate-edge `context_count`;
3. distinct candidate `(input, anchor)` context-signature count.

Made sources are processed in:

1. hotspot-edge count descending;
2. source label ascending.

Within the exact three-bin stratum choose the unused control minimizing:

1. absolute candidate-edge-count difference;
2. absolute summed-context-count difference;
3. absolute distinct-context-count difference;
4. source label ascending.

If no control exists, record the made source as unmatched.

**Do not widen bins.**

## Primary source features

Compare:

- source out-strength;
- source mean outgoing weight;
- source maximum outgoing weight;
- source outgoing conservative edge-row count.

## Secondary source features

Also report:

- source median outgoing weight;
- top-1 output share;
- top-5 output share;
- outgoing-weight HHI;
- distinct downstream target count;
- target diversity ratio =
  `distinct downstream target count / source outgoing edge-row count`.

## Reporting

For every feature and for S/C separately report:

- made-source median;
- matched-control median;
- median paired difference;
- fraction made > control.

Also report:

- candidate-source count;
- made-source `k`;
- matched and unmatched counts;
- exact opportunity-bin audit;
- overlap between S-made and C-made source sets.

No p-values.

No post-hoc significance threshold.

## Frozen interpretation

If made sources retain greater outgoing strength or heavier outgoing weights
after opportunity matching, recurrent hotspot production is associated with
source-level network properties beyond opportunity alone.

If those differences collapse, the SQ-03F.2 source phenotype is compatible with
the same source-opportunity structure that helps generate recurrence.

Concentration and target-diversity features remain descriptive.

## Claim boundary

SQ-03F.4 is a source-level graph analysis inside the frozen MoscaQuant model.

It does not establish a biological neuron class, biological hierarchy,
biological sex mechanism, living-fly behavior, population effect, or financial
utility.

**THE FAMILY EXPLAINS THE RACKET. IT DOES NOT CHANGE THE BOOKS.**
