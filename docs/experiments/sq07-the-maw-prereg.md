# SQ-07 — THE MAW — Preregistration Review Candidate

## Why this study exists

SQ-05 and SQ-06 are sealed.

SQ-05 prospectively reused the inherited historical 13-edge lesion and showed
that it exceeded its matched sham in both frozen layouts. Its strict
matched-topology null reproduced the intact response in `0/20` frozen topology
seeds.

A post-SQ-05 descriptive audit partitioned those 13 historical lesion edges
into a 10-edge LR-associated group and a 3-edge RL-associated group. Because
that partition was discovered after SQ-05 results existed, SQ-06 froze it as a
new prospective validation rather than treating it as independent discovery.

SQ-06 then found the exact group-level partition under the frozen endpoint:

- in LR, the 10-edge LR group exactly reproduced FULL13 while the 3-edge RL
  group exactly reproduced INTACT;
- in RL, the 3-edge RL group exactly reproduced FULL13 while the 10-edge LR
  group exactly reproduced INTACT;
- both subgroup shams exactly reproduced INTACT;
- all preregistered primary conditions passed.

That result establishes a reproducible group-level partition under the frozen
model endpoint. It does not reveal the complete interaction structure inside
those groups.

A whole group can be null even if smaller subsets within it are not. Opposing
subset effects can cancel. Likewise, a group that reproduces FULL13 may contain
edges that are unnecessary, redundant, or interchangeable.

SQ-07 therefore freezes the complete 13-edge intervention universe and tests
every possible lesion subset prospectively.

## Scientific question

Across the complete frozen 13-edge intervention lattice, what subsets exactly
reproduce INTACT, what subsets exactly reproduce FULL13, and what
inclusion-minimal subsets are sufficient to reproduce the FULL13 endpoint in
each layout?

A second prospective question is whether the SQ-06 inactive-group nulls remain
closed under every subset of those groups, or whether exhaustive enumeration
reveals hidden subset effects that were invisible at the whole-group level.

## Frozen edge universe

The edge universe is inherited prospectively from the sealed SQ-06 grouping
artifact.

It contains exactly 13 targeted historical lesion edges:

- indices `E00` through `E09` are the frozen 10-edge `LR_OBSERVED` group;
- indices `E10` through `E12` are the frozen 3-edge `RL_OBSERVED` group.

The ordering is frozen in
`config/controls/sq07-the-maw-edge-registry-v1.json`.

Every intervention is represented by a 13-character binary mask. Character
position `i` refers exactly to edge `Ei`.

`0` means that edge remains intact.

`1` means that edge is lesioned.

Therefore:

`0000000000000` is INTACT.

`1111111111111` is FULL13.

All `2^13 = 8192` masks are enumerated in frozen lexicographic order. No mask
may be added, removed, selected adaptively, pruned after observing results, or
skipped because an earlier result appears sufficient.

## Design

All 8,192 masks are evaluated under both frozen visual layouts:

- `LR`
- `RL`

Every mask/layout condition is executed twice from fresh runtime state.

Total planned conditions before duplication: **16,384**.

Total planned episodes: **32,768**.

The frozen SQ-06 visual runtime, 1,191-DN anatomy-only population,
positive-membrane-voltage fingerprint, and exact-reproduction tolerances are
retained.

The primary fingerprint for one episode remains `192 x 1191`.

Exact reproduction requires both:

- symmetric normalized L2 `<= 1e-9`;
- maximum absolute difference `<= 1e-12`.

Every deterministic duplicate pair must reproduce exactly.

The same-layout INTACT and FULL13 anchors must remain distinguishable under
those exactness tolerances. If they collapse into exact equivalence, the
experiment fails closed rather than redefining the classification.

Each mask is classified relative to its same-layout anchors as:

`EXACT_INTACT`

`EXACT_FULL13`

or

`INTERMEDIATE`.

`INTERMEDIATE` means only that the fingerprint is not exact to either frozen
anchor. No biological or minimum meaningful-effect interpretation is attached
to that label.

