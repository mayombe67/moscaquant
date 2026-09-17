# MQ-5.7 — Neuroscope Intervention Replay Protocol

Status:

**PRE-REGISTERED / IMPLEMENTATION NOT YET EXECUTED**

## Purpose

MQ-5.7 exposes completed MQ-5 intervention evidence for interactive,
read-only inspection in Neuroscope.

Neuroscope remains a visualization and replay system.

It is not an experiment engine.

## Scientific boundary

MQ-5.7 must not:

- execute neural simulation
- execute MQ-5 interventions
- generate new causal outcomes
- select new causal nodes
- select new causal frames
- select new controls
- alter frozen MQ-1 through MQ-5 artifacts
- write experimental results back into source artifacts
- feed viewer state into the neural model

MQ-5.7 may only transform already-completed artifacts into a compact
visualization payload.

## Existing MQ-4 replay

The existing:

`neuroscope/web/data/replay-A-v1.json`

remains the base neural telemetry replay.

MQ-5.7 must not require modification of its scientific contents.

MQ-5 intervention data will be exported as a separate payload.

## MQ-5.7 web artifact

Proposed artifact:

`neuroscope/web/data/mq5-interventions-v1.json`

Schema:

`mq5-neuroscope-intervention-replay-v1`

The payload must explicitly contain:

- `readOnly = true`
- `simulationFeedback = false`
- source artifact provenance
- source software commits where available
- intervention identities
- frozen source nodes
- frozen target nodes
- frozen causal frames
- attenuation doses
- completed outcome metrics
- result classifications already established by MQ-5

## Intervention families

### Generalized single-edge interventions

Source:

`mq5-generalized-intervention-matrix-v1`

Expose all 13 frozen causal edges.

For each edge expose, where available:

- source
- target
- causal frame
- frozen weight
- baseline metrics
- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation
- timing-control result
- matched-control result
- existing validation state

No new classification is performed by Neuroscope.

### Two-hop pathway

Source:

`mq5-4-pathway-56393-68045-1273-v1`

Expose:

`56393 → 68045 → 1273`

including:

- upstream intervention
- intermediate intervention
- frozen causal frames
- baseline telemetry
- completed dose-series metrics

### Convergence systems

Source:

`mq5-5-convergence-specificity-v1`

Expose:

- `44274 + 55925 → 55`
- `55548 + 87441 → 51`
- `92657 + 93484 → 129`

including:

- A-only intervention
- B-only intervention
- combined intervention
- dose
- completed effect magnitude
- completed combined-versus-single result

Do not label interaction as synergy, antagonism, subadditivity, or
superadditivity.

### Methodological robustness

CONF-004A and MQ-5.6 may be shown as evidence badges or provenance panels.

These panels report completed robustness evidence only.

They must not be represented as new intervention outcomes.

## Viewer behavior

MQ-5.7 should add an `INTERVENTION REPLAY` mode or panel.

The viewer should support:

- intervention-family selection
- experiment selection
- attenuation-dose selection
- baseline versus intervention comparison
- causal-frame marker
- source highlighting
- target highlighting
- pathway highlighting
- convergence-input highlighting
- completed effect metrics
- existing result classification
- provenance display

## Temporal traces

Where a frozen MQ-5 NPZ artifact contains baseline and intervention traces,
the MQ-5.7 builder may export only the already-recorded traces necessary for
visual inspection.

The viewer must never recompute a missing trace.

Missing telemetry must be displayed as unavailable rather than reconstructed.

## Anatomy semantics

Existing MQ-4 geometry semantics remain unchanged.

Real MaleCNS `somaLocation` geometry remains anatomical.

`topologyFallback` remains explicitly non-anatomical.

MQ-5.7 must not infer or invent anatomical positions.

## Display semantics

Intervention overlays must visually distinguish:

- baseline state
- intervened source
- affected target
- frozen causal edge
- pathway intermediate
- convergence inputs
- matched control where present
- timing control where present

Visual emphasis is not additional evidence.

## Read-only acceptance checks

MQ-5.7 passes only if:

- source artifacts are unchanged before and after export
- web artifact declares read-only behavior
- simulation feedback is disabled
- no production neural runtime is imported
- no MQ-5 intervention runtime is imported
- no experimental runner is imported
- all displayed experiment identifiers resolve to frozen source artifacts
- all displayed nodes and causal edges resolve to the existing Neuroscope
  population
- topology fallback remains explicitly non-anatomical

## Scientific interpretation

MQ-5.7 does not strengthen or weaken the underlying causal evidence.

It makes completed MQ-5 evidence inspectable.

The evidence continues to come from the frozen MQ-5 experiment artifacts,
not from Neuroscope.

Biological causality:

**NOT CLAIMED**

Financial semantics:

**NOT ASSIGNED**
