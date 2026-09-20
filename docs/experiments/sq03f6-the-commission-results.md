# SQ-03F.6 — THE COMMISSION — Results

**Status:** COMPLETE

**Authoritative result:** `artifacts/sidequests/sq03f6-the-commission-result-v1.json`

**Provenance sidecar:** `artifacts/sidequests/sq03f6-the-commission-provenance-v1.json`

## Result

SQ-03F.6 tested whether the downstream convergence established by SQ-03F.5
is unusually concentrated among a relatively small set of downstream targets.

- Eligible sources: **42**
- Candidate-source universe: **4455**
- Candidate edges: **114825**
- Conservative graph edges: **639435**
- Primary statistic: **participation-mass HHI**
- Observed HHI: **0.0002087914357059647**
- Matched-null median HHI: **0.0001640372384629388**
- Effect ratio vs null median: **1.272829496901932** (27.28% above null median)
- Randomizations: **10,000**
- Base seed: **314159**
- Empirical upper-tail p: **9.999000099990002e-05**
- Empirical lower-tail p: **1**
- Frozen classification: **`GREATER_THAN_NULL_TARGET_CONCENTRATION`**

The empirical upper-tail p-value equals the add-one floor for 10,000 randomizations (`1 / 10001`), meaning zero randomized draws reached or exceeded the observed concentration statistic.

## Descriptive participation structure

- Unique downstream targets: **7475**
- Total participation mass: **144882**
- Maximum participation count for a single target: **42**
- Targets reached by all 42 sources: **306**
- Targets reached by at least half of the sources: **3317**
- Top-1 participation share: **0.0002898910837785232**
- Top-5 participation share: **0.001449455418892616**
- Top-10 participation share: **0.002898910837785232**

These quantities are descriptive. The frozen classification is based on the participation-mass HHI and its matched-source null.

## Interpretation

Under the frozen SQ-03F.6 rules, the downstream participation structure shows
**greater-than-null target concentration**.

Combined with SQ-03F.5, the narrow model-level interpretation is:

1. the 42 shared sources converge downstream more strongly than expected; and
2. that downstream participation is itself more concentrated among targets than expected under the inherited matched-source null.

This does **not** establish literal biological command hierarchy, anatomical governing bodies or "commissions", organism-level functional modules, sex-specific neural organization, consciousness, agency, intent, coordination, financial usefulness, or trading usefulness.

## Provenance note

The authoritative result artifact was produced once and was not regenerated after its classification was observed. The provenance sidecar was added afterward to bind that original artifact to the execution commit, frozen config, analyzer, protocol, and SQ-03F.5 parent artifacts by SHA-256.
