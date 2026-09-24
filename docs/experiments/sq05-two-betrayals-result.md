# SQ-05 — TWO BETRAYALS — Result

## Status

`COMPLETE_PREREGISTERED_RESULT`

Authoritative execution completed all **52 / 52** frozen episodes in local/Habitat
mode. The independent post-run verifier passed without neural re-execution,
topology reconstruction, result mutation, commit, or push.

The authoritative manifest SHA-256 is:

`72bbef6b8cd996f81a371938af9fd3f024ef381bce8cf458c378dc55b05646b1`

The authoritative dense NPZ sidecar SHA-256 is:

`b3fbe9f28d07aa5d8dfe707eed99e4b7b48b28364e1afc37875e8442fbeb7a8e`

The execution log is byte-identical to the JSON result manifest and has the
same SHA-256:

`72bbef6b8cd996f81a371938af9fd3f024ef381bce8cf458c378dc55b05646b1`

## Frozen scientific outcomes

SQ-05 reports three separate outcomes. There is no combined winner.

### Cue transition

`BOTH_LAYOUTS_RESPOND_TO_CUE_B`

The fixed INTACT replicate-1 DN-C summary responded to Cue B in both LR and RL
under the preregistered `1e-12` block-delta rule.

This is a modeled DN response to the frozen visual sequence. It is not a claim
of fruit recognition, hunger, danger perception, threat perception, fear, or
behavior.

### BETRAYAL I — inherited causal-route lesion versus matched sham

`LESION_EFFECT_EXCEEDS_SHAM_BOTH_LAYOUTS`

- LR lesion-to-INTACT distance: `3.8240768866345015e-05`
- LR sham-to-INTACT distance: `0.0`
- RL lesion-to-INTACT distance: `0.1276743202466753`
- RL sham-to-INTACT distance: `0.0`

The preregistered `lesion distance > sham distance` criterion is satisfied in
both layouts.

Important magnitude note: the effect is **not similar in size across layouts**.
The LR lesion distance is small while the RL lesion distance is much larger.
The preregistered classification records direction relative to sham separately
for each layout; it does not assert layout-invariant effect magnitude.

This is an in-model response difference relative to the frozen matched sham.
It is not a biological causal claim.

### BETRAYAL II — strict matched topology null

`STRICT_NULL_RARELY_REPRODUCES_INTACT_RESPONSE`

All **20 / 20** preregistered seeds completed. There were **0 failed seeds** and
**0 / 20** exact INTACT-response reproductions across both LR and RL.

Within this frozen model and the tested preregistered null block, preserving
the strict null's protected and matched structural constraints was not
sufficient to exactly reproduce the INTACT DN response.

That statement is deliberately bounded: zero of these 20 frozen nulls
reproduced INTACT. It does not claim that no possible shuffled topology can do
so, and the frozen protocol attaches no population-level significance claim to
the count band.

## Determinism and verification

Independent verification confirmed:

- 52 / 52 sidecar episodes in the frozen order;
- 6 / 6 deterministic duplicate pairs exactly equal;
- all BETRAYAL-II topology invariants passed;
- Cue Transition recomputed from the dense sidecar;
- BETRAYAL I distances and classification recomputed from the dense sidecar;
- all 20 BETRAYAL-II exact-reproduction decisions recomputed from the dense
  sidecar;
- JSON and execution log are byte-identical;
- NPZ hash matches the manifest.

Independent verifier SHA-256:

`5d4701202dcf55f6677f1431b67a2ea25c53939db0170f3f0bc09df81bb74d13`

## Provenance

Execution authorization commit:

`1184680ee21cd9a4c97b405262a90500ed4fedb0`

Runner implementation commit:

`1472ebf7e3cde6c1f0c98f0462446640710027b7`

Runner SHA-256:

`06f640dd6c829d917bb537298f8e54048066455b92f6932dc09fe5abdef4867e`

Runner configuration SHA-256:

`ca9570a5b912bb320c8d9287eea0878578fede2c51ebcdebf32eed9afd28f3cb`

Result schema SHA-256:

`bf1069e457eff0e828e890d74ae1b5831e2204e2bc070edd2fe5732311acd33f`

Execution authorization SHA-256:

`a25cc8731298d91be5b1be7fd634a206070e94b6bf3d55300bc0b6723d43e0c9`

Core preregistration SHA-256:

`871f1216fe8a6160c937615b9d48a881209201aeb102a6993cf2e54bf37b5196`

## Result storage

The dense result artifacts remain outside Git under
`${MOSCAQUANT_DATA_ROOT}/experiments/` and are bound by SHA-256 in the result
seal. The seal does not copy or rewrite the scientific result.

## Claim boundary

SQ-05 establishes only the frozen modeled-network outcomes above.

It does not establish fruit recognition, hunger, danger or threat perception,
fear, behavior, biological causality, population-level statistical
significance, market prediction, or financial value.

## THE MAW

The result exists.

Now we preserve the evidence without changing the story it tells.
