# MQ-5.ER.4 — THE STEVEDORES

## Purpose

MQ-5.ER.4 tests whether any of the three runtime-aligned recurrent edges
identified by MQ-5.ER.3 RETOUR are causally necessary for the Arm-C response
pattern that survives the original frozen 13-edge lesion.

RETOUR was discovery-only. THE STEVEDORES is the preregistered causal follow-up.

Financial semantics remain **NOT ASSIGNED**.

## Parent experiment

- MQ-5.ER.3 — RETOUR
- Parent result SHA-256:
  `90d8198a1c218ad24ef29c2c70b4b7a88fd8b24804516d2fd8f20903b847ff3e`

## Frozen candidate edges

1. `11725 -> 29921`
2. `11345 -> 47350`
3. `10647 -> 51642`

These are hypotheses, not established causal edges.

## Frozen target sets

Affected targets:

- `55`
- `92`
- `656`
- `126002`
- `137122`

Retained-dependency comparison targets:

- `51`
- `129`
- `317`
- `1273`

All nine responders remain measured.

## Baseline condition

The causal baseline is:

**C13 = Arm C + original frozen 13-edge lesion**

Frozen C13 first-positive onsets:

- `51`: `150`
- `55`: `145`
- `92`: `141`
- `129`: `149`
- `317`: `156`
- `656`: `141`
- `1273`: `149`
- `126002`: `151`
- `137122`: `151`

## Intervention arms

All interventions are applied on top of C13.

- `C13-S1`: lesion `11725 -> 29921`
- `C13-S2`: lesion `11345 -> 47350`
- `C13-S3`: lesion `10647 -> 51642`
- `C13-ALL`: lesion all three STEVEDORE edges simultaneously

No other topology change is permitted.

## Single-edge necessity endpoint

For each target and each single-edge intervention, dependency is expressed iff:

- the target is present in C13; and
- intervention onset is later than C13, or the target becomes absent.

Earlier onset does not count as necessity.

For each candidate edge:

- `SINGLE_EDGE_CAUSAL_SUPPORT_COMPLETE`
- `SINGLE_EDGE_CAUSAL_SUPPORT_PARTIAL`
- `SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED`

Frozen candidate-associated affected targets:

- `11725 -> 29921`: `55, 126002, 137122`
- `11345 -> 47350`: `92, 656, 126002`
- `10647 -> 51642`: `55, 92, 656`

## Combined-edge endpoint

For `C13-ALL`, dependency is assessed on all five affected targets.

- `COMBINED_SET_CAUSAL_SUPPORT_COMPLETE`: `5 / 5`
- `COMBINED_SET_CAUSAL_SUPPORT_PARTIAL`: `1-4 / 5`
- `COMBINED_SET_CAUSAL_SUPPORT_NOT_OBSERVED`: `0 / 5`

A pattern where no single lesion changes a target but the combined lesion does
may be reported as compatible with redundancy or distributed routing. It does
not prove either mechanism.

## Comparison-target specificity

The same onset endpoint is evaluated on retained comparison targets
`51, 129, 317, 1273`.

- `AFFECTED_SET_SPECIFIC_WITHIN_TESTED_TARGETS`
- `SHARED_WITH_RETAINED_DEPENDENCY_TARGETS`
- `RETAINED_ONLY_OR_NONPRIMARY_PATTERN`
- `SPECIFICITY_NOT_ESTABLISHED`

Specificity is separate from necessity.

## Secondary waveform diagnostics

For each intervention versus C13:

- first-positive onsets for all nine responders;
- responder presence/absence;
- normalized positive-voltage fingerprint L2 distance;
- normalized positive-voltage fingerprint cosine similarity;
- per-target peak positive voltage;
- per-target integrated positive voltage.

These remain secondary descriptive diagnostics.

## BUBBLES REPORT

Every intervention must emit a descriptive `bubbles_report` section.

Bubbles reports only observations:

