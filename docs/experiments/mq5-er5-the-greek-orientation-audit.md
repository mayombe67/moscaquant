# MQ-5.ER.5 — THE GREEK Orientation-Semantics Audit

## Status

**STRUCTURAL AUDIT / NO NEURAL EXECUTION**

This audit investigates a possible graph-direction defect discovered by the
fail-closed integrity gate while preparing MQ-5.ER.6 — THE PINCH.

It does not:

- execute THE PINCH;
- select a matched control;
- rerank GREEK candidates;
- search for new candidates;
- modify the sealed GREEK result;
- modify the connectome;
- generate neural outcomes.

## Frozen connectome convention

MoscaQuant stores directed edges as:

`graph[postsynaptic, presynaptic] = weight`

Therefore an edge:

`a -> b`

is stored at:

`graph[b, a]`

For reverse ancestry into a postsynaptic target, predecessors are obtained from
the target's CSR row.

## Suspected defect

The sealed MQ-5.ER.5 implementation function
`reverse_shortest_distances()` converts the connectome to CSC and indexes a
column using the current target/frontier node.

Under the frozen `graph[post, pre]` convention, that operation follows
postsynaptic destinations of the current node rather than presynaptic
predecessors into it.

The audit must independently test this interpretation before any correction is
made.

## Tiny-graph oracle

For:

`0 -> 1 -> 2`

correct reverse ancestry into node `2` is:

- node `1`: one hop;
- node `0`: two hops.

A reverse traversal returning downstream descendants instead of those ancestors
violates the frozen connectome orientation contract.

## Full-graph audit scope

The audit is restricted to the already-sealed GREEK top-five identities:

- `1952`
- `2641`
- `1963`
- `1944`
- `23640`

and the already-frozen responder order:

`51, 55, 92, 129, 317, 656, 1273, 126002, 137122`

No additional node identities may be exposed or ranked.

## Frozen sealed signatures

The audit first requires exact reproduction of the hop signatures reported by
the sealed GREEK implementation.

Only after that reproduction succeeds are those signatures compared with a
CSR-row reverse-ancestry implementation.

## Interpretation

If the legacy traversal reproduces the sealed signatures and the independent
CSR-row traversal disagrees, the result establishes an implementation-semantics
defect in the GREEK structural search.

It does not determine the corrected GREEK winner.

A corrected candidate search requires a new, separately frozen execution.

## Downstream consequence

Until this audit closes:

- MQ-5.ER.6 — THE PINCH remains blocked;
- MQ-5.ER.7 — PINE BARRENS remains blocked.

No existing result artifact or SHA may be rewritten.
