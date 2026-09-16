# MQ-4.7 — Neuroscope Causal Traversal

**Status:** Complete
**Branch:** `mq4/neuroscope`

## Objective

Extend Neuroscope with interactive traversal of the frozen MQ-3.2 causal graph.

MQ-4.7 adds graph-navigation and visualization only.

No experimental model behavior, causal evidence, anatomical source data, or financial semantics are modified.

## Causal Traversal

Selecting a causal node can now activate a trace of the connected causal subgraph.

The trace identifies:

- root node
- upstream nodes
- downstream nodes
- hop depth
- traced-node count
- traced-edge count
- maximum traversal depth

## Visual Semantics

During an active trace:

- unrelated neurons are dimmed
- unrelated causal edges are dimmed
- upstream nodes and edges are emphasized in cyan
- downstream nodes and edges are emphasized in green
- the trace root is highlighted separately

The underlying causal graph remains unchanged.

## Navigation

The inspector provides:

- previous causal node
- next causal node
- trace path
- clear trace

Navigation cycles through nodes participating in the frozen causal overlay.

## Verified Example

The preserved MQ-3.2 causal chain:

`56393 → 68045 → 1273`

is correctly reconstructed when tracing model index `1273`.

The trace reports:

- 3 nodes
- 2 edges
- maximum depth 2
- model `68045` upstream at depth 1
- model `56393` upstream at depth 2

## Scientific Boundary

Traversal is performed entirely over the existing 13-edge causal graph exported from MQ-3.2.

MQ-4.7 does not infer new causal edges or causal relationships.

Financial semantics remain:

**NOT ASSIGNED**

## Preserved Invariants

- 12,475 selected neurons
- 7,486 real soma positions
- 4,989 topology fallbacks
- 13 causal edges
- 9 causal responders

## Conclusion

MQ-4.7 is complete.

Neuroscope now supports anatomical visualization, replay inspection, neuron-role exploration, causal-edge inspection, and graph traversal over the frozen experimental state.

**Same neurons. Deeper questions.**