- target onset change;
- target present/absent;
- peak positive-voltage change;
- integrated positive-voltage change;
- fingerprint L2/cosine;
- candidate edge(s) actually lesioned;
- whether any unexpected responder appeared.

Bubbles must not assign causality, mechanism, hierarchy, cognition, or financial
meaning.

**Bubbles observes. Lester interprets. McNulty speculates.**

## Structural matched controls

A matched control edge must be frozen separately for each STEVEDORE edge before
result execution.

Control selection must use structural information only and must not inspect any
MQ-5.ER.4 neural outcome.

Matching variables:

1. intervention-addressable under RETOUR eligibility semantics;
2. same associated-target hop signature where feasible;
3. minimize maximum log-scale mismatch across:
   - absolute edge weight;
   - presynaptic outdegree;
   - postsynaptic indegree;
4. minimize summed log-scale mismatch;
5. deterministic tie-break by postsynaptic then presynaptic model index.

Any retina-to-relay ordinary edge deterministically canceled by the frozen relay
bookkeeping is ineligible as a matched control.

## Runtime and integrity gates

Before result execution:

- reproduce frozen Arm-C stimulus SHA-256:
  `e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`
- reproduce exact C13 onsets;
- verify exact original 13-edge lesion;
- verify all three STEVEDORE edges exist with frozen weights recorded before
  authorization;
- verify all matched controls are frozen and intervention-addressable;
- verify RETOUR parent result SHA-256;
- require clean git worktree;
- require all protocol/runner/test/control files tracked;
- require result artifact absent.

Result execution remains disabled until a separate authorization commit changes
only the execution gate.

## Claim limits

THE STEVEDORES may support or fail to support computational necessity under the
frozen runtime.

It does not establish biological causality, uniqueness, sufficiency, cognition,
financial semantics, market prediction, or trading value.

## Lore

This section is a readability layer only. The frozen scientific definitions,
endpoints, controls, and claim limits above remain authoritative.

RETOUR followed Marlo's package to THE DOCKS and found three recurrent
runtime-aligned candidates. THE STEVEDORES treats those candidates like dock
workers repeatedly seen near a suspicious handoff:

- remove each worker separately;
- replay the same C13 operation;
- compare what changes against a structurally matched control worker;
- then remove the entire three-worker crew to test whether the operation can
  compensate for single losses but not the combined loss.

Bubbles is the observational layer. He reports what changed and stops there.
Lester is the methodological layer. He keeps interpretation tied to the frozen
endpoint. McNulty is the hypothesis layer, and his judgment is intentionally
getting worse as the running joke progresses.

At this stage the fictional McNulty BAC meter is approximately **0.08%**.
Real-world impairment at about that level includes reduced judgment, divided
attention, coordination, and reaction time. The number is narrative context,
not an experimental variable, recommendation, or drinking target.

Horseface remains McNulty's working theory only.

Omar remains reserved for a result that demonstrates a genuine causal
disruption under the frozen experiment. No disruption, no whistle.

## Frozen matched controls

Selected before any MQ-5.ER.4 neural outcome was inspected.

- S1 control `19300 -> 26090`, weight `-0.22811059653759003`, hop `[3,3,3]`, pre outdegree `17`, post indegree `88`.
- S2 control `16922 -> 34070`, weight `-0.33714285492897034`, hop `[3,2,3]`, pre outdegree `22`, post indegree `40`.
- S3 control `12775 -> 57635`, weight `0.3538961112499237`, hop `[3,2,2]`, pre outdegree `46`, post indegree `62`.

Selector artifact SHA-256: `7afd63ef205a21e19306b9145b1bbfdd09e8b254f413a59950f77b8c0a9ce20c`

No MQ-5.ER.4 neural outcome was used during control selection.

## Pre-run RETOUR audit clarifications

These facts were already present in the frozen RETOUR result and are recorded
explicitly here before any MQ-5.ER.4 result execution.

### Focused-recurrence threshold provenance