## Primary tests

First, THE MAW requires the already-sealed SQ-06 group-level partition to
reproduce inside the exhaustive lattice.

In LR:

- the full 10-edge LR-group mask must exactly reproduce FULL13;
- the full 3-edge RL-group mask must exactly reproduce INTACT.

In RL:

- the full 3-edge RL-group mask must exactly reproduce FULL13;
- the full 10-edge LR-group mask must exactly reproduce INTACT.

Second, the experiment tests inactive-subset closure.

For LR, all `2^3 = 8` masks composed only of the frozen RL group, including the
empty subset, must exactly reproduce INTACT for complete inactive-subset
closure.

For RL, all `2^10 = 1024` masks composed only of the frozen LR group, including
the empty subset, must exactly reproduce INTACT for complete inactive-subset
closure.

If any inactive-only subset is not exact INTACT, that is reported as a hidden
subset effect. It does not retroactively invalidate SQ-06; it shows that the
whole-group null concealed structure that SQ-06 was not designed to resolve.

Third, THE MAW identifies every inclusion-minimal FULL13 recapitulator
separately in each layout.

A mask is inclusion-minimal only when:

- it is `EXACT_FULL13`; and
- no strict submask is also `EXACT_FULL13`.

Minimum Hamming weight alone is not sufficient to define minimality.

The experiment reports whether every inclusion-minimal FULL13 recapitulator is
contained entirely within the layout's frozen SQ-06 active group, and whether
any inclusion-minimal FULL13 recapitulator requires edges from both frozen
groups.

The following result flags are evaluated separately:

`SQ06_PARTITION_REPLICATED`

`INACTIVE_SUBSET_CLOSURE_SUPPORTED`

`INACTIVE_SUBSET_EFFECT_PRESENT`

`ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY`

`MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT`

`STRICT_SUBSET_SEPARABILITY_SUPPORTED`

`STRICT_SUBSET_SEPARABILITY_SUPPORTED` requires, in both layouts, reproduction
of the SQ-06 partition, complete inactive-subset closure, active-group-only
inclusion-minimal FULL13 recapitulators, and no mixed-group inclusion-minimal
FULL13 recapitulator.

There is no overall scientific winner.

No minimum meaningful-effect floor is introduced.

## Why this study comes next

SQ-06 answered the group-level question cleanly but intentionally stopped there.

Testing selected single edges or hand-picked combinations next would reopen
researcher degrees of freedom: the choice of subsets could be influenced by the
already-observed SQ-06 result.

The 13-edge universe is small enough to avoid that problem entirely.

Exhaustive enumeration replaces subset selection with a complete prospective
intervention landscape.

That landscape can reveal redundancy, substitutability, cancellation,
mixed-group interactions, and inclusion-minimal FULL13 recapitulation without
requiring a post-result search over which subsets deserve testing.

Execution may be divided into content-addressed shards for operational reasons,
but sharding does not change the scientific universe. Every mask, layout, and
replicate remains mandatory, and preserved evidence must be sufficient for an
independent verifier to recompute the reported classifications.

## Boundaries

The 13-edge universe originates historically from earlier post-hoc work.

The 10-edge versus 3-edge grouping was itself derived after SQ-05 and was only
prospectively validated in SQ-06.

SQ-07 therefore does not transform either history into independent discovery.

No result may be described as fruit recognition, hunger, danger perception,
fear, behavior, a biological orientation circuit, population-level biological
significance, or financial value.

`INTERMEDIATE` does not imply a meaningful biological intermediate state.

SQ-07 execution requires explicit, run-specific authorization from the human
operator. No software agent, automated system, successful test or CI result,
runner availability, or prior authorization may be treated as execution
authorization.

No SQ-05 or SQ-06 result is reopened or rewritten.

No neural or result execution is authorized by this preregistration.

## THE MAW

The map is no longer the question.

Every door on it is about to open.
