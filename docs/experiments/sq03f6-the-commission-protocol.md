# SQ-03F.6 — THE COMMISSION

**Status:** FROZEN — NOT YET EXECUTED

## Question

Is the greater-than-null downstream convergence established by SQ-03F.5
concentrated in a relatively small shared downstream core, or broadly
distributed across many downstream targets?

SQ-03F.6 is a downstream-target concentration test.

It does not retest whether the SQ-03F.4 shared sources converge downstream.
That question was frozen and answered by SQ-03F.5.

## Scientific position

SQ-03F.5 established that the 42 shared sources inherited from SQ-03F.4 have
greater-than-null overlap among their frozen two-hop downstream territories.

SQ-03F.5 did not determine whether that excess overlap is:

1. concentrated on a small group of repeatedly reached downstream targets; or
2. distributed across a broad population of downstream targets.

SQ-03F.6 tests that distinction prospectively.

## Frozen parent inputs

The observed source set SHALL be inherited directly from the authoritative SQ-03F.5 result artifact.

The downstream territory rule SHALL remain identical to SQ-03F.5:

- directed downstream traversal;
- maximum depth of two hops;
- source nodes excluded from their own territories;
- repeated nodes collapsed;
- cycles handled by visited-set collapse;
- same frozen conservative graph;
- same frozen candidate-source universe.

No source or downstream target may be added, removed, or redefined because it
appears interesting after inspection.

If the authoritative SQ-03F.5 artifact or its provenance cannot be validated,
SQ-03F.6 SHALL fail closed.

## Target participation

For each downstream target, define its participation count as the number of eligible SQ-03F.5 sources whose frozen two-hop territory contains that target.

The first result-bearing analyzer contract SHALL freeze:

- treatment of targets reached by only one source;
- normalization of participation counts;
- whether concentration is computed on raw participation mass or another
  explicitly defined frozen transform;
- handling of ties;
- target ordering;
- any minimum participation requirement;
- exact treatment of empty or degenerate cases.

These rules MUST be frozen before observed concentration is interpreted.

## Primary concentration statistic

SQ-03F.6 SHALL use a single pre-declared primary concentration statistic that
quantifies how strongly downstream participation mass is concentrated among
targets.

The result-bearing analyzer contract MUST freeze the exact formula before
execution.

Candidate families include concentration measures such as HHI or an equivalent
pre-declared normalized concentration statistic, but the exact metric SHALL NOT
be selected after inspecting the observed target distribution.

## Supporting descriptive measures

The result artifact MAY include descriptive measures such as:

- number of unique downstream targets;
- target participation histogram;
- maximum target participation count;
- top-k participation shares;
- cumulative participation curve;
- number of targets reached by all eligible sources;
- number of targets reached by at least half of eligible sources.

These are descriptive unless explicitly incorporated into the frozen
classification rule before execution.

## Null model

The null SHALL inherit the SQ-03F.5 matched-source randomization framework.

Each randomized draw SHALL:

- preserve the observed source count;
- sample from the same frozen SQ-03F candidate-source universe;
- preserve the frozen source-matching rule used by SQ-03F.5;
- compute downstream territories using the identical frozen two-hop rule;
- compute the same frozen concentration statistic as the observed source set.

The randomization count SHALL remain **10,000**.

The base randomization seed SHALL remain **314159** unless the analyzer
contract requires independent deterministic streams, in which case the exact
derivation SHALL be frozen and recorded before execution.

## Classification

SQ-03F.6 SHALL distinguish at minimum:

1. **GREATER_THAN_NULL_TARGET_CONCENTRATION**  
   Downstream convergence is more concentrated than expected under the frozen
   matched-source null.

2. **NO_CLEAR_EVIDENCE_OF_UNUSUAL_TARGET_CONCENTRATION**  
   The observed concentration is not unusual enough under the frozen rule to
   support a stronger concentration claim.

3. **LESS_THAN_NULL_TARGET_CONCENTRATION**  
   Downstream participation is more broadly distributed than expected under
   the frozen matched-source null.

Exact numeric classification thresholds, tail definitions, and any required
effect-size gate SHALL be frozen in the result-bearing analyzer contract before
execution.

No threshold may be moved after inspecting the observed result.

## Claim boundary

A positive result would support only the claim that, within the frozen
MoscaQuant model and frozen SQ-03F source set, downstream participation is more
concentrated among targets than expected under the matched-source null.

It would NOT establish:

- literal biological command hierarchy;
- anatomical governing bodies or "commissions";
- organism-level functional modules;
- sex-specific neural organization;
- consciousness, agency, intent, or coordination;
- financial usefulness;
- trading usefulness;
- generalization beyond the frozen model and source universe.

A null or broadly distributed result would not invalidate SQ-03F.5. It would
mean that the previously established downstream convergence is not primarily
explained by unusually concentrated downstream target participation under the
frozen SQ-03F.6 statistic.

## Separation from preceding experiments

- SQ-03F.3 — MADE MEN: repeat hotspot/shared-source structure under frozen
  stratified randomization.
- SQ-03F.4 — SIT-DOWN: records the shared source relationship.
- SQ-03F.5 — TURF WAR: tests whether shared sources converge into common
  downstream territory.
- SQ-03F.6 — THE COMMISSION: tests whether that downstream convergence is
  concentrated on a relatively small shared target core.

## Execution boundary

This protocol freezes the scientific question, inherited parent inputs, target
participation concept, null family, claim boundary, and required
classification structure.

It does NOT:

- calculate target participation;
- rank downstream targets;
- inspect target concentration;
- choose the final primary concentration formula after seeing the data;
- execute randomizations;
- classify a result;
- create an SQ-03F.6 result artifact.

The result-bearing analyzer contract SHALL be reviewed and frozen separately
before SQ-03F.6 is executed.

> The family may own the same turf. SQ-03F.6 asks whether everybody still
> reports to the same table.
