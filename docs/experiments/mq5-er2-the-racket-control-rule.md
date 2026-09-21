# MQ-5.ER.2 — THE RACKET matched-control selection rule

**Status:** V2 FROZEN RULE — CONTROL NOT YET SELECTED
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

## V1 engineering finding and pre-outcome correction

The first frozen selector rule ranked absolute weight distance before degree
similarity. Its first selected edge was `3671 -> 27236`.

That edge matched the focused edge almost exactly in weight but had a
presynaptic outdegree of `282` versus `4` for the focused edge, and a
postsynaptic indegree of `104` versus `33`.

No THE RACKET neural outcome had been generated or inspected.

The V1 selected edge was therefore rejected as an insufficiently balanced
topology match, and the selector objective was corrected prospectively before
confirmatory execution.

## Deterministic V2 ranking

For every eligible edge, compute three log-scale structural distances:

- absolute difference in `log10(abs(weight))`;
- absolute difference in `log1p(presynaptic outdegree)`;
- absolute difference in `log1p(postsynaptic indegree)`.

Choose lexicographically by:

1. minimum **maximum** of the three log-scale distances;
2. minimum **sum** of the three log-scale distances;
3. minimum absolute-weight distance;
4. minimum presynaptic-outdegree distance;
5. minimum postsynaptic-indegree distance;
6. lower postsynaptic neuron ID;
7. lower presynaptic neuron ID.

This prevents an almost-perfect match on one covariate from dominating an
extreme mismatch on another.

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

## Frozen selected control

The V2 selector deterministically selected:

`78481 -> 16087`

Structural comparison against focused edge `116680 -> 12024`:

- hop signature: `(3, 3, 3, 3)` for both;
- sign: inhibitory / negative for both;
- presynaptic outdegree: `4` versus `4`;
- postsynaptic indegree: `37` versus `33`;
- control weight: `-0.10757946223020554`;
- focused weight: `-0.13293051719665527`.

Frozen V2 matching distances:

- `log10(abs(weight))`: `0.09189532548319435`;
- `log1p(pre outdegree)`: `0.0`;
- `log1p(post indegree)`: `0.1112256351102241`;
- maximum distance: `0.1112256351102241`;
- summed distance: `0.20312096059341844`.

No THE RACKET confirmatory outcome was generated or inspected during selection.

The earlier V1 candidate `3671 -> 27236` remains rejected and must not be used
as the authoritative matched control.

### Lore

The lineup finally has a civilian.

Same neighborhood. Same number of outgoing connections. Similar incoming
company. Similar weight on the books. DETOUR never named him.

If taking out the civilian causes the same disruption as taking out the suspect,
the suspect was not special. If only the suspect matters, the case gets much
stronger.
