# MQ-4.8 — Responder Ensemble Analysis

**Status:** Complete
**Branch:** `mq4/neuroscope`

## Objective

Extend Neuroscope with coordinated inspection of the nine causal responders identified by the frozen MQ-3 experimental state.

MQ-4.8 adds analysis and visualization of existing replay telemetry only.

No experimental model behavior, causal evidence, anatomical source data, or financial semantics are modified.

## Responder Ensemble

The frozen responder ensemble contains nine model indices:

- 92
- 656
- 317
- 137122
- 126002
- 55
- 129
- 51
- 1273

Neuroscope provides a dedicated responder-ensemble panel for these neurons.

## Ensemble Isolation

The viewer can isolate the nine responders from the full 12,475-neuron visualization.

Isolation affects presentation only.

Responder identity remains derived from the frozen replay telemetry.

## Per-Responder Analysis

For each responder, Neuroscope exposes:

- model index
- preserved causal-input count
- current-frame response value
- peak replay response value
- peak replay frame

Peak-frame controls allow direct navigation to the corresponding replay frame.

## Verified Peak Responses

Observed replay peaks:

- model 92: frame 191, approximately 4.024e-3
- model 656: frame 165, approximately 1.979e-3
- model 317: frame 187, approximately 5.445e-4
- model 137122: frame 183, approximately 2.004e-4
- model 126002: frame 191, approximately 5.738e-5
- model 55: frame 191, approximately 4.026e-5
- model 129: frame 191, approximately 2.447e-8
- model 51: frame 191, approximately 1.088e-8
- model 1273: frame 191, approximately 3.219e-6

## Synchronized Activity Plot

Neuroscope now renders the nine responder activity series over all 192 replay frames.

The plot includes:

- all nine responder traces
- current-frame cursor
- selected-responder emphasis
- frame labels
- click-to-jump timeline navigation
- synchronization with replay playback and manual scrubbing

The plot visualizes recorded replay telemetry and does not perform a new simulation.

## Causal Context

Responder ensemble analysis remains connected to the frozen MQ-3.2 causal overlay.

Existing causal inputs are shown alongside responder replay behavior.

No additional causal relationship is inferred from response magnitude or timing.

## Preserved Invariants

MQ-4.8 preserves:

- 12,475 selected neurons
- 7,486 real soma positions
- 4,989 topology fallbacks
- 13 causal edges
- 9 causal responders
- 192 recorded replay frames

## Scientific Boundary

Neuroscope remains a read-only experimental interpretation layer.

Responder peaks, plots, and ensemble isolation are computed only from previously recorded replay telemetry.

Financial semantics remain:

**NOT ASSIGNED**

## Conclusion

MQ-4.8 is complete.

Neuroscope now supports hybrid anatomical visualization, role inspection, replay exploration, causal inspection, causal traversal, and synchronized analysis of the nine-neuron responder ensemble.

**Same neurons. Deeper questions.**
