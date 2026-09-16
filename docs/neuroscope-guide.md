# MoscaQuant Neuroscope User Guide

**Project:** MoscaQuant
**Component:** MQ-4 Neuroscope
**Scope:** MQ-4.1 through MQ-4.8
**Status:** Operator Guide

> **Same neurons. Deeper questions.**

Neuroscope is the interactive visualization and inspection layer for the frozen MoscaQuant MQ-1 through MQ-3 experimental state.

It is designed to help inspect anatomy, replay recorded neural activity, examine preserved causal evidence, traverse causal pathways, and analyze the nine-neuron responder ensemble.

Neuroscope is a **read-only interpretation layer**.

It does not modify the experimental model and does not create new causal evidence.

---

# 1. Five-Minute Quick Start

## 1.1 Open Neuroscope

From the MoscaQuant repository, generate the web replay if needed:

```bash
source .venv/bin/activate
python -m neuroscope.build_web_replay

Serve the web directory using the existing development server.

Open:

http://127.0.0.1:8080/

If the browser appears to show an older version of Neuroscope, use a cache-busting URL such as:

http://127.0.0.1:8080/?fresh=1

and perform a hard refresh.

1.2 Move Around the Brain

Mouse controls:

drag — rotate
Shift + drag — pan
mouse wheel — zoom
double-click — reset camera

The orientation marker in the lower-left shows the viewer X/Y axes.

1.3 Click a Neuron

Click any visible neuron.

The Neuron Inspector displays information such as:

model index
MaleCNS body ID
functional roles
graded type
DN cluster
soma side
soma neuromere
geometry source
causal-node status
responder status

Causal nodes expose additional causal-edge information.

1.4 Scrub the Replay

Use the Replay slider.

The replay contains:

192 frames
frames 0–191

The frame summary shows recorded neural-state information for the selected replay frame.

Controls include:

previous frame
play / pause
next frame
playback speed
direct slider scrubbing

Dragging the slider automatically pauses playback.

1.5 Trace a Causal Path

Select a neuron participating in the causal overlay.

Use:

TRACE PATH

Neuroscope dims unrelated anatomy and reconstructs the connected frozen causal subgraph.

During traversal:

cyan = upstream
green = downstream
highlighted root = selected trace origin

Use:

◀ PREV
NEXT ▶

to move between causal nodes.

1.6 Explore the Responder Ensemble

Scroll to:

RESPONDER ENSEMBLE

Use:

ISOLATE 9 RESPONDERS

to display only the nine causal responders.

Each responder row shows:

model index
preserved causal-input count
current-frame value
peak value
peak frame

Click a peak-frame button such as:

F165

to jump directly to that responder's peak.

The synchronized activity graph displays all nine response series over all 192 replay frames.

Click anywhere on the graph to jump to that frame.

2. What You Are Looking At

Neuroscope uses hybrid geometry.

The viewer contains:

12,475 selected neurons
 7,486 real soma positions
 4,989 topology fallbacks
    13 causal edges
     9 causal responders
   192 replay frames

These are the core Neuroscope invariants.

3. Geometry
3.1 Real Soma Geometry

Blue neurons marked:

somaLocation

use actual MaleCNS soma coordinates.

These coordinates are anatomical data.

The current MQ-4 geometry contains:

7,486 real soma positions
3.2 Topology Fallback

Gray neurons marked:

topologyFallback

do not have usable soma geometry in the MQ-4 artifact.

Their positions exist only to preserve useful topology and viewer structure.

They are not anatomical coordinates.

The current viewer contains:

4,989 topology fallback neurons

Neuroscope intentionally keeps this distinction visible.

A fallback position must never be interpreted as evidence of the neuron's anatomical location.

4. Main Display Controls
Real soma geometry

Shows or hides neurons with real MaleCNS somaLocation coordinates.

Topology fallback

Shows or hides neurons displayed using non-anatomical topology placement.

Causal overlay

Shows or hides the preserved MQ-3.2 causal edges.

Responders only

Restricts the visible population to causal responder neurons.

This affects presentation only.

5. Role Filters

Neuroscope exposes five role categories.

Retina

Role bit:

1

Population:

3,241
Relay

Role bit:

2

Population:

2,430
Graded

Role bit:

4

Population:

5,490
Descending neurons

Role bit:

8

Population:

1,314
Responders

Role bit:

16

Population:

9

A neuron may belong to more than one role.

Role filters alter visibility only.

They do not modify replay telemetry or experimental state.

6. Replay

The Neuroscope replay is derived from the frozen MQ-4 replay artifact.

It contains:

192 frames

The replay is not a live simulation.

It is playback of previously recorded telemetry.

6.1 Replay Controls
Previous

Moves backward one frame.

Play / Pause

Automatically advances through replay frames.

Next

Moves forward one frame.

Speed

Available playback rates include:

2 fps
4 fps
8 fps
12 fps
24 fps
Slider

Directly selects any frame from:

0–191

Manual scrubbing pauses automatic playback.

7. Frame Summary

The Replay panel exposes several recorded values.

Retinal spikes

Number of retinal spikes recorded during the current frame.

Relay spikes

Number of relay spikes recorded during the current frame.

Graded active

Number of graded neurons active during the frame.

DN mean

Mean descending-neuron activity by recorded DN grouping.

DN max

Maximum descending-neuron activity by grouping.

DN spikes

Recorded DN spike counts.

Max responder

Maximum response magnitude among the nine responder neurons for the current frame.

8. Activity Visualization

Replay activity changes the appearance of neurons without changing their identity.

Baseline

Normal neuron color reflects geometry classification.

Voltage activity

Increasing voltage magnitude increases visual intensity and node size.

Effective activity

Effective activity is emphasized in cyan.

Spikes

Spike activity appears as a bright white emphasis.

Responders

Responder identity remains amber.

A responder does not stop being a responder when its current activity is zero.

Responder magnitude may increase the displayed responder size during replay.

9. Neuron Inspector

Clicking a neuron opens its metadata.

Model index

Internal MoscaQuant model index.

This is often the most useful identifier when following replay or causal results.

Body ID

MaleCNS body identifier.

Roles

Decoded role membership.

Example:

DN · RESPONDER
Graded type

Recorded graded-neuron classification where available.

DN cluster

Descending-neuron cluster assignment where available.

Soma side

Recorded soma side, such as:

L
R
Neuromere

Recorded soma neuromere where available.

Geometry

Either:

somaLocation

or:

topologyFallback
Causal node

Indicates whether the neuron participates in the preserved MQ-3.2 causal graph.

Responder

Indicates membership in the frozen nine-neuron responder ensemble.

10. Causal Connections

When a selected neuron participates in the preserved causal graph, Neuroscope displays its local causal connections.

Each entry includes:

direction
connected model index
preserved edge weight
observed frame or frames

Example:

IN · model 43417
weight 6.6445e-4
frame 145

This means the selected node receives one preserved causal edge from model 43417, with the displayed weight, observed at frame 145.

Neuroscope is displaying previously established MQ-3.2 evidence.

It is not generating a new causal conclusion.

11. Causal Traversal

The Trace Path function reconstructs the connected portion of the frozen causal graph around a selected causal node.

TRACE PATH

Starts traversal from the selected node.

CLEAR TRACE

Returns to the normal viewer.

PREV / NEXT

Moves through nodes participating in the causal graph.

11.1 Trace Summary

An active trace reports:

TRACE ROOT
NODES
EDGES
MAX DEPTH
Trace root

The model index from which traversal began.

Nodes

Number of causal nodes in the connected trace.

Edges

Number of preserved causal edges in that trace.

Maximum depth

Maximum graph distance from the trace root.

11.2 Trace Colors
Cyan

Upstream nodes and edges.

These lead toward the trace root.

Green

Downstream nodes and edges.

These lead away from the trace root.

Root highlight

The selected trace origin.

Dimmed anatomy

Neurons and causal edges unrelated to the active trace are visually suppressed.

They are not removed from the underlying data.

12. Verified Causal Example

A useful test path is:

56393 → 68045 → 1273

Select model:

1273

and choose:

TRACE PATH

The expected result is:

TRACE ROOT    1273
NODES         3
EDGES         2
MAX DEPTH     2

With:

UP model 68045 depth 1
UP model 56393 depth 2

This is an excellent quick test that causal traversal is functioning correctly.

13. Responder Ensemble

The frozen responder ensemble contains nine neurons:

92
656
317
137122
126002
55
129
51
1273

These identities originate from the frozen MQ-3 experimental state.

14. Responder Ensemble Panel

Each responder row displays:

Model index

Responder's MoscaQuant model index.

Inputs

Number of preserved MQ-3.2 causal edges entering that responder.

Now

Responder value at the current replay frame.

Peak

Maximum absolute response observed during the 192-frame replay.

Peak frame

Frame at which the recorded peak occurred.

The peak button directly jumps the replay to that frame.

15. Verified Responder Peaks

Current frozen replay peaks:

Model      Peak frame      Peak value

92         191             ~4.024e-3
656        165             ~1.979e-3
317        187             ~5.445e-4
137122     183             ~2.004e-4
126002     191             ~5.738e-5
55         191             ~4.026e-5
129        191             ~2.447e-8
51         191             ~1.088e-8
1273       191             ~3.219e-6

These are replay measurements.

Their relative magnitude alone should not be interpreted as additional causal evidence.

16. Synchronized Responder Activity Graph

The responder activity graph displays all nine responder time series over:

frames 0–191
White vertical line

Current replay frame.

Colored traces

Recorded activity of the nine responder neurons.

Selected responder

The currently selected responder trace is drawn more prominently.

Click-to-jump

Click anywhere along the graph timeline to move the replay to the corresponding frame.

The graph remains synchronized with:

playback
manual slider movement
peak-frame buttons
direct timeline clicks
17. Guided Exercise 1 — Responder 656

This exercise introduces replay, responders, and causal inspection.

Locate responder:

656

Click:

F165

Expected:

current frame = 165
selected model = 656

Model 656 has a recorded responder peak near:

1.979e-3

Its preserved causal input includes:

43417 → 656

with evidence associated with frame:

145

This exercise demonstrates the difference between:

causal-edge observation frame
later replay response peak

Do not assume those two timestamps represent the same type of evidence.

18. Guided Exercise 2 — Multi-Hop Causal Traversal

Navigate to:

1273

Choose:

TRACE PATH

Expected path:

56393 → 68045 → 1273

Expected trace:

3 nodes
2 edges
maximum depth 2

Observe:

cyan upstream highlighting
dimmed unrelated anatomy
depth values in the inspector

Then select model:

68045

and trace again.

This demonstrates how trace direction changes relative to the selected root.

19. Guided Exercise 3 — Late Responder Ensemble

Use the replay controls to move toward:

frame 191

Several responders reach their replay maxima at or near the end of the recorded sequence.

Use:

ISOLATE 9 RESPONDERS

Then inspect the synchronized activity graph.

Compare:

92
317
137122
656

Notice that the responders do not all peak on the same frame.

The ensemble is temporally structured.

This is a replay observation, not a new causal inference.

20. Color Cheat Sheet

Approximate viewer semantics:

Blue        real soma geometry
Gray        topology fallback

Orange      causal responder / causal overlay
White       spike or selected-node emphasis
Cyan        effective activity / upstream trace
Green       downstream trace
Purple      interface / control emphasis

Context matters.

For example, cyan can indicate replay effective activity or an upstream causal trace depending on the active viewer mode.

21. Scientific Boundaries

These constraints are important.

Frozen experimental state

Neuroscope consumes telemetry produced by earlier MoscaQuant experimental phases.

It does not modify that state.

No invented anatomy

Only MaleCNS somaLocation coordinates are treated as anatomical geometry.

Topology fallback coordinates are explicitly non-anatomical.

No new causal inference

Neuroscope visualizes the frozen MQ-3.2 causal graph.

Tracing, highlighting, and replay comparison do not create new causal relationships.

Replay is not simulation

Playback shows recorded telemetry.

Pressing Play does not rerun MoscaQuant.

Response magnitude is descriptive

A larger responder value does not automatically imply greater biological importance or stronger causal status.

Financial semantics

Financial and trading semantics remain:

NOT ASSIGNED

Neuroscope currently describes the neural experimental model only.

22. Expected Invariants

A healthy MQ-4.8 Neuroscope build should report:

NEURONS       12,475
REAL SOMA      7,486
FALLBACK       4,989
CAUSAL EDGES      13
RESPONDERS          9

Replay:

192 frames

If these values unexpectedly change, treat the change as a data/build issue until explained.

Do not modify the viewer to hide an invariant mismatch.

23. Regenerating the Browser Replay

The browser replay file is generated data and is intentionally not committed to Git.

Expected output:

neuroscope/web/data/replay-A-v1.json

Regenerate with:

source .venv/bin/activate
python -m neuroscope.build_web_replay

Then reload Neuroscope.

24. Troubleshooting
DATA LOAD FAILED / HTTP 404

If Neuroscope reports:

HTTP 404

for the replay artifact, regenerate:

python -m neuroscope.build_web_replay

Verify:

ls -lh neuroscope/web/data/replay-A-v1.json
Browser shows an old UI

Firefox may retain an older app.js.

Try:

Ctrl + Shift + R

If necessary, use a query parameter:

http://127.0.0.1:8080/?fresh=2

The query value can be changed whenever a completely fresh load is needed.

Verify what the server is serving

Example:

curl -s http://127.0.0.1:8080/app.js \
  | grep -n "RESPONDER ENSEMBLE"

If the source file contains a feature but the HTTP response does not, the web server may be serving a different directory.

Verify JavaScript syntax

Before committing:

node --check neuroscope/web/app.js

No output indicates a successful syntax check.

Verify Git whitespace/errors

Run:

git diff --check

No output is expected.

25. Operator Workflow

A practical Neuroscope analysis session usually follows this order:

1. Inspect anatomy
2. Adjust role filters
3. Select a neuron
4. Inspect metadata
5. Scrub replay
6. Examine local causal edges
7. Trace causal graph if applicable
8. Compare responder activity
9. Jump to interesting replay frames
10. Return to full anatomy view

This keeps anatomy, recorded activity, and causal evidence conceptually separate.

26. Current MQ-4 Capability Summary

As of MQ-4.8, Neuroscope supports:

hybrid anatomical geometry
real soma coordinates
explicit topology fallback
interactive rotation
pan and zoom
neuron inspection
role decoding
role filtering
causal-edge overlay
local causal inspection
selected-edge highlighting
192-frame replay
replay frame summaries
play / pause
adjustable replay speed
activity visualization
causal traversal
upstream/downstream analysis
graph-depth reporting
causal-node navigation
nine-responder isolation
responder peak analysis
responder peak-frame navigation
synchronized responder activity plotting

Neuroscope remains an experimental inspection instrument rather than an execution engine.

27. Project Principle

The viewer should continue to preserve one fundamental rule:

Visualization may make the evidence easier to understand, but it must not silently change what the evidence means.

Anatomy. Evidence. Causality. Next.

Same neurons. Deeper questions.
