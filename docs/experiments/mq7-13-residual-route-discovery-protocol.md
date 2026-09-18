# MQ-7.13 Residual Route Discovery Protocol

## Research question

What short structural routes from neuron 68045 toward the DN-C1 readout
population could plausibly carry the residual perturbation-dependent SC-03
effect not mediated by:

68045 -> 1273

## Background

MQ-7.12 found:

- intact DN-C1 plasticity-expression magnitude:
  1.1174368270910759e-08
- after functional ablation of 68045 -> 1273:
  7.3405055408023634e-09
- attenuation:
  34.309435998174054%

Therefore the validated downstream edge carries a substantial but incomplete
fraction of the measured effect.

The residual route structure is not yet known.

## Analysis type

Structural discovery only.

No neural edge is modified.

No lesion is performed.

## Source node

68045

## Destination population

All model indices belonging to anonymous readout population DN-C1.

## Candidate routes

Enumerate simple directed paths of:

- 1 edge
- 2 edges
- 3 edges

from neuron 68045 to any DN-C1 model index.

A simple path may not repeat a node.

## Known route exclusion

Residual-route ranking excludes paths containing neuron 1273.

The known route through 1273 is reported separately.

## Structural path score

For a path with edge weights:

w1, w2, ..., wn

define:

path_strength = abs(w1 * w2 * ... * wn)

This is a structural ranking heuristic only.

It is not interpreted as measured causal contribution or biological signal
strength.

## Ranking

Residual routes are ranked by:

1. descending path_strength;
2. shorter path length;
3. lexicographic model-index path.

Freeze the top 25 residual routes.

## Additional output

Report:

- number of DN-C1 destination neurons;
- total candidate routes found;
- known 68045 -> 1273 weight;
- top 25 residual routes;
- repeated intermediate nodes among the top routes;
- candidate intermediate nodes ranked by frequency and summed path strength.

## Interpretation

MQ-7.13 generates preregistered candidates for causal testing.

Structural ranking alone does not prove that a route carries the observed
neural effect.

No route may be called causal until experimentally ablated.

## Claims excluded

This analysis does not establish:

- causal mediation;
- actual neural activity propagation;
- biological learning in a living organism;
- financial utility;
- subjective state;
- exclusivity of any route.
