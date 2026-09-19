# SQ-01 — Temporal Decoupling Results v1

**Lore name:** TEMPORAL JETLAG  
**Status:** COMPLETE — RESULTS RECORDED  
**Source commit:** `dad63a384a5bd23be0823c81ea2eaf410d160f53`  
**Frozen config SHA-256:** `ee87df86bee3d2a7456ec4833e034eef75b869f04df7b695d095797ae2b22733`

## Integrity gates

- baseline harness parity against the accepted MQ-2.1 runner: **PASS** for A and B;
- A/A exact determinism: **PASS** for every frozen variant;
- frozen seven-variant matrix executed without modification.

Machine-readable result:

`artifacts/sidequests/sq01-temporal-decoupling-v1.json`

## Frozen matrix results

| Variant | Frames | dt ms | Stimulus scale | A relay | B relay | A wider | B wider | A first relay ms | B first relay ms | A/B relay discrimination | A/B wider discrimination |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| BASELINE | 16 | 1.0 | 1.0 | 40 | 0 | 0 | 0 | 131.0 | None | YES | NO |
| CLOCK_FAST | 16 | 0.5 | 1.0 | 226 | 106 | 0 | 0 | 20.5 | 20.5 | YES | NO |
| CLOCK_SLOW | 16 | 2.0 | 1.0 | 3 | 0 | 0 | 0 | 286.0 | None | YES | NO |
| RESAMPLE_8 | 8 | 2.0 | 2.0 | 35 | 1 | 0 | 0 | 102.0 | 102.0 | YES | NO |
| RESAMPLE_32 | 32 | 0.5 | 0.5 | 38 | 0 | 0 | 0 | 130.0 | None | YES | NO |
| RAW_8 | 8 | 1.0 | 1.0 | 14 | 0 | 0 | 0 | 70.0 | None | YES | NO |
| RAW_32 | 32 | 1.0 | 1.0 | 76 | 3 | 0 | 0 | 133.0 | 133.0 | YES | NO |

## Primary observations

### 1. Duration-and-input-matched temporal resampling was comparatively stable

The accepted 16-frame / 1 ms baseline produced A=40 and B=0 relay spikes, with
A first relay at 131.0 ms.

`RESAMPLE_8` produced A=35 and B=1 relay spikes; A first relay was 102.0 ms.

`RESAMPLE_32` produced A=38 and B=0 relay spikes; A first relay was 130.0 ms.

Both matched variants retained A/B relay-trajectory discrimination.
`RESAMPLE_32` was especially close to baseline in relay count and first-relay
model time.

### 2. The neural integration step is a sensitive scientific parameter

At fixed 16-frame representation:

- `CLOCK_FAST` (0.5 ms): A=226, B=106 relay spikes;
- `BASELINE` (1.0 ms): A=40, B=0;
- `CLOCK_SLOW` (2.0 ms): A=3, B=0.

This large response change supports treating `dt_ms` as scientific
configuration rather than machine-speed or deployment configuration.

### 3. Raw frame-count changes showed larger response shifts

The deliberately confounded controls produced:

- `RAW_8`: A=14, B=0 relay spikes;
- `RAW_32`: A=76, B=3 relay spikes.

Compared with the matched resampling arms, these larger shifts are compatible
with effective observation duration and accumulated input being important
confounds when frame count changes without compensation.

This comparison is descriptive. SQ-01 did not preregister a statistical
decomposition assigning a percentage of the raw-frame effect to any one
confound.

### 4. MQ-2.1 wider-connectome limitation was preserved

Every SQ-01 arm produced zero wider-connectome spikes for A and B.

This is not a newly discovered SQ-01 failure. The accepted MQ-2.1 baseline
reproduced by the harness already had no wider-connectome propagation in this
experiment.

### 5. Determinism was preserved

Every frozen variant produced exact A/A replay agreement.

The observed differences therefore track declared experimental parameter
changes within this deterministic harness, not detected run-to-run
nondeterminism.

## Architectural implication

SQ-01 provides direct project evidence for keeping **wall-clock execution rate**
separate from **simulated neural time**.

A faster CPU, slower CPU, cloud migration, scheduler delay, or worker cadence
must not silently change `dt_ms` or reinterpret one simulation step.

Runtime/hardware changes may change how quickly computation completes. They
must not change frozen scientific time-step semantics without a new scientific
protocol.

## Deferred hypothesis

`RESAMPLE_8` produced one B relay spike while `RESAMPLE_32` produced none. This
may motivate a separately frozen future temporal-convergence experiment.

No additional frame-count sweep is inferred or executed from SQ-01 v1.

## Result interpretation

SQ-01 supports **conditional temporal robustness** of MQ-2.1 relay behavior
under the two tested duration-and-input-matched resampling variants, alongside
**strong sensitivity to the neural integration time step**.

This wording is a post-run interpretation of the preregistered matrix, not a
newly preregistered classification threshold.

## Claim boundary

SQ-01 is a deterministic sensitivity analysis of the frozen MoscaQuant
computational model. It tests dependence on temporal discretization and runtime
leak-step assumptions. It does not establish biological timing, biological
robustness, market profitability, or live-trading utility.
