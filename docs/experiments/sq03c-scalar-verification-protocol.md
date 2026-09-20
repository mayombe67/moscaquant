# SQ-03C — CHECK THE RECEIPTS

## Scalar Verification Protocol

**Status:** FROZEN BEFORE PANEL SELECTION  
**Class:** Confirmatory computational verification follow-up  
**Parents:** SQ-03A — THE OTHER FLY; SQ-03B — FIND THE DIFFERENCE

## Question

SQ-03B found a strongly long-tailed distribution of single-edge
counterfactual sensitivities. The strongest effects were orders of magnitude
larger than the known scalar-vs-batched numerical discrepancy, but SQ-03B was
executed through the validated batched engine.

SQ-03C asks:

> Do the strongest SQ-03B localization effects survive independent
> re-execution through the original scalar `HybridRuntime`, while deterministic
> low-tail controls remain low?

This is a confirmatory computational verification experiment. It does not
create a new biological claim.

## Frozen source evidence

Panel selection must be derived only from the completed SQ-03B durable
checkpoint ledger.

Expected source hashes:

- SQ-03B result:
  `0bcfbeef18ba43e4a3371cae13f1d05a04fc63fc988084e9bf45a33f6a00a2f8`
- SQ-03B checkpoint ledger:
  `7b2632de5792973534177b697efdd7c3af0b82a836d9d2b597812dbc0dd1f725`

Any mismatch stops the experiment.

## Frozen strata

Selection is stratified by the already-frozen SQ-03B input and subject:

- inputs: `TmY14`, `LPLC2`, `AVLP234`, `AVLP435`
- subjects: `MORTY`, `LILITH`

This produces eight input/subject strata.

The purpose of stratification is to prevent a single high-magnitude
input/subject combination from consuming the entire verification panel.

## Upper-tail verification panel

Within each stratum, freeze the union of:

1. the top **8** jobs ranked by maximum absolute
   `integrated_positive_voltage_delta` over that job's relevant anchors; and
2. the top **8** jobs ranked by maximum absolute `peak_voltage_delta` over the
   same relevant anchors.

Deduplicate that union by `(input, subject, edge_id)`.

Tie-breaking is deterministic and frozen.

No manual candidate may be added after the panel is generated.

## Low-tail controls

Within each stratum, freeze the bottom **8** jobs ranked by:

1. max absolute integrated-positive-voltage delta — ascending;
2. max absolute peak-voltage delta — ascending;
3. edge ID — ascending.

These are deterministic low-tail controls from the same completed experiment.

No numerical threshold is used to define the upper or lower panel.

## Scalar execution

Each selected job is rerun one job at a time through:

`brain.hybrid_runtime.HybridRuntime`

using the same SQ-03A/SQ-03B runtime and stimulus:

- 64 frames;
- stimulus frame 0;
- amplitude 0.5;
- `dt_ms = 1.0`;
- `tau_ms = 20.0`;
- threshold 1.0;
- reset voltage 0.0;
- same conservative matched graph;
- same common normalization;
- same single-edge equalization rule.

MORTY receives only the selected edge's LILITH weight.
LILITH receives only the selected edge's MORTY weight.

No batched neural execution is used for the SQ-03C verification run.

## Controls

Before accepting SQ-03C output:

1. the SQ-03A scalar baseline must replay exactly for every frozen stratum;
2. every scalar counterfactual must pass exact A/A replay;
3. the matched graph and normalization must match the accepted SQ-03B source;
4. panel membership must match the frozen panel artifact;
5. runtime and stimulus parameters must remain identical.

Any failure stops acceptance.

## Batched-vs-scalar agreement

The scalar result is compared against the already-recorded SQ-03B metric.

Numerical agreement uses the engineering tolerance frozen before SQ-03B
production execution:

- `rtol = 1e-6`
- `atol = 1e-7`

This tolerance was not selected from SQ-03C outcomes.

SQ-03C must also report the raw scalar effect magnitudes and the raw difference
from the SQ-03B batched result.

## Outputs

Primary outputs:

- scalar peak-voltage delta;
- scalar integrated-positive-voltage delta;
- scalar first-positive-frame delta;
- batched-vs-scalar metric agreement.

Descriptive follow-up outputs:

- upper-tail effect retention by stratum;
- low-tail control magnitude by stratum;
- rank stability within the frozen verification panel.

No p-value is manufactured from deterministic simulation replicates.

## Interpretation boundary

SQ-03C can confirm or fail replication of selected model-level SQ-03B
localization effects under the original scalar runtime.

It does not establish:

- a biological mechanism;
- formal population-level statistical significance;
- general male/female behavioral differences;
- sex superiority;
- intelligence differences;
- market skill;
- profitability;
- financial usefulness.

The SQ-03B post-hoc tolerance table remains descriptive only.
