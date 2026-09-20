# SQ-03B — FIND THE DIFFERENCE

## Mechanistic Localization Protocol

**Status:** FROZEN BEFORE LOCALIZATION EXECUTION  
**Class:** Post-hoc mechanistic follow-up with preregistered localization rules  
**Parent:** SQ-03A — THE OTHER FLY

## Question

Which already-matched central-brain edge-weight differences are locally
responsible for the SQ-03A downstream response differences?

SQ-03B is explicitly a follow-up to an observed SQ-03A result. It is not an
independent confirmatory experiment.

## Frozen follow-up inputs

SQ-03A reported a peak-voltage anchor rank-order change for exactly four
preregistered inputs:

- `TmY14`
- `LPLC2`
- `AVLP234`
- `AVLP435`

Those four labels are the complete SQ-03B input set.

No other SQ-03A input may be added after SQ-03B localization outputs are seen.

## Frozen output anchors

The SQ-03A output anchors remain unchanged:

- `DNc02`
- `DNp27`
- `DNp30`

No new output anchor may be added after localization begins.

## Frozen matched graph

Use the same SQ-03A graph:

- `verdict_corr == "isomorphic"`
- `weight_m > 0`
- `weight_f > 0`
- identical node identities;
- identical edge set;
- MORTY uses `weight_m`;
- LILITH uses `weight_f`.

No missing edge may be inferred.
No optic-lobe anatomy may be reconstructed.

## Candidate-edge rule

Candidate edges are selected structurally before any SQ-03B counterfactual
results are generated.

For each frozen input-anchor pair, include a matched edge only if:

1. it lies on at least one directed simple path from that input to that anchor;
2. the path contains no more than four edges;
3. its aligned male and female weights differ.

The union of these edges is the frozen SQ-03B candidate set.

Path membership is a topological selection rule. SQ-03B neural outcomes may
not be used to add, remove, or reorder candidates.

## Counterfactual localization

Each candidate edge is tested independently.

### MORTY counterfactual

Replace only that edge's `weight_m` with its `weight_f`.

Everything else remains identical to the accepted SQ-03A MORTY execution.

### LILITH counterfactual

Replace only that edge's `weight_f` with its `weight_m`.

Everything else remains identical to the accepted SQ-03A LILITH execution.

No two-edge or multi-edge combination search is permitted in SQ-03B.

## Primary localization metric

For the relevant frozen input and anchor:

> counterfactual anchor peak voltage minus the subject's unmodified SQ-03A
> baseline anchor peak voltage.

Secondary descriptive metrics are:

- integrated-positive-voltage change;
- first-positive-frame change.

No post-hoc numerical threshold will be introduced to manufacture a
"significant" edge.

An edge may be reported as a **model-level localization candidate** when its
single-edge equalization changes the corresponding anchor response in either
subject.

## Required controls

Before accepting localization output:

1. unmodified baseline replay must reproduce the corresponding SQ-03A result;
2. deterministic A/A replay must pass;
3. the candidate-edge set must be frozen before counterfactual execution;
4. runtime parameters must remain identical between subjects;
5. stimulus parameters must remain identical between subjects.

Any failure stops the run.

## Interpretation boundary

SQ-03B can identify where the frozen computational model is sensitive to
aligned male/female edge-weight differences.

That is not equivalent to showing that the same edge causes a biological sex
difference in a living fly.

The experiment does not establish:

- a biological mechanism;
- sex superiority;
- intelligence differences;
- general behavioral differences;
- market skill;
- profitability;
- financial usefulness.

SQ-03B does not alter WARDEN, ORACLE, Sugar Cube Protocol, FLYSWATTER PROTOCOL,
or any containment/reinforcement semantics.
