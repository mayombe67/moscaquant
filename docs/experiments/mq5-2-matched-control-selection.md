# MQ-5.2 — Matched Non-Causal Control Selection

## Initial selection rule

The initial matched-control rule for the `43417 → 656` showcase was frozen
before candidate selection.

Required properties were:

- same functional class as source neuron 43417
- same graded subtype where applicable
- positive baseline effective activity at frame 145
- exclusion from the frozen causal-node set
- no direct structural edge to target neuron 656
- baseline activity ratio between 0.5 and 2.0 relative to neuron 43417
- in-degree ratio between 0.5 and 2.0
- out-degree ratio between 0.5 and 2.0

Eligible candidates:

`0`

Result:

**NO VALID MATCH UNDER INITIAL PRE-REGISTERED RULE**

No intervention outcome was inspected or used to alter the matching rule.

The failed candidate search is retained as part of the experimental record.

## Amendment 1

Status:

**PRE-REGISTERED BEFORE SECOND CANDIDATE SEARCH**

The categorical eligibility criteria remain unchanged:

- exact functional class match
- exact graded subtype match where applicable
- positive activity at frame 145
- exclusion from frozen causal nodes
- exclusion of nodes with a direct structural edge to neuron 656

The continuous matching tolerances are expanded to:

- activity ratio: 0.25 to 4.0
- in-degree ratio: 0.25 to 4.0
- out-degree ratio: 0.25 to 4.0

Candidate ranking remains unchanged:

`|ln(activity ratio)| + |ln(in-degree ratio)| + |ln(out-degree ratio)|`

Lowest score wins.

Model index remains the deterministic tie breaker.

Rationale:

The initial matching window produced no eligible candidate.

This amendment broadens only continuous similarity tolerances while
preserving the categorical biological and causal exclusions.

The amendment was defined before a second candidate search and before
any matched-control intervention outcome was observed.
