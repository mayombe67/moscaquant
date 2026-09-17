# MQ-5.1 — Experimental Intervention Protocol

**Status:** PRE-REGISTERED / IMPLEMENTATION NOT STARTED  
**Phase:** MQ-5 — Intervention and Perturbation Experiments  
**Branch:** `mq5/interventions`

## Purpose

MQ-5 begins the active intervention phase of MoscaQuant.

MQ-1 through MQ-3 established the frozen experimental evidence.

MQ-4 established Neuroscope as a read-only inspection instrument.

MQ-5 now asks whether deliberate, controlled perturbations of evidence-defined nodes and pathways produce reproducible downstream changes relative to predefined controls.

This document freezes the experimental design before intervention implementation or result inspection.

---

# 1. Scientific Boundary

MQ-5 must preserve the distinction between:

1. frozen pre-MQ-5 evidence,
2. the intervention applied,
3. the resulting neural activity,
4. the comparison against controls,
5. any new causal conclusion.

MQ-5 does not modify MQ-1 through MQ-3 artifacts in place.

MQ-4 Neuroscope remains read-only.

Financial and trading semantics remain:

**NOT ASSIGNED**

---

# 2. Frozen Evidence Entering MQ-5

MQ-5 begins with the accepted MQ-4 / MQ-3 experimental state.

## Population

- 12,475 selected neurons
- 7,486 real MaleCNS soma positions
- 4,989 topology fallbacks
- 1,314 descending neurons
- 9 frozen responders
- 13 preserved causal edges
- 192 replay frames

## Frozen responder ensemble

The nine responder model indices are:

- 92
- 656
- 317
- 137122
- 126002
- 55
- 129
- 51
- 1273

## Frozen causal edges

The accepted MQ-3.2 causal graph contains:

1. `43417 → 656` at frame 145
2. `44274 → 55` at frame 146
3. `55548 → 51` at frame 149
4. `55925 → 55` at frame 146
5. `56393 → 68045` at frame 146
6. `64717 → 92` at frame 145
7. `65084 → 137122` at frame 146
8. `68045 → 1273` at frame 147
9. `87441 → 51` at frame 149
10. `92657 → 129` at frame 148
11. `93484 → 129` at frame 148
12. `128590 → 317` at frame 147
13. `135589 → 126002` at frame 147

These edges define the primary intervention-eligible causal set.

No target may be added to the primary causal set after intervention results are observed.

---

# 3. Primary Research Question

Do interventions on frozen MQ-3 causal nodes produce reproducible downstream changes in their predicted responder or downstream pathway relative to predefined controls?

---

# 4. Primary Hypothesis

For an evidence-defined causal connection:

`A → B`

reducing the contribution of `A` during the relevant intervention window will reduce the downstream response of `B` relative to the matched sham condition.

This hypothesis is directional.

The primary test is not whether the system changes somewhere.

The primary test is whether the predefined downstream target changes in the predicted direction relative to control.

---

# 5. Secondary Hypothesis — Pathway Dependence

For the accepted multi-hop path:

`56393 → 68045 → 1273`

perturbation of the intermediate node `68045` will reduce downstream response in model `1273` relative to sham.

Perturbation of upstream model `56393` is also expected to reduce activity transmitted through the same pathway.

This pathway is designated before MQ-5 execution and therefore may be used as the primary multi-hop specificity experiment.

---

# 6. Secondary Hypothesis — Convergent Inputs

Three frozen responders have multiple preserved causal inputs:

## Model 55

`44274 → 55`

`55925 → 55`

## Model 51

`55548 → 51`

`87441 → 51`

## Model 129

`92657 → 129`

`93484 → 129`

These systems will be used to test whether:

- perturbing one input changes the responder,
- perturbing the other input changes the responder,
- combined perturbation differs from either single-input perturbation.

Combined interventions are secondary experiments and must not replace the primary single-node tests.

---

# 7. Intervention Classes

MQ-5 will initially support controlled perturbations that can be expressed without changing the underlying connectome.

The initial intervention classes are:

## A. Node silencing

Suppress the selected source neuron's contribution during the intervention window.

Purpose:

Test whether removing the candidate causal source reduces its predicted downstream effect.

## B. Partial attenuation

Reduce, but do not completely remove, the selected source neuron's contribution.

Purpose:

Test whether downstream effects exhibit intervention-strength sensitivity.

The initial attenuation series will use predefined levels:

- 25% attenuation
- 50% attenuation
- 75% attenuation
- 100% attenuation / full silencing

These values refer to reduction relative to the unperturbed contribution.

## C. Timing-shift intervention

Apply the same intervention magnitude outside the evidence-defined causal timing window.

Purpose:

Separate timing-specific effects from generic perturbation effects.

## D. Combined-input intervention

For predefined convergent-input responder systems only, perturb both preserved causal inputs together.

Purpose:

Evaluate whether combined input removal produces a different downstream effect than either single-input perturbation.

Combined-input experiments occur only after the corresponding individual interventions have been executed.

---

# 8. Intervention Scope

