# SQ-05 — TWO BETRAYALS — Core Preregistration Candidate

**Status:** REVIEW CANDIDATE — NO NEURAL OR RESULT EXECUTION AUTHORIZED

This gate freezes the remaining scientific choices that could otherwise drift
after outcomes become visible: the lesion sham, BETRAYAL II seed block, fixed
readout population, endpoint definitions, and classification rules.

## Arms

The scientific protocol contains four analysis arms:

1. `INTACT` — exact frozen baseline connectome.
2. `BETRAYAL_I_LESIONED` — exact inherited 13-edge causal-route lesion.
3. `BETRAYAL_I_SHAM` — exact 13-edge historical matched sham.
4. `BETRAYAL_II_SHUFFLED` — strict matched-topology null at frozen depth 1.0x.

The sham is a scientific control and is not required to become a headline
Panopticon arm.

## BETRAYAL I sham

The historical MQ-3.2 sham was re-derived from the frozen baseline before any
SQ-05 neural execution and reproduced exactly.

Frozen canonical edge-set digest:

`4a96cc329bb98a6cce66315280d80dcf9389c1ea7e39934b5d40d31ab4cc6879`

At authoritative SQ-05 execution these edges are loaded as exact identities.
They are not reselected.

## BETRAYAL II fresh seeds

The first candidate block beginning at `20265000` is rejected because
`20265000` already appears in the BETRAYAL II engineering test.

The first collision-free audited candidate block is frozen:

`20265100..20265119`

Exactly 20 seeds are required. There is no early stopping and no silent
replacement of failed seeds. A seed topology is built once and reused for both
`LR` and `RL`.

This remains a fixed 20-seed benchmark, not a population-level significance
claim.

## Primary response population

The primary population is fixed independently of SQ-05 outcome:

- DN-C0: 6 neurons
- DN-C1: 646 neurons
- DN-C2: 539 neurons
- total assigned consensus DNs: 1,191

The 123 structurally unassigned DNs remain excluded under the already-frozen
consensus rule, not because of SQ-05 response.

No post-result responder selection is permitted.

## Primary fingerprint

For each layout, store the complete 192-frame positive-voltage trajectory for
all 1,191 assigned consensus DNs in ascending model-index order.

Positive voltage is `max(voltage, 0)`.

The individual-neuron fingerprint is the primary comparison object. Also store
the full 192-frame mean-positive-voltage trace for DN-C0, DN-C1, and DN-C2.

## Cue-transition status

The final Cue-A-only block, frames `80..95`, is the reference.

Cue-B blocks are `96..111`, `112..127`, `128..143`, `144..159`, `160..175`,
and `176..191`.

A layout counts as showing a DN cue transition when any DN-C channel block mean
differs from its Cue-A reference mean by more than `1e-12`.

Statuses:

- `BOTH_LAYOUTS_RESPOND_TO_CUE_B`
- `LAYOUT_DEPENDENT_CUE_B_RESPONSE`
- `NO_DN_CUE_B_RESPONSE`

This describes modeled DN activity only. It is not threat perception.

## Distance metric

For primary fingerprints `x` and `y`:

`D(x,y) = ||x-y||2 / max(||x||2 + ||y||2, 1e-12)`

Maximum absolute difference is also recorded.

## BETRAYAL I classification

For each layout compare lesion-to-INTACT distance with sham-to-INTACT distance.

Statuses:

- `LESION_EFFECT_EXCEEDS_SHAM_BOTH_LAYOUTS`
- `LAYOUT_DEPENDENT_LESION_EFFECT`
- `LESION_NOT_SEPARATED_FROM_SHAM`

This is a model-response comparison, not a hunger, danger, fear, or behavior
claim.

## BETRAYAL II exact reproduction

A seed counts as an exact intact-response reproduction only when both layouts
pass all frozen tolerances:

- symmetric normalized L2 `<= 1e-9`
- maximum absolute difference `<= 1e-12`
- primary individual-DN fingerprint passes
- DN-C summary traces pass

The 20-seed count bands are:

- 0–1: `STRICT_NULL_RARELY_REPRODUCES_INTACT_RESPONSE`
- 2–9: `MIXED_STRICT_NULL_REPRODUCTION`
- 10–20: `STRICT_NULL_FREQUENTLY_REPRODUCES_INTACT_RESPONSE`

No population-level significance claim is attached.

## Lesion-specific secondary diagnostic

The accepted nine MQ-3.2 responders remain fixed secondary endpoints:

`51, 55, 92, 129, 317, 656, 1273, 126002, 137122`

Record responder identity, first-positive onset, and full positive-voltage
fingerprint.

They are secondary because they were response-selected during earlier
Condition-A work. SQ-05's novel visual sequence may recruit activity elsewhere.

## Determinism

`INTACT`, `BETRAYAL_I_LESIONED`, and `BETRAYAL_I_SHAM` each require exact
duplicate replay in both layouts before interpretation.

Every arm/layout starts from fresh runtime state.

## Reporting rule

SQ-05 has no single combined winner. Report separately:

1. cue-transition status
2. BETRAYAL I versus sham status
3. BETRAYAL II strict-null reproduction status

## Still not authorized

This preregistration does not freeze or authorize the authoritative runner,
result schema/writer, capacity/execution mode, execution authorization, or
result-bearing neural execution.

## TWO BETRAYALS

The Index is now close enough to make everyone nervous.

But the switches are labeled before we touch it.
