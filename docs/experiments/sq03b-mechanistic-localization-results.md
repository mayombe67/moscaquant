# SQ-03B — FIND THE DIFFERENCE — Results

**Status:** COMPLETE  
**Classification:** Authoritative model-level localization result  
**Source commit:** `d33487934833fc9d252216f814a258c038d19763`  
**Final artifact SHA-256:** `0bcfbeef18ba43e4a3371cae13f1d05a04fc63fc988084e9bf45a33f6a00a2f8`  
**Checkpoint ledger SHA-256:** `7b2632de5792973534177b697efdd7c3af0b82a836d9d2b597812dbc0dd1f725`

## Execution integrity

SQ-03B completed **469,860** frozen input/edge/subject counterfactual jobs.

- candidate edges: **114,825**
- frozen inputs: **4**
- frozen anchors: **3**
- deterministic A/A replay: **PASS**
- first-positive-frame changes: **0**

The run preserved the frozen single-edge equalization design. Each counterfactual
changed one aligned edge weight at a time and left the remaining subject graph,
runtime parameters, and stimulus parameters unchanged.

## Effect-magnitude distribution

The production runner's `model_level_effect_observed` field used an exact
non-zero floating-point comparison. Because the validated batched engine is
known to differ from scalar execution by tiny floating-point roundoff, the
reported `469,859` exact-nonzero rows are **not**
interpreted as that many meaningful causal/localization effects.

Descriptively:

- median absolute peak-voltage delta: `8.73114913702e-11`
- p99 absolute peak-voltage delta: `2.38651409745e-09`
- maximum absolute peak-voltage delta: `0.000555032660486`
- median absolute integrated-positive-voltage delta: `3.25962901115e-09`
- p99 absolute integrated-positive-voltage delta: `5.07570803165e-08`
- maximum absolute integrated-positive-voltage delta: `0.0202821558341`

Rows exceeding descriptive tolerances in any relevant anchor metric:

| Descriptive tolerance | Rows | Share |
| --- | ---: | ---: |
| `>1e-10` | 468,813 | 99.7772% |
| `>1e-09` | 438,004 | 93.2201% |
| `>1e-08` | 173,066 | 36.8335% |
| `>1e-07` | 4,533 | 0.9648% |
| `>1e-06` | 1,397 | 0.2973% |
| `>1e-05` | 387 | 0.0824% |
| `>0.0001` | 70 | 0.0149% |

These tolerances are **descriptive only**. They were examined after SQ-03B
completed and therefore are not preregistered significance thresholds.

## Per input / subject maxima

| Input | Subject | Jobs | Max abs peak delta | Max abs integrated delta |
| --- | --- | ---: | ---: | ---: |
| `AVLP234` | LILITH | 44,839 | 0.000316987385304 | 0.0142249667551 |
| `AVLP234` | MORTY | 44,839 | 0.000316408561048 | 0.0142353321426 |
| `AVLP435` | LILITH | 70,808 | 0.00029358048414 | 0.0131770505104 |
| `AVLP435` | MORTY | 70,808 | 0.000292421580525 | 0.0131783564575 |
| `LPLC2` | LILITH | 79,972 | 0.000224799106945 | 0.0123187894933 |
| `LPLC2` | MORTY | 79,972 | 0.000555032660486 | 0.0202821558341 |
| `TmY14` | LILITH | 39,311 | 0.000118359486805 | 0.00536159751937 |
| `TmY14` | MORTY | 39,311 | 0.000117920688353 | 0.00533251650631 |

The largest observed peak and integrated effects occurred in the upper tail of
the localization distribution. The full distribution is strongly long-tailed:
most single-edge substitutions produced extremely small magnitude changes,
while a small subset produced effects orders of magnitude larger than the
known scalar-vs-batched numerical discrepancy.

## Interpretation

SQ-03B supports a **model-level long-tailed sensitivity landscape** inside the
frozen matched-central-brain comparison.

It does **not** establish:

- a formal statistical-significance threshold for individual edges;
- a biological mechanism in living flies;
- general behavioral or intelligence differences;
- sex superiority;
- market skill, profitability, or financial usefulness.

No post-hoc tolerance above is promoted to a significance cutoff.

A separately frozen verification experiment is required before strong
individual-edge localization claims are made from the upper tail.

## Claim boundary

SQ-03B localizes sensitivity within the frozen matched-central-brain computational model by single-edge counterfactual equalization. Reported effects are model-level sensitivities and do not establish biological mechanism, general sex differences, behavior, intelligence, market skill, profitability, or financial usefulness.
