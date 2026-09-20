# SQ-03D.1 — DOUBLE CHECK THE KNIFE — Results

**Status:** COMPLETE — PREREGISTERED VERIFICATION FAILED  
**Classification:** Authoritative scalar verification result  
**Source commit:** `2bf6ecca9793f885c914bbaaa37c374b2282a127`  
**Artifact SHA-256:** `5f52a162f5161efcc548dc52ccf6c82eb55e6cefb6f310b87656e1dad5f0214d`

## Preregistered result

SQ-03D.1 did **not** satisfy its frozen all-pair acceptance criterion.

- frozen pairs: **32**
- upper-tail pairs: **16**
- low-tail controls: **16**
- exact A/A replay: **PASS**
- primitive subject metrics agreeing with SQ-03B: **64/64**
- all reconstructed pair metrics agreeing with SQ-03D: **FAIL**
- formally verified pairs under the frozen all-metric rule:
  **1/32**
- upper-tail formally verified: **1/16**
- low-tail formally verified: **0/16**

The frozen verification criterion is preserved as written. It is not relaxed
after seeing the result.

## Failure localization

The failure was isolated to the normalized-asymmetry ratio.

| Pair metric | Failures |
| --- | ---: |
| Integrated context residual `C` | 0/32 |
| Integrated total effect magnitude `S` | 0/32 |
| Integrated normalized asymmetry `A` | 31/32 |
| Peak context residual `C` | 0/32 |
| Peak total effect magnitude `S` | 0/32 |
| Peak normalized asymmetry `A` | 30/32 |

All **64/64 primitive subject-level scalar counterfactual metrics** remained
within the already-frozen SQ-03B/SQ-03C numerical agreement contract.

All **32/32 pairs** reproduced the SQ-03D primary integrated context residual
and total-effect magnitude within that same contract.

All **32/32 pairs** also reproduced the peak context residual and peak
total-effect magnitude.

The normalized ratio was numerically unstable because it divides by
`|ΔM| + |ΔL|`. This is especially severe in low-tail controls, where both
primitive effects are near floating-point scale: tiny accepted changes in the
numerator or denominator can produce large changes in the ratio.

The upper tail shows the same phenomenon at much smaller amplitude: raw `C`
and `S` reproduce while ratio differences can exceed the frozen direct
`np.isclose` criterion.

## Scientific interpretation

SQ-03D.1 is a **formal verification failure under its preregistered all-metric
acceptance rule**.

At the same time, the diagnostic result is highly informative:

1. the scalar neural reruns reproduced all primitive SQ-03B effects;
2. the SQ-03D primary quantity, raw context residual `C`, reproduced for every
   selected pair;
3. total effect magnitude `S` reproduced for every selected pair;
4. the failure is confined to normalized asymmetry `A`, a derived ratio that is
   ill-conditioned near zero.

Therefore the experiment does **not** justify calling SQ-03D.1 a pass, but it
does support the narrower model-level statement that the selected SQ-03D raw
context-residual effects survived independent scalar execution.

Normalized asymmetry should remain descriptive and should not be used as a
future acceptance gate without a separately frozen numerical-stability model.

## Claim boundary

SQ-03D.1 can verify that selected SQ-03D context-dependent hotspots survive an independent scalar execution path. It does not establish a biological sex mechanism, population-level statistical significance, organism-level behavior, intelligence differences, or financial utility.
