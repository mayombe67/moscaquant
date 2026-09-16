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

## Amendment 2

Status:

**PRE-REGISTERED BEFORE THIRD CANDIDATE SEARCH**

Amendment 1 also produced zero eligible candidates.

The categorical criteria remain unchanged:

- exact Tm2 graded subtype
- positive baseline effective activity at frame 145
- exclusion from frozen causal nodes
- no direct structural edge to neuron 656

The activity requirement remains:

- activity ratio between 0.25 and 4.0 relative to neuron 43417

Structural in-degree and out-degree are no longer hard eligibility
constraints.

They remain part of candidate ranking.

Ranking becomes lexicographic:

1. smallest absolute log activity ratio
2. smallest combined absolute log in-degree and out-degree difference
3. lowest model index as deterministic tie breaker

Formally:

activity_distance =
`|ln(candidate_activity / source_activity)|`

degree_distance =
`|ln((candidate_in_degree + 1) / (source_in_degree + 1))|`
`+ |ln((candidate_out_degree + 1) / (source_out_degree + 1))|`

Candidates are sorted by:

`(activity_distance, degree_distance, model_index)`

Rationale:

Two prospectively frozen attempts produced no eligible candidate when
graph degree was treated as a hard matching criterion.

This amendment preserves functional identity and intervention-frame
activity while treating graph degree as a secondary similarity measure
rather than a requirement.

No matched-control intervention outcome has been observed.

## Amendment 3

Status:

**PRE-REGISTERED BEFORE FOURTH CANDIDATE SEARCH**

Amendment 2 also produced zero eligible candidates.

This establishes that no eligible control exists under all of the
following simultaneously:

- exact Tm2 subtype
- positive effective activity at frame 145
- activity ratio between 0.25 and 4.0
- exclusion from frozen causal nodes
- no direct structural edge to neuron 656

The activity window will not be widened.

Instead, exact graded subtype is relaxed to the frozen graded functional
class.

Eligible candidates may therefore be:

- Tm2
- Tm3
- Tm4

All remaining criteria are unchanged:

- candidate must be a member of the frozen graded population
- candidate must have positive effective activity at frame 145
- activity ratio must remain between 0.25 and 4.0 relative to neuron 43417
- candidate must not be part of the frozen causal-node set
- candidate must not have a direct structural edge to neuron 656

Ranking remains:

1. smallest absolute log activity ratio
2. smallest combined in-degree/out-degree log distance
3. lowest model index

Exact subtype is not used as a ranking preference.

Rationale:

Two tolerance-based searches and one degree-relaxed search produced no
valid exact-Tm2 control.

This amendment relaxes one categorical matching dimension while retaining
functional graded-neuron identity, intervention-frame activity matching,
causal exclusion, and the previously frozen activity tolerance.

No matched-control intervention outcome has been observed.
