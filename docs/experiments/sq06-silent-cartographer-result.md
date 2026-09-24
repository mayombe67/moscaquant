# SQ-06 — SILENT CARTOGRAPHER — Result

## Status

`COMPLETE_PREREGISTERED_RESULT`

Authoritative local execution completed **28 / 28** frozen episodes. All **14 / 14**
deterministic duplicate pairs were array-exact across the stored primary and
channel outputs.

The authoritative result-manifest SHA-256 is:

`f9fe6e3ea23edc86869e7e47fa88ab11c25a607b8fe4fce6b5cdec2c8c0a58a9`

The authoritative dense NPZ sidecar SHA-256 is:

`f10b9769bd799a390295ced25b99c2a98e3efe49c823c2a5a79595d28fcc0feb`

The execution log is byte-identical to the JSON result manifest and has the
same SHA-256:

`f9fe6e3ea23edc86869e7e47fa88ab11c25a607b8fe4fce6b5cdec2c8c0a58a9`

An independent post-run verifier that did **not** import the SQ-06 runner
recomputed the primary conditions directly from the NPZ and passed.

Independent verifier SHA-256:

`70dabe8ef0cecabb3c7d672d89de88bf8fdf16e9fe99e144006d42db53983d00`

## Experimental purpose

SQ-06 prospectively tested an outcome-derived observation from sealed SQ-05:
the historical 13-edge intervention appeared to partition into a 10-edge
`LR_OBSERVED` group and a disjoint 3-edge `RL_OBSERVED` group.

The grouping was discovered from SQ-05 outcomes and frozen before SQ-06
execution. SQ-06 is therefore **prospective validation of an SQ-05-derived
grouping**, not independent discovery.

## Frozen primary outcome

All preregistered primary conditions were satisfied.

There is no combined winner and no minimum meaningful-effect floor was defined.

### FULL13 positive control

The complete 13-edge targeted intervention remained separated from its frozen
matched sham in both layouts:

- LR: target distance `3.824076886634501e-05`, sham distance `0`
- RL: target distance `0.1276743202466753`, sham distance `0`

The metric is the frozen symmetric normalized L2 distance over the
**192 × 1191 positive membrane-voltage fingerprint**.

### Subset sham guard

Both subgroup shams reproduced INTACT exactly in both layouts:

- `LR_GROUP_SHAM / LR`: exact
- `LR_GROUP_SHAM / RL`: exact
- `RL_GROUP_SHAM / LR`: exact
- `RL_GROUP_SHAM / RL`: exact

Each comparison had symmetric normalized L2 `0` and maximum absolute
difference `0`.

### Prospective exact-partition tests

All four preregistered partition conditions were exactly satisfied:

- **LR recapitulation:** `LR_GROUP_TARGETED / LR` exactly reproduced
  `FULL13_TARGETED / LR`.
- **LR cross-group null:** `RL_GROUP_TARGETED / LR` exactly reproduced
  `INTACT / LR`.
- **RL recapitulation:** `RL_GROUP_TARGETED / RL` exactly reproduced
  `FULL13_TARGETED / RL`.
- **RL cross-group null:** `LR_GROUP_TARGETED / RL` exactly reproduced
  `INTACT / RL`.

For every comparison above, symmetric normalized L2 was `0`, maximum absolute
difference was `0`, and the stored arrays were equal.

## Determinism

All **14 / 14** arm-layout duplicate pairs were array-exact across:

- primary positive membrane voltage
- primary spikes
- channel mean positive voltage
- channel positive fraction
- channel spike count
- channel spike rate

No randomized topology was constructed in SQ-06.

## Spike output

The stored DN spike count across all **28 episodes** was **0**.

The validated partition therefore concerns the frozen model's positive
subthreshold membrane-voltage dynamics at the primary DN endpoint. It does not
establish a spiking behavioral output.

## Interpretation

Under the frozen SQ-05 stimulus/runtime and the frozen 1191-DN positive-voltage
endpoint, the SQ-05-derived 10-edge/3-edge grouping prospectively decomposed the
13-edge intervention exactly by layout:

- in LR, the 10-edge group recapitulated FULL13 while the 3-edge group was
  indistinguishable from INTACT;
- in RL, the 3-edge group recapitulated FULL13 while the 10-edge group was
  indistinguishable from INTACT.

This is a validated property of the frozen modeled network and endpoint.

It does **not** establish that the grouping is a biological orientation circuit,
that the animal recognizes an object, that it experiences hunger, danger,
threat, or fear, or that a behavioral response occurred. It carries no
population-level significance claim and no market-prediction or financial-value
claim.

The strong LR/RL interpretation remains bounded by the frozen spatial stimulus
and naturally asymmetric retinal sampling.

## Provenance

Execution authorization commit:

`4973de1b4bdcde1ae1077c2f7902d8059036d254`

Runner implementation commit:

`133731606203b666c8e554510401d67e3999264d`

Runner SHA-256:

`39d4da93386b37c97ee4c276e388776d1e479046818764e6fc2ac8097a9803d8`

Runner configuration SHA-256:

`bbd6cde905af20a60216cc6cf29fdd7f18de980c7e653a8d0674c63f52af0bbd`

Result schema SHA-256:

`a0fe8b814a17e2c416576381c25aaf1d1b4ea0432af7c3112d617c5f1366eb37`

Execution authorization SHA-256:

`577b35ed143c0d55d0d3945a3ee5193072048ce26c59228886bd237c00b9f716`

SQ-06 preregistration SHA-256:

`3182a91b08dacc278ba180999f0358eea812da94ec5e2eeff9ed834498820f92`

Orientation-group artifact SHA-256:

`2fac74225e9874dfe13f919bfc47062065ba85b1ed1b61cce424f9a2c777c38d`

Orientation-group operator SHA-256:

`0ea1d6f3188f03e4a90da36898b9cb46a6546c830aebf9fb5f51508d66cce0ce`

## Result storage

The dense result artifacts remain outside Git under
`${MOSCAQUANT_DATA_ROOT}/experiments/` and are bound by SHA-256 in the result
seal. The seal does not copy, rewrite, or reclassify the scientific result.

## SILENT CARTOGRAPHER

The map predicted the routes.

The prospective run followed them exactly.

Now preserve the evidence without changing the story it tells.
