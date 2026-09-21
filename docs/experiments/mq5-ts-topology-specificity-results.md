# MQ-5.TS — Topology Specificity Results

## Status

**COMPLETE — TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED**

## Purpose

MQ-5.TS tested whether the accepted MoscaQuant response depends on the
specific frozen MaleCNS wiring arrangement, rather than being recoverable from
coarser or tightly matched graph statistics alone.

This was a model-level topology-specificity benchmark.

Financial semantics were not assigned.

## Frozen arms

- **Arm A — original MaleCNS topology**
- **Arm B — SHUFFLED MOSCA v2**
- **Arm C — strict matched-topology null**
- **Arm D — accepted MQ-3.2 first-onset causal-route lesion**

Arm C preserved the preregistered structural constraints, including exact
directed degree, transmitter-sign structure, retinal-origin interface,
postsynaptic signed weight structure, incoming absolute normalization, total
edge count, duplicate-edge exclusion, and no-new-self-edge semantics.

## Deterministic positive-control gate

Before randomized interpretation:

- Arm A duplicate replay was exact;
- Arm D duplicate replay was exact;
- Arm A retained all 13 / 13 frozen first-onset causal edges;
- Arm D retained 0 / 13;
- Arm D delayed all 9 / 9 accepted responder onsets while retaining the same
  nine-responder identity.

The randomized ensemble was permitted only after this gate passed.

## Randomized ensemble

### Arm B

- expected seeds: **20**
- completed seeds: **20 / 20**
- exact Arm-A response-pattern reproductions: **0 / 20**

### Arm C

- expected seeds: **20**
- completed seeds: **20 / 20**
- exact Arm-A response-pattern reproductions: **0 / 20**

No failed randomized seed was replaced.

No early stopping was used.

## Frozen exact-reproduction definition

An Arm C seed counted as an exact response-pattern reproduction only if all
three preregistered checks matched Arm A:

1. exact responder-set identity;
2. exact first-onset vector over the accepted responder universe;
3. normalized responder-voltage-fingerprint L2 distance <= `1e-9`.

Observed exact reproductions:

**0 / 20**

## Preregistered classification

The frozen rule classified Arm C as:

- `TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED` for 0–1 exact reproductions;
- `MIXED TOPOLOGY SPECIFICITY` for 2–9;
- `STRICT NULL FREQUENTLY REPRODUCES RESPONSE` for 10–20.

Observed classification:

**TOPOLOGY-SPECIFIC RESPONSE PATTERN SUPPORTED**

## Interpretation

Within the frozen MoscaQuant computational model and the tested null families,
the accepted response pattern was not recovered by either:

- the existing SHUFFLED MOSCA v2 control; or
- the stricter Arm C topology null that preserved the preregistered local and
  global structural statistics.

The Arm C result narrows the explanation beyond the preserved graph statistics
tested here. Under this benchmark, the specific arrangement of directed
MaleCNS connections contributed materially to the accepted response pattern.

This is stronger than showing only that an unconstrained or destructive shuffle
breaks the response.

## What this does not establish

MQ-5.TS does **not** establish:

- that the frozen MaleCNS topology is uniquely optimal;
- that every appropriate topology/null-model family has been excluded;
- biological causal equivalence in living Drosophila;
- natural fly behavior;
- general sensory-encoding independence;
- market prediction;
- trading usefulness;
- profitability.

The supported scope is:

**topology-specificity within the frozen MoscaQuant simulation under the
preregistered Arm B and Arm C null families.**

## Provenance

Result artifact:

`/home/wil/moscaquant-data/experiments/mq5-ts-topology-specificity-v1.json`

Artifact SHA-256:

`903bff56fba99580b93db2a875f4c1996e3976a018bb26d306ef61baf73b2811`

Frozen randomized execution commit:

`aa2418e3661ff5b5a8e1f3c4e580eedf29d997c8`

A/D gate SHA-256:

`ef5cb45202327af4d82eb633db5c810ffb238a56c8e32875afb3960e0bb5674f`

Financial semantics used:

**NO**

Biological causality claimed:

**NO**
