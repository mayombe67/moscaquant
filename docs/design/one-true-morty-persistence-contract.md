# One True Morty — Persistent Subject State Contract

Status: **DESIGN SCAFFOLD / NON-EXECUTABLE**

This document defines the future state-boundary model for persistent MQ-001
individual lineages.

It does not activate plasticity, alter checkpoints, or modify scientific runtime
behavior.

## Principle

Serializable state is not automatically persistent scientific state.

Any state capable of affecting future subject computation across a defined
persistence boundary must be explicitly classified.

## State classes

### IMMUTABLE_BASELINE

Shared scientific substrate that identifies the starting model.

Examples:

- MaleCNS structural connectome
- neuron identity mapping
- frozen runtime semantics
- immutable experiment configuration

This state is referenced by hash/version and is not rewritten by an individual.

### SUBJECT_PERSISTENT

State belonging to one experimental MQ individual and permitted to affect its
future computation across the frozen persistence boundary.

Potential examples, only when explicitly authorized by a future protocol:

- synaptic/plasticity overlays
- persistent scar/modulatory state
- recovery counters
- learned subject-specific parameters
- persistent eligibility state

A field is not included merely because an implementation can serialize it.

### EPISODE_LOCAL

State reset at the declared episode/session boundary.

Potential examples:

- membrane voltage
- current spike state
- refractory state
- transient activity traces
- transient modulation
- transient eligibility

A future protocol may promote a field from episode-local to subject-persistent
only prospectively.

### EXTERNAL_AUTHORITY

State that may affect what the subject is allowed to do but is not part of the
neural individual.

Examples:

- WARDEN state
- broker/account state
- financial limits
- containment authorization
- kill switches

This state must never be smuggled into a subject checkpoint as learned state.

### PRESENTATION_ONLY

State used to display or narrate the subject but not to determine scientific
behavior.

Examples:

- Panopticon cosmetics
- HR records
- achievements
- mood presentation
- lore
- Employee of the Month status

Presentation state does not become neural state.

## Lineage

Every persistent individual checkpoint must identify:

- subject ID
- parent checkpoint, if any
- immutable baseline identity
- scientific runtime/config identity
- persistent-state schema version
- hashes of persistent state
- experiment/experience lineage
- deterministic replay provenance where applicable

After an experimental fork, candidate individuals must not silently share
subject-persistent mutable state.

## One True Morty

"One True Morty" is a lineage/provenance designation for a promoted persistent
MQ-001 subject.

Promotion does not imply:

- biological individuality
- consciousness
- intelligence
- market skill
- profitability
- scientific superiority to controls

A One True Morty checkpoint must be complete with respect to every
protocol-defined state variable capable of affecting that subject's future
computation.

## Fail-closed rule

For every checkpoint field that can affect future computation, exactly one must
be true:

1. it is explicitly SUBJECT_PERSISTENT; or
2. it is explicitly reset at the persistence boundary.

Unclassified causal state invalidates the checkpoint as a complete persistent
individual.

Science first.

Lulz a very close second.
