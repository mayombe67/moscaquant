# MQ-5.ER.5 THE GREEK — Performance Amendment

## Status

`IMPLEMENTED FOR EQUIVALENCE REVIEW — NOT AUTHORIZED FOR RESULT EXECUTION`

## Trigger

WRATH / AKSIS Attempt 7 reached authoritative result execution but AWS Batch
terminated the job at the frozen 21,600-second attempt-duration timeout.

The non-result complexity census at frozen science revision `1e19947aa5950788709d14c9cc736eaaf4ecb355`
measured:

- connectome shape: `166700 x 166700`
- edges: `25,582,925`
- candidate nodes: `166,258`
- affected candidate/target pairs: `818,489`
- retained candidate/target pairs: `658,020`
- child reverse-search pressure upper bound: `127,603,950`

## Root cause

The frozen candidate-discovery implementation calls
`shortest_path_first_hops()` for candidate/affected-target pairs.

That reference helper:

1. performs a bounded BFS for each pair;
2. then recomputes `reverse_shortest_distances(target, max_hops - 1)` once for
   every direct child of the candidate.

The reverse-distance result depends only on target and hop bound, but the frozen
implementation recomputes it across millions of candidate/child combinations.

## Amendment

The scientific selection and interpretation rules are unchanged.

The optimized implementation:

- retains the original `shortest_path_first_hops()` as the frozen reference;
- precomputes exact bounded distances into each affected target once;
- precomputes the frozen reverse-distance maps once per target;
- converts required distance classes into boolean lookup masks;
- uses the same direct-child membership rule to produce the same first-hop sets.

No target set, hop limit, ranking key, temporal rule, candidate exclusion,
classification rule, or result schema is changed.

## Required proof before authorization

1. exhaustive equivalence on deterministic small sparse graphs;
2. full unit suite;
3. non-result full-connectome performance probe;
4. new science revision;
5. new immutable runtime image;
6. safe known-replay runtime acceptance;
7. separate Attempt 8 authorization.

`--run-frozen` remains forbidden until all gates above pass.
