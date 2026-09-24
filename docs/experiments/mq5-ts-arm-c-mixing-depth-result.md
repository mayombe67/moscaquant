# MQ-5.TS.MIX — WARTHOG RUN — Result

## Status

**COMPLETED — STRUCTURAL CHARACTERIZATION RESULT SEALED FOR REVIEW**

Frozen classification:

`CURRENT_1X_ADEQUATE_FOR_SQ05`

Financial semantics:

`NOT ASSIGNED`

Neural execution:

`false`

## Authoritative execution

- authorization commit: `ddb1e3b9ae0cb55a1baefcd3edbc62ff6cb69984`
- implementation commit: `c4409caea38136553c9c12ad89b853ae62a358f7`
- execution mode: `local`
- result artifact:
  `${MOSCAQUANT_DATA_ROOT}/experiments/mq5-ts-arm-c-mixing-depth-v1.json`
- result SHA-256:
  `fe5d9c718a80aee41ed66af43bbd1c091250c972eb9ad7f41bdb2de5df7aff31`
- execution transcript:
  `${MOSCAQUANT_DATA_ROOT}/experiments/mq5-ts-arm-c-mixing-depth-v1.execution.log`
- execution transcript SHA-256:
  `1f7580b5a24d94a1e6b7b66f389558382a90198e90525c24284f76b6e6eece62`

All 12 frozen seed-depth builds completed. There were zero recorded failures.
Every scalable Arm-C structural invariant passed, every accepted-swap target was
reached, and the baseline-relative `no_new_self_edges` invariant passed.

## Frozen decision

The preregistered primary adequacy metric was seed-memory excess relative to the
tested `4.0x` deep references, with tolerance `0.01`.

At `1.0x`:

- seed `20264000`: `0.005022006208`
- seed `20264001`: `0.005003115752`
- seed `20264002`: `0.005013929854`

All three are below `0.01`.

Therefore the frozen result is:

`CURRENT_1X_ADEQUATE_FOR_SQ05`

This permits SQ-05 to prospectively reuse the existing `1.0x` Arm C depth,
subject to SQ-05's own implementation freeze.

## Descriptive structural curve

Mean eligible-edge identity retained from baseline:

- `0.5x`: `0.378364126`
- `1.0x`: `0.152664139`
- `2.0x`: `0.032146524`
- `4.0x`: `0.007318181`

Mean eligible-edge identity changed from baseline:

- `0.5x`: `0.621635874`
- `1.0x`: `0.847335861`
- `2.0x`: `0.967853476`
- `4.0x`: `0.992681819`

The three `4.0x` deep-reference pairwise overlaps are:

- `20264000:20264001`: `0.006919343268`
- `20264000:20264002`: `0.006881093028`
- `20264001:20264002`: `0.006874952652`

These quantities are descriptive and do not independently determine the frozen
classification.

## Fixed-endpoint observation

At `2.0x`, all three seed-memory excess values are above the frozen threshold:

- seed `20264000`: `0.025851491214`
- seed `20264001`: `0.025860271560`
- seed `20264002`: `0.025891227659`

This does not invalidate the frozen result. The `2.0x` state lies only `2.0x`
accepted swaps before its same-seed `4.0x` endpoint, whereas `1.0x` lies `3.0x`
before that endpoint. Higher same-seed overlap at `2.0x` can therefore arise
from the shorter deterministic trajectory lag.

The result does not establish monotonic mixing, stationarity, or complete graph
randomization. Any fixed-lag or expanded-depth convergence study must be
prospectively frozen as a new experiment and may not rewrite WARTHOG RUN.

## Claim boundary

The sealed result supports only that, under the frozen strict Arm-C constructor
and tested `4.0x` deep reference, `1.0x` seed-memory excess is within the
preregistered one-percentage-point tolerance for all three frozen seeds.

It does not establish perfect random-graph mixing, mathematical stationarity,
convergence of every graph statistic, biological realism, optimality of the
null, neural-response equivalence, or financial/predictive value.

## TWO BETRAYALS narrative

Chief cleared the Maw.

The flight recorder says the `1.0x` Warthog made the jump.

Cortana has also marked the strange `2.0x` reading for a future mission rather
than rewriting this one.
