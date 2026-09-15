# MQ-1 Visual Heartbeat

## Status

Baseline biological sensory propagation experiment.

## Input population

MaleCNS v1.0 `ol_sensory` R1-R6 photoreceptors.

- Photoreceptors mapped: 3,377
- Unique MQ-001 mappings: 3,377
- Missing mappings: 0

The population is selected from biological annotations rather than
arbitrary MQ-001 indices.

## Neurotransmitter validation

All 3,377 R1-R6 neurons have:

- `consensus_nt = histamine`
- `ground_truth = histamine`
- `celltype_predicted_nt = histamine`

All 3,377 therefore have compiled MQ-001 transmitter sign `-1`.

## Experiment

A stimulus amplitude of `1.1` was applied to all 3,377 mapped R1-R6
photoreceptors at simulation step 0 using the baseline LIF runtime.

Baseline modeled dynamics:

- dt: 1 ms
- tau: 20 ms
- threshold: 1.0
- reset: 0.0

No parameters were tuned in response to the result.

## Result

Step 0:

- 3,377 photoreceptors fired

Step 1:

- 4,846 neurons received non-zero downstream input
- 4,846 negative responses
- 0 positive responses

First-hop superclass distribution:

- `ol_intrinsic`: 4,295
- `ol_sensory`: 551

Major first-hop neuron types:

| Type | Count |
|---|---:|
| L2 | 814 |
| L1 | 809 |
| L3 | 782 |
| L4 | 653 |
| T1 | 641 |
| R1-R6 | 523 |
| C3 | 309 |
| C2 | 78 |
| Lai | 75 |
| Lawf1 | 55 |
| L5 | 39 |
| Lawf2 | 22 |

The resulting membrane potentials subsequently decayed according to
the baseline LIF dynamics without additional spikes during the
10-step observation window.

## Interpretation

The experiment demonstrates a deterministic path from an annotated
MaleCNS sensory population through the frozen MQ-001 connectome into
predominantly optic-lobe intrinsic circuitry.

The entirely negative first-hop response is consistent with the
current compiler assigning histaminergic R1-R6 output a sign of `-1`.

This experiment does **not** establish that the current LIF dynamics
constitute a complete biological model of Drosophila vision.
Histaminergic transmission is currently represented by the simplified
MQ-001 transmitter-sign model.

The result is preserved as a baseline rather than used as justification
for parameter tuning.

## Next experiment

Spatially localized R1-R6 stimulation rather than simultaneous
whole-population illumination.