Interventions must be implemented as experimental overlays.

They must not rewrite:

- the baseline connectome,
- frozen MQ-1 through MQ-3 artifacts,
- MaleCNS source data,
- frozen MQ-4 replay artifacts.

Every generated intervention run must identify the baseline artifact from which it was derived.

---

# 9. Primary Intervention Set

The first-pass single-node intervention set consists of the direct causal source nodes from the frozen graph:

- 43417
- 44274
- 55548
- 55925
- 56393
- 64717
- 65084
- 68045
- 87441
- 92657
- 93484
- 128590
- 135589

The corresponding predefined downstream targets are:

| Intervention source | Primary downstream target |
| --- | --- |
| 43417 | 656 |
| 44274 | 55 |
| 55548 | 51 |
| 55925 | 55 |
| 56393 | 68045 |
| 64717 | 92 |
| 65084 | 137122 |
| 68045 | 1273 |
| 87441 | 51 |
| 92657 | 129 |
| 93484 | 129 |
| 128590 | 317 |
| 135589 | 126002 |

The source/target mapping is frozen before intervention results are observed.

---

# 10. Control Conditions

Every MQ-5 intervention must include a predefined control.

No intervention result is accepted without its required control.

## 10.1 Baseline control

Run the unchanged experimental configuration.

Purpose:

Confirm that the intervention harness reproduces the expected unperturbed state.

The baseline must be validated before perturbation results are interpreted.

## 10.2 Sham intervention

Execute the intervention machinery while applying zero perturbation.

Purpose:

Detect effects caused by the intervention framework itself.

## 10.3 Timing-shift control

Apply the same perturbation outside the evidence-defined intervention window.

Purpose:

Test temporal specificity.

## 10.4 Matched non-causal control

Where a scientifically valid matched node can be selected without using intervention outcomes, perturb a node that is not part of the frozen causal relationship.

Matching rules must be defined before the control node is selected.

Potential matching dimensions include:

- functional role
- activity magnitude
- graph degree
- baseline activity
- anatomical class where available

Control-node selection must not use MQ-5 outcome data.

---

# 11. Measurement Window

The intervention harness must preserve the original temporal sequence.

Measurements will include:

## Pre-intervention window

Used to establish local baseline activity before perturbation.

## Intervention window

Defined from the evidence-associated timing of the tested causal relationship.

## Post-intervention window

Used to measure downstream effects and persistence.

Exact frame/window mechanics will be implemented consistently across intervention and control runs.

They must be fixed before the first outcome comparison is interpreted.

---

# 12. Primary Outcome Metrics

For each predefined downstream target, record:

## Peak response

Maximum absolute target response during the post-intervention measurement window.

## Integrated response

Integrated absolute response over the post-intervention window.

This captures effects not represented by a single peak.

## Response latency

Time from the predefined intervention onset to the first qualifying downstream response.

## Peak-frame shift

Difference between intervention and control peak timing.

## Spike count

Where the target uses spiking telemetry, compare downstream spike counts.

## Effective activity

Compare recorded effective activity where available.

---

# 13. Ensemble-Level Metrics

For experiments involving responder-associated causal sources, also record:

- all nine responder values
- maximum responder value
- responder rank ordering
- number of responders measurably changed relative to control
- total responder-ensemble activity

These metrics are secondary to the predefined source → target test.

A large ensemble effect does not substitute for failure of the primary target prediction.

---

# 14. Effect Direction

For silencing and attenuation experiments, the preregistered primary prediction is:

**downstream target response decreases relative to matched control**

A response increase may still be scientifically interesting but does not count as confirmation of the primary directional hypothesis.

Unexpected directional effects must be reported as such.

They must not be relabeled as confirmation after the result is known.

---

# 15. Dose-Response Test

For nodes receiving the attenuation series:

- 0% attenuation / sham
- 25%
- 50%
- 75%
- 100%

the downstream target will be evaluated for an ordered relationship between intervention magnitude and response.

No assumption of strict linearity is required.

However, a stronger intervention producing systematically weaker downstream activity provides stronger intervention evidence than a single binary comparison.

The dose-response analysis is secondary unless explicitly designated primary for an experiment before execution.

---

# 16. Replication

A single intervention run is insufficient for MQ-5 acceptance.

Where the system is deterministic under a fixed seed and configuration:

- exact reruns must reproduce the same result.

Where randomness exists:

- multiple predefined seeds must be used.

The seed set must be frozen before aggregate results are interpreted.

The intervention harness must record every seed used.

---

# 17. Configuration Separation

MQ-5 must maintain explicit separation between:

## Scientific configuration

Defines the biological/computational model.

## Experiment configuration

Defines:

- target
- intervention type
- intervention magnitude
- timing
- control
- measurement window
- seed

## Runtime configuration

Defines machine/runtime details such as:

- Habitat
- future workstation
- cloud runtime
- CPU/GPU execution environment

Runtime configuration must not alter scientific semantics.

---

# 18. Required Run Metadata

Every MQ-5 run artifact must record at minimum:

