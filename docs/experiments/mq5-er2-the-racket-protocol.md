# MQ-5.ER.2 — THE RACKET

**Codename:** THE RACKET
**Kind:** prospective confirmatory causal intervention
**Parent discovery:** MQ-5.ER.1 — DETOUR
**Prior placeholder name:** ROADBLOCK
**Financial semantics:** NOT ASSIGNED
**Result execution:** disabled at initial freeze

## Question

DETOUR identified directed edge `116680 -> 12024` as a focused recurring
candidate for affected targets `92`, `656`, and `137122`. The same edge also
appeared in retained-dependency comparison target `1273`.

THE RACKET asks:

> Which frozen Arm-C responses causally depend on `116680 -> 12024`, especially
> after the original 13-edge bundle has been removed?

This experiment tests necessity of the discovered edge. It does not test
sufficiency, biological equivalence, financial meaning, trading usefulness, or
general connectome optimality.

## Frozen subjects

All nine accepted MQ-5 responder targets remain measured:

`51, 55, 92, 129, 317, 656, 1273, 126002, 137122`

Primary discovery-positive affected targets:

`92, 656, 137122`

Affected negative-comparison targets:

`55, 126002`

Retained-dependency comparison targets:

`51, 129, 317, 1273`

Target `1273` is the prespecified key specificity comparison because DETOUR also
ranked `116680 -> 12024` in its top-five list.

## Frozen intervention

Focused DETOUR edge:

`116680 -> 12024`

Primary intervention:

- set the effective weight of this exact directed edge to zero;
- do not alter any other edge;
- do not retune gains, thresholds, encoders, runtime constants, or responder
  definitions.

The original frozen 13-edge lesion from MQ-5.TS / MQ-5.ER remains unchanged.

## Frozen arms

All arms use the frozen MQ-5.ER Arm-C encoder and the same 192-frame episode.

### C0 — Arm-C baseline

No lesion.

Purpose: reproduce the known Arm-C baseline.

### C13 — Arm-C + original 13-edge lesion

Apply only the previously frozen 13-edge causal-route lesion.

Purpose: reproduce the parent no-jitter lesion condition and establish the
background in which the DETOUR edge persisted.

### CR — Arm-C + RACKET edge lesion

Lesion only `116680 -> 12024`.

Purpose: test whether the focused edge contributes to the intact Arm-C response.

### C13R — Arm-C + original 13-edge lesion + RACKET edge lesion

Apply both the original 13-edge lesion and `116680 -> 12024`.

Purpose: primary causal test. Compare C13R prospectively against C13.

## Primary endpoint

For each frozen target, the primary causal endpoint is first-positive onset
under C13R relative to C13.

A target shows a prespecified RACKET dependency if either:

1. its first-positive onset occurs later in C13R than in C13; or
2. the target is present in C13 but fails to become positive within 192 frames
   in C13R.

An earlier onset is not counted as evidence of necessity.

## Secondary endpoints

Secondary descriptive measurements:

- responder presence/absence;
- exact onset shift in frames;
- normalized responder-voltage fingerprint distance;
- intact-background effect CR versus C0;
- full nine-target response pattern.

Secondary endpoints cannot override the primary dependency definition.

## Primary interpretation set

The primary confirmatory set is:

`92, 656, 137122`

These targets were chosen before THE RACKET because the frozen DETOUR result
placed the exact edge `116680 -> 12024` in each target's top-five candidate list.

No additional target may be promoted into the primary set after result
inspection.

## Prespecified causal-support classification

Let `k` be the number of primary targets (`92`, `656`, `137122`) satisfying the
RACKET dependency endpoint in C13R versus C13.

- `RACKET_CAUSAL_SUPPORT_COMPLETE` — `k = 3`
- `RACKET_CAUSAL_SUPPORT_PARTIAL` — `k = 1 or 2`
- `RACKET_CAUSAL_SUPPORT_NOT_OBSERVED` — `k = 0`

These labels apply only to necessity of the focused edge within the frozen
computational intervention.

## Prespecified specificity classification

Specificity is reported separately from causal support.

- `AFFECTED_SET_SPECIFIC_WITHIN_TESTED_TARGETS` — at least one primary target
  satisfies the dependency endpoint and none of `51, 129, 317, 1273` does.
- `SHARED_WITH_RETAINED_DEPENDENCY_TARGETS` — at least one primary target and
  at least one retained-dependency comparison target satisfy the dependency
  endpoint.
- `RETAINED_ONLY_OR_NONPRIMARY_PATTERN` — no primary target satisfies the
  endpoint but at least one retained-dependency comparison target does.
- `SPECIFICITY_NOT_ESTABLISHED` — any remaining pattern.

The affected negative-comparison targets `55` and `126002` are reported
separately and are not used to redefine the primary set.

