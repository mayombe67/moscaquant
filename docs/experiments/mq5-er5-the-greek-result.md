# MQ-5.ER.5 — THE GREEK — Authoritative Result

Status: **COMPLETED — AUTHORITATIVE DISCOVERY RESULT SEALED**

Classification:

`GREEK_FOCUSED_COORDINATOR_CANDIDATE`

Financial semantics:

`NOT ASSIGNED`

Causal claims authorized:

`false`

## Authoritative provenance

- frozen scientific execution SHA: `4978062b48b557ad9f8f327308ce4aeca0a49ae3`
- authoritative execution: `wotm-the-greek-20260922T201928Z`
- successful attempt: `attempt-9`
- AWS Batch job: `0a277562-bfcf-45b1-bcab-fc03158102bd`
- immutable image: `249215389153.dkr.ecr.us-east-2.amazonaws.com/moscaquant/rasputin@sha256:635403f4e527b5e98c68887884fb4198a9946b9cc8714b50ba0220a33f6f8796`
- job definition: `arn:aws:batch:us-east-2:249215389153:job-definition/moscaquant-rasputin-wrath-aksis:8`
- result SHA-256: `1ed37ae6d4e19cd39409a2bb714ed7394236d2a273316005c6ae596e5d837790`
- result seal SHA-256: `63fb631e661ff054e28869f0c784eddea088ab8c3307a0c82bc5d55a40b94ee9`
- eligible candidates: `17340`
- max backward hops: `3`
- frozen top-k: `5`
- focused threshold: affected coverage `>= 4/5`

## Frozen result

THE GREEK satisfied the preregistered focused-coordinator classification because
at least one eligible candidate reached the frozen `affected_coverage >= 4`
threshold.

The result was stronger than the threshold requirement: every emitted top-five
candidate covered all five affected targets.

| Rank | Node | Affected | Retained | Branches | First positive | Min lead |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | `1952` | 5/5 | 4/4 | 771 | 140 | 1 |
| 2 | `2641` | 5/5 | 4/4 | 642 | 140 | 1 |
| 3 | `1963` | 5/5 | 4/4 | 592 | 140 | 1 |
| 4 | `1944` | 5/5 | 4/4 | 551 | 140 | 1 |
| 5 | `23640` | 5/5 | 4/4 | 243 | 140 | 1 |

## Top-ranked candidate

The deterministic ranking placed node **`1952`** first.

Node `1952`:

- covers all `5/5` affected targets;
- also covers all `4/4` retained comparison targets;
- participates through `771` distinct immediate downstream branches on shortest
  paths to covered affected targets;
- becomes positive at frame `140`;
- has a minimum temporal lead of `1` frame over its covered affected targets.

The retained coverage matters. Node `1952` is **not** established as
affected-set-specific by this result; it reaches the retained comparison set as
well.

## Candidate detail

### #1 — node `1952`

- affected coverage: `5/5`
- retained coverage: `4/4`
- distinct downstream branches: `771`
- first-positive frame: `140`
- minimum temporal lead: `1`
- affected targets: `55`, `92`, `656`, `126002`, `137122`
- retained targets: `51`, `129`, `317`, `1273`
- hop signature: `{"126002": 2, "1273": 2, "129": 2, "137122": 2, "317": 3, "51": 2, "55": 3, "656": 2, "92": 2}`

### #2 — node `2641`

- affected coverage: `5/5`
- retained coverage: `4/4`
- distinct downstream branches: `642`
- first-positive frame: `140`
- minimum temporal lead: `1`
- affected targets: `55`, `92`, `656`, `126002`, `137122`
- retained targets: `51`, `129`, `317`, `1273`
- hop signature: `{"126002": 2, "1273": 2, "129": 2, "137122": 2, "317": 3, "51": 2, "55": 2, "656": 2, "92": 2}`

### #3 — node `1963`

- affected coverage: `5/5`
- retained coverage: `4/4`
- distinct downstream branches: `592`
- first-positive frame: `140`
- minimum temporal lead: `1`
- affected targets: `55`, `92`, `656`, `126002`, `137122`
- retained targets: `51`, `129`, `317`, `1273`
- hop signature: `{"126002": 2, "1273": 2, "129": 2, "137122": 2, "317": 2, "51": 2, "55": 2, "656": 1, "92": 2}`

### #4 — node `1944`

- affected coverage: `5/5`
- retained coverage: `4/4`
- distinct downstream branches: `551`
- first-positive frame: `140`
- minimum temporal lead: `1`
- affected targets: `55`, `92`, `656`, `126002`, `137122`
- retained targets: `51`, `129`, `317`, `1273`
- hop signature: `{"126002": 2, "1273": 2, "129": 2, "137122": 2, "317": 2, "51": 2, "55": 2, "656": 1, "92": 3}`

### #5 — node `23640`

- affected coverage: `5/5`
- retained coverage: `4/4`
- distinct downstream branches: `243`
- first-positive frame: `140`
- minimum temporal lead: `1`
- affected targets: `55`, `92`, `656`, `126002`, `137122`
- retained targets: `51`, `129`, `317`, `1273`
- hop signature: `{"126002": 2, "1273": 1, "129": 3, "137122": 2, "317": 2, "51": 2, "55": 3, "656": 2, "92": 3}`


## Interpretation

Under the frozen protocol, the result answers the discovery question:

> Does the three-hop upstream search contain a focused coordinator candidate
> satisfying the preregistered coverage/timing rule?

**Yes.**

It does **not** establish that node `1952` is uniquely responsible for the
response. It does not establish causal necessity or sufficiency. It does not
establish biological identity, cognition, intent, market understanding,
financial meaning, trading value, or predictive value.

All five emitted candidates share full `5/5` affected and `4/4` retained
coverage. Their ordering comes from the frozen deterministic ranking fields,
not from post-result preference.

## Stopping rule / next science

MQ-5.ER.5 itself authorizes **no intervention**.

Because a focused coordinator candidate was observed, the frozen stopping rule
requires any causal test to be a **new, separately preregistered experiment**
with frozen interventions and matched controls.

The next causal experiment should therefore be designed *after* this closeout.
No threshold lowering, hop expansion, top-k expansion, candidate reroll, or
post-hoc re-ranking is permitted from the MQ-5.ER.5 result.

`THE WEAVE` is **not activated by this result**. The sealed classification is a
focused-coordinator-candidate result, not the frozen distributed-pattern class.

## Execution-history note

The scientific result comes from Attempt 9 only. Earlier infrastructure/runtime
attempts remain provenance, not alternative scientific outcomes.

The authoritative result bytes are immutable and bound to:

`1ed37ae6d4e19cd39409a2bb714ed7394236d2a273316005c6ae596e5d837790`
