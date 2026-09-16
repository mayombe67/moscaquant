# MQ-4 — Neuroscope Acceptance Record

**Status:** COMPLETE  
**Branch:** `mq4/neuroscope`

## Purpose

MQ-4 introduced Neuroscope as the read-only visualization and inspection layer for the frozen MoscaQuant MQ-1 through MQ-3 experimental state.

The phase focused on making existing anatomy, replay telemetry, causal evidence, and responder behavior inspectable without altering the underlying scientific model.

---

## Acceptance Result

MQ-4 passed final operator acceptance.

All planned Neuroscope capabilities through MQ-4.8 were verified in the live visualization.

No MQ-4.9 feature is required for phase completion.

---

## Verified Dataset Invariants

The accepted Neuroscope build reports:

NEURONS       12,475  
REAL SOMA      7,486  
FALLBACK       4,989  
CAUSAL EDGES      13  
RESPONDERS          9  
REPLAY FRAMES      192

These values remained stable while using display filters, replay controls, causal traversal, and responder isolation.

---

## Geometry Acceptance

Verified:

- 7,486 neurons use real MaleCNS `somaLocation`
- 4,989 neurons use explicit `topologyFallback`
- real and fallback geometry remain visually distinguishable
- topology fallback is never presented as anatomical evidence
- geometry filtering changes presentation only

Hybrid anatomy behavior is accepted.

---

## Inspection Acceptance

Neuron inspection successfully exposes:

- model index
- MaleCNS body ID
- role membership
- graded type where available
- DN cluster where available
- soma side
- soma neuromere where available
- geometry source
- causal-node status
- responder status

Inspection is read-only.

---

## Role Filter Acceptance

Verified role populations:

Retina                3,241  
Relay                 2,430  
Graded                5,490  
Descending neurons    1,314  
Responders                 9

Role filters alter visible populations without modifying dataset totals or experimental state.

---

## Replay Acceptance

Verified:

- 192 replay frames
- frame range 0–191
- previous / next navigation
- play / pause
- adjustable playback speed
- manual timeline scrubbing
- synchronized frame summaries
- voltage activity visualization
- effective-activity visualization
- spike visualization
- responder magnitude visualization

Replay represents previously recorded telemetry.

Playback does not execute a new simulation.

---

## Causal Inspection Acceptance

The frozen MQ-3.2 causal overlay remains:

13 causal edges

Selected causal nodes expose:

- incoming / outgoing direction
- peer model index
- preserved edge weight
- observed frame or frames

Selected connections can be visually emphasized without altering the underlying graph.

---

## Causal Traversal Acceptance

Graph traversal successfully reconstructs connected causal paths.

Verified example:

56393 → 68045 → 1273

Tracing model `1273` produces:

TRACE ROOT    1273  
NODES         3  
EDGES         2  
MAX DEPTH     2

with:

UP model 68045 depth 1  
UP model 56393 depth 2

Traversal semantics:

- cyan = upstream
- green = downstream
- root = selected trace origin
- unrelated anatomy = visually suppressed

Traversal does not generate new causal relationships.

---

## Responder Ensemble Acceptance

The frozen responder ensemble remains:

92  
656  
317  
137122  
126002  
55  
129  
51  
1273

Verified capabilities:

- isolate all nine responders
- current-frame responder values
- preserved causal-input counts
- peak response calculation
- peak-frame navigation
- synchronized 192-frame activity visualization
- selected-responder emphasis
- timeline click-to-jump behavior
- replay cursor synchronization

Verified peak frames:

92        F191  
656       F165  
317       F187  
137122    F183  
126002    F191  
55        F191  
129       F191  
51        F191  
1273      F191

Responder magnitude and timing remain descriptive telemetry and do not create additional causal claims.

---

## Operator Guide Acceptance

Neuroscope now includes a persistent:

GUIDE

control in the main header.

The guide is available directly from the visualization and documents:

- viewer navigation
- geometry semantics
- display controls
- role filters
- replay
- activity visualization
- neuron inspection
- causal inspection
- causal traversal
- responder ensemble analysis
- color semantics
- guided examples
- troubleshooting
- scientific boundaries

The repository also retains the corresponding project documentation.

---

## Runtime Portability

MQ-4 preserves separation between:

- scientific configuration
- replay artifacts
- runtime / machine configuration

The viewer does not depend on Habitat-specific scientific behavior.

Runtime migration to another workstation or cloud environment must not change experimental semantics.

---

## Scientific Boundaries

MQ-4 obeys the following constraints:

### Read-only

Neuroscope does not alter the frozen experimental model.

### Anatomy provenance

Only MaleCNS `somaLocation` is treated as anatomical geometry.

### Replay provenance

Replay displays previously recorded telemetry.

### Causal provenance

Causal overlays and traversal use the frozen MQ-3 causal result.

### No inference inflation

Visualization, timing comparison, graph traversal, and responder magnitude do not create additional causal evidence.

### Financial semantics

Financial and trading semantics remain:

NOT ASSIGNED

---

## Final MQ-4 Capability Set

MQ-4 delivers:

- hybrid anatomical visualization
- explicit geometry provenance
- interactive 3D navigation
- neuron inspection
- role decoding
- population filtering
- replay exploration
- activity visualization
- causal-edge inspection
- causal graph traversal
- responder ensemble isolation
- responder peak analysis
- synchronized responder activity plotting
- integrated operator documentation

---

## Acceptance Decision

**MQ-4 is accepted and complete.**

No additional MQ-4 feature is required before moving to the next project phase.

Neuroscope is now a stable inspection instrument for the frozen MoscaQuant experimental state.

> Visualization may make the evidence easier to understand, but it must not silently change what the evidence means.

**Anatomy. Evidence. Causality. Next.**

**Same neurons. Deeper questions.**
