# MQ-5.ER.3 — RETOUR — Results

## Status

**DISCOVERY ONLY**

Financial semantics remain **NOT ASSIGNED**.

## Authoritative run

- Git HEAD: `9686f4ae130b3c50e15d96c7b66ed3aa71d2311a`
- Result artifact:
  `/home/wil/moscaquant-data/experiments/mq5-er3-retour-v1.json`
- Result SHA-256:
  `90d8198a1c218ad24ef29c2c70b4b7a88fd8b24804516d2fd8f20903b847ff3`
- DETOUR parent SHA-256:
  `4b06c0181514f01715319dfacfa91569202067e583db7ef9fda5f35818eb4611`
- THE RACKET parent SHA-256:
  `3c5e18e63330d99c591536a59db9e6d40c5e5e8dca0789b576fa573e6e0bbfb1`
- Arm-A stimulus SHA-256:
  `9c06a18293dd7dd27b1a1717785e2da25518d4b0081e5266794c3166a3f471e9`
- Arm-C stimulus SHA-256:
  `e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`
- Maximum backward hops: `3`
- Top candidates per target: `5`

## Runtime-alignment correction

RETOUR retained DETOUR's frozen dynamic discovery score but excluded
ordinary retina-to-relay candidate edges whose ordinary-connectome coefficient
is exactly mirrored by the frozen relay representation and therefore removed by
the runtime's retinal double-count-removal bookkeeping.

The two preregistered negative controls behaved exactly as required:

- `116680 -> 12024` — THE NO-SHOW:
  `DETERMINISTICALLY_CANCELED_RETINA_RELAY`
- `78481 -> 16087` — THE RACKET matched control:
  `DETERMINISTICALLY_CANCELED_RETINA_RELAY`

Both were absent from RETOUR candidate lists.

Across the authoritative run, RETOUR rejected `1732` dynamically eligible
candidate checks under the canceled retina-to-relay rule.

## Classification

**FOCUSED_RETOUR_CANDIDATES**

Three directed edges recurred in the top-five lists of at least three of the
five affected targets:

| Edge | Affected targets | Recurrence |
|---|---|---:|
| `11725 -> 29921` | `55, 126002, 137122` | 3 / 5 |
| `11345 -> 47350` | `92, 656, 126002` | 3 / 5 |
| `10647 -> 51642` | `55, 92, 656` | 3 / 5 |

All three recurrent candidates were discovered at hop 3 in the corresponding
target rankings.

## Important comparison-target observation

The recurrent candidates are not automatically specific to the affected set.

In particular, `10647 -> 51642` also appeared among retained-dependency
comparison targets, including `51`, `129`, `317`, and `1273`.

Other RETOUR candidates likewise appear in comparison-target rankings.

Therefore the discovery result supports recurrent runtime-aligned routing
candidates, but does not establish affected-set specificity.

## Interpretation

RETOUR repaired the methodological problem exposed by THE RACKET and still
recovered structured recurrence.

This supports the narrower conclusion that the Arm-C / C13 state contains
recurrent, intervention-addressable candidate edges after removal of the known
pre-cancellation retina-to-relay artifact class.

It does **not** establish that any of the three recurrent edges is necessary,
sufficient, unique, biologically causal, cognitively meaningful, or specific to
the affected targets.

A preregistered causal intervention is required.

## Next experiment

The next experiment should test the three recurrent RETOUR edges as candidate
routing/transfer points.

The primary causal comparison should be against the frozen Arm-C + original
13-edge lesion condition, because RETOUR's candidate score was defined in the
state that survived that lesion.

Individual candidate lesions should be tested separately.

A preregistered combined-candidate lesion may additionally test whether the
three edges behave redundantly as a transfer set, but its interpretation must be
kept separate from single-edge necessity.

Matched structural controls should be frozen before outcome inspection.

## Lore — THE DOCKS

DETOUR followed a guy on the books.

THE RACKET found the no-show job.

RETOUR followed the package after the books were reconciled and found three
places where it kept changing hands.

**THE DOCKS** is the transfer layer.

The three recurrent candidates are **THE STEVEDORES**: inside handlers who may
be moving Marlo's package between containers.

"Horseface" is a working lore hypothesis only. No candidate has earned that
identity scientifically.

Omar has not entered the experiment.
