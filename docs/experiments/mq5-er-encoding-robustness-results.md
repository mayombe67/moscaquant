# MQ-5.ER — Encoding Robustness Results

**Experiment:** `mq5-er-encoding-robustness-v1`

**Status:** COMPLETE — FROZEN RESULT

**Financial semantics:** NOT ASSIGNED

## Result artifact

`~/moscaquant-data/experiments/mq5-er-encoding-robustness-v1.json`

SHA-256:

`737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39`

## Frozen classifications

- **Arm A — frozen encoder:** `RESPONSE PATTERN PRESERVED`
- **Arm B — fixed temporal cadence:** `RESPONSE RETAINED WITH ALTERED EXPRESSION`
- **Arm C — zero entropy-dependent temporal jitter:** `RESPONSE PATTERN NOT RETAINED`
- **Arm D — balanced asset/ticker-to-retinal-territory remap family:** `ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS`
- **Arm E — no momentum-dependent temporal motion:** `RESPONSE RETAINED WITH ALTERED EXPRESSION`

All eleven non-identity Arm D confirmatory mappings individually satisfied
`RESPONSE PATTERN PRESERVED`.

## Arm B

All nine frozen responder targets remained present. The frozen 13-edge lesion
bundle remained causally expressed across all nine targets.

However, Arm B did not preserve the exact Arm-A onset vector or normalized
positive-voltage fingerprint.

Fingerprint diagnostics versus Arm A:

- normalized L2: `0.46395110314356997`
- cosine similarity: `0.9232567460841561`
- maximum absolute voltage difference: `0.0018528567161411047`

Interpretation: replacing volatility-dependent cadence with the preregistered
fixed cadence materially altered response expression while preserving the
accepted bundle-level causal dependency.

## Arm C

All nine frozen responder targets remained present, so the failure was not
caused by simple disappearance of the accepted responder set.

The Arm-C baseline first-positive onsets were:

- `51: 148`
- `55: 145`
- `92: 141`
- `129: 148`
- `317: 153`
- `656: 141`
- `1273: 144`
- `126002: 151`
- `137122: 151`

The frozen 13-edge lesion bundle failed the causal-expression criterion for
five targets:

- `55`: baseline `145`, lesion `145`
- `92`: baseline `141`, lesion `141`
- `656`: baseline `141`, lesion `141`
- `126002`: baseline `151`, lesion `151`
- `137122`: baseline `151`, lesion `151`

It remained causally expressed for `51`, `129`, `317`, and `1273`.

Fingerprint diagnostics versus Arm A:

- normalized L2: `0.23144747739534738`
- cosine similarity: `0.977749408591247`
- maximum absolute voltage difference: `0.001375941006699577`

Arm C therefore failed the frozen retention criterion because the accepted
bundle-level causal dependency changed, not because the nine responders
vanished.

A key retrospective lesson is:

> Same responders does not mean same mechanism.

Arm C's voltage fingerprint was closer to Arm A than Arm B's under normalized
L2, while Arm C failed causal retention and Arm B did not. Response-shape
similarity therefore did not guarantee preservation of the accepted causal
mechanism.

## Arm D

All eleven non-identity balanced asset/ticker-to-retinal-territory mappings
were individually classified `RESPONSE PATTERN PRESERVED`.

Frozen family classification:

`ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS`

Within the tested balanced remap family, the accepted response did not depend
on the original asset-to-retinal-territory assignment.

This result is limited to the tested remap family and does not establish
general spatial-encoding independence.

## Arm E

All nine frozen responder targets remained present. The exact Arm-A onset
vector remained intact. The frozen 13-edge lesion bundle remained causally
expressed across all nine targets.

The normalized positive-voltage fingerprint changed:

- normalized L2: `0.052037829631433274`
- cosine similarity: `0.9990322823844667`
- maximum absolute voltage difference: `0.00027526689518708736`

Interpretation: removing momentum-dependent temporal motion altered response
expression without changing the accepted onset timing or bundle-level causal
dependency.

## Scientific interpretation

MQ-5.ER supports robustness of the accepted MoscaQuant response to several
reasonable encoding changes while directly demonstrating dependence on at
least one tested representation choice.

Specifically:

- balanced asset-to-retinal-territory assignment was highly robust across the
  tested confirmatory family;
- volatility-dependent cadence materially shaped response timing and voltage
  expression without removing the frozen causal dependency;
- momentum-dependent temporal motion modestly shaped the voltage fingerprint
  without changing accepted onset timing or causal dependency;
- entropy-dependent temporal irregularity was mechanistically consequential:
  removing that jitter changed dependence on the frozen 13-edge lesion bundle
  for five of nine accepted responder targets.

## Claim boundaries

MQ-5.ER does **not** establish that the network "understands entropy."

It does **not** identify which alternative routes support the five Arm-C
responders whose frozen lesion sensitivity disappeared.

It does **not** prove general sensory-encoding independence.

It does **not** test sensory-gain robustness.

It does **not** establish biological causality in a living fly.

It does **not** assign financial meaning, market-prediction ability, trading
utility, or profitability.
