# SQ-06 — SILENT CARTOGRAPHER — Orientation Group Operator

**Status:** IMPLEMENTATION REVIEW CANDIDATE — NO NEURAL EXECUTION AUTHORIZED

## Scope

This module implements only the deterministic structural operators required by
the already-published SQ-06 preregistration.

It does not execute neural dynamics and has no result writer or result-bearing
CLI.

## Frozen inputs

The operator binds:

- the published SQ-06 orientation-group artifact;
- the historical MQ-3.2 13-edge causal lesion through the existing SQ-05 loader;
- the exact frozen SQ-05 13-edge sham artifact;
- the historical `zero_edges` implementation.

No target or sham edge is derived from a future SQ-06 outcome.

## Resolution rule

The SQ-06 group artifact intentionally stores edge identities, matched-sham
identities, and accepted-responder membership rather than copying historical
weights.

At runtime, this implementation resolves each targeted pair against the frozen
historical 13-edge lesion and each sham pair against the frozen 13-edge sham.
Missing or altered pairs fail closed.

The two groups remain:

- `LR_OBSERVED`: 10 targeted edges / 10 matched sham edges;
- `RL_OBSERVED`: 3 targeted edges / 3 matched sham edges.

## Mutation contract

`build_orientation_group()` copies the supplied connectome through the inherited
`zero_edges` operator and verifies:

- connectome shape is unchanged;
- edge count falls by exactly the subset size;
- exactly the requested subset identities changed;
- each baseline edge still has its frozen historical weight before zeroing;
- every selected edge is zero afterward.

## Scientific boundary

The grouping was derived descriptively after SQ-05 was sealed.

This implementation does not make the grouping independent discovery, does not
reinterpret SQ-05, and does not establish a biological orientation circuit.

Its only future scientific role is prospective validation under the separately
frozen SQ-06 protocol.

## SILENT CARTOGRAPHER

The coordinates are frozen.

This gate only proves that the demolition charges can be placed on exactly the
roads shown on the map.
