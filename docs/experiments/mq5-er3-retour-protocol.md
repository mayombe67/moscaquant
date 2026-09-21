# MQ-5.ER.3 — RETOUR

## Purpose

RETOUR is a corrected discovery experiment following MQ-5.ER.1 DETOUR and
MQ-5.ER.2 THE RACKET.

DETOUR identified a recurrent candidate edge, `116680 -> 12024`. THE RACKET
then found no preregistered causal-support signal when that edge was lesioned.
A post-result audit showed that the focused edge was a retina-to-relay edge
whose ordinary connectome contribution is subject to the frozen retinal
double-count-removal path.

RETOUR asks:

> After excluding or neutralizing ordinary-connectome contributions that are
> not intervention-addressable in the actual runtime, does Arm C still expose
> a recurrent candidate route for the five affected targets?

This is a discovery experiment. It does not authorize causal claims.

## Parent experiments

- MQ-5.ER.1 — DETOUR
- MQ-5.ER.2 — THE RACKET

## Frozen scientific inputs

- Arm C encoding from MQ-5.ER.
- `192` frames.
- Frozen responder set:
  `51, 55, 92, 129, 317, 656, 1273, 126002, 137122`.
- Affected targets:
  `55, 92, 656, 126002, 137122`.
- Retained-dependency comparisons:
  `51, 129, 317, 1273`.
- Original frozen 13-edge lesion.
- Maximum backward hops: `3`.
- Top candidates per target: `5`.
- Financial semantics: `NOT ASSIGNED`.

No MQ-5.ER.3 outcome may be inspected before the scoring and eligibility rules
below are frozen and tested.

## Runtime-aligned eligibility correction

RETOUR operates on the same frozen runtime semantics used by THE RACKET.

The runtime computes ordinary connectome synaptic current and then performs
frozen retinal double-count removal at relay neurons. Therefore an
ordinary-connectome edge may appear dynamically large before cancellation while
being non-addressable by a connectome-only lesion.

A candidate edge is **intervention-addressable** only if its ordinary
connectome contribution survives the frozen runtime bookkeeping used by the
later causal lesion.

### Retina-to-relay rule

For every ordinary edge `pre -> post`:

1. If `pre` is not in the frozen retina population, the edge remains eligible
   under this correction.
2. If `post` is not in the frozen relay population, the edge remains eligible
   under this correction.
3. If `pre` is retina and `post` is relay, RETOUR must inspect the corresponding
   frozen `relay_from_retina` coefficient.
4. If the relay coefficient matches the ordinary connectome coefficient within
   `rtol=1e-6`, `atol=1e-12`, the ordinary edge is classified
   `DETERMINISTICALLY_CANCELED_RETINA_RELAY` and is ineligible for DETOUR-style
   candidate ranking.
5. If the two coefficients do not match within tolerance, execution aborts.
   RETOUR must not guess a residual per-edge contribution from an inconsistent
   frozen representation.

This rule is frozen before outcome generation.

## Why exclusion is used instead of rescoring the canceled edge

THE RACKET lesions the ordinary connectome edge. It does not alter the frozen
retinal relay artifact.

Accordingly, an ordinary retina-to-relay edge whose contribution is exactly
removed by the double-count-removal path is not a valid candidate for that
intervention class. RETOUR therefore excludes such edges rather than assigning
them a misleading pre-cancellation score.

A future experiment may separately test causal interventions on the frozen
retinal relay artifact. RETOUR does not do that.

## Dynamic discovery score

For eligible edges, RETOUR preserves DETOUR's frozen dynamic score:

`score = L1(C edge contribution - A edge contribution) * L1(C13 edge contribution)`

The temporal window runs from frame `0` through the target's Arm-C baseline
first-positive onset, inclusive.

Eligibility additionally requires:

- integrated Arm-C versus Arm-A edge-contribution difference `> 1e-12`;
- integrated absolute C13 contribution `> 1e-12`;
- edge is intervention-addressable under the retina-to-relay rule above.

## Search and ranking

- maximum backward hops: `3`
- top `5` candidates per affected target
- rank descending by score
- then fewer hops
- then lower postsynaptic model index
- then lower presynaptic model index

The traversal must not use a
`DETERMINISTICALLY_CANCELED_RETINA_RELAY` ordinary edge as a candidate edge.

Whether such an edge may appear elsewhere in a backward ancestry walk must not
allow it to be emitted or scored as a candidate.

## Frozen recurrence classification

- `FOCUSED_RETOUR_CANDIDATES`:
  the same eligible directed edge appears in the top-five lists of at least
  `3 / 5` affected targets.
- `DIFFUSE_RETOUR_CANDIDATES`:
  eligible candidates exist, but no directed edge reaches recurrence `3 / 5`.
- `NO_CLEAR_RETOUR_CANDIDATES`:
  no eligible candidate survives the frozen rule.

This is discovery-only classification.

## Mandatory negative control from THE RACKET

`116680 -> 12024` — canonically THE NO-SHOW — must be classified
`DETERMINISTICALLY_CANCELED_RETINA_RELAY` and must not appear in any RETOUR
candidate list.

The frozen matched-control edge `78481 -> 16087` must satisfy the same
classification and must not appear in any RETOUR candidate list.

Failure of either negative-control assertion aborts execution.

## Known-replay gates

Before any result-bearing execution, RETOUR must reproduce:

- frozen Arm-A stimulus hash;
- frozen Arm-C stimulus hash;
- Arm-A baseline onsets;
- Arm-C baseline onsets;
- Arm-C + original 13-edge-lesion onsets;
- exact frozen 13-edge lesion;
- exact `192` frame count.

Any mismatch aborts.

## Result authorization

Result execution is disabled at preregistration.

A separate commit must:

1. freeze the implementation and tests;
2. confirm known replay;
3. leave the repository clean;
4. then authorize result execution by changing only the execution gate.

The result artifact must not already exist.

## Claim limits

RETOUR may identify runtime-aligned discovery candidates.

RETOUR does **not** establish:

- necessity;
- sufficiency;
- uniqueness;
- biological causality;
- cognition;
- financial semantics;
- market-predictive value;
- trading value.

Any focused RETOUR candidate requires a later preregistered causal intervention
experiment.

## Lore

DETOUR followed a guy who was on the books. THE RACKET discovered he had a
no-show job.

RETOUR sends the accountants back through the ledger with one new rule:

> If the paycheck gets reversed before closing, he does not make the suspect
> list.

THE NO-SHOW can still appear in the case file. He just cannot get arrested
twice for the same accounting trick.
