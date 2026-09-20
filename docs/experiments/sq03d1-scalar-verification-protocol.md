# SQ-03D.1 — DOUBLE CHECK THE KNIFE

## Scalar Verification Protocol

**Status:** FROZEN BEFORE PANEL SELECTION  
**Class:** Confirmatory scalar verification follow-up  
**Parent:** SQ-03D — THE SAME KNIFE CUTS DIFFERENTLY

## Question

SQ-03D identified a long upper tail of paired-background context residuals from
the complete SQ-03B intervention census.

SQ-03D.1 asks:

> Do the strongest SQ-03D context-dependent pairs survive independent scalar
> re-execution of both MORTY and LILITH counterfactuals?

A frozen near-zero control panel is rerun in parallel.

## Selection source

The authoritative SQ-03D result artifact remains the controlling result.

Because that artifact stores the full summaries and top-100 ranking but not every low-tail row identity, **Amendment SQ-03D.1-A1** was frozen before panel selection. It permits deterministic replay of the already-frozen SQ-03D analysis against the exact same hashed SQ-03B ledger solely to recover complete row identities required by the precommitted low-tail selection rule.

The replay must reproduce:

- the authoritative SQ-03D global summary;
- the authoritative SQ-03D top-100 ranking;
- the exact SQ-03B ledger hash recorded by SQ-03D.

No neural dynamics are rerun.

No selection threshold, ranking rule, panel size, runtime mechanic, or acceptance criterion is changed by this amendment.

No candidate may be added manually.

No selected candidate may be substituted after execution begins.

## Upper-tail panel

Freeze **16 pairs** from the SQ-03D ranking:

1. integrated-positive-voltage context residual — descending;
2. peak-voltage context residual — descending;
3. integrated-positive-voltage total effect magnitude — descending;
4. edge ID — ascending.

Selection is stratified so every input contributes at least two upper-tail pairs
when the frozen ranking contains enough eligible observations.

The stratified allocation is deterministic:

1. rank all eligible pairs by the frozen upper-tail ranking;
2. seed the panel with the first two pairs for each input;
3. fill the remaining slots from the global ranking, skipping pairs already
   selected.

## Low-tail controls

Freeze **16 near-zero pairs** ranked by:

1. integrated-positive-voltage context residual — ascending;
2. integrated-positive-voltage total effect magnitude — ascending;
3. peak-voltage context residual — ascending;
4. edge ID — ascending.

Selection is stratified so every input contributes at least two low-tail
controls when possible.

The low-tail allocation is deterministic:

1. rank all eligible pairs by the frozen low-tail ranking;
2. exclude all upper-tail panel pairs;
3. seed the controls with the first two remaining pairs for each input;
4. fill the remaining slots from the global low-tail ranking, skipping pairs
   already selected.

Upper-tail and low-tail panel membership may not overlap.

## Scalar execution

Each selected pair requires two scalar counterfactual reruns:

- MORTY receives the LILITH edge weight;
- LILITH receives the MORTY edge weight.

Each subject counterfactual is executed independently through the original
scalar `HybridRuntime`.

The same SQ-03A/SQ-03B mechanics remain frozen:

- same matched graph;
- same normalization;
- same stimulus;
- same runtime parameters;
- same edge orientation;
- same single-edge equalization rule.

Exact A/A replay is required.

SQ-03A baseline replay is required.

## Reconstruction

For every selected pair, reconstruct from scalar results:

- `ΔM`
- `ΔL`
- integrated context residual
- integrated total effect magnitude
- integrated normalized asymmetry
- peak context residual
- peak total effect magnitude
- peak normalized asymmetry

These scalar reconstructions are compared directly with the corresponding
SQ-03D values.

## Numerical agreement

The already-frozen SQ-03B/SQ-03C engineering contract is reused:

- `rtol = 1e-6`
- `atol = 1e-7`

This tolerance is not chosen from SQ-03D.1 outcomes.

## Acceptance

The verification passes only if:

1. every selected upper-tail pair reproduces both subject counterfactuals;
2. every selected low-tail control reproduces both subject counterfactuals;
3. every A/A replay is exact;
4. every baseline replay is accepted;
5. the reconstructed SQ-03D metrics agree within the frozen numerical contract.

## Statistical boundary

SQ-03D.1 is a deterministic computational replication.

No p-value is generated from simulation rows.

The result does not establish a biological mechanism or a population-level
sex-difference statistic.

## Claim boundary

A passing SQ-03D.1 result supports only the statement that selected
model-level paired-background context effects survive an independent scalar
execution path.

It does not establish:

- a biological sex mechanism;
- organism-level behavior;
- population-level statistical significance;
- intelligence differences;
- market skill;
- profitability;
- financial usefulness.
