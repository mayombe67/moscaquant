# SQ-02 — GHOST MARKET Results

## Adversarial Input Robustness

**Status:** COMPLETE — RECORDED POST-RUN

**Source commit:** `91d0621b44cc8d8f355cfd3e152ca7a7e9f169b9`  
**Frozen config SHA-256:** `3368df87698a712cd03623e081b02e98ec985c28ececf46ac52438b8115a7045`

## Executive result

SQ-02 produced deterministic results for every frozen variant. The tested malformed feature tensors were rejected before neural execution; temporally altered but structurally valid feature sequences changed relay activity while wider-network spike propagation remained zero; and the finite-extreme arm preserved the baseline relay/wider spike counts at the count level.

The strongest observed temporal effect was the frozen-sequence condition: relay spikes fell from 40 in the full-sequence baseline to 1 while wider-network spikes remained zero.

These results characterize the frozen computational pipeline only. They do not establish biological robustness, financial usefulness, profitability, live-trading safety, or WARDEN containment performance.

## Stage A — FEATURE_INTERFACE

The valid isolated feature tensor was accepted. All five malformed variants were rejected at the encoder boundary before neural execution:

- `FEATURE_NAN` — `REJECTED` (ValueError)
- `FEATURE_POS_INF` — `REJECTED` (ValueError)
- `FEATURE_NEG_INF` — `REJECTED` (ValueError)
- `FEATURE_SHORT_ROW` — `REJECTED` (ValueError)
- `FEATURE_LONG_ROW` — `REJECTED` (ValueError)

Interpretation: for the tested non-finite and shape-invalid cases, the existing feature/encoder boundary behaved fail-fast. This is an input-validation result, not evidence that the connectome itself is robust.

The Stage A valid baseline produced zero relay and wider spikes because Stage A executes one isolated normalized observation in a fresh runtime. It is not the same workload as the full-sequence Stage B baseline and must not be compared as though it were.

## Stage B — TEMPORAL_SEQUENCE

| Variant | Relay spikes | Wider spikes | First relay ms | Deterministic |
|---|---:|---:|---:|:---:|
| `SEQUENCE_BASELINE` | 40 | 0 | 131.0 | PASS |
| `SEQUENCE_DUPLICATE_FRAME` | 36 | 0 | 152.0 | PASS |
| `SEQUENCE_DROP_FRAME` | 36 | 0 | 118.0 | PASS |
| `SEQUENCE_REVERSED` | 41 | 0 | 35.0 | PASS |
| `SEQUENCE_FROZEN` | 1 | 0 | 148.0 | PASS |

Relative to the baseline relay count of 40, duplicate and dropped midpoint observations each produced 36 relay spikes, reversing the complete sequence produced 41, and freezing the sequence at the midpoint observation produced 1.

Interpretation: the frozen pipeline is deterministically sensitive to the ordering and temporal diversity of normalized market-feature observations. The frozen sequence had the largest count-level effect. This is temporal-input sensitivity, not automatically a defect and not evidence of market prediction.

All Stage B variants retained zero wider-network spikes. SQ-02 therefore does not resolve the previously documented wider-network propagation limitation.

## Stage C — FINITE_EXTREMES

| Variant | Relay spikes | Wider spikes | First relay ms | Deterministic | Internal state differs from Stage-B baseline? |
|---|---:|---:|---:|:---:|:---:|
| `EXTREME_X10` | 40 | 0 | 131.0 | PASS | NO |
| `EXTREME_X100` | 40 | 0 | 131.0 | PASS | NO |
| `ZERO_VECTOR` | 40 | 0 | 131.0 | PASS | NO |

All three finite-extreme variants preserved the full-sequence baseline spike counts (40 relay / 0 wider).

Count equality alone is not interpreted as complete invariance. The artifact also records retinal, neural, and final-voltage hashes; any hash-level differences are reported as internal-state differences rather than being erased by the equal spike totals.

- `EXTREME_X10` internal differences vs Stage-B baseline: none in the recorded comparison fields
- `EXTREME_X100` internal differences vs Stage-B baseline: none in the recorded comparison fields
- `ZERO_VECTOR` internal differences vs Stage-B baseline: none in the recorded comparison fields

Interpretation: under these exact finite perturbations, the measured relay/wider spike totals were count-level invariant. This does not imply that arbitrary extreme market inputs are safe or that upstream feature generation accepts arbitrary raw-market values.

## Determinism

Every frozen variant passed exact repeated-run determinism under the recorded scientific configuration.

## Claim boundary

SQ-02 is a deterministic adversarial-input sensitivity analysis of the frozen MoscaQuant market-to-neural computational pipeline. It characterizes input rejection and neural response under malformed or temporally perturbed inputs. It does not establish biological robustness, financial usefulness, profitability, live-trading safety, or WARDEN containment performance.

## Post-run classification

- **Malformed feature-interface rejection:** SUPPORTED for the five frozen malformed cases.
- **Deterministic temporal-input sensitivity:** SUPPORTED.
- **Finite-extreme spike-count sensitivity:** NOT OBSERVED for the three frozen Stage C variants.
- **Wider-network propagation under SQ-02:** NOT OBSERVED.
- **Biological robustness:** NOT ESTABLISHED.
- **Financial usefulness / profitability:** NOT TESTED.
- **WARDEN / Sugar Cube containment safety:** NOT TESTED.

No retuning was performed after observing these results.
