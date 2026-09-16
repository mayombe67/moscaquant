# MQ-3.2 — Physiology-Constrained Visual Propagation

## Status

**COMPLETE**

## Purpose

Test whether a narrowly physiology-constrained graded-transmission rule can
restore propagation from the frozen visual system to the frozen descending
readout without contaminating neutral conditions.

This experiment follows the rejection of MQ-3.1 global positive-subthreshold
propagation.

No financial semantics are used.

---

## Background

Under the original spike-only MQ-3 runtime:

- retinal activity was produced;
- MQ-2.1 visual relay activity was produced;
- relay current reached intermediate neurons;
- intermediate neurons remained below the point-LIF spike threshold;
- assigned descending neurons received no modeled activity;
- both market Conditions A and B therefore produced `ABSTAIN`.

A global MQ-3.1 rule allowing positive subthreshold voltage to propagate from
all non-retinal neurons restored activity but also activated the descending
population during neutral input.

MQ-3.1 was therefore rejected at its precommitted neutral-contamination gate.

---

## Bridge-neuron census

The previously identified relay-to-DN bridge population contained 25 neurons.

All 25 were annotated:

`superclass = ol_intrinsic`

Type distribution:

| Type | Count |
|---|---:|
| Tm4 | 11 |
| Tm3 | 4 |
| Dm17 | 3 |
| Dm19 | 3 |
| MeLo2 | 1 |
| TmY3 | 1 |
| Tm2 | 1 |
| T2 | 1 |

The bridge census motivated a visual-circuit-specific physiology hypothesis.

Bridge membership itself was **not** used to select individual neurons for the
new propagation rule.

---

## Precommitted graded types

The MQ-3.2 rule was restricted to annotation-defined:

- Tm2
- Tm3
- Tm4

The rule applies globally to every represented neuron of those types in the
frozen 166,700-neuron model.

It was not restricted to neurons known to lie on the Condition-A path.

### Frozen population

| Type | Count |
|---|---:|
| Tm2 | 1,766 |
| Tm3 | 2,054 |
| Tm4 | 1,670 |
| **Total** | **5,490** |

Artifact:

`/home/wil/moscaquant-data/processed/mq3-2-graded-visual-types-v1.npz`

SHA-256:

`1c514bf58bf69b24bfba28489344d0fe3e0f7590d649e0ef446c33898d38e379`

Provenance:

`/home/wil/moscaquant-data/processed/mq3-2-graded-visual-types-v1.json`

SHA-256:

`c73bbbf385fef62740c05b9cdd3763cdeb53946862a8211708133e30d44c7c1f`

Selection properties:

- market response used: NO
- bridge membership used: NO
- financial semantics used: NO
- P/L used: NO

---

## MQ-3.2 propagation rule

The frozen MQ-2.1 R1-R6 mechanism remains unchanged.

For Tm2, Tm3, and Tm4 only:

```text
graded_activity =
    clip(positive_voltage / threshold, 0, 1)

effective_activity =
    max(spike, graded_activity)
