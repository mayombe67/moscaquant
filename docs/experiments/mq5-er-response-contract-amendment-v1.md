# MQ-5.ER Response-Contract Amendment v1

**Status:** PRE-RESULT CLARIFICATION

This amendment is frozen before any MQ-5.ER alternative encoding is executed
through the neural runtime.

It resolves two ambiguities in the original protocol.

## Responder universe

The phrase `frozen responder universe` is narrowed to the nine accepted MQ-3.2
responder targets.

MQ-5.ER does not perform post-hoc responder discovery and does not classify
neurons outside those nine targets.

Therefore the earlier clause requiring that no previously absent neuron in an
undefined broader universe become present is superseded.

## Causal-route expression

The phrase `accepted causal-route expression` is operationalized as replay of
the frozen MQ-3.2 13-edge lesion bundle under each encoding.

The bundle is considered expressed only when every one of the nine accepted
targets has a strictly later lesion onset than its encoding-specific baseline,
or loses the response entirely within the 192-frame episode.

This is a bundle-level causal-expression test, not a new claim that all 13
edges are independently necessary under every encoding.

## Strict preservation

`RESPONSE PATTERN PRESERVED` now requires:

- all nine accepted responders present;
- exact Arm-A onset vector;
- normalized positive-voltage fingerprint L2 <= 1e-9;
- bundle-level causal expression across all nine targets.

No onset tolerance is used for the strict category.

Any deterministic onset or voltage-shape change that retains responder identity
and bundle-level causal expression is reported as:

`RESPONSE RETAINED WITH ALTERED EXPRESSION`

## Arm D family labels

The earlier three-way Arm-D family wording is superseded by the four-way family
classification in:

`docs/experiments/mq5-er-response-classification-contract-v1.md`

This prevents an all-retained-but-altered mapping family from being mislabeled
as complete assignment dependence.

No result-bearing MQ-5.ER neural execution occurred before this clarification.
