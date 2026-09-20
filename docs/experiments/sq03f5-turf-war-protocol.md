# SQ-03F.5 — TURF WAR

**Status:** FROZEN — NOT YET EXECUTED

## Question

Do the shared high-interest sources established by the preceding SQ-03F
experiments converge downstream into common neural territory, or do they
primarily influence separate downstream crews?

SQ-03F.5 is a downstream-territory convergence test.

It does not re-test whether the sources qualify as hotspots, capos, or made
sources. Those upstream classifications are inherited from the frozen prior
SQ-03F record.

## Scientific position

SQ-03F.4 — THE SIT-DOWN established the shared-source relationship used to
define the eligible source set for this experiment.

SQ-03F.4 did not determine whether those sources converge onto common
downstream territories.

SQ-03F.5 tests that next question prospectively.

## Frozen source eligibility

The eligible source set SHALL be derived only from the authoritative frozen
SQ-03F.4 result artifact.

No source may be added because it looks interesting during SQ-03F.5 analysis.

No source may be removed because its downstream behavior weakens the result.

If the frozen SQ-03F.4 artifact does not expose an unambiguous eligible shared
source set, SQ-03F.5 SHALL fail closed rather than infer one from narrative
text.

## Territory definition

A source's downstream territory is the set of eligible downstream nodes
reachable under the frozen traversal rule used by the analyzer.

The first result-bearing analyzer implementation SHALL freeze and record:

- traversal direction;
- maximum path depth;
- edge eligibility rule;
- node eligibility rule;
- whether repeated nodes are collapsed;
- whether source nodes themselves are excluded;
- treatment of cycles;
- any edge-weight or effect-strength threshold.

These parameters SHALL be fixed before the observed convergence statistic is
interpreted.

Changing a territory-definition parameter after inspecting the observed
classification requires a new experiment/version rather than an in-place
rerun.

## Primary statistic

The primary statistic SHALL quantify overlap among downstream territories of
the frozen eligible sources.

The analyzer SHALL record enough component counts to reconstruct the statistic.

The statistic MUST be symmetric with respect to source ordering.

A result SHALL NOT be classified from a hand-selected visualization.

## Null model

The confirmatory comparison SHALL use a matched randomization null.

Randomized source sets MUST preserve the number of eligible sources and SHALL
be sampled from the same frozen source universe used by the applicable
SQ-03F analysis.

Matching constraints used by the null MUST be declared before the observed
classification is inspected.

The randomization count SHALL be **10,000**.

The base randomization seed SHALL be **314159**.

If independent randomization streams are required, their deterministic
derivation from the base seed SHALL be recorded explicitly in the result
artifact.

## Classification

The analyzer SHALL compare the observed territory-overlap statistic with the
frozen matched-null distribution.

The result document SHALL report:

- observed overlap statistic;
- null summary;
- empirical tail probability or equivalent frozen rank measure;
- effect-size summary;
- source-level territory sizes;
- pairwise overlap components where applicable;
- randomization count;
- actual randomization seed or derived stream seeds;
- exact input artifact references.

The experiment SHALL distinguish among at least these interpretations:

1. evidence of greater-than-null downstream convergence;
2. no clear evidence of unusual downstream convergence;
3. evidence more consistent with separated downstream territories.

The exact numeric classification boundaries MUST be frozen in the analyzer
contract before result interpretation.

## Claim boundary

A positive result would support a statement about downstream convergence
within the frozen MoscaQuant model and the frozen SQ-03F source set.

It would not establish:

- biological gang-like organization;
- anatomical territory in the organism;
- sex-specific neural organization;
- financial usefulness;
- trading usefulness;
- generalization beyond the frozen model and eligible source set.

A null or separated result would not invalidate the preceding SQ-03F
hotspot/source findings. It would only constrain the downstream-territory
interpretation.

## Separation from prior experiments

SQ-03F.1 asks whether network-position features relate to the observed
structure.

SQ-03F.2 tests source-strength robustness.

SQ-03F.3 tests repeat hotspot/shared-source structure under stratified
randomization.

SQ-03F.4 — THE SIT-DOWN records the shared-source relationship and its
prospective interpretation boundary.

SQ-03F.5 — TURF WAR asks whether those frozen shared sources converge into
common downstream territory.

## Execution boundary

This document freezes the scientific question and the high-level confirmatory
design.

Creating this protocol does not execute SQ-03F.5.

No SQ-03F.5 result artifact exists merely because this protocol is committed.

The result-bearing analyzer and its exact territory/classification contract
must be reviewed and frozen separately before execution.
