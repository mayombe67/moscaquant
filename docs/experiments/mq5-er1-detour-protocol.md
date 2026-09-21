# MQ-5.ER.1 — DETOUR

**Codename:** DETOUR

**Status:** PRE-REGISTERED / DISCOVERY ONLY / NO CAUSAL CLAIM AUTHORIZED

**Parent experiment:** MQ-5.ER — Encoding Robustness

**Parent result artifact SHA-256:**

`737a316a98d91b95dc1a5fe3ac25e7bf229447ae422ecd23ecf39ea8d4f6bb39`

**Financial semantics:** NOT ASSIGNED

## Question

When entropy-dependent temporal jitter is removed, all nine accepted responders
remain present, but five targets no longer depend on the previously frozen
13-edge lesion bundle.

MQ-5.ER.1 asks:

> Where does the Arm-C response begin to diverge from the accepted Arm-A causal
> route organization, and which alternative dynamic routes become plausible
> candidates for later prospective testing?

This is a **discovery experiment**. It may identify candidate detours. It may
not promote those candidates into causal mechanisms.

## Frozen target set

Primary affected targets are exactly:

`55, 92, 656, 126002, 137122`

These are the five MQ-5.ER Arm-C targets for which the frozen 13-edge bundle
lesion produced no onset delay or within-window response loss.

The other four accepted responders:

`51, 129, 317, 1273`

form an internal retained-dependency comparison set.

No post-hoc responder expansion is allowed.

## Frozen conditions

Exactly three neural conditions are compared:

1. **A-BASELINE**
   - original frozen MQ-5.ER Arm-A encoding
   - original connectome
   - no lesion

2. **C-BASELINE**
   - MQ-5.ER Arm-C encoding
   - entropy-dependent temporal jitter multiplier = `0.0`
   - original connectome
   - no lesion

3. **C-LESION13**
   - identical Arm-C encoding
   - same frozen 13-edge lesion bundle used by MQ-5.ER
   - no additional lesions

No other encoding arm is part of DETOUR v1.

## Frozen runtime

DETOUR SHALL reuse the same frozen neural runtime, topology loading, sensory
gain, 192-frame observation window, responder universe, and Arm-C stimulus
construction already accepted by MQ-5.ER.

DETOUR SHALL NOT retune:

- release gain;
- sensory gain;
- thresholds;
- membrane constants;
- responder definitions;
- lesion strength;
- observation length;
- encoding parameters;
- connectome weights;
- stimulus energy normalization.

## Discovery trace

For every frame and neuron needed by the trace implementation, record enough
state to distinguish at least:

- membrane/activity state;
- incoming effective synaptic contribution;
- first frame at which C-BASELINE differs from A-BASELINE;
- first frame at which C-LESION13 differs from C-BASELINE;
- upstream contributors associated with those first divergences.

The implementation MAY use a bounded candidate subgraph or event-driven trace
for tractability, but the candidate-generation rule must be frozen and tested
before any DETOUR result-bearing execution.

## Candidate-detour definition

A neuron or directed edge may become a DETOUR candidate only if it satisfies
the frozen implementation's prospective trace rule.

The trace rule must use dynamic timing/contribution evidence, not static graph
strength alone.

At minimum, a promoted candidate must be associated with one or more of the
five primary affected targets and occur no later than that target's Arm-C
baseline first-positive onset.

Candidate ranking, tie handling, and maximum candidate count must be frozen
before result execution.

## Required comparisons

DETOUR must explicitly separate:

### Encoding divergence

`A-BASELINE` versus `C-BASELINE`

This localizes dynamics changed by removing entropy-dependent jitter.

### Lesion bypass divergence

`C-BASELINE` versus `C-LESION13`

This localizes dynamics that remain capable of supporting the response after
the old 13-edge bundle is removed.

A candidate is more interesting if it is consistent with both comparisons,
but DETOUR SHALL NOT call any candidate causal.

## Negative / retained-dependency comparison

The four targets that remain sensitive to the 13-edge bundle in Arm C:

`51, 129, 317, 1273`

must be traced under the same machinery.

This guards against a candidate rule that simply labels generic Arm-C
differences everywhere.

## Output classes

DETOUR may output only:

- `NO_CLEAR_DETOUR_CANDIDATES`
- `DIFFUSE_DETOUR_CANDIDATES`
- `FOCUSED_DETOUR_CANDIDATES`

These are discovery labels, not causal classifications.

The exact quantitative classification thresholds must be frozen in the
implementation amendment before result execution.

## Prohibited claims

DETOUR alone cannot establish:

- that any candidate edge or neuron is necessary;
- that any candidate route replaces the 13-edge bundle;
- that rerouting is biological;
- that the network understands entropy;
- that the discovered path generalizes beyond Arm C;
- financial, predictive, or trading semantics.

## Required next experiment

Any candidate route promoted from DETOUR must be frozen before intervention in
a separate confirmatory experiment:

**MQ-5.ER.2 — ROADBLOCK**

ROADBLOCK will be the first experiment allowed to make a prospective causal
claim about DETOUR candidates.

Discovery and confirmation must not be the same calculation grading itself.

## Execution gate

Result-bearing execution is disabled in the initial DETOUR freeze.

The initial implementation phase may:

- build trace instrumentation;
- build deterministic synthetic tests;
- verify exact replay of A and C stimuli;
- verify trace capture on toy graphs;
- benchmark bounded trace storage;
- inspect schema/shape/runtime feasibility.

It may not inspect DETOUR neural outcomes on the frozen full experiment until
the candidate-generation rule, ranking rule, candidate cap, and result schema
are frozen.

## Parent fact motivating DETOUR

MQ-5.ER Arm C retained all nine accepted responders while the frozen 13-edge
lesion bundle ceased to affect targets:

`55, 92, 656, 126002, 137122`

This motivates DETOUR. It does not pre-decide the mechanism.

**Science first. Lulz close second.**
