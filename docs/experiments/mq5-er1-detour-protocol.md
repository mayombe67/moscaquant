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

## Instrumentation amendment 1 — read-only dynamic trace plumbing

The frozen MQ-3.2 physiology runtime already exposes a `synaptic_modifier`
hook after effective presynaptic activity has been computed and after ordinary
connectome aggregation, but before the remainder of the frozen voltage update.

DETOUR will use that hook only as a read-only observer.

The initial instrumentation module:

`brain/mq5_er1_detour_trace.py`

provides:

- deterministic construction of a bounded incoming-edge topology cone;
- read-only recording of effective presynaptic activity;
- per-edge contribution computed as frozen connectome weight times effective
  presynaptic activity;
- the postsynaptic aggregate visible at the hook;
- post-step voltage/spike snapshots for explicitly selected neurons.

The observer must return the supplied synaptic array unchanged.

This amendment does **not** freeze or execute the DETOUR candidate-selection
rule. In particular it does not freeze:

- backward-cone hop depth for the full experiment;
- candidate score;
- candidate ranking;
- candidate cap;
- tie handling;
- focused/diffuse classification thresholds.

Those remain intentionally unresolved until trace feasibility and exact
observer neutrality are tested on synthetic/toy data and bounded non-result
benchmarks.

No frozen A/C neural outcome may be inspected through this instrumentation
before those rules are subsequently frozen.

## Instrumentation amendment 2 — candidate rule freeze

Before any full frozen A/C DETOUR outcome is inspected, the candidate-generation
rule is frozen as follows.

### Search depth

The dynamic search space is the deterministic incoming-edge cone extending at
most **3 directed synaptic hops backward** from each frozen responder target.

This is a bounded local mechanism search, not an unrestricted connectome-wide
path discovery.

### Temporal window

For each affected responder, only dynamic edge contributions from frame 0
through that responder's **C-BASELINE first-positive onset, inclusive**, may
contribute to candidate scoring.

Post-onset activity cannot promote a candidate.

### Eligibility

A directed edge is eligible only when both are true within the frozen temporal
window:

1. its time-resolved dynamic contribution differs between A-BASELINE and
   C-BASELINE by more than `1e-12` in integrated L1 magnitude; and
2. it carries more than `1e-12` integrated absolute dynamic contribution in
   C-LESION13.

Thus static graph strength alone cannot create a candidate.

### Discovery score

For each eligible edge:

`score = L1(C-BASELINE - A-BASELINE) × L1(C-LESION13)`

where each L1 term is integrated over frames 0 through the target's C-baseline
onset, inclusive.

This score is a discovery heuristic only. It does not estimate causal effect
size.

### Ranking and cap

For each affected responder independently:

1. descending discovery score;
2. fewer backward hops;
3. lower postsynaptic model index;
4. lower presynaptic model index.

Exactly the first **5** candidates are retained when at least five exist.

This ordering is also the frozen tie rule.

### Discovery family classification

- `NO_CLEAR_DETOUR_CANDIDATES`: no eligible candidate for any affected target.
- `FOCUSED_DETOUR_CANDIDATES`: at least one exact directed edge appears in the
  retained top-5 candidate lists for at least **3 of the 5** affected targets.
- `DIFFUSE_DETOUR_CANDIDATES`: one or more eligible candidates exist, but the
  focused recurrence rule is not met.

These labels are descriptive discovery outputs only.

### Confirmation boundary

No DETOUR score, recurrence count, or family label establishes necessity or
sufficiency.

All promoted candidates remain hypotheses until preregistered intervention in
MQ-5.ER.2 — ROADBLOCK.
