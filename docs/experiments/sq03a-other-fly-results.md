# SQ-03A — THE OTHER FLY — Results

**Status:** COMPLETE  
**Classification:** Authoritative result-bearing execution  
**Source commit:** `f2ef3880fd65bca2132d60df12ae5aa07c0d4335`  
**Artifact SHA-256:** `8b9f5ccdd1004769002c05c1c1842c7798e760c99342568f32a8583b3aae6c5c`

## Execution integrity

The frozen SQ-03A protocol executed on:

- **7,943** matched nodes;
- **639,435** matched edges;
- **12** preregistered input labels;
- **3** preregistered descending-neuron anchor labels.

The male and female runs used the same matched sparsity pattern, identical
runtime parameters, identical stimulus parameters, and the same common graph
normalization rule.

Deterministic A/A replay passed for every input in both subjects:

- MORTY: **PASS**
- LILITH: **PASS**

## Predefined comparison summary

| Frozen input | Response-vector distance | Peak anchor rank identical? |
| --- | ---: | :---: |
| `TmY14` | 0.00633643381652 | no |
| `AN_multi_124` | 0.00463246698114 | yes |
| `AVLP532` | 0.00380525377375 | yes |
| `CB2576` | 0.00628425962599 | yes |
| `DNc01` | 0.0166498901141 | yes |
| `LHPV6q1` | 0.00169673280542 | yes |
| `LPLC2` | 0.0271292392522 | no |
| `aMe4` | 0.00500605876957 | yes |
| `AVLP234` | 0.0149596792686 | no |
| `AVLP435` | 0.0138684232661 | no |
| `CB4116` | 0.0015073863519 | yes |
| `SLP230` | 0.00310899377261 | yes |

Peak-voltage anchor rank order differed for **4 of 12**
frozen inputs:

- `TmY14`
- `LPLC2`
- `AVLP234`
- `AVLP435`

It was identical for the remaining **8 of 12**
inputs.

## Result classification

SQ-03A demonstrates that, under the frozen matched-central-brain simulation,
using the aligned male versus aligned female edge weights can produce different
deterministic downstream response vectors for the same standardized input.

For some frozen inputs, the ordering of peak responses across the three
predefined descending-neuron anchors also changes.

These are **model-level comparative results inside the preregistered matched
subgraph**.

They do not establish a general biological or behavioral sex difference and
do not identify a biological mechanism.

## Scope limitation

SQ-03A does not recreate or compare the unavailable female optic-lobe sensory
pathway. The experiment begins at the frozen matched central-brain input panel.

The result therefore does not answer whether MORTY and LILITH would process the
same external market stimulus differently through their complete sensory
systems.

## Claim boundary

SQ-03A compares deterministic model responses of officially cross-matched male and female Drosophila central-brain edge-weight sets under identical simulation mechanics and standardized stimulation. Differences are model results within this matched subgraph and do not establish sex superiority, intelligence, general behavior, biological mechanism, market skill, profitability, or financial usefulness.

No market skill, profitability, financial usefulness, WARDEN authority,
ORACLE authority, or broker authority is assigned by this result.
