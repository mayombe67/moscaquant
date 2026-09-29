# MQ-5.ER.5 — THE GREEK Orientation-Semantics Audit Result

## Status

**SEALED STRUCTURAL AUDIT**

Classification:

`GREEK_ORIENTATION_DEFECT_CONFIRMED_ALL_TOP5`

No neural execution was performed.

No new candidates were searched.

No candidate reranking was performed.

No existing THE GREEK artifact was modified.

## Trigger

While preparing MQ-5.ER.6 — THE PINCH, the frozen matched-control selector
refused execution because node `1952` did not reproduce THE GREEK's sealed
structural hop signature under the project's declared connectome orientation.

The selector failed before:

- selecting a matched control;
- creating a control artifact;
- executing THE PINCH;
- observing any MQ-5.ER.6 neural outcome.

This triggered a dedicated structural-semantics audit.

## Frozen connectome convention

MoscaQuant stores directed connectivity as:

`graph[postsynaptic, presynaptic] = weight`

Therefore:

`graph[b, a]`

represents:

`a -> b`

Reverse ancestry into a target must therefore obtain presynaptic predecessors
from the target's CSR row.

## Historical GREEK traversal

The sealed MQ-5.ER.5 implementation function
`reverse_shortest_distances()` converted the matrix to CSC and indexed columns
using the current target/frontier node.

Under the frozen `graph[post, pre]` convention, that operation follows
postsynaptic destinations of the current node rather than presynaptic
predecessors into it.

A deterministic tiny-graph contract confirmed the distinction using:

`0 -> 1 -> 2`

Correct reverse ancestry into node `2` is:

- node `1` at one hop;
- node `0` at two hops.

The historical GREEK traversal instead follows the opposite direction.

## Reproduction requirement

Before comparing against corrected orientation semantics, the audit required
exact reproduction of every sealed GREEK top-five hop signature.

All five historical signatures reproduced exactly.

This establishes that the discrepancy is not result-file corruption, stale
documentation, or an inability to reproduce the sealed implementation.

## Top-five comparison

Target order:

`51, 55, 92, 129, 317, 656, 1273, 126002, 137122`

| Node | Sealed GREEK signature | Correct reverse-ancestry signature | Differences |
|---:|---|---|---:|
| 1952 | `(2,3,2,2,3,2,2,2,2)` | `(2,3,2,3,3,2,2,3,2)` | 2 |
| 2641 | `(2,2,2,2,3,2,2,2,2)` | `(2,2,2,3,3,2,2,3,2)` | 2 |
| 1963 | `(2,2,2,2,2,1,2,2,2)` | `(2,2,2,3,3,2,2,3,2)` | 4 |
| 1944 | `(2,2,3,2,2,1,2,2,2)` | `(2,2,2,2,3,2,2,3,2)` | 4 |
| 23640 | `(2,3,3,3,2,2,1,2,2)` | `(2,3,2,3,3,2,2,3,3)` | 5 |

All five top-ranked GREEK candidates therefore disagree with correct
reverse-ancestry semantics.

## Classification

`GREEK_ORIENTATION_DEFECT_CONFIRMED_ALL_TOP5`

The defect is systemic across the sealed emitted top-five candidate set.

## Effect on the original result

The original THE GREEK result remains an immutable historical artifact.

Its authoritative result SHA-256 remains:

`1ed37ae6d4e19cd39409a2bb714ed7394236d2a273316005c6ae596e5d837790`

Its result-seal SHA-256 remains:

`63fb631e661ff054e28869f0c784eddea088ab8c3307a0c82bc5d55a40b94ee9`

Those bytes correctly record the output of the frozen historical
implementation.

However, the classification:

`GREEK_FOCUSED_COORDINATOR_CANDIDATE`

does not support the intended scientific claim that the search identified an
upstream coordinator under the declared three-hop reverse-ancestry semantics.

The implementation answered a different directional graph question.

Node `1952` therefore does not remain an authorized upstream-coordinator
candidate merely because it ranked first in the historical execution.

## Downstream experiments

MQ-5.ER.6 — THE PINCH remains historically preregistered but blocked.

Its frozen node `1952` may not be substituted or changed after the fact.

MQ-5.ER.7 — PINE BARRENS also remains blocked.

Neither experiment produced a neural result.

A corrected GREEK discovery requires a new experiment identity and a fresh
scientific freeze.

## Corrected-discovery boundary

The corrected experiment must preserve the original scientific question while:

- using the declared `graph[post, pre]` orientation correctly;
- freezing the corrected traversal before candidate discovery;
- performing a fresh candidate search;
- inheriting no winner from the historical top five;
- accepting null, focused, or distributed classification according to its
  frozen rule.

The corrected experiment is:

**MQ-5.ER.5R — WAY DOWN IN THE HOLE**

## Provenance

Frozen auditor commit:

`5f9e282`

Audit artifact commit:

`9d2277f`

Audit artifact SHA-256:

`5e441e0027dd40363705ebcf914d5f3d53245efbde2bc91129cd8cbfac82b11f`

## APOTHEOSIS #29 — Direction Is Part of the Model

Any graph-derived scientific claim must bind traversal direction to the model's
declared edge orientation and prove that relationship with an executable
minimal-graph contract.

Exact reproduction of a misoriented implementation does not validate the
intended scientific semantics.

The fail-closed boundary in THE PINCH detected this defect before a downstream
causal result was generated.

That is the intended behavior of the scientific control system.
