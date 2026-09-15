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
