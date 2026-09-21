# MQ-3.PD — Propagation-Depth Diagnostic Protocol

**Status:** PRE-REGISTERED / IMPLEMENTATION READY  
**Parent evidence:** MQ-3.2  
**Scientific configuration mutation:** NO  
**Financial semantics:** NOT ASSIGNED

## Question

Does the weak downstream response already observed in the accepted MQ-3.2
Condition-A causal route reflect progressive signal loss with increasing
synaptic depth under the frozen MoscaQuant dynamics?

This diagnostic does not reopen MQ-3 and does not replace any accepted MQ-3.2
artifact.

## Frozen path basis

The diagnostic uses the already accepted
`mq3-2-causal-path-decomposition-v1` artifact.

Only paths reported at each responder's `first_positive` frame are used.

Hop depth is defined relative to each frozen path:

- hop 0 — path source;
- hop 1 — one directed edge downstream;
- hop 2 — two directed edges downstream;
- and so on.

Nodes are unioned by hop across the frozen path set. The diagnostic performs no
new route discovery.

## Primary run

The first authoritative diagnostic run uses the frozen MQ-3.2 release gain:

`0.9981738484618123`

Condition A, retinal mapping, sensory gain, graded Tm2/Tm3/Tm4 population,
connectome, market replay, and causal path basis remain unchanged.

## Measurements by hop

Record:

- node count;
- integrated positive voltage;
- episode mean positive voltage;
- maximum voltage;
- integrated effective activity;
- episode mean effective activity;
- active-neuron fraction;
- spike count;
- first positive-voltage frame;
- first effective-activity frame;
- voltage survival relative to hop 0;
- effective-activity survival relative to hop 0;
- voltage survival relative to the previous hop;
- effective-activity survival relative to the previous hop.

No single metric is allowed to redefine success after inspection.

## Diagnostic gain sweep

After the frozen-gain run, repeat the diagnostic at pre-registered release-gain
multipliers:

- 0.50×
- 0.75×
- 1.00×
- 1.25×
- 1.50×

The 1.00× repetition is retained inside the sweep to make the sensitivity
series self-contained.

The sweep is a sensitivity analysis only. It does not update or tune MQ-3.2.

## Interpretation

A steep reduction in voltage/effective-activity survival over the first few hops
would support the interpretation that weak downstream magnitude is compatible
with a propagation-depth limitation **within the frozen MoscaQuant model**.

Preserved signal across depth would argue against simple depth attenuation as
the explanation for the weak DN response.

Neither outcome establishes a universal MaleCNS biological limit.

Neither outcome authorizes changing the frozen release gain.

## Provenance

The implementation must record hashes for:

- causal-path decomposition;
- connectome;
- retina artifact;
- graded visual population;
- this frozen protocol configuration.

## Output

`${MOSCAQUANT_DATA_ROOT}/experiments/mq3-pd-propagation-depth-v1.json`

Negative results are retained.
