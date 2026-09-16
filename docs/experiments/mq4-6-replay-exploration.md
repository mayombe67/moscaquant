# MQ-4.6 — Neuroscope Replay Exploration

**Status:** Complete  
**Branch:** `mq4/neuroscope`

## Objective

Extend Neuroscope with time-based replay exploration using the existing frozen MQ-4 replay telemetry.

MQ-4.6 adds visualization and playback only.

No experimental model behavior, causal evidence, anatomical data, or financial semantics are modified.

## Replay Timeline

The replay contains 192 frames.

Neuroscope now supports:

- timeline scrubbing
- previous frame
- next frame
- play / pause
- adjustable playback rate
- automatic pause when manually scrubbing

The timeline is read-only and operates on the existing replay artifact.

## Frame Summary

The current frame exposes:

- retinal spike count
- relay spike count
- graded-active count
- descending-neuron mean activity
- descending-neuron maximum activity
- descending-neuron spike counts
- maximum responder activity

## Activity Visualization

Current-frame activity is projected onto the existing hybrid anatomical viewer.

Visualization semantics:

- baseline neuron color preserves geometry classification
- voltage activity increases node intensity and size
- effective activity is emphasized in cyan
- spike activity is emphasized in white
- responder identity remains amber
- responder magnitude modulates responder size

Activity visualization does not alter neuron role identity.

## Causal Context

The existing MQ-3.2 causal overlay remains available during replay.

Observed causal-frame metadata remains preserved.

For example, causal evidence associated with frame 145 remains inspectable through the frozen causal artifact.

## Preserved Scientific Invariants

MQ-4.6 preserves:

- 12,475 selected neurons
- 7,486 real soma positions
- 4,989 topology fallbacks
- 13 causal edges
- 9 causal responders

No topology fallback is represented as anatomical evidence.

## Scientific Boundary

Neuroscope remains a read-only interpretation layer.

Replay activity is visualization of previously recorded telemetry, not a new simulation run and not a new causal experiment.

Financial semantics remain:

**NOT ASSIGNED**

## Conclusion

MQ-4.6 is complete.

Neuroscope now supports anatomical inspection, causal inspection, role filtering, replay navigation, and time-varying activity visualization over the frozen MQ-1 through MQ-3 experimental state.

**Same neurons. Deeper questions.**
