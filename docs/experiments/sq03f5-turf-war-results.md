# SQ-03F.5 — TURF WAR — Results

**Status:** COMPLETE

**Authoritative result:** `artifacts/sidequests/sq03f5-turf-war-result-v1.json`

**Provenance sidecar:** `artifacts/sidequests/sq03f5-turf-war-provenance-v1.json`

## Result

SQ-03F.5 tested whether the 42 shared made sources inherited from SQ-03F.4 converge downstream into common neural territory more strongly than expected under the frozen matched-source null.

- Eligible shared sources: **42**
- Candidate-source universe: **4455**
- Candidate edges: **114825**
- Conservative graph edges: **639435**
- Territory rule: **2 downstream hops**
- Primary statistic: **mean pairwise Jaccard overlap**
- Observed mean pairwise Jaccard: **0.5621987198049191**
- Matched-null median: **0.4052166225170337**
- Effect ratio vs null median: **1.387402906407884** (38.74% above null median)
- Randomizations: **10,000**
- Base seed: **314159**
- Empirical upper-tail p: **9.999000099990002e-05**
- Empirical lower-tail p: **1**
- Frozen classification: **`GREATER_THAN_NULL_DOWNSTREAM_CONVERGENCE`**

The empirical upper-tail p-value equals the add-one floor for 10,000 randomizations (`1 / 10001`), meaning zero randomized draws reached or exceeded the observed overlap statistic.

## Interpretation

Under the frozen SQ-03F.5 rules, the shared SQ-03F.4 sources show **greater-than-null downstream convergence**.

This is evidence about organization inside the frozen MoscaQuant model and the frozen SQ-03F source set. It does **not** establish biological gang-like organization, organism-level anatomical territory, sex-specific organization, financial usefulness, or trading usefulness.

## Provenance note

The authoritative result artifact was produced once and was not regenerated after its classification was observed. The provenance sidecar binds that original artifact to the execution commit, frozen config, analyzer, protocol, parent SQ-03F.4 artifact, and aligned-edge input by SHA-256.
