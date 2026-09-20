# SQ-04 — GLOBAL MODULATION SENSITIVITY Results

**Status:** COMPLETE — RECORDED POST-RUN

**Source commit:** `f4d2949012abd1a2db33df264fa0ecf3415f1a25`  
**Frozen config SHA-256:** `f764888910fd49887ec2f2d203eea9424c54aa74fdd13d77cf93ea93bfb0940f`

## Executive result

Every frozen SQ-04 variant passed exact repeated-run determinism.

Small global changes in spike threshold and membrane time constant produced large, directionally ordered changes in retinal and relay spike counts and in first-relay timing under the frozen Condition A replay.

No tested variant produced wider-network spikes.

## Primary measurements

| Variant | Retinal spikes | Relay spikes | Wider spikes | First relay ms | First wider ms |
|---|---:|---:|---:|---:|---:|
| `REFERENCE` | 2605 | 40 | 0 | 131.0 | — |
| `THRESHOLD_LOW_10` | 3685 | 70 | 0 | 48.0 | — |
| `THRESHOLD_HIGH_10` | 1816 | 17 | 0 | 138.0 | — |
| `TAU_FAST_25` | 1094 | 15 | 0 | 139.0 | — |
| `TAU_SLOW_25` | 4010 | 66 | 0 | 65.0 | — |

## Threshold sensitivity

Lowering threshold from `1.0` to `0.9` increased retinal spikes from 2605 to 3685, increased relay spikes from 40 to 70, and advanced first relay activity from 131 ms to 48 ms.

Raising threshold from `1.0` to `1.1` reduced retinal spikes to 1816, reduced relay spikes to 17, and delayed first relay activity to 138 ms.

Within the frozen three-point threshold comparison, count-level ordering was monotonic.

## Membrane-time-constant sensitivity

Reducing `tau_ms` from `20` to `15` reduced retinal spikes from 2605 to 1094, reduced relay spikes from 40 to 15, and delayed first relay activity from 131 ms to 139 ms.

Increasing `tau_ms` from `20` to `25` increased retinal spikes to 4010, increased relay spikes to 66, and advanced first relay activity to 65 ms.

Within the frozen three-point tau comparison, count-level ordering was monotonic.

## Wider-network result

No wider-network spike propagation was observed in any SQ-04 variant.

## Hash/state differences

Every non-reference arm differed from REFERENCE in neural/relay activity hashes, spike counts, first-relay timing, and final-voltage state.

The artifact field named `retinal_hash` also changed in every non-reference arm because the current runner hashes both encoded retinal frames and retinal firing state into that digest. It must therefore not be interpreted as a pure input-stimulus hash.

This naming limitation does not affect the primary spike-count/timing conclusions above, but future runners should separate `retinal_stimulus_hash` from `retinal_spike_hash`.

## Runner hash note

The current runner's `retinal_hash` combines encoded retinal-frame data with retinal firing-state data. It must not be interpreted as a pure input-stimulus hash.

This bookkeeping limitation does not affect the recorded spike-count or timing results. Future runners should separate `retinal_stimulus_hash` from `retinal_spike_hash`.

## Determinism

All five variants passed exact A/A replay determinism under the frozen scientific configuration.

## Claim boundary

SQ-04 measures deterministic sensitivity of the frozen MoscaQuant computational runtime to small global changes in spike threshold and membrane time constant. These parameters are model mechanics. The experiment does not identify or simulate a biological neuromodulatory system, establish biological realism, test learning, or demonstrate financial usefulness.

## Post-run classification

- **Global threshold sensitivity:** SUPPORTED within the frozen tested range.
- **Membrane time-constant sensitivity:** SUPPORTED within the frozen tested range.
- **Directionally ordered count response:** OBSERVED for both tested parameter axes.
- **Wider-network propagation:** NOT OBSERVED.
- **Biological neuromodulation:** NOT ESTABLISHED.
- **Plasticity / learning:** NOT TESTED.
- **Financial usefulness / profitability:** NOT TESTED.
- **WARDEN / Sugar Cube containment:** NOT TESTED.

No retuning was performed after observing these results.
