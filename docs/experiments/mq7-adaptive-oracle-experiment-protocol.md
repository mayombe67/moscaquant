# MQ-7 — Adaptive Oracle Experiment Protocol

Status:

**PRE-REGISTERED / ADAPTIVE RUNS NOT YET GENERATED**

## Research question

Does protocol-controlled SC-03 plasticity produce reproducible changes in
MoscaQuant behavior relative to a matched non-learning Oracle condition?

## Conditions

### O1 — Static Oracle control

- Oracle interpretation enabled
- D6 enabled
- SC-03 may be selected
- `plasticity_active = false`
- SC-03 therefore returns `NOT_APPLICABLE`
- all other D6 conditions operate normally

### O2 — Adaptive Oracle

- same Oracle logic
- same D6 selector
- same seeds
- same market inputs
- same runtime-independent scientific configuration
- SC-03 protocol explicitly enabled
- validated credit assignment active
- validated persistent plasticity active

The only intended difference between O1 and O2 is adaptive SC-03 plasticity.

## Matching

Each O1/O2 pair must use identical:

- experiment seed;
- session sequence;
- market replay/input;
- connectome artifact;
- sensory configuration;
- readout configuration;
- D6 selector version;
- Oracle version;
- WARDEN policy.

Hardware/runtime profile may differ only when reproducibility has already been
demonstrated and must not alter scientific behavior.

## Primary outcomes

Primary outcomes are neural and behavioral, not financial.

Measure:

1. number of SC-03 selections;
2. number of applicable SC-03 events;
3. number of unique-credit updates;
4. number of ambiguous-credit blocks;
5. number of no-eligible-pathway blocks;
6. distribution of active plasticity multipliers;
7. persistence and recovery across sessions;
8. changes in predefined readout metrics relative to matched O1;
9. divergence in Oracle proposals relative to matched O1.

## Secondary outcomes

May include:

- D6 condition frequencies;
- intervention carryover;
- state-hash divergence;
- candidate-state changes;
- Panopticon-visible behavior changes.

## Financial outcomes

Financial performance may be recorded descriptively but is not a primary
scientific endpoint for this phase.

No claim of financial utility is preregistered.

## Hypotheses

H1:
O2 will produce measurable neural-state divergence from matched O1 after
eligible SC-03 updates.

H2:
O2 divergence will persist across sessions according to the frozen plasticity
state and recovery rules.

H3:
Runs without applicable SC-03 updates should remain substantially aligned
with matched O1 aside from other independently randomized D6 perturbations.

No hypothesis of improved profitability is preregistered.

## Controls

Required:

- O1 matched control;
- identical seeds;
- identical market inputs;
- frozen artifact hashes;
- deterministic replay;
- checked-in SC-03 default config remains disabled;
- explicit experiment config required for O2.

## Stop conditions

Abort the experiment if:

- protocol/version mismatch occurs;
- state-hash validation fails;
- persisted plasticity fails replay;
- baseline connectome changes;
- WARDEN boundary is violated;
- runtime profile changes scientific outputs unexpectedly.

## Interpretation limits

Observed adaptation supports modeled plasticity effects within MoscaQuant.

It does not establish:

- biological learning in living Drosophila;
- consciousness;
- emotion;
- financial intelligence;
- profitable trading ability.

Panopticon may provide humorous interpretation only after the underlying
scientific event and provenance are preserved.