## Matched-control edge

A topology-matched non-candidate control edge is required for authoritative
execution and must not be selected from confirmatory outcomes.

Before result execution, a deterministic control-edge selection procedure SHALL
be frozen using only pre-outcome information such as:

- directed-edge existence;
- hop class relative to the same targets;
- absolute edge weight;
- presynaptic/postsynaptic degree or other explicitly frozen structural
  covariates;
- exclusion from the DETOUR top-five candidate lists.

The selected control edge and the exact matching rule must be committed before
THE RACKET result execution is enabled.

If no scientifically defensible matched control can be selected prospectively,
THE RACKET may still test necessity, but claims of candidate-edge specificity
must remain correspondingly narrower.

## Replay and integrity gates

Before any result-bearing RACKET execution:

1. C0 must reproduce the frozen Arm-C stimulus hash and known baseline onset
   vector.
2. C13 must reproduce the frozen Arm-C stimulus hash and known C-LESION13 onset
   vector.
3. The focused edge identity must equal exactly `116680 -> 12024`.
4. The original 13-edge lesion set must match the frozen parent set exactly.
5. The frame count must equal `192`.
6. The candidate-rule outcome from DETOUR must not be recomputed or retuned.
7. Result execution must remain disabled until implementation tests and control
   selection are frozen in separate commits.
8. The working tree must be clean before authoritative result execution.

Any replay mismatch aborts the run.

## Claim boundary

THE RACKET may support a prospective causal claim about necessity of
`116680 -> 12024` in the tested computational condition.

It may not establish:

- sufficiency of the edge;
- uniqueness of the route;
- biological causality in a real fly;
- intentional or cognitive meaning;
- financial semantics;
- market prediction;
- trading utility or profitability.

## Planned output

The authoritative artifact shall record:

- Git HEAD;
- parent DETOUR artifact SHA-256;
- frozen edge identity;
- frozen 13-edge lesion identity/hash;
- replay hashes and onset vectors;
- per-arm target onsets and presence;
- per-target dependency endpoint;
- primary causal-support classification;
- specificity classification;
- matched-control identity/rule if available;
- financial semantics;
- artifact SHA-256.

## Lore

DETOUR found the guy everybody named.

THE RACKET finds out whether he actually runs the operation — or whether
somebody put him out front to take the heat.

If the operation keeps moving after he disappears, he may have been the fall
guy.

If multiple downstream targets stop responding, somebody really was giving
orders through him.

The jokes remain downstream of the evidence.

## Pre-outcome matched-control intervention amendment

This amendment is frozen before any MQ-5.ER.2 neural outcome is generated.

The matched-control edge selected under the frozen V2 structural rule is
`78481 -> 16087`. The control must be used as an intervention, not merely
reported as a structural descriptor.

Two additional arms are therefore part of the confirmatory design:

- **CC** = Arm C baseline + matched-control edge lesion only.
- **C13C** = original frozen 13-edge lesion + matched-control edge lesion.

The complete intervention set is:

- **C0** — Arm C baseline, no lesion.
- **C13** — original frozen 13-edge lesion only.
- **CR** — focused RACKET edge `116680 -> 12024` lesioned only.
- **C13R** — original 13-edge lesion + focused RACKET edge.
- **CC** — matched-control edge `78481 -> 16087` lesioned only.
- **C13C** — original 13-edge lesion + matched-control edge.

The preregistered primary necessity endpoint remains **C13R versus C13**:
for a target, focused-edge dependency is observed only if C13R has a later
first-positive onset than C13 or the target is present in C13 and absent within
192 frames in C13R. Earlier onset is not evidence of necessity.

The matched-control calibration comparison is **C13C versus C13**, using the
same endpoint definition. It asks whether a structurally similar non-candidate
edge produces the same kind of dependency signal.

Interpretation is constrained as follows:

- focused-edge dependency with no matched-control dependency strengthens the
  case that the focused DETOUR candidate is not merely one interchangeable
  perturbation of similar structural size;
- focused-edge and matched-control dependency together indicate a
  non-specific or shared perturbation effect within this tested control;
- matched-control dependency without focused-edge dependency argues against
  interpreting the focused edge as the relevant causal dependency;
- neither comparison establishes uniqueness, sufficiency, biological
  causality, cognition, financial semantics, or market-predictive value.

Target-set specificity and matched-edge specificity are separate axes and must
not be collapsed into one label.

No threshold, target set, lesion, encoder, runtime parameter, or classification
rule may be retuned from MQ-5.ER.1 outcomes or from any MQ-5.ER.2 result.

### Lore

The suspect gets pulled out of the room. Then the civilian gets pulled out of
the room under the same rules.

If the whole operation falls apart either way, the cops learned nothing from
the lineup. If only the suspect matters, now the sit-down gets interesting.
