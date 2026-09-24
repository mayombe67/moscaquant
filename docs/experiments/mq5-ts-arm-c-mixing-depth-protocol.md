# MQ-5.TS.MIX — Arm C Mixing-Depth Characterization

**Narrative label:** WARTHOG RUN — presentation only / non-scientific
**Status:** PRE-REGISTERED / NOT YET EXECUTED
**Scope:** structural null-model characterization only
**Parent result:** accepted MQ-5.TS topology-specificity result
**Parent public commit:** `d29c08a60b561ce47631a372a4af7f89d2249c5b`
**Financial semantics:** NOT ASSIGNED

## Purpose

MQ-5.TS Arm C used one accepted directed double-edge swap per eligible
non-retinal edge.

Before Arm C becomes the public-facing topology-null arm in SQ-05 / TWO
BETRAYALS, this prospective study asks whether the frozen `1.0x` swap depth has
lost enough edge-identity memory of its deterministic swap trajectory relative
to a deeper tested `4.0x` reference.

This study does not rerun neural dynamics and does not reinterpret the accepted
MQ-5.TS `0 / 20` result.

The label **WARTHOG RUN** is narrative only. It has no effect on scientific
configuration, analysis, classification, or claims.

## Frozen production backend

The study reuses, without reimplementation:

- `brain/mq5_ts_strict_shuffle_native.py`
- `brain/mq5_ts_strict_shuffle_verify.py`
- the same protected R1-R6 population;
- the same transmitter-sign constraints;
- the same no-new-self-edge semantics;
- the same duplicate-edge exclusion;
- the same exact degree / row-weight / normalization invariants.

The reference Python backend is not the full-connectome constructor.

## Frozen inputs

Runtime paths resolve from `MOSCAQUANT_DATA_ROOT`.

- connectome:
  `${MOSCAQUANT_DATA_ROOT}/processed/connectome-baseline-v1.npz`
- connectome SHA-256:
  `e00e3f2a9828c921fe1f093cc567bf45a85adad0526176be0aa1b8be09336eeb`
- transmitter sign:
  `${MOSCAQUANT_DATA_ROOT}/processed/transmitter_sign.npy`
- transmitter SHA-256:
  `0a8b1abe338e17afde197f7ef2d9a6b86cc67a2b51d0f50d9610108f809af69f`
- retinal map:
  `${MOSCAQUANT_DATA_ROOT}/processed/visual-r1-r6-map-v1.npz`
- retinal-map SHA-256:
  `c4655220e1aee4eab580a534df009f0a7493f075c42285b430ad1365ae37917f`

The SHA-256 values define frozen input identity. Workstation-specific absolute
paths do not.

Any input hash mismatch fails closed.

## Frozen paired depth grid

Each seed is evaluated at all four accepted-swap depths:

- `0.5x`
- `1.0x`
- `2.0x`
- `4.0x`

Each depth run starts from the same frozen baseline with the same seed. The
implementation freeze must verify that the constructor is deterministic and
that shallower same-seed runs correspond to prefixes of the deeper accepted
swap trajectory.

`4.0x` is the **tested deep reference**, not an assertion of mathematically
complete Markov-chain mixing or stationarity.

## Frozen seeds

Three fresh structural-only seeds:

- `20264000`
- `20264001`
- `20264002`

They are disjoint from the accepted MQ-5.TS Arm C result-bearing range
`20263000..20263019`.

All `3 x 4 = 12` seed-depth builds must complete. No early stopping and no seed
replacement are allowed.

## Frozen construction policy

For every build:

- `max_attempt_multiplier = 20`;
- all preregistered Arm C invariants must pass;
- failure to reach the accepted-swap target is a failed build;
- a failed invariant is a failed build;
- no neural simulation is executed;
- no responder, voltage, onset, market, trading, or profitability metric is
  evaluated.

## Structural metrics

Let `E0` be the set of eligible non-retinal directed edge identities in the
baseline graph and `E(d,i)` the eligible directed edge identities at depth `d`
for seed `i`.

### Descriptive distance-from-baseline metrics

For every seed/depth record:

`retention_fraction(d,i) = |E0 ∩ E(d,i)| / |E0|`

`changed_fraction(d,i) = 1 - retention_fraction(d,i)`

`baseline_edge_jaccard(d,i) = |E0 ∩ E(d,i)| / |E0 ∪ E(d,i)|`

