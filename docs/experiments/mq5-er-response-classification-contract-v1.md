# MQ-5.ER Response Classification Contract v1

**Status:** FROZEN BEFORE ANY MQ-5.ER NEURAL OUTCOME

## Purpose

This document freezes the neural interpretation rules for MQ-5.ER before any
alternative encoding is executed through the connectome.

The real-artifact encoding verifier passed with artifact SHA-256:

`15340cae365c291424f88ac3206e7ddc3f16885a52e89aece96d347bba741acb`

No neural runtime was used to choose these rules.

## Frozen baseline target set

MQ-5.ER evaluates the nine accepted MQ-3.2 responder targets only:

- 51
- 55
- 92
- 129
- 317
- 656
- 1273
- 126002
- 137122

The reference Arm-A onset vector is frozen as:

- 51: 149
- 55: 146
- 92: 145
- 129: 148
- 317: 147
- 656: 145
- 1273: 147
- 126002: 147
- 137122: 146

MQ-5.ER does not use post-hoc responder discovery.

It makes no classification claim about neurons outside this frozen target set.

## Frozen causal-expression intervention

The phrase `accepted causal-route expression` is operationalized as a replay of
the already frozen MQ-3.2 13-edge lesion bundle under each encoding.

For each encoding, run:

1. baseline with the original connectome;
2. the same encoding with the frozen 13-edge lesion bundle.

For every one of the nine accepted targets, causal expression is counted as
present only if the lesion produces either:

- a strictly later first-positive-voltage onset than that encoding's own
  baseline; or
- complete loss of the responder within the 192-frame episode.

An unchanged or earlier lesion onset does not satisfy the target-wise
causal-expression criterion.

The intervention bundle is considered expressed only when all nine frozen
targets satisfy that rule.

This is deliberately a test of the previously accepted 13-edge intervention
bundle. It is not a new per-edge causal screen and does not establish that every
individual edge remains independently necessary.

## Strict `RESPONSE PATTERN PRESERVED`

An encoding is classified:

`RESPONSE PATTERN PRESERVED`

only when all of the following are true:

1. all nine frozen responders are present;
2. the exact nine-target onset vector equals Arm A;
3. normalized positive-voltage fingerprint L2 distance relative to Arm A is
   `<= 1e-9`;
4. the frozen 13-edge intervention bundle is causally expressed by the
   target-wise criterion above.

No timing tolerance is allowed in this strict category.

The `1e-9` fingerprint threshold is a numerical equality tolerance, not a
biological or scientific-effect tolerance.

## `RESPONSE RETAINED WITH ALTERED EXPRESSION`

An encoding is classified:

`RESPONSE RETAINED WITH ALTERED EXPRESSION`

when:

1. all nine frozen responders are present;
2. the frozen 13-edge intervention bundle remains causally expressed for all
   nine targets;
3. at least one strict-preservation condition for onset or voltage fingerprint
   is not met.

Timing shifts and deterministic voltage-shape changes therefore remain visible
as altered expression rather than being hidden inside a permissive tolerance.

## `RESPONSE PATTERN NOT RETAINED`

An encoding is classified:

`RESPONSE PATTERN NOT RETAINED`

if either:

- any of the nine frozen responders is absent in the baseline encoding; or
- the frozen 13-edge intervention bundle fails the target-wise causal-expression
  criterion for any frozen target.

A failed arm is retained as evidence. It must not be repaired, replaced, or
retuned after inspection.

## Arm D family interpretation

Every one of the eleven non-identity Arm-D remaps is classified independently
using the rules above.

The family-level label is frozen as:

- `ASSET-TERRITORY ROBUST ACROSS TESTED REMAPS`
  - all 11 / 11 are `RESPONSE PATTERN PRESERVED`;
- `ASSET-TERRITORY RETAINED BUT ALTERED ACROSS TESTED REMAPS`
  - all 11 / 11 are either `PRESERVED` or `ALTERED`, but at least one is
    `ALTERED`;
- `MIXED ASSET-TERRITORY DEPENDENCE`
  - between 1 / 11 and 10 / 11 are at least retained;
- `ASSET-TERRITORY ASSIGNMENT DEPENDENCE SUPPORTED`
  - 0 / 11 are retained.

No remap may be dropped or replaced.

## Frozen stimulus provenance

The real-artifact verification established:

- normalized episode SHA-256:
  `0e813cad7c9fe7af487c0373cfaae81e6f691420686d2794be9766bdee836a46`
- Arm A stimulus SHA-256:
  `9c06a18293dd7dd27b1a1717785e2da25518d4b0081e5266794c3166a3f471e9`
- Arm B stimulus SHA-256:
  `50da7b3f749629ba96ed74e40ff065db9b6c9040f141cb452ec91412083a2ba0`
- Arm C stimulus SHA-256:
  `e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`
- Arm E stimulus SHA-256:
  `b6b3e67336d5a5e169cdbb20227a6119af93f26e149f270790d706133866fee2`

All primary arms used the same 3,241-neuron retinal support with SHA-256:

`7d9bdb9fd14c6c87bbe1a62ed65f30bc56657c1f17cf1b5b79d3e4092f61613e`

All 15 alternative determinism checks passed.

## Claim boundary

These classifications describe robustness of the accepted MoscaQuant response
within the frozen computational model and the tested encoding alternatives.

They do not establish:

- biological encoding independence;
- in-vivo Drosophila decision mechanisms;
- universal representation invariance;
- market prediction;
- trading usefulness;
- profitability.

Financial semantics remain:

**NOT ASSIGNED**
