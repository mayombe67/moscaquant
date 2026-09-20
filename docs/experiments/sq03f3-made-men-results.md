# SQ-03F.3 — MADE MEN — Results

**Status:** COMPLETE  
**Authoritative artifact:** `artifacts/sidequests/sq03f3-made-men-result-v1.json`  
**Artifact SHA256:** `4a6d47be04d8ac31e5994e5ff83f3d8722840e41ebf104e03dc982e7399f0788`

## Design

SQ-03F.3 reused the exact frozen S and C hotspot memberships and compared their
source recurrence against 10,000 stratified hotspot-label randomizations.

The null preserved hotspot count inside exact strata of:

- context count;
- total-weight decile;
- absolute-weight-difference decile.

Source identities and candidate context memberships remained fixed.

## S hotspots

- unique_hotspot_source_count: observed `314`; null median `463.0`; 5–95% `446.0`–`481.0`; descriptive null percentile `0.0`
- fraction_hotspot_edges_repeated_source: observed `0.804177545691906`; null median `0.7606614447345518`; 5–95% `0.741514360313316`–`0.7798085291557877`; descriptive null percentile `1.0`
- max_hotspot_edges_one_source: observed `140`; null median `24.0`; 5–95% `20.0`–`31.0`; descriptive null percentile `1.0`
- source_count_hhi: observed `0.02901452127365454`; null median `0.005505979771262104`; 5–95% `0.005128688737548297`–`0.005946821733963236`; descriptive null percentile `1.0`
- top1_source_share: observed `0.12184508268059181`; null median `0.020887728459530026`; 5–95% `0.017406440382941687`–`0.026979982593559618`; descriptive null percentile `1.0`
- top5_source_share: observed `0.2950391644908616`; null median `0.0835509138381201`; 5–95% `0.07484769364664925`–`0.09399477806788512`; descriptive null percentile `1.0`

## C hotspots

- unique_hotspot_source_count: observed `290`; null median `455.0`; 5–95% `438.0`–`473.0`; descriptive null percentile `0.0`
- fraction_hotspot_edges_repeated_source: observed `0.824194952132289`; null median `0.7667536988685814`; 5–95% `0.7484769364664926`–`0.7850739773716269`; descriptive null percentile `1.0`
- max_hotspot_edges_one_source: observed `135`; null median `25.0`; 5–95% `20.0`–`32.0`; descriptive null percentile `1.0`
- source_count_hhi: observed `0.028104053852405813`; null median `0.00563929280465626`; 5–95% `0.005240792879266111`–`0.0060816496881914185`; descriptive null percentile `1.0`
- top1_source_share: observed `0.1174934725848564`; null median `0.02175805047867711`; 5–95% `0.017406440382941687`–`0.0278503046127067`; descriptive null percentile `1.0`
- top5_source_share: observed `0.2863359442993908`; null median `0.08529155787641426`; 5–95% `0.07571801566579635`–`0.09573542210617927`; descriptive null percentile `1.0`

## Supported interpretation

Within the frozen matched-central-brain model, hotspot edges are substantially
more concentrated into a limited set of recurring source neurons than the
stratified edge-opportunity reference.

Observed hotspot sets occupy fewer sources, have larger repeated-source
fractions, much larger maximum per-source hotspot counts, and much larger
source-count concentration than the randomization reference.

The result is descriptive/model-internal. The randomization percentile is not
a biological population probability and no p-value threshold is introduced.

## Context-signature qualification

The number of hotspot sources represented in at least two input-anchor context
signatures is lower than the null because observed hotspot edges are compressed
into fewer source neurons overall.

The maximum distinct context-signature count is saturated at 12 in both
observed and null samples and is not discriminative here.

## Family Model

> **The same capos keep showing up in the books, and opportunity alone does not
> explain it.**

## Next question

SQ-03F.4 — THE SIT-DOWN moves the unit of analysis to the source neuron:

> What graph properties distinguish the most recurrent hotspot-producing
> sources from sources with comparable opportunity?

## Randomization implementation note

The frozen protocol specified base seed `314159` and independent S/C
randomization but did not explicitly define stream derivation. The executed
analyzer used S seed `314159` and C seed `314160` (`base_seed + 1`), as
recorded in the authoritative artifact.

See
[`sq03f3-randomization-stream-clarification.md`](sq03f3-randomization-stream-clarification.md)
for the protocol-integrity classification and future rule.

