# MQ-5.ER.2 — THE RACKET matched-control selection rule

**Status:** FROZEN RULE — CONTROL NOT YET SELECTED
**Result-bearing RACKET execution:** disabled

## Purpose

THE RACKET requires one topology-matched non-candidate control edge before
authoritative execution.

The control is selected using only frozen connectome structure plus the already
completed MQ-5.ER.1 DETOUR discovery artifact. No THE RACKET neural outcome may
be generated or inspected during control selection.

## Focused edge

`116680 -> 12024`

## Structural matching universe

The control must:

1. exist in the frozen connectome;
2. have the same transmitter/sign direction as the focused edge;
3. have the exact same backward-hop signature across targets
   `92, 656, 137122, 1273`;
4. be absent from every MQ-5.ER.1 DETOUR top-five candidate list;
5. not equal the focused edge.

The frozen focused-edge signature is required to be:

`(3, 3, 3, 3)`

for targets:

`(92, 656, 137122, 1273)`

## Deterministic ranking

Among eligible edges, choose lexicographically by:

1. minimum absolute difference in `log10(abs(weight))`;
2. minimum absolute difference in `log1p(presynaptic outdegree)`;
3. minimum absolute difference in `log1p(postsynaptic indegree)`;
4. lower postsynaptic neuron ID;
5. lower presynaptic neuron ID.

No neural activity, onset, voltage, responder fingerprint, RACKET arm, or
RACKET result may enter this ranking.

## Output

The selector emits one structural-control record containing:

- focused edge;
- selected control edge;
- hop signature;
- edge weights;
- structural degrees;
- matching distances;
- exclusion policy;
- deterministic tie-break.

The emitted control must then be written into THE RACKET config and committed
in a separate freeze commit before result execution can be enabled.

## Claim boundary

This control improves the specificity of the intervention comparison. It does
not make the control edge biologically equivalent to the focused edge and does
not authorize any causal conclusion before THE RACKET executes.

## Lore

Before the sit-down, we find another guy with the same neighborhood, similar
connections, and similar weight on the books — except DETOUR never named him.

No outcomes. No wiretap. Just the org chart.