- MQ-5 schema version
- experiment ID
- baseline artifact version
- intervention target model index
- intervention type
- intervention magnitude
- intervention start
- intervention end
- control type
- random seed where applicable
- runtime profile
- scientific configuration identifier
- experiment configuration identifier
- timestamp
- software commit
- downstream target
- outcome metrics

---

# 19. Artifact Policy

MQ-5 results must be written as new versioned artifacts.

Suggested artifact family:

`mq5-intervention-<experiment>-v1.json`

and, where dense numerical data is required:

`mq5-intervention-<experiment>-v1.npz`

Summary artifacts must identify the raw run artifacts from which they were derived.

No frozen MQ-1 through MQ-4 artifact may be overwritten.

---

# 20. Primary Acceptance Logic

For each source → target experiment, classify the outcome using the predefined intervention/control comparison.

## Supported intervention effect

The predicted downstream target changes in the preregistered direction relative to the required control and the effect is reproducible under the protocol.

## No supported intervention effect

The predefined downstream target does not show a reproducible directional change relative to control.

## Opposite-direction effect

The predefined target shows a reproducible change opposite to the preregistered direction.

This is reported separately and is not counted as confirmation.

## Inconclusive

The experiment fails a required control, reproducibility requirement, artifact-integrity requirement, or implementation validation.

Inconclusive results must not be converted into positive or negative causal conclusions.

---

# 21. MQ-5 Phase-Level Success Criteria

MQ-5 is not required to make every preserved MQ-3 causal edge survive intervention testing.

The experiment is successful if it produces a valid, reproducible intervention dataset capable of distinguishing:

- supported intervention effects,
- unsupported effects,
- opposite-direction effects,
- inconclusive experiments.

Scientific value comes from the controlled result, not from maximizing confirmations.

---

# 22. MQ-5.2 Entry Gate

Implementation of the intervention harness may begin only after this MQ-5.1 protocol is committed.

MQ-5.2 must provide:

- baseline execution
- zero-effect sham execution
- node-targeted intervention
- configurable attenuation
- timing control
- reproducible configuration
- versioned artifact output
- invariant validation

Before running the full causal set, MQ-5.2 must demonstrate that:

1. baseline reproduces the expected state,
2. sham matches baseline within the model's deterministic/stochastic expectations,
3. a deliberately applied intervention is actually present in the resulting telemetry,
4. frozen source artifacts remain unchanged.

---

# 23. Neuroscope Integration

MQ-5 intervention artifacts may later be visualized in Neuroscope.

Potential visualization includes:

- baseline vs intervention replay
- intervention target highlighting
- downstream difference visualization
- responder delta traces
- control comparison
- intervention timing overlays

This belongs to a later MQ-5 stage.

Neuroscope remains read-only.

It must not execute interventions.

---

# 24. Interpretation Guardrails

MQ-5 must not:

- change a hypothesis after viewing results
- choose control nodes based on favorable outcomes
- adjust thresholds after seeing results
- promote topology fallback coordinates to anatomical evidence
- treat visualization as proof
- overwrite frozen experimental artifacts
- hide failed or opposite-direction interventions
- interpret every system-wide change as target-specific evidence
- assign financial meaning to neural activity

---

# 25. Pre-Registered Showcase Experiments

The following experiments are designated before MQ-5 execution for detailed reporting.

## Showcase A — Direct responder pathway

`43417 → 656`

Why selected:

- direct frozen causal edge
- responder 656 has a clear recorded peak at frame 165
- causal evidence is associated with frame 145

Primary question:

Does perturbing model 43417 reduce the later response of model 656 relative to sham?

---

## Showcase B — Multi-hop pathway

`56393 → 68045 → 1273`

Why selected:

- only explicit two-hop chain in the accepted frozen causal graph
- supports both upstream and intermediate intervention tests

Primary questions:

1. Does perturbing 68045 reduce downstream model 1273?
2. Does perturbing 56393 reduce activity reaching 68045?
3. Does upstream perturbation subsequently affect 1273?

The three questions are evaluated separately.

---

## Showcase C — Convergent responder

`44274 → 55`

`55925 → 55`

Why selected:

- two preserved inputs converge on one frozen responder

Primary questions:

1. What is the effect of perturbing 44274 alone?
2. What is the effect of perturbing 55925 alone?
3. What is the effect of perturbing both together?

No assumption of additive or synergistic behavior is preregistered.

---

# 26. Protocol Freeze

Once this document is committed, substantive changes to:

- hypotheses
- primary target mappings
- intervention classes
- required controls
- primary metrics
- outcome classification logic

must be recorded as an explicit protocol amendment.

The original protocol must remain recoverable from Git history.

No protocol amendment may be presented as though it preceded results already observed.

---

# 27. MQ-5.1 Decision

**MQ-5.1 defines the experimental protocol only.**

No MQ-5 intervention result exists at the time of protocol freeze.

The next stage is:

**MQ-5.2 — Intervention Harness**

The order is deliberate:

**Evidence → Protocol → Intervention → Measurement → Interpretation**

**Anatomy. Evidence. Causality. Next.**
