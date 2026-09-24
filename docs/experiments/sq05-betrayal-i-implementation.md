# SQ-05 — TWO BETRAYALS — BETRAYAL I Implementation

**Arm:** `BETRAYAL_I_LESIONED`

**Narrative:** THE FIRST BETRAYAL — presentation only

**Status:** IMPLEMENTATION FREEZE CANDIDATE — NO SQ-05 RESULT EXECUTION AUTHORIZED

## Decision

SQ-05 adopts the exact pre-existing MQ-3.2 first-onset causal-route lesion as
the implementation candidate for `BETRAYAL_I_LESIONED`.

The lesion artifact is:

`${MOSCAQUANT_DATA_ROOT}/processed/mq3-2-first-onset-causal-edges-v1.json`

SHA-256:

`23cc19a39c30e554671bdf92b904865311d2f7df4dd9ef82af1eaf66638c3a2b`

It contains exactly 13 edges spanning the nine accepted responder targets.

## Why inherit rather than invent

The lesion is not selected from SQ-05 outcomes. It predates SQ-05, is
content-addressed, was intervention-tested in MQ-3.2, and was later reused as
the deterministic Arm-D positive control in MQ-5.TS.

The SQ-05 implementation reuses the exact historical zero-edge operator rather
than defining a new lesion rule:

`brain.mq3_2_causal_intervention.zero_edges`

Operator source SHA-256:

`007aa507ac22b07811bff5ae8102a0916c88549aa3011fa22fa57c70598c6a87`

## Historical provenance caveat

The original MQ-3.2 edge set records `post_hoc = true`: it was selected from
activity-supported first-positive paths before the confirmatory intervention.

That history is preserved rather than rewritten.

For SQ-05, however, adoption of this already-fixed lesion is prospective: the
edge identities are frozen before SQ-05 stimulus, endpoint, or outcome
execution.

Accordingly, BETRAYAL I may be described as an **inherited validated
causal-route lesion**. It must not be described as a prospectively discovered
"hunger circuit", "danger circuit", fear circuit, or subjective-state lesion.

## Exact operation

Only the 13 frozen edge weights are set to zero on a copy of the baseline
connectome. The adapter verifies that exactly those 13 edge identities changed
and that every one is absent afterward.

No replacement lesion, route search, or result-dependent target selection is
allowed.

## Sham requirement

The future full SQ-05 protocol must include a scientific lesion sham/control,
even though it need not be one of the three headline Panopticon arms.

The existing MQ-3.2 deterministic sham rule is retained as the starting
control contract:

`same_presynaptic_neuron_nearest_positive_weight`

The exact SQ-05 sham edges are **not** frozen by this implementation gate.
They must be derived and frozen before any SQ-05 result-bearing execution.

## Still unresolved

This implementation does not yet freeze:

- the fruit-associated stimulus;
- the looming/threat-associated stimulus;
- their timing;
- SQ-05 neural endpoints or classification;
- exact sham-edge identities;
- BETRAYAL II fresh seed(s);
- trial count or public showcase-trial selection.

## Execution boundary

`brain/sq05_betrayal_i.py` has no CLI and no result writer.

This gate authorizes no neural execution and no SQ-05 result construction.

## TWO BETRAYALS

The First Betrayal's knife was already in evidence locker MQ-3.2.

We are inheriting that exact knife, not sharpening a new one after seeing
SQ-05 outcomes.

The Index is still not inserted.
