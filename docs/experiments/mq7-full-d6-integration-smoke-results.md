# MQ-7 Full D6 Integration Smoke Test Results

## Status

SUPPORTED WITH VALID NULL EFFECTS

The complete D6 execution layer was exercised through the real MQ-3.2 replay
pipeline.

Each D6 condition was routed through its preregistered intervention boundary.

The structural connectome remained unchanged.

This smoke test validates execution-layer integration. It is not a replicated
multi-session efficacy experiment.

---

## Experimental setup

Market replay condition:

A

Acute intervention generation:

32

D6 conditions tested:

- SC-01 THE SHOCK
- SC-02 DARKNESS
- SC-03 BAD SYNAPSE
- SC-04 TIME OUT
- SC-05 SCAR TISSUE
- SC-06 MERCY

A matched baseline replay was generated for comparison.

---

## SC-01 THE SHOCK

Selected seed:

3

Target:

55548

Observed:

- voltage trace divergence: YES
- spike trace divergence: NO
- readout score divergence: YES
- final decision divergence: NO

DN-C1 score delta:

4.1843249884249267e-07

Classification:

MEASURABLE NEURAL EFFECT

---

## SC-02 DARKNESS

Selected seed:

3

Duration:

10 transitions

Observed:

- voltage trace divergence: YES
- spike trace divergence: YES
- readout score divergence: YES
- final decision divergence: NO

DN-C1 score delta:

-2.6150539770656518e-08

Classification:

MEASURABLE NEURAL AND SPIKE-LEVEL EFFECT

---

## SC-03 BAD SYNAPSE

Selected seed:

9

A validated persistent SC-03 plasticity overlay was supplied.

Observed:

- voltage trace divergence: YES
- spike trace divergence: NO
- readout score divergence: YES
- final decision divergence: NO

DN-C1 score delta:

-1.0445370643920353e-11

Classification:

MEASURABLE PERSISTENT PLASTICITY EFFECT

---

## SC-04 TIME OUT

Selected seed:

9

Duration:

10 transitions

Observed:

- voltage trace divergence: NO
- spike trace divergence: NO
- readout score divergence: NO
- final decision divergence: NO

Classification:

VALID NULL RESULT

The TIME OUT execution path was active, but this replay/timing did not produce a
measurable aggregate readout difference.

This result must not be interpreted as evidence that the intervention is
nonfunctional.

---

## SC-05 SCAR TISSUE

Selected seed:

10

Origin-session target:

93484

Origin phase:

CURRENT_SESSION

Observed during origin session:

- voltage trace divergence: YES
- spike trace divergence: NO
- readout score divergence: YES
- final decision divergence: NO

DN-C1 score delta:

-1.448486129743018e-13

Classification:

MEASURABLE ORIGIN-SESSION EFFECT

### Following session

Scar active:

YES

Scar phase:

FOLLOWING_SESSION

Following-session target:

93484

Observed:

- voltage trace divergence: YES
- spike trace divergence: NO

The target remained identical between the origin and following sessions.

Classification:

PERSISTENT SCAR CARRYOVER SUPPORTED

---

## SC-06 MERCY

Selected seed:

1

Target:

68045

Observed:

- voltage trace divergence: NO
- spike trace divergence: NO
- readout score divergence: NO
- final decision divergence: NO

Classification:

VALID NULL RESULT

MERCY only amplifies existing activity and does not create activity from zero.

The selected target did not produce a measurable replay-level effect during its
single active transition.

---

## Structural integrity

The structural connectome digest remained unchanged before and after all D6
smoke trials.

Classification:

STRUCTURAL CONNECTOME UNCHANGED

---

## Supported conclusions

The smoke test supports the following:

- all six D6 conditions can be dispatched through the integrated replay system;
- SC-01 produces a measurable activity-level neural effect;
- SC-02 produces measurable voltage and spike-level effects;
- SC-03 persistent plasticity remains functional inside the integrated D6
  execution layer;
- SC-05 produces origin-session and following-session effects;
- SC-05 target identity persists correctly across sessions;
- SC-04 and SC-06 can produce valid null outcomes;
- intervention execution does not modify the structural connectome.

---

## Not supported

This smoke test does not establish:

- financial utility;
- improved or degraded trading performance;
- final decision-level adaptation;
- biological learning in a living organism;
- consciousness, pain, trauma, reward, or subjective experience;
- comparative superiority of any D6 intervention.

---

## Final classification

MQ-7 FULL D6 EXECUTION INTEGRATION: SUPPORTED

Next phase:

Preregister and run a frozen multi-session experiment in which all six D6
conditions are actually administered according to deterministic selector
outcomes.
