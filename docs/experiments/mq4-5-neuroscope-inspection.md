# MQ-4.5 — Neuroscope Inspection and Causal Exploration

**Status:** Complete  
**Branch:** `mq4/neuroscope`

## Objective

Extend the MQ-4 Neuroscope viewer with interactive inspection tools while preserving the frozen MQ-1 through MQ-3 experimental state.

MQ-4.5 changes visualization and exploration only.

No experimental model behavior, causal evidence, anatomical source data, or financial semantics are modified.

## Neuron Inspection

The neuron inspector now exposes telemetry already present in the MQ-4 replay artifact:

- model index
- body ID
- role membership
- graded type
- descending-neuron cluster
- soma side
- soma neuromere
- geometry source
- causal-node status
- responder status

Roles are decoded from the replay role bitmask:

- Retina
- Relay
- Graded
- Descending neuron
- Responder

A neuron may carry more than one role.

## Role Filtering

Neuroscope now supports independent visibility controls for:

- Retina
- Relay
- Graded
- Descending neurons
- Responders

Observed replay populations:

- Retina: 3,241
- Relay: 2,430
- Graded: 5,490
- Descending neurons: 1,314
- Responders: 9

Filtering affects presentation only.

The canonical dataset totals remain unchanged.

## Causal Inspection

Selecting a node participating in the frozen MQ-3.2 causal pathway now exposes causal connections touching that node.

Displayed edge information includes:

- direction: incoming or outgoing
- connected model index
- causal edge weight
- observed frame or frames

The corresponding edge is highlighted in the viewer.

This does not generate new causal claims.

All displayed causal information originates from the existing MQ-3.2 causal artifact carried through the MQ-4 replay payload.

## Preserved MQ-4.4 Invariants

MQ-4.5 preserves:

- 12,475 selected neurons
- 7,486 real soma positions
- 4,989 explicit topology fallbacks
- 13 causal edges
- 9 causal responders

No topology fallback position is represented as anatomical evidence.

## Scientific Boundary

Neuroscope remains a read-only interpretation layer over frozen experimental telemetry.

MQ-4.5 improves the ability to inspect and navigate that evidence without changing the evidence itself.

Financial semantics remain:

**NOT ASSIGNED**

## Conclusion

MQ-4.5 is complete.

Neuroscope has progressed from a hybrid anatomical visualization into an interactive experimental inspection tool capable of examining neuron identity, functional role, causal membership, and local causal pathway evidence.

**Same neurons. Deeper questions.**