These describe distance traveled from baseline. They do **not** by themselves
determine mixing-depth adequacy.

### Primary adequacy metric — seed-memory excess

For `d` in `{1.0, 2.0}` and seed `i`:

`within_seed_overlap(d,i) = |E(d,i) ∩ E(4,i)| / |E0|`

For the same checkpoint, compare against the `4.0x` states from the other two
seeds:

`cross_seed_overlap(d,i) = mean_j!=i(|E(d,i) ∩ E(4,j)| / |E0|)`

Then:

`seed_memory_excess(d,i) = within_seed_overlap(d,i) - cross_seed_overlap(d,i)`

If a checkpoint still strongly remembers its own deterministic future,
same-seed overlap will exceed overlap with other deep trajectories.

Also record the three pairwise `4.0x` deep-state overlaps as descriptive
deep-reference dispersion.

This is an edge-identity autocorrelation-style diagnostic against the tested
`4.0x` reference. It is not a proof of complete graph mixing or stationarity.

## Required diagnostics

For every seed/depth record:

- eligible edge count;
- target accepted swaps;
- accepted swaps;
- attempted swaps;
- rejection counts by reason;
- construction wall time as non-scientific telemetry;
- complete invariant report;
- baseline self-edge count;
- candidate self-edge count;
- eligible-edge identity retention;
- eligible-edge changed fraction;
- baseline-edge Jaccard.

Across checkpoints additionally record:

- within-seed checkpoint-to-`4.0x` overlap at `1.0x` and `2.0x`;
- cross-seed checkpoint-to-other-`4.0x` mean overlap at `1.0x` and `2.0x`;
- seed-memory excess at `1.0x` and `2.0x`;
- all pairwise `4.0x` deep-state overlaps.

Wall-clock time does not enter scientific interpretation.

## Frozen adequacy rule

The `4.0x` states are the tested deep reference.

Tolerance:

`0.01` absolute eligible-edge fraction (one percentage point).

Classification is frozen as:

1. `CURRENT_1X_ADEQUATE_FOR_SQ05`
   - all 12 builds complete;
   - all invariants pass;
   - for **all three seeds**,
     `seed_memory_excess(1.0,i) <= 0.01`.

2. `SQ05_REQUIRES_2X_PROSPECTIVE_DEPTH`
   - the `1.0x` rule fails; and
   - for **all three seeds**,
     `seed_memory_excess(2.0,i) <= 0.01`.

3. `NO_ADEQUATE_DEPTH_WITHIN_TESTED_RANGE`
   - the `2.0x` rule also fails.

4. `INCOMPLETE_OR_INVALID`
   - any build is missing;
   - any target is not reached; or
   - any structural invariant fails.

`0.5x` and distance-from-baseline statistics are descriptive. They help show
the below-current portion of the trajectory but do not independently determine
the SQ-05 decision.

## Consequences for SQ-05

- `CURRENT_1X_ADEQUATE_FOR_SQ05`:
  SQ-05 may prospectively reuse the existing `1.0x` Arm C depth.
- `SQ05_REQUIRES_2X_PROSPECTIVE_DEPTH`:
  SQ-05 may use `2.0x` only after its own implementation freeze; this does not
  rewrite MQ-5.TS.
- `NO_ADEQUATE_DEPTH_WITHIN_TESTED_RANGE`:
  BETRAYAL II remains blocked and a separately frozen expanded-depth study is
  required.
- `INCOMPLETE_OR_INVALID`:
  no SQ-05 topology-null authorization.

## No-free-looks boundary

The depth grid, seeds, metrics, tolerance and decision rule are frozen before
any mixing-depth build is executed.

After results exist, this study may not:

- add a convenient depth;
- replace a seed;
- change the one-percentage-point tolerance;
- substitute neural outcome metrics;
- reinterpret the accepted MQ-5.TS result.

## Claim boundary

A positive adequacy classification establishes only that the tested
edge-identity seed-memory excess at `1.0x` or `2.0x` is within the
preregistered one-percentage-point tolerance relative to the tested `4.0x`
reference under the frozen Arm C constructor.

It does **not** establish:

- perfect random-graph mixing;
- mathematical stationarity;
- convergence of every graph statistic;
- biological realism;
- optimality of the null;
- neural-response equivalence;
- financial or predictive value.

## Execution boundary

This preregistration authorizes no build by itself.

A separate implementation freeze must be committed and reviewed before the
first seed-depth construction.
