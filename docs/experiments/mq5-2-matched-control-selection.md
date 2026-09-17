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

## Candidate-landscape audit

After Amendment 3 also produced zero eligible candidates, candidate
availability was audited without performing any matched-control
intervention.

At frame 145:

- frozen graded population: 5,490 neurons
- graded neurons with positive effective activity: 9
- graded neurons within the frozen 0.25x to 4.0x activity window: 1

Subtype distribution:

- Tm2: 1,766 total, 2 active, 1 within activity window
- Tm3: 2,054 total, 0 active, 0 within activity window
- Tm4: 1,670 total, 7 active, 0 within activity window

The only graded neuron within the activity-matching window was:

`43417`

Properties:

- type: Tm2
- effective activity at frame 145: `0.37755101919174194`
- activity ratio relative to source: `1.0`
- in-degree: `74`
- out-degree: `128`
- frozen causal node: yes
- direct structural edge to neuron 656: yes

After excluding the source neuron itself, zero candidates remain.

## Final matched-control decision

Result:

**NO SCIENTIFICALLY VALID MATCHED NODE AVAILABLE AT FRAME 145**

No further matching-rule amendments will be made for this showcase.

The activity range will not be widened further and biological class
constraints will not be removed merely to force a control to exist.

The inability to construct a matched non-causal node control is retained
as part of the experimental record.

This does not invalidate the baseline, sham, attenuation, timing-shift,
reproducibility, or frozen-artifact controls.

It does mean that this showcase does not provide a matched non-causal
node comparison.

MQ-5.1 allowed such a control where a scientifically valid matched node
could be selected without using intervention outcomes.

For `43417 -> 656` at frame 145, that condition cannot be satisfied.

No matched-node intervention outcome was observed during the selection
process.
