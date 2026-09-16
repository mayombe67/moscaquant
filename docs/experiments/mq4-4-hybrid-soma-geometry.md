# MQ-4.4 — Hybrid Soma Geometry Neuroscope

**Status:** Complete  
**Branch:** `mq4/neuroscope`  
**Implementation commit:** `a208cb1`

## Objective

Extend Neuroscope from topology replay into a hybrid anatomical viewer using real MaleCNS soma coordinates where available, while preserving explicit topology fallback for neurons without valid soma geometry.

The viewer remains a read-only interpretation layer over frozen MQ-1 through MQ-3 telemetry.

No financial or trading semantics are assigned.

## Result

MQ-4.4 successfully produced a hybrid Neuroscope geometry containing:

- 12,475 selected neurons
- 7,486 neurons with real `somaLocation` geometry
- 4,989 neurons using explicit `topologyFallback`
- 13 MQ-3.2 causal-path edges
- 9 causal responders

## Geometry Contract

A neuron displayed from `somaLocation` is treated as anatomical geometry.

A neuron without valid soma geometry is displayed using topology fallback only.

Topology fallback coordinates are not treated or presented as anatomical coordinates.

The viewer preserves this distinction visually and in the neuron inspector.

No synthetic fallback position is promoted to anatomical evidence.

## Causal Overlay

The MQ-3.2 causal pathway is overlaid on the hybrid geometry without altering the underlying experimental model.

The viewer preserves:

- 13 causal edges
- 9 responder neurons
- responder identity by frozen model index

Responder visualization is derived from the existing replay telemetry and does not modify the experiment artifacts.

## Runtime Portability

Neuroscope runtime configuration is isolated from the scientific model through the runtime-profile layer.

The viewer is intended to remain portable across execution environments including:

- habitat
- workstation
- cloud

Runtime location does not alter experimental semantics.

## Browser Replay

The browser replay artifact remains derived data and is not committed to Git.

Canonical generated output:

`neuroscope/web/data/replay-A-v1.json`

Regeneration:

`source .venv/bin/activate`

`python -m neuroscope.build_web_replay`

## Verified Viewer Invariants

- NEURONS: 12,475
- REAL SOMA: 7,486
- FALLBACK: 4,989
- CAUSAL EDGES: 13
- RESPONDERS: 9

These counts define the MQ-4.4 browser-viewer checkpoint.

## Interpretation

MQ-4.4 demonstrates that the frozen MQ-1 through MQ-3 experimental telemetry can be projected into a substantially more anatomical representation without changing the underlying model or overstating missing anatomical data.

The result is therefore a hybrid visualization:

- anatomy where MaleCNS soma geometry exists
- explicit topology representation where it does not

This distinction is part of the scientific contract of Neuroscope.

## Conclusion

MQ-4.4 is complete.

The Neuroscope viewer now supports interactive rotation, zoom, pan, neuron inspection, real soma geometry, topology fallback, causal-path visualization, and responder highlighting while preserving the frozen experimental state.

**Same neurons. Deeper questions.**




