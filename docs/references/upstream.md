# Upstream References

MoscaQuant uses public MaleCNS research data and studies existing open-source
implementations to avoid unnecessarily reimplementing solved infrastructure.

## fly.ai / FlyBrain

Repository:
https://github.com/alextitonis/fly.ai

Reference commit:

    5ec5e544468894d13896eb09ea2a960eafae1101

License: MIT

MoscaQuant's initial structural baseline was informed by the FlyBrain MaleCNS
builder, including:

- superclass-based neuron retention
- deterministic bodyId ordering
- sparse graph construction
- neurotransmitter-derived sign assumptions
- incoming absolute-weight normalization
- known sensory and motor population mappings

MoscaQuant independently verifies its source data, population counts, graph
invariants, processed artifacts, and provenance.

The upstream implementation is a reference, not a runtime dependency.

## Attribution

Additional research projects and upstream implementations used during
development will be recorded here and acknowledged in the public Panopticon.

## Community research prompt — route compensation

In September 2026, external technical feedback on the public Neuroscope
example raised a concrete methodological question:

Could partially redundant downstream routes compensate for one another in a
way that makes single-route ablations misleading?

That question directly motivated:

- MQ-7.18 — Pairwise Route Interaction / Compensation
- MQ-7.19 — Conditional Pairwise Contribution

The external reviewer supplied the research question only.

MoscaQuant independently defined the experimental design, frozen pair set,
independent-residual null, controls, execution, acceptance logic, and claim
boundaries before inspecting the corresponding outcomes.

**Credit:** Reddit community reviewer, September 2026.

If a stable public username and comment permalink are retained later, they may
be added here without changing scientific provenance.

### r/quant moderation as a standards prompt

A separate r/quant moderation event emphasized rigorous statistical analysis,
theoretical grounding, scaling considerations, and professional relevance for
quantitative-finance discussion.

That moderation feedback influenced presentation and validation standards
only. It is not scientific evidence and did not determine any experimental
result.

Internal project nickname: **the r/quant neckbeards problem**.


## Community research prompt — pairwise route compensation

In September 2026, a Reddit community reviewer examining the public
Neuroscope example asked whether partially redundant downstream routes could
compensate for one another, making single-route ablations incomplete.

That question directly motivated:

- MQ-7.18 — Pairwise Route Interaction
- MQ-7.19 — Conditional Pairwise Contribution

The reviewer supplied the research question. MoscaQuant independently defined
the frozen pair set, independent-residual null, controls, metrics, execution,
acceptance logic, and claim boundaries before inspecting the corresponding
outcomes.

**Credit:** Reddit community reviewer, September 2026.

If a stable username and public comment permalink are retained later, they may
be added here without changing scientific provenance.

### r/quant moderation as a standards prompt

A separate r/quant moderation event emphasized rigorous statistical analysis,
theoretical grounding, scaling considerations, and professional relevance for
quantitative-finance discussion.

That moderation feedback influenced presentation and validation standards
only. It is not scientific evidence and did not determine any experimental
result.

Internal project nickname: **the r/quant neckbeards problem**.

## Runtime portability, embodiment, and adjacent trading watch — 2026-09-19

These projects are engineering/benchmark references, not scientific evidence for MoscaQuant claims.

### FlyBrain / flybrain provenance patterns

Useful patterns include deterministic experiment entry points, source/output hashes, explicit dataset provenance, and separation of real-data experiments from synthetic fixtures.

References:
- https://github.com/mehrantsi/flyBrain
- https://github.com/Imperol3/flybrain

### soup-connectome

Reference: https://github.com/MakazhanAlpamys/soup-connectome

Use: backend-portability and parity benchmark only. MoscaQuant does not adopt its fixed-point numerical model as scientific dynamics.

### FlyDrones

Reference: https://github.com/SpikeCalls/FlyDrones

Use: inspect camera/sensory-to-connectome and descending-neuron interface patterns. Engineered drone-control semantics are not imported.

### Closed-Loop Fly

Reference: https://github.com/ZeroXClem/closed-loop-fly

Use: inspect compound-eye/optic-lobe/MaleCNS integration, descending-neuron inspection, parity benches, and especially documented readout artefacts.

### flyquant

Reference: https://github.com/0xbuilder1/flyquant

Use: adjacent trading comparator. MoscaQuant does not adopt its execution or leverage design. Future comparison should focus on controls, provenance, causal evidence, held-out financial validation, adapter boundaries, and independent WARDEN-01 containment.

### MoscaQuant adoption decision

ADOPT:
- hashable provenance manifests;
- explicit empirical/surrogate/synthetic classes;
- executable runtime-parity acceptance;
- separately hashable adapter boundaries.

BENCHMARK:
- backend portability;
- sensory and DN inspection interfaces;
- adjacent connectome-to-finance claims.

DO NOT ADOPT:
- another project's scientific dynamics merely for portability;
- another project's engineered motor/trading mapping;
- financial success as evidence of biological validity.

## MaleCNS / FlyWire comparative connectomics — MQ-002 // LILITH

MQ-002 // LILITH is a provisional comparative biological control built from
independent published female-brain connectome data, not from a transformed or
derived copy of MQ-001 / MORTY.

### MaleCNS

Berg, S., Beckett, I. R., Costa, M., Schlegel, P., Januszewski, M., Marin,
E. C., Nern, A., Preibisch, S., Qiu, W., Takemura, S.-Y., et al. (2026).
**Sexual dimorphism in the complete Drosophila male central nervous system
connectome.** *Cell* 189(18), 5504-5526.e15.

DOI: https://doi.org/10.1016/j.cell.2026.08.015

Project companion data:

- https://github.com/flyconnectome/2025malecns

MoscaQuant uses the official MaleCNS/FlyWire comparison products for MQ-002
qualification, including:

- `mcns_fw_edge_comp_mappings.json` — neuron-to-cross-matched-label assignments;
- `mcns_fw_edge_comp.feather` — aligned male/female central-brain type-to-type
  edge weights and comparison annotations.

The published aligned-edge product excludes connections made within the VNC
portion of MaleCNS. MoscaQuant therefore does not infer or manufacture a female
VNC counterpart.

### FlyWire female adult brain

Dorkenwald, S., Matsliah, A., Sterling, A. R., Schlegel, P., Yu, S.-C.,
McKellar, C. E., Lin, A., Costa, M., Eichler, K., Yin, Y., et al. (2024).
**Neuronal wiring diagram of an adult brain.** *Nature* 634, 124-138.

DOI: https://doi.org/10.1038/s41586-024-07558-y

FlyWire provides the independently reconstructed adult female *Drosophila*
brain connectome underlying the female side of the published MaleCNS/FlyWire
comparison used to qualify MQ-002 // LILITH.

### MoscaQuant use and claim boundary

MQ-001 / MORTY and MQ-002 // LILITH originate from separate biological
connectome resources. LILITH is not a clone, transformation, or female-derived
version of MORTY.

The initial MQ-002 program is restricted to traceable cross-matched anatomy and
explicitly qualified comparison products. SHUFFLED MOSCA remains a separate
randomized-topology control family.

A computational difference between MQ-001 and MQ-002 does not by itself
establish a biological sex mechanism, intelligence difference, behavioral
generality, market skill, or financial usefulness.

MoscaQuant is an independent experimental project and is not affiliated with
the MaleCNS, FlyWire, or FlyWire Consortium teams.
