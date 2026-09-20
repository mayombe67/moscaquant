# SQ-03F.4 — THE SIT-DOWN — Results

**Status:** COMPLETE  
**Authoritative artifact:** `artifacts/sidequests/sq03f4-sit-down-result-v1.json`  
**Artifact SHA256:** `268d42d5e697a879abac92586596c8ecbf9f86893777ff2b4e19ea806d3d6db0`  
**Parent SQ-03F.3 SHA256:** `4a6d47be04d8ac31e5994e5ff83f3d8722840e41ebf104e03dc982e7399f0788`

## Design

SQ-03F.4 moved the unit of analysis from hotspot edges to source neurons.

The analysis selected the exact top 1% of candidate sources by hotspot-edge
recurrence separately for S and C, then matched each made source to a non-made
control on the frozen opportunity bins:

- candidate-edge-count decile;
- summed candidate-context-count decile;
- distinct candidate-context-signature-count decile.

No new neural dynamics were executed.

## Universe

- candidate edges: `114825`
- candidate sources: `4455`
- conservative graph edges: `639435`
- made-source k per hotspot definition: `45`
- S/C made-source overlap: `42/45`
  (`0.933333`)

## S made sources

- matched controls: `45/45`
- unmatched: `0`
- exact opportunity-bin check: `True`

| Feature | Made median | Control median | Median paired Δ | Fraction made > control |
|---|---:|---:|---:|---:|
| `distinct_downstream_target_count` | 214 | 204 | -1 | 0.377778 |
| `source_max_outgoing_weight` | 1548 | 576.5 | 752 | 0.711111 |
| `source_mean_outgoing_weight` | 74.2477 | 49.9334 | 24.6414 | 0.844444 |
| `source_median_outgoing_weight` | 24.5 | 20.25 | 4.5 | 0.666667 |
| `source_out_edge_count` | 214 | 204 | -1 | 0.377778 |
| `source_out_strength` | 20333 | 10538 | 6023 | 0.866667 |
| `source_output_hhi` | 0.0255702 | 0.0174721 | 0.00452913 | 0.688889 |
| `source_target_diversity_ratio` | 1 | 1 | 0 | 0 |
| `source_top1_output_share` | 0.0814484 | 0.0752549 | 0.0164674 | 0.644444 |
| `source_top5_output_share` | 0.257555 | 0.203296 | 0.0438906 | 0.644444 |

## C made sources

- matched controls: `45/45`
- unmatched: `0`
- exact opportunity-bin check: `True`

| Feature | Made median | Control median | Median paired Δ | Fraction made > control |
|---|---:|---:|---:|---:|
| `distinct_downstream_target_count` | 214 | 204 | -2 | 0.355556 |
| `source_max_outgoing_weight` | 1169.5 | 575 | 707 | 0.755556 |
| `source_mean_outgoing_weight` | 82.2252 | 49.3646 | 29.8886 | 0.866667 |
| `source_median_outgoing_weight` | 24.5 | 20 | 6.25 | 0.688889 |
| `source_out_edge_count` | 214 | 204 | -2 | 0.355556 |
| `source_out_strength` | 20333 | 10214 | 6534.5 | 0.866667 |
| `source_output_hhi` | 0.0259272 | 0.0174721 | 0.00452913 | 0.711111 |
| `source_target_diversity_ratio` | 1 | 1 | 0 | 0 |
| `source_top1_output_share` | 0.0886656 | 0.073697 | 0.0239614 | 0.644444 |
| `source_top5_output_share` | 0.268932 | 0.203296 | 0.0496535 | 0.666667 |

## Supported interpretation

Within the frozen matched-central-brain model, the most recurrent
hotspot-producing sources are distinguished primarily by **heavier outgoing
operations**, not by simply having more opportunities.

After exact opportunity matching, made sources show substantially greater
aggregate outgoing strength and larger mean / maximum outgoing weights, while
outgoing edge count is comparatively similar.

The source-level matched comparison therefore sharpens the preceding SQ-03F.2
result: recurrent hotspot-producing sources are not merely present in more
candidate jobs. Their outgoing jobs are heavier.

The strong S/C made-source overlap shows that the recurrence phenotype is
largely shared across the two frozen hotspot definitions.

## Family Model

> **They weren't hanging around the Family. They are the Family.**

Operational translation:

> **Made sources don't get more jobs. Their jobs are heavier.**

## Claim boundary

This is a source-level graph association inside the frozen matched-central-brain
MoscaQuant model.

The top-1% made-source definition is a preregistered descriptive selection rule,
not a biological class boundary.

The analysis does not establish biological neuron classes, sex mechanisms,
living-fly behavior, population effects, or financial utility.

No p-value threshold or post-hoc significance threshold is introduced.

## Next question

The high overlap between S and C made sources motivates a downstream-territory
question:

> Among the shared made sources, do downstream targets converge into common
> territories or separate into distinct crews?

That question is not answered by SQ-03F.4.
