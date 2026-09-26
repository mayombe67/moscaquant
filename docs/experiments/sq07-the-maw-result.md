# SQ-07 — THE MAW — sealed result

## Status

**SEALED RESULT**

Run: `sq07-maw-20260924-01`

Authoritative analysis SHA-256:

`2db405151cc8771ccd0c50080bcd6a83ca3824e5487c666d22e01db8bed6d80c`

Independent RASPUTIN reduction SHA-256:

`107e2780602c3ab8531afdf15dda4057a093ed4716bb1a7e2236c7536e38adf7`

512 canonical shards and 32,768 deterministic episodes were included in
the sealed result.

## Question

SQ-07 exhaustively tested every binary subset of the frozen 13-edge
intervention universe under both LR and RL layouts.

The experiment asked whether the directional partition observed in SQ-06
survived exhaustive subset testing, whether supposedly inactive groups
contained hidden subset effects, and which inclusion-minimal subsets
exactly recapitulated the FULL13 computational endpoint.

## Result

The preregistered SQ-06 partition reproduced under both layouts.

All inactive-group subsets reproduced the INTACT endpoint:

- LR: 0 failures among the 8 subsets composed only of the frozen RL group.
- RL: 0 failures among the 1,024 subsets composed only of the frozen LR group.

No mixed-group inclusion-minimal FULL13 recapitulator was present.

The unique LR inclusion-minimal FULL13 recapitulator was:

`1111011111000`

Its Hamming weight is 9. Within the frozen 10-edge LR active group,
E04 is omitted. This means only that E04 was not required for exact
FULL13 recapitulation under this frozen computational endpoint when the
other nine members of that subset were lesioned.

The unique RL inclusion-minimal FULL13 recapitulator was:

`0000000000111`

Its Hamming weight is 3 and it is exactly the frozen three-edge RL
active group. No strict submask reached the FULL13 endpoint.

## Classification counts

| Layout | EXACT_INTACT | EXACT_FULL13 | INTERMEDIATE |
| --- | ---: | ---: | ---: |
| LR | 8 | 16 | 8,168 |
| RL | 1,024 | 1,024 | 6,144 |

`INTERMEDIATE` is a computational endpoint class only. SQ-07 defines no
minimum meaningful-effect floor for that class.

## Preregistered flags

- `SQ06_PARTITION_REPLICATED = True`
- `INACTIVE_SUBSET_CLOSURE_SUPPORTED = True`
- `INACTIVE_SUBSET_EFFECT_PRESENT = False`
- `ALL_MINIMAL_FULL13_RECAPITULATORS_ACTIVE_ONLY = True`
- `MIXED_GROUP_MINIMAL_RECAPITULATOR_PRESENT = False`
- `STRICT_SUBSET_SEPARABILITY_SUPPORTED = True`

There is no single overall scientific winner.

## Independent verification

The authoritative analyzer was frozen before outcome exposure.

The sealed result was subsequently recomputed through RASPUTIN's
bounded-memory independent verification path:

- 512/512 shard summaries
- 32,768/32,768 episodes
- deterministic duplicate replay checked within each shard
- canonical cloud evidence bound by SHA-256 and size before verification
- one staged cloud sidecar at a time
- bounded-memory streaming/mmap access
- exact shard-universe reduction
- no import of the SQ-07 analysis module
- no import of the SQ-06 classifier
- independent result agreement: **PASS**

The nine scientific classification/minimality functions used by the
RASPUTIN adapter were normalized-AST identical to the independent
verifier frozen at `ebc2d02` before the
full verification pass.

The 512 summary artifacts are bound by deterministic summary-universe
SHA-256:

`8e1dece1f47ba4fc1a78264a10368b8daa566623996566ca1a148710b2b1edbc`

## Claim boundary

These findings are properties of the frozen SQ-07 computational model,
intervention universe, and endpoint.

They do **not** establish fruit recognition, hunger, danger perception,
fear, behavior, a biological orientation circuit, population-level
biological significance, or financial value.

SQ-07 also does not convert historically derived edge/group structure
into an independent biological discovery.

## Storage

Dense execution, analysis, and verification artifacts remain outside Git
under `${MOSCAQUANT_DATA_ROOT}/experiments/`.

The repository stores the result narrative, schema, tests, and
content-addressed seal rather than duplicating the dense evidence.
