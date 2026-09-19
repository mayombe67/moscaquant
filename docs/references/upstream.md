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

