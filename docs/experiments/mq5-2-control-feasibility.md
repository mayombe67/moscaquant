# MQ-5.2 — Generalized Control Feasibility

Status:

**FROZEN BEFORE GENERALIZED INTERVENTION OUTCOMES**

The frozen 13-edge MQ-3 causal set was scanned prospectively to determine
matched non-causal control availability before generalized MQ-5
intervention outcomes were generated.

## Result

- causal edges: 13
- matched controls available: 12
- matched controls unavailable: 1

The sole edge without a scientifically valid matched control is:

`43417 -> 656 @ frame 145`

For that edge, only the causal source itself fell inside the prospectively
defined activity-matching window.

The absence of a matched control for this edge is retained as an
experimental limitation rather than repaired by further post-hoc
relaxation.

## Generalized control policy

For each frozen causal edge:

1. baseline and zero-effect sham remain mandatory
2. dose-response intervention remains mandatory
3. timing controls remain applicable
4. the prospectively selected matched non-causal control is used where
   available
5. matched-control infeasibility is explicitly recorded where no valid
   candidate exists
6. no substitute control is selected after intervention outcomes are seen

Twelve matched-control assignments are frozen in:

`config/controls/mq5-2-generalized-control-map-v1.json`

The `43417 -> 656` entry explicitly records no matched control.

## Interpretation constraint

A matched-control comparison is available for 12 of 13 frozen causal
edges.

Claims about the complete 13-edge set must preserve the fact that one
edge lacks that control family.

Control infeasibility is not counted as a failed intervention result.

Financial semantics remain:

**NOT ASSIGNED**