RETOUR did **not** choose "three of five affected targets" after inspecting its
result. Its frozen classification rule defined a focused candidate as the same
directed edge appearing in the top-five candidate list for at least **3 of the
5 affected targets**.

THE STEVEDORES inherits the three edges that satisfied that frozen discovery
rule. No MQ-5.ER.4 outcome was used to choose the threshold or the candidates.

### Retained-comparison recurrence was already known

The RETOUR discovery output also showed that the three STEVEDORE candidates
were not confined to the five affected targets' top-five lists:

- `S1 = 11725 -> 29921` also appeared in retained-comparison targets `51` and
  `129`.
- `S2 = 11345 -> 47350` also appeared in retained-comparison target `51`.
- `S3 = 10647 -> 51642` also appeared in retained-comparison targets `51`,
  `129`, `317`, and `1273`.

These are top-five discovery recurrences, not causal effects.

Therefore THE STEVEDORES does **not** preregister any of the three candidates as
affected-set-specific. All four retained targets remain measured, and
specificity is reported separately from the primary necessity endpoint.

The candidates are intentionally not dropped after seeing retained-target
recurrence. Removing them now would turn known discovery information into a
post-hoc selection filter. The confirmatory intervention is instead allowed to
show whether an edge has:

- affected-target dependency only;
- shared affected and retained dependency;
- retained-only dependency; or
- no tested dependency.

### Chain stopping rule

MQ-5.ER.4 closes this three-candidate confirmatory branch under the following
precommitted rules:

1. **No single-edge and no combined affected-target dependency:** this
   STEVEDORE candidate set is closed. No pairwise, higher-order, or replacement
   edge fishing may be launched from the same result.
2. **At least one single-edge affected-target dependency:** report the frozen
   single-edge and specificity classifications. Mechanistic follow-up requires
   a separately preregistered experiment with a new explicit hypothesis; the
   current result does not authorize adaptive edge searching.
3. **Joint-only affected-target dependency** — no single candidate shows
   dependency for that target, but `C13-ALL` does — permits exactly one
   predefined follow-up branch testing the three pairwise candidate lesions:
   `S1+S2`, `S1+S3`, and `S2+S3`, against the same C13 baseline and endpoint.
   That follow-up must be separately frozen before execution.
4. After that pairwise follow-up, this candidate-combination branch closes
   regardless of outcome unless an independent new hypothesis is introduced
   and preregistered.

A joint-only result is described as **redundancy-compatible** or
**distributed-routing-compatible** only. It does not prove redundancy.

No blind replacement-candidate search is authorized by MQ-5.ER.4.


## Result closeout

Authoritative result artifact:
`/home/wil/moscaquant-data/experiments/mq5-er4-the-stevedores-v1.json`

SHA-256:
`4de3cd6f52782908fc7afad853a5db0e0a1595923de1965c0b47606b5329f5dc`

Result commit:
`7134cbc81d1b40174646424e5da0ecf2ed69d98f`

Frozen primary outcome:

- S1: `SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED`
- S2: `SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED`
- S3: `SINGLE_EDGE_CAUSAL_SUPPORT_NOT_OBSERVED`
- S1+S2+S3: `COMBINED_SET_CAUSAL_SUPPORT_NOT_OBSERVED`
- affected-target dependency count under combined lesion: `0/5`
- redundancy-compatible pattern: not observed for any frozen affected target
- specificity: not established because no preregistered dependency was observed

Secondary descriptive telemetry showed that S3 changed positive-voltage amplitude
for some targets while preserving all frozen first-positive onsets. In
particular, target `92` showed a reduced integrated positive voltage under the
S3 lesion, but onset remained frame `141`. This is descriptive waveform
sensitivity, not evidence for the preregistered necessity endpoint.

Per the pre-run stopping rule, this three-candidate STEVEDORE branch is closed.
No pairwise follow-up is authorized because the combined lesion was null on the
frozen affected-target dependency endpoint. Any deeper investigation requires a
new independent hypothesis and a new preregistration.
